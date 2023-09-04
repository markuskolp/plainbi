# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 11:40:53 2023

@author: kribbel
"""

import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from plainbi_backend.db import db_exec,get_db_type,sql_select,db_ins,db_upd,db_del,get_item_raw
from json import JSONEncoder, loads

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
"""
import sys
sys.path.insert(0,'C:\\Users\\kribbel\\plainbi\\backend')

log.addHandler(logging.StreamHandler())

repoengine = sqlalchemy.create_engine("sqlite:////Users/kribbel/plainbi_repo.db")
"""

def repo_export_appl(repoengine,id=None,alias=None):
    if id is not None:
        sql=f"select * from plainbi_application where id={id}"
    elif alias is not None:
        sql=f"select * from plainbi_application where alias={alias}"
    else:    
        sql="select * from plainbi_application"
    items,columns,total_count,e=sql_select(repoengine,sql,is_repo=True)
    applist=[]
    for v in items:
        print("------------")
        print("------------")
        app_id=v["id"]
        print("application_id",app_id)
        grpsql=f"select g.name as gruppe,g.alias as gruppe_alias from plainbi_application_to_group ag join plainbi_group g on ag.group_id=g.id where ag.application_id={app_id}"
        grpitems,grpcolumns,grptotal_count,grpe=sql_select(repoengine,grpsql,is_repo=True)
        print("------------")
        v["groups"]=grpitems
        applist.append(v)
    appjson=JSONEncoder(sort_keys=True, indent=4).encode(applist)
    return appjson

def repo_import_appl(repoengine,jsontxt,new_id=None,new_name=None,new_alias=None,generate_id=False,replace=False):
    "importiert ein appl json object"
    log.debug("in repo_import_appl")
    a_tab="application"
    a_plainbitab="plainbi_"+a_tab
    a_pkcols=["id"]
    r = loads(jsontxt)
    a={}
    if new_name is not None:
        a["name"]=new_name
        log.debug("new name %s",new_name)
    else:    
        a["name"]=r["name"]
    if new_alias is not None:
        a["alias"]=new_alias
        log.debug("new alias %s",new_alias)
    else:
        a["alias"]=r["alias"]
    a["datasource_id"]=r["datasource_id"]
    a["spec_json"]=r["spec_json"]
    a_alt=None
    if generate_id:
        sequenz="application"
        log.debug("generate new %s (copy)",a_tab)
    else:
        sequenz=None
        if new_id is not None:
            a["id"]=new_id
            log.debug("new id %s",new_id)
        else:
            a["id"]=r["id"]
            log.debug("keep id %s",new_id)
        # check existing app
        log.debug("check if %s with id %s already exists",a_tab,a["id"])
        r_a_alt = get_item_raw(repoengine,a_plainbitab,a["id"],pk_column_list=a_pkcols,versioned=False,version_deleted=False, is_repo=True, user_id=None, customsql=None)
        log.debug("check returns %s",str(r_a_alt))
        if "data" in r_a_alt.keys():
            if len(r_a_alt["data"])>0:
                a_alt=r_a_alt["data"][0]
                log.debug("%s %s already exists alt=%s",a_tab,a["id"],str(r_a_alt))
    # add new
    if a_alt is None:
        log.debug("add new %s",a_tab)
        # add new application
        r_neu=db_ins(repoengine,a_plainbitab,a,pkcols=a_pkcols,is_versioned=False,seq=sequenz,changed_by=None,is_repo=True, user_id=None, customsql=None)
    else:
        if replace:
            log.debug("update/replace %s with id=%d",a_tab,a["id"])
            r_neu = db_upd(repoengine,a_plainbitab,a["id"],a,pkcols=a_pkcols,is_versioned=False,changed_by=None,customsql=None)
        else:
            log.error("skip %s due to existence and don't overwrite/replace mode",a_tab)
            return
    log.debug("result of insert/update %s",a_tab)
    if "data" in r_neu.keys():
        if len(r_neu["data"])>0:
                a_neu=r_neu["data"][0]
                log.debug("new_id:%s",a_neu["id"])
        else:
            log.error("Error: keine data RÜckgabedaten mit new id")
            return 
    else:
        log.error("Error: keine RÜckgabedaten mit kay data")
        return
    # add to groups
    g_tab="group"
    g_plainbitab="plainbi_"+g_tab
    g_pkcols=["id"]
    ag_tab="application_to_group"
    ag_plainbitab="plainbi_"+ag_tab
    ag_pkcols=["application_id","group_id"]
    for gruppe in r["groups"]:
        # check existing group
        gitems,gcolumns,gtotal_count,ge = sql_select(repoengine,g_plainbitab,order_by=None,offset=None,limit=None,filter=None,with_total_count=False,where_clause="group = '"+gruppe+"'",versioned=False,is_repo=True,user_id=None, customsql=None)
        if len(gitems) > 0:
            g_alt = gitems[0]
        ag_neu={}
        ag_neu["application_id"]=a_neu["id"]
        ag_neu["group_id"]=a_neu["id"]
        # check existence
        r_ag_alt = get_item_raw(repoengine,ag_plainbitab,ag_neu,pk_column_list=ag_pkcols,versioned=False,version_deleted=False, is_repo=True, user_id=None, customsql=None)
        if "data" in r_ag_alt.keys():
            if len(r_ag_alt["data"])>0:
                # record already exists
                print("skip application to group due to existence")
            else:
                r_ag_neu=db_ins(repoengine,ag_plainbitab,ag_neu,pkcols=ag_pkcols,is_versioned=False,seq=None,changed_by=None,is_repo=True, user_id=None, customsql=None)
                if "data" in r_ag_neu.keys():
                    if len(r_ag_neu["data"])>0:
                        print("inserted")
    return

def repo_export_adhoc(repoengine,id=None,alias=None):
    if id is not None:
        sql=f"select * from plainbi_adhoc where id={id}"
    elif alias is not None:
        sql=f"select * from plainbi_adhoc where alias={alias}"
    else:    
        sql="select * from plainbi_adhoc"
    items,columns,total_count,e=sql_select(repoengine,sql,is_repo=True)
    adhoclist=[]
    for v in items:
        print("------------")
        print("------------")
        adhoc_id=v["id"]
        print("adhoc_id",adhoc_id)
        grpsql=f"select g.name as gruppe,g.alias as gruppe_alias from plainbi_adhoc_to_group ag join plainbi_group g on ag.group_id=g.id where ag.adhoc_id={adhoc_id}"
        grpitems,grpcolumns,grptotal_count,grpe=sql_select(repoengine,grpsql,is_repo=True)
        print("------------")
        v["groups"]=grpitems
        adhoclist.append(v)
    adhocjson=JSONEncoder(sort_keys=True, indent=4).encode(v)
    print(adhocjson)
    return adhocjson

def repo_import_adhoc(repoengine,jsontxt,new_id=None,new_name=None,new_alias=None,generate_id=False,replace=False):
    "importiert ein adhoc json object"
    log.debug("in repo_import_adhoc")
    a_tab="adhoc"
    a_plainbitab="plainbi_"+a_tab
    a_pkcols=["id"]
    r = loads(jsontxt)
    a={}
    if new_name is not None:
        a["name"]=new_name
        log.debug("new name %s",new_name)
    else:    
        a["name"]=r["name"]
    if new_alias is not None:
        a["alias"]=new_alias
        log.debug("new alias %s",new_alias)
    else:
        a["alias"]=r["alias"]
    a["datasource_id"]=r["datasource_id"]
    a["sql_query"]=r["sql_query"]
    a["output_format"]=r["output_format"]
    a["owner_user_id"]=r["owner_user_id"]
    a_alt=None
    if generate_id:
        sequenz="adhoc"
        log.debug("generate new %s (copy)",a_tab)
    else:
        sequenz=None
        if new_id is not None:
            a["id"]=new_id
            log.debug("new id %s",new_id)
        else:
            a["id"]=r["id"]
            log.debug("keep id %s",new_id)
        # check existing app
        log.debug("check if %s with id %s already exists",a_tab,a["id"])
        r_a_alt = get_item_raw(repoengine,a_plainbitab,a["id"],pk_column_list=a_pkcols,versioned=False,version_deleted=False, is_repo=True, user_id=None, customsql=None)
        log.debug("check returns %s",str(r_a_alt))
        if "data" in r_a_alt.keys():
            if len(r_a_alt["data"])>0:
                a_alt=r_a_alt["data"][0]
                log.debug("%s %s already exists alt=%s",a_tab,a["id"],str(r_a_alt))
    # add new
    if a_alt is None:
        log.debug("add new %s",a_tab)
        # add new application
        r_neu=db_ins(repoengine,a_plainbitab,a,pkcols=a_pkcols,is_versioned=False,seq=sequenz,changed_by=None,is_repo=True, user_id=None, customsql=None)
    else:
        if replace:
            log.debug("update/replace %s with id=%d",a_tab,a["id"])
            r_neu = db_upd(repoengine,a_plainbitab,a["id"],a,pkcols=a_pkcols,is_versioned=False,changed_by=None,customsql=None)
        else:
            log.error("skip %s due to existence and don't overwrite/replace mode",a_tab)
            return
    log.debug("result of insert/update %s",a_tab)
    if "data" in r_neu.keys():
        if len(r_neu["data"])>0:
                a_neu=r_neu["data"][0]
                log.debug("new_id:%s",a_neu["id"])
        else:
            log.error("Error: keine data RÜckgabedaten mit new id")
            return 
    else:
        log.error("Error: keine RÜckgabedaten mit kay data")
        return
    # add to groups
    g_tab="group"
    g_plainbitab="plainbi_"+g_tab
    g_pkcols=["id"]
    ag_tab="adhoc_to_group"
    ag_plainbitab="plainbi_"+ag_tab
    ag_pkcols=["adhoc_id","group_id"]
    for gruppe in r["groups"]:
        # check existing group
        gitems,gcolumns,gtotal_count,ge = sql_select(repoengine,g_plainbitab,order_by=None,offset=None,limit=None,filter=None,with_total_count=False,where_clause="group = '"+gruppe+"'",versioned=False,is_repo=True,user_id=None, customsql=None)
        if len(gitems) > 0:
            g_alt = gitems[0]
        ag_neu={}
        ag_neu["application_id"]=a_neu["id"]
        ag_neu["group_id"]=a_neu["id"]
        # check existence
        r_ag_alt = get_item_raw(repoengine,ag_plainbitab,ag_neu,pk_column_list=ag_pkcols,versioned=False,version_deleted=False, is_repo=True, user_id=None, customsql=None)
        if "data" in r_ag_alt.keys():
            if len(r_ag_alt["data"])>0:
                # record already exists
                print("skip application to group due to existence")
            else:
                r_ag_neu=db_ins(repoengine,ag_plainbitab,ag_neu,pkcols=ag_pkcols,is_versioned=False,seq=None,changed_by=None,is_repo=True, user_id=None, customsql=None)
                if "data" in r_ag_neu.keys():
                    if len(r_ag_neu["data"])>0:
                        print("inserted")
    return
