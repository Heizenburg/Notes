import win32com.client as win32
import datetime

TO_ADDRESS = 'nasier@oneupcc.co.za'
CC_ADDRESSES = (
    'Marcus.Hendricks@Circana.com;'
    'Nabeela.Ebrahim@circana.com;'
    'Thato.Sello@circana.com;'
    'Varisha.Satayapal@circana.com;'
    'Gift.Mdlalose@circana.com;'
    'Kiash.Kalipersad@Circana.com'
)

def send_email():
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)  # 0 represents MailItem type

    today = datetime.date.today()
    last_week_sunday = today - datetime.timedelta(days=today.weekday() + 1) # Looks for the latest Sunday
    last_week_sunday = last_week_sunday.strftime("%d %b %Y") 

    # Set email parameters
    mail.To = TO_ADDRESS
    mail.CC = CC_ADDRESSES  
    mail.Subject = f'EST 1UP | WE-{last_week_sunday} | Weekly Feed'
    mail.Body = (
        "Hi Nasier,\n\n"
        "I hope you're well.\n\n"
        "Just a reminder to upload the latest dataset to our FTP server.\n\n"
        "Thank you!\n\n"
        "Regards,\n"
        "Thato"
    )

    try:
        mail.Send()
        print("Email sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_email()