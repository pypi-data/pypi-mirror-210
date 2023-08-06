// Imports =====================================================================
use std::{fs, io, str};
use std::boxed::Box;
use std::io::{Read, Write};
use std::path::PathBuf;
use niffler;
use pyo3::prelude::*;
use rmp_serde::Serializer;
use rustc_hash::FxHashMap as HashMap;
use serde::Serialize;
use tar::Archive;
use crate::{Kmer, Score, ScoreList, PKGenomes};
use crate::helpers::score_byte_to_blist;
use crate::get_kmers::genome_index_to_byte_idx_and_bit_mask;

//Functions ====================================================================
pub fn load_scores_partial(idx_dir: &str, lower: Kmer, upper: Kmer) -> ScoreList {
    let mut in_path: PathBuf = PathBuf::from(&idx_dir);
    let in_base: String = format!("{lower}_{upper}_scores.pks");
    in_path.push(in_base);
    let inpath = in_path.into_os_string().into_string().unwrap();
    let buffer = fs::read(&inpath).expect(&format!("Can't read file {}", &inpath));
    let scores = rmp_serde::from_slice(&buffer).expect(&format!("Can't deserialize data from {}", &inpath));
    fs::remove_file(&inpath).expect("could not remove partial scores file");
    scores
}

#[pyfunction]
pub fn load_scores(idx_dir: &str, tar_file: &str) -> PyResult<ScoreList> {
    let mut scores: ScoreList = ScoreList::new();
    if tar_file.len() > 0 {
        let (tar, _format) = niffler::from_path(tar_file).expect(
            &format!("File not found: {}", tar_file));
        for f in Archive::new(tar).entries().expect("Can't read tar file") {
            let f = f.expect("Error reading tar archive");
            let in_path = f.path().expect("Error reading tar archive");
            let in_str = format!("{0:?}", &in_path);
            let in_base = format!("scores.pks\"");
            if !(&in_str.ends_with(&in_base)) { continue; }
            let (mut reader, _format) = niffler::get_reader(Box::new(f)).expect("Can't read from tar archive");
            let mut buffer: Vec<u8> = Vec::new();
            reader.read_to_end(&mut buffer).expect(&format!("Can't read file {}", &in_str));
            scores = rmp_serde::from_slice(&buffer).expect(&format!("Can't deserialize data from {}", &in_str));
        }
    } else {
          let mut in_path: PathBuf = PathBuf::from(&idx_dir);
          let in_base: String = format!("scores.pks");
          in_path.push(in_base);
          let inpath = in_path.into_os_string().into_string().unwrap();
          let buffer = fs::read(&inpath).expect(&format!("Can't read file {}", &inpath));
          scores = rmp_serde::from_slice(&buffer).expect(&format!("Can't deserialize data from {}", inpath));
    }
    Ok(scores)
}

#[pyfunction]
pub fn dump_scores(scores: ScoreList, outpath: &str) -> PyResult<()> {
    let mut buf: Vec<u8> = Vec::new();
    scores.serialize(&mut Serializer::new(&mut buf)).expect("Couldn't serialize ScoreList");
    if outpath != "-" {
        let mut file = fs::File::create(&outpath).expect(
            &format!("Can't open file {} for writing", &outpath)
        );
        file.write_all(&buf).expect(
            &format!("Couldn't write ScoreList to file {}", &outpath)
        );
    }
    else {
        io::stdout().write_all(&buf).expect("Couldn't write ScoreList to stdout");
    }
    Ok(())
}

#[pyfunction]
pub fn compress_scores(superset_scores: ScoreList, superset_genomes: PKGenomes, subset_genomes: PKGenomes) -> PyResult<(ScoreList, HashMap<usize, usize>)> {
    let n_superset_genomes = superset_genomes.len();
    let n_subset_genomes = subset_genomes.len();
    let n_superset_bytes = (n_superset_genomes + 7) / 8;
    let n_subset_bytes = (n_subset_genomes + 7) / 8;
    let mut memberships: Vec<usize> = Vec::new();
    for (i, genome) in superset_genomes.iter().enumerate() {
        if subset_genomes.contains(&genome) { memberships.push(i); }
    }
    let mut indices_map: HashMap<usize, usize> = HashMap::default();
    let mut subset_scores = ScoreList::new();
    for (key, score) in superset_scores.iter().enumerate() {
        let expanded_score: Vec<usize> = score_byte_to_blist(&score, n_superset_genomes)?;
        let mut compressed_score: Score = vec![0; n_subset_bytes];
        for (i, j) in memberships.iter().enumerate() {
            if expanded_score[*j] == 1 {
                let (byte_idx, bit_mask) = genome_index_to_byte_idx_and_bit_mask(i, n_subset_bytes);
                compressed_score[byte_idx] = score[byte_idx] | bit_mask;
            }
        }
        let compressed_sum: u8 = compressed_score.iter().sum();
        if compressed_sum == 0 { continue; }
        indices_map.insert(key, subset_scores.len());
        subset_scores.push(compressed_score);
    }
    Ok((subset_scores, indices_map))
}

#[pyfunction]
pub fn subset_scores(idx_dir: &str, tar_file: &str, superset_genomes: PKGenomes, subset_genomes: PKGenomes, outpath: &str) -> PyResult<HashMap<usize, usize>> {
    let superset_scores = load_scores(idx_dir, tar_file)?;
    let (compressed_scores, idx_map) = compress_scores(superset_scores, superset_genomes, subset_genomes)?;
    dump_scores(compressed_scores, &outpath)?;
    Ok(idx_map)
}
