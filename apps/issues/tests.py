import pytest

@pytest.mark.issues
def test_create_issue(db, auth_client2, repo):
    repo_id = repo.data["id"]
    res = auth_client2.post(f'/api/repositories/{repo_id}/issues/',
                            data={
                                "title": "test issue",
                                "description": "nice to know",
                            })

    assert res.status_code == 201

@pytest.mark.issues
def test_create_issue_non_authenticated(db, api_client, repo):
    repo_id = repo.data["id"]
    res = api_client.post(f'/api/repositories/{repo_id}/issues/',
                            data={
                                "title": "test issue",
                                "description": "nice to know",
                            })

    assert res.status_code == 401

@pytest.mark.issues
def test_create_issue_on_private_repo_non_owner(db, private_repo, auth_client2):
    repo_id = private_repo.data["id"]
    res = auth_client2.post(f'/api/repositories/{repo_id}/issues/',
                            data={
                                "title": "test issue",
                                "description": "nice to know",
                            })

    assert res.status_code == 403

@pytest.mark.issues
def test_create_issue_on_private_repo_owner(db, private_repo, auth_client):
    repo_id = private_repo.data["id"]
    res = auth_client.post(f'/api/repositories/{repo_id}/issues/',
                            data={
                                "title": "test issue",
                                "description": "nice to know",
                            })

    assert res.status_code == 201

@pytest.mark.issues
def test_issue_index_non_authenticated(db, issue, api_client):
    issue, repo_id = issue
    res = api_client.get(f'/api/repositories/{repo_id}/issues/')

    assert res.status_code == 200
    assert res.data[0]["title"] == "someissue"

@pytest.mark.issues
def test_issue_on_private_repo_index_non_author(db, issue_on_private, auth_client2):
    issue, repo_id = issue_on_private
    res = auth_client2.get(f'/api/repositories/{repo_id}/issues/')

    assert res.status_code == 403

@pytest.mark.issues
def test_issue_on_private_repo_index_author(db, issue_on_private, auth_client):
    issue, repo_id = issue_on_private
    res = auth_client.get(f'/api/repositories/{repo_id}/issues/')

    assert res.status_code == 200
    assert len(res.data) == 1


@pytest.mark.issues
def test_issue_show_non_authenticated(db, issue, api_client):
    issue, repo_id = issue
    res = api_client.get(f'/api/repositories/{repo_id}/issues/{issue.data['id']}/')

    assert res.status_code == 200
    assert res.data["title"] == "someissue"

@pytest.mark.issues
def test_issue_on_private_show_non_authenticated(db, issue_on_private, api_client):
    issue, repo_id = issue_on_private
    res = api_client.get(f'/api/repositories/{repo_id}/issues/{issue.data['id']}/')

    assert res.status_code == 403

@pytest.mark.issues
def test_issue_on_private_repo_show_non_author(db, issue_on_private, auth_client2):
    issue, repo_id = issue_on_private
    res = auth_client2.get(f'/api/repositories/{repo_id}/issues/{issue.data['id']}/')

    assert res.status_code == 403

@pytest.mark.issues
def test_issue_on_private_repo_show_author(db, issue_on_private, auth_client):
    issue, repo_id = issue_on_private
    res = auth_client.get(f'/api/repositories/{repo_id}/issues/{issue.data['id']}/')

    assert res.status_code == 200
    assert res.data["title"] == "someissue"

@pytest.mark.issues
def test_issue_update(db, issue, auth_client):
    issue, repo_id = issue
    res = auth_client.patch(f'/api/repositories/{repo_id}/issues/{issue.data['id']}/',
                            data={
                                "description": "newdescription",
                                "status": "CLOSED",
                            }) 
    
    assert res.status_code == 200
    assert res.data["description"] == "newdescription"
    assert res.data["status"] == "CLOSED"

@pytest.mark.issues
def test_issue_update_repo_owner(db, issue_user2, auth_client):
    issue, repo_id = issue_user2
    res = auth_client.patch(f'/api/repositories/{repo_id}/issues/{issue.data['id']}/',
                            data={
                                "status": "CLOSED",
                            }) 

    assert res.status_code == 200
    assert res.data["status"] == "CLOSED"

@pytest.mark.issues
def test_issue_update_repo_owner_failure(db, issue_user2, auth_client):
    issue, repo_id = issue_user2
    res = auth_client.patch(f'/api/repositories/{repo_id}/issues/{issue.data['id']}/',
                            data={
                                "title": "u suck",
                                "status": "CLOSED",
                            }) 

    assert res.status_code == 403

@pytest.mark.issues
def test_issue_update_non_onwer(db, issue, auth_client2):
    issue, repo_id = issue
    res = auth_client2.patch(f'/api/repositories/{repo_id}/issues/{issue.data['id']}/',
                            data={
                                "title": "new broski"
                            }) 

    assert res.status_code == 403

@pytest.mark.issues
def test_issue_update_non_auth(db, issue, api_client):
    issue, repo_id = issue
    res = api_client.patch(f'/api/repositories/{repo_id}/issues/{issue.data['id']}/',
                            data={
                                "title": "new broski"
                            }) 

    assert res.status_code == 401

@pytest.mark.issues
def test_issue_delete_owner(db, issue, auth_client):
    issue, repo_id = issue
    res = auth_client.delete(f'/api/repositories/{repo_id}/issues/{issue.data['id']}/') 

    assert res.status_code == 204

@pytest.mark.issues
def test_issue_delete_non_owner(db, issue, auth_client2):
    issue, repo_id = issue
    res = auth_client2.delete(f'/api/repositories/{repo_id}/issues/{issue.data['id']}/') 

    assert res.status_code == 403

@pytest.mark.issues
def test_issue_delete_repo_owner_failure(db, issue_user2, auth_client):
    issue, repo_id = issue_user2
    res = auth_client.delete(f'/api/repositories/{repo_id}/issues/{issue.data['id']}/') 

    assert res.status_code == 403



# Create your tests here.
