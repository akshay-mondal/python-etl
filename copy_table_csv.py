import oracledb
import csv
import os
import boto3
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Get Oracle credentials from environment variables
username = os.getenv('ORACLE_USERNAME')
password = os.getenv('ORACLE_PASSWORD')
dsn = os.getenv('ORACLE_DSN')
oracle_client_path = os.getenv('ORACLE_CLIENT_PATH')

# Get AWS credentials and S3 bucket details
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
s3_bucket_name = os.getenv('S3_BUCKET_NAME')

# Initialize Oracle Instant Client (for thick mode)
try:
    oracledb.init_oracle_client(lib_dir=oracle_client_path)  # Path from environment variable
except oracledb.DatabaseError as e:
    print(f"Error initializing Oracle Client: {e}")
    exit(1)

schema_name = 'classicmodels'
table_name = 'productlines'

# Connect to Oracle Database using python-oracledb in thick mode
try:
    connection = oracledb.connect(user=username, password=password, dsn=dsn)
    print("Successfully connected to Oracle Database")

    # Create a cursor
    cursor = connection.cursor()

    # Query the required table from the required schema
    query = f"SELECT productLine, textDescription FROM {schema_name}.{table_name}"
    cursor.execute(query)

    # Fetch column names
    column_names = [desc[0] for desc in cursor.description]

    # Fetch all data from the query
    rows = cursor.fetchall()

    # Save the data to a CSV file under the folder 'task_1-2'
    csv_file = f'task_1-2/{schema_name}.{table_name}.csv'
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the column headers
        writer.writerow(column_names)

        # Write the rows
        writer.writerows(rows)

    print(f"'{schema_name}.{table_name}' table has been successfully saved locally as {csv_file}")
    
    # Upload the CSV file to S3 
    try:
        s3_client = boto3.client('s3',
                                aws_access_key_id=aws_access_key,
                                aws_secret_access_key=aws_secret_key,
                                region_name=aws_region)
        
    except:
        print(f"Error: Cannot connect to AWS S3")
        
    # Upload local file to S3
    with open(csv_file, 'rb') as file_data:
        s3_client.put_object(
            Bucket=s3_bucket_name,
            Key=csv_file,
            Body=file_data
        )

    print(f"'{schema_name}.{table_name}' table has been successfully uploaded to S3 as {csv_file}")

except oracledb.DatabaseError as e:
    print(f"Error: {e}")
finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
        print("Database connection closed.")
