use pyo3::prelude::*;
use ndarray::s;
use numpy::{ToPyArray,PyArray1,PyArray2};


#[pyfunction]
pub fn add_score_mat_np<'py>(py: Python<'py>, score_multi: &PyArray1<i64>, mat: &PyArray2<i64>) -> PyResult<&'py PyArray2<i64>> {
    let size = score_multi.len();
    let score_multi = score_multi.readwrite().as_array().to_owned();
    let mut mat = mat.readwrite().as_array_mut().to_owned();
    for count in 0..size {
        if score_multi[count] != 0 {
            let sum = &mat.slice(s![count, ..]) + &score_multi;
            mat.slice_mut(s![count, ..]).assign(&sum)
        }
    }
    Ok(mat.to_pyarray(py))
}

// fn count_scores(pkidx: &PKIdx) -> HashMap<Score, u64> {
//   let mut score_index_counts: HashMap<usize, u64> = HashMap::default();
//   for (i, _s) in pkidx.scores.iter().enumerate() {
//       score_index_counts.insert(i, 0);
//   }
//   for (_k, si) in pkidx.kmers.iter() {
//       match score_index_counts.get(&si) {
//           Some(n) => {
//               score_index_counts.insert(*si, n + 1)
//           },
//           None => {
//               panic!("Unexpected score index encountered")
//           }
//       };
//   }
//   let mut score_counts: HashMap<Score, u64> = HashMap::default();
//   for (si, c) in score_index_counts.iter() {
//       if c > &0 {
//           score_counts.insert(pkidx.scores[*si].clone(), *c);
//       }
//   }
//   return score_counts
// }

// fn compute_jaccards(pkidx: &PKIdx) -> HashMap<String, HashMap<String, f64>> {
//     let score_counts = count_scores(&pkidx);
//     let mut table =  HashMap::default();
//     for (i1, f1) in pkidx.genomes.iter().enumerate() {
//         let mut row: HashMap<String, f64> = HashMap::default();
//         let (byte_idx1, bit_mask1) = genome_index_to_byte_idx_and_bit_mask(i1);
//         for (i2, f2) in pkidx.genomes.iter().enumerate() {        
//             let (byte_idx2, bit_mask2) = genome_index_to_byte_idx_and_bit_mask(i2);
//             let (mut i, mut u) = (0, 0);
//             for (score, c) in score_counts.iter(){
//                 let flag1 = (score[byte_idx1] & bit_mask1) > 0u8;
//                 let flag2 = (score[byte_idx2] & bit_mask2) > 0u8;
//                 if flag1 | flag2 { u += c };
//                 if flag1 & flag2 { i += c };
//             }
//             row.insert(f2.clone(), i as f64 / u as f64);
//         }
//         table.insert(f1.clone(), row);
//     }
//     return table
// }
