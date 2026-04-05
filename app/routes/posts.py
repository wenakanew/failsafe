from flask import Blueprint, request, jsonify, abort

from app.models.user import User
from app.models.post import Post
from app.database import retry_db_operation

posts_bp = Blueprint("posts_bp", __name__)

@posts_bp.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    if not data or not all(k in data for k in ('user_id', 'content')):
        abort(400, description="Missing required fields: user_id, content")
        
    # Validation
    content = str(data['content']).strip()
    if len(content) == 0 or len(content) > 280:
        abort(400, description="Post content must be between 1 and 280 characters")

    # Referential Integrity Check
    user = User.get_or_none(User.id == data['user_id'])
    if not user:
        abort(404, description="User ID not found")

    def save_post():
        return Post.create(user=user, content=content)
        
    new_post = retry_db_operation(save_post)
    return jsonify({"id": new_post.id, "user_id": new_post.user.id, "content": new_post.content}), 201

@posts_bp.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.select()
    return jsonify([{"id": p.id, "user_id": p.user.id, "content": p.content, "created_at": p.created_at.isoformat()} for p in posts]), 200
