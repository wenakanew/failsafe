import os
import pytest
from app import create_app
from app.database import db
from app.models.user import User
from app.models.post import Post

@pytest.fixture
def client():
    os.environ["TESTING"] = "1"
    app = create_app()
    app.config['TESTING'] = True
    
    with app.app_context():
        db.connect(reuse_if_open=True)
        db.create_tables([User, Post])
    
    with app.test_client() as client:
        yield client
        
    with app.app_context():
        db.drop_tables([User, Post])
        db.close()

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'healthy'

def test_create_user_success(client):
    res = client.post('/users', json={"name": "Alice", "email": "alice@test.com", "age": 22})
    assert res.status_code == 201

def test_create_user_idempotency(client):
    client.post('/users', json={"name": "Bob", "email": "bob@test.com", "age": 25})
    res2 = client.post('/users', json={"name": "Bob Duplicate", "email": "bob@test.com", "age": 25})
    assert res2.status_code == 200
    assert "User already exists" in res2.get_json()['message']

def test_invalid_age(client):
    res = client.post('/users', json={"name": "Timmy", "email": "timmy@test.com", "age": 10})
    assert res.status_code == 400

def test_create_post_success(client):
    user_res = client.post('/users', json={"name": "Alice", "email": "alice2@test.com", "age": 22})
    user_id = user_res.get_json()['id']
    
    post_res = client.post('/posts', json={"user_id": user_id, "content": "Hello World!"})
    assert post_res.status_code == 201

def test_create_post_invalid_user(client):
    post_res = client.post('/posts', json={"user_id": 999, "content": "Ghost post"})
    assert post_res.status_code == 404

def test_create_post_missing_fields(client):
    post_res = client.post('/posts', json={"content": "Forgot user"})
    assert post_res.status_code == 400

def test_get_users(client):
    client.post('/users', json={"name": "Z", "email": "z@z.com", "age": 25})
    res = client.get('/users')
    assert res.status_code == 200
    assert len(res.get_json()) > 0

def test_get_posts(client):
    user_res = client.post('/users', json={"name": "Y", "email": "y@y.com", "age": 25})
    user_id = user_res.get_json()['id']
    client.post('/posts', json={"user_id": user_id, "content": "Hello"})
    res = client.get('/posts')
    assert res.status_code == 200
    assert len(res.get_json()) > 0

def test_not_found_handler(client):
    res = client.get('/random/path/not/exist')
    assert res.status_code == 404
