#!/usr/bin/env python
import argparse
import gzip
import io
from os.path import join, isfile, isdir, basename, dirname, exists
import seaborn as sns
from os import mkdir, listdir
import sys
import time
from multiprocessing import Pool
import pandas as pd
import math
import json
from Bio import SeqIO
import numpy as np
import shutil
import tarfile
import itertools
from operator import itemgetter

# from pankmer.index import (print_err, genome_name, break_seq, get_kmers,
#                    score_byte_to_blist, kmer_byte_to_blist, kmer_byte_to_long)
from pankmer.index import (kmer_size, break_seq, print_err, score_byte_to_blist,
                           run_index, load_scores)
from pankmer.env import EXAMPLE_DATA_DIR
from pankmer.download import download_example
from pankmer.count import count_kmers
from pankmer.collect import COL_COLOR_PALETTE, collect
from pankmer.upset import upset
from pankmer.subset import subset
from pankmer.adjacency_matrix import get_adjacency_matrix
from pankmer.tree import tree
from pankmer.clustermap import clustermap
from pankmer.reg_coverage import (COLOR_PALETTE, reg_coverage, genome_coverage,
                                  genome_coverage_plot, coverage_heatmap)
from pankmer.dryrun import dryrun
from pankmer.version import __version__
from pankmer.gzip_agnostic_open import gzip_agnostic_open
from pankmer.get_lower_bound import get_lower_bound

#===============================================================================


def retrieve_metadata(metadata_path):
    if isinstance(metadata_path, tarfile.ExFileObject):
        metadata = json.load(metadata_path)
    else:
        with open(metadata_path, 'rt') as infile:
            metadata = json.load(infile)
    genomes = {}
    for pos in range(len(metadata['genomes'])):
        genome = metadata['genomes'][str(pos)]
        size = metadata['genome_sizes'][genome]
        genomes[genome] = size
    return metadata['kmer_size'], genomes, metadata['positions'], metadata['mem_blocks']


def get_positional_kmers(fasta_path, upper, lower, contig_header='id'):
    kmers_dict = {}
    with gzip_agnostic_open(fasta_path, 'rt') as infile:
        for record in SeqIO.parse(infile, 'fasta'):
            names = {'id': record.id, 'description': record.description}
            seq_byte = bytes(str(record.seq).upper(), 'ascii')
            kmers_dict[names[contig_header]] = break_seq(seq_byte, upper, lower)
    return kmers_dict


def get_sorted_kmer_scores(args: list) -> dict:
    index_path, kmers = args
    results = PKResults(index_path)
    lower = min(list(kmers.keys()))
    upper = max(list(kmers.keys()))
    lb_bit = int(lower).to_bytes(results.kmer_bitsize, byteorder="big", signed=False) # lower bound bit
    ub_bit = int(upper).to_bytes(results.kmer_bitsize, byteorder="big", signed=False)
    # Find lower bound position from index
    initial_lower_bound = get_lower_bound(results.positions, lower)
    # Move iterator from initial lower bound to actual lower bound
    if initial_lower_bound != None:
        results.seek_kmer(initial_lower_bound)
        results.seek_i(initial_lower_bound)
    for kmer_bit, _, score in results:
        if kmer_bit > ub_bit:
            break
        kmer  = results.decode_kmer(kmer_bit)
        if kmer in kmers:
            kmers[kmer] = score
    return kmers


class PKIterator:
    def __init__(self, results):
        self._results = results
    
    def __next__(self):
        kmer = self._results.get_kmer_byte()
        i_score = self._results.get_score_byte()
        if kmer == None or i_score == None:
            self._results.reset_iter()
            raise StopIteration
        return (kmer, *i_score)


class PKResults:
    def __init__(self, results_dir: str, threads: int = 1):
        index_files = ['metadata.json', 'kmers.bgz', 'indices.bgz', 'scores.pks']
        self.input_is_tar = False
        if isfile(results_dir) and tarfile.is_tarfile(results_dir):
            self.input_is_tar = True
            self.tar = tarfile.open(results_dir)
            found_files = {basename(tarinfo.name) for tarinfo in self.tar
                            if tarinfo.isreg()}
            for file in index_files:
                if file not in found_files:
                    raise ValueError(f"{file} is not found in index!")
            indices_filename, kmers_filename, metadata_filename, scores_filename = sorted(
                tarinfo.name for tarinfo in self.tar if tarinfo.isreg())
            kmer_size, genomes, positions, mem_blocks = retrieve_metadata(
                self.tar.extractfile(metadata_filename))
            self.number_of_genomes = len(genomes)
            self.scores = {i: tuple(self.decode_score(bytes(s))) for i, s in enumerate(load_scores(str(results_dir), str(results_dir)))}
            self.kmers_stream = gzip.open(self.tar.extractfile(kmers_filename), 'rb')
            self.indices_stream = gzip.open(self.tar.extractfile(indices_filename), 'rb')
        elif isdir(results_dir):
            for file in index_files:
                file_path = join(results_dir, file)
                if not isfile(file_path):
                    raise ValueError(f"{file} is not found in results directory!")
            kmer_size, genomes, positions, mem_blocks = retrieve_metadata(join(results_dir, 'metadata.json'))
            self.number_of_genomes = len(genomes)
            self.scores = {i: tuple(self.decode_score(bytes(s))) for i, s in enumerate(load_scores(str(results_dir), ''))}
            self.kmers_stream = gzip.open(join(results_dir, 'kmers.bgz'), 'rb')
            self.indices_stream = gzip.open(join(results_dir, 'indices.bgz'), 'rb')
        else:
            raise ValueError(f"{results_dir} is not a valid directory!")
        self.results_dir = results_dir
        self.kmer_size = kmer_size
        self.genomes = genomes
        self.positions = positions
        self.kmer_bitsize = math.ceil(((kmer_size*2))/8)
        self.i_bitsize = 8
        self.threads = threads
        self.mem_blocks = mem_blocks
        self.kmer_buffer = io.BufferedReader(self.kmers_stream)
        self.i_buffer = io.BufferedReader(self.indices_stream)
        
    def __iter__(self) -> PKIterator:
        """ Object iterator

        Returns
        -------
        PKIterator
            returns a kmer and a score in bytes
        """        
        return PKIterator(self)

        
    def get_kmer_byte(self) -> bytes:
        """read bytes in size of one kmer from kmers file

        Returns
        -------
        bytes
            bytes representing Kmer
        """        
        kmer_byte = self.kmer_buffer.read(self.kmer_bitsize)
        if not kmer_byte:
            return None
        return kmer_byte
        
    def get_score_byte(self) -> bytes:
        """read bytes in size of one score from scores file

        Returns
        -------
        bytes
            bytes represting what samples have a Kmer
        """        
        i_byte = self.i_buffer.read(self.i_bitsize)
        if not i_byte:
            return None
        i = int.from_bytes(i_byte, byteorder='big', signed=False)
        return i_byte, self.scores[i]
    
    def seek_kmer(self, kmer_num : int):
        """Move Kmer file pointer past a number of Kmers

        Parameters
        ----------
        kmer_num : int
            Number of Kmers to skip
        """        
        self.kmer_buffer.seek(kmer_num*self.kmer_bitsize)
    
    def seek_i(self, i_num: int):
        """Move Score file pointer past a number of scores

        Parameters
        ----------
        score_num : int
            Number of scores to skip
        """        
        self.i_buffer.seek(i_num*self.i_bitsize)

    def reset_iter(self):
        """Move Kmer and Score files' pointers to 0 position
        """        
        self.seek_kmer(0)
        self.seek_i(0)
        
    def set_threads(self, threads : int):
        """Set number of threads to run multithreaded processes

        Parameters
        ----------
        threads : int
            Number of threads
        """        
        self.threads = threads
    
    def decode_score(self, bits : bytes) -> list:
        """Convert score bytes to a list of binary flags


        Parameters
        ----------
        bits : bytes
            Score bytes generated by PanKmer indexing

        Returns
        -------
        list
            List of binary flags indicating if genome at position x has the corresponding Kmer
            0: Genome doesn't have Kmer
            1: Genome has Kmer
        """        
        return score_byte_to_blist(bits, self.number_of_genomes)
        
#     def encode_score(self, present_samples):
        
    
    def decode_kmer(self, bits : bytes) -> int:
        """Convert Kmer bytes to an integer (C unsigned long long)

        Parameters
        ----------
        bits : bytes
            Bytes representing Kmer generated by PanKmer indexing

        Returns
        -------
        int
            Python integer represting the Kmer represented by bytes
        """        
        return int.from_bytes(bits, byteorder='big')
    
    def encode_kmer(self, kmer : str) -> int:
        """Generate a integer represting canonical Kmer

        Parameters
        ----------
        kmer : str
            Sequence representing one Kmer only

        Returns
        -------
        int
            Python integer representing canonical Kmer
        """        
        upper = (1<<(self.kmer_size*2))-1
        lower = 0
        kmer_byte = bytes(kmer.upper(), 'ascii')
        kmer_list = break_seq(kmer_byte, upper, lower)
        if len(kmer_list) > 1:
            raise ValueError(f"encode_kmer should be used for one Kmer of size {self.kmer_size} only! "
                             f"Please use get_sequence_kmerbits for a sequence larger than that.")
        return kmer_list[0]
    
    def get_sequence_kmerbits(self, seq : str, upper : int = None, lower : int = None) -> list:
        """Get canonical Kmers making up the sequence

        Parameters
        ----------
        seq : str
            Sequence to Kmerize

        Returns
        -------
        list
            list of Python integers representing the canonical Kmers
        """        
        if upper == None:
            upper = (1<<(self.kmer_size*2))-1
        if lower == None:
            lower = 0
        seq_byte = bytes(str(seq).upper(), 'ascii')
        kmer_bits = break_seq(seq_byte, upper, lower)
        
        return kmer_bits
    
    def get_kmer_scores(self, kmers : dict = None) -> dict:
        """Retrieve scores of Kmer in the Kmers dictionary.
        if no dictionary is supplied then retrieve all scores.

        Parameters
        ----------
        kmers : dict, optional
            Dictionary where the keys are target Kmers and values are default values
            to populate with if the Kmer isn't found in the index, by default None

        Returns
        -------
        dict
            Populated dictionary where keys are Kmers and values are scores
        """
        if kmers == None:
            # get all scores
            kmers = {}
            for kmer, score in self:
                kmers[kmer] = score
        else:
            # get only scores in kmers
            for kmer, score in self:
                kmer_int = self.decode_kmer(kmer)
                if kmer_int in kmers:
                    kmers[kmer_int] = score
        return kmers
    
    def get_sequence_score(self, seq : str, kmers : dict = None) -> list:
        """Retrieve scores of canonical Kmers in the sequence

        Parameters
        ----------
        seq : str
            Target sequence
        kmers : dict, optional
            dictionary of Kmer:Score to use to assign scores to Kmers in sequence.
            If no dictionary is supplied then the index will be used, by default None

        Returns
        -------
        list
            List of integers representing score of Kmer ending at postion x in the sequence
        """        
        kmer_bits = self.get_sequence_kmerbits(seq)
        if kmers == None:
            kmers = {kmer:None for kmer in kmer_bits}
            kmers = self.get_kmer_scores(kmers=kmers)
        return [kmers[kmer_bit] for kmer_bit in kmer_bits]

    def get_fasta_kmerbits(self, fasta_path : str, upper : int = None,
                           lower : int = None) -> set:
        """Get integers representing all canonical Kmers in a fasta file

        Parameters
        ----------
        fasta_path : str
            Path to fasta file
        upper : int, optional
            Python integer of the upper bound limit of canonical Kmer, by default None
        lower : int, optional
            Python integer of the lower bound limit of canonical Kmer, by default None

        Returns
        -------
        set
            A set of integers representing all canonical Kmers in fasta file
        """        
        kmer_set = {}
        with gzip_agnostic_open(fasta_path, 'rt') as infile:
            for record in SeqIO.parse(infile, 'fasta'):
                kmers = self.get_sequence_kmerbits(str(record.seq), upper, lower)
                kmer_set = kmer_set.union(set(kmers))
        return kmer_set
        
    def get_positional_fasta_kmerbits(self, fasta_path : str,
                                      contig_header : str = 'id') -> dict:
        """Get lists of integers representing each canonical Kmer in each position
        in each contig in the fasta file

        Parameters
        ----------
        fasta_path : str
            Path to fasta file
        contig_header : str, optional
            Header style to retrieve for contigs (id or description), by default 'id'

        Returns
        -------
        dict
            A dictionary where keys are contigs' names and values are lists of
            integers representing each canonical Kmer in each position in the corresponding contig
        """        
        upper = (1<<(kmer_size*2))-1
        lower = 0
        return get_positional_kmers(fasta_path, upper, lower, contig_header)

    def get_sequences_scores(self, sequences: dict, cpu: int = None) -> dict:
        """
        Get per-position scores for a dictionary of sequences

        Parameters
        ----------
        sequences : dict
            A dictionary of sequences. Key = name, value = sequence
        cpu : int, optional
            Number of cores to use. This will replicate memory used by parent function.

        Returns
        -------
        dict
            A dictionary of scores. Key = name, value = list of per-position scores
        """
        if cpu == None:
            cpu = self.threads
        # Get sequences kmers and sort them
        sequences_kmers = {name:self.get_sequence_kmerbits(seq) for name, seq in sequences.items()}
        combined_kmers = set()
        scored_kmers = {}
        for name, kmer_bits in sequences_kmers.items():
            for kmer_bit in kmer_bits:
                combined_kmers.add(kmer_bit)
        combined_kmers = sorted(list(combined_kmers))
        # divide kmers into buckets of kmers
        chunk_size = math.ceil(len(combined_kmers)/cpu)
        core_chunks = [[self.results_dir, {kmer:0 for kmer in combined_kmers[i:i+chunk_size]}] for i in range(0, len(combined_kmers), chunk_size)]
        # Update the kmers with their scores from the index
        if cpu == 1:
            results = map(get_sorted_kmer_scores, core_chunks)
        else:
            core_worker = Pool(cpu)
            results = core_worker.map(get_sorted_kmer_scores, core_chunks)
        for result in results:
            scored_kmers.update(result)
        
        return {name:self.get_sequence_score(seq, scored_kmers) for name, seq in sequences.items()}
    
    def get_regional_scores(self, reference: str, regions: dict,
                            cpu: int = None) -> dict:
        """
        Retrieve regions from the reference and return their per-position Kmer scores

        Parameters
        ----------
        reference : str
            Path to a reference file in GZIP fasta format.
        regions : dict
            Dictionary of regions. Key = name of contig, values = list of start and end positions to extract.
            If no start, end positions are given, the function will use the entire contig.
            example = {'contig_1': [[4, 10], [59, 90]], 'contig_2': []}
        cpu : int, optional
            Number of cores to use. This will replicate memory used by parent function., default to PKResults threads.

        Returns
        -------
        dict
            A nested dictionary of scores. Key = contig, value = dictionary where key = tuple of start and end positons
            and value = list of per-position scores.
            example: {'contig_1': {(4, 10): [scores], (59, 90): [scores]}}
        """
        if cpu == None:
            cpu = self.threads
        sequences = {}
        with gzip_agnostic_open(reference, 'rt') as infile:
            for record in SeqIO.parse(infile, 'fasta'):
                # sequences[record.id] = {}
                if record.id in regions:
                    if len(regions[record.id]) > 0:
                        for start, end in regions[record.id]:
                            seq  = str(record.seq)[start:end]
                            sequences[(record.id, start, end)] = seq
                    else:
                        seq = str(record.seq)
                        sequences[(record.id, 0, len(seq))] = seq
        sequence_scores = self.get_sequences_scores(sequences=sequences, cpu=cpu)
        sequences_reduced = {}
        for id, start, end in sequences.keys():
            if id not in sequences_reduced:
                sequences_reduced[id] = {}
            sequences_reduced[id][(start, end)] = sequence_scores[(id, start, end)]


        return sequences_reduced
    
    def get_collapsed_regional_scores(self, reference : str, regions : dict) -> dict:
        """
        Retrieve regions from the reference and return their per-position Kmer scores

        Parameters
        ----------
        reference : int
            Path to a reference file in GZIP fasta format.
        regions : int
            Dictionary of regions. Key = name of contig, values = list of start and end positions to extract.
            If no start, end positions are given, the function will use the entire contig.
            example = {'contig_1': [[4, 10], [59, 90]], 'contig_2': []}

        Returns
        -------
        dict
            _description_
        """        
        regional_scores = self.get_regional_scores(reference, regions)
        blevel_scores = {}
        for id, regions in regional_scores.items():
            blevel_scores[id] = {}
            for region, scores in regions.items():
                blevel_scores[id][region] = self.get_blevel_scores(scores)

        return blevel_scores

    def get_blevel_scores(self, scores: list) -> list:
        '''
        Get base level score for each position in the reference
        '''
        
        fillna_val = [0] * self.number_of_genomes
        scores = [scores[0] for i in range(self.kmer_size-1)] + scores
        for c, s in enumerate(scores[self.kmer_size:], start=self.kmer_size):
            for i in range(self.kmer_size): 
                if c-i < 0:
                    break
                scores[c-i] = tuple(max(b1, b2) for b1, b2 in zip((scores[c-i] or fillna_val), (s or fillna_val)))
                # When index does not contain ref, scores[c-i] or s may be NoneType, which causes an error
        return [(s or fillna_val) for s in scores]
    
    def get_regional_coverage(self, reference : str, regions : dict) -> dict:
        '''
        Get per position coverage for each region in the reference specified by the 
        regions dictionary.

        Parameters
        ----------
        reference: str, required
            A path to the reference file in fasta format
        regions: dict, required
            A dictionary whose keys are contigs in the refernce and the values
            are lists of start and end positons

        Returns
        -------
        A dictionary whose keys are contig names and start and end positions and 
        values are lists of number of samples in the index that have that position
        '''
        coverage = {}
        regional_scores = self.get_collapsed_regional_scores(reference, regions)
        for id, regions in regional_scores.items():
            coverage[id] = {}
            for region, scores in regions.items():
                coverage[id][region] = list(np.array(scores).sum(axis=1))
        
        return coverage

    def close(self):
        self.kmers_stream.close()
        self.scores_stream.close()
        if self.input_is_tar:
            self.tar.close()
        

# def update_genomes(index, genomes, genomes_dict):
#     results = PKResults(index)
#     index_genomes = results.genomes
#     genomes_size_dict = {}
#     for genome, genome_size in genomes_dict.items():
#         genomes_size_dict[genome] = genome_size
#     for genome in index_genomes:
#         genomes_size_dict[genome] = index_genomes[genome]
    
#     genomes = genomes + [i for i in index_genomes]
#     return genomes, genomes_size_dict


# def update_index(upper, lower, kmer_bitsize, score_bitsize, genomes, outdir, index_dir):
#     gnum = len(genomes)
#     kmers_post = {}
#     kmers = get_kmers(upper, lower, genomes)
#     print_err(f"Saving {lower}-{upper} kmers.")
#     kmers_out_path = join(outdir, f'kmers_{lower}_{upper}.b.gz')
#     scores_out_path = join(outdir, f'scores_{lower}_{upper}.b.gz')
#     kmers_exist = sorted(kmers.keys())

#     results = PKResults(index_dir)
#     total_genomes_number = score_bitsize + results.number_of_genomes
#     new_score_bitsize = math.ceil(total_genomes_number/8)
#     # Find lower bound position from index
#     initial_lower_bound = get_lower_bound(results.positions, lower)
#     # Move iterator from initial lower bound to actual lower bound
#     if initial_lower_bound != None:
#         results.seek_kmer(initial_lower_bound)
#         results.seek_score(initial_lower_bound)
#     lb_bit = int(lower).to_bytes(results.kmer_bitsize, byteorder="big", signed=False) # lower bound bit
#     ub_bit = int(upper).to_bytes(results.kmer_bitsize, byteorder="big", signed=False) # upper bound bit
#     results_iter = iter(results)
#     try:
#         index_kmer, index_score = next(results_iter)
#     except StopIteration:
#         index_kmer, index_score = [None, None]
#     while index_kmer != None and index_kmer < lb_bit:
#         try:
#             index_kmer, index_score = next(results_iter)
#         except StopIteration:
#             index_kmer, index_score = [None, None]    


#     dict_iter = iter(kmers_exist)
#     if kmers_exist:
#         dict_kmer = next(dict_iter)
#         dict_kmer_bit = dict_kmer.to_bytes(results.kmer_bitsize,
#                                         byteorder="big", signed=False)
#     else:
#         dict_kmer = None
#     count = 0
#     kmer_to_write = None
#     score_to_write = None
#     with gzip.open(kmers_out_path, 'wb') as kmers_out, gzip.open(scores_out_path,'wb') as scores_out:
#         with io.BufferedWriter(scores_out, buffer_size=1000*score_bitsize) as so_buffer ,\
#             io.BufferedWriter(kmers_out, buffer_size=1000*kmer_bitsize) as ko_buffer:
#             while (index_kmer != None and index_kmer <= ub_bit) or dict_kmer != None:
#                 if count%10000000 == 0 and count != 0:
#                     kmers_post[kmer_to_write] = count
#                     count = 0
#                 # Current samples don't have any Kmers left
#                 # but pre-existing index still has Kmers
#                 if dict_kmer == None and index_kmer != None:
#                     score = int.from_bytes(index_score, 'big', signed=False)
#                     index_kmer_int = int.from_bytes(index_kmer, 'big', signed=False)
#                     kmer_to_write = index_kmer_int
#                     score_to_write = score << gnum
#                     try:
#                         index_kmer, index_score = next(results_iter)
#                     except StopIteration:
#                         index_kmer, index_score = [None, None]
#                 # Current samples have Kmers left
#                 # but pre-existing index doesn't have any Kmers left
#                 elif dict_kmer != None and index_kmer == None:
#                     kmer_to_write = dict_kmer
#                     score_to_write = kmers[dict_kmer]
#                     try:
#                         dict_kmer = next(dict_iter)
#                         dict_kmer_bit = dict_kmer.to_bytes(results.kmer_bitsize,
#                                                         byteorder="big", signed=False)
#                     except StopIteration:
#                         dict_kmer = None
#                 # Current sample Kmer and pre-existing Kmer is the same
#                 elif index_kmer == dict_kmer_bit:
#                     score = int.from_bytes(index_score, 'big', signed=False)
#                     new_score = (score << gnum) | kmers[dict_kmer]
#                     # kmers[dict_kmer_bit] = new_score
#                     kmer_to_write = dict_kmer
#                     score_to_write = new_score
#                     try:
#                         dict_kmer = next(dict_iter)            
#                         dict_kmer_bit = dict_kmer.to_bytes(results.kmer_bitsize,
#                                                     byteorder="big", signed=False)
#                     except StopIteration:
#                         dict_kmer = None

#                     try:
#                         index_kmer, index_score = next(results_iter)
#                     except StopIteration:
#                         index_kmer, index_score = [None, None]
#                 # Add pre-existing Kmer
#                 elif index_kmer < dict_kmer_bit or dict_kmer == None:
#                     score = int.from_bytes(index_score, 'big', signed=False)
#                     index_kmer_int = int.from_bytes(index_kmer, 'big', signed=False)
#                     new_score = score << gnum
#                     # kmers[index_kmer] = new_score
#                     kmer_to_write = index_kmer_int
#                     score_to_write = new_score

#                     try:
#                         index_kmer, index_score = next(results_iter)
#                     except StopIteration:
#                         index_kmer, index_score = [None, None]
#                 # Add current sample Kmer
#                 else:
#                     kmer_to_write = dict_kmer
#                     score_to_write = kmers[dict_kmer]
#                     try:
#                         dict_kmer = next(dict_iter)
#                         dict_kmer_bit = dict_kmer.to_bytes(results.kmer_bitsize,
#                                                         byteorder="big", signed=False)
#                     except StopIteration:
#                         dict_kmer = None
#                 a = ko_buffer.write(
#                     kmer_to_write.to_bytes(kmer_bitsize,
#                     byteorder="big", signed=False))
#                 b = so_buffer.write(
#                     score_to_write.to_bytes(new_score_bitsize,
#                     byteorder="big", signed=False))
#                 count += 1
#             if kmer_to_write != None and kmer_to_write not in kmers_post:
#                 kmers_post[kmer_to_write] = count-1

#     return kmers_post


# def count_scores(scores_file, score_bitsize):
#     scores_counts = {}
#     # Read kmers and scores files in byte mode
#     with gzip.open(scores_file, "rb") as score_in:
#         # Buffer file reading
#         score_buffer = io.BufferedReader(score_in)
#         # Read score/kmer sized bytes from the files
#         score = score_buffer.read(score_bitsize)
#         while score:
#             if score in scores_counts:
#                 scores_counts[score]+=1
#             else:
#                 scores_counts[score] = 1
#             score = score_buffer.read(score_bitsize)

#     return scores_counts


def get_kmers_wrapper(seq, upper, lower):
    seq_byte = bytes(str(seq).upper(), 'ascii')
    kmers = break_seq(seq_byte, upper, lower)
    return kmers


def index_wrapper(genomes_input, outdir: str, split_memory: int = 1,
                  threads: int = 1, index: str = '', fraction: float = 1.0,
                  k=31):
    if basename(outdir).endswith('.tar'):
        output_is_tar = True
        outdir = join(dirname(outdir), basename(outdir)[:-4])
    else:
        output_is_tar = False

    if not isinstance(genomes_input, (tuple, list)):
        genomes_input = list(genomes_input) if isinstance(genomes_input, set) else [genomes_input]
    if len(genomes_input) == 1 and isfile(genomes_input[0]) and tarfile.is_tarfile(genomes_input[0]):
        input_is_tar = True
        with tarfile.open(genomes_input[0]) as tar:
            genomes = [tarinfo.name for tarinfo in tar if tarinfo.isreg()]
    else:
        input_is_tar = False
        genomes = list(itertools.chain.from_iterable(
            ([join(g, f) for f in sorted(listdir(g))] if isdir(g) else [g])
            for g in genomes_input))
        # Check if input files exist and are files
        for genome in genomes:
            if not exists(genome) or not isfile(genome):
                raise RuntimeError(f"{genome} does not exist or is not a file!")
                return 1

    # Make the output directory if it doesn't exist
    if not exists(outdir):
        mkdir(outdir)

    print_err('Recording genome sizes')
    genomes_dict = {}
    for genome in genomes:
        print_err(f'Measuring {genome}')
        genomes_dict[genome] = 0
        if input_is_tar:
            tar = tarfile.open(genomes_input[0])
            infile = gzip_agnostic_open(genome, 'rt', tar=tar)
        else:
            infile = gzip_agnostic_open(genome, 'rt')
        for record in SeqIO.parse(infile, 'fasta'):
            genomes_dict[genome] += len(str(record.seq))
        infile.close()
        if input_is_tar:
            tar.close()

    positions_dictionary, mem_blocks = run_index((str(genomes_input[0]) if input_is_tar else ''),
            genomes, str(outdir),
            split_memory=split_memory, threads=threads,
            index=index, input_is_tar=input_is_tar, fraction=fraction,
            kmersize=kmer_size())
    
    # if index:
    #     genomes, genomes_dict = update_genomes(index, genomes, genomes_dict)

    print_err("Saving metadata.")
    metadata_dict = {'kmer_size': kmer_size(),
        'version': __version__,
        'genomes': {c:g for c, g in enumerate(genomes)},
        'genome_sizes': genomes_dict,
        'positions': dict(sorted(positions_dictionary.items(), key=itemgetter(1))),
        'mem_blocks': mem_blocks
    }
    with open(f'{outdir}/metadata.json', 'w') as outfile:
        json.dump(metadata_dict, outfile)
    if output_is_tar:
        with tarfile.open(f'{outdir}.tar', 'w') as tar:
            tar.add(outdir)
        shutil.rmtree(outdir)

def run_index_wrapper(args):
    if args.time:
        start = time.time()
    # index = args.index
    # index_wrapper(genomes_input, fraction, 31, output)
    index_wrapper(args.genomes, args.output, split_memory=args.split_memory,
                  threads=args.threads, index='', k=31,
                  fraction=args.fraction)
    if args.time:
        stop = time.time()
        print(f'Indexed in {(stop - start) / 60:.2f} minutes')


def run_count(args):
    kmer_counts = count_kmers(*(PKResults(i) for i in args.index), names=args.index)
    kmer_counts.to_csv(sys.stdout, sep='\t')


def run_collect(args):
    sat_df = collect(PKResults(args.index), args.output, title=args.title,
                        width=args.width, height=args.height,
                        palette=args.color_palette, alpha=args.alpha,
                        linewidth=args.linewidth, conf=args.conf,
                        contours=args.contours, legend_loc=args.legend_loc)
    if args.table:
        sat_df.to_csv(args.table, sep='\t', index=False)


def run_upset(args):
    if args.time:
        start = time.time()
    upset(PKResults(args.input), args.output, args.genomes,
          vertical=args.vertical,
          show_counts=args.show_counts,
          min_subset_size=args.min_subset_size,
          max_subset_size=args.max_subset_size,
          exclusive=args.exclusive,
          table=args.table)
    if args.time:
        stop = time.time()
        print(f'UpSet plot generated in {(stop - start) / 60:.2f} minutes')


def run_subset(args):
    if args.time:
        start = time.time()
    subset(PKResults(args.input), args.output, args.genomes,
          exclusive=args.exclusive)
    if args.time:
        stop = time.time()
        print(f'subset index generated in {(stop - start) / 60:.2f} minutes')


def run_adjacency_matrix(args):
    if args.time:
        start = time.time()
    results = PKResults(args.input_dir)
    output = args.output
    df = get_adjacency_matrix(results)
    df.to_csv(output)
    if args.time:
        stop = time.time()
        print(f'Matrix generated in {(stop - start) / 60:.2f} minutes')


def run_tree(args):
    adj_matrix = pd.read_csv(args.input, index_col=0)
    tree(adj_matrix, newick=args.newick, metric=args.metric, method=args.method,
         transformed_matrix=args.transformed_matrix)


def run_clustermap(args):
    adj_matrix = pd.read_csv(args.input, index_col=0)
    clustermap(adj_matrix, args.output, cmap=args.colormap, width=args.width,
        height=args.height, metric=args.metric, method=args.method,
        heatmap_tick_pos=args.heatmap_ticks,
        cbar_tick_pos=args.cbar_ticks, dendrogram_ratio=args.dend_ratio,
        dendrogram_spacer=args.dend_spacer)



def run_regcoverage(args):
    if args.output:
        reg_coverage(*(PKResults(i) for i in args.index), ref=args.ref,
            coords=args.coords, output_file=args.output, bgzip=args.bgzip,
            genes=args.genes, flank=args.flank, processes=args.processes)
    else:
        for chrom, start, end, *values in reg_coverage(
            *(PKResults(i) for i in args.index), ref=args.ref,
                coords=args.coords, genes=args.genes, flank=args.flank,
                processes=args.processes):
            print(chrom, start, end, *values, sep='\t')


def run_genome_coverage(args):
    genome_coverage(*(PKResults(i) for i in args.index), output=args.output,
        ref=args.ref, chromosomes=args.chromosomes, output_table=args.table,
        groups=args.groups, title=args.title, x_label=args.x_label,
        legend=args.legend,
        legend_title=args.legend_title, legend_loc=args.legend_loc,
        bin_size=args.bin_size, width=args.width, height=args.height,
        color_palette=args.color_palette, alpha=args.alpha,
        linewidth=args.linewidth, processes=args.processes)


def run_genome_coverage_plot(args):
    plotting_data=pd.read_table(args.table)
    x_label = args.x_label if args.x_label else plotting_data.columns[1]
    legend_title = args.legend_title if args.legend_title else plotting_data.columns[3]
    columns = (
        plotting_data.columns[0],
        x_label,
        plotting_data.columns[2],
        legend_title,
        f'{legend_title}_chrom'
    )
    plotting_data.columns = columns
    if args.chromsizes:
        sizes = pd.read_table(args.chromsizes, header=None)
        sizes.columns = 'name', 'size'
    else:
        sizes = None
    genome_coverage_plot(plotting_data, output=args.output,
        groups=args.groups, loci=args.loci, sizes=sizes,
        title=args.title, x_label=x_label, legend=args.legend,
        legend_title=legend_title,
        legend_loc=args.legend_loc, width=args.width, height=args.height,
        color_palette=args.color_palette, alpha=args.alpha,
        linewidth=args.linewidth)


def run_coverage_heatmap(args):
    coverage_heatmap(PKResults(args.index), args.refs, args.features,
        args.output, n_features=args.n_features, width=args.width,
        height=args.height)


def run_dryrun(args):
    metadata_dict = dryrun(args.genomes, split_memory=args.split_memory, threads=args.threads)
    json.dump(metadata_dict, sys.stdout)


def run_download_example(args):
    download_example(args.dir, args.bacterial, args.n_samples)


def main():
    parser = argparse.ArgumentParser(
        add_help=True)
    parser.add_argument('--version', action='version',
                    version='%(prog)s {version}'.format(version=__version__))
    subparsers = parser.add_subparsers(dest='func')
    index_parser = subparsers.add_parser('index',
        help='generate k-mer index')
    index_parser.add_argument(
        '-g', '--genomes', metavar='<genomes[.tar]>',
        required=True,
        nargs='+',
        help='directory containig input genomes')
    index_parser.add_argument(
        '-o', '--output', metavar='<output[.tar]>',
        required=True,
        help='output directory or tarfile that will contain the k-mer index')
    index_parser.add_argument(
        '--split-memory', metavar='<int>',
        type=int, help=(
        'Parallel.'
        'This splits the indexing into multiple rounds; reducing memory.'
        ), default=1)
    index_parser.add_argument(
        '-t', '--threads', metavar='<int>',
        type=int, help=('Number of threads to use'), default=1)
    index_parser.add_argument(
        '--fraction', metavar='<float>', type=float, default=1.0, help=(
        'Fraction of k-mer minimizers to use'))
    # index_parser.add_argument(
    #     '-i', '--index', metavar='<index[.tar]>',
    #     dest='index', required=False, default='',
    #     help=('Path to existing index to update.')
    # )
    index_parser.add_argument(
        '--time', action='store_true',
        help='Report the time required to execute'
    )
    index_parser.set_defaults(func=run_index_wrapper)

    count_parser = subparsers.add_parser('count',
        help='count k-mers in one or more indexes')
    count_parser.add_argument(
        '-i', '--index', metavar='<index[.tar]>', type=str, action='store',
        dest='index', required=True, nargs='+', help='a k-mer index')
    count_parser.set_defaults(func=run_count)

    collect_parser = subparsers.add_parser('collect',
        help='calculate k-mer collection curve')
    collect_parser.add_argument(
        '-i', '--index', metavar='<index[.tar]>', type=str, action='store',
        required=True, help='a k-mer index')
    collect_parser.add_argument(
        '-o', '--output', metavar='<output.{pdf,png,svg}>', type=str,
        action='store', dest='output',
        help='destination file for plot')
    collect_parser.add_argument(
        '-t', '--table', metavar='<output-table.tsv>',
        help='output TSV file containing plotted data')
    collect_parser.add_argument('--title', metavar='<"Plot title">',
        help='set the title for the plot')
    collect_parser.add_argument('--width', metavar='<float>', type=float,
        default=4.0, help='set width of figure in inches [4]')
    collect_parser.add_argument('--height', metavar='<float>', type=float,
        default=3.0, help='set height of figure in inches [3]')
    collect_parser.add_argument('--color-palette', metavar='<#color>', nargs='+',
        default=COL_COLOR_PALETTE, help='color palette to use')
    collect_parser.add_argument('--alpha', metavar='<float>', type=float,
        default=1.0, help='transparency value for lines [1.0]')
    collect_parser.add_argument('--linewidth', metavar='<int>', type=int,
        default=3, help='line width for plot [3]')
    conf_or_cont = collect_parser.add_mutually_exclusive_group()
    conf_or_cont.add_argument('--conf', action='store_true',
        help='calculate confidence intervals for collection curves')
    conf_or_cont.add_argument('--contours', metavar='<int>', type=int,
        nargs='+', help='set contours for collection curves (in percent)')
    collect_parser.add_argument('--legend-loc',
        choices=('best', 'upper left', 'upper right', 'lower left',
                 'lower right', 'outside'),
        default='best', help='location of legend [best]')
    collect_parser.set_defaults(func=run_collect)

    upset_parser = subparsers.add_parser('upset', help='generate upset plot')
    upset_parser.add_argument(
        '-i', '--input', metavar='<index[.tar]>',
        required=True, help='a k-mer index')
    upset_parser.add_argument(
        '-o', '--output', metavar='<output.{pdf,png,svg}>', required=True,
        help='destination file for upset plot')
    upset_parser.add_argument(
        '-g', '--genomes', metavar='<genome>', required=True, nargs='+',
        help='list of genomes to include')
    upset_parser.add_argument(
        '-v', '--vertical', action='store_true',
        help='draw the plot vertically')
    upset_parser.add_argument(
        '-x', '--exclusive', action='store_true',
        help='exclude k-mers that occur in genomes other than the input set')
    upset_parser.add_argument(
        '-t', '--table', metavar='<table.tsv[.gz]>',
        help='write (optionally compressed) table of values in tsv format')
    upset_parser.add_argument(
        '--show-counts', action='store_true',
        help='show counts for each subset')
    upset_parser.add_argument(
        '--min-subset-size', metavar='<int>', type=int,
        help='show only subsets larger than a minimum size')
    upset_parser.add_argument(
        '--max-subset-size', metavar='<int>', type=int,
        help='show only subsets smaller than a maximum size')
    upset_parser.add_argument(
        '--time', action='store_true',
        help='report the time required to execute')
    upset_parser.set_defaults(func=run_upset)

    subset_parser = subparsers.add_parser('subset', help='subset an index')
    subset_parser.add_argument(
        '-i', '--input', metavar='<input-index[.tar]>',
        required=True, help='a k-mer index')
    subset_parser.add_argument(
        '-o', '--output', metavar='<output-index[.tar]>', required=True,
        help='destination file for subset index')
    subset_parser.add_argument(
        '-g', '--genomes', metavar='<genome>', required=True, nargs='+',
        help='list of genomes to include '
    )
    subset_parser.add_argument(
        '-x', '--exclusive', action='store_true',
        help='exclude k-mers that occur in genomes other than the input set'
    )
    subset_parser.add_argument(
        '--time', action='store_true',
        help='report the time required to execute'
    )
    subset_parser.set_defaults(func=run_subset)

    adjmat_parser = subparsers.add_parser('adj-matrix',
        help='generate adjacency matrix')
    adjmat_parser.add_argument(
        '-i', '--input', metavar='<index[.tar]>',
        dest='input_dir', required=True, help='a k-mer index')
    adjmat_parser.add_argument(
        '-o', '--output', metavar='<adjmatrix.csv>',
        dest='output', required=True,
        help='destination file for adjacency matrix')
    adjmat_parser.add_argument(
        '--time', action='store_true',
        help='Report the time required to execute')
    adjmat_parser.set_defaults(func=run_adjacency_matrix)

    tree_parser = subparsers.add_parser('tree',
        help='generate a heirarchical clustering tree from an adjacency matrix')
    tree_parser.add_argument(
        '-i', '--input', metavar='<adjmatrix.csv>',
        dest='input', required=True, help='adjacency matrix file')
    tree_parser.add_argument(
        '-n', '--newick', action='store_true', dest='newick',
        help='output tree in NEWICK format'
    )
    tree_parser.add_argument(
        '--metric', choices=('intersection', 'jaccard', 'overlap'),
        type=str, action='store', dest='metric', default='intersection',
        help='similarity metric [intersection]')
    tree_parser.add_argument(
        '--method', choices=('single', 'complete', 'average', 'weighted', 'centroid'),
        type=str, action='store', dest='method', default='complete',
        help='clustering method [complete]')
    tree_parser.add_argument(
        '--transformed-matrix', metavar='<matrix.csv>',
        help='Write similarity transformed matrix to file')
    tree_parser.set_defaults(func=run_tree)

    clustermap_parser = subparsers.add_parser('clustermap',
        help='plot a clustered heatmap from the adjacency matrix')
    clustermap_parser.add_argument(
        '-i', '--input', metavar='<adjmatrix.csv>', type=str, action='store',
        dest='input', required=True,
        help='adjacency matrix file')
    clustermap_parser.add_argument(
        '-o', '--output', metavar='<adjmatrix.{pdf,png,svg}>', type=str, action='store',
        dest='output', required=True,
        help='destination file for plot')
    clustermap_parser.add_argument(
        '--metric', choices=('intersection', 'jaccard', 'overlap'),
        type=str, action='store', dest='metric', default='intersection',
        help='similarity metric [intersection]')
    clustermap_parser.add_argument(
        '--method', choices=('single', 'complete', 'average', 'weighted', 'centroid'),
        type=str, action='store', dest='method', default='complete',
        help='clustering method [complete]')
    clustermap_parser.add_argument(
        '--colormap', metavar='<color_map>', type=str, action='store',
        default='mako_r', help='seaborn colormap for plot [mako_r]')
    clustermap_parser.add_argument(
        '--width', metavar='<float>', type=float, action='store',
        default=7.0, help='width of plot in inches [7]')
    clustermap_parser.add_argument(
        '--height', metavar='<float>', type=float, action='store',
        default=7.0, help='height of plot in inches [7]')
    clustermap_parser.set_defaults(func=run_clustermap)
    clustermap_parser.add_argument(
        '--heatmap-ticks', choices=('left', 'right'),
        default='left',
        help='Position of heatmap ticks. Must be "left" or "right" [left]')
    clustermap_parser.add_argument(
        '--cbar-ticks', choices=('left', 'right'),
        default='left',
        help='Position of color bar ticks. Must be "left" or "right" [left]')
    clustermap_parser.add_argument(
        '--dend-ratio', metavar='<float>', type=float, default=0.2,
        help='Fraction of plot width used for dendrogram [0.2]')
    clustermap_parser.add_argument(
        '--dend-spacer', metavar='<float>', type=float, default=0.1,
        help='Fraction of plot width used as spacer between dendrogram and heatmap [0.1]')
    clustermap_parser.set_defaults(func=run_clustermap)

    regcov_parser = subparsers.add_parser('reg-coverage',
        help='generate regional coverage')
    regcov_parser.add_argument(
        '-i', '--index', metavar='<index[.tar]>', type=str, action='store',
        dest='index', required=True, nargs='+', help='index')
    regcov_parser.add_argument(
        '-r', '--reference', metavar='<reference.fa.gz>', type=str, action='store',
        dest='ref', required=True, help='reference')
    regcov_parser.add_argument(
        '-c', '--coords', metavar='<chr:start-end>', type=str, action='store',
        dest='coords', required=True, help='genomic coordinates')
    regcov_parser.add_argument(
        '-o', '--output', metavar='<output.bdg[.gz]>', type=str,
        dest='output', help='write to file instead of standard output')
    regcov_parser.add_argument(
        '-b', '--bgzip', action='store_true',
        dest='bgzip', help='block compress the output file')
    regcov_parser.add_argument(
        '-g', '--genes', metavar='<genes.gff3[.gz]>', type=str,
        dest='genes', help='gff file of gene coordinates')
    regcov_parser.set_defaults(func=run_regcoverage)
    regcov_parser.add_argument(
        '-f', '--flank', metavar='<int>', type=int, default=0,
        dest='flank', help='size of flanking regions')
    regcov_parser.add_argument(
        '-p', '--processes', metavar='<int>', type=int, default=1,
        dest='processes', help='number of processes to use')
    regcov_parser.set_defaults(func=run_regcoverage)

    genomecov_parser = subparsers.add_parser('genome-coverage',
        help='generate genomic coverage')
    genomecov_parser.add_argument(
        '-i', '--index', metavar='<index[.tar]>', type=str, action='store',
        dest='index', required=True, nargs='+', help='index')
    genomecov_parser.add_argument(
        '-o', '--output', metavar='<output.{pdf,png,svg}>', type=str,
        action='store', dest='output', required=True,
        help='destination file for plot')
    genomecov_parser.add_argument(
        '-r', '--reference', metavar='<reference.fa.gz>', type=str,
        action='store', dest='ref', required=True,
        help='reference in BGZIP compressed FASTA format')
    genomecov_parser.add_argument(
        '-c', '--chromosomes', metavar='<chrX>', type=str, action='store',
        dest='chromosomes', required=True, nargs='+',
        help='chromosomes to include')
    genomecov_parser.add_argument(
        '-t', '--table', metavar='<output-table.tsv>',
        help='output TSV file containing plotted data')
    genomecov_parser.add_argument('--groups', metavar='<"Group">', nargs='+',
        help='list of groups for provided indexes [0]')
    genomecov_parser.add_argument('--title', metavar='<"Plot title">',
        default='Coverage', help='set the title for the plot')
    genomecov_parser.add_argument('--x-label', metavar='<"Label">',
        default='Chromosome', help='set the x-axis label for the plot')
    genomecov_parser.add_argument('--legend', action='store_true',
        help='include a legend with the plot')
    genomecov_parser.add_argument('--legend-title', metavar='<"Title">',
        default='Group', help='title of legend')
    genomecov_parser.add_argument('--legend-loc',
        choices=('best', 'upper left', 'upper right', 'lower left',
                 'lower right', 'outside'),
        default='best', help='location of legend [best]')
    genomecov_parser.add_argument('--bin-size', metavar='<int>', type=int, default=0,
        choices=(-2,-1,0,1,2),
        help=('Set bin size. The input <int> is converted to the bin size by '
              'the formula: 10^(<int>+6) bp. The default value is 0, i.e. '
              '1-megabase bins. [0]'))
    genomecov_parser.add_argument('--width', metavar='<float>', type=float,
        default=7.0, help='set width of figure in inches [7]')
    genomecov_parser.add_argument('--height', metavar='<float>', type=float,
        default=3.0, help='set height of figure in inches [3]')
    genomecov_parser.add_argument('--color-palette', metavar='<#color>', nargs='+',
        default=COLOR_PALETTE, help='color palette to use')
    genomecov_parser.add_argument('--alpha', metavar='<float>', type=float,
        default=0.5, help='transparency value for lines [0.5]')
    genomecov_parser.add_argument('--linewidth', metavar='<int>', type=int,
        default=3, help='line width for plot [3]')
    genomecov_parser.add_argument('--processes', metavar='<int>', type=int,
        default=1, help='number of processes to use')
    genomecov_parser.set_defaults(func=run_genome_coverage)

    gcplot_parser = subparsers.add_parser('gcplot',
        help='generate a plot from genomic coverage results')
    gcplot_parser.add_argument(
        '-t', '--table', metavar='<genomecov.tsv>', type=str, action='store',
        dest='table', required=True, help='genomic coverage results')
    gcplot_parser.add_argument(
        '-o', '--output', metavar='<output.{pdf,png,svg}>', type=str,
        action='store', dest='output', required=True,
        help='destination file for plot')
    gcplot_parser.add_argument('--groups', metavar='<"Group">', nargs='+',
        help='list of groups for provided indexes')
    gcplot_parser.add_argument('--loci', metavar='<"chr:pos:name">', nargs='+',
        help='list of loci to mark on plot')
    gcplot_parser.add_argument('--chromsizes', metavar='<file.chrom.sizes>',
        help='chromsizes file of the reference used to generate the table')
    gcplot_parser.add_argument('--title', metavar='<"Plot title">',
        help='set the title for the plot')
    gcplot_parser.add_argument('--x-label', metavar='<"Label">',
        help='set x-axis label for the plot')
    gcplot_parser.add_argument('--legend', action='store_true',
        help='include a legend with the plot')
    gcplot_parser.add_argument('--legend-title', metavar='<"Title">',
        help='title of legend')
    gcplot_parser.add_argument('--legend-loc',
        choices=('best', 'upper left', 'upper right', 'lower left',
                 'lower right', 'outside'),
        default='best', help='location of legend [best]')
    gcplot_parser.add_argument('--width', metavar='<float>', type=float,
        default=7.0, help='set width of figure in inches [7]')
    gcplot_parser.add_argument('--height', metavar='<float>', type=float,
        default=3.0, help='set height of figure in inches [3]')
    gcplot_parser.add_argument('--color-palette', metavar='<#color>', nargs='+',
        default=COLOR_PALETTE, help='color palette to use')
    gcplot_parser.add_argument('--alpha', metavar='<float>', type=float,
        default=0.5, help='transparency value for lines [0.5]')
    gcplot_parser.add_argument('--linewidth', metavar='<int>', type=int,
        default=3, help='line width for plot [3]')
    gcplot_parser.set_defaults(func=run_genome_coverage_plot)

    covhm_parser = subparsers.add_parser('cov-heatmap',
        help='draw coverage heatmap')
    covhm_parser.add_argument(
        '-i', '--index', metavar='<index[.tar]>', type=str, action='store',
        dest='index', required=True, help='index')
    covhm_parser.add_argument(
        '-r', '--refs', metavar='<reference.fa.gz>', type=str, action='store',
        dest='refs', required=True, nargs='+', help='references')
    covhm_parser.add_argument(
        '-f', '--features', metavar='<features.gff3>', type=str, action='store',
        dest='features', required=True, nargs='+',
        help='GFF files defining features (such as genes)')
    covhm_parser.add_argument(
        '-o', '--output', metavar='<output.{pdf,png,svg}>', type=str, action='store',
        dest='output', required=True, help='output file (must end with ".png")')
    covhm_parser.add_argument(
        '--n-features', metavar='<int>', type=int, action='store',
        dest='n_features',
        help='use to limit plotting to the first n features for each genome')
    covhm_parser.add_argument(
        '--width', metavar='<float>', type=float, action='store',
        dest='width', default=7, help='width of plot in inches', )
    covhm_parser.add_argument(
        '--height', metavar='<float>', type=float, action='store',
        dest='height', default=7, help='height of plot in inches', )
    covhm_parser.set_defaults(func=run_coverage_heatmap)

    dryrun_parser = subparsers.add_parser('dryrun',
        help='perform a dry run of indexing and print metadata')
    dryrun_parser.add_argument(
        '-g', '--genomes', metavar='<genomes[.tar]>',
        required=True,
        nargs='+',
        help='directory containig input genomes')
    dryrun_parser.add_argument(
        '--split-memory', metavar='<int>',
        type=int, help=(
        'Parallel.'
        'This splits the indexing into multiple rounds; reducing memory.'
        ), default=1)
    dryrun_parser.add_argument(
        '-t', '--threads', metavar='<int>',
        type=int, help=('Number of threads to use'), default=1)
    dryrun_parser.set_defaults(func=run_dryrun)

    download_parser = subparsers.add_parser('download-example',
        help='download an example dataset')
    download_parser.add_argument(
        '-d', '--dir', metavar='<dir/>', type=str, action='store',
        dest='dir', default=EXAMPLE_DATA_DIR,
        help='destination directory for example data')
    download_parser.add_argument(
        '-b', '--bacterial', action='store_true', dest='bacterial',
        help='if True, download bacterial genomes')
    download_parser.add_argument(
        '-n', '--n-samples', metavar='<int>', type=int, default=1, action='store', dest='n_samples',
        help='number of bacterial samples to download, max 164 [1]')
    download_parser.set_defaults(func=run_download_example)

    args = parser.parse_args()
    args.func(args)
