def test_index(client):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

def test_register_and_login(client, app):
    # Test register
    response = client.post(
        '/auth/register',
        data={'username': 'test_user', 'password': 'test_password'}
    )
    assert response.status_code == 302
    
    # Test login
    response = client.post(
        '/auth/login',
        data={'username': 'test_user', 'password': 'test_password'}
    )
    assert response.status_code == 302
    
    with client:
        client.get('/')
        assert b"test_user" in response.data
