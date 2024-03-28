import os
import re

with open("api.py") as f:
    ll=f.readlines()

def get_following_comment(j):
    if (ll[j+1]).strip()=='"""':
        s=""
        k=2
        while ll[j+k].strip()!='"""':
            s+=ll[j+k]
            k+=1
        return s
    return None

def get_route(j):
    k=1
    s=""
    while ll[j-k].strip().startswith("@"):
        s+=ll[j-k]
        k+=1
    return s

def pp_route(a):
    la=a.splitlines()
    s = ""
    for z in la:
        if "token" in z:
            pass
        else:
            b=z
            b=b.replace("@api.route(","")
            b=b.replace("api_root+","/api")
            b=b.replace("repo_api_root+","/api/repo")
            b=b.replace("api_prefix+","/api/crud")
            try:
                p=b.split(",")
                if "GET" in p[1]:
                    m="GET"
                if "PUT" in p[1]:
                    m="PUT"
                if "POST" in p[1]: 
                    m="POST"
                if "DELETE" in p[1]: 
                    m="DELETE"
                s+=m+" "+p[0].replace("'","").replace('"',"")+"\n"
            except:
                print("ASDASD; "+b)
    return s

for i,l in enumerate(ll):
  if re.match("^def.*\:\w*$", l):
     print("===========")
     r=get_route(i)
     if r : 
        print(pp_route(r))
        #print(i,l)
        d=get_following_comment(i)
        if d : 
            #print("-------------")
            print(d)
            #print("-------------")
