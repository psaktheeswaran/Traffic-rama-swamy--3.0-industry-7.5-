import os
import pyodbc
import pymongo
import firebase_admin
from firebase_admin import credentials, firestore
import pytesseract
from PIL import Image

# SQL Server Connection Details
sql_server = '<SQL_SERVER_NAME>'
database = '<DATABASE_NAME>'
username = '<USERNAME>'
password = '<PASSWORD>'

# MongoDB Connection Details
mongo_uri = '<MONGODB_CONNECTION_URI>'
mongo_database = '<MONGODB_DATABASE>'
mongo_collection = '<MONGODB_COLLECTION>'

# Firebase Service Account Details
firebase_credentials = '<PATH_TO_FIREBASE_CREDENTIALS_JSON>'
firebase_collection = '<FIREBASE_COLLECTION_NAME>'

# Set up Firebase credentials
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
firebase_db = firestore.client()

# Connect to SQL Server
sql_connection = pyodbc.connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                                 f"SERVER={sql_server};"
                                 f"DATABASE={database};"
                                 f"UID={username};"
                                 f"PWD={password}")

# Connect to MongoDB
mongo_client = pymongo.MongoClient(mongo_uri)
mongo_db = mongo_client[mongo_database]
mongo_col = mongo_db[mongo_collection]

# Function to perform OCR on an image
def perform_ocr(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

# Function to compare OCR text with database
def compare_with_database(text):
    # Compare with SQL database
    cursor = sql_connection.cursor()
    cursor.execute(f"SELECT * FROM <TABLE_NAME> WHERE <COLUMN_NAME> = '{text}'")
    sql_result = cursor.fetchone()

    # Compare with MongoDB
    mongo_result = mongo_col.find_one({'<FIELD_NAME>': text})

    # Compare with Firebase
    firebase_result = firebase_db.collection(firebase_collection).where('<FIELD_NAME>', '==', text).get()

    # Return the results
    return sql_result, mongo_result, firebase_result

# Main code
image_folder = '<PATH_TO_IMAGE_FOLDER>'
for image_file in os.listdir(image_folder):
    image_path = os.path.join(image_folder, image_file)
    ocr_text = perform_ocr(image_path)
    sql_result, mongo_result, firebase_result = compare_with_database(ocr_text)

    # Check for matches
    if sql_result or mongo_result or not firebase_result.empty:
        print(f'Match found for image: {image_file}')
    else:
        print(f'No match found for image: {image_file}')

