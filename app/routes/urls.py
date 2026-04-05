import uuid
from flask import Blueprint, request, jsonify, abort
from app.models.url import Url
from app.models.user import User
from app.database import retry_db_operation
from playhouse.shortcuts import model_to_dict

urls_bp = Blueprint("urls_bp", __name__)

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
        "sample": [model_to_dict(i, exclude=[Url.user.email]) for i in items],
        "total_items": total
    }

@urls_bp.route('/urls', methods=['POST'])
def create_url():
    data = request.get_json(silent=True, force=True) or request.form or {}
    if 'original_url' not in data or 'title' not in data or 'user_id' not in data:
        abort(400, description="Missing required fields: original_url, title, user_id")
        
    user = User.get_or_none(User.id == data['user_id'])
    if not user:
        abort(404, description="User ID not found")
        
    code = str(uuid.uuid4())[:8]
        
    def save():
        return Url.create(user=user, original_url=data['original_url'], title=data['title'], short_code=code)
        
    new_url = retry_db_operation(save)
    return jsonify(model_to_dict(new_url)), 201

@urls_bp.route('/urls', methods=['GET'])
def get_urls():
    query = Url.select()
    data = request.get_json(silent=True, force=True) or request.form or {}
    
    uid = request.args.get('user_id') or data.get('user_id')
    if uid is not None:
        query = query.where(Url.user == uid)
        
    active = request.args.get('is_active') or data.get('is_active')
    if active is not None:
        act = False if str(active).lower() == 'false' else True
        query = query.where(Url.is_active == act)
        
    return jsonify(paginate(query)), 200

@urls_bp.route('/urls/<int:url_id>', methods=['GET'])
def get_url(url_id):
    url = Url.get_or_none(Url.id == url_id)
    if not url:
        abort(404, description="URL not found")
    return jsonify(model_to_dict(url)), 200

@urls_bp.route('/urls/<int:url_id>', methods=['PUT'])
def update_url(url_id):
    url = Url.get_or_none(Url.id == url_id)
    if not url:
        abort(404, description="URL not found")
        
    data = request.get_json() or {}
    if 'title' in data:
        url.title = data['title']
    if 'is_active' in data:
        url.is_active = data['is_active']
    url.save()
    return jsonify(model_to_dict(url)), 200

@urls_bp.route('/urls/<int:url_id>', methods=['DELETE'])
def delete_url(url_id):
    url = Url.get_or_none(Url.id == url_id)
    if not url:
        abort(404, description="URL not found")
    url.delete_instance()
    return '', 204

@urls_bp.route('/<short_code>', methods=['GET'])
def redirect_to_url(short_code):
    from app.models.event import Event
    url = Url.get_or_none(Url.short_code == short_code)
    if not url or not url.is_active:
        abort(404, description="URL not found or inactive")
        
    try:
        from app.database import db
        with db.atomic():
            Event.create(url=url, event_type="click")
    except Exception:
        pass # Ignore failure to log event, but keep redirecting
        
    from flask import redirect
    return redirect(url.original_url)
