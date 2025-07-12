# Student GPA Prediction System with Email Verification and Secure Authentication

## Overview

This project is a secure and intelligent web application built with **Flask** that predicts a student's GPA based on key academic inputs. It ensures strong authentication practices with email verification and password hashing for data protection.

## Features

- **GPA Prediction** using machine learning (trained Decision Tree Regressor).
- **Secure Sign-Up & Login** with password hashing using `werkzeug.security`.
- **Email Verification** via `smtplib` before account activation.
- **Session Management** to track logged-in users.
- **Show/Hide Password** toggle in login form for user convenience.
- **Error Handling** and informative flash messages.
- **Modern UI** with responsive design using **Tailwind CSS**.

## Tech Stack

- **Backend**: Flask, Python, scikit-learn, joblib
- **Frontend**: HTML, CSS, Tailwind CSS, Bootstrap (for email verification page)
- **Security**: smtplib (email), werkzeug.security (hashing), Flask sessions
- **Model**: Trained ML model (DecisionTreeRegressor) using student performance features



## How It Works

1. **Sign-Up**:
   - User enters their name, email, and password.
   - A 6-digit verification code is sent to their email via SMTP.
   - User must verify the code to proceed to login.

2. **Login**:
   - Email and password are validated.
   - Passwords are hashed during both storage and validation.
   - On success, user is redirected to the prediction page.

3. **Prediction**:
   - User fills in academic details.
   - A trained ML model predicts their GPA based on inputs.

## Security Highlights

- Passwords are never stored in plain text. They are hashed using Werkzeug's `generate_password_hash` and verified using `check_password_hash`.
- Email verification ensures that only legitimate users complete registration.
- User sessions are securely managed using Flask's session management.
- Form submissions are validated and protected with Flash messaging for user feedback.

## Requirements

Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt

```
## Requirenments Include

- flask
- scikit-learn
- joblib
- numpy
- werkzeug

