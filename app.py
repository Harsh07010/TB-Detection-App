from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import pickle
import numpy as np
import joblib
import pandas as pd
from PIL import Image
import tensorflow as tf

app = Flask(__name__)
app.secret_key = 'your_secret_key'

conn = sqlite3.connect('users.db')
conn.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)''')
conn.close()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = sqlite3.connect('users.db')
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Username already exists"
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect('/symptoms')
        else:
            return "Invalid login"
    return render_template('login.html')

# Load the model when the app starts
symptom_model = joblib.load('models/final_text_model.pkl')

@app.route('/symptoms', methods=['GET', 'POST'])
def symptoms():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        # Collect form responses into a dictionary
        data = dict(request.form)
        print("Symptom data:", data)

         # Convert 'yes'/'no' to 1/0 for model input
        model_input = {key: 1 if value.lower() == 'yes' else 0 for key, value in data.items()}
        print("Model input (numeric):", model_input)

        # Create DataFrame for prediction
        input_df = pd.DataFrame([model_input])

        # Make prediction using the model
        prediction = symptom_model.predict(input_df)[0]
        print("Model prediction:", prediction)

        if prediction == 1:  # Assuming 1 means 'yes' or high risk
            return redirect('/xray')
        else:
            return render_template('result.html', result="Low risk. But consult doctor if symptoms persist.")
    
    return render_template('symptoms.html')


# Load the model when the app starts
resnet_model = joblib.load('models/resnet_model.pkl')

@app.route('/xray', methods=['GET', 'POST'])
def xray():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        if 'xray_image' not in request.files:
            return render_template('result.html', result="No file uploaded.")
        
        file = request.files['xray_image']
        if file.filename == '':
            return render_template('result.html', result="No selected file.")

        try:
            # Load image from file in memory (no saving)
            image = Image.open(file.stream).convert('RGB')
            image = image.resize((224, 224))
            image_array = np.array(image) / 255.0  # Normalize
            image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension

            # Predict
            prediction = resnet_model.predict(image_array)[0][0]
            print("Prediction:", prediction)

            if prediction > 0.5:
                return render_template('result.html', result="X-ray suggests possible TB. Please consult a doctor.")
            else:
                return render_template('result.html', result="Low risk. But consult doctor if symptoms persist.")
        except Exception as e:
            return render_template('result.html', result=f"Prediction failed: {e}")

    return render_template('xray.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
