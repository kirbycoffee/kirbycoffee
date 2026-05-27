import os
import random
import smtplib
import ssl
from email.mime.text import MIMEText

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 為了方便你直接測試，我幫你加了一個預設的測試帳號
# 格式為 { "信箱": { "username": "用戶名", "password": "密碼" } }
users = {
    'test@gmail.com': {
        'username': '夢境觀測員',
        'password': 'password123'
    }
}
verification_codes = {}

# =======================================================
# 🔒 在這裡直接填入你的 GMAIL 帳號與 16 位應用程式密碼
# =======================================================
EMAIL_ADDRESS = '' 
EMAIL_APP_PASSWORD = '' # ⚠️ 注意：不能填一般密碼，要填 Google 申請的應用程式密碼
# =======================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify(success=False, message='Email and password are required'), 400

    user = users.get(email)
    if not user or user['password'] != password:
        return jsonify(success=False, message='Invalid email or password'), 401

    return jsonify(success=True, message='Login successful', user={'username': user['username'], 'email': email})

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    confirm_password = data.get('confirmPassword') or ''

    if not username or not email or not password or not confirm_password:
        return jsonify(success=False, message='All fields are required'), 400
    if password != confirm_password:
        return jsonify(success=False, message='Passwords do not match'), 400
    if email in users:
        return jsonify(success=False, message='Email already registered'), 409

    users[email] = {
        'username': username,
        'password': password,
    }
    return jsonify(success=True, message='Account created successfully')

@app.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()

    if not email:
        return jsonify(success=False, message='Email is required'), 400
    if email not in users:
        return jsonify(success=False, message='No account found for that email'), 404
        
    # 防止你忘記改範例帳密的安全檢查
    if EMAIL_ADDRESS == '你的帳號@gmail.com' or not EMAIL_APP_PASSWORD:
        return jsonify(success=False, message='Email service not configured. Please check app.py line 24.'), 500

    code = f"{random.randint(100000, 999999)}"
    verification_codes[email] = code

    subject = 'Subconscious Observation System 密碼重設驗證碼'
    body = (
        f'您好，\n\n請使用以下 6 位數驗證碼重設您的密碼：{code}\n\n'
        '如果您沒有提出重設請求，請忽略此郵件。'
    )

    try:
        message = MIMEText(body, _charset='utf-8')
        message['Subject'] = subject
        message['From'] = EMAIL_ADDRESS
        message['To'] = email

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
            smtp.sendmail(EMAIL_ADDRESS, email, message.as_string())
    except Exception as error:
        return jsonify(success=False, message=f'Email send failed: {error}'), 500

    return jsonify(success=True, message='Verification code sent')

@app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    code = (data.get('code') or '').strip()
    password = data.get('password') or ''

    if not email or not code or not password:
        return jsonify(success=False, message='Email, code, and new password are required'), 400
    if email not in users:
        return jsonify(success=False, message='No account found for that email'), 404
    expected_code = verification_codes.get(email)
    if expected_code != code:
        return jsonify(success=False, message='Invalid verification code'), 400

    users[email]['password'] = password
    verification_codes.pop(email, None)
    return jsonify(success=True, message='Password reset successfully')

if __name__ == '__main__':
    app.run(debug=True)