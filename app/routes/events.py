from flask import Blueprint, request, jsonify, abort
from app.models.event import Event
from app.models.url import Url
from app.models.user import User
from app.database import retry_db_operation
from playhouse.shortcuts import model_to_dict

events_bp = Blueprint("events_bp", __name__)

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
        "sample": [model_to_dict(i, max_depth=1) for i in items],
        "total_items": total
    }

@events_bp.route('/events', methods=['POST'])
def create_event():
    data = request.get_json(silent=True, force=True) or request.form or {}
    if 'event_type' not in data or 'url_id' not in data:
        abort(400, description="Missing required fields: event_type, url_id")
        
    url = Url.get_or_none(Url.id == data['url_id'])
    if not url:
        abort(404, description="URL ID not found")
        
    user = None
    if 'user_id' in data:
        user = User.get_or_none(User.id == data['user_id'])
        
    def save():
        return Event.create(url=url, user=user, event_type=data['event_type'], details=data.get('details'))
        
    new_e = retry_db_operation(save)
    return jsonify(model_to_dict(new_e, max_depth=1)), 201

@events_bp.route('/events', methods=['GET'])
def get_events():
    query = Event.select()
    data = request.get_json(silent=True, force=True) or request.form or {}
    
    uid = request.args.get('user_id') or data.get('user_id')
    if uid is not None:
        query = query.where(Event.user == uid)
        
    urlid = request.args.get('url_id') or data.get('url_id')
    if urlid is not None:
        query = query.where(Event.url == urlid)
        
    evtype = request.args.get('event_type') or data.get('event_type')
    if evtype is not None:
        query = query.where(Event.event_type == evtype)
        
    return jsonify(paginate(query)), 200
