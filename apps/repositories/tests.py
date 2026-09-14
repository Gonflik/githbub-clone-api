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
    for i in res.data["results"]:
        assert i["visibility"] == "PUBLIC"

@pytest.mark.repositories
def test_repo_index_not_filter_priv_for_author(db, private_repo, auth_client):
    res = auth_client.get('/api/repositories/')

    assert res.data["results"][0]["visibility"] == "PRIVATE"

@pytest.mark.repositories
def test_repo_show_non_authenticated(db, api_client, repo):
    repo_id = repo.data["id"]
    res = api_client.get(f'/api/repositories/{repo_id}/')

    assert res.status_code == 200

@pytest.mark.repositories
def test_private_repo_show_non_author(db, private_repo, auth_client2):
    repo_id = private_repo.data["id"]
    res = auth_client2.get(f'/api/repositories/{repo_id}/')

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
def test_remove_collaborator(db, collaborator, auth_client, repo):
    col_id, inv_id = collaborator
    res = auth_client.delete(f'/api/repositories/{repo.data["id"]}/collaborators/{col_id}/')

    assert res.status_code == 204

@pytest.mark.collaborators
def test_non_owner_remove_collaborator(db, collaborator, auth_client3, repo):
    col_id = collaborator
    res = auth_client3.delete(f'/api/repositories/{repo.data["id"]}/collaborators/{col_id}/')

    assert res.status_code == 403

@pytest.mark.collaborators
def test_owner_list_collaborators(db, collaborator, auth_client, repo):
    col_id = collaborator
    res = auth_client.get(f'/api/repositories/{repo.data["id"]}/collaborators/')

    assert res.status_code == 200
    assert len(res.data) == 1

@pytest.mark.collaborators
def test_collaborator_list_collaborators(db, collaborator, auth_client2, repo):
    col_id = collaborator
    res = auth_client2.get(f'/api/repositories/{repo.data["id"]}/collaborators/')

    assert res.status_code == 403

@pytest.mark.collaborators
def test_non_owner_list_collaborators(db, collaborator, auth_client3, repo):
    col_id = collaborator
    res = auth_client3.get(f'/api/repositories/{repo.data["id"]}/collaborators/')

    assert res.status_code == 403

@pytest.mark.collaborators
def test_invite_self(db, auth_client, repo):
    repo_id = repo.data["id"]
    res = auth_client.post(f'/api/repositories/{repo_id}/collaborators/',
                           data={
                               "invitee": "testuser"
                           })

    assert res.status_code == 400

@pytest.mark.repositories
def test_transfer_ownership(db, repo, auth_client, another_user, user):
    from apps.repositories.models import Collaborator, Repository
    repo_id = repo.data["id"]

    res = auth_client.post(f'/api/repositories/{repo_id}/transfer/',
                           data={"user": "another"})

    assert res.status_code == 200

    assert Collaborator.objects.filter(user=user).exists() == True
    assert Repository.objects.get(pk=repo_id).user == another_user
    

@pytest.mark.repositories
def test_non_owner_transfer_ownership(db, repo, auth_client2):
    repo_id = repo.data["id"]

    res = auth_client2.post(f'/api/repositories/{repo_id}/transfer/',
                           data={"user": "another"})

    assert res.status_code == 403

@pytest.mark.repositories
def test_transfer_ownership_to_non_exist_user(db, repo, auth_client):
    repo_id = repo.data["id"]

    res = auth_client.post(f'/api/repositories/{repo_id}/transfer/',
                           data={"user": "anotherblabla"})

    assert res.status_code == 404



@pytest.mark.repositories
def test_transfer_ownership_to_org(db, repo, auth_client, organization):
    repo_id = repo.data["id"]

    res = auth_client.post(f'/api/repositories/{repo_id}/transfer/',
                           data={"organization": "Neworg"})

    assert res.status_code == 200

@pytest.mark.repositories
def test_transfer_ownership_to_non_exist_org(db, repo, auth_client):
    repo_id = repo.data["id"]

    res = auth_client.post(f'/api/repositories/{repo_id}/transfer/',
                           data={"organization": "Bibiorg"})

    assert res.status_code == 404

@pytest.mark.repositories
def test_transfer_ownership_to_both(db, repo, auth_client, organization, another_user):
    repo_id = repo.data["id"]

    res = auth_client.post(f'/api/repositories/{repo_id}/transfer/',
                           data={"organization": "Neworg",
                                 "user": "another"})

    assert res.status_code == 400

@pytest.mark.repositories
def test_transfer_ownership_empty_json(db, repo, auth_client, organization, another_user):
    repo_id = repo.data["id"]

    res = auth_client.post(f'/api/repositories/{repo_id}/transfer/',
                           data={})

    assert res.status_code == 400

@pytest.mark.repositories
def test_owner_create_org_repo(db, auth_client, organization):
    org_id, org_name = organization
    res = auth_client.post(f'/api/organizations/{org_name}/repositories/',
                           data={
                               "name": "Organization Repo"
                           })

    assert res.status_code == 201
    assert res.data["owner"]["name"] == "Neworg"

@pytest.mark.repositories
def test_non_owner_create_org_repo(db, auth_client2, organization):
    org_id, org_name = organization
    res = auth_client2.post(f'/api/organizations/{org_name}/repositories/',
                           data={
                               "name": "Organization Repo"
                           })

    assert res.status_code == 403

@pytest.mark.repositories
def test_non_auth_create_org_repo(db, api_client, organization):
    org_id, org_name = organization
    res = api_client.post(f'/api/organizations/{org_name}/repositories/',
                           data={
                               "name": "Organization Repo"
                           })

    assert res.status_code == 401

@pytest.mark.repositories
def test_member_create_org_repo(db, auth_client2, organization, org_member_user2):
    org_id, org_name = organization
    res = auth_client2.post(f'/api/organizations/{org_name}/repositories/',
                           data={
                               "name": "Organization Repo"
                           })

    assert res.status_code == 403

@pytest.mark.repositories
def test_owner_list_org_repo(db, organization, auth_client, org_repo, org_repo_private):
    org_id, org_name = organization
    res = auth_client.get(f'/api/organizations/{org_name}/repositories/')

    assert res.status_code == 200
    print(res.data)
    assert len(res.data["results"]) == 2

@pytest.mark.repositories
def test_non_auth_list_org_repo(db, organization, api_client, org_repo, org_repo_private):
    org_id, org_name = organization
    res = api_client.get(f'/api/organizations/{org_name}/repositories/')

    assert res.status_code == 200
    assert len(res.data["results"]) == 1

@pytest.mark.repositories
def test_member_list_org_repo(db, organization, auth_client2, org_repo, org_repo_private, org_member_user2):
    org_id, org_name = organization
    res = auth_client2.get(f'/api/organizations/{org_name}/repositories/')

    assert res.status_code == 200
    assert len(res.data["results"]) == 1

@pytest.mark.repositories
def test_non_member_list_org_repo(db, organization, auth_client2, org_repo, org_repo_private):
    org_id, org_name = organization
    res = auth_client2.get(f'/api/organizations/{org_name}/repositories/')

    assert res.status_code == 200
    assert len(res.data["results"]) == 1

@pytest.mark.repositories
def test_retrieve_org_repo(db, organization, org_repo, auth_client):
    org_id, org_name = organization
    repo_id = org_repo

    res = auth_client.get(f'/api/organizations/{org_name}/repositories/{repo_id}/')

    assert res.status_code == 405

@pytest.mark.repositories
def test_transfer_ownership_of_org_repo_to_user(db, organization, org_repo, auth_client, another_user):
    org_id, org_name = organization
    repo_id = org_repo

    res = auth_client.post(f'/api/organizations/{org_name}/repositories/{repo_id}/transfer/',
                           data={"user": "another"})

    assert res.status_code == 200

@pytest.mark.repositories
def test_non_owner_ransfer_ownership_of_org_repo_to_user(db, organization, org_repo, auth_client3, another_user):
    org_id, org_name = organization
    repo_id = org_repo

    res = auth_client3.post(f'/api/organizations/{org_name}/repositories/{repo_id}/transfer/',
                           data={"user": "another"})

    assert res.status_code == 403

@pytest.mark.repositories
def test_non_auth_ransfer_ownership_of_org_repo_to_user(db, organization, org_repo, api_client, another_user):
    org_id, org_name = organization
    repo_id = org_repo

    res = api_client.post(f'/api/organizations/{org_name}/repositories/{repo_id}/transfer/',
                           data={"user": "another"})

    assert res.status_code == 401

@pytest.mark.repositories
def test_member_ransfer_ownership_of_org_repo_to_user(db, organization, org_repo, org_member_user3, auth_client3, another_user):
    org_id, org_name = organization
    repo_id = org_repo

    res = auth_client3.post(f'/api/organizations/{org_name}/repositories/{repo_id}/transfer/',
                           data={"user": "another"})

    assert res.status_code == 403

@pytest.mark.repositories
def test_update_collaborator_role(db, repo, auth_client, collaborator):
    col_id, inv_id = collaborator

    repo_id = repo.data['id']

    res = auth_client.patch(f'/api/repositories/{repo_id}/collaborators/{col_id}/',
                            data={
                                "role": "WRITE",
                            })

    assert res.status_code == 200

@pytest.mark.repositories
def test_update_collaborator_role_failure(db, repo, auth_client, collaborator):
    col_id, inv_id = collaborator

    repo_id = repo.data['id']

    res = auth_client.patch(f'/api/repositories/{repo_id}/collaborators/{col_id}/',
                            data={
                                "role": "OWNER",
                            })

    assert res.status_code == 400

@pytest.mark.repositories
def test_update_collaborator_role_failure2(db, repo, auth_client, collaborator):
    col_id, inv_id = collaborator

    repo_id = repo.data['id']

    res = auth_client.patch(f'/api/repositories/{repo_id}/collaborators/{col_id}/',
                            data={
                                "role": "READ",
                            })

    assert res.status_code == 400

@pytest.mark.repositories
def test_update_collaborator_org_repo(db, org_repo, collaborator_org_repo, auth_client):
    repo_id = org_repo
    col_id = collaborator_org_repo

    res = auth_client.patch(f'/api/repositories/{repo_id}/collaborators/{col_id}/',
                            data={
                                "role": "READ",
                            })

    assert res.status_code == 200

@pytest.mark.repositories
def test_update_collaborator_org_repo_2(db, org_repo, collaborator_org_repo, auth_client):
    repo_id = org_repo
    col_id = collaborator_org_repo

    res = auth_client.patch(f'/api/repositories/{repo_id}/collaborators/{col_id}/',
                            data={
                                "role": "ADMIN",
                            })

    assert res.status_code == 200

@pytest.mark.repositories
def test_update_collaborator_org_repo_failure(db, org_repo, collaborator_org_repo, auth_client):
    repo_id = org_repo
    col_id = collaborator_org_repo

    res = auth_client.patch(f'/api/repositories/{repo_id}/collaborators/{col_id}/',
                            data={
                                "role": "OWNER",
                            })

    assert res.status_code == 400

@pytest.mark.repositories
def test_non_owner_update_collaborator_org_repo(db, org_repo, collaborator_org_repo, auth_client3):
    repo_id = org_repo
    col_id = collaborator_org_repo

    res = auth_client3.patch(f'/api/repositories/{repo_id}/collaborators/{col_id}/',
                            data={
                                "role": "ADMIN",
                            })

    assert res.status_code == 403

@pytest.mark.repositories
def test_non_auth_update_collaborator_org_repo(db, org_repo, collaborator_org_repo, api_client):
    repo_id = org_repo
    col_id = collaborator_org_repo

    res = api_client.patch(f'/api/repositories/{repo_id}/collaborators/{col_id}/',
                            data={
                                "role": "ADMIN",
                            })

    assert res.status_code == 401

@pytest.mark.repositories
def test_collaborator_show_repo(db, collaborator, repo, auth_client2):
    repo_id = repo.data["id"]

    res = auth_client2.get(f'/api/repositories/{repo_id}/')

    assert res.status_code == 200

@pytest.mark.repositories
def test_collaborator_read_show_private_org_repo(db, org_repo_private, collaborator_private_org_repo, auth_client2):
    repo_id = org_repo_private
    col_id = collaborator_private_org_repo

    res = auth_client2.get(f'/api/repositories/{repo_id}/')

    assert res.status_code == 200

@pytest.mark.repositories
def test_collaborator_write_show_private_org_repo(db, org_repo_private, collaborator_private_org_repo_write, auth_client2):
    repo_id = org_repo_private
    col_id = collaborator_private_org_repo_write

    res = auth_client2.get(f'/api/repositories/{repo_id}/')

    assert res.status_code == 200

@pytest.mark.repositories
def test_collaborator_admin_show_private_org_repo(db, org_repo_private, collaborator_private_org_repo_admin, auth_client2):
    repo_id = org_repo_private
    col_id = collaborator_private_org_repo_admin

    res = auth_client2.get(f'/api/repositories/{repo_id}/')

    assert res.status_code == 200
    print(res.data)

@pytest.mark.repositories
def test_non_collaborator_show_private_org_repo(db, org_repo_private, auth_client3):
    repo_id = org_repo_private

    res = auth_client3.get(f'/api/repositories/{repo_id}/')

    assert res.status_code == 403

@pytest.mark.repositories
def test_org_member_non_collaborator_show_private_org_repo(db, org_repo_private, org_member_user2, auth_client2):
    repo_id = org_repo_private

    res = auth_client2.get(f'/api/repositories/{repo_id}/')

    assert res.status_code == 403

@pytest.mark.repositories
def test_random_guy_show_public_org_repo(db, org_repo, auth_client2):
    repo_id = org_repo

    res = auth_client2.get(f'/api/repositories/{repo_id}/')

    assert res.status_code == 200

@pytest.mark.repositories
def test_collaborator_update_repo_description(db, repo, collaborator, auth_client2):
    repo_id = repo.data["id"]

    res = auth_client2.patch(f'/api/repositories/{repo_id}/',
                             data={
                                 "description": "newdesc"
                             })

    assert res.status_code == 200
    assert res.data["description"] == "newdesc"

@pytest.mark.repositories
def test_collaborator_update_repo_visibility(db, repo, collaborator, auth_client2):
    repo_id = repo.data["id"]

    res = auth_client2.patch(f'/api/repositories/{repo_id}/',
                             data={
                                 "visibility": "PRIVATE"
                             })

    assert res.status_code == 403

@pytest.mark.repositories
def test_collaborator_read_patch_org_repo(db, org_repo_private, collaborator_private_org_repo, auth_client2):
    repo_id = org_repo_private
    res = auth_client2.patch(f'/api/repositories/{repo_id}/',
                             data={"description": "newdesc"})
    
    assert res.status_code == 403

@pytest.mark.repositories
def test_collaborator_write_patch_org_repo_description(db, org_repo_private, collaborator_private_org_repo_write, auth_client2):
    repo_id = org_repo_private
    res = auth_client2.patch(f'/api/repositories/{repo_id}/',
                             data={"description": "newdesc"})
    
    assert res.status_code == 200

@pytest.mark.repositories
def test_collaborator_write_patch_org_repo_visibility(db, org_repo_private, collaborator_private_org_repo_write, auth_client2):
    repo_id = org_repo_private
    res = auth_client2.patch(f'/api/repositories/{repo_id}/',
                             data={"visibility": "PUBLIC"})
    
    assert res.status_code == 403

@pytest.mark.repositories
def test_collaborator_delete_personal_repo(db, repo, collaborator, auth_client2):
    repo_id = repo.data["id"]
    res = auth_client2.delete(f'/api/repositories/{repo_id}/')

    assert res.status_code == 403

@pytest.mark.repositories
def test_collaborator_transfer_personal_repo(db, repo, collaborator, auth_client2, another_user):
    repo_id = repo.data["id"]
    res = auth_client2.post(f'/api/repositories/{repo_id}/transfer/',
                            data={"user": "another"})
    
    assert res.status_code == 403

@pytest.mark.repositories
def test_collaborator_star_private_repo(db, private_repo, collaborator_private_repo, auth_client2):
    repo_id = private_repo.data["id"]
    res = auth_client2.post(f'/api/repositories/{repo_id}/stars/')

    assert res.status_code == 201

@pytest.mark.repositories
def test_non_collaborator_star_private_org_repo(db, org_repo_private, auth_client3):
    repo_id = org_repo_private
    res = auth_client3.post(f'/api/repositories/{repo_id}/stars/')

    assert res.status_code == 403

@pytest.mark.repositories
def test_collaborator_read_star_private_org_repo(db, org_repo_private, collaborator_private_org_repo, auth_client2):
    repo_id = org_repo_private
    res = auth_client2.post(f'/api/repositories/{repo_id}/stars/')

    assert res.status_code == 201

@pytest.mark.collaborators
def test_admin_collaborator_invite(db, org_repo, collaborator_org_repo_admin, auth_client2, another_user2):
    repo_id = org_repo
    res = auth_client2.post(f'/api/repositories/{repo_id}/collaborators/',
                            data={"invitee": "another2"})
    
    assert res.status_code == 201

@pytest.mark.collaborators
def test_admin_collaborator_remove(db, org_repo, collaborator_org_repo_admin, auth_client2, auth_client3, another_user2):
    repo_id = org_repo
    
    res = auth_client2.post(f'/api/repositories/{repo_id}/collaborators/',
                            data={"invitee": "another2"})
    
    inv_id = res.data["id"]
    col = auth_client3.post(f'/api/invitations/{inv_id}/accept/')
    
    res = auth_client2.delete(f'/api/repositories/{repo_id}/collaborators/{col.data['id']}/')

    assert res.status_code == 204

@pytest.mark.collaborators
def test_write_collaborator_cannot_manage(db, org_repo_private, collaborator_private_org_repo_write, another_user, auth_client2):
    repo_id = org_repo_private
    res = auth_client2.post(f'/api/repositories/{repo_id}/collaborators/',
                            data={"invitee": "another"})
    
    assert res.status_code == 403

@pytest.mark.collaborators
def test_read_collaborator_cannot_manage(db, org_repo_private, collaborator_private_org_repo, another_user, auth_client2):
    repo_id = org_repo_private
    res = auth_client2.post(f'/api/repositories/{repo_id}/collaborators/',
                            data={"invitee": "another"})
    
    assert res.status_code == 403

@pytest.mark.repositories
def test_patch_org_repo_endpoint(db, organization, org_repo, auth_client):
    org_id, org_name = organization
    res = auth_client.patch(f'/api/organizations/{org_name}/repositories/{org_repo}/',
                            data={"description": "new"})
    
    assert res.status_code == 405

@pytest.mark.repositories
def test_delete_org_repo_endpoint(db, organization, org_repo, auth_client):
    org_id, org_name = organization
    res = auth_client.delete(f'/api/organizations/{org_name}/repositories/{org_repo}/')

    assert res.status_code == 405

@pytest.mark.repositories
def test_collaborator_sees_private_org_repo_in_list(db, organization, org_repo_private, collaborator_private_org_repo, auth_client2):
    org_id, org_name = organization
    res = auth_client2.get(f'/api/organizations/{org_name}/repositories/')

    assert res.status_code == 200
    assert len(res.data["results"]) == 1
    



    
# Create your tests here.
