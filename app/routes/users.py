from flask import Blueprint, request, jsonify, abort
from email_validator import validate_email, EmailNotValidError
from peewee import IntegrityError

from app.models.user import User
from app.database import retry_db_operation

users_bp = Blueprint("users_bp", __name__)

@users_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or not all(k in data for k in ('name', 'email', 'age')):
        abort(400, description="Missing required fields: name, email, age")
    
    # 1. Validation
    try:
        validate_email(data['email'])
    except EmailNotValidError:
        abort(400, description="Invalid email format")
        
    if not isinstance(data['age'], int) or data['age'] < 13:
        abort(400, description="User must be at least 13 years old")

    # 2. Idempotency (Return existing if email matches)
    existing_user = User.get_or_none(User.email == data['email'])
    if existing_user:
        return jsonify({"id": existing_user.id, "name": existing_user.name, "email": existing_user.email, "message": "User already exists"}), 200

    # 3. Create with Retry Logic
    def save_user():
        return User.create(name=data['name'], email=data['email'], age=data['age'])
    
    try:
        new_user = retry_db_operation(save_user)
        return jsonify({"id": new_user.id, "name": new_user.name, "email": new_user.email}), 201
    except IntegrityError:
        abort(500, description="Database integrity error during user creation")

@users_bp.route('/users', methods=['GET'])
def get_users():
    users = User.select()
    return jsonify([{"id": u.id, "name": u.name, "email": u.email, "age": u.age} for u in users]), 200
