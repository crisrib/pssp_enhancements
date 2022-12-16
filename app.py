from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

db = SQLAlchemy()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + MYSQL_USERNAME + ':' + MYSQL_PASSWORD + '@' + MYSQL_HOST + ':3306/patients'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'iegrfiuerh38364%@g74'

db.init_app(app)

# Models
class Patients(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    zip_code = db.Column(db.String(255))
    dob = db.Column(db.String(255))
    gender = db.Column(db.String(255))

    # this first function __init__ is to establish the class for python GUI
    def __init__(self, mrn, first_name, last_name, zip_code,dob,gender):
        self.mrn = mrn
        self.first_name = first_name
        self.last_name = last_name
        self.zip_code = zip_code 
        self.dob = dob
        self.gender = gender 

    # this second function is for the API endpoints to return JSON 
    def to_json(self):
        return {'id': self.id,
        'mrn': self.mrn,
        'first_name': self.first_name,
        'last_name': self.last_name,
        'zip_code': self.zip_code,
        'dob': self.dob,
        'gender': self.gender}

class Conditions_patient(db.Model):
    __tablename__ = 'patient_conditions'
    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(255), db.ForeignKey('patients.mrn'))
    icd10_code = db.Column(db.String(255), db.ForeignKey('conditions.icd10_code'))

    # this first function __init__ is to establish the class for python GUI
    def __init__(self, mrn, icd10_code):
        self.mrn = mrn
        self.icd10_code = icd10_code

    # this second function is for the API endpoints to return JSON
    def to_json(self):
        return {'id': self.id, 'mrn': self.mrn, 'icd10_code': self.icd10_code}

class Conditions(db.Model):
    __tablename__ = 'conditions'
    id = db.Column(db.Integer, primary_key=True)
    icd10_code = db.Column(db.String(255))
    icd10_description = db.Column(db.String(255))

    # this first function __init__ is to establish the class for python GUI
    def __init__(self, icd10_code, icd10_description):
        self.icd10_code = icd10_code
        self.icd10_description = icd10_description

    # this second function is for the API endpoints to return JSON
    def to_json(self):
        return {'id': self.id, 'icd10_code': self.icd10_code, 'icd10_description': self.icd10_description}

class Medications_patient(db.Model):
    __tablename__ = 'patient_medications'
    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(255), db.ForeignKey('patients.mrn'))
    med_ndc = db.Column(db.String(255), db.ForeignKey('medications.med_ndc'))

    # this first function __init__ is to establish the class for python GUI
    def __init__(self, mrn, med_ndc):
        self.mrn = mrn
        self.med_ndc = med_ndc

    # this second function is for the API endpoints to return JSON
    def to_json(self):
        return {'id': self.id, 'mrn': self.mrn, 'med_ndc': self.med_ndc}
    
class Medications(db.Model):
    __tablename__ = 'medications'
    id = db.Column(db.Integer, primary_key=True)
    med_ndc = db.Column(db.String(255))
    med_human_name = db.Column(db.String(255))

    # this first function __init__ is to establish the class for python GUI
    def __init__(self, med_ndc, med_human_name):
        self.med_ndc = med_ndc
        self.med_human_name = med_human_name

    # this second function is for the API endpoints to return JSON
    def to_json(self):
        return {'id': self.id, 'med_ndc': self.med_ndc, 'med_human_name': self.med_human_name}

# Basic routes without data pulsl for now
@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

# Create basic GUI for CRUD
@app.route('/patients', methods=['GET'])
def get_gui_patients():
    returned_Patients = Patients.query.all()
    return render_template("patient_all.html", patients = returned_Patients)

# This endpoint is for inserting in a new patient
@app.route('/insert', methods = ['POST'])
def insert(): # note this function needs to match name in html form action 
    if request.method == 'POST':
        mrn = request.form['mrn']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        zip_code = request.form['zip_code']
        dob = request.form['dob']
        gender = request.form['gender']
        my_data = Patients(mrn, first_name, last_name, zip_code, dob, gender)
        db.session.add(my_data)
        db.session.commit()
        flash("Patient Inserted Successfully")
        return redirect(url_for('get_gui_patients'))

# This endpoint is for updating our patients basic info 
@app.route('/update', methods = ['GET', 'POST'])
def update(): # note this function needs to match name in html form action
    if request.method == 'POST':
        ## get mrn from form
        form_mrn = request.form.get('mrn')
        print('form_mrn', form_mrn)
        patient = Patients.query.filter_by(mrn=form_mrn).first()
        print('patient', patient)
        patient.first_name = request.form.get('first_name')
        patient.last_name = request.form.get('last_name')
        patient.zip_code = request.form.get('zip_code')
        patient.dob = request.form.get('dob')
        patient.gender = request.form.get('gender')
        db.session.commit()
        flash("Patient Updated Successfully")
        return redirect(url_for('get_gui_patients'))

# This route is for deleting our patients
@app.route('/delete/<string:mrn>', methods = ['GET', 'POST'])
def delete(mrn): # note this function needs to match name in html form action
    patient = Patients.query.filter_by(mrn=mrn).first()
    print('Found patient: ', patient)
    db.session.delete(patient)
    db.session.commit()
    flash("Patient Deleted Successfully")
    return redirect(url_for('get_gui_patients'))

# This route is for getting patient details
@app.route('/view/<string:mrn>', methods = ['GET'])
def get_patient_details(mrn):
    patient_details = Patients.query.filter_by(mrn=mrn).first()
    patient_conditions = Conditions_patient.query.filter_by(mrn=mrn).all()
    patient_medications = Medications_patient.query.filter_by(mrn=mrn).all()
    db_conditions = Conditions.query.all()
    return render_template("patient_details.html", patient_details = patient_details, 
        patient_conditions = patient_conditions, patient_medications = patient_medications,
        db_conditions = db_conditions)

# This endpoint is for updating ONE patient condition
@app.route('/update_conditions', methods = ['GET', 'POST'])
def update_conditions(): # note this function needs to match name in html form action
    if request.method == 'POST':
        ## get mrn from form
        form_id = request.form.get('id')
        print('form_id', form_id)
        form_icd10_code = request.form.get('icd10_code')
        print('form_icd10_code', form_icd10_code)
        patient_condition = Conditions_patient.query.filter_by(id=form_id).first()
        print('patient_condition', patient_condition)
        patient_condition.icd10_code = request.form.get('icd10_code')
        db.session.commit()
        flash("Patient Condition Updated Successfully")
        ## then return to patient details page
        return redirect(url_for('get_patient_details', mrn=patient_condition.mrn))

# Create basic API endpoints
# Get all patients
@app.route("/api/patients/list", methods=["GET"])
def get_patients():
    patients = Patients.query.all()
    return jsonify([patient.to_json() for patient in patients])

# Get specific Patient by MRN 
@app.route("/api/patients/<string:mrn>", methods=["GET"])
def get_patient(mrn):
    ## get patient by mrn column
    patient = Patients.query.filter_by(mrn=mrn).first()
    if patient is None:
        abort(404)
    return jsonify(patient.to_json())

# Basic post routes
# New patient 
@app.route('/api/patient', methods=['POST'])
def create_patient():
    if not request.json:
        abort(400)
    patient = Patients(
        mrn=request.json.get('mrn'),
        first_name=request.json.get('first_name'),
        last_name=request.json.get('last_name'),
        zip_code=request.json.get('zip_code'),
        dob= request.json.get('dob'),
        gender= request.json.get('gender')
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify(patient.to_json()), 201

# Update patient 
@app.route('/api/patient/<string:mrn>', methods=['PUT'])
def update_patient(mrn):
    if not request.json:
        abort(400)
    patient = Patients.query.filter_by(mrn=mrn).first()
    if patient is None:
        abort(404)
    patient.first_name = request.json.get('first_name', patient.first_name)
    patient.last_name = request.json.get('price', patient.last_name)
    db.session.commit()
    return jsonify(patient.to_json())

# Delete patient
@app.route("/api/patient/<string:mrn>", methods=["DELETE"])
def delete_patient(mrn):
    patient = Patients.query.filter_by(mrn=mrn).first()
    if patient is None:
        abort(404)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'result': True})




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)