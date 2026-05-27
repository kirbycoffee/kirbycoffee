from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = 'replace-with-a-strong-secret-key'

# In-memory store for demo purposes. Replace with a database in production.
users = {}
verification_codes = {}

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify(success=False, message='All fields are required.')

    if email in users:
        return jsonify(success=False, message='An account with this email already exists.')

    users[email] = {
        'username': username,
        'email': email,
        'password': password,
        'created_at': datetime.utcnow().isoformat(),
    }

    return jsonify(success=True, message='Account created successfully.')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    user = users.get(email)

    if not user or user['password'] != password:
        return jsonify(success=False, message='Invalid email or password.')

    session['user_email'] = email
    return jsonify(success=True, username=user['username'], email=user['email'])

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_email', None)
    return jsonify(success=True)

@app.route('/api/password/send-code', methods=['POST'])
def send_verification_code():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if email not in users:
        return jsonify(success=False, message='No account found for that email.')

    code = f"{random.randint(0, 999999):06d}"
    verification_codes[email] = {
        'code': code,
        'expires_at': datetime.utcnow() + timedelta(minutes=15)
    }

    # In a real system, send the code via email here.
    print(f"[DEBUG] Verification code for {email}: {code}")

    return jsonify(success=True, message='Verification code sent.')

@app.route('/api/password/reset', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    code = data.get('code', '').strip()
    new_password = data.get('newPassword', '')

    if email not in users:
        return jsonify(success=False, message='Account not found.')

    record = verification_codes.get(email)
    if not record or record['code'] != code:
        return jsonify(success=False, message='Invalid verification code.')
    if datetime.utcnow() > record['expires_at']:
        return jsonify(success=False, message='Verification code has expired.')
    if not new_password or len(new_password) < 6:
        return jsonify(success=False, message='New password must be at least 6 characters.')

    users[email]['password'] = new_password
    verification_codes.pop(email, None)
    return jsonify(success=True, message='Password updated successfully.')

@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    user_email = session.get('user_email')
    if not user_email or user_email not in users:
        return jsonify(success=False, message='Unauthorized'), 401

    user = users[user_email]
    return jsonify(
        success=True,
        username=user['username'],
        features=['Canvas & AI Dream Room', 'Subconscious Data Chart', 'Time Capsule'],
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
