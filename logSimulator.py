import random
import time
import datetime

# List of example IP addresses and users for failed login simulations
ip_addresses = ['192.168.1.1', '172.16.0.5', '203.0.113.15', '10.0.0.2', '198.51.100.45']
users = ['user1', 'user2', 'admin', 'guest', 'test']

# Log types: normal activity, HTTP errors, failed login attempts
log_types = ['INFO', 'ERROR', 'SECURITY']

# Example log messages
normal_logs = [
    'User accessed the dashboard',
    'User viewed the homepage',
    'File downloaded successfully',
    'Inside method cart()',
    'Inside method com.org.spring.getDetails()'
]

error_logs = [
    'HTTP 500 Internal Server Error',
    'HTTP 404 Not Found',
    'Database connection timed out',
]

security_logs = [
    'Failed password for {} from {}',
    'Unauthorized access attempt detected from {}',
    'Multiple failed login attempts detected from {}'
]

# Function to generate random log entries
def generate_log_entry():
    # Generate a random timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Select a random log type
    log_type = random.choice(log_types)

    if log_type == 'INFO':
        # Normal log entry
        message = random.choice(normal_logs)
        log_entry = f"{timestamp} {log_type}: {message}"

    elif log_type == 'ERROR':
        # Error log entry
        message = random.choice(error_logs)
        log_entry = f"{timestamp} {log_type}: {message}"

    elif log_type == 'SECURITY':
        # Security-related log entry (e.g., failed login attempt)
        user = random.choice(users)
        ip = random.choice(ip_addresses)
        message = random.choice(security_logs).format(user, ip)
        log_entry = f"{timestamp} {log_type}: {message}"

    return log_entry

# Function to generate logs continuously
def generate_logs_to_file(filename, num_logs=100, interval=5):
    with open(filename, 'a') as logfile:
        for _ in range(num_logs):
            log_entry = generate_log_entry()
            print(log_entry)  # Print to console (optional)
            logfile.write(log_entry + '\n')
            time.sleep(interval)  # Wait before generating the next log

# Generate 50 random logs every 2 seconds
if __name__ == "__main__":



    
    generate_logs_to_file('../logs/simulator.log', num_logs=50, interval=5)
