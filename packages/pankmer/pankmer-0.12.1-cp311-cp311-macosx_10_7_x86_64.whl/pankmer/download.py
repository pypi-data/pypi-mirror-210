import urllib3
import shutil
import os
import os.path
import tarfile
import ftplib
from pankmer.env import (EXAMPLE_DATA_URL, EXAMPLE_DATA_DIR,
                         BACTERIAL_DATA_FTP, BACTERIAL_DATA_PATHS)

def download_example(dir: str = EXAMPLE_DATA_DIR, bacterial: bool = False,
                     n_samples: int = 1):
    """Download an example datatset

    Parameters
    ----------
    dir : str
        Destination directory for example data
    bacterial : bool
        If True, download bacterial genomes
    n_samples : int
        Number of bacterial samples to download, max 164 [1]
    """

    if n_samples > 164:
        raise RuntimeError('n_samples parameter must be <= 164')
    if bacterial:
        ftp = ftplib.FTP(BACTERIAL_DATA_FTP)
        ftp.login()
        for ftp_path in BACTERIAL_DATA_PATHS[:n_samples]:
            with open(os.path.join(dir, os.path.basename(ftp_path)), 'wb') as f:
                ftp.retrbinary(f'RETR {ftp_path}', f.write)
    else:
        http = urllib3.PoolManager()
        tar_file_path = os.path.join(dir, os.path.basename(EXAMPLE_DATA_URL))
        if os.path.exists(tar_file_path[:-7]):
            raise RuntimeError('destination already exists')
        with http.request('GET', EXAMPLE_DATA_URL, preload_content=False) as r, open(tar_file_path, 'wb') as out_file:
            shutil.copyfileobj(r, out_file)
        with tarfile.open(tar_file_path) as tar:
            tar.extractall(dir)
        os.remove(tar_file_path)
