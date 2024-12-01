import mysql.connector
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Database configuration
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "RAJsql"
MYSQL_DB = "log_analysis"

# Gmail configuration
GMAIL_USER = "thamizhproject@gmail.com"
GMAIL_PASSWORD = "bdxkvunvgqgooosg"  # App Password if 2FA enabled
RECIPIENT_EMAIL = "thamizhthileepan@gmail.com"

# Connect to MySQL database
db_conn = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)
cursor = db_conn.cursor()

# Track last notification ID
last_notified_id = 0

# Function to fetch new anomalies
def fetch_new_anomalies():
    global last_notified_id
    query = "SELECT id, log_message, timestamp, severity FROM anomalies WHERE id > %s"
    cursor.execute(query, (last_notified_id,))
    anomalies = cursor.fetchall()
    
    if anomalies:
        last_notified_id = max([anomaly[0] for anomaly in anomalies])
    
    return anomalies

# Function to send a notification email
def send_email_notification(anomaly):
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = "New Anomaly Detected"
    
    body = f"""\
    Anomaly Detected:
    - **Message**: {anomaly[1]}
    - **Timestamp**: {anomaly[2]}
    - **Severity**: {anomaly[3]}
    """
    msg.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())
            print("Email notification sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Main loop to continuously check for anomalies
def main():
    try:
        while True:
            anomalies = fetch_new_anomalies()
            if anomalies:
                for anomaly in anomalies:
                    send_email_notification(anomaly)
            else:
                print("No new anomalies detected.")
                
            # Wait for a minute before checking again
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping notification service.")
    finally:
        cursor.close()
        db_conn.close()

if __name__ == "__main__":
    main()

