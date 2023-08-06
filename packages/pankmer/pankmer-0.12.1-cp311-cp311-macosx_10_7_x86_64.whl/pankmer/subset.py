import gzip
import os
import os.path
import io
import math
import tarfile
import shutil
import json
from itertools import compress
from pankmer.index import load_scores, dump_scores, subset_scores
from pankmer.version import __version__

def bools_to_score(bools):
    return int(''.join(str(int(b)) for b in bools), base = 2)


def generate_subset_scores(pk_results, genomes):
    genome_set = set(genomes)
    for kmer, i, score in pk_results:
        memberships = set(compress(pk_results.genomes, (x==1 for x in score)))
        inter = memberships.intersection(genome_set)
        if inter:
            yield kmer, i
            # yield kmer, i, bools_to_score(g in memberships for g in genomes)


def generate_subset_scores_exclusive(pk_results, genomes):
    genome_set = set(genomes)
    for kmer, i, score in pk_results:
        memberships = set(compress(pk_results.genomes, (x==1 for x in score)))
        inter = memberships.intersection(genome_set)
        diff = memberships - genome_set
        if inter and not diff:
            yield kmer, i
            # yield kmer, i, bools_to_score(g in memberships for g in genomes)


def subset(pk_results, output, genomes, exclusive=False):
    metadata_dict = {
        "kmer_size": pk_results.kmer_size,
        "version": __version__,
        "genomes": dict(enumerate(genomes)),
        "genome_sizes": {g: pk_results.genomes[g] for g in genomes},
        "positions": {},
        "mem_blocks": pk_results.mem_blocks
    }
    kmer_bitsize = math.ceil(((pk_results.kmer_size*2))/8)
    i_bitsize = 8
    output_is_tar = output.endswith('.tar')
    output_dir = output[:-4] if output_is_tar else output
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    idx_map = subset_scores(pk_results.results_dir,
        (pk_results.results_dir if pk_results.input_is_tar else ''),
        tuple(pk_results.genomes), genomes, os.path.join(output_dir, 'scores.pks'))
    idx_map_bytes = {i.to_bytes(i_bitsize, byteorder="big", signed=False):
                         j.to_bytes(i_bitsize, byteorder="big", signed=False)
                     for i, j in idx_map.items()}
    kmers_out_path = os.path.join(output_dir, f'kmers.bgz')
    indices_out_path = os.path.join(output_dir, f'indices.bgz')
    with gzip.open(kmers_out_path, 'wb') as kmers_out, gzip.open(indices_out_path, 'wb') as indices_out:
        with io.BufferedWriter(indices_out, buffer_size=1000*i_bitsize) as io_buffer ,\
            io.BufferedWriter(kmers_out, buffer_size=1000*kmer_bitsize) as ko_buffer:
            count = 0
            for kmer, i in (generate_subset_scores_exclusive(pk_results, genomes) if exclusive
                else generate_subset_scores(pk_results, genomes)):
                ko_buffer.write(kmer)
                io_buffer.write(idx_map_bytes[i])
                if count%10000000 == 0 and count != 0: 
                    metadata_dict['positions'][str(pk_results.decode_kmer(kmer))] = count
                    count = 0
                count += 1
    with open(f'{output_dir}/metadata.json', 'w') as f:
        json.dump(metadata_dict, f)
    if output_is_tar:
        with tarfile.open(output, 'w') as tar:
            tar.add(output_dir)
        shutil.rmtree(output_dir)
