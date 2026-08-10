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


@pytest.mark.comments
def test_create_comment(db, issue, auth_client):
    issue, repo_id = issue
    issue_id = issue.data['id']
    res = auth_client.post(f'/api/repositories/{repo_id}/issues/{issue_id}/comments/',
                           data={
                               "contents": "testcomment"
                           })

    assert res.status_code == 201

@pytest.mark.comments
def test_create_comment_unauth(db, issue, api_client):
    issue, repo_id = issue
    issue_id = issue.data['id']
    res = api_client.post(f'/api/repositories/{repo_id}/issues/{issue_id}/comments/',
                           data={
                               "contents": "testcomment"
                           })

    assert res.status_code == 401

@pytest.mark.comments
def test_create_comment_failure(db, issue, auth_client):
    issue, repo_id = issue
    issue_id = issue.data['id']
    res = auth_client.post(f'/api/repositories/{repo_id}/issues/{issue_id}/comments/',
                           data={
                               "contents": ""
                           })

    assert res.status_code == 400

@pytest.mark.comments
def test_create_comment_no_credentials(db, issue, auth_client):
    issue, repo_id = issue
    issue_id = issue.data['id']
    res = auth_client.post(f'/api/repositories/{repo_id}/issues/{issue_id}/comments/',
                           data={
                               
                           })

    assert res.status_code == 400

@pytest.mark.comments
def test_create_comment_issue_wrong_repo(db, issue, repo2, auth_client):
    issue, repo_id = issue
    issue_id = issue.data['id']

    repo2_id = repo2.data['id']
    res = auth_client.post(f'/api/repositories/{repo2_id}/issues/{issue_id}/comments/',
                           data={
                               "contents": "comment type beat"
                           })

    assert res.status_code == 404

@pytest.mark.comments
def test_create_comment_non_existent_issue(db, repo, auth_client):
    repo_id = repo.data['id']
    res = auth_client.post(f'/api/repositories/{repo_id}/issues/{1}/comments/',
                           data={
                               "contents": "new new new"
                           })

    assert res.status_code == 404

@pytest.mark.comments
def test_update_comment(db, comment, auth_client):
    repo_id, issue_id, comment_id = comment
    res = auth_client.patch(f'/api/repositories/{repo_id}/issues/{issue_id}/comments/{comment_id}/',
                            data={
                                "contents": "newcontents",
                            })

    assert res.status_code == 200
    assert res.data['contents'] == "newcontents"

@pytest.mark.comments
def test_update_comment_non_owner(db, comment, auth_client2):
    repo_id, issue_id, comment_id = comment
    res = auth_client2.patch(f'/api/repositories/{repo_id}/issues/{issue_id}/comments/{comment_id}/',
                            data={
                                "contents": "newcontents",
                            })

    assert res.status_code == 404

@pytest.mark.comments
def test_update_comment_failure(db, comment, auth_client):
    repo_id, issue_id, comment_id = comment
    res = auth_client.patch(f'/api/repositories/{repo_id}/issues/{issue_id}/comments/{comment_id}/',
                            data={
                                "contents": "",
                            })

    assert res.status_code == 400

@pytest.mark.comments
def test_delete_comment(db, comment, auth_client):
    repo_id, issue_id, comment_id = comment
    res = auth_client.delete(
        f'/api/repositories/{repo_id}/issues/{issue_id}/comments/{comment_id}/'
    )
    assert res.status_code == 204


@pytest.mark.comments
def test_delete_comment_non_owner(db, comment, auth_client2):
    repo_id, issue_id, comment_id = comment
    res = auth_client2.delete(
        f'/api/repositories/{repo_id}/issues/{issue_id}/comments/{comment_id}/'
    )
    assert res.status_code == 404


@pytest.mark.comments
def test_delete_comment_unauth(db, comment, api_client):
    repo_id, issue_id, comment_id = comment
    res = api_client.delete(
        f'/api/repositories/{repo_id}/issues/{issue_id}/comments/{comment_id}/'
    )
    assert res.status_code == 401


@pytest.mark.comments
def test_comment_wrong_issue(db, comment, issue2, auth_client):
    repo_id, issue_id, comment_id = comment
    issue2, repo_id = issue2
    wrong_issue_id = issue2.data['id']
    res = auth_client.patch(
        f'/api/repositories/{repo_id}/issues/{wrong_issue_id}/comments/{comment_id}/',
        data={"contents": "should not work"}
    )
    assert res.status_code == 404


@pytest.mark.comments
def test_put_not_allowed(db, comment, auth_client):
    repo_id, issue_id, comment_id = comment
    res = auth_client.put(
        f'/api/repositories/{repo_id}/issues/{issue_id}/comments/{comment_id}/',
        data={"contents": "full replace attempt"}
    )
    assert res.status_code == 405


@pytest.mark.comments
def test_list_comments_not_allowed(db, issue, auth_client):
    issue, repo_id = issue
    issue_id = issue.data['id']
    res = auth_client.get(
        f'/api/repositories/{repo_id}/issues/{issue_id}/comments/'
    )
    assert res.status_code == 405


@pytest.mark.comments
def test_retrieve_comment_not_allowed(db, comment, auth_client):
    repo_id, issue_id, comment_id = comment
    res = auth_client.get(
        f'/api/repositories/{repo_id}/issues/{issue_id}/comments/{comment_id}/'
    )
    assert res.status_code == 405

# Create your tests here.
