import os
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from flask_session import Session
from email_validator import validate_email, EmailNotValidError
import random
import smtplib
import joblib
import numpy as np
from dotenv import load_dotenv
import hashlib
from email.message import EmailMessage

app = Flask(__name__)
# app.secret_key = "your_secret_key"

# Ensure users.txt exists
if not os.path.exists('users.txt'):
    open('users.txt', 'w').close()

# Load the trained GPA prediction model
model = joblib.load('models/final_gpa_model.pkl')

@app.route('/')
def home():
    return redirect(url_for('signup'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Hash user details
        hashed_name = hash_data(name)
        hashed_email = hash_data(email)
        hashed_password = hash_data(password)
        
        # Check if email already exists
        with open('users.txt', 'r') as file:
            users = file.readlines()
            for user in users:
                if not user.strip():
                    continue
                stored_name, stored_email, stored_password = user.strip().split(',')
                if email == stored_email:
                    flash("This email is already in use. Please use a different email.", "danger")
                    return redirect(url_for('signup'))

        # Save the user data to users.txt
        with open('users.txt', 'a') as file:
            file.write(f"{hashed_name},{hashed_email},{hashed_password}\n")
        
        try:
            validate_email(email)
            session['email'] = email
            session['code'] = str(random.randint(100000, 999999))
            
            # Send the code via email
            send_email(email, session['code'])
            return redirect(url_for('verify_code'))
        except EmailNotValidError as e:
            flash(str(e), 'error')

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('signin'))

    return render_template('email_input.html')


# Function to hash data
def hash_data(data):
    return hashlib.sha256(data.encode()).hexdigest()

# Helper Function: Send Email

def send_email(email, code):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    smtp_server = os.environ.get("SMTP_SERVER")
    port = 587

    try:
        # Create the email
        msg = EmailMessage()
        msg["Subject"] = "Verify Your Email"
        msg["From"] = f"Multi Factor Authentication <{sender_email}>"
        msg["To"] = email

        msg.set_content(f"""Hi {request.form.get('name')}!
        You Recently Tried to Sign Up on GPA Predictor.
        Your verification code is: {code}.
        You can use this code to get your email verified

        Your Account Credentials are:
        Email: {email}
        Password: {request.form.get('password')}

        Note: Kindly save these credentials for future use. You won't be able to login if you lost/forgotten your password.""")

        # Send the email
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"Verification code sent to {email}")
    except Exception as e:
        print("Error sending email:", e)


# Route: Verify Code
@app.route('/verify', methods=['GET', 'POST'])
def verify_code():
    if request.method == 'POST':
        user_code = request.form.get('code')
        if user_code == session.get('code'):
            session.pop('code', None)  # Clear the code after successful verification
            return redirect(url_for('signin'))
        else:
            flash('Invalid code. Please try again.', 'error')
    return render_template('verify_code.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Hash the provided email and password
        hashed_email = hash_data(email)
        hashed_password = hash_data(password)

        # Check the credentials in users.txt
        with open('users.txt', 'r') as file:
            users = file.readlines()
            for user in users:
                if not user.strip():
                    continue
                stored_name, stored_email, stored_password = user.strip().split(',')
                # Compare hashed email and hashed password
                if hashed_email == stored_email and hashed_password == stored_password:
                    session['email'] = email  # Save email in session for user tracking
                    session['authenticated'] = True  # Set authentication status
                    flash("Login successful!", "success")
                    return redirect(url_for('index'))

        flash("Incorrect email or password. Please try again.", "danger")
        return redirect(url_for('signin'))

    return render_template('signin.html')

# Add logout route
@app.route('/logout')
def logout():
    # Clear the session
    session.pop('email', None)
    session.pop('authenticated', None)
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('signin'))

@app.route('/index', methods=['GET', 'POST'])
def index():
    # Check if user is authenticated
    if not session.get('authenticated'):
        flash("Please sign in to access this page.", "danger")
        return redirect(url_for('signin'))
        
    predicted_gpa = None  # Default value for GPA
    if request.method == 'POST':
        try:
            # Retrieve form data
            attendance = float(request.form['attendance'])
            study_hours = float(request.form['study-hours'])
            previous_cgpa = float(request.form['previous-cgpa'])
            quizzes_performance = float(request.form['quizzes-performance'])
            class_participation = float(request.form['class-participation'])

            print(f"Form data received: Attendance={attendance}, Study Hours={study_hours}, "
                  f"Previous CGPA={previous_cgpa}, Quizzes Performance={quizzes_performance}, "
                  f"Class Participation={class_participation}")

            # Prepare data for prediction
            features = np.array([[attendance, study_hours, previous_cgpa, quizzes_performance, class_participation]])
            prediction = model.predict(features)
            predicted_gpa = np.clip(prediction[0], 0, 4)  # Clip GPA between 0 and 4
            predicted_gpa = round(predicted_gpa, 2)  # Round to 2 decimal places
            print(f"Predicted GPA: {round(predicted_gpa, 2)}")
        except Exception as e:
            flash(f"Error during prediction: {e}", "danger")
            print(f"Error occurred: {e}")

    # Pass predicted GPA to template
    return render_template('index.html', predicted_gpa=predicted_gpa)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)