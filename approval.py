import smtplib
from email.mime.text import MIMEText


def send_approval_email(articles, admin_email, sender_email, sender_key):
    body = "Please review and approve the following articles:\n\n"
    for i, article in enumerate(articles, 1):
        body += f"{i}. {article['title']}\n"
        body += f"Summary: {article['summary']}\n"
        body += f"Score: {article['score']}\n\n"

    msg = MIMEText(body)
    msg["Subject"] = "Daily Tech Articles for Approval"
    msg["From"] = "vps@techbot.com"
    msg["To"] = admin_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_key)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")

