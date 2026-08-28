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
def test_create_org_non_auth(db, api_client, user):
    res = api_client.post('/api/organizations/',
                           data={
                               "org_name": "Neworg"
                           })

    assert res.status_code == 401

@pytest.mark.organizations
def test_index_org(db, auth_client, organization):
    res = auth_client.get(f'/api/organizations/')

    for i in res.data:
        assert i["org_name"] == "Neworg"

@pytest.mark.organizations
def test_show_org_non_auth(db, api_client, organization):
    res = api_client.get(f'/api/organizations/Neworg/')

    assert res.status_code == 200
    assert "Neworg" == res.data["org_name"]


@pytest.mark.organizations
def test_update_org(db, auth_client, organization):
    org_id, org_name = organization
    res = auth_client.patch(f'/api/organizations/{org_name}/',
                            data={"display_name": "joking"})

    assert res.status_code == 200
    assert res.data["display_name"] == "joking"

@pytest.mark.organizations
def test_update_org_non_owner(db, auth_client2, organization):
    org_id, org_name = organization
    res = auth_client2.patch(f'/api/organizations/{org_name}/',
                            data={"display_name": "joking"})

    assert res.status_code == 403

@pytest.mark.organizations
def test_update_org_non_auth(db, api_client, organization):
    org_id, org_name = organization
    res = api_client.patch(f'/api/organizations/{org_name}/',
                            data={"display_name": "joking"})

    assert res.status_code == 401

@pytest.mark.organizations
def test_delete_org(db, auth_client, organization):
    org_id, org_name = organization
    res = auth_client.delete(f'/api/organizations/{org_name}/')

    assert res.status_code == 204

@pytest.mark.organizations
def test_member_delete_org(db, org_member_user2, auth_client2, organization):
    org_id, org_name = organization
    res = auth_client2.delete(f'/api/organizations/{org_name}/')

    assert res.status_code == 403

@pytest.mark.organizations
def test_delete_org_non_auth(db, api_client, organization):
    org_id, org_name = organization
    res = api_client.delete(f'/api/organizations/{org_name}/')

    assert res.status_code == 401

@pytest.mark.organizations
def test_delete_org_non_member(db, auth_client2, organization):
    org_id, org_name = organization
    res = auth_client2.delete(f'/api/organizations/{org_name}/')

    assert res.status_code == 403

@pytest.mark.organizations
def test_invite_member(db, auth_client, organization, another_user):
    org_id, org_name = organization
    res = auth_client.post(f'/api/organizations/{org_name}/members/',
                           data={
                               "invitee": "another"
                           })

    assert res.status_code == 201

@pytest.mark.organizations
def test_invite_member_alr_pending(db, auth_client, organization, invite_org_to_user2, another_user):
    org_id, org_name = organization
    res = auth_client.post(f'/api/organizations/{org_name}/members/',
                           data={
                               "invitee": "another"
                           })

    assert res.status_code == 400

@pytest.mark.organizations
def test_invite_existing_member(db, auth_client, org_member_user2, organization):
    org_id, org_name = organization
    res = auth_client.post(f'/api/organizations/{org_name}/members/',
                           data={
                               "invitee": "another"
                           })

    assert res.status_code == 400

@pytest.mark.organizations
def test_invite_self(db, auth_client, organization):
    org_id, org_name = organization
    res = auth_client.post(f'/api/organizations/{org_name}/members/',
                           data={
                               "invitee": "testuser"
                           })

    assert res.status_code == 400

@pytest.mark.organizations
def test_non_owner_invite_member(db, auth_client2, organization, user):
    org_id, org_name = organization
    res = auth_client2.post(f'/api/organizations/{org_name}/members/',
                           data={
                               "invitee": "testuser"
                           })

    assert res.status_code == 403

@pytest.mark.organizations
def test_member_invite_member(db, organization, org_member_user2, auth_client2, another_user2):
    org_id, org_name = organization

    res = auth_client2.post(f'/api/organizations/{org_name}/members/',
                            data={
                                "invitee": "another2"
                            })

    assert res.status_code == 403

@pytest.mark.organizations
def test_owner_update_member(db, org_member_user2, auth_client, organization):
    org_id, org_name = organization
    member_id = org_member_user2
    res = auth_client.patch(f'/api/organizations/{org_name}/members/{member_id}/',
                           data={
                               "role": "OWNER",
                               "visibility": "PUBLIC"
                           })
    
    assert res.status_code == 200
    assert res.data["role"] == "OWNER"
    assert res.data["visibility"] == "PUBLIC"

@pytest.mark.organizations
def test_member_update_self_visibility(db, org_member_user2, auth_client2, organization):
    org_id, org_name = organization
    member_id = org_member_user2
    res = auth_client2.patch(f'/api/organizations/{org_name}/members/{member_id}/',
                           data={
                               "visibility": "PUBLIC"
                           })
    
    assert res.status_code == 200
    assert res.data["visibility"] == "PUBLIC"

@pytest.mark.organizations
def test_member_update_self_role(db, org_member_user2, auth_client2, organization):
    org_id, org_name = organization
    member_id = org_member_user2
    res = auth_client2.patch(f'/api/organizations/{org_name}/members/{member_id}/',
                           data={
                               "role": "OWNER"
                           })
    
    assert res.status_code == 403

@pytest.mark.organizations
def test_member_update_member(db, org_member_user2, org_member_user3, organization, auth_client3):
    org_id, org_name = organization
    member_id = org_member_user2
    res = auth_client3.patch(f'/api/organizations/{org_name}/members/{member_id}/',
                           data={
                               "role": "OWNER",
                               "visibility": "PUBLIC"
                           })
    
    assert res.status_code == 403

@pytest.mark.organizations
def test_update_member_non_auth(db, org_member_user2, api_client, organization):
    org_id, org_name = organization
    member_id = org_member_user2
    res = api_client.patch(f'/api/organizations/{org_name}/members/{member_id}/',
                           data={
                               "role": "OWNER",
                               "visibility": "PUBLIC"
                           })
    
    assert res.status_code == 401

@pytest.mark.organizations
def test_update_member_non_member(db, org_member_user2, auth_client3, organization):
    org_id, org_name = organization
    member_id = org_member_user2
    res = auth_client3.patch(f'/api/organizations/{org_name}/members/{member_id}/',
                           data={
                               "role": "OWNER",
                               "visibility": "PUBLIC"
                           })
    
    assert res.status_code == 403

@pytest.mark.organizations
def test_delete_member(db, org_member_user2, auth_client, organization):
    org_id, org_name = organization
    member_id = org_member_user2
    res = auth_client.delete(f'/api/organizations/{org_name}/members/{member_id}/')

    assert res.status_code == 204

@pytest.mark.organizations
def test_member_delete_member(db, org_member_user2, org_member_user3, auth_client3, organization):
    org_id, org_name = organization
    member_id = org_member_user2
    res = auth_client3.delete(f'/api/organizations/{org_name}/members/{member_id}/')

    assert res.status_code == 403

@pytest.mark.organizations
def test_delete_member_non_member(db, org_member_user2, auth_client3, organization):
    org_id, org_name = organization
    member_id = org_member_user2
    res = auth_client3.delete(f'/api/organizations/{org_name}/members/{member_id}/')

    assert res.status_code == 403

@pytest.mark.organizations
def test_delete_member_non_auth(db, org_member_user2, api_client, organization):
    org_id, org_name = organization
    member_id = org_member_user2
    res = api_client.delete(f'/api/organizations/{org_name}/members/{member_id}/')

    assert res.status_code == 401


@pytest.mark.organizations
def test_leave_org(db, organization, org_member_user2, auth_client2):
    org_id, org_name = organization
    res = auth_client2.post(f'/api/organizations/{org_name}/leave/')

    assert res.status_code == 204

@pytest.mark.organizations
def test_last_owner_leave_org(db, organization, auth_client):
    org_id, org_name = organization
    res = auth_client.post(f'/api/organizations/{org_name}/leave/')

    assert res.status_code == 403

@pytest.mark.organizations
def test_non_member_leave_org(db, organization, auth_client2):
    org_id, org_name = organization
    res = auth_client2.post(f'/api/organizations/{org_name}/leave/')

    assert res.status_code == 403

@pytest.mark.organizations
def test_non_auth_leave_org(db, organization, api_client):
    org_id, org_name = organization
    res = api_client.post(f'/api/organizations/{org_name}/leave/')

    assert res.status_code == 401



# Create your tests here.
