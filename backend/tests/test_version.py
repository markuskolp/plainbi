# -*- coding: utf-8 -*-
"""
Created on Mon May 15 10:02:36 2023

run:
    python -m pytest tests\test_version.py

@author: kribbel
"""
import sys
import logging
#sys.path.append('/plainbi/backend')
import urllib
import sqlalchemy
import os

from plainbi_backend.config import config,load_pbi_env
from plainbi_backend.db import db_connect

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

dbengine = db_connect(pbi_env["db_engine"],pbi_env["db_params"] if "db_params" in pbi_env.keys() else None)
log.info("dbengine %s",dbengine.url)

from sys import platform
if platform == "win32":
    x=f"{home_directory}".replace("\\","/")
    x=x.replace("C:/","")
    test_repo_engine_str=f"sqlite:////{x}/plainbi_repo_pytests.db"
else:
    test_repo_engine_str=f"sqlite:///{home_directory}/plainbi_repo_pytests.db"
log.info("pytests repo db str = %s",test_repo_engine_str)
repoengine = db_connect(test_repo_engine_str)
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

def format_url(method, url, data=None, auth=True, port=3001, testname=None):
    log.info("format_url")
    #curl -H "Content-Type: application/json"  -H "Authorization: %tok%" --request GET "localhost:3002/api/repo/resource?order_by=name&offset=1" -w "%{http_code}\n"
    winurl="curl"
    uxurl="curl"
    winurl+=' -H "Content-Type: application/json"'
    uxurl+=' -H "Content-Type: application/json"'
    if auth:
        winurl+=' -H "Authorization: %tok%"'
        uxurl+=' -H "Authorization: $tok"'
    if data is not None:
        winurl+=" --data '{"
        uxurl+="  --data '{"
        for k,v in data.items():
            if isinstance(v,int):
               winurl+='\\"'+k+'\\":'+str(v)
               uxurl+='"'+k+'":'+str(v)
            else:
               winurl+='\\"'+k+'\\":\\"'+v+'\\"'
               uxurl+='"'+k+'":"'+v+'"'
        winurl+="}'"
        uxurl+="}'"
        
    winurl+=' --request '+method.upper()
    uxurl+=' --request '+method.upper()
    winurl+=' "localhost:'+str(port)+url+'"'
    uxurl+='  "localhost:'+str(port)+url+'"'
    winurl+=' -w "%{http_code}\\n"'
    uxurl+='  -w "%{http_code}\\n"'
    print("win:",winurl)
    print("ux :",uxurl)
    t=""
    if testname is not None:
        t=testname
    log.info(f"({t})win:%s",winurl)
    log.info(f"({t})lnx:%s",uxurl)

@pytest.fixture
def setup_and_teardown_for_stuff():
    global t,tv,s,tvc
    log.info("dbengine %s",dbengine.url)
    log.info("\nsetting up")
    create_repo_db(repoengine)
    t,tv,s,tvc = create_pytest_tables(dbengine)
    # first add testuser
    print("\nrepo created")
    print (t,tv,s,tvc)
    yield
    print("\ntearing down")

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app(config_filename=None,p_repository=test_repo_engine_str)

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!


#def test_000_add___user_joe(test):
#    global headers,testuser_id
#    log.info('TEST: %s',func_name())
#    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
#    response = test_client.post('/api/repo/user', json= { "username" : "joe", "password_hash" : "joe123", "role_id" : 1 }, headers=headers)
#    assert response.status_code == 200
#    json_out = response.get_json()
#    print("got=",json_out)
#    row1=(json_out["data"])[0]
#    assert row1["username"]=="joe"
#    joeuser_id=row1["id"]


def test_000_init_repo(setup_and_teardown_for_stuff):
    log.info('TEST: %s',func_name())
    assert 1 == 1


def test_000_login(test_client):
    #
    # login with testuser
    global token,headers
    log.info('++++++++++++++++\nTEST: %s++++++++++++++++\n',func_name())
    db_adduser(repoengine,"joe",fullname="Johannes Kribbel",pwd="joe123",is_admin=True)
    log.info("++++++++++++++++\ndone add user joe\n++++++++++++++++\n")
    log.info('++++++++++++++++\nlogin joe\n++++++++++++++++\n')
    test_url='/login'
    test_json={ "username" : "joe", "password":"joe123" }
    format_url("post", test_url, auth=False,testname=func_name())
    response = test_client.post(test_url, json=test_json)
    log.info('++++++++++++++++\nlogin joe2\n++++++++++++++++\n')
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    log.info('++++++++++++++++\njson_out=%s\n++++++++++++++++\n',json_out)
    token=json_out["access_token"]
    print(token)
    log.info("Token: %s",str(token))
    
    #con.setRequestProperty("Content-Type", "application/json; charset=utf8");
    #con.setRequestProperty("Accept", "application/json");
    
    #headers = { 'Authorization': '{}'.format(token), "Accept": "application/json", "Content-Type" : "application/json; charset=utf8" }
    headers = { 'Authorization': '{}'.format(token)}
    log.info("Headers set to: %s",str(headers))
    assert json_out["role"] == "Admin"

def test_000_version(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    log.info('TEST: %s',func_name())
    test_url='/api/version'
    format_url("get",test_url, testname=func_name())
    response = test_client.get(test_url)
    assert response.status_code == 200
    assert b"0.3" in response.data


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
    appnam = 'testapp'
    test_url = '/api/repo/application'
    test_data = {"name" : appnam }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
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
    global headers
    #
    log.info('TEST: %s',func_name())
    appnam='testgroup'
    test_url='/api/repo/group'
    test_data={ "name" : appnam, "id" : -3 }
    format_url("post", test_url, data=test_data)
    response = test_client.post(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    appnam='testapp'
    test_url='/api/repo/application'
    test_data={ "name" : appnam, "id" : -9 }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
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
    appnam='testuser_app'
    test_url='/api/repo/application'
    test_data={ "name" : appnam, "id" : -10 }
    format_url("post", test_url, data=test_data)
    response = test_client.post(test_url, json=test_data, headers=headers)
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
    test_url='/api/repo/application'
    test_data={ "name" : appnam, "id" : -11 }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request PUT --data '{\"name\":\"testappx\"}' "localhost:3002/api/repo/application/-9" -w "%{http_code}\n"    
    appid=-9
    appnam2='testapp2'
    test_url='/api/repo/application/'+str(appid)
    test_data={ "name" : appnam2 }
    format_url("put", test_url, data=test_data, testname=func_name())
    response = test_client.put(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appid=-9
    appnam2='testapp2'
    test_url='/api/repo/application/'+str(appid)
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    appid=-9
    test_url='/api/repo/application/'+str(appid)
    format_url("delete", test_url)
    response = test_client.delete(test_url, headers=headers)
    assert response.status_code == 200

def test_1050_repo_get_app(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    appid=-9
    test_url='/api/repo/application/'+str(appid)
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"
    test_url='/api/repo/application_to_group'
    test_data={ "application_id" : -9, "group_id": -3 }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["application_id"]==-9
    assert row1["group_id"]==-3

def test_1101_repo_compound_get(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/repo/application_to_group/(application_id:-9:group_id:-3)'
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request DELETE  "localhost:3002/api/repo/application_to_group/(application_id:-9:group_id:-3)?pk=application_id,group_id" -w "%{http_code}\n"
    test_url='/api/repo/application_to_group/(application_id:-9:group_id:-3)?pk=application_id,group_id'
    format_url("delete", test_url, testname=func_name())
    response = test_client.delete(test_url, headers=headers)
    assert response.status_code == 200

def test_1106_repo_get(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/repo/application_to_group/(application_id:-9:group_id:-3)?pk=application_id,group_id'
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
    assert response.status_code == 204

def test_1114_repo_ins_app_to_grp_nopk(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"    
    test_url='/api/repo/application_to_group'
    test_data={ "application_id" : -9, "group_id": -3 }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["group_id"]==-3


def test_1115_repo_compound_del_nopk(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request DELETE  "localhost:3002/api/repo/application_to_group/(application_id:-9:group_id:-3)?pk=application_id,group_id" -w "%{http_code}\n"
    test_url='/api/repo/application_to_group/(application_id:-9:group_id:-3)'
    format_url("get", test_url, testname=func_name())
    response = test_client.delete(test_url, headers=headers)
    assert response.status_code == 200

def test_1116_repo_get_nopk(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/repo/application_to_group/(application_id:-9:group_id:-3)'
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable" -w "%{http_code}\n"
    nam="item1"
    id=-8
    test_url='/api/crud/'+t
    test_data={ "name" : nam, "nr" : id }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\"}' "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable?seq=DWH.analysis.pytest_seq" -w "%{http_code}\n"
    nam="item6"
    test_url='/api/crud/'+t+"?seq="+s
    test_data={ "name" : nam,}
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request PUT --data '{\"name\":\"item2\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable/-8" -w "%{http_code}\n"
    nam="item2"
    id=-8
    test_url='/api/crud/'+t+'/'+str(id)
    test_data={ "name" : nam, "nr":-8 }
    format_url("put", test_url, data=test_data, testname=func_name())
    response = test_client.put(test_url, json=test_data, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam
    assert row1["nr"]==id

# customsql
def test_2025_repo_ins_customsql(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/repo/customsql'
    test_data={ "name" : "test customsql2" , "alias" : "customsql2", "sql_query": f"select * from {t}" }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["alias"]=="customsql2"


def test_2030_get(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers,t
    log.info('TEST: %s',func_name())
    id=-8
    test_url='/api/crud/'+t+'/'+str(id)
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
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
    global t,headers
    log.info('TEST: %s',func_name())
    test_url='/api/crud/'+t
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    #row1=(json_out["data"])[0]
    assert json_out["total_count"]==2

   
def test_2032_crud_get_customsql(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers,t
    log.info('TEST: %s',func_name())
    id=-8
    test_url='/api/crud/'+t+'/'+str(id)+"?customsql=customsql2"
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]=="item2"
    assert row1["nr"]==id

def test_2033_crud_getall_customsql(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global t,headers
    log.info('TEST: %s',func_name())
    test_url='/api/crud/'+t+"?customsql=customsql2"
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    #row1=(json_out["data"])[0]
    assert json_out["total_count"]==2


def test_2035_getall_filter(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global t,headers
    log.info('TEST: %s',func_name())
    test_url='/api/crud/'+t+"?filter=item"
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    #row1=(json_out["data"])[0]
    assert json_out["total_count"]==2

def test_2036_getall_filter2(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global t,headers
    log.info('TEST: %s',func_name())
    test_url='/api/crud/'+t+"?filter=item2"
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    #row1=(json_out["data"])[0]
    assert json_out["total_count"]==1

def test_2040_del(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request DELETE "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable/-8" -w "%{http_code}\n"    
    id=-8
    test_url='/api/crud/'+t+'/'+str(id)
    format_url("delete", test_url, testname=func_name())
    response = test_client.delete(test_url, headers=headers)
    assert response.status_code == 200


def test_2050_clear_cache(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    test_url='/clear_cache'
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
    json_out = response.get_json()
    print("got=",json_out)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    nam="item1"
    id=-8
    test_url='/api/crud/'+tv+"?v"
    test_data={ "name" : nam, "nr" : id }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    nam="item2"
    id=-8
    test_url='/api/crud/'+tv+"/"+str(id)+"?v&pk=nr"
    test_data= { "name" : nam, "nr" : -8 }
    format_url("put", test_url, data=test_data, testname=func_name())
    response = test_client.put(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    id=-8
    test_url='/api/crud/'+tv+'/'+str(id)+"?v&pk=nr"
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/crud/'+tv+"?v"
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    #row1=(json_out["data"])[0]
    assert json_out["total_count"]==1
    
def test_3032_vgetall_filter(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/crud/'+tv+"?v&filter=item"
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request DELETE "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable/-8" -w "%{http_code}\n"    
    id=-8
    test_url='/api/crud/'+tv+'/'+str(id)+"?v"
    format_url("delete", test_url, testname=func_name())
    response = test_client.delete(test_url, headers=headers)
    assert response.status_code == 200

def test_3041_vgetall(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/crud/'+tv+"?v"
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    nam="item1"
    id=-8
    test_url='/api/crud/'+tv+"?v"
    test_data={ "name" : nam, "nr" : id }
    format_url("put", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/crud/'+tv+"?v"
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    nam="item1"
    id=-8
    typid=-2
    test_url='/api/crud/'+tvc+"?v&pk=nr,typ"
    test_data={ "name" : nam, "nr" : id, "typ" : typid }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    id=-10
    typid=-2
    nam="item-"+str(id)+"-"+str(typid)+"_ins"
    test_url='/api/crud/'+tvc+"?v&pk=nr,typ"
    test_data={ "name" : nam, "nr" : id, "typ" : typid }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    id=-10
    typid=-3
    nam="item-"+str(id)+"-"+str(typid)+"_ins"
    test_url='/api/crud/'+tvc+"?v&pk=nr,typ"
    test_data={ "name" : nam, "nr" : id, "typ" : typid }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    id=-8
    typid=-2
    nam="item2"
    test_url='/api/crud/'+tvc+"/(nr:"+str(id)+":typ:"+str(typid)+")?v&pk=nr,typ"
    test_data={ "name" : nam, "nr" : -8 }
    format_url("put", test_url, data=test_data, testname=func_name())
    response = test_client.put(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    id=-10
    typid=-2
    nam="item-"+str(id)+"-"+str(typid)+"_upd"
    test_url='/api/crud/'+tvc+"/(nr:"+str(id)+":typ:"+str(typid)+")?v&pk=nr,typ"
    test_data={ "name" : nam }
    format_url("put", test_url, data=test_data, testname=func_name())
    response = test_client.put(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    nam="item-10-3_upd"
    id=-10
    typid=-3
    test_url='/api/crud/'+tvc+"/(nr:"+str(id)+":typ:"+str(typid)+")?v&pk=nr,typ"
    test_data={ "name" : nam }
    format_url("put", test_url, data=test_data, testname=func_name())
    response = test_client.put(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    id=-8
    typid=-2
    test_url='/api/crud/'+tvc+"/(nr:"+str(id)+":typ:"+str(typid)+")?v&pk=nr,typ"
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/crud/'+tvc+"?v"
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request DELETE "localhost:3002/api/crud/dwh.analysis.pytest_api_testtable/-8" -w "%{http_code}\n"    
    id=-8
    typid=-2
    test_url='/api/crud/'+tvc+"/(nr:"+str(id)+":typ:"+str(typid)+")?v&pk=nr,typ"
    format_url("delete", test_url, testname=func_name())
    response = test_client.delete(test_url, headers=headers)
    assert response.status_code == 200

def test_4050_vtab_reins(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"item\",\"nr\":-8}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable?v" -w "%{http_code}\n"
    nam="reinsert"
    id=-8
    typid=-2
    test_url='/api/crud/'+tvc+"?v&pk=nr,typ"
    test_data= { "name" : nam, "nr" : id, "typ" : typid }
    format_url("put", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==nam
    
def test_4100_repo_get_apps(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/repo/application'
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
    json_out = response.get_json()
    print("got=",json_out)
    assert response.status_code == 200
    assert json_out["total_count"] == 5

def test_4101_repo_get_apps_filter(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/repo/application?filter=testapp'
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
    json_out = response.get_json()
    print("got=",json_out)
    assert response.status_code == 200
    assert json_out["total_count"] == 1
    
### customsql testing

# customsql
def test_4500_repo_ins_customsql(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/repo/customsql'
    test_data={ "name" : "test customsql" , "alias" : "application_to_group:1", "sql_query": "select ag.application_id, a.name as application_name, ag.group_id, g.name as group_name from plainbi_application_to_group ag join plainbi_application a on ag.application_id =a.id join plainbi_group g on ag.group_id = g.id" }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["alias"]=="application_to_group:1"



def test_4510_repo_ins_app_to_grp_customsql(test_client):
    global headers
    log.info('TEST: %s',func_name())
    #curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"
    test_url='/api/repo/application_to_group'
    test_data={ "application_id" : -15, "group_id": -3 }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["application_id"]==-15
    assert row1["group_id"]==-3
    
def test_4511_repo_ins_app(test_client):
    global headers
    log.info('TEST: %s',func_name())
    appnam = 'testapp3'
    test_url = '/api/repo/application'
    test_data = {"name" : appnam, "id" : -15  }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["name"]==appnam


def test_4520_repo_compound_get(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/repo/application_to_group/(application_id:-15:group_id:-3)'
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["application_id"]==-15
    assert row1["group_id"]==-3

def test_4521_repo_compound_get_customsql(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/repo/application_to_group/(application_id:-15:group_id:-3)?customsql=application_to_group:1'
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["application_id"]==-15
    assert row1["group_id"]==-3
    assert row1["group_name"]=="testgroup"



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
    test_url='/api/repo/user'
    test_data={ "username" : "testuser", "password_hash" : "testuser123", "role_id" : 2 }
    format_url("put", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    row1=(json_out["data"])[0]
    assert row1["username"]=="testuser"
    testuser_id=row1["id"]

def test_5001_testuser_login(test_client):
    #
    # login with testuser
    global testuser_token, testuser_headers, headers
    log.info('TEST: %s',func_name())
    test_url='/login'
    test_data={ "username" : "testuser", "password":"testuser123" }
    format_url("post", test_url, data=test_data, testname=func_name(),auth=False)
    response = test_client.post(test_url,json=test_data )
    assert response.status_code == 200
    json_out = response.get_json()
    print("got=",json_out)
    testuser_token=json_out["access_token"]
    print("Testuser token=",testuser_token)
    testuser_headers = { 'Authorization': '{}'.format(testuser_token)}
    assert json_out["role"] == "User"


def test_5008_repo_ins_app_to_grp(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/repo/application_to_group'
    test_data={ "application_id" : -10, "group_id": -3 }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
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
    test_url='/api/repo/user_to_group'
    test_data={ "user_id" : testuser_id, "group_id" : -3 }
    format_url("post", test_url, data=test_data, testname=func_name())
    response = test_client.post(test_url, json=test_data, headers=headers)
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
    global headers
    log.info('TEST: %s',func_name())
    appid=-10
    test_url='/api/repo/application/'+str(appid)
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=testuser_headers)
    json_out = response.get_json()
    print("got=",json_out)
    assert response.status_code == 200

def test_5011_repo_get_noapp(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    appid=-11
    test_url='/api/repo/application/'+str(appid)
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=testuser_headers)
    json_out = response.get_json()
    print("got=",json_out)
    assert response.status_code == 204

def test_5020_repo_get_resource(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    global headers
    log.info('TEST: %s',func_name())
    test_url='/api/repo/resources'
    format_url("get", test_url, testname=func_name())
    response = test_client.get(test_url, headers=testuser_headers)
    json_out = response.get_json()
    print("got=",json_out)
    assert response.status_code == 200
    assert json_out["total_count"] == 2


