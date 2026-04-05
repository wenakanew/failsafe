import os
import pytest
from app import create_app
from app.database import db
from app.models.user import User
from app.models.url import Url
from app.models.event import Event

@pytest.fixture
def client():
    os.environ["TESTING"] = "1"
    app = create_app()
    app.config['TESTING'] = True
    
    with app.app_context():
        db.connect(reuse_if_open=True)
        db.create_tables([User, Url, Event])
    
    with app.test_client() as client:
        yield client
        
    with app.app_context():
        db.drop_tables([User, Url, Event])
        db.close()

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200

def test_user_crud(client):
    # Create
    res = client.post('/users', json={"username": "Alice", "email": "alice@test.com"})
    assert res.status_code == 201
    user_id = res.get_json()['id']
    
    # Get List
    res_list = client.get('/users')
    assert res_list.status_code == 200
    assert res_list.get_json()['total_items'] == 1
    
    # Get Single
    res_single = client.get(f'/users/{user_id}')
    assert res_single.status_code == 200
    assert res_single.get_json()['username'] == 'Alice'

    # Update
    res_update = client.put(f'/users/{user_id}', json={"username": "Alice2"})
    assert res_update.status_code == 200
    
    # Delete
    res_del = client.delete(f'/users/{user_id}')
    assert res_del.status_code == 204

def test_url_crud(client):
    user_res = client.post('/users', json={"username": "Bob", "email": "bob@test.com"})
    user_id = user_res.get_json()['id']
    
    res = client.post('/urls', json={"original_url": "https://google.com", "title": "Google", "user_id": user_id})
    assert res.status_code == 201
    url_id = res.get_json()['id']
    short_code = res.get_json()['short_code']
    assert len(short_code) > 0
    
    res_list = client.get('/urls')
    assert res_list.get_json()['total_items'] == 1
    
    res_user = client.get(f'/urls?user_id={user_id}')
    assert res_user.get_json()['total_items'] == 1
    
    res_upd = client.put(f'/urls/{url_id}', json={"is_active": False})
    assert res_upd.status_code == 200
    assert res_upd.get_json()['is_active'] == False
    
    res_del = client.delete(f'/urls/{url_id}')
    assert res_del.status_code == 204

def test_event_crud(client):
    u = client.post('/users', json={"username": "Ev", "email": "ev@test.com"}).get_json()
    url = client.post('/urls', json={"original_url": "http://g.com", "title": "G", "user_id": u['id']}).get_json()
    
    res = client.post('/events', json={"event_type": "click", "url_id": url['id'], "user_id": u['id']})
    assert res.status_code == 201
    
    res_list = client.get('/events')
    assert res_list.status_code == 200
    assert res_list.get_json()['total_items'] == 1
