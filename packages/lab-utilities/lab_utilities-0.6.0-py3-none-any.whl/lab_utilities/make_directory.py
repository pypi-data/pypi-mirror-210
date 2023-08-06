# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 09:48:03 2023

@author: stefa
"""

import os

def create_directory(name):
    # Create a new directory with the given name
    os.mkdir(name)

    # Create sub-directories called "methods" and "equipment" inside the new directory
    os.mkdir(os.path.join(name, "methods"))
    os.mkdir(os.path.join(name, "equipment"))
