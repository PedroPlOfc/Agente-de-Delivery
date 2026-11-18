from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def test_admin_panel_is_served():
    response = client.get('/admin')
    assert response.status_code == 200
    assert 'CANA Admin' in response.text
    assert 'movement-form' in response.text
    assert 'products-table' in response.text


def test_admin_login_proxy(monkeypatch):
    monkeypatch.setattr(main, 'admin_login', lambda username, password: {
        'token': 'demo-token', 'user': {'username': username, 'nome': 'Nicolas', 'papel': 'ADMIN'}
    })
    response = client.post('/admin/api/login', json={'username': 'nicolas', 'password': '123'})
    assert response.status_code == 200
    assert response.json()['token'] == 'demo-token'


def test_admin_proxy_forwards_bearer_token(monkeypatch):
    calls = {}

    def fake_admin_call(method, path, token, *, params=None, payload=None):
        calls.update(method=method, path=path, token=token, params=params, payload=payload)
        return {'total_produtos': 30}

    monkeypatch.setattr(main, 'admin_call', fake_admin_call)
    response = client.get('/admin/api/dashboard', headers={'Authorization': 'Bearer demo-token'})
    assert response.status_code == 200
    assert response.json()['total_produtos'] == 30
    assert calls['token'] == 'demo-token'
    assert calls['path'] == '/api/admin/dashboard'


def test_admin_proxy_requires_login():
    response = client.get('/admin/api/dashboard')
    assert response.status_code == 401
