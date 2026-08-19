import pytest
from .models import OrgMember

@pytest.mark.organizations
def test_create_org(db, auth_client, user):
    res = auth_client.post('/api/organizations/',
                           data={
                               "org_name": "Neworg"
                           })

    assert res.status_code == 201
    
    orgmember = OrgMember.objects.get(user=user)
    assert orgmember is not None
    assert orgmember.role == "OWNER"

@pytest.mark.organizations
def test_index_org(db, auth_client, organization):
    res = auth_client.get(f'/api/organizations/')

    print(res.data)

@pytest.mark.organizations
def test_show_org_non_auth(db, api_client, organization):
    res = api_client.get(f'/api/organizations/Neworg/')

    assert res.status_code == 200


# Create your tests here.
