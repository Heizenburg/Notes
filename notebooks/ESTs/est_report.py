import ftplib
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration for FTP and Email
FTP_HOST = 'your_ftp_host'
FTP_USER = 'your_username'
FTP_PASS = 'your_password'
EMAIL_SENDER = 'your_email@example.com'
EMAIL_RECEIVER = 'receiver_email@example.com'
EMAIL_SUBJECT = 'Contents of FTP Folders'

# Function to list files in a given FTP directory
def list_files(ftp, remote_folder):
	files_list = []
	
	# Change to the specified directory
	ftp.cwd(remote_folder)
	
	# List files in the directory
	files = ftp.nlst()
	
	for file in files:
			files_list.append(file)

	return files_list


# Main function to execute the program
def main():
    folders_to_check = ['/euestup1ftp/Up', '/euetrac1ftp/Up/A1 SUPERMARKET']
    all_files = []

    try:
        # Connect to FTP server
        with ftplib.FTP(FTP_HOST) as ftp:
            ftp.login(FTP_USER, FTP_PASS)
            print(f"Connected to {FTP_HOST}")
            
            # List files from each folder and combine them
            for folder in folders_to_check:
                print(f"Checking folder: {folder}")
                files_in_folder = list_files(ftp, folder)
                all_files.extend(files_in_folder)

            if all_files:
                print("Files found:")
                for file in all_files:
                    print(file)
                
                # Send email with the list of files
                # send_email(all_files)
            else:
                print("No files found in the specified folders.")
                
    except ftplib.all_errors as e:
        print(f"FTP error: {e}")

if __name__ == "__main__":
    main()