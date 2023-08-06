# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 19:17:39 2022

@author: stefa
"""
import csv
import sys


def ids_from_col(manifest, column):
    ids = [well[1] for well in manifest if int(well[0][1:len(well[0])]) == column]
    return ids

def time_estimate(manifest):
    all_strains = set()
    time_estimate = 0
    for col in range(1,12,2):
        time_estimate += len(set(ids_from_col(manifest, col)))*75
        all_strains.union(set(ids_from_col(manifest, col)))
    time_estimate += len(all_strains)*45
    return time_estimate

if __name__ == '__main__':
    
    path = sys.argv[1]
    manifest = []
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            manifest.append(row)


print(time_estimate(manifest))