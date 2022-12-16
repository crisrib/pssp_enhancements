import dbm
import pandas as pd 
import sqlalchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

connection_string = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:3306/{MYSQL_DATABASE}'
db = create_engine(connection_string)

### drop the old tables that do not start with production_
def droppingFunction_limited(dbList, db_source):
    for table in dbList:
        if table.startswith('production_') == False:
            db_source.execute(f'drop table {table}')
            print(f'dropped table {table}')
        else:
            print(f'kept table {table}')

def droppingFunction_all(dbList, db_source):
    for table in dbList:
        db_source.execute(f'drop table {table}')
        print(f'dropped table {table} succesfully!')
    else:
        print(f'kept table {table}')


tableNames_db = db.table_names()
droppingFunction_all(tableNames_db, db)
db.table_names()

# Creating Tables
table_prod_patients = """
create table if not exists patients (
id int auto_increment,
mrn varchar(255) default null unique,
first_name varchar(255) default null,
last_name varchar(255) default null,
zip_code varchar(255) default null,
dob varchar(255) default null,
gender varchar(255) default null,
contact_mobile varchar(255) default null,
contact_email varchar(255) default null,
PRIMARY KEY (id)); """


table_prod_medications = """
create table if not exists medications(
id int auto_increment,
med_ndc varchar(255) default null unique,
med_human_name varchar(255) default null,
med_is_dangerous varchar(255) default null,
PRIMARY KEY (id)); """

table_prod_conditions = """
create table if not exists conditions(
id int auto_increment,
icd10_code varchar(255) default null unique,
icd10_description varchar(255) default null,
PRIMARY KEY (id) ); """

table_prod_patients_medications = """
create table if not exists patient_medications(
id int auto_increment,
mrn varchar(255) default null,
med_ndc varchar(255) default null,
PRIMARY KEY (id),
FOREIGN KEY (mrn) REFERENCES patients(mrn) ON DELETE CASCADE,
FOREIGN KEY (med_ndc) REFERENCES medications(med_ndc) ON DELETE CASCADE); """


table_prod_patient_conditions = """
create table if not exists patient_conditions (
    id int auto_increment,
    mrn varchar(255) default null,
    icd10_code varchar(255) default null,
    PRIMARY KEY (id),
    FOREIGN KEY (mrn) REFERENCES patients(mrn) ON DELETE CASCADE,
    FOREIGN KEY (icd10_code) REFERENCES conditions(icd10_code) ON DELETE CASCADE); """

db.execute(table_prod_patients)
db.execute(table_prod_medications)
db.execute(table_prod_conditions)
db.execute(table_prod_patients_medications)
db.execute(table_prod_patient_conditions)

db_tables = db.table_names()
db_tables