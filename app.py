from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import json
from datetime import datetime

app = Flask(__name__)
# QUICK FIX: Hardcoded secret key for session management. Change this for production security!
app.secret_key = 'b7e2f8c1-4e2a-4c3e-9a1b-2f7e6d8c9a5f'
ADMIN_PASSWORD = 'Maddy@#13'
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
SUBMISSION_FILE = 'submissions.json'

# Load existing submissions
if os.path.exists(SUBMISSION_FILE):
    with open(SUBMISSION_FILE, 'r') as f:
        submissions = json.load(f)
else:
    submissions = []

# ALLOWED_EXTENSIONS = {'pdf', 'docx', 'png'}
# MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file(filename):
    return True  # Allow all file types

@app.route('/')
def user_dashboard():
    return render_template('user.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    file = request.files['document']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not file or not file.filename:
        flash('No file selected!')
        return redirect(url_for('user_dashboard'))

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        submissions.append({
            'name': name,
            'filename': file.filename,
            'timestamp': timestamp
        })

        with open(SUBMISSION_FILE, 'w') as f:
            json.dump(submissions, f)

    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Incorrect password!')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully!')
    return redirect(url_for('login'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    # Sort submissions by timestamp descending
    sorted_submissions = sorted(submissions, key=lambda x: x['timestamp'], reverse=True)
    return render_template('admin.html', submissions=sorted_submissions)

@app.route('/delete', methods=['POST'])
def delete_submission():
    filename = request.form.get('filename')
    timestamp = request.form.get('timestamp')
    global submissions
    submissions = [s for s in submissions if not (s['filename'] == filename and s['timestamp'] == timestamp)]
    with open(SUBMISSION_FILE, 'w') as f:
        json.dump(submissions, f)
    return redirect(url_for('admin_dashboard'))
