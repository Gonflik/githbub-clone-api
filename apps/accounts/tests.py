import pytest

@pytest.mark.accounts
def test_user_register(db, api_client):
    res = api_client.post('/api/auth/register/', data={"username": "aboba652", 
                                                       "email": "abobus652@gmail.com", 
                                                       "password": "testpassword", 
                                                       "password2": "testpassword"}
                                                        )

    assert res.status_code == 201

@pytest.mark.accounts
def test_user_register_failure(db, api_client):
    res = api_client.post('/api/auth/register/', data={"username": "aboba652", 
                                                        "email": "abobus652", 
                                                        "password": "testpassword", 
                                                        "password2": "testnot"}
                                                        )
    
    assert res.status_code == 400

@pytest.mark.accounts
def test_user_login(db, api_client, user):
    res = api_client.post('/api/auth/login/',
                          data={
                              "email": "testemail@gmail.com",
                              "password": "testpass"
                          }) 

    assert res.status_code == 200
    assert res.data["message"] == "Logged in!"
    assert res.data["tokens"] is not None

@pytest.mark.accounts
def test_user_login_failure(db, api_client, user):
    res = api_client.post('/api/auth/login/',
                              data={
                                  "email": "testemail@gmail.com",
                                  "password": "nottestpass"
                              }) 
    
    assert res.status_code == 401

@pytest.mark.accounts
def test_user_me_profile(db, auth_client):
    res = auth_client.get('/api/users/me/')

    assert res.status_code == 200
    for i in ["username", "email", "bio"]:
        assert i in res.data.keys()

@pytest.mark.accounts
def test_user_me_update(db, auth_client):
    res = auth_client.patch('/api/users/me/',
                            data={
                                "bio": "im just testing",
                            })
    assert res.status_code == 200
    assert res.data["bio"] == "im just testing"

@pytest.mark.accounts
def test_user_me_update_failure(db, auth_client, auth_client2):
    res = auth_client.patch('/api/users/me/',
                            data={
                                "username": "another"
                            })
    assert res.status_code == 400

@pytest.mark.accounts
def test_user_me_unauthenticated(db, api_client):
    res = api_client.get('/api/users/me/')

    assert res.status_code == 401

@pytest.mark.accounts
def test_user_public_profile(db, auth_client, api_client):
    res = api_client.get('/api/users/testuser/')
    assert res.status_code == 200
    assert "username" in res.data.keys()

    res2 = auth_client.get('/api/users/testuser/')
    assert res2.status_code == 200
    assert "username" in res2.data.keys()

@pytest.mark.accounts
def test_user_public_profile_cant_update(db, auth_client):
    res = auth_client.patch('/api/users/testuser/',
                            data={
                                "bio": "newbio"
                            })
    assert res.status_code == 405

@pytest.mark.accounts
def test_user_public_profile_not_found(db, auth_client):
    res = auth_client.get('/api/users/nobody/')

    assert res.status_code == 404

@pytest.mark.accounts
def test_user_logout(db, api_client, user):
    res = api_client.post('/api/auth/login/',
                          data={
                              "email": "testemail@gmail.com",
                              "password": "testpass"
                          })

    refresh_token = res.data["tokens"]["refresh"]

    api_client.force_authenticate(user=user)
    res2 = api_client.post('/api/auth/logout/',
                            data={
                                "refresh": refresh_token
                            })
    assert res2.status_code == 200

@pytest.mark.accounts
def test_user_logout_invalid_token(db, api_client, user):
    res = api_client.post('/api/auth/logout/',
                          data={
                              "refresh": "gamnotoken"
                          })

    assert res.status_code == 401


# Create your tests here.
