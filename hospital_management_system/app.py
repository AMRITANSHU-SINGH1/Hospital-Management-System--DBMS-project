from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template,request,redirect,url_for
from flask import render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
from flask import session,flash,redirect,url_for,jsonify
from datetime import date,datetime,timedelta,timezone
'''----IMPORTED ALL THE IMPORTANT THINGS------ '''
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
app.secret_key = 'your-secret-key-here-change-in-production'

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'admin' or 'admin_id' not in session:
            flash('Please login as admin first')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'doctor_id' not in session:
            flash('Please login as doctor first')
            return redirect(url_for('doctor_login'))
        return f(*args, **kwargs)
    return decorated_function


def patient_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'patient_id' not in session:
            flash('Please login as patient first')
            return redirect(url_for('patient_login'))
        return f(*args, **kwargs)
    return decorated_function



'''---------MODELS AND RELATIONSHIPS STARTS FROM HERE ------------'''
class Department(db.Model):
     id=db.Column(db.Integer,primary_key=True)
     dpt_id=db.Column(db.String(20),unique=True)
     name=db.Column(db.String(100),nullable=False)
     # specialization=db.Column(db.String(100))
     head=db.Column(db.String(100))  #this input should be the doctor id 

class Doctor(db.Model):
     id=db.Column(db.Integer,primary_key=True)
     doc_id=db.Column(db.String(20),unique=True)
     name=db.Column(db.String(100),nullable=False)
     dept_id=db.Column(db.String(20),db.ForeignKey('department.dpt_id'))
     status=db.Column(db.String(20),default="Active")
     spec=db.Column(db.String(100))
     email = db.Column(db.String(120), unique=True, nullable=False)    
     password_hash = db.Column(db.String(128), nullable=False)
     def set_password(self, password):
          self.password_hash = generate_password_hash(password)

     def check_password(self, password):
          return check_password_hash(self.password_hash, password)


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pat_id=db.Column(db.String(20),unique=True)
    name = db.Column(db.String(100), nullable=False)
    age=db.Column(db.Integer,nullable=False)
    blood=db.Column(db.String(10),nullable=False)
    gender=db.Column(db.String(20),nullable=False)
    contact_info = db.Column(db.Integer,nullable=False)
    #update after version 1
    email = db.Column(db.String(120), unique=True, nullable=False)  
    password_hash = db.Column(db.String(128), nullable=False)      
    def set_password(self, password):
          self.password_hash = generate_password_hash(password)

    def check_password(self, password):
          return check_password_hash(self.password_hash, password)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.String(20), db.ForeignKey('doctor.doc_id'),nullable=False)
    pat_id = db.Column(db.String(20), db.ForeignKey('patient.pat_id'),nullable=False)
    date = db.Column(db.Date,nullable=False)
    time = db.Column(db.String(5),nullable=False)
    status = db.Column(db.String(20),default='Pending',nullable=False)

class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    diagnosis = db.Column(db.String(200))
    prescription = db.Column(db.String(200))
    notes = db.Column(db.String(500))
    date = db.Column(db.String(10))
    status = db.Column(db.String(20))

class Admin(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String(100), nullable=False)
     #below are the updates for the admin
     username=db.Column(db.String(50),unique=True)
     email = db.Column(db.String(120), unique=True, nullable=False)   
     password_hash = db.Column(db.String(128), nullable=False)

     def set_password(self,password):
          self.password_hash=generate_password_hash(password)
     
     def check_password(self, password):
          return check_password_hash(self.password_hash, password)

class DoctorAvailability(db.Model):
    __tablename__ = 'doctor_availability'

    id = db.Column(db.Integer, primary_key=True)

    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)

    date = db.Column(db.Date, nullable=False)  # YYYY-MM-DD format

    start_time = db.Column(db.String(5), nullable=False)  # HH:MM format (e.g., "09:00")
    end_time = db.Column(db.String(5), nullable=False)  # HH:MM format (e.g., "17:00")

    slot_duration = db.Column(db.Integer, default=30)  # Duration in minutes (default 30 min)
    
    is_available = db.Column(db.Boolean, default=True)  # Can be marked as unavailable

    doctor = db.relationship('Doctor', backref=db.backref('availabilities', lazy=True))

    def __repr__(self):
        return f'<Availability {self.doctor_id} on {self.date}>'
    

class Prescription(db.Model):
    __tablename__ = 'prescription'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    doctor_id = db.Column(db.String(20), db.ForeignKey('doctor.doc_id'), nullable=False)
    patient_id = db.Column(db.String(20), db.ForeignKey('patient.pat_id'), nullable=False)
    
    # Prescription details
    diagnosis = db.Column(db.String(500), nullable=False)
    medicines = db.Column(db.Text, nullable=False)
    dosage = db.Column(db.String(500))
    instructions = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Timestamps
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda:datetime.now(timezone.utc))
    
    # Relationships
    appointment = db.relationship('Appointment', backref=db.backref('prescription', uselist=False))
    
    def __repr__(self):
        return f'<Prescription {self.id} for Patient {self.patient_id}>'

     


''' MODELS ENDS HERE ---> ADDED ALL THE MODELS THAT ARE NEEDED WITH RELATIONSHIPS -------'''
@app.route('/')
def home():
     return render_template('home.html')

''' -------below are the login routes----'''
@app.route('/admin/login',methods=['GET','POST'])
def admin_login():
     if request.method=='POST':
          username=request.form['username']
          password=request.form['password']

          admin=Admin.query.filter_by(username=username).first()

          if admin and admin.check_password(password):
               session['admin_id']=admin.id
               session['user_type']='admin'
               flash('Login successful!')
               return redirect(url_for('admin_dashboard'))
          else:
               flash('Invalid username or password')

     return render_template('admin_login.html')

# Doctor login page 
@app.route('/doctor/login',methods=['GET','POST'])
def doctor_login():
     if request.method=='POST':
          email=request.form['email']
          password=request.form['password']

          doctor=Doctor.query.filter_by(email=email).first()
          if doctor and doctor.check_password(password) and doctor.status=='Active':
               session['doctor_id']=doctor.id
               session['user_type']='doctor'
               flash('Login successfull!')
               return redirect(url_for('doctor_dashboard'))
          
          else:
               flash('Invalid email or password or Doctor is InActive')
     return render_template('doctor_login.html')


#patient registration
@app.route('/patient/register',methods=['GET','POST'])
def patient_register():
     if request.method=='POST':
          name=request.form['name']
          email=request.form['email']
          password=request.form['password']
          age=request.form['age']
          blood=request.form['blood']
          gender=request.form['gender']
          contact_info=request.form['contact_info']



          #check for the email format
          if '@' not in email:
               flash('Invalid email format')
               return redirect(url_for('patient_register'))

          #check for account existence
          existing_patient=Patient.query.filter_by(email=email).first()

          if existing_patient:
               flash("email already registered")
               return redirect(url_for('patient_register'))
          
          try:
               new_patient=Patient(name=name,email=email,age=age,blood=blood,gender=gender,contact_info=contact_info)

               new_patient.set_password(password)

               db.session.add(new_patient)
               db.session.commit()

               new_patient.pat_id=f'PAT_{new_patient.id:03d}'
               db.session.commit()
               flash('Registeration successful ! please login')
               return redirect(url_for('patient_login'))
          except Exception as e:
               db.session.rollback()
               flash(f'Registration error:{str(e)}')
               return redirect(url_for('patient_register'))
     return render_template('patient_register.html')


@app.route('/logout')
def logout():
     user_type=session.get('user_type')
     session.clear()
     flash('You have been logged out')

     if user_type=='admin':
          return redirect(url_for('admin_login'))
     elif user_type=='doctor':
          return redirect(url_for('doctor_login'))
     else:
          return redirect(url_for('patient_login'))
     

#patient login
@app.route('/patient/login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        patient = Patient.query.filter_by(email=email).first()

        if patient and patient.check_password(password):
            session['patient_id'] = patient.id
            session['user_type'] = 'patient'
            flash('Login successful!')
            return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid email or password')

    return render_template('patient_login.html')


'''------LOGIN LOGOUT AND REGISTER ROUTES ENDS HERE -----------'''

'''===============AN APi route================='''
@app.route('/api/doctors',methods=['GET'])
def get_doctor_api():
     doctors=Doctor.query.filter_by(status='Active').all()
     doctor_list = []
     for doc in doctors:
          doctor_data = {
               'id': doc.doc_id,
               'name': doc.name,
               'department': doc.dept_id,
               'specialization': doc.spec,
               'email': doc.email
          }
          doctor_list.append(doctor_data)
     return jsonify(doctor_list)   
'''------------------------ADMIN FEATURES starts--------------'''
@app.route('/ADMIN-HOME')
@admin_required
def admin_dashboard():
    total_doctors = Doctor.query.filter_by(status='Active').count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()

    # Separating upcoming and past appointments
    today = date.today()

    
    upcoming_appointments = db.session.query(Appointment, Doctor, Patient)\
        .join(Doctor, Appointment.doc_id == Doctor.doc_id)\
        .join(Patient, Appointment.pat_id == Patient.pat_id)\
        .filter(Appointment.date >= today)\
        .order_by(Appointment.date.asc(), Appointment.time.asc())\
        .all()

    past_appointments = db.session.query(Appointment, Doctor, Patient)\
        .join(Doctor, Appointment.doc_id == Doctor.doc_id)\
        .join(Patient, Appointment.pat_id == Patient.pat_id)\
        .filter(Appointment.date < today)\
        .order_by(Appointment.date.desc(), Appointment.time.desc())\
        .all()

    return render_template('admin_home.html',
                          total_doctors=total_doctors,
                          total_patients=total_patients,
                          total_appointments=total_appointments,
                          upcoming_appointments=upcoming_appointments,
                          past_appointments=past_appointments)



@app.route('/add_doctor', methods=['GET', 'POST'])
@admin_required
def add_doctor():
     departments=Department.query.all()
     if request.method=='POST':
          name=request.form['name']
          email=request.form['email']   #added the email
          password=request.form['password'] #added the password
          dept_id=request.form['dept_id']
          # status=request.form['status']
          spec=request.form['spec']

          #check for if the email already existed or not 

          existing_doc=Doctor.query.filter_by(email=email).first()

          if existing_doc:
               flash("email already registered")
               return redirect(url_for('add_doctor'))

          new_doctor=Doctor(name=name,dept_id=dept_id,email=email,spec=spec)

          new_doctor.set_password(password)
          db.session.add(new_doctor)
          db.session.commit()
          # creating the doc code

          new_doctor.doc_id=f'DOC_{new_doctor.id:03d}'
          db.session.commit()

          flash('Doctor added succesfully')
          # return redirect(url_for('list_doctors'))
     return render_template('add_doctor.html',departments=departments)

@app.route('/doctors')
@admin_required
def list_doctors():
     doctors = Doctor.query.all()
     departments=Department.query.all()
     return render_template('list_doctors2.html',doctors=doctors)
                            


@app.route('/delete/<int:id>')
@admin_required
def delete_doc(id):
     doctor_delete=Doctor.query.get_or_404(id)
     doctor_delete.status = "InActive"
     try:
          db.session.commit()
          return redirect('/doctors')
     except:
          return 'there was a problem deleting the doctor'
     
@app.route('/update/<int:id>',methods=['POST','GET'])
@admin_required
def update_doc(id):
     task=Doctor.query.get_or_404(id)
     departments=Department.query.all()
     if request.method=='POST':
          task.name=request.form['name']
          task.email=request.form['email']
          task.dept_id=request.form['dept_id']
          task.status=request.form['status']
          task.spec=request.form['spec']

          # existing_doc=Doctor.query.filter_by(email=task.email).first()

          # if existing_doc:
          #      flash("email already registered")
          #      return redirect(url_for('update_doc'))



          try:
               db.session.commit()
               return redirect('/doctors')
          except:
               return 'There was an error updating the doctor details: Email already registered'
     
     else:
          return render_template('update_doc.html',task=task,departments=departments)


@app.route('/add_patient', methods=['GET', 'POST'])
@admin_required
def add_patient():
     if request.method == 'POST':
          name = request.form['name']
          email=request.form['email'] #added email
          password=request.form['password'] #added at ver2
          contact_info = request.form['contact_info']
          age=request.form['age']
          blood=request.form['blood']
          gender=request.form['gender']


          existing_patient=Patient.query.filter_by(email=email).first()

          if existing_patient:
               flash("email already registered")
               return redirect(url_for('add_patient'))

          new_patient = Patient(name=name,email=email,contact_info=contact_info,age=age,blood=blood,gender=gender)

          new_patient.set_password(password)
          db.session.add(new_patient)
          db.session.commit()

          # creating the pat id
          new_patient.pat_id=f'PAT_{new_patient.id:03d}'
          db.session.commit()
          return redirect(url_for('list_patients'))
     return render_template('add_patient.html')

@app.route('/patients')
@admin_required
def list_patients():
    patients = Patient.query.all()
    return render_template('list_patients2.html', patients=patients)


# deleting the patient 

@app.route('/delete_pat/<int:id>')
@admin_required
def delete_pat(id):
     delete_patient=Patient.query.get_or_404(id) # basicaly it capture that task using its id if got then ok else give 404 
     try:
          db.session.delete(delete_patient)
          db.session.commit()
          return redirect('/patients')
     except:
          return 'there was a problem deleting the patient'

@app.route('/update_pat/<int:id>',methods=['POST','GET'])
@admin_required
def update_pat(id):
     task=Patient.query.get_or_404(id)
     if request.method=='POST':
          task.name = request.form['name']
          task.contact_info = request.form['contact_info']
          task.email=request.form['email']
          task.age=request.form['age']
          task.blood=request.form['blood']
          task.gender=request.form['gender']

          # existing_pat=Patient.query.filter_by(email=task.email).first()

          # if existing_pat:
          #      flash("email already registered")
          #      return redirect(url_for('update_pat'))

          try:
               db.session.commit()
               return redirect('/patients')
          except:
               return 'There was an error updating patient details email already registered'
          
     else:
          return render_template('update_pat.html',task=task)




@app.route('/add_department',methods=['GET','POST'])
@admin_required
def add_department():
     doctors=Doctor.query.all()
     if request.method=='POST':
          name=request.form['name']
          head=request.form['head']
          new_dept=Department(name=name,head=head)
          db.session.add(new_dept)
          db.session.commit()
          new_dept.dpt_id=f'DPT_{new_dept.id:03d}'
          db.session.commit()
          return redirect(url_for('list_departments'))
     return render_template('add_department.html',doctors=doctors)


@app.route('/departments')
@admin_required
def list_departments():
     departments=Department.query.all()
     return render_template('list_departements2.html',departments=departments)

@app.route('/update_dept/<int:id>',methods=['POST','GET'])
@admin_required
def update_dept(id):
     task=Department.query.get_or_404(id)
     doctors=Doctor.query.all()
     if request.method=='POST':
          task.name=request.form['name']
          task.head=request.form['head']

          try:
               db.session.commit()
               return redirect('/departments')
          except:
               return 'There was an error updating the department details'
     
     else:
          return render_template('update_dept.html',task=task,doctors=doctors)

@app.route('/delete_dept/<int:id>')
@admin_required
def delete_dept(id):
     task=Department.query.get_or_404(id) # basicaly it capture that task using its id if got then ok else give 404 
     try:
          db.session.delete(task)
          db.session.commit()
          return redirect('/departments')
     except:
          return 'there was a problem deleting the department'


@app.route('/Admin/view-patient-records/<int:id>')
@admin_required
def admin_view_records(id):

     patient=Patient.query.get(id)

     prescriptions = Prescription.query.filter_by(
               patient_id=patient.pat_id  # Use pat_id here
          ).all()

     return render_template('admin_list_patient_records.html',prescriptions=prescriptions,patient=patient)

@app.route('/admin/prescription/<int:id>')
@admin_required
def admin_view_prescription(id):
     prescription = Prescription.query.get_or_404(id)
     # patient = Patient.query.get(session['patient_id'])
     # doctor=Doctor.query.get(session['doctor_id'])

     doctor = Doctor.query.filter_by(doc_id=prescription.doctor_id).first()
     patient = Patient.query.filter_by(pat_id=prescription.patient_id).first()
     appointment = Appointment.query.get(prescription.appointment_id)
     
     return render_template('admin_view_prescription.html',
                              prescription=prescription,
                              doctor=doctor,
                              appointment=appointment,
                              patient=patient)




'''----- ADMIN FEATURES ENDS-------'''



'''----------PATIENT FEATURES STARTS--------'''
@app.route('/patient/dashboard')
@patient_required
def patient_dashboard():
     # Get current patient info
     patient = Patient.query.get(session['patient_id'])

     # Get all departments (specializations)
     departments = Department.query.all()

     return render_template('patient_dashboard.html',
                              patient=patient,
                              departments=departments)
@app.route('/patient/profile')
@patient_required
def patient_profile():
     patient=Patient.query.get(session['patient_id'])
     return render_template('patient_profile.html',patient=patient)

@app.route('/patient/edit_profile',methods=['POST','GET'])
@patient_required
def edit_patient_profile():
     patient=Patient.query.get(session['patient_id'])
     if request.method=='POST':
          patient.name=request.form['name']
          patient.contact_info=request.form['contact_info']
          patient.age=request.form['age']
          patient.blood=request.form['blood']
          patient
          patient.gender=request.form['gender']
          patient.contact_info=request.form['contact_info']

          try:
               db.session.commit()
               flash('Profile updated successfully')
               return redirect(url_for('patient_dashboard'))
          except:
               db.session.rollback()
               flash('Error updating profile. Please try again.')
               return redirect(url_for('edit_patient_profile'))
     return render_template('edit_patient_profile.html',patient=patient)

@app.route('/patient/doctors/<int:department_id>')
@patient_required
def view_doctors_by_specialty(department_id):
    
     department = Department.query.get_or_404(department_id)
     
     dept_id=department.dpt_id
     # Get all doctors with dept_id matching this department
     doctors = Doctor.query.filter_by(dept_id=dept_id,status="Active").all()

     # Get available time slots for each doctor (next 7 days)
     from datetime import date, timedelta
     today = date.today()
     next_7_days = today + timedelta(days=7)

     # Create availability map
     availability_map = {}
     for doctor in doctors:
          availabilities = DoctorAvailability.query.filter(
               DoctorAvailability.doctor_id == doctor.id,
               DoctorAvailability.date >= today,
               DoctorAvailability.date <= next_7_days,
               DoctorAvailability.is_available == True
          ).all()
          availability_map[doctor.id] = availabilities

     return render_template('doctors_by_specialty.html',
                              department=department,
                              doctors=doctors,
                              availability_map=availability_map)




'''----------PATIENT FEATURES ENDS--------'''

'''----------DOCTOR FEATURES STARTS--------'''
@app.route('/doctor/dashboard')
@doctor_required
def doctor_dashboard():
     doctor = Doctor.query.get(session['doctor_id'])

     # Get doctor's availability for next 7 days
     from datetime import date, timedelta
     today = date.today()
     next_7_days = today + timedelta(days=7)

     availabilities = DoctorAvailability.query.filter(
          DoctorAvailability.doctor_id == session['doctor_id'],
          DoctorAvailability.date >= today,
          DoctorAvailability.date <= next_7_days
     ).order_by(DoctorAvailability.date.asc()).all()

     return render_template('doctor_dashboard.html',
                              doctor=doctor,
                              availabilities=availabilities)

@app.route('/doctor/add_availability', methods=['GET', 'POST'])
@doctor_required
def add_availability():
     if request.method == 'POST':
          date_str = request.form['date']
          start_time = request.form['start_time']
          end_time = request.form['end_time']
          slot_duration = request.form.get('slot_duration', 30)

          # Validation
          if start_time >= end_time:
               flash('Start time must be before end time')
               return redirect(url_for('add_availability'))

          try:
               # Convert string to date object
               date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
               today = date.today()
               if date_obj < today:
                    flash('Cannot add availability for past dates. Please select today or a future date.')
                    return redirect(url_for('add_availability'))

               existing = DoctorAvailability.query.filter_by(doctor_id=session['doctor_id'],date=date_obj).first()

               if existing:
                    flash('You already have availability for this date. Please choose a different date.')
                    return redirect(url_for('add_availability'))
               

               availability = DoctorAvailability(
                    doctor_id=session['doctor_id'],
                    date=date_obj,  # ✅ Now it's a date object!
                    start_time=start_time,
                    end_time=end_time,
                    slot_duration=int(slot_duration)
               )

               db.session.add(availability)
               db.session.commit()

               flash('Availability added successfully!')
               return redirect(url_for('doctor_dashboard'))

          except ValueError as e:
               db.session.rollback()
               flash(f'Invalid date format. Please use YYYY-MM-DD: {str(e)}')
               return redirect(url_for('add_availability'))
          except Exception as e:
               db.session.rollback()
               flash(f'Error: {str(e)}')
               return redirect(url_for('add_availability'))

     return render_template('add_availability.html')


@app.route('/doctor/availability/<int:id>/toggle', methods=['POST'])
@doctor_required
def toggle_availability(id):
     availability = DoctorAvailability.query.get_or_404(id)

    # Check it's doctor's own availability
     if availability.doctor_id != session['doctor_id']:
          flash('Unauthorized')
          return redirect(url_for('doctor_dashboard'))

     availability.is_available = not availability.is_available

     try:
          db.session.commit()
          status = "enabled" if availability.is_available else "disabled"
          flash(f'Availability {status}')
          return redirect(url_for('doctor_dashboard'))   
     except:
          db.session.rollback()
          flash('Error updating availability')
          return redirect(url_for('doctor_dashboard'))
    


#doctor feature for viewing all the patients -working 
@app.route('/doctor/patients')
@doctor_required
def doctor_list_patients():
    doctor=Doctor.query.get(session['doctor_id'])
    patients = db.session.query(Patient)\
    .join(Prescription)\
    .filter(Prescription.doctor_id == doctor.doc_id)\
    .distinct()\
    .all()
    
    return render_template('list_patients_doctor.html', patients=patients)



# doctor view all the prescriptions a selected patient  -working
@app.route('/doctor/prescriptions/<int:id>')
@doctor_required
def doctor_view_patients_records(id):
     doctor=Doctor.query.get(session['doctor_id'])
     patient=Patient.query.get(id)


     prescriptions = Prescription.query.filter_by(
          doctor_id=doctor.doc_id, 
          patient_id=patient.pat_id  # Use pat_id here
     ).all()

     return render_template('doctor_prescriptions.html',doctor=doctor,prescriptions=prescriptions,patient=patient)

#doctor view prescirption
@app.route('/doctor/prescription/<int:id>')
@doctor_required
def doctor_view_prescription(id):
     prescription = Prescription.query.get_or_404(id)
     # patient = Patient.query.get(session['patient_id'])
     doctor=Doctor.query.get(session['doctor_id'])
     patient = Patient.query.filter_by(pat_id=prescription.patient_id).first()
     appointment = Appointment.query.get(prescription.appointment_id)
     

     
     if prescription.doctor_id != doctor.doc_id:
          flash('Unauthorized access')
          return redirect(url_for('doctor_appointments'))
     
    
     
     return render_template('doctor_view_prescription.html',
                              prescription=prescription,
                              doctor=doctor,
                              appointment=appointment,
                              patient=patient)


#updating the prescription
@app.route('/doctor/update-prescription/<int:id>', methods=['GET', 'POST'])
@doctor_required
def update_prescription(id):
     prescription = Prescription.query.get_or_404(id)
     task=Prescription.query.get_or_404(id)
     doctor = Doctor.query.get(session['doctor_id'])
     patient = Patient.query.filter_by(pat_id=prescription.patient_id).first()
     appointment = Appointment.query.get(prescription.appointment_id)
     
     if appointment.doc_id != doctor.doc_id:
          flash('Unauthorized action')
          return redirect(url_for('doctor_appointments'))
     
     
     if request.method == 'POST':
          task.diagnosis = request.form['diagnosis']
          task.medicines = request.form['medicines']
          task.dosage = request.form.get('dosage', '')
          task.instructions = request.form.get('instructions', '')
          task.notes = request.form.get('notes', '')
          
          
          try:
               db.session.commit()
               flash('Prescription updated successfully')
               return redirect(url_for('doctor_view_patients_records',id=patient.id))
          except:
               db.session.rollback()
               flash('Error updating prescription')

     return render_template('doctor_update_prescription.html', task=task,
                              appointment=appointment,
                              doctor=doctor,
                              patient=patient)



'''--------DOCTOR FEATURE ENDS HERE -------------------------'''





'''---APOINTMENT BOOKING ROUTES-------'''       
@app.route('/patient/book-appointment/<int:doctor_id>/<int:availability_id>', methods=['GET', 'POST'])
@patient_required
def book_appointment(doctor_id, availability_id):
     doctor = Doctor.query.get_or_404(doctor_id)
     availability = DoctorAvailability.query.get_or_404(availability_id)
     patient = Patient.query.get(session['patient_id'])
     
     # Verify availability belongs to this doctor
     if availability.doctor_id != doctor_id:
          flash('Invalid availability selection')
          return redirect(url_for('patient_dashboard'))
     
     # Check if availability is still available
     if not availability.is_available:
          flash('This time slot is no longer available')
          return redirect(url_for('view_doctors_by_specialty', department_id=doctor.dept_id))
     

     existing_patient_appointment = Appointment.query.filter_by(
          doc_id=doctor.doc_id,
          pat_id=patient.pat_id,
          date=availability.date
     ).filter(Appointment.status != 'Cancelled').first()
     
     if existing_patient_appointment:
          flash('You already have an appointment for this date,Book on another date')
          return redirect(url_for('patient_dashboard'))
     
     if request.method == 'POST':
          # ✅ NEW: Check if time_slot was provided in the form
          selected_time = request.form.get('time_slot')
          
          if not selected_time:
               flash('Please select a valid time slot.')
               return redirect(url_for('book_appointment', doctor_id=doctor_id, availability_id=availability_id))
          
          # ✅ Check if the selected time has already passed
          from datetime import datetime, timedelta
          selected_datetime = datetime.combine(availability.date, datetime.strptime(selected_time, '%H:%M').time())
          current_datetime = datetime.now()
          
          if selected_datetime < current_datetime:
               flash('This time slot has already passed. Please select a future time slot.')
               return redirect(url_for('book_appointment', doctor_id=doctor_id, availability_id=availability_id))
          
          # Check for existing appointments at this time
          existing = Appointment.query.filter_by(
               doc_id=doctor.doc_id,
               date=availability.date,
               time=selected_time).filter(
               Appointment.status != 'Cancelled'
               ).first()
          
          if existing:
               flash('This time slot has already been booked. Please select another.')
               return redirect(url_for('book_appointment', doctor_id=doctor_id, availability_id=availability_id))
          
          # Create new appointment
          new_appointment = Appointment(
               doc_id=doctor.doc_id,
               pat_id=patient.pat_id,
               date=availability.date,
               time=selected_time,
               status='Pending'
          )
          
          try:
               db.session.add(new_appointment)
               db.session.commit()
               flash('Appointment booked successfully!')
               return redirect(url_for('appointment_success', appointment_id=new_appointment.id))
          except Exception as e:
               db.session.rollback()
               flash(f'Error booking appointment: {str(e)}')
               return redirect(url_for('book_appointment', doctor_id=doctor_id, availability_id=availability_id))
     
     # Generate time slots
     from datetime import datetime, timedelta
     start = datetime.strptime(availability.start_time, '%H:%M')
     end = datetime.strptime(availability.end_time, '%H:%M')
     duration = timedelta(minutes=availability.slot_duration)
     
     time_slots = []
     current = start
     current_datetime = datetime.now()
     
     while current < end:
          time_str = current.strftime('%H:%M')
          
          # Combine date and time to check if slot has passed
          slot_datetime = datetime.combine(availability.date, current.time())
          is_past = slot_datetime < current_datetime
          
          # Check if slot is already booked
          is_booked = Appointment.query.filter_by(
               doc_id=doctor.doc_id,
               date=availability.date,
               time=time_str
          ).filter(Appointment.status!='Cancelled').first() is not None
          
          time_slots.append({
               'time': time_str,
               'is_booked': is_booked,
               'is_past': is_past
          })
          current += duration
     
     return render_template('book_appointment.html',
                              doctor=doctor,
                              availability=availability,
                              patient=patient,
                              time_slots=time_slots)


@app.route('/patient/appointment-success/<int:appointment_id>')
@patient_required
def appointment_success(appointment_id):
     appointment = Appointment.query.get_or_404(appointment_id)
     
     # Verify this appointment belongs to the logged-in patient
     patient = Patient.query.get(session['patient_id'])
     if appointment.pat_id != patient.pat_id:
          flash('Unauthorized access')
          return redirect(url_for('patient_dashboard'))
     
     # Get doctor details using STRING foreign key
     doctor = Doctor.query.filter_by(doc_id=appointment.doc_id).first()
     
     return render_template('appointment_success.html',
                              appointment=appointment,
                              doctor=doctor,
                              patient=patient)




# patient -My Appointment
@app.route('/patient/my-appointments')
@patient_required
def patient_appointments():
     patient=Patient.query.get(session['patient_id'])

     # get all the appointments 
     today=date.today()
     upcoming=db.session.query(Appointment,Doctor).join(Doctor,Appointment.doc_id==Doctor.doc_id).filter(Appointment.pat_id==patient.pat_id,Appointment.date>=today).order_by(Appointment.date.asc(),Appointment.time.asc()).all()

     past = db.session.query(Appointment, Doctor).join(
        Doctor, Appointment.doc_id == Doctor.doc_id).filter(
        Appointment.pat_id == patient.pat_id,
        Appointment.date < today).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
     return render_template('patient_appointments.html',
                          patient=patient,
                          upcoming_appointments=upcoming,
                          past_appointments=past)


#patient-cancel Appointment
@app.route('/patient/cancel-appointment/<int:appointment_id>', methods=['POST'])
@patient_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    patient = Patient.query.get(session['patient_id'])
    
    # Verify ownership
    if appointment.pat_id != patient.pat_id:
        flash('Unauthorized action')
        return redirect(url_for('patient_appointments'))
    
    # Check if appointment is in the future
    if appointment.date < date.today():
        flash('Cannot cancel past appointments')
        return redirect(url_for('patient_appointments'))
    
    # Check if already cancelled or completed
    if appointment.status in ['Cancelled', 'Completed']:
        flash(f'Cannot cancel {appointment.status.lower()} appointment')
        return redirect(url_for('patient_appointments'))
    
    # Cancel the appointment
    appointment.status = 'Cancelled'
    
    try:
        db.session.commit()
        flash('Appointment cancelled successfully')
    except:
        db.session.rollback()
        flash('Error cancelling appointment')
    
    return redirect(url_for('patient_appointments'))



# doctor - view appointments 
# Doctor - View Appointments
@app.route('/doctor/appointments')
@doctor_required
def doctor_appointments():
     doctor = Doctor.query.get(session['doctor_id'])
    
     today = date.today()
    
    # Get all appointments for this doctor
     upcoming = db.session.query(Appointment, Patient).join(
          Patient, Appointment.pat_id == Patient.pat_id
     ).filter(
          Appointment.doc_id == doctor.doc_id,
          Appointment.date >= today,
          Appointment.status != 'Cancelled'
     ).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    
     past = db.session.query(Appointment, Patient).join(
        Patient, Appointment.pat_id == Patient.pat_id
     ).filter(
          Appointment.doc_id == doctor.doc_id,
          Appointment.date < today
          ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    # Today's appointments
     today_appointments = db.session.query(Appointment, Patient).join(
        Patient, Appointment.pat_id == Patient.pat_id
     ).filter(
        Appointment.doc_id == doctor.doc_id,
        Appointment.date == today,
        Appointment.status != 'Cancelled'
     ).order_by(Appointment.time.asc()).all()
    
     return render_template('doctor_appointments.html',
                          doctor=doctor,
                          upcoming_appointments=upcoming,
                          past_appointments=past,
                          today_appointments=today_appointments)


#Doctor -mark appointment as compltete
@app.route('/doctor/appointment/<int:id>/complete',methods=['POST'])
@doctor_required
def complete_appointment(id):
     appointment=Appointment.query.get_or_404(id)
     doctor=Doctor.query.get(session['doctor_id'])

     #verify ownership
     if appointment.doc_id!=doctor.doc_id:
          flash('Unauthorized action')
          return redirect(url_for('doctor_appointments'))
     
     #update the status
     appointment.status='Completed'
     
     try:
          db.session.commit()
          flash('Appointment marked as completed')
     except:
          db.session.rollback()
          flash('Error updating appointmnet')
     
     return redirect(url_for('doctor_appointments'))



#doctor cancel the appointment
@app.route('/doctor/appointment/<int:id>/cancel',methods=['POST'])
@doctor_required
def doctor_cancel_appointment(id):
     appointment=Appointment.query.get_or_404(id)
     doctor=Doctor.query.get(session['doctor_id'])

     #verify ownership
     if appointment.doc_id!=doctor.doc_id:
          flash('Unauthorized action')
          return redirect(url_for('doctor_appointments'))
     
     #update the status
     appointment.status='Cancelled'
     
     try:
          db.session.commit()
          flash('Appointment marked as cancelled')
     except:
          db.session.rollback()
          flash('Error updating appointmnet')
     
     return redirect(url_for('doctor_appointments'))

#admin cancel the appointment
@app.route('/admin/cancel-appointment/<int:id>', methods=['POST'])
@admin_required
def admin_cancel_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    appointment.status = 'Cancelled'
    try:
        db.session.commit()
        flash('Appointment cancelled by admin')
    except:
        db.session.rollback()
        flash('Error cancelling appointment')
    return redirect(url_for('admin_dashboard'))





'''------appointment ROUTES ENDS HERE------------'''

'''------ precscription routes ends here ------------'''

@app.route('/doctor/appointment/<int:id>/add-prescription', methods=['GET', 'POST'])
@doctor_required
def add_prescription(id):
     appointment = Appointment.query.get_or_404(id)
     doctor = Doctor.query.get(session['doctor_id'])
     
     
     if appointment.doc_id != doctor.doc_id:
          flash('Unauthorized action')
          return redirect(url_for('doctor_appointments'))
     
     
     if appointment.status != 'Completed':
          flash('Prescription can only be added for completed appointments')
          return redirect(url_for('doctor_appointments'))
     
     
     existing = Prescription.query.filter_by(appointment_id=id).first()
     if existing:
          flash('Prescription already exists for this appointment')
          return redirect(url_for('doctor_appointments'))
     
     if request.method == 'POST':
          diagnosis = request.form['diagnosis']
          medicines = request.form['medicines']
          dosage = request.form.get('dosage', '')
          instructions = request.form.get('instructions', '')
          notes = request.form.get('notes', '')
          
          prescription = Prescription(
               appointment_id=id,
               doctor_id=appointment.doc_id,
               patient_id=appointment.pat_id,
               diagnosis=diagnosis,
               medicines=medicines,
               dosage=dosage,
               instructions=instructions,
               notes=notes,
               date=date.today()
          )
          
          try:
               db.session.add(prescription)
               db.session.commit()
               flash('Prescription added successfully')
               return redirect(url_for('doctor_appointments'))
          except:
               db.session.rollback()
               flash('Error adding prescription')
     
     # Get patient details
     patient = Patient.query.filter_by(pat_id=appointment.pat_id).first()
     
     return render_template('add_prescription.html',
                              appointment=appointment,
                              doctor=doctor,
                              patient=patient)




#all the prescriptions for the patient
@app.route('/patient/prescriptions')
@patient_required
def patient_prescriptions():
     patient=Patient.query.get(session['patient_id'])

     prescriptions=db.session.query(Prescription,Doctor,Appointment)\
     .join(Doctor,Prescription.doctor_id==Doctor.doc_id)\
     .join(Appointment,Prescription.appointment_id==Appointment.id)\
     .filter(Prescription.patient_id==patient.pat_id)\
     .order_by(Prescription.date.desc())\
     .all()

     return render_template('patient_prescriptions.html',patient=patient,prescriptions=prescriptions)


@app.route('/patient/prescription/<int:id>')
@patient_required
def view_prescription(id):
     prescription = Prescription.query.get_or_404(id)
     patient = Patient.query.get(session['patient_id'])
     
     # Verify ownership
     if prescription.patient_id != patient.pat_id:
          flash('Unauthorized access')
          return redirect(url_for('patient_prescriptions'))
     
     # Get related data
     doctor = Doctor.query.filter_by(doc_id=prescription.doctor_id).first()
     appointment = Appointment.query.get(prescription.appointment_id)
     
     return render_template('view_prescription.html',
                              prescription=prescription,
                              doctor=doctor,
                              appointment=appointment,
                              patient=patient)




@app.route('/Admin/prescriptions')
@admin_required
def admin_prescriptions():
     prescriptions=db.session.query(Prescription,Doctor,Patient)\
     .join(Doctor,Prescription.doctor_id==Doctor.doc_id)\
     .join(Patient,Prescription.patient_id==Patient.pat_id)\
     .order_by(Prescription.date.desc())\
     .all()

     return render_template('admin_prescriptions.html',prescriptions=prescriptions)


if __name__=='__main__':
     with app.app_context():
          db.create_all()

          #create the default admin

          admin=Admin.query.filter_by(username='admin').first()
          if not admin:
               default_admin=Admin(name='System Administrator',
                                   username='admin',
                                   email='admin@hospital.com')
               default_admin.set_password('admin123')
               db.session.add(default_admin)
               db.session.commit()
               print('Default admin created: username=admin,password=admin123')
     app.run(debug=True)
