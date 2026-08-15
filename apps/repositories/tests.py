import pytest


@pytest.mark.repositories
def test_repo_create(db, auth_client):
    res = auth_client.post('/api/repositories/',
                           data={
                               "name": "newrepo",
                               "description": "ddd",
                           })

    assert res.status_code == 201

@pytest.mark.repositories
def test_repo_create_failure(db, auth_client):
    res = auth_client.post('/api/repositories/',
                           data={
                               "name": "newrepo",
                               "description": "ddd",
                           })

    res = auth_client.post('/api/repositories/',
                           data={
                               "name": "newrepo",
                               "description": "aaa",
                           })

    assert res.status_code == 400

@pytest.mark.repositories
def test_repo_create_same_name_diff_users(db, auth_client, auth_client2):
    res = auth_client.post('/api/repositories/',
                        data={
                            "name": "newrepo",
                            "description": "ddd",
                        })

    assert res.status_code == 201

    res = auth_client2.post('/api/repositories/',
                           data={
                               "name": "newrepo",
                               "description": "aaa",
                           })

    assert res.status_code == 201

@pytest.mark.repositories
def test_repo_index_not_authenticated(db, api_client):
    res = api_client.get('/api/repositories/')

    assert res.status_code == 200

@pytest.mark.repositories
def test_repo_index_filter_private_for_non_author(db, private_repo, repo, auth_client2):
    res = auth_client2.get('/api/repositories/')
    for i in res.data:
        assert i["visibility"] == "PUBLIC"

@pytest.mark.repositories
def test_repo_index_not_filter_priv_for_author(db, private_repo, auth_client):
    res = auth_client.get('/api/repositories/')

    assert res.data[0]["visibility"] == "PRIVATE"

@pytest.mark.repositories
def test_repo_show_non_authenticated(db, api_client, repo):
    repo_id = repo.data["id"]
    res = api_client.get(f'/api/repositories/{repo_id}/')

    assert res.status_code == 200

@pytest.mark.repositories
def test_private_repo_show_non_author(db, private_repo, api_client):
    repo_id = private_repo.data["id"]
    res = api_client.get(f'/api/repositories/{repo_id}/')

    assert res.status_code == 403

@pytest.mark.repositories
def test_private_repo_show_author(db, private_repo, auth_client):
    repo_id = private_repo.data["id"]
    res = auth_client.get(f'/api/repositories/{repo_id}/')

    assert res.status_code == 200

@pytest.mark.repositories
def test_repo_update_success(db, repo, auth_client):
    repo_id = repo.data["id"]
    res = auth_client.patch(f'/api/repositories/{repo_id}/',
                            data={
                                "description": "newdescription",
                            })

    assert res.status_code == 200
    assert res.data["description"] == "newdescription"
    
@pytest.mark.repositories
def test_repo_update_failure(db, repo, auth_client2):
    repo_id = repo.data["id"]
    res = auth_client2.patch(f'/api/repositories/{repo_id}/',
                        data={
                            "description": "newdescription",
                        })

    assert res.status_code == 403

@pytest.mark.repositories
def test_repo_update_unauth_user(db, repo, api_client):
    repo_id = repo.data["id"]
    res = api_client.patch(f'/api/repositories/{repo_id}/',
                            data={
                                "description": "newdescription",
                            })

    assert res.status_code == 401

@pytest.mark.repositories
def test_priv_repo_update_success(db, private_repo, auth_client):
    repo_id = private_repo.data["id"]
    res = auth_client.patch(f'/api/repositories/{repo_id}/',
                            data={
                                "description": "newdescription",
                            })

    assert res.status_code == 200
    assert res.data["description"] == "newdescription"
    
@pytest.mark.repositories
def test_priv_repo_update_failure(db, private_repo, auth_client2):
    repo_id = private_repo.data["id"]
    res = auth_client2.patch(f'/api/repositories/{repo_id}/',
                        data={
                            "description": "newdescription",
                        })

    assert res.status_code == 403

@pytest.mark.repositories
def test_repo_delete(db, auth_client, repo):
    repo_id = repo.data["id"]
    res = auth_client.delete(f'/api/repositories/{repo_id}/')

    assert res.status_code == 204

@pytest.mark.repositories
def test_repo_delete_failure(db, auth_client2, repo):
    repo_id = repo.data["id"]
    res = auth_client2.delete(f'/api/repositories/{repo_id}/')
    
    assert res.status_code == 403

@pytest.mark.repositories
def test_repo_delete_unauth_user(db, api_client, repo):
    repo_id = repo.data["id"]
    res = api_client.delete(f'/api/repositories/{repo_id}/')
    
    assert res.status_code == 401

@pytest.mark.repositories
def test_priv_repo_delete(db, auth_client, private_repo):
    repo_id = private_repo.data["id"]
    res = auth_client.delete(f'/api/repositories/{repo_id}/')

    assert res.status_code == 204

@pytest.mark.repositories
def test_priv_repo_delete_failure(db, auth_client2, private_repo):
    repo_id = private_repo.data["id"]
    res = auth_client2.delete(f'/api/repositories/{repo_id}/')
    
    assert res.status_code == 403

@pytest.mark.repositories
def test_star_repo(db, auth_client2, repo):
    repo_id = repo.data["id"]
    res = auth_client2.post(f'/api/repositories/{repo_id}/stars/')

    assert res.status_code == 201

@pytest.mark.repositories
def test_star_repo_already_starred(db, auth_client2, repo):
    repo_id = repo.data["id"]
    res = auth_client2.post(f'/api/repositories/{repo_id}/stars/')

    res2 = auth_client2.post(f'/api/repositories/{repo_id}/stars/')
    assert res2.status_code == 409

@pytest.mark.repositories
def test_star_remove_success(db, auth_client2, repo):
    repo_id = repo.data["id"]
    res = auth_client2.post(f'/api/repositories/{repo_id}/stars/')

    res2 = auth_client2.delete(f'/api/repositories/{repo_id}/stars/')
    assert res2.status_code == 200

@pytest.mark.repositories
def test_star_remove_not_starred(db, auth_client2, repo):
    repo_id = repo.data["id"]

    res = auth_client2.delete(f'/api/repositories/{repo_id}/stars/')
    assert res.status_code == 409

@pytest.mark.repositories
def test_non_owner_star_private_repo(db, auth_client2, private_repo):
    repo_id = private_repo.data["id"]
    res = auth_client2.post(f'/api/repositories/{repo_id}/stars/')

    assert res.status_code == 403

@pytest.mark.repositories
def test_owner_star_private_repo(db, auth_client, private_repo):
    repo_id = private_repo.data["id"]
    res = auth_client.post(f'/api/repositories/{repo_id}/stars/')

    assert res.status_code == 201

@pytest.mark.repositories
def test_unauth_user_star_repo(db, api_client, private_repo):
    repo_id = private_repo.data["id"]
    res = api_client.post(f'/api/repositories/{repo_id}/stars/')

    assert res.status_code == 401

@pytest.mark.collaborators
def test_invite_collaborator(db, auth_client, repo, another_user):
    repo_id = repo.data["id"]
    res = auth_client.post(f'/api/repositories/{repo_id}/collaborators/',
                           data={
                               "invitee": "another"
                           })

    assert res.status_code == 201

@pytest.mark.collaborators
def test_non_repo_owner_invite_collaborator(db, auth_client2, repo, user):
    repo_id = repo.data["id"]
    res = auth_client2.post(f'/api/repositories/{repo_id}/collaborators/',
                            data={
                                "invitee": "testuser",
                            })
    assert res.status_code == 403

@pytest.mark.collaborators
def test_accept_invite(db, auth_client2, invite_user_to_user2):
    inv_id = invite_user_to_user2

    res = auth_client2.post(f'/api/invitations/{inv_id}/accept/')
    assert res.status_code == 200

@pytest.mark.collaborators
def test_non_invitee_accept_invite(db, invite_user_to_user2, auth_client3):
    inv_id = invite_user_to_user2

    res = auth_client3.post(f'/api/invitations/{inv_id}/accept/')
    assert res.status_code == 404

@pytest.mark.collaborators
def test_invite_already_collaborator(db, collaborator, auth_client, repo):
    repo_id = repo.data["id"]

    res = auth_client.post(f'/api/repositories/{repo_id}/collaborators/',
                           data={
                               "invitee": "anotheruser",
                           })

    assert res.status_code == 400

@pytest.mark.collaborators
def test_invite_alr_pending(db, invite_user_to_user2, auth_client, repo):
    repo_id = repo.data["id"]
    res = auth_client.post(f'/api/repositories/{repo_id}/collaborators/',
                           data={
                               "invitee": "another"
                           })

    assert res.status_code == 400

@pytest.mark.collaborators
def test_reinvite_declined_invite(db, invite_user_to_user2, auth_client, auth_client2, repo):
    inv_id = invite_user_to_user2
    repo_id = repo.data["id"]

    res = auth_client2.post(f'/api/invitations/{inv_id}/decline/')

    
    res = auth_client.post(f'/api/repositories/{repo_id}/collaborators/',
                            data={
                                "invitee": "another"
                            })
    assert res.status_code == 201

@pytest.mark.collaborators
def test():
    pass

    
# Create your tests here.
