// Modules =====================================================================
mod helpers;
mod mem_blocks;
mod decompose_kmers;
mod get_kmers;
mod score_list_io;
mod pkidx;
mod adj_matrix;
mod metadata;

// Imports =====================================================================
use pyo3::prelude::*;
// use pyo3::exceptions::Py<?>Error
use rustc_hash::FxHashMap as HashMap;
use crate::helpers::{kmer_size, print_err, genome_name, score_byte_to_blist};
use crate::metadata::{PKMeta, load_metadata, dump_metadata};
use crate::mem_blocks::generate_mem_blocks;
use crate::decompose_kmers::{decompose_kmers, break_seq};
use crate::score_list_io::{load_scores, dump_scores, subset_scores};
use crate::pkidx::run_index;
use crate::adj_matrix::add_score_mat_np;

// Constants ===================================================================
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const K: usize = 31;

// Types =======================================================================
pub type Kmer = u64;
pub type Score = Vec<u8>;
pub type ScoreList = Vec<Score>;
pub type ScoreToIDX = HashMap<Score, usize>;
pub type IDXMap = HashMap<u64, usize>;
pub type PKTbl = HashMap<Kmer, usize>; // Should we use nohash_hasher here instead? (https://stackoverflow.com/questions/70551997/faster-hashmap-for-sequential-keys)
pub type PKGenomes = Vec<String>;
pub type MemBlocks = Vec<Vec<Kmer>>;

// Functions ===================================================================
#[pyfunction]
pub fn version() -> PyResult<String> {
    Ok(String::from(VERSION))
}

// PyModule ====================================================================
#[pymodule]
fn index(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PKMeta>()?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(kmer_size, m)?)?;
    m.add_function(wrap_pyfunction!(print_err, m)?)?;
    m.add_function(wrap_pyfunction!(genome_name, m)?)?;
    m.add_function(wrap_pyfunction!(break_seq, m)?)?;
    m.add_function(wrap_pyfunction!(score_byte_to_blist, m)?)?;
    m.add_function(wrap_pyfunction!(add_score_mat_np, m)?)?;
    m.add_function(wrap_pyfunction!(generate_mem_blocks, m)?)?;
    m.add_function(wrap_pyfunction!(dump_metadata, m)?)?;
    m.add_function(wrap_pyfunction!(load_scores, m)?)?;
    m.add_function(wrap_pyfunction!(dump_scores, m)?)?;
    m.add_function(wrap_pyfunction!(subset_scores, m)?)?;
    m.add_function(wrap_pyfunction!(run_index, m)?)?;
    Ok(())
}

// Tests =======================================================================
fn test_decompose_kmers(){
    let corrects = [
        0b1110101010101010101010101010101010101010101010101010101010101010u64,
        0b1110101010101010101010101010101010101010101010101010101010101001u64,
        0b1111111111111111111111111111111111111111111111111111111111111111u64,
        0b1111111111111111111111111111111111111111111111111111111111111100u64,
        0b1111111111111111111111111111111111111111111111111111111111111000u64
    ];
    let result1 = decompose_kmers(b"CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCG", 31, Kmer::MAX, Kmer::MAX, 0);
    assert_eq!(result1[0], corrects[0]);
    assert_eq!(result1[1], corrects[1]);
    let result2 = decompose_kmers(b"CGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG", 31, Kmer::MAX, Kmer::MAX, 0);
    assert_eq!(result2[1], corrects[0]);
    assert_eq!(result2[0], corrects[1]);
    let result3 = decompose_kmers(b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAT", 31, Kmer::MAX, Kmer::MAX, 0);
    assert_eq!(result3[0], corrects[2]);
    assert_eq!(result3[1], corrects[3]);
    let result4 = decompose_kmers(b"ATTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT", 31, Kmer::MAX, Kmer::MAX, 0);
    assert_eq!(result4[0], corrects[3]);
    assert_eq!(result4[1], corrects[2]);
    let result5 = decompose_kmers(b"AAANAAAAAAAAAAAAAAAAaAAAAAAAAAAAAAA", 31, Kmer::MAX, Kmer::MAX, 0);
    assert_eq!(result5[0], corrects[2]);
    let result6 = decompose_kmers(b"ACT", 3, Kmer::MAX, Kmer::MAX, 0);
    assert_eq!(result6[0], corrects[4]);
}

// fn download_test_data(){
//     eprintln!("Downloading and Unpacking Test Data...");
//     Command::new("wget")
//             .arg("-q")
//             .arg("https://salk-tm-pub.s3.us-west-2.amazonaws.com/PanKmer_example/PanKmer_test_data_1.tar.gz")
//             .arg("-O")
//             .arg("PanKmer_test_data_1.tar.gz")
//             .output()
//             .expect("Couldn't download test data");
//     Command::new("tar")
//             .arg("-zxf")
//             .arg("PanKmer_test_data_1.tar.gz")
//             .output()
//             .expect("Couldn't unpack test data");
//     return 
// }

// fn test_create_index(){
//     let result_idx1 = create_index(
//         vec![
//             "PanKmer_test_data_1/Sp_chr19/Sp7498_HiC_Chr19.fasta".to_string(),
//             "PanKmer_test_data_1/Sp_chr19/Sp9509_oxford_v3_Chr19.fasta".to_string(),
//             "PanKmer_test_data_1/Sp_chr19/Sp9512_a02_genome_Chr19.fasta".to_string()
//         ],
//         31,
//         1.0
//     );
//     assert_eq!(4764864, result_idx1.kmers.len());
//     let result_idx2 = create_index(vec!["PanKmer_test_data_1/smalls/test1.fasta".to_string()], 31, 1.0);
//     assert_eq!(1, result_idx2.kmers.len());
//     let kmer_poly_a = Kmer::MAX;
//     assert_eq!(vec![1u8],result_idx2.scores[*result_idx2.kmers.get(&kmer_poly_a).expect(
//         "Failed to find polyA kmer in result_idx2.kmers"
//     )]);
//     let result_idx3 = create_index(vec![
//         "PanKmer_test_data_1/smalls/test1.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test2.fasta".to_string(),
//     ], 31, 1.0);
//     assert_eq!(1, result_idx3.kmers.len());
//     let result_idx4 = create_index(vec![
//         "PanKmer_test_data_1/smalls/test1.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test3.fasta".to_string(),
//     ], 31, 1.0);
//     let i = 0b1110101010101010101010101010101010101010101010101010101010101010u64;
//     assert_eq!(vec![2u8], result_idx4.scores[*result_idx4.kmers.get(&i).unwrap()]);
//     let result_idx5 = create_index(vec![
//         "PanKmer_test_data_1/smalls/test1.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test2.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test3.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test4.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test5.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test6.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test7.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test8.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test9.fasta.gz".to_string(),
//     ], 31, 1.0);
//     assert_eq!(6, result_idx5.kmers.len());
//     let i = 0b1111100000000001010100001010111100111100110011010101101010111111u64;
//     assert_eq!(vec![0u8, 1u8], result_idx5.scores[*result_idx5.kmers.get(&i).expect(
//         "failed to find expected kmer in result_idx5"
//     )]);
//     assert_eq!(vec![0b11100011u8, 0u8], result_idx5.scores[*result_idx5.kmers.get(&kmer_poly_a).expect(
//         "Failed to find polyA kmer in results_idx5"
//     )]);
//     return
// }

// fn test_load_dump(){
//     let result_idx1 = create_index(vec![
//         "PanKmer_test_data_1/smalls/test1.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test2.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test3.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test4.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test5.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test6.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test7.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test8.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test9.fasta.gz".to_string(),
//     ], 31, 1.0);
//     let fpath = "temp.pkidx";
//     dump_pkidx(&result_idx1, &fpath);
//     let result_idx2 = load_pkidx(&fpath);
//     assert_eq!(result_idx1.kmers, result_idx2.kmers);
//     assert_eq!(result_idx1.genomes, result_idx2.genomes);
//     assert_eq!(result_idx1.k, result_idx2.k);
//     assert_eq!(result_idx1.scores, result_idx2.scores);
//     assert_eq!(result_idx1.score_map, result_idx2.score_map);
//     assert_eq!(result_idx1.kmer_cutoff, result_idx2.kmer_cutoff);
//     return
// }

// fn run_tests(){
//     test_decompose_kmers();
//     download_test_data();
//     test_create_index();
//     test_load_dump();
//     eprintln!("{}", "All tests passed.");
//     return
// }
