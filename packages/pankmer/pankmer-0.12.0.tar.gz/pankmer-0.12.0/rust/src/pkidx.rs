// Imports =====================================================================
use std::{fs, str};
use std::io::{Read, Write};
use std::path::PathBuf;
use niffler;
use pyo3::prelude::*;
use rayon::iter::{IntoParallelRefIterator, ParallelIterator};
use rustc_hash::FxHashMap as HashMap;
use serde::{Serialize, Deserialize};
use crate::{K, Kmer, ScoreList, ScoreToIDX, PKTbl, PKGenomes, IDXMap, MemBlocks};
use crate::helpers::print_err;
use crate::mem_blocks::generate_mem_blocks;
use crate::get_kmers::get_kmers;
use crate::score_list_io::{load_scores_partial, dump_scores};
use crate::metadata::PKMeta;

// Structs =====================================================================
#[derive(Serialize, Deserialize, Debug)]
pub struct PKIdx {
    pub kmers: PKTbl,
    pub genomes: PKGenomes,
    pub k: usize,
    pub scores: ScoreList,
    pub score_map: ScoreToIDX,
    pub kmer_cutoff: Kmer
}

// Functions ===================================================================
#[pyfunction]
pub fn run_index(genomes_input: &str, genomes: PKGenomes, outdir: &str, fraction: f64,
             kmersize: usize, split_memory: usize, threads: usize,
             index: &str, input_is_tar: bool) -> PyResult<(PKTbl, MemBlocks)> {
    let mut tar_file = String::from("");
    if input_is_tar { tar_file = String::from(genomes_input); }
    print_err("Indexing genomes.");
    let (post_dict, all_core_blocks) = index_genomes(&genomes,
        kmersize, fraction, split_memory,  &outdir,
        threads, index, &tar_file).expect("couldn't index genomes");
    print_err("Finished Indexing.");
    print_err("Concatenating files.");
    let positions_dictionary = concat_files(post_dict, &all_core_blocks, &outdir)?;
    print_err("Finished concatenating.");
    Ok((positions_dictionary, all_core_blocks))
}

fn run_core_cohort(args: (&Vec<Kmer>, &PKGenomes, usize, f64, &str, &str, &str)) -> (String, PKTbl) {
    let (limits, genomes, kmersize, kmer_fraction, outdir, index, tar_file) = args;
    let lower = limits[0];
    let upper = limits[1];
    let kmer_bitsize = (2 * K + 7) / 8;
    let score_bitsize = (genomes.len() + 7) / 8;
    let key = format!("{lower}_{upper}");
    let kmers_post = create_index(genomes, kmersize, kmer_fraction, upper, lower,
        kmer_bitsize, score_bitsize,  &outdir, &tar_file).expect("Failed to run core cohort");
    (key, kmers_post)
}

fn index_genomes(genomes: &PKGenomes, kmersize: usize, kmer_fraction: f64,
                 mem_split: usize, outdir: &str, threads: usize, index: &str,
                 tar_file: &str) -> PyResult<(HashMap<String, PKTbl>, MemBlocks)> {
    let all_core_blocks: MemBlocks = generate_mem_blocks(mem_split, threads)?;
    let mut core_block_args: Vec<(&Vec<Kmer>, &PKGenomes, usize, f64, &str, &str, &str)> = Vec::new();
    let rayon_num_threads: usize = rayon::current_num_threads();
    let results = match threads >= rayon_num_threads {
        true => {
            print_err(&format!("{threads} threads requested, using {rayon_num_threads} (entire global thread pool)"));
            for limits in all_core_blocks.iter() {
                core_block_args.push((limits, genomes, kmersize, kmer_fraction, &outdir, &index, &tar_file));
            }
            core_block_args.par_iter().map(|args| run_core_cohort(*args)).collect::<Vec<(String, PKTbl)>>()
        },
        false => {
            print_err(&format!("{threads} threads requested, using {threads} (partial global thread pool)"));
            let mut results: Vec<(String, PKTbl)> = Vec::new();
            let cb_len = all_core_blocks.len();
            for (i, limits) in all_core_blocks.iter().enumerate() {
                core_block_args.push((limits, genomes, kmersize, kmer_fraction, &outdir, &index, &tar_file));
                if (i+1)%threads==0 || (i+1)==cb_len {
                    results.extend(core_block_args.par_iter().map(|args| run_core_cohort(*args)).collect::<Vec<(String, PKTbl)>>());
                    core_block_args.clear();
                }
            }
            results
        }
    };
    let mut post_dict: HashMap<String, PKTbl> = HashMap::default();
    for result in results {
        post_dict.insert(result.0, result.1);
    }
    Ok((post_dict, all_core_blocks))
}

fn concat_files(post_dict: HashMap<String, PKTbl>, all_core_blocks: &MemBlocks, outdir: &str) -> PyResult<PKTbl> {
    let mut positions_dict: PKTbl = HashMap::default();
    let mut num: usize = 0;
    let mut scores = ScoreList::new();
    let mut score_to_idx: ScoreToIDX = ScoreToIDX::default();
    let mut kmers_out_path = PathBuf::from(&outdir);
    kmers_out_path.push("kmers.bgz");
    let mut indices_out_path = PathBuf::from(&outdir);
    indices_out_path.push("indices.bgz");
    let mut kmers_out = niffler::to_path(kmers_out_path, niffler::compression::Format::Gzip, niffler::Level::Nine).expect("Can't open file for writing");
    let mut indices_out = niffler::to_path(indices_out_path, niffler::compression::Format::Gzip, niffler::Level::Nine).expect("Can't open file for writing");
    let mut scores_out_path = PathBuf::from(outdir);
    scores_out_path.push(format!("scores.pks"));
    let scores_outpath = scores_out_path.into_os_string().into_string().unwrap();
    for limits in all_core_blocks {
        let mut idx_map: IDXMap = IDXMap::default();
        let lower = limits[0];
        let upper = limits[1];
        let key  = format!("{lower}_{upper}");
        let temp_dict = post_dict.get(&key).unwrap();
        let mut sorted_temp: Vec<&Kmer> = temp_dict.keys().collect();
        sorted_temp.sort_unstable();
        for kmer in sorted_temp {
            let cur = temp_dict.get(kmer).expect("could not get kmer from temp dict");
            num = cur + num;
            positions_dict.insert(*kmer, num);
        }
        num += 1;
        let scores_partial = load_scores_partial(&outdir, lower, upper);
        for (i, s) in scores_partial.iter().enumerate() {
            match score_to_idx.get(s) {
                Some(x) => { (idx_map.insert(i as u64, *x)); },
                None => {
                    idx_map.insert(i as u64, scores.len());
                    score_to_idx.insert(s.clone().to_vec(), scores.len());
                    scores.push(s.to_vec());
                }
            };
        }

        let mut kmers_in_path: PathBuf = PathBuf::from(&outdir);
        kmers_in_path.push(format!("{lower}_{upper}_kmers.bgz"));
        let (mut k, _format) = niffler::from_path(&kmers_in_path).expect("File not found");
        let mut k_vec: Vec<u8> = Vec::new();
        k.read_to_end(&mut k_vec)?;
        kmers_out.write_all(&k_vec).unwrap();
        fs::remove_file(&kmers_in_path)?;

        let mut indices_in_path: PathBuf = PathBuf::from(&outdir);
        indices_in_path.push(format!("{lower}_{upper}_indices.bgz"));
        let (mut i, _format) = niffler::from_path(&indices_in_path).expect("File not found");
        let mut i_vec: Vec<u8> = Vec::new();
        i.read_to_end(&mut i_vec)?;
        for x in (0..i_vec.len()).step_by(8) {
            let idx = u64::from_be_bytes(i_vec[x..(x+8)].try_into().unwrap());
            let i_remapped = idx_map.get(&idx).unwrap().to_be_bytes();
            indices_out.write_all(&i_remapped).unwrap();
        }
        fs::remove_file(&indices_in_path)?;
    }
    dump_scores(scores, &scores_outpath).expect("could not write scores.pks");
    Ok(positions_dict)
}

fn create_index(genomes: &PKGenomes, kmersize: usize, kmer_fraction: f64,
                upper: Kmer, lower: Kmer, kmer_bitsize: usize,
                score_bitsize: usize, outdir: &str, tar_file: &str) -> PyResult<PKTbl> {
    let idx: PKIdx = get_kmers(kmersize, kmer_fraction, upper, lower,
                                genomes.to_vec(), tar_file);
    let mut scores_out_path = PathBuf::from(outdir);
    scores_out_path.push(format!("{lower}_{upper}_scores.pks"));
    let scores_outpath = scores_out_path.into_os_string().into_string().unwrap();
    let mut kmers_out_path = PathBuf::from(&outdir);
    kmers_out_path.push(format!("{lower}_{upper}_kmers.bgz"));
    let mut indices_out_path = PathBuf::from(&outdir);
    indices_out_path.push(format!("{lower}_{upper}_indices.bgz"));
    let mut kmers_out = niffler::to_path(kmers_out_path, niffler::compression::Format::Gzip, niffler::Level::Nine).expect("Can't open file for writing");
    let mut indices_out = niffler::to_path(indices_out_path, niffler::compression::Format::Gzip, niffler::Level::Nine).expect("Can't open file for writing");                     
    let kmers: &PKTbl = &idx.kmers;
    let mut sorted_kmers: Vec<Kmer> = kmers.keys().cloned().collect();
    sorted_kmers.sort_unstable();
    let mut count: usize = 0;
    let mut kmers_post: PKTbl = HashMap::default();
    let mut kmer_none: bool = true;
    let mut kmer_mut: Kmer = 0;
    for kmer in sorted_kmers {
        kmers_out.write_all(&kmer.to_be_bytes()[8-kmer_bitsize..]).unwrap();
        let i = kmers.get(&kmer).unwrap().to_be_bytes();
        indices_out.write_all(&i).unwrap();
        if count%10000000 == 0 && count != 0 {
            kmers_post.insert(kmer, count);
            count = 0;
        }
        count += 1;
        kmer_mut = kmer;
        kmer_none = false;
    }
    dump_scores(idx.scores, &scores_outpath).expect("could not write scores.pks");
    if !kmer_none && !kmers_post.contains_key(&kmer_mut) {
        kmers_post.insert(kmer_mut, count-1);
    }
    Ok(kmers_post)
}
