# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 16:02:04 2023

@author: stefa
"""

import git
import os
import traceback
import hashlib
import importlib
import inspect

def check_if_committed():
    repo = git.Repo('.')
    uncommitted_changes = repo.is_dirty(untracked_files=True)

    if uncommitted_changes:
        print('There are uncommitted changes in the repository.')
    else:
        print('There are no uncommitted changes in the repository.')

def get_hash(path):
    repo = git.Repo(path)
    current_commit_hash = repo.head.commit.hexsha
    return current_commit_hash


def run_tests():
    directory = "tests"
    exclude_file = "test_utils.py"
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != exclude_file:
            filepath = os.path.join(directory, filename)
            try:
                exec(compile(open(filepath).read(), filepath, 'exec'))
            except Exception as e:
                print(f"Error in {filename}:")
                traceback.print_exc()


def get_dependency_hashes(class_list):
    class_source_hashes = {}

    for cl in class_list:
        source = inspect.getsource(cl)
        source_hash = hashlib.sha256(source.encode()).hexdigest()
        class_source_hashes[cl.__name__] = source_hash
    
    repo = git.Repo(os.getcwd(), search_parent_directories=True)
    repo_hash = repo.head.commit.hexsha
    class_source_hashes['repo_hash'] = repo_hash

    return class_source_hashes



