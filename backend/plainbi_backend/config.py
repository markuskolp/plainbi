# -*- coding: utf-8 -*-
"""
Created on Mon May 22 10:57:04 2023

@author: kribbel
"""
import os

class MyConfig:
        pass
    
config = MyConfig()

config.version="0.2 22.05.2023"
config.SECRET_KEY=os.urandom(24)
print("secred key generated")

