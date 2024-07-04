from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
import segno
import base64
import os
import datetime

app = Flask(__name__)
app.secret_key = 'CSIR'  # Your secret key

# Configure MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['test_db']

# Path to save the QR code image
QR_CODE_PATH = '/Users/avanimehrotra/Library/Mobile Documents/com~apple~CloudDocs/Desktop/SUBJECTS/QRcode/qr_code.png'

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if the email exists
        user = db.users.find_one({'email': email, 'password': password})
        
        if user:
            session['user_id'] = str(user['_id'])
            session['user_email'] = user['email']
            return redirect(url_for('qr_code'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/qr_code')
def qr_code():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('index.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    try:
        data = request.get_json()

        qr_data = data['qr_data']
        fill_color = data['fill_color']
        background_color = data['background_color']
        error_correction = data['error_correction']
        border_width = int(data['border_width'])
        box_size = int(data['box_size'])

        error_correction_levels = {
            'L': 'L',
            'M': 'M',
            'Q': 'Q',
            'H': 'H',
        }

        qr = segno.make_qr(qr_data, error=error_correction_levels[error_correction])

        # Ensure the directory exists
        os.makedirs(os.path.dirname(QR_CODE_PATH), exist_ok=True)

        # Save the QR code to the specified path
        qr.save(QR_CODE_PATH, scale=box_size, border=border_width, dark=fill_color, light=background_color)
        
        with open(QR_CODE_PATH, "rb") as image_file:
            img_str = base64.b64encode(image_file.read()).decode("utf-8")

        # Save QR code generation event to the database
        user_id = session['user_id']
        user_email = session['user_email']
        qr_event = {
            'user_id': user_id,
            'user_email': user_email,
            'qr_data': qr_data,
            'fill_color': fill_color,
            'background_color': background_color,
            'error_correction': error_correction,
            'border_width': border_width,
            'box_size': box_size,
            'generated_at': datetime.datetime.now(),
            'img_data': f"data:image/png;base64,{img_str}"
        }
        db.qr_code_history.insert_one(qr_event)

        return jsonify({"img_data": f"data:image/png;base64,{img_str}"})
    
    except Exception as e:
        app.logger.error("Error generating QR code", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    qr_code_history = db.qr_code_history.find({'user_id': user_id})
    return render_template('history.html', history=qr_code_history)

@app.route('/admin')
def admin():
    qr_code_history = db.qr_code_history.find()
    return render_template('admin.html', history=qr_code_history)

if __name__ == '__main__':
    app.run(debug=True)
