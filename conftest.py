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
    client = APIClient()
    client.force_authenticate(user=another_user)
    return client