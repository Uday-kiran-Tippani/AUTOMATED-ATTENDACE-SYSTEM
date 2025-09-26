import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_test_email():
    sender_email = "adikavinannayauniversitystaff@gmail.com"       # your Gmail
    sender_password = "eblx ovrz ibzu prlo"       # 16-char App Password
    receiver_email = "udaykirantippani@gmail.com" # send to yourself for test

    subject = "✅ Test Email from Attendance System"
    body = "Hey buddy! This is a test email to check if SMTP is working fine."

    # Setup the MIME
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    send_test_email()
