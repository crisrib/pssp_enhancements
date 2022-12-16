import dbm
import pandas as pd 
import sqlalchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from faker import Faker # https://faker.readthedocs.io/en/master/
import uuid
import random

load_dotenv()

MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

connection_string = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:3306/{MYSQL_DATABASE}'
db = create_engine(connection_string)

print(db.table_names())

# Creating fake patient data
fake = Faker()

fake_patients = [
    {
        #keep just the first 8 characters of the uuid
        'mrn': str(uuid.uuid4())[:8], 
        'first_name':fake.first_name(), 
        'last_name':fake.last_name(),
        'zip_code':fake.zipcode(),
        'dob':(fake.date_between(start_date='-90y', end_date='-20y')).strftime("%Y-%m-%d"),
        'gender': fake.random_element(elements=('M', 'F')),
        'contact_mobile':fake.phone_number(),
        'contact_email':fake.phone_number()
    } for x in range(50)]

df_fake_patients = pd.DataFrame(fake_patients)
df_fake_patients = df_fake_patients.drop_duplicates(subset=['mrn'])

insertQuery = "INSERT INTO patients (mrn, first_name, last_name, zip_code, dob, gender, contact_mobile, contact_email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
for index, row in df_fake_patients.iterrows():
    db.execute(insertQuery, (row['mrn'], row['first_name'], row['last_name'], row['zip_code'], row['dob'], row['gender'], row['contact_mobile'], row['contact_email']))
    print("Inserting row: ", index)

# NDC codes - Medication Table
ndc_codes = pd.read_csv('https://raw.githubusercontent.com/hantswilliams/FDA_NDC_CODES/main/NDC_2022_product.csv')
ndc_codes_1k = ndc_codes.sample(n=1000, random_state=1)
ndc_codes_1k = ndc_codes_1k.drop_duplicates(subset=['PRODUCTNDC'], keep='first')

insertQuery = "INSERT INTO medications (med_ndc, med_human_name) VALUES (%s, %s)"
medRowCount = 0
for index, row in ndc_codes_1k.iterrows():
    medRowCount += 1
    db.execute(insertQuery, (row['PRODUCTNDC'], row['NONPROPRIETARYNAME']))
    print("inserted row: ", index)
    if medRowCount == 75:
        break

# Patient medication Table
df_medications = pd.read_sql_query("SELECT med_ndc FROM medications", db) 
df_patients = pd.read_sql_query("SELECT mrn FROM patients", db)

# Create a stacked df & give each patient a random number of medications between 1-5
df_patient_medications = pd.DataFrame(columns=['mrn', 'med_ndc'])

# For each patient in df_patient_medications, take a random number of medications between 1-10 from df_medications and palce it in df_patient_medications
for index, row in df_patients.iterrows():
    # get a random number of medications between 1 and 5
    numMedications = random.randint(1, 5)
    # get a random sample of medications from df_medications
    df_medications_sample = df_medications.sample(n=numMedications)
    # add the mrn to the df_medications_sample
    df_medications_sample['mrn'] = row['mrn']
    # append the df_medications_sample to df_patient_medications
    df_patient_medications = df_patient_medications.append(df_medications_sample)

print(df_patient_medications.head(10))

# Add a random medication to each patient
insertQuery = "INSERT INTO patient_medications (mrn, med_ndc) VALUES (%s, %s)"
for index, row in df_patient_medications.iterrows():
    db.execute(insertQuery, (row['mrn'], row['med_ndc']))
    print("inserted row: ", index)

# ICD10 codes CONDITIONS
icd10codes = pd.read_csv('https://raw.githubusercontent.com/Bobrovskiy/ICD-10-CSV/master/2020/diagnosis.csv')
list(icd10codes.columns)
icd10codesShort = icd10codes[['CodeWithSeparator', 'ShortDescription']]
icd10codesShort_1k = icd10codesShort.sample(n=1000)
icd10codesShort_1k = icd10codesShort_1k.drop_duplicates(subset=['CodeWithSeparator'], keep='first')

insertQuery = "INSERT INTO conditions (icd10_code, icd10_description) VALUES (%s,%s)"
startingRow = 0
for index, row in icd10codesShort_1k.iterrows():
    startingRow += 1
    print('startingRow: ', startingRow)
    print("inserted row db_azure: ", index)
    db.execute(insertQuery, (row['CodeWithSeparator'], row['ShortDescription']))
    print("inserted row db_gcp: ", index)
    if startingRow == 100: 
        break

df_gcp = pd.read_sql_query("SELECT * FROM conditions", db)

# Patient Conditions Table
df_conditions = pd.read_sql_query("SELECT icd10_code FROM conditions", db)
df_patients = pd.read_sql_query("SELECT mrn FROM patients", db)

# Create stacked df & give each patient a random number of conditions between 1-5
df_patient_conditions = pd.DataFrame(columns=['mrn', 'icd10_code'])
# For each patient in df_patient_conditions, take a random number of conditions between 1-10 from df_conditions and palce it in df_patient_conditions
for index, row in df_patients.iterrows():
    # get a random number of conditions between 1 and 5
    # numConditions = random.randint(1, 5)
    # get a random sample of conditions from df_conditions
    df_conditions_sample = df_conditions.sample(n=random.randint(1, 5))
    # add the mrn to the df_conditions_sample
    df_conditions_sample['mrn'] = row['mrn']
    # append the df_conditions_sample to df_patient_conditions
    df_patient_conditions = df_patient_conditions.append(df_conditions_sample)

print(df_patient_conditions.head(20))

# Add a random condition to each patient
insertQuery = "INSERT INTO patient_conditions (mrn, icd10_code) VALUES (%s, %s)"
for index, row in df_patient_conditions.iterrows():
    db.execute(insertQuery, (row['mrn'], row['icd10_code']))
    print("inserted row: ", index)

df_conditions = pd.read_sql_query("SELECT icd10_code FROM conditions", db)
df_patients = pd.read_sql_query("SELECT mrn FROM patients", db)
