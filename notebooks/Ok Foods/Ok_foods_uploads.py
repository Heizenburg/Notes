import pysftp
import os
from getpass import getpass
from dotenv import load_dotenv

class SFTPUploader:
  def __init__(self, host, username, password=None, port=22):
    self.host = host
    self.username = username
    self.password = password
    self.port = port

  def get_password(self):
    if self.password is None:
      # Check if password is available in environment file
      load_dotenv('.env')
      password = os.getenv('FTP_PASSWORD')
      if password:
        self.password = password
      else:
        self.password = getpass('Enter SFTP password: ')

  def upload_data(self, local_folder, remote_folder, client_name):
      self.get_password()
      cnopts = pysftp.CnOpts()
      cnopts.hostkeys = None  # Disable host key checking
      with pysftp.Connection(self.host, username=self.username, password=self.password, port=self.port, cnopts=cnopts) as sftp:
        self._upload_files(sftp, local_folder, remote_folder, client_name)

  def _upload_files(self, sftp, local_folder, remote_folder, client_name):
    sftp.cwd(remote_folder)
    files = sftp.listdir()
    for file in files:
      file_path = remote_folder + '/' + file
      if sftp.isfile(file_path):
          sftp.remove(file_path)
    for file in os.listdir(local_folder):
      local_file_path = os.path.join(local_folder, file)
      remote_file_path = remote_folder + '/' + file
      if client_name.lower() in file.lower():
          remote_file_path = os.path.join(remote_folder, file) 
          sftp.put(local_file_path, remote_file_path)
          print(f"Uploaded {file} to {remote_folder}")
    directories = [file for file in os.listdir(local_folder) if os.path.isdir(os.path.join(local_folder, file))]
    for directory in directories:
      local_directory_path = os.path.join(local_folder, directory)
      remote_directory_path = remote_folder + '/' + directory
      sftp.mkdir(remote_directory_path)
      self._upload_files(sftp, local_directory_path, remote_directory_path, client_name)1

if __name__ == "__main__":
  
	sftp_uploader = SFTPUploader('sftp.eu.infores.com', 'tsello01', 22)
	source_folder = r'Q:\Manufacturer Services\General\CSV Extractions\New CSV Extraction\Ok foods\\Weekly Delivery'

	upload_list = [
			(source_folder, r'\euaqurs6ftp\\Down\OKFOODS', 'Aquelle'),
			(source_folder, r'\eudilys4ftp\\Down\OKFOODS', 'Diageo'),
			(source_folder, r'\eurclva4ftp\\Down\RCL',     'Siqalo'),
			(source_folder, r'\eurclva4ftp\\Down\RCL',     'RCL'),
			(source_folder, r'\eurymjc8ftp\\Down\OKFOODS', 'Rymco'),
			(source_folder, r'\eusouba6ftp\\Down\OKFOODS', 'Southern'),
			(source_folder, r'\eusutnm7ftp\\Down\OKFOODS', 'Thokoman Foods')
	]

	for source_folder, remote_folder, client_name in upload_list:
		print(f"{remote_folder}, {client_name}")
		sftp_uploader.upload_data(source_folder, remote_folder, client_name)