import glob
import json
import os
import typing

from pathlib import Path
from dare_datasets.dataset_abc import Dataset
from dare_datasets.utils.downloader import get_file_from_gdrive

GDRIVE_URL = "https://drive.google.com/drive/folders/1LCD4gObeX-PBxkNYNuZxSmrTBvzEK095?usp=sharing"
DATASET_NAME = "QR2T_Benchmark"


class QR2TBenchmark(Dataset):
    def __init__(self, cache_dir: typing.Optional[str] = f'{Path.home()}/.cache/dare-datasets/') -> None:
        self.data = None
        self.cache_dir = cache_dir
        self.dataset_folder = cache_dir + DATASET_NAME + "/"

    def get_info(self) -> dict[str, str]:
        return {
            "name": "QR2T Benchmark",
            "description": "QR2T Benchmark is an extension of the Spider dataset for the QR2T task.",
            "url": GDRIVE_URL,
            "original_url": "-",
            "formats": ["json"],
            "dataset_folder": self.dataset_folder if self.data is not None else "NOT_YET_DOWNLOADED"
        }

    def _init_data(self):
        get_file_from_gdrive(url=GDRIVE_URL, cache_dir=self.cache_dir, folder_name=DATASET_NAME)

        self.data = {}
        for file in glob.glob(self.dataset_folder + "*"):
            self.data[os.path.basename(file).split('.')[0]] = json.load(open(file))

    def get_raw(self):
        if self.data is None:
            self._init_data()

        return self.data

    def get_processed(self):
        pass
