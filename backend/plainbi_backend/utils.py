# -*- coding: utf-8 -*-
"""
Created on Thu May  4 07:43:34 2023

@author: kribbel
"""

def db_subs_env(s,d):
    if s is None: return None
    for k,v in d.items():
        if v is None:
            s=s.replace("{"+k+"}","")
        else:
            s=s.replace("{"+k+"}",v)
    return s
