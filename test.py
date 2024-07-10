
import smtplib
from email.mime.text import MIMEText

# Email configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 465
smtp_user = 'mahdiarmansouri@gmail.com'
smtp_password = 'edwo lpav blpm ivtl'  # Use an app password if you have 2FA enabled

# Email content
subject = 'Test Email'
body = 'This is a test email.'
from_email = smtp_user
to_email = 'mahdiarm60@gmail.com'

# Create the email message
msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = from_email
msg['To'] = to_email

# Send the email
try:
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())
    print('Email sent successfully')
except Exception as e:
    print(f'Failed to send email: {e}')
