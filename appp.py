from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import numpy as np
import joblib
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key

# Load the trained model
model = joblib.load('final_gpa_model.pkl')

# Hashing function
def hash_data(data):
    return hashlib.sha256(data.encode()).hexdigest()

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Hash the email and password
        hashed_email = hash_data(email)
        hashed_password = hash_data(password)

        # Store the user data in users.txt
        with open('users.txt', 'a') as file:
            file.write(f"{name},{hashed_email},{hashed_password}\n")

        flash("Registration successful! Please sign in.", "success")
        return redirect(url_for('signin'))

    return render_template('register.html')

# Modify the signin route to set authenticated status
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

# Update the logout route to clear authenticated status
@app.route('/logout')
def logout():
    # Clear the session
    session.pop('email', None)
    session.pop('authenticated', None)
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('signin'))

# Add authentication check to index route
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

# Route for the sign-in page
@app.route('/signin')
def signin_get():
    return render_template('signin.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)