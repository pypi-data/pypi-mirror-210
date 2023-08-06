# -*- coding: utf-8 -*-
"""
Created on Sat Feb 18 19:08:04 2023

@author: stefa
"""


import json
import importlib
import sys
import os
import inspect

class ConfigLoader:
    '''
    ConfigLoader enables dynamic imports of equipment interface
    objects based on a configuration file
    '''
    def __init__(self, filename):
        with open(filename) as f:
            self.config = json.load(f)

    def load_class(self, key, **kwargs):
        entry = self.config['equipment'][key]
        if entry['type'] == 'module':
            module = importlib.import_module(entry['import'])
            class_obj = getattr(module, entry['class'])
            combined_args = {**entry.get('args', {}), **kwargs}
            return class_obj(**combined_args)
        elif entry['type'] == 'path':
            module_path = entry['import']
            module_dir = os.path.dirname(module_path)  # extract directory containing module
            sys.path.append(module_dir)  # add directory to sys.path
            module_name = os.path.basename(module_path)
            module = importlib.import_module(module_name)
            class_obj = getattr(module, entry['class'])
            combined_args = {**entry.get('args', {}), **kwargs}
            return class_obj(**combined_args)
        else:
            raise ValueError(f"Unsupported type {entry['type']} for key {key}")
    
    def get_field(self, field):
        return self.config[field]

if __name__ == '__main__':
    a = ConfigLoader('config.json')
    a.load_class()
