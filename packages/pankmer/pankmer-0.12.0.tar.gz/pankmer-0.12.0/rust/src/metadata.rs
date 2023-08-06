// Imports =====================================================================
use std::{fs, io};
use std::path::PathBuf;
use std::io::{Read, Write};
use pyo3::prelude::*;
use rmp_serde::Serializer;
use rustc_hash::FxHashMap as HashMap;
use serde::{Serialize, Deserialize};
use serde_json::to_writer;
use tar::Archive;
use crate::{K, VERSION, Kmer, MemBlocks};

// Structs =====================================================================
#[pyclass]
#[derive(Clone, Serialize, Deserialize)]
pub struct PKMeta {
    #[pyo3(get)]
    pub kmer_size: usize,
    #[pyo3(get)]
    pub version: String,
    #[pyo3(get, set)]
    pub genomes: HashMap<usize, String>,
    #[pyo3(get, set)]
    pub genome_sizes: HashMap<String, usize>,
    #[pyo3(get, set)]
    pub positions: HashMap<String, Kmer>,
    #[pyo3(get, set)]
    pub mem_blocks: MemBlocks
}

#[pymethods]
impl PKMeta {
    #[new]
    pub fn new() -> Self {
        return PKMeta {
            kmer_size: K,
            version: String::from(VERSION),
            genomes: HashMap::default(),
            genome_sizes: HashMap::default(),
            positions: HashMap::default(),
            mem_blocks: MemBlocks::new()
        }
    }
}

// Functions ===================================================================
#[pyfunction]
pub fn dump_metadata(metadata: PKMeta, outpath: &str) -> PyResult<()> {
    if outpath != "-" {
        let mut file = fs::File::create(&outpath).expect(
            &format!("Can't open file {} for writing", &outpath)
        );
        serde_json::to_writer(&file, &metadata).expect(
            &format!("Couldn't write PKMeta to file {}", &outpath)
        );
    }
    else {
        let buf = serde_json::to_vec(&metadata).expect("couldnt serialize PKMeta");
        io::stdout().write_all(&buf).expect("Couldn't write ScoreList to stdout");
    }
    Ok(())
}

#[pyfunction]
pub fn load_metadata(idx_dir: &str, tar_file: &str) -> PyResult<PKMeta> {
    let metadata = match tar_file.len() > 0 {
        true => {
            let mut metadata = PKMeta::new();
            let (tar, _format) = niffler::from_path(tar_file).expect(
            &format!("File not found: {}", tar_file));
            for f in Archive::new(tar).entries().expect("Can't read tar file") {
                let f = f.expect("Error reading tar archive");
                let in_path = f.path().expect("Error reading tar archive");
                let in_str = format!("{0:?}", &in_path);
                let in_base = format!("metadata.json\"");
                if !(&in_str.ends_with(&in_base)) { continue; }
                let (mut reader, _format) = niffler::get_reader(Box::new(f)).expect("Can't read from tar archive");
                let mut buffer: Vec<u8> = Vec::new();
                reader.read_to_end(&mut buffer).expect(&format!("Can't read file {}", &in_str));
                metadata = serde_json::from_slice(&buffer).expect("Unable to parse");
            }
            metadata
        },
        false => {
            let mut in_path: PathBuf = PathBuf::from(&idx_dir);
            let in_base: String = format!("metadata.json");
            in_path.push(in_base);
            // let inpath = in_path.into_os_string().into_string().unwrap();
            let metadata_string = fs::read_to_string(&in_path).expect("Unable to read file");
            let metadata = serde_json::from_str(&metadata_string).expect("Unable to parse");
            metadata
        }
    };
    Ok(metadata)
}
