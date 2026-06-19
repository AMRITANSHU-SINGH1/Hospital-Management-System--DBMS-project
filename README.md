# Hospital_Management_System
MedSync: Digital Healthcare Ecosystem 🏥

##  Overview

MedSync is a full-stack, scalable digital healthcare management system designed to streamline the interactions between hospital administrators, doctors, and patients. Built with Python and Flask, this ecosystem manages the end-to-end software development life cycle (SDLC) of hospital operations, featuring a highly normalized relational database schema to maintain data integrity.

## 🌟 Key Technical Highlights

Role-Based Access Control (RBAC): Implemented custom Python decorators (@admin_required, @doctor_required, @patient_required) coupled with Flask sessions for secure route protection.

Normalized Database Architecture: Designed 8 interconnected SQLAlchemy models (Departments, Doctors, Patients, Appointments, Treatments, Prescriptions, Availability) with foreign key constraints to eliminate data redundancy.

Dynamic Time-Slot Generation: Engineered an algorithm using Python's datetime and timedelta to automatically generate, validate, and manage non-overlapping appointment slots based on doctor availability.

Security: Integrated werkzeug.security for robust password hashing (generate_password_hash, check_password_hash).

## 👥 System Roles & Features

#### 1. Administrator Module

Global Dashboard: Oversee total doctors, patients, and system-wide upcoming/past appointments.

Entity Management: Perform CRUD operations on Hospital Departments, Doctor profiles, and Patient records.

Record Oversight: Global access to view any patient's prescription history and appointment logs.

#### 2. Doctor Portal

Dynamic Scheduling: Add, update, and toggle daily availability slots and durations.

Appointment Management: View upcoming schedules, mark appointments as completed, or cancel them.

Clinical Records: Generate, update, and manage detailed prescriptions (diagnosis, medicines, dosages) linked directly to specific appointment IDs.

#### 3. Patient Dashboard

Secure Onboarding: Registration system with email validation and secure credential storage.

Smart Booking: Filter doctors by specialty and book dynamic time slots (prevents double-booking and past-date booking).

Medical History: Access past appointments and view detailed digital prescriptions.

## 🛠️ Tech Stack

Backend: Python, Flask

Database: SQLite (Configured via Flask-SQLAlchemy ORM for easy migration to PostgreSQL)

Frontend: HTML5, CSS3, Jinja2 Templating

Authentication: Flask Sessions, Werkzeug Security

## 🚀 Local Setup & Installation

Follow these steps to run the application locally:

#### 1. Clone the repository

git clone (https://github.com/AMRITANSHU-SINGH1/Hospital-Management-System--DBMS-project.git)


#### 2. Create and activate a virtual environment

##### Windows
python -m venv venv
venv\Scripts\activate

##### macOS/Linux
python3 -m venv venv
source venv/bin/activate


#### 3. Install dependencies

pip install Flask Flask-SQLAlchemy Werkzeug


#### 4. Run the application

python app.py


Note: The SQLite database (hospital.db) and all tables will be generated automatically on the first run.

#### 5. Default Admin Credentials
Upon initialization, the system automatically creates a master admin account:

Username: admin

Password: admin123

## 🔮 Future Enhancements

Database Migration: Transition from SQLite to PostgreSQL for enterprise-level scaling.

AI Integration: Implement a machine learning model to predict patient no-show probabilities based on historical appointment data.

REST API Expansion: Expand the /api/doctors endpoint into a full suite of headless REST APIs for mobile app integration.


