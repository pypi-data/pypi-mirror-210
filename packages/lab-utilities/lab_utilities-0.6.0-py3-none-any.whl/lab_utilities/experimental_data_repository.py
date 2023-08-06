# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 14:24:20 2022

@author: stefa
"""
from datetime import datetime as dt
import os
import re
import json
import shutil

class ExperimentalDataHandler:
    
    def __init__(self, data_repository, new_experiment, method_name, 
                 params_dir, experiment_fields = 'experiment_fields.json'):
        
        self.data_repository = data_repository
        self.method_name = method_name
        self.roboid = os.environ['roboid']
        
        self.experiment_fields = experiment_fields
        self.params_path = os.path.join(params_dir, 'experimental_params.json')
        
        if new_experiment:
            path = self.create_experimental_config()
        else:
            path = self.pull_experimental_config()
        
        self.experiment_path = path


    def create_experimental_config(self):
        """
        Gets experimental params from user input and writes these to the file
        self.params_file_name
        """
        self.define_experimental_params()
        
        with open(self.params_path, 'w') as fp:
            json.dump(self.experimental_params, fp)
        
        exp_dir_path = self.get_experiment_directory()
        shutil.copy(self.params_path, exp_dir_path)
        return exp_dir_path
    
    def define_experimental_params(self):
        ''' 
        Returns a dictionary of experimental parameters based on user inputs
        '''
        experimental_params_dict = {}
        
        experimental_params_dict.update({'Method_Name': self.method_name})
        experimental_params_dict.update({'Robot_ID': self.roboid})
        
        user_name = input("\n\n\nRunning " + self.method_name + "\n\n\n\nWhat is your name?: ")
        experimental_params_dict.update({'Username': user_name})
        
        experiment_name = input("Please provide a unique name for your experiment: ")
        experimental_params_dict.update({'Experiment_Name': experiment_name})
        
        experiment_desc = input("(Optional) Feel free to provide a description for your experiment: ")
        experimental_params_dict.update({'Experiment_Desc': experiment_desc})
        
        timestamp = str(dt.now())
        experimental_params_dict.update({'Timestamp': timestamp})
        
        with open(self.experiment_fields, 'r') as f:
            prompts = json.load(f)

        for prompt in prompts:
            parameter = input(prompt['prompt'] + ': ')
            if parameter:
                experimental_params_dict.update({prompt['field']: int(parameter)})
            else:
                try:
                    experimental_params_dict.update({prompt['field']: prompt['default']})
                except KeyError:
                    raise Exception("No default setting for this field")
        
        self.experimental_params = experimental_params_dict


    def pull_experimental_config(self):
        with open(self.params_path, 'r') as fp:
            self.experimental_params = json.load(fp)
        exp_dir_path = self.get_experiment_directory()
        return exp_dir_path
    
    def get_experiment_directory(self):
        '''
        Creates a directory for the experimental data if it does not already
        exist, and returns the directory path
        '''
        
        user = self.experimental_params['Username']
        exp_name = self.experimental_params['Experiment_Name']
        timestamp = self.experimental_params['Timestamp']
        method_name = self.experimental_params['Method_Name']
        robot_id_num = self.experimental_params['Robot_ID']
        
        user_dir = os.path.join(self.data_repository, user + '_Robot_Experiments')
        user_method_dir = os.path.join(user_dir, method_name)
        dir_string = timestamp.split(' ')[0]
        dir_string = re.sub('-', '', dir_string)
        dir_string = dir_string + '_' + exp_name + '_' + robot_id_num
        
        experiment_dir = os.path.join(user_method_dir, dir_string)
        if not os.path.exists(experiment_dir):
            os.makedirs(experiment_dir, exist_ok=True) 
            
        return experiment_dir
    
    def get_user_email(self, user):
        emails_json = os.path.join(self.data_repository, 'user_emails.json')
        print(self.data_repository)
        with open(emails_json, 'r') as fp:
            emails = json.load(fp)
        user_email = emails[user]
        return user_email
    
    def get_experimental_params(self):
        return self.experimental_params
    
    def write_json_to_dir(self, data, fn):
        file_path = os.path.join(self.experiment_path, fn)
        with open(file_path, 'w') as f:
            # write the dictionary to the JSON file
           json.dump(data, f)

        