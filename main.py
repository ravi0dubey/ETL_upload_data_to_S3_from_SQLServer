import mysql.connector as connection
from sqlalchemy import create_engine
import mysql.connector as connection
from sqlalchemy.orm import sessionmaker, scoped_session
import pandas as pd
import json
import io
import boto3
import os

# Get API Keys
content = open('config.json')
config = json.load(content)
access_key = config['access_key']
secret_access_key = config['secret_access_key']


def connect_extract_db():
    try:
        mydb = connection.connect(host="localhost", user="root", passwd="root", use_pure=True)
        df = pd.read_sql("select * from projectdb.superstore_usa_orders", mydb)
        load(df, 'super_store')
    except Exception as e:
            print("Data extract error: " + str(e))
            return (str(e))
    
# load data to postgres
def load(df, tbl):
    try:
        rows_imported = 0
        print(f'importing rows {rows_imported} to {rows_imported + len(df)}... for table {tbl}')
        # save to s3
        upload_file_bucket = 'sqldb-bucket'
        upload_file_key = 'public/' + str(tbl) + f"/{str(tbl)}"
        filepath =  upload_file_key + ".csv"
        #
        s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_access_key,region_name='us-east-1')
        with io.StringIO() as csv_buffer:
            df.to_csv(csv_buffer, index=False)

            response = s3_client.put_object(
                Bucket=upload_file_bucket, Key=filepath, Body=csv_buffer.getvalue()
            )

            status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

            if status == 200:
                print(f"Successful S3 put_object response. Status - {status}")
            else:
                print(f"Unsuccessful S3 put_object response. Status - {status}")
            rows_imported += len(df)
            print("Data imported successful")
    except Exception as e:
        print("Data load error: " + str(e))


try:
    # call extract function
    connect_extract_db()
except Exception as e:
    print("Error while extracting data: " + str(e))