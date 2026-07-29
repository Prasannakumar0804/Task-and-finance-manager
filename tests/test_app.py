import pytest
from app import create_app
from models import db

@pytest.fixture
def client():
    app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })

    with app.test_client() as client:
        yield client
        with app.app_context():
            db.drop_all()

def test_register(client):
    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    assert response.status_code == 201
    assert response.get_json()['message'] == 'User registered successfully'

def test_register_duplicate_username(client):
    client.post('/register', json={'username': 'testuser', 'password': 'testpass123'})
    response = client.post('/register', json={'username': 'testuser', 'password': 'anotherpass'})
    assert response.status_code == 409

def test_login_success(client):
    client.post('/register', json={'username': 'testuser', 'password': 'testpass123'})
    response = client.post('/login', json={'username': 'testuser', 'password': 'testpass123'})
    assert response.status_code == 200
    assert 'access_token' in response.get_json()

def test_login_wrong_password(client):
    client.post('/register', json={'username': 'testuser', 'password': 'testpass123'})
    response = client.post('/login', json={'username': 'testuser', 'password': 'wrongpass'})
    assert response.status_code == 401

def test_create_task_requires_auth(client):
    response = client.post('/tasks', json={'title': 'Test task'})
    assert response.status_code == 401

def test_create_and_get_task(client):
    client.post('/register', json={'username': 'testuser', 'password': 'testpass123'})
    login_response = client.post('/login', json={'username': 'testuser', 'password': 'testpass123'})
    token = login_response.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    create_response = client.post('/tasks', json={'title': 'Test task', 'description': 'A task'}, headers=headers)
    assert create_response.status_code == 201

    get_response = client.get('/tasks', headers=headers)
    assert get_response.status_code == 200
    tasks = get_response.get_json()
    assert len(tasks) == 1
    assert tasks[0]['title'] == 'Test task'

def test_update_task(client):
    client.post('/register', json={'username': 'testuser', 'password': 'testpass123'})
    login_response = client.post('/login', json={'username': 'testuser', 'password': 'testpass123'})
    token = login_response.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    create_response = client.post('/tasks', json={'title': 'Test task'}, headers=headers)
    task_id = create_response.get_json()['id']

    update_response = client.put(f'/tasks/{task_id}', json={'completed': True}, headers=headers)
    assert update_response.status_code == 200

def test_delete_task(client):
    client.post('/register', json={'username': 'testuser', 'password': 'testpass123'})
    login_response = client.post('/login', json={'username': 'testuser', 'password': 'testpass123'})
    token = login_response.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    create_response = client.post('/tasks', json={'title': 'Test task'}, headers=headers)
    task_id = create_response.get_json()['id']

    delete_response = client.delete(f'/tasks/{task_id}', headers=headers)
    assert delete_response.status_code == 200

    get_response = client.get('/tasks', headers=headers)
    assert len(get_response.get_json()) == 0

def _get_auth_headers(client):
    client.post('/register', json={'username': 'testuser', 'password': 'testpass123'})
    login_response = client.post('/login', json={'username': 'testuser', 'password': 'testpass123'})
    token = login_response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_create_transaction(client):
    headers = _get_auth_headers(client)
    response = client.post('/transactions', json={
        'amount': 500,
        'type': 'expense',
        'category': 'food',
        'description': 'Groceries'
    }, headers=headers)
    assert response.status_code == 201
    assert 'id' in response.get_json()

def test_create_transaction_missing_fields(client):
    headers = _get_auth_headers(client)
    response = client.post('/transactions', json={'amount': 500}, headers=headers)
    assert response.status_code == 400

def test_create_transaction_invalid_type(client):
    headers = _get_auth_headers(client)
    response = client.post('/transactions', json={
        'amount': 500,
        'type': 'invalid',
        'category': 'food'
    }, headers=headers)
    assert response.status_code == 400

def test_get_transactions(client):
    headers = _get_auth_headers(client)
    client.post('/transactions', json={
        'amount': 500, 'type': 'expense', 'category': 'food'
    }, headers=headers)

    response = client.get('/transactions', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['amount'] == 500

def test_update_transaction(client):
    headers = _get_auth_headers(client)
    create_response = client.post('/transactions', json={
        'amount': 500, 'type': 'expense', 'category': 'food'
    }, headers=headers)
    transaction_id = create_response.get_json()['id']

    update_response = client.put(f'/transactions/{transaction_id}', json={
        'amount': 700
    }, headers=headers)
    assert update_response.status_code == 200

def test_delete_transaction(client):
    headers = _get_auth_headers(client)
    create_response = client.post('/transactions', json={
        'amount': 500, 'type': 'expense', 'category': 'food'
    }, headers=headers)
    transaction_id = create_response.get_json()['id']

    delete_response = client.delete(f'/transactions/{transaction_id}', headers=headers)
    assert delete_response.status_code == 200

def test_dashboard(client):
    headers = _get_auth_headers(client)
    client.post('/transactions', json={
        'amount': 20000, 'type': 'income', 'category': 'salary'
    }, headers=headers)
    client.post('/transactions', json={
        'amount': 500, 'type': 'expense', 'category': 'food'
    }, headers=headers)

    response = client.get('/dashboard', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['total_income'] == 20000
    assert data['total_expenses'] == 500
    assert data['savings'] == 19500
    assert data['category_breakdown']['food'] == 500

def test_reset_password(client):
    client.post('/register', json={'username': 'testuser', 'password': 'oldpass'})
    response = client.post('/reset-password', json={
        'username': 'testuser',
        'new_password': 'newpass123'
    })
    assert response.status_code == 200

    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'newpass123'
    })
    assert login_response.status_code == 200

def test_logout(client):
    headers = _get_auth_headers(client)
    response = client.post('/logout', headers=headers)
    assert response.status_code == 200