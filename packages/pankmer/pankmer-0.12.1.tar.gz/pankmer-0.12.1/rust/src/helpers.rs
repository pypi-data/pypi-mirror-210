use pyo3::prelude::*;
use time::OffsetDateTime;
use std::path::Path;

use crate::K;
use crate::Kmer;

#[pyfunction]
pub fn kmer_size() -> PyResult<usize> {
    Ok(K)
}

#[pyfunction]
pub fn print_err(message: &str) {
    let date_time = OffsetDateTime::now_utc();
    eprintln!("{date_time}: {message}");
}

#[pyfunction]
pub fn genome_name(genome: &str) -> PyResult<&str> {
    let file_stem = Path::new(genome).file_stem().expect("could not get genome file stem");
    let file_stem_str = file_stem.to_str().expect("could not stringify genome file stem");
    Ok(file_stem_str)
}

#[pyfunction]
pub fn score_byte_to_blist(b: &[u8], sz: usize) -> PyResult<Vec<usize>> {
    let mut vec = Vec::new();
    let s = b.len();
    for k in 0..sz {
        vec.push((b[s - (k/8) - 1] & (1<<(k%8)) > 0) as usize)
    }
    Ok(vec)
}

#[inline]
pub fn mix64(mut x: Kmer) -> Kmer {
    x ^= x >> 32;
    x = x.wrapping_mul(0xbea225f9eb34556d);
    x ^= x >> 29;
    x = x.wrapping_mul(0xbea225f9eb34556d);
    x ^= x >> 32;
    x = x.wrapping_mul(0xbea225f9eb34556d);
    x ^ (x >> 29)
}
