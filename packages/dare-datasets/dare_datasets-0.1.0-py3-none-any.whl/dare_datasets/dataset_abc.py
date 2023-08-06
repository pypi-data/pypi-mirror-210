from abc import ABC, abstractmethod


# Url of the FOLDER of the dataset in Google Drive. The folder must be publicly available.
GDRIVE_URL = ""


class Dataset(ABC):
    """
    Set of methods that every dataset should implement. Apart from these methods the class can
    implement whichever other method is considered needed e.g. different versions of the dataset.
    """
    @abstractmethod
    def __init__(self, cache_dir: str | None = '~/.cache/dare-datasets/') -> None:
        pass

    @abstractmethod
    def _init_data(self):
        """
        Loads the dataset from disk. If the dataset is not available on disk, it is downloaded and saved in cache.
        """
        pass

    @abstractmethod
    def get_info(self) -> dict[str, str]:
        """
        Returns a dictionary with information about the dataset.
        Necessary:
            - name: name of dataset
            - description: description of dataset
            - url: url of cocalc file
            - original_url: original url of dataset (can be the paper url)
            - formats: list of formats the dataset is available eg. ["csv", "json", "xml"]

        """
        pass

    @abstractmethod
    def get_raw(self):
        """
        Returns the raw data of the dataset on whichever format we consider default.
        Structure (if not applicable it is not enforced):
            {
                 "train":[],
                 "dev":[],
                 "test":[]
            }
        """
        pass

    @abstractmethod
    def get_processed(self):
        """
        Returns the processed data of the dataset on whichever format we consider default.
        If many processed versions are available, the one we consider default should be the one returned.
        Structure (if not applicable it is not enforced):
            {
                 "train":[],
                 "dev":[],
                 "test":[]
            }
        """
        pass


