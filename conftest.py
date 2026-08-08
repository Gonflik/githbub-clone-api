import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    client = APIClient()
    client.default_format = "json"
    return client

@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", email="testemail@gmail.com", password="testpass")

@pytest.fixture
def another_user(db):
    return User.objects.create_user(username="another", email="another@gmail.com", password="testpass")

@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def auth_client2(another_user):
    client2 = APIClient()
    client2.force_authenticate(user=another_user)
    return client2

@pytest.fixture
def repo(auth_client):
    res = auth_client.post('/api/repositories/',
                               data={
                                   "name": "newrepo",
                                   "description": "ddd",
                                   "visibility": "PUBLIC"
                               })
    return res

@pytest.fixture
def private_repo(auth_client):
    res = auth_client.post('/api/repositories/',
                               data={
                                   "name": "privaterepotypebeat",
                                   "description": "ddd",
                                   "visibility": "PRIVATE",
                               })
    return res

@pytest.fixture
def issue(repo, auth_client):
    repo_id = repo.data['id']

    res = auth_client.post(f'/api/repositories/{repo_id}/issues/',
                           data={
                               "title": "someissue",
                               "description": "issue on public repo",
                           })
    return (res, repo_id)

@pytest.fixture
def issue_on_private(private_repo, auth_client):
    repo_id = private_repo.data['id']

    res = auth_client.post(f'/api/repositories/{repo_id}/issues/',
                           data={
                               "title": "someissue",
                               "description": "issue on public repo",
                           })
    return (res, repo_id)

@pytest.fixture
def issue_user2(repo, auth_client2):
    repo_id = repo.data['id']

    res = auth_client2.post(f'/api/repositories/{repo_id}/issues/',
                           data={
                               "title": "someissue",
                               "description": "issue on public repo",
                           })
    return (res, repo_id)

