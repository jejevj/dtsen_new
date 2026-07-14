def test_login_missing_fields(client):
    res = client.post('/api/v1/auth/login', json={})
    assert res.status_code == 400


def test_login_invalid_credentials(client):
    res = client.post('/api/v1/auth/login', json={'email': 'wrong@test.com', 'password': 'wrong'})
    assert res.status_code == 401
