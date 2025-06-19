from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import db, User, OTP
from datetime import datetime, timedelta
import random
import string
import re

auth_bp = Blueprint('auth', __name__)

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('name'):
            return jsonify({'error': 'Email and name are required'}), 400
        
        email = data['email'].lower().strip()
        name = data['name'].strip()
        password = data.get('password', '')
        
        # Validate email format
        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Create new user
        password_hash = generate_password_hash(password) if password else None
        user = User(
            email=email,
            name=name,
            password_hash=password_hash
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].lower().strip()
        password = data.get('password', '')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check password if provided
        if user.password_hash and password:
            if not check_password_hash(user.password_hash, password):
                return jsonify({'error': 'Invalid password'}), 401
        elif user.password_hash and not password:
            return jsonify({'error': 'Password is required'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/google', methods=['POST'])
def google_auth():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('google_id'):
            return jsonify({'error': 'Email and Google ID are required'}), 400
        
        email = data['email'].lower().strip()
        google_id = data['google_id']
        name = data.get('name', email.split('@')[0])
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Update Google ID if not set
            if not user.google_id:
                user.google_id = google_id
            user.last_login = datetime.utcnow()
        else:
            # Create new user
            user = User(
                email=email,
                name=name,
                google_id=google_id
            )
            db.session.add(user)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Google authentication successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].lower().strip()
        
        # Validate email format
        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Generate OTP
        otp_code = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=10)  # OTP expires in 10 minutes
        
        # Save OTP to database
        otp = OTP(
            email=email,
            otp_code=otp_code,
            expires_at=expires_at
        )
        db.session.add(otp)
        db.session.commit()
        
        # In a real application, you would send the OTP via email
        # For demo purposes, we'll return it in the response
        return jsonify({
            'message': 'OTP sent successfully',
            'otp': otp_code,  # Remove this in production
            'expires_at': expires_at.isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('otp'):
            return jsonify({'error': 'Email and OTP are required'}), 400
        
        email = data['email'].lower().strip()
        otp_code = data['otp']
        
        # Find the most recent unused OTP for this email
        otp = OTP.query.filter_by(
            email=email,
            otp_code=otp_code,
            is_used=False
        ).order_by(OTP.created_at.desc()).first()
        
        if not otp:
            return jsonify({'error': 'Invalid OTP'}), 400
        
        if otp.is_expired():
            return jsonify({'error': 'OTP has expired'}), 400
        
        # Mark OTP as used
        otp.is_used = True
        db.session.commit()
        
        # Check if user exists, create if not
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                name=email.split('@')[0]  # Use email prefix as default name
            )
            db.session.add(user)
            db.session.commit()
        
        return jsonify({
            'message': 'OTP verified successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    # In a real application with JWT tokens, you would invalidate the token here
    return jsonify({'message': 'Logout successful'}), 200

