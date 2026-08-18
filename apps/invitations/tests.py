import pytest

@pytest.mark.invitations
def test_accept_invite(db, auth_client2, invite_user_to_user2):
    inv_id = invite_user_to_user2

    res = auth_client2.post(f'/api/invitations/{inv_id}/accept/')
    assert res.status_code == 200

@pytest.mark.invitations
def test_decline_invite(db, auth_client2, invite_user_to_user2):
    inv_id = invite_user_to_user2

    res = auth_client2.post(f'/api/invitations/{inv_id}/decline/')
    assert res.status_code == 200

@pytest.mark.invitations
def test_non_invitee_decline_invite(db, auth_client3, invite_user_to_user2):
    inv_id = invite_user_to_user2

    res = auth_client3.post(f'/api/invitations/{inv_id}/decline/')
    assert res.status_code == 404

@pytest.mark.invitations
def test_non_invitee_accept_invite(db, invite_user_to_user2, auth_client3):
    inv_id = invite_user_to_user2

    res = auth_client3.post(f'/api/invitations/{inv_id}/accept/')
    assert res.status_code == 404

@pytest.mark.invitations
def test_accept_already_accepted_invite(db, collaborator, repo, auth_client2):
    collaborator_id, inv_id = collaborator

    res = auth_client2.post(f'/api/invitations/{inv_id}/accept/')
    assert res.status_code == 400

@pytest.mark.invitations
def test_decline_already_declined_invite(db, auth_client, repo, auth_client2, invite_user_to_user2):
    inv_id = invite_user_to_user2

    res = auth_client2.post(f'/api/invitations/{inv_id}/decline/')


    res = auth_client2.post(f'/api/invitations/{inv_id}/decline/')
    assert res.status_code == 400

@pytest.mark.invitations
def test_accept_already_declined_invite(db, auth_client, repo, auth_client2, invite_user_to_user2):
    inv_id = invite_user_to_user2

    res = auth_client2.post(f'/api/invitations/{inv_id}/decline/')


    res = auth_client2.post(f'/api/invitations/{inv_id}/accept/')
    assert res.status_code == 400

@pytest.mark.invitations
def test_reinvite_declined_invite(db, invite_user_to_user2, auth_client, auth_client2, repo):
    inv_id = invite_user_to_user2
    repo_id = repo.data["id"]

    res = auth_client2.post(f'/api/invitations/{inv_id}/decline/')

    
    res = auth_client.post(f'/api/repositories/{repo_id}/collaborators/',
                            data={
                                "invitee": "another"
                            })
    assert res.status_code == 201

@pytest.mark.invitations
def test_list_invites(db, invite_user_to_user2, auth_client2):
    res = auth_client2.get('/api/invitations/')

    assert res.status_code == 200
    assert len(res.data) == 1

@pytest.mark.invitations
def test_list_invites_zero(db, auth_client2):
    res = auth_client2.get('/api/invitations/')

    assert res.status_code == 200
    assert len(res.data) == 0

# Create your tests here.
