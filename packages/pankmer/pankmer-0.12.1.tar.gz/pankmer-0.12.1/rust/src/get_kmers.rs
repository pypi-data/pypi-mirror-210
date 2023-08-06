// Imports =====================================================================
use bio::io::fasta;
use niffler;
use rustc_hash::FxHashMap as HashMap;
use tar::Archive;
use crate::{Kmer, Score, ScoreList, ScoreToIDX, PKTbl, PKGenomes};
use crate::helpers::{print_err, genome_name};
use crate::decompose_kmers::break_seq;
use crate::pkidx::PKIdx;

// Functions ===================================================================
#[inline]
pub fn genome_index_to_byte_idx_and_bit_mask(i: usize, nbytes: usize) -> (usize, u8) {
    let byte_idx = nbytes - 1 - (i / 8);
    let bit_mask = match i%8 {
        0 => { 1u8 }
        1 => { 2u8 }
        2 => { 4u8 }
        3 => { 8u8 }
        4 => { 16u8 }
        5 => { 32u8 }
        6 => { 64u8 }
        7 => { 128u8 }
        _ => panic!("This ought to be impossible.")
    };
    return (byte_idx, bit_mask)
}

fn parse_record(result: Result<bio::io::fasta::Record, std::io::Error>) -> Vec<u8> {
    let record = result.expect("Error during fasta record parsing");
    record.seq().to_ascii_uppercase()
}

fn update_score(kmers: &PKTbl, kmer: &Kmer, score_list: &ScoreList,
                byte_idx: usize, bit_mask: u8, nbytes: usize) -> Score {
    let new_score: Score = match kmers.get(&kmer) {
        Some(score_idx) => {
            let mut score: Score = score_list[*score_idx].clone();
            score[byte_idx] = score[byte_idx] | bit_mask;
            score
        },
        None => {
            let mut score: Score = vec![0; nbytes];
            score[byte_idx] = bit_mask;
            score
        }
    };
    new_score
}

pub fn get_kmers(kmersize: usize, kmer_fraction: f64,
             upper: Kmer, lower: Kmer, genomes: PKGenomes, tar_file: &str) -> PKIdx {
    let mut kmers: PKTbl = HashMap::default();
    let mut score_to_idx: ScoreToIDX = HashMap::default();
    let mut score_list: ScoreList = Vec::new();
    let nbytes = (genomes.len() + 7) / 8;
    let cutoff = (kmer_fraction * Kmer::MAX as f64) as Kmer;
    let gnum: usize = genomes.len();

    if tar_file.len() > 0 {
        let (tar, _format) = niffler::from_path(tar_file).expect(
            &format!("File not found: {}", tar_file));
        for (i, f) in Archive::new(tar).entries().expect("Can't read tar file").enumerate() {
            let (byte_idx, bit_mask) = genome_index_to_byte_idx_and_bit_mask(i, nbytes);
            let f = f.expect("Error reading tar archive");
            let genome_path = f.header().path().expect("Error reading tar archive");
            if !((&genome_path).ends_with("fasta")
                 || (&genome_path).ends_with("fa")
                 || (&genome_path).ends_with("fna")
                 || (&genome_path).ends_with("fastq")
                 || (&genome_path).ends_with("fq")
                 || (&genome_path).ends_with("fasta.gz")
                 || (&genome_path).ends_with("fa.gz")
                 || (&genome_path).ends_with("fna.gz")
                 || (&genome_path).ends_with("fastq.gz")
                 || (&genome_path).ends_with("fq.gz")) { continue; }
            let genome_str = format!("{0:?}", &genome_path);
            print_err(&format!("Scoring {0} ({1}/{2}).", genome_name(&genome_str).expect("Error inferring genome name"), i+1, gnum));
            let (reader, _format) = niffler::get_reader(Box::new(f)).expect(
                "Can't read from tar archive");
            for result in fasta::Reader::new(reader).records() {
                let seq = parse_record(result);
                for kmer in break_seq(&seq, upper, lower).expect("Error decomposing sequence") {
                    let new_score: Score = update_score(&kmers, &kmer,
                        &score_list, byte_idx,  bit_mask, nbytes);
                    match score_to_idx.get(&new_score){
                        Some(idx) => { kmers.insert(kmer, *idx); },
                        None => {
                            kmers.insert(kmer, score_list.len());
                            score_to_idx.insert(new_score.clone(), score_list.len());
                            score_list.push(new_score);
                        }
                    };
                }
            }
            print_err(&format!("Finished scoring {0}.", genome_name(&genome_str).expect("Error inferring genome name")));
        }
    } else {
        for (i, f) in genomes.iter().enumerate() {
            let (byte_idx, bit_mask) = genome_index_to_byte_idx_and_bit_mask(i, nbytes);
            print_err(&format!("Scoring {0} ({1}/{2}).", genome_name(f).expect("Error inferring genome name"), i+1, gnum));
            let (reader, _format) = niffler::from_path(f).expect(
                &format!("File not found: {}", f));
            for result in fasta::Reader::new(reader).records() {
                let seq = parse_record(result);
                for kmer in break_seq(&seq, upper, lower).expect("Error decomposing sequence") {
                    let new_score: Score = update_score(&kmers, &kmer,
                        &score_list, byte_idx,  bit_mask, nbytes);
                    match score_to_idx.get(&new_score){
                        Some(idx) => { kmers.insert(kmer, *idx); },
                        None => {
                            kmers.insert(kmer, score_list.len());
                            score_to_idx.insert(new_score.clone(), score_list.len());
                            score_list.push(new_score);
                        }
                    };
                }
            }
            print_err(&format!("Finished scoring {0}.", genome_name(f).expect("Error inferring genome name")));
        }
    }
    PKIdx{
        kmers: kmers, 
        genomes: genomes,
        scores: score_list,
        score_map: score_to_idx,
        k: kmersize,
        kmer_cutoff: cutoff
    }
}
