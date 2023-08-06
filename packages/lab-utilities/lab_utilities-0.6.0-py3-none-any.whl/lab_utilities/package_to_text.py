# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 19:28:02 2023

@author: stefa
"""

import os
import re

class PackageParser:
    def __init__(self, package_path, file_regex=None, dir_regex=None):
        self.package_path = package_path
        self.file_list = []
        self.file_regex = file_regex
        self.dir_regex = dir_regex
        self.output = ''
        self._parse_package()
        
    def _parse_package(self):
        try:
            for root, dirs, files in os.walk(self.package_path):
                if self.dir_regex is not None and not re.search(self.dir_regex, root):
                    del dirs[:]
                    continue
                rel_path = os.path.relpath(root, self.package_path)
                output = os.path.basename(root) + '\n' if rel_path == '.' else rel_path + '\n'
                for file in files:
                    if self.file_regex is not None and not re.search(self.file_regex, file):
                        continue
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            file_content = f.read().strip().split('\n')
                            file_content = [line.strip() for line in file_content if line.strip()]
                            file_content = '\n\t'.join(file_content)
                            output += file + '\n\t' + file_content + '\n'
                        self.file_list.append(file_path)
                    except Exception as e:
                        output += f"\nError reading file {file_path}: {e}"
                self.output += output + '\n'
        except Exception as e:
            self.output += f"\nError walking directory {self.package_path}: {e}"
        

if __name__ == '__main__':
    package_path = "C:\\Users\\stefa\\modular_lab"
    file_regex = r"\.(py|json)$"
    dir_regex = r"^(?!\.git).*$"

    my_parser = PackageParser(package_path, file_regex=file_regex, dir_regex=dir_regex)

    # Access the output and file list attributes
    print(my_parser.output)
    print(my_parser.file_list)

