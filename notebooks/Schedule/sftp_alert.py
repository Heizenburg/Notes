import pysftp
import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

# FTP server credentials
ftp_user = os.getenv('FTP_USERNAME')
ftp_host = os.getenv('FTP_HOST')
ftp_pass = os.getenv('FTP_PASSWORD')

# Email settings
sender_email   = os.getenv('SENDER_EMAIL')
receiver_email = os.getenv('RECEIVER_EMAIL')
email_password = os.getenv('GMAIL_PASSWORD')
smtp_server    = os.getenv('SMTP_SERVER')
smtp_port      = os.getenv('SMTP_PORT') # or 465 for SSL

ftp_directory = '/euestup1ftp/Up'
# Function to list files using pysftp
def list_files():
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None  # Disable host key checking
    try:
        with pysftp.Connection(ftp_host, username=ftp_user, password=ftp_pass, port=22, cnopts=cnopts) as sftp:
            with sftp.cd(ftp_directory):
                files = sftp.listdir()
                print('Files listed successfully')
                return files
    except Exception as e:
        print(f"SFTP error: {e}")
        return []


# Function to send email alert
def send_email_alert(new_files):
    msg = EmailMessage()
    msg.set_content('New files uploaded: ' + ', '.join(new_files))
    msg['Subject'] = 'FTP Alert: New Files Uploaded'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, email_password)
            server.send_message(msg)
            print('Email alert sent successfully')
    except Exception as e:
        print(f"Error sending email alert: {e}")

def main():
    try:
        # Load previously recorded files
        with open('recorded_files.txt', 'r') as file:
            recorded_files = file.read().splitlines()
    except FileNotFoundError:
        recorded_files = []

    # List current files on the FTP server
    current_files = list_files()
    
    new_files = [file for file in current_files if file not in recorded_files]

    if new_files:
        send_email_alert(new_files)
        
        with open('recorded_files.txt', 'w') as file:
            file.write('\n'.join(current_files))

if __name__ == "__main__":
    main()

