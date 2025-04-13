import subprocess
import time

def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                ["pg_isready", "-h", host], check=True, capture_output=True, text=True)
            if "accepting connections" in result.stdout:
                print(f" PostgreSQL on {host} is ready!")
                return True
        except subprocess.CalledProcessError as e:
            print(f" Cannot connect to {host}: {e}")
        retries += 1
        print(f" Retrying in {delay_seconds}s... (Attempt {retries}/{max_retries})")
        time.sleep(delay_seconds)
    print(f" Max retries reached for {host}. Exiting.")
    return False


if not wait_for_postgres("source_postgres"):
    exit(1)
if not wait_for_postgres("destination_postgres"):
    exit(1)

print("Starting ELT script...")

source_config = {
    'dbname': 'source_db',
    'user': 'postgres',
    'password': 'secret',
    'host': 'source_postgres'
}

destination_config = {
    'dbname': 'destination_db',
    'user': 'postgres',
    'password': 'secret',
    'host': 'destination_postgres'
}

print("Dumping data from source_db...")
dump_command = [
    'pg_dump',
    '-h', source_config['host'],
    '-U', source_config['user'],
    '-d', source_config['dbname'],
    '-f', 'data_dump.sql',
    '-w'
]

subprocess_env = dict(PGPASSWORD=source_config['password'])
subprocess.run(dump_command, env=subprocess_env, check=True)
print("Dump completed.")

print("Loading data into destination_db...")
load_command = [
    'psql',
    '-h', destination_config['host'],
    '-U', destination_config['user'],
    '-d', destination_config['dbname'],
    '-a', '-f', 'data_dump.sql'
]

subprocess_env = dict(PGPASSWORD=destination_config['password'])
subprocess.run(load_command, env=subprocess_env, check=True)
print("Load completed.")

print("ELT script finished.")
