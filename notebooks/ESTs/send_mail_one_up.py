import win32com.client as win32
import datetime
import pysftp
import os
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

TO_ADDRESS = 'thato.sello@circana.com'
# TO_ADDRESS = 'nasier@oneupcc.co.za'
CC_ADDRESSES = (
  # 'Marcus.Hendricks@Circana.com;'
  # 'Nabeela.Ebrahim@circana.com;'
  # 'Thato.Sello@circana.com;'
  # 'Varisha.Satayapal@circana.com;'
  # 'Gift.Mdlalose@circana.com;'
  # 'Kiash.Kalipersad@Circana.com;'
)

# SFTP configuration
SFTP_HOST = os.getenv('FTP_HOST')
SFTP_USERNAME = os.getenv('FTP_USERNAME')
SFTP_PASSWORD = os.getenv('FTP_PASSWORD')
SFTP_PORT = int(os.getenv('FTP_PORT', 22))
MY_EMAIL = os.getenv('MY_EMAIL')

SFTP_REMOTE_FOLDER = '/euestup1ftp/Up'  
DOWNLOAD_LOCATION = r'R:\RawData\Elite Star\One Up Cash & Carry\ToUpload'

class SFTPChecker:
    def __init__(self, host, username, password, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port

    def get_latest_file_info(self, remote_folder):
        """Check the SFTP folder for the latest file and its modification date."""
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        try:
            with pysftp.Connection(self.host, username=self.username, password=self.password, port=self.port, cnopts=cnopts) as sftp:
                sftp.cwd(remote_folder)
                files = sftp.listdir()
                if not files:
                    return None, None

                # Get the latest file based on modification time
                latest_file = None
                latest_modified_time = None
                for file in files:
                    file_path = remote_folder + '/' + file
                    modified_time = sftp.stat(file_path).st_mtime
                    if latest_modified_time is None or modified_time > latest_modified_time:
                        latest_file = file
                        latest_modified_time = modified_time

                return latest_file, datetime.datetime.fromtimestamp(latest_modified_time)
        except Exception as e:
            print(f"Failed to connect to SFTP server: {e}")
            return None, None

    def list_files(self, remote_folder):
        """List all files in the SFTP folder."""
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None  
        
        try:
            with pysftp.Connection(self.host, username=self.username, password=self.password, port=self.port, cnopts=cnopts) as sftp:
                sftp.cwd(remote_folder)
                files = sftp.listdir()
                return files
        except Exception as e:
            print(f"Failed to list files in SFTP folder: {e}")
            return []

    def download_file(self, remote_folder, file_name, local_folder):
        """Download a file from the SFTP server to a local folder."""
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None  
        try:
            with pysftp.Connection(self.host, username=self.username, password=self.password, port=self.port, cnopts=cnopts) as sftp:
                sftp.cwd(remote_folder)
                local_path = os.path.join(local_folder, file_name)
                sftp.get(file_name, local_path)
                print(f"File '{file_name}' downloaded to '{local_path}'.")
                return local_path
        except Exception as e:
            print(f"Failed to download file '{file_name}': {e}")
            return None

def send_email(subject, body, to_address, cc_addresses=None):
    """Send an email using Outlook."""
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)  

    mail.To = to_address
    if cc_addresses:
        mail.CC = cc_addresses
    mail.Subject = subject
    mail.Body = body

    try:
        mail.Send()
        print("Email sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def is_valid_file_name(file_name):
    """Check if the file name matches expected format (dd-dd Mon yyyy.csv)."""
    pattern = r'^\d{2}-\d{2} [A-Za-z]{3} \d{4}\.csv$'
    return re.match(pattern, file_name) is not None

def main():
    sftp_checker = SFTPChecker(SFTP_HOST, SFTP_USERNAME, SFTP_PASSWORD, SFTP_PORT)
    latest_file, latest_modified_date = sftp_checker.get_latest_file_info(SFTP_REMOTE_FOLDER)

    if latest_file and is_valid_file_name(latest_file):
        downloaded_file_path = sftp_checker.download_file(SFTP_REMOTE_FOLDER, latest_file, DOWNLOAD_LOCATION)
        if downloaded_file_path:
            subject = f'EST 1UP | File Downloaded: {latest_file}'
            body = (
                f"The latest file '{latest_file}' was downloaded from the SFTP server.\n\n"
                f"Download location: {downloaded_file_path}\n\n"
                f"File was last modified on: {latest_modified_date.strftime('%d %b %Y %H:%M:%S')}.\n\n"
                "Regards,\nThato (automated)"
            )
            send_email(subject, body, TO_ADDRESS, CC_ADDRESSES)
    else:
        # Use last modified date if the filename is invalid or doesn't exist.
        if latest_modified_date is not None:
            print(f"Latest modified date: {latest_modified_date}")
            # Additional logic can be added here if needed.

if __name__ == "__main__":
    main()
