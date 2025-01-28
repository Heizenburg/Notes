import win32com.client as win32
import datetime
import pysftp
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email configuration
TO_ADDRESS = 'thato.sello@circana.com'
# TO_ADDRESS = 'nasier@oneupcc.co.za'
CC_ADDRESSES = (
  # 'Marcus.Hendricks@Circana.com;'
  # 'Nabeela.Ebrahim@circana.com;'
  # 'Thato.Sello@circana.com;'
  # 'Varisha.Satayapal@circana.com;'
  # 'Gift.Mdlalose@circana.com;'
  # 'Kiash.Kalipersad@Circana.com'
  # 'Simphiwe.Telana@circana.com'
)


# SFTP configuration
SFTP_HOST = os.getenv('FTP_HOST')
SFTP_USERNAME = os.getenv('FTP_USERNAME')
SFTP_PASSWORD = os.getenv('FTP_PASSWORD')
SFTP_PORT = int(os.getenv('FTP_PORT', 22))
MY_EMAIL = os.getenv('MY_EMAIL')
SFTP_REMOTE_FOLDER = '/euestup1ftp/Up'  
DAYS_THRESHOLD = 3  # Maximum allowed days since last file upload
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
    cnopts.hostkeys = None  # Disable host key checking
    try:
      with pysftp.Connection(self.host, username=self.username, password=self.password, port=self.port, cnopts=cnopts) as sftp:
        sftp.cwd(remote_folder)
        files = sftp.listdir()
        if not files:
          return None, None  # No files in the folder

        # Get the latest file based on modification time
        latest_file = None
        latest_modified_time = None
        for file in files:
          file_path = remote_folder + '/' + file
          modified_time = sftp.stat(file_path).st_mtime
          modified_date = datetime.datetime.fromtimestamp(modified_time)
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
    cnopts.hostkeys = None  # Disable host key checking
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
    cnopts.hostkeys = None  # Disable host key checking
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

def send_email(subject, body, to_address):
  """Send an email using Outlook."""
  outlook = win32.Dispatch('outlook.application')
  mail = outlook.CreateItem(0)  # 0 represents MailItem type

  # Set email parameters
  mail.To = to_address
  mail.Subject = subject
  mail.Body = body

  try:
    mail.Send()
    print("Email sent!")
  except Exception as e:
    print(f"Failed to send email: {e}")

def main():
  sftp_checker = SFTPChecker(SFTP_HOST, SFTP_USERNAME, SFTP_PASSWORD, SFTP_PORT)
  latest_file, latest_modified_date = sftp_checker.get_latest_file_info(SFTP_REMOTE_FOLDER)
  # Calculate the date threshold (3 days ago)
  threshold_date = datetime.datetime.now() - datetime.timedelta(days=DAYS_THRESHOLD)

  # Check if the latest file is recent
  if latest_modified_date is not None and latest_modified_date >= threshold_date:
    downloaded_file_path = sftp_checker.download_file(SFTP_REMOTE_FOLDER, latest_file, DOWNLOAD_LOCATION)
    if downloaded_file_path:
      subject = f'File Downloaded: {latest_file}'
      body = (
        f"The latest file '{latest_file}' was downloaded from the SFTP server.\n\n"
        f"Download location: {downloaded_file_path}\n\n"
        f"File was last modified on: {latest_modified_date.strftime('%d %b %Y %H:%M:%S')}.\n\n"
        "Regards,\nThato"
      )
      send_email(subject, body, MY_EMAIL)
  else:
    # Prepare email subject and body for Nasier
    today = datetime.date.today()
    last_week_sunday = today - datetime.timedelta(days=today.weekday() + 1)  # Latest Sunday
    last_week_sunday = last_week_sunday.strftime("%d %b %Y")

    subject = f'EST 1UP | WE-{last_week_sunday} | Weekly Feed Reminder'
    body = (
      "Hi Nasier,\n\n"
      "I hope you're well.\n\n"
      "This is a reminder to upload the latest dataset to our SFTP server.\n\n"
    )

    # Add file information to the email body
    if latest_modified_date:
      body += (
        f"The latest file in the SFTP folder is '{latest_file}', "
        f"last modified on {latest_modified_date.strftime('%d %b %Y %H:%M:%S')}.\n\n"
      )
    else:
      body += "No files were found in the SFTP folder.\n\n"

    # List all files in the SFTP folder as proof
    files = sftp_checker.list_files(SFTP_REMOTE_FOLDER)
    if files:
      body += "Files currently in the SFTP folder:\n\n"
      body += "\n".join(files)
    else:
      body += "The SFTP folder is empty."

    body += "\n\nRegards,\nThato"

    # Send the email to Nasier
    send_email(subject, body, TO_ADDRESS)

if __name__ == "__main__":
  main()