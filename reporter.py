# reporter.py
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_alert(status, prediction_map_path=None):
    print("--- Generating and sending report ---")

    # !! IMPORTANT: DO NOT hardcode your password. Use environment variables or a secure vault in a real application.
    # For Gmail, you need to create a special "App Password".
    sender_email = "your_email@gmail.com"
    receiver_email = "your_email@gmail.com" # Send to yourself for testing
    password = "YOUR_GMAIL_APP_PASSWORD"

    if status == "flood":
        subject = "Flood Alert: New Inundation Detected in Nagaon"
        body = f"An automated analysis of a new satellite image has detected potential flooding. The prediction map has been generated and is stored on the server at: {prediction_map_path}"
    elif status == "no_flood":
        subject = "No Flood Detected in Nagaon"
        body = f"An automated analysis of a new satellite image has been completed and no significant flooding was detected. The prediction map is available at: {prediction_map_path}"
    elif status == "no_data":
        subject = "Daily Flood Report: No New Satellite Imagery"
        body = "The daily check for new satellite imagery over the Nagaon area completed, but no new images were found in the last 24 hours."
    else:
        print("Invalid status for reporting.")
        return

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender_email, password)
            smtp_server.sendmail(sender_email, receiver_email, msg.as_string())
        print("✅ Alert sent successfully!")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--status', required=True, choices=['flood', 'no_flood', 'no_data'])
    parser.add_argument('--map', required=False) # The map is not required for a "no_data" status
    args = parser.parse_args()
    send_email_alert(args.status, args.map)