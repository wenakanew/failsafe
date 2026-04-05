import os
import csv
from flask import Blueprint, request, jsonify, abort
from peewee import IntegrityError, chunked

from app.models.user import User
from app.database import retry_db_operation, db
from playhouse.shortcuts import model_to_dict

users_bp = Blueprint("users_bp", __name__)

def paginate(query):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    data = request.get_json(silent=True, force=True) or request.form or {}
    page = data.get('page', page)
    per_page = data.get('per_page', per_page)
        
    total = query.count()
    items = query.paginate(int(page), int(per_page))
    return {
        "kind": "list",
        "sample": [model_to_dict(i) for i in items],
        "total_items": total
    }

@users_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json(silent=True, force=True) or request.form or {}
    if 'username' not in data or 'email' not in data:
        abort(400, description="Missing required fields: username, email")
        
    def save():
        return User.create(username=data['username'], email=data['email'])
        
    try:
        new_user = retry_db_operation(save)
        return jsonify(model_to_dict(new_user)), 201
    except IntegrityError:
        abort(400, description="User already exists")

@users_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify(paginate(User.select())), 200

@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.get_or_none(User.id == user_id)
    if not user:
        abort(404, description="User not found")
    return jsonify(model_to_dict(user)), 200

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.get_or_none(User.id == user_id)
    if not user:
        abort(404, description="User not found")
        
    data = request.get_json() or {}
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    user.save()
    return jsonify(model_to_dict(user)), 200

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.get_or_none(User.id == user_id)
    if not user:
        abort(404, description="User not found")
    user.delete_instance()
    return '', 204

@users_bp.route('/users/bulk', methods=['POST'])
def load_csv():
    data = request.get_json(silent=True, force=True) or request.form or {}
    filepath = data.get('file')
    if not filepath or not os.path.exists(filepath):
        abort(404, description="File not found")
        
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with db.atomic():
        for batch in chunked(rows, 100):
            User.insert_many(batch).on_conflict_ignore().execute()
            
    return jsonify({"status": "ok"}), 201
