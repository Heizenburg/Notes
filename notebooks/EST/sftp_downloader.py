import pysftp
import datetime
import os
from dotenv import load_dotenv

class SFTPDownloader:
    def __init__(self, host, username, password, port=22, days=3):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.days = days

    def download_data(self, remote_folder, local_folder):
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None  # Disable host key checking
        with pysftp.Connection(self.host, username=self.username, password=self.password, port=self.port, cnopts=cnopts) as sftp:
            self._download_files(sftp, remote_folder, local_folder)

    def _download_files(self, sftp, remote_folder, local_folder):
        print(f"{self.username}: Connected to {self.host} SFTP server")
        sftp.cwd(remote_folder)
        files = sftp.listdir()
        for file in files:
            file_path = remote_folder + '/' + file
            modified_time = sftp.stat(file_path).st_mtime
            modified_date = datetime.datetime.fromtimestamp(modified_time)
            days_difference = (datetime.datetime.now() - modified_date).days
            if days_difference <= self.days:
                sftp.get(file_path, local_folder + '/' + file)
                print(f"Downloaded {file} from {remote_folder}")
        directories = [file for file in files if sftp.isdir(remote_folder + '/' + file)]
        for directory in directories:
            self._download_files(sftp, remote_folder + '/' + directory, local_folder + '/' + directory)
        print("Downloading complete")




