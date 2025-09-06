import smtplib
from email.message import EmailMessage
from datetime import datetime
from email.mime.text import MIMEText


def send_approval_email(posts, recepient_email, sender_email, sender_key, conn, cursor):
    msg = EmailMessage()
    msg["Subject"] = (
        f"Request for Post Approval {datetime.now().month}/{datetime.now().day}"
    )
    msg["From"] = "vps@techbot.com"
    msg["To"] = recepient_email
    body = "Hello!\n\nPlease review the following generated text and image for X:\n\n"
    article_ids = []
    for i, post in enumerate(posts):
        article_ids.append(post[1])
        body += f"{i + 1}. {post[2]}"
        res = cursor.execute("SELECT url FROM crawled_articles WHERE id==?", (post[1],)).fetchone()
        body += f"{res[0]}\n\n"
    msg.set_content(body)

    for i, post in enumerate(posts):
        with open(post[3], "rb") as f:
            img_data = f.read()
        msg.add_attachment(img_data, maintype="image", subtype="jpg")
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_key)
        server.send_message(msg)
        server.quit()
        for id in article_ids:
            cursor.execute("UPDATE generated_posts SET emailed=1 WHERE id==?", (id,))
            conn.commit()
    except Exception as e:
        print(f"Error sending email: {e}")


def send_no_new_posts_email(
    post, recepient_email, sender_email, sender_key, conn, cursor
):
    msg = EmailMessage()
    msg["Subject"] = f"Re-Request for Approval"
    msg["From"] = "vps@techbot.com"
    msg["To"] = recepient_email
    body = "Hello!\n\n\n\n"
    msg.set_content(body)
    with open(post[3], "rb") as f:
        img_data = f.read()
    msg.add_attachment(img_data, maintype="image", subtype="jpg")
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_key)
        server.send_message(msg)
        server.quit()
        cursor.execute("UPDATE generated_posts SET emailed=1 WHERE id==?", (post[0],))
        conn.commit()
    except Exception as e:
        print(f"Error sending email: {e}")
