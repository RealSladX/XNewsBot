import smtplib
from email.mime.text import MIMEText

def send_approval_email(articles, admin_email):
    body = "Please review and approve the following articles:\n\n"
    for i, article in enumerate(articles, 1):
        body += f"{i}. {article['title']}\n"
        body += f"Summary: {article['summary']}\n"
        body += f"Score: {article['score']}\n\n"
    
    msg = MIMEText(body)
    msg['Subject'] = 'Daily Tech Articles for Approval'
    msg['From'] = 'vps@techbot.com'
    msg['To'] = admin_email
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("liquidpacket@gmail.com", "guyl ivkp ckjd nmnf")
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")

def send_test_email():
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
# start TLS for security
    s.starttls()
# Authentication
    s.login("liquidpacket@gmail.com", "guyl ivkp ckjd nmnf")
# message to be sent
    message = "WHADDUP NIMROD"
# sending the mail
    s.sendmail("notsladx@gmail.com", "imsladx@gmail.com", message)
# terminating the session
    s.quit()

