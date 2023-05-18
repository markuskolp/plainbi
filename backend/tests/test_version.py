# -*- coding: utf-8 -*-
"""
Created on Mon May 15 10:02:36 2023

@author: kribbel
"""
import sys
sys.path.append('/plainbi/backend')
sys.path.append('C:/users/kribbel/plainbi/backend')
import urllib
import sqlalchemy
repoengine = sqlalchemy.create_engine("sqlite:////Users/kribbel/plainbi_repo.db")

params = urllib.parse.quote_plus("DSN=DWH_DEV_PORTAL;UID=portal;PWD=s7haPsjrnl3")
dbengine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)


import pytest
from plainbi_backend.api import create_app
from plainbi_backend.repo import create_repo_db,create_pytest_tables

t=None
tv=None
s=None

@pytest.fixture
def setup_and_teardown_for_stuff():
    global t,tv,s
    print("\nsetting up")
    create_repo_db(repoengine)
    t,tv,s = create_pytest_tables(dbengine)
    print("\nrepo created")
    print (t,tv,s)
    yield
    print("\ntearing down")

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('flask_test.cfg')

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!

def test_000_init_repo(setup_and_teardown_for_stuff):
    assert 1 == 1

def test_000_version(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/api/version')
    assert response.status_code == 200
    assert b"0.2" in response.data


def test_1000_repo_ins_app(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appnam='testapp'
    response = test_client.post('/api/repo/application', json= { "name" : appnam })
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==appnam

def test_1010_repo_ins_app2(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appnam='testapp'
    response = test_client.post('/api/repo/application', json= { "name" : appnam, "id" : -9 })
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==appnam
    assert row1["id"]==-9

def test_1020_repo_upd_app(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appid=-9
    appnam2='testapp2'
    response = test_client.put('/api/repo/application/'+str(appid), json= { "name" : appnam2 })
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==appnam2
    assert row1["id"]==appid

def test_1030_repo_get_app(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appid=-9
    appnam2='testapp2'
    response = test_client.get('/api/repo/application/'+str(appid))
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==appnam2
    assert row1["id"]==appid

def test_1040_repo_del_app(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appid=-9
    response = test_client.delete('/api/repo/application/'+str(appid))
    assert response.status_code == 200

def test_1050_repo_get_app(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appid=-9
    response = test_client.get('/api/repo/application/'+str(appid))
    json_out = response.get_json()
    print("got=",json_out)
    assert response.status_code == 204

def test_2000_tab_ins(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable" -w "%{http_code}\n"
    nam="item1"
    id=-8
    response = test_client.post('/api/crud/'+t, json= { "name" : nam, "nr" : id })
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam

def test_2000_tab_ins2(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\"}' "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable?seq=DWH.analysis.pytest_seq" -w "%{http_code}\n"
    nam="item6"
    response = test_client.post('/api/crud/'+t+"?seq="+s, json= { "name" : nam,})
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam

def test_2020_upd(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    #curl --header "Content-Type: application/json" --request PUT --data '{\"name\":\"item2\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable/-8" -w "%{http_code}\n"
    nam="item2"
    id=-8
    response = test_client.put('/api/crud/'+t+'/'+str(id), json= { "name" : nam, "nr":-8 })
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam
    assert row1["nr"]==id

def test_2030_get(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    #
    id=-8
    response = test_client.get('/api/crud/'+t+'/'+str(id))
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]=="item2"
    assert row1["nr"]==id

def test_2031_getall(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    #
    response = test_client.get('/api/crud/'+t)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    #row1=(json_out["data"])[0]
    assert json_out["total_count"]==2

def test_2040_del(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    id=-8
    response = test_client.delete('/api/crud/'+t+'/'+str(id))
    assert response.status_code == 200
