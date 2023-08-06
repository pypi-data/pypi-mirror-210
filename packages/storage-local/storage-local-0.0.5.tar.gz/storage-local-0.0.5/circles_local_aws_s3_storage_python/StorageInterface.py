# Abstract Base Classes (abc)
from abc import ABC, abstractmethod

# Interface for all storage services


class StorageInterface(ABC):
    """
    Method uploads a file from local_path to the cloud in remoth_path, and names the file filname
    """
    @abstractmethod
    def upload_file(self, local_path, filename, remote_path, created_user_id) -> int:
        pass

    @abstractmethod
    def download_file(self, remote_path, local_path):
        pass

    @abstractmethod
    def delete_file(self, remote_path, filename, updated_user_id):
        pass
