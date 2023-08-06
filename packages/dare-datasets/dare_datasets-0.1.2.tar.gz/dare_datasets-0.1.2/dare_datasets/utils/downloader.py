import glob
import logging
import os
from pathlib import Path

import gdown

print()


def get_file_from_gdrive(url: str, folder_name: str, cache_dir: str) -> None:
    cached_datasets = list(map(os.path.basename, glob.glob(f"{cache_dir}*")))

    if folder_name not in cached_datasets:  # Check if file is already downloaded in cache
        gdown.download_folder(url, output=cache_dir, quiet=True, use_cookies=False)
    else:
        logging.debug(f"Using cached version of {folder_name}")


get_file_from_gdrive(url="https://drive.google.com/drive/folders/1LCD4gObeX-PBxkNYNuZxSmrTBvzEK095?usp=sharing",
                     cache_dir='~/.cache/dare-datasets/', folder_name='QR2T_Benchmark')
