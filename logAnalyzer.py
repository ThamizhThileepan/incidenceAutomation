import mysql.connector
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta

# Elasticsearch and MySQL configuration
ES_HOST = "localhost"  # Replace with your Elasticsearch host
ES_PORT = 9200
INDEX_NAME = ".ds-filebeat-8.15.3-2024.11.06-000001"  # Replace with your Elasticsearch index name

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "RAJsql"
MYSQL_DB = "log_analysis"

# Keywords or patterns for anomaly detection
ANOMALY_KEYWORDS = ["error", "failed", "exception", "critical","404","timed out"]

# Initialize Elasticsearch client
es = Elasticsearch([{"host": ES_HOST, "port": ES_PORT , "scheme": "http"}])

# MySQL connection setup
db_conn = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)
cursor = db_conn.cursor()

# Create the anomalies table if not exists
create_table_query = """
CREATE TABLE IF NOT EXISTS anomalies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    log_message TEXT,
    timestamp DATETIME,
    severity VARCHAR(50)
);
"""
cursor.execute(create_table_query)
db_conn.commit()

# Function to fetch logs from Elasticsearch
def fetch_logs():
    # Set the time window for log retrieval (e.g., last 15 minutes)
    #end_time = datetime.now()
    #start_time = end_time - timedelta(minutes=15)
    
    # Query for logs in the specified time range
    query = {
        "query": {
            # "range": {
            #     "@timestamp": {
            #         "gte": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            #         "lte": end_time.strftime("%Y-%m-%dT%H:%M:%S")
            #     }
            # }
            "match_all": {}
        }
    }
    
    # Fetch logs from Elasticsearch
    response = es.search(index=INDEX_NAME, body=query, size=1000)
    # return response['hits']['hits']
    logs = response['hits']['hits']
    print(f"Fetched {len(logs)} logs from Elasticsearch.")
    return logs

# Function to analyze logs and identify anomalies
def detect_anomalies(logs):
    anomalies = []
    for log in logs:
        message = log["_source"].get("message", "")
        
        es_timestamp = log["_source"].get("@timestamp", "")
        try:
            timestamp = datetime.strptime(es_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Convert to MySQL format
        except ValueError:
            print(f"Skipping log due to incompatible timestamp format: {es_timestamp}")
            continue
        
        # Check if any keyword in ANOMALY_KEYWORDS is in the log message
        if any(keyword.lower() in message.lower() for keyword in ANOMALY_KEYWORDS):
            #timestamp = log["_source"].get("@timestamp", "")
            severity = "High" if "critical" in message.lower() else "Moderate"
            
            # Store the anomaly data in a dictionary
            anomalies.append({
                "message": message,
                "timestamp": timestamp,
                "severity": severity
            })
            print(f"Anomaly detected: {message} | Severity: {severity} | Timestamp: {timestamp}")
    return anomalies

# Function to store anomalies in MySQL
def store_anomalies(anomalies):
    insert_query = """
    INSERT INTO anomalies (log_message, timestamp, severity)
    VALUES (%s, %s, %s)
    """
    for anomaly in anomalies:
        cursor.execute(insert_query, (anomaly["message"], anomaly["timestamp"], anomaly["severity"]))
    db_conn.commit()

# Main process
def main():
    # Fetch logs from Elasticsearch
    logs = fetch_logs()
    
    # Detect anomalies in the logs
    anomalies = detect_anomalies(logs)
    
    # Store anomalies in MySQL database
    if anomalies:
        store_anomalies(anomalies)
        print(f"Stored {len(anomalies)} anomalies in the database.")
    else:
        print("No anomalies detected in this batch.")

# Run the script
if __name__ == "__main__":
    main()

    # Close database connection
    cursor.close()
    db_conn.close()

