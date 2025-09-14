# reporter.py
import argparse
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_alert(status, prediction_map_path=None, error_message=None):
    """
    Sends an email notification based on the pipeline's status.
    """
    print(f"--- Generating report for status: {status} ---")

    # Securely gets the email password from an environment variable (GitHub Secret)
    password = os.environ.get('GMAIL_APP_PASSWORD')
    sender_email = "your_email@gmail.com"  # Change this
    receiver_email = "your_email@gmail.com" # Change this

    if not password:
        print("FATAL: GMAIL_APP_PASSWORD environment variable not set.")
        return

    # --- Email content based on status ---
    if status == "flood":
        subject = "Flood Alert: Inundation Detected in Monitored Area"
        body = (f"An automated analysis of a new satellite image has detected significant flooding.\n\n"
                f"The flood prediction map is available on the server at:\n{prediction_map_path}")
    elif status == "no_flood":
        subject = "Daily Report: No Flood Detected"
        body = (f"An automated analysis of a new satellite image has been completed, and no significant flooding was detected.\n\n"
                f"The prediction map is available at:\n{prediction_map_path}")
    elif status == "no_data":
        subject = "Daily Report: No New Satellite Imagery Found"
        body = "The daily check for new satellite imagery completed, but no new images were found in the last 24 hours for the monitored area."
    elif status == "pipeline_failed":
        subject = "CRITICAL ALERT: Flood Detection Pipeline Failed"
        body = (f"The automated flood detection pipeline encountered a critical error and could not complete its run.\n\n"
                f"Error Message:\n{error_message}")
    else:
        print(f"Invalid status '{status}' for reporting.")
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
        print("✅ Email alert sent successfully!")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send email reports for the flood detection pipeline.")
    parser.add_argument('--status', required=True, choices=['flood', 'no_flood', 'no_data', 'pipeline_failed'])
    parser.add_argument('--map', help="Path to the prediction map TIFF file.")
    parser.add_argument('--error-message', help="The error message to include in failure reports.")
    args = parser.parse_args()

    send_email_alert(args.status, args.map, args.error_message)
