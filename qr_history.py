from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
import datetime

app = Flask(__name__)

# MongoDB connection settings
mongo_uri = 'mongodb://localhost:27017/'
db_name = 'test_db'

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client[db_name]

# Collection for users and qr_history
users_collection = db['users']
qr_history_collection = db['qr_history']

# Function to authenticate user (example)
def authenticate_user(email, password):
    user = users_collection.find_one({'email': email})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return user
    return None

# Example route to generate QR code
@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    if request.method == 'POST':
        # Parse form data
        qr_data = request.json.get('qr_data')
        fill_color = request.json.get('fill_color')
        background_color = request.json.get('background_color')
        error_correction = request.json.get('error_correction')
        border_width = request.json.get('border_width')
        box_size = request.json.get('box_size')

        # Example authentication (replace with your own)
        auth_user = authenticate_user('test@example.com', 'password')

        if auth_user:
            # Generate QR code logic (replace with your own)
            # Example: store QR code data into qr_history collection
            qr_record = {
                'user_id': auth_user['_id'],
                'qr_data': qr_data,
                'fill_color': fill_color,
                'background_color': background_color,
                'error_correction': error_correction,
                'border_width': border_width,
                'box_size': box_size,
                'timestamp': datetime.datetime.now()
            }
            qr_history_collection.insert_one(qr_record)
            
            return jsonify({'status': 'success', 'message': 'QR code generated successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Authentication failed'})

# Route to render QR code generator page with history
@app.route('/')
def index():
    # Example: Fetch QR history for authenticated user
    auth_user = authenticate_user('test@example.com', 'password')

    if auth_user:
        # Query QR history for the authenticated user
        user_qr_history = qr_history_collection.find({'user_id': auth_user['_id']})

        # Pass history data to template
        return render_template('index.html', history=user_qr_history)
    else:
        return jsonify({'status': 'error', 'message': 'Authentication failed'})

if __name__ == '__main__':
    app.run(debug=True)
