use pyo3::prelude::*;

use crate::MemBlocks;

#[pyfunction]
pub fn generate_mem_blocks(mem_split: usize, threads: usize) -> PyResult<MemBlocks> {
    let split_num: u64 = (mem_split*threads) as u64;
    let block_size = ((1<<63)-1)/(2*split_num);
    let mut all_core_blocks: MemBlocks = Vec::new();
    for x in 0..split_num {
        all_core_blocks.push(vec![x*block_size, (x+1)*block_size]);
    }
    all_core_blocks.push(vec![split_num*block_size, (1<<63)-1]);
    Ok(all_core_blocks)
}
