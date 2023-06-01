# -*- coding: utf-8 -*-
"""
Created on Mon May 15 10:02:36 2023

run:
    python -m pytest tests\test_version.py

@author: kribbel
"""
import sys
import os
import logging
#sys.path.append('/plainbi/backend')
import urllib
import sqlalchemy

from plainbi_backend.config import config,load_pbi_env

#log = logging.getLogger(__name__)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

fh = logging.FileHandler("test_version.log")
fh_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(fh_formatter)
fh.setLevel(logging.DEBUG)
log.addHandler(fh)

home_directory = os.path.expanduser( '~' )
sys.path.append(home_directory+'/plainbi/backend')

logging.basicConfig(filename='pytest.log', encoding='utf-8', level=logging.DEBUG)

pbi_env = load_pbi_env()

def func_name(): 
    return sys._getframe(1).f_code.co_name


if "db_params" in pbi_env.keys():
    params = urllib.parse.quote_plus(pbi_env["db_params"])
    print("params",params)
    print("db_engine",pbi_env["db_engine"])
    dbengine = sqlalchemy.create_engine(pbi_env["db_engine"] % params)
else:
    dbengine = sqlalchemy.create_engine(pbi_env["db_engine"])
log.info("dbengine %s",dbengine.url)

if "repo_params" in pbi_env.keys():
    params = urllib.parse.quote_plus(pbi_env["repo_params"])
    print("repo params",params)
    print("repo_engine",pbi_env["repo_engine"])
    repoengine = sqlalchemy.create_engine(pbi_env["repo_engine"] % params)
else:
    repoengine = sqlalchemy.create_engine(pbi_env["repo_engine"])
log.info("repoengine %s",repoengine.url)
repo_table_prefix="plainbi_"


token=None
testuser_token=None
headers=None
testuser_headers=None
testuser_id=None

import pytest
from plainbi_backend.api import create_app
from plainbi_backend.repo import create_repo_db,create_pytest_tables
from plainbi_backend.db import db_adduser

t=None
tv=None
tvc=None
s=None

@pytest.fixture
def setup_and_teardown_for_stuff():
    global t,tv,s,tvc
    log.info("dbengine %s",dbengine.url)
    log.info("\nsetting up")
    create_repo_db(repoengine)
    t,tv,s,tvc = create_pytest_tables(dbengine)
    # first add testuser
    db_adduser(repoengine,"joe",fullname="Johannes Kribbel",pwd="joe123",is_admin=True)
    print("\nrepo created")
    print (t,tv,s,tvc)
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
    log.info('TEST: %s',func_name())
    assert 1 == 1


def test_000_login(test_client):
    #
    # login with testuser
    log.info('TEST: %s',func_name())
    global token,headers
    response = test_client.post('/login', json= { "username" : "joe", "password":"joe123" })
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    token=json_out["access_token"]
    print(token)
    headers = { 'Authorization': '{}'.format(token)}


def test_000_version(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    response = test_client.get('/api/version')
    assert response.status_code == 200
    assert b"0.2" in response.data


##############################################################
# REPO tests
##############################################################

def test_1000_repo_ins_app(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appnam='testapp'
    response = test_client.post('/api/repo/application', json= { "name" : appnam }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==appnam


def test_1003_repo_ins_group(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    #
    log.info('TEST: %s',func_name())
    appnam='testgroup'
    url='/api/repo/group'
    print(url)
    curl="curl --header \"Content-Type: application/json\" --request POST --data '{\\\"id\\\":\\\""+str(-3)+"\\\",\\\"name\\\":\\\""+appnam+"\\\"}' \"localhost:3002"+url+"\" -w \"%{http_code}\n\""
    print("curl: ",curl)
    response = test_client.post(url, json= { "name" : appnam, "id" : -3 }, headers=headers)
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
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\",\"id\":\"-9\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"
    appnam='testapp'
    response = test_client.post('/api/repo/application', json= { "name" : appnam, "id" : -9 }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==appnam
    assert row1["id"]==-9

def test_1011_repo_ins_testapp(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appnam='testuser_app'
    response = test_client.post('/api/repo/application', json= { "name" : appnam, "id" : -10 }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==appnam
    assert row1["id"]==-10

def test_1012_repo_ins_testnoapp(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appnam='testuser_noapp'
    response = test_client.post('/api/repo/application', json= { "name" : appnam, "id" : -11 }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==appnam
    assert row1["id"]==-11

def test_1020_repo_upd_app(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request PUT --data '{\"name\":\"testappx\"}' "localhost:3002/api/repo/application/-9" -w "%{http_code}\n"    
    appid=-9
    appnam2='testapp2'
    response = test_client.put('/api/repo/application/'+str(appid), json= { "name" : appnam2 }, headers=headers)
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
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appid=-9
    appnam2='testapp2'
    response = test_client.get('/api/repo/application/'+str(appid), headers=headers)
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
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request DELETE  "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appid=-9
    response = test_client.delete('/api/repo/application/'+str(appid), headers=headers)
    assert response.status_code == 200

def test_1050_repo_get_app(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appid=-9
    response = test_client.get('/api/repo/application/'+str(appid), headers=headers)
    json_out = response.get_json()
    print("got=",json_out)
    assert response.status_code == 204

# test mit compound keys
def test_1100_repo_ins_app_to_grp(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    response = test_client.post('/api/repo/application_to_group', json= { "application_id" : -9, "group_id": -3 }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["group_id"]==-3

def test_1101_repo_compound_get(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    response = test_client.get('/api/repo/application_to_group/(application_id:-9:group_id:-3)', headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["group_id"]==-3

def test_1105_repo_compound_del(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request DELETE  "localhost:3002/api/repo/application_to_group/(application_id:-9:group_id:-3)?pk=application_id,group_id" -w "%{http_code}\n"
    response = test_client.delete('/api/repo/application_to_group/(application_id:-9:group_id:-3)?pk=application_id,group_id', headers=headers)
    assert response.status_code == 200

def test_1106_repo_get(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    response = test_client.get('/api/repo/application_to_group/(application_id:-9:group_id:-3)?pk=application_id,group_id', headers=headers)
    assert response.status_code == 204


##############################################################
# normal table crud tests
##############################################################

def test_2000_tab_ins(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable" -w "%{http_code}\n"
    nam="item1"
    id=-8
    url='/api/crud/'+t
    print(url)
    curl="curl --header \"Content-Type: application/json\" --request POST --data '{\\\"nr\\\":\\\""+str(id)+"\\\",\\\"name\\\":\\\""+nam+"\\\",\\\"dat\\\":\\\"2023-04-27\\\"}' \"localhost:3002"+url+"\" -w \"%{http_code}\n\""
    print("curl: ",curl)

    response = test_client.post('/api/crud/'+t, json= { "name" : nam, "nr" : id }, headers=headers)
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
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\"}' "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable?seq=DWH.analysis.pytest_seq" -w "%{http_code}\n"
    nam="item6"
    response = test_client.post('/api/crud/'+t+"?seq="+s, json= { "name" : nam,}, headers=headers)
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
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request PUT --data '{\"name\":\"item2\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable/-8" -w "%{http_code}\n"
    nam="item2"
    id=-8
    response = test_client.put('/api/crud/'+t+'/'+str(id), json= { "name" : nam, "nr":-8 }, headers=headers)
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
    log.info('TEST: %s',func_name())
    id=-8
    response = test_client.get('/api/crud/'+t+'/'+str(id), headers=headers)
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
    log.info('TEST: %s',func_name())
    response = test_client.get('/api/crud/'+t, headers=headers)
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
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request DELETE "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable/-8" -w "%{http_code}\n"    
    id=-8
    response = test_client.delete('/api/crud/'+t+'/'+str(id), headers=headers)
    assert response.status_code == 200



##############################################################
# versioned table crud tests
##############################################################
def test_3000_vtab_ins(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    nam="item1"
    id=-8
    url='/api/crud/'+tv+"?v"
    print(url)
    response = test_client.post(url, json= { "name" : nam, "nr" : id }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam

def test_3010_vtab_upd(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    nam="item2"
    id=-8
    url='/api/crud/'+tv+"/"+str(id)+"?v&pk=nr"
    print("url:", url)
    curl="curl --header \"Content-Type: application/json\" --request PUT --data '{\\\"nr\\\":\\\""+str(id)+"\\\",\\\"name\\\":\\\""+nam+"\\\",\\\"dat\\\":\\\"2023-04-27\\\"}' \"localhost:3002"+url+"\" -w \"%{http_code}\n\""
    print("curl: ",curl)
    response = test_client.put(url, json= { "name" : nam, "nr" : -8 }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam
    assert row1["nr"]==id

def test_3030_vget(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    id=-8
    url='/api/crud/'+tv+'/'+str(id)+"?v&pk=nr"
    print(url)
    response = test_client.get(url, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]=="item2"
    assert row1["nr"]==id

def test_3031_vgetall(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    url='/api/crud/'+tv+"?v"
    print(url)
    response = test_client.get(url, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    #row1=(json_out["data"])[0]
    assert json_out["total_count"]==1

def test_3040_vdel(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request DELETE "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable/-8" -w "%{http_code}\n"    
    id=-8
    url='/api/crud/'+tv+'/'+str(id)+"?v"
    print(url)
   
    response = test_client.delete(url, headers=headers)
    assert response.status_code == 200

def test_3041_vgetall(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    url='/api/crud/'+tv+"?v"
    print(url)
    response = test_client.get(url, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    #row1=(json_out["data"])[0]
    assert json_out["total_count"]==0

def test_3050_vtab_reins(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    nam="item1"
    id=-8
    url='/api/crud/'+tv+"?v"
    print(url)
    curl="curl --header \"Content-Type: application/json\" --request POST --data '{\\\"nr\\\":\\\""+str(id)+"\\\",\\\"name\\\":\\\""+nam+"\\\",\\\"dat\\\":\\\"2023-04-27\\\"}' \"localhost:3002"+url+"\" -w \"%{http_code}\n\""
    print("curl: ",curl)
    response = test_client.post(url, json= { "name" : nam, "nr" : id }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam

def test_3051_vgetall(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    url='/api/crud/'+tv+"?v"
    print(url)
    response = test_client.get(url, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    #row1=(json_out["data"])[0]
    assert json_out["total_count"]==1

##############################################################
# versioned table crud tests with compound pk
##############################################################
def test_4000_vtab_ins(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    nam="item1"
    id=-8
    typid=-2
    url='/api/crud/'+tvc+"?v&pk=nr,typ"
    print(url)
    response = test_client.post(url, json= { "name" : nam, "nr" : id, "typ" : typid }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam


def test_4001_vtab_ins_pk1_pk_a(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    id=-10
    typid=-2
    nam="item-"+str(id)+"-"+str(typid)+"_ins"
    url='/api/crud/'+tvc+"?v&pk=nr,typ"
    print(url)
    response = test_client.post(url, json= { "name" : nam, "nr" : id, "typ" : typid }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam
    assert row1["nr"]==id
    assert row1["typ"]==typid

def test_4002_vtab_ins_pk1_pk_b(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    id=-10
    typid=-3
    nam="item-"+str(id)+"-"+str(typid)+"_ins"
    url='/api/crud/'+tvc+"?v&pk=nr,typ"
    print(url)
    response = test_client.post(url, json= { "name" : nam, "nr" : id, "typ" : typid }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam
    assert row1["nr"]==id
    assert row1["typ"]==typid


def test_4010_vtab_upd(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    id=-8
    typid=-2
    nam="item2"
    url='/api/crud/'+tvc+"/(nr:"+str(id)+":typ:"+str(typid)+")?v&pk=nr,typ"
    print("url:", url)
    curl="curl --header \"Content-Type: application/json\" --request PUT --data '{\\\"nr\\\":\\\""+str(id)+"\\\",\\\"name\\\":\\\""+nam+"\\\",\\\"dat\\\":\\\"2023-04-27\\\"}' \"localhost:3002"+url+"\" -w \"%{http_code}\n\""
    print("curl: ",curl)
    response = test_client.put(url, json= { "name" : nam, "nr" : -8 }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam
    assert row1["nr"]==id

def test_4011_vtab_upd(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    id=-10
    typid=-2
    nam="item-"+str(id)+"-"+str(typid)+"_upd"
    url='/api/crud/'+tvc+"/(nr:"+str(id)+":typ:"+str(typid)+")?v&pk=nr,typ"
    print("url:", url)
    curl="curl --header \"Content-Type: application/json\" --request PUT --data '{\\\"nr\\\":\\\""+str(id)+"\\\",\\\"name\\\":\\\""+nam+"\\\",\\\"dat\\\":\\\"2023-04-27\\\"}' \"localhost:3002"+url+"\" -w \"%{http_code}\n\""
    print("curl: ",curl)
    response = test_client.put(url, json= { "name" : nam }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam
    assert row1["nr"]==id

def test_4012_vtab_upd(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    nam="item-10-3_upd"
    id=-10
    typid=-3
    url='/api/crud/'+tvc+"/(nr:"+str(id)+":typ:"+str(typid)+")?v&pk=nr,typ"
    print("url:", url)
    curl="curl --header \"Content-Type: application/json\" --request PUT --data '{\\\"nr\\\":\\\""+str(id)+"\\\",\\\"name\\\":\\\""+nam+"\\\",\\\"dat\\\":\\\"2023-04-27\\\"}' \"localhost:3002"+url+"\" -w \"%{http_code}\n\""
    print("curl: ",curl)
    response = test_client.put(url, json= { "name" : nam }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam
    assert row1["nr"]==id


def test_4030_vget(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    id=-8
    typid=-2
    url='/api/crud/'+tvc+"/(nr:"+str(id)+":typ:"+str(typid)+")?v&pk=nr,typ"
    print(url)
    response = test_client.get(url, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]=="item2"
    assert row1["nr"]==id

def test_4031_vgetall(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    url='/api/crud/'+tvc+"?v"
    print(url)
    response = test_client.get(url, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    #row1=(json_out["data"])[0]
    assert json_out["total_count"]==3

def test_4040_vdel(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request DELETE "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable/-8" -w "%{http_code}\n"    
    id=-8
    typid=-2
    url='/api/crud/'+tvc+"/(nr:"+str(id)+":typ:"+str(typid)+")?v&pk=nr,typ"
    print(url)
   
    response = test_client.delete(url, headers=headers)
    assert response.status_code == 200

def test_4050_vtab_reins(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    nam="reinsert"
    id=-8
    typid=-2
    url='/api/crud/'+tvc+"?v&pk=nr,typ"
    print(url)
    curl="curl --header \"Content-Type: application/json\" --request POST --data '{\\\"nr\\\":\\\""+str(id)+"\\\",\\\"name\\\":\\\""+nam+"\\\",\\\"dat\\\":\\\"2023-04-27\\\"}' \"localhost:3002"+url+"\" -w \"%{http_code}\n\""
    print("curl: ",curl)
    response = test_client.post(url, json= { "name" : nam, "nr" : id, "typ" : typid }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam

### auth testing

def test_5000_repo_ins_user(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers,testuser_id
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    response = test_client.post('/api/repo/user', json= { "username" : "testuser", "password_hash" : "testuser123", "role_id" : 2 }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["username"]=="testuser"
    testuser_id=row1["id"]

def test_5001_testuser_login(test_client):
    #
    # login with testuser
    global testuser_token, testuser_headers
    log.info('TEST: %s',func_name())
    response = test_client.post('/login', json= { "username" : "testuser", "password":"testuser123" })
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    testuser_token=json_out["access_token"]
    print("Testuser token=",testuser_token)
    testuser_headers = { 'Authorization': '{}'.format(testuser_token)}

def test_5008_repo_ins_app_to_grp(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    response = test_client.post('/api/repo/application_to_group', json= { "application_id" : -10, "group_id": -3 }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["group_id"]==-3

def test_5009_repo_ins_user_grp(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers,testuser_id
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    response = test_client.post('/api/repo/user_to_group', json= { "user_id" : testuser_id, "group_id" : -3 }, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["group_id"]==-3


def test_5010_repo_get_app(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appid=-10
    response = test_client.get('/api/repo/application/'+str(appid), headers=testuser_headers)
    json_out = response.get_json()
    print("got=",json_out)
    assert response.status_code == 200

def test_5011_repo_get_noapp(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appid=-11
    response = test_client.get('/api/repo/application/'+str(appid), headers=testuser_headers)
    json_out = response.get_json()
    print("got=",json_out)
    assert response.status_code == 204
