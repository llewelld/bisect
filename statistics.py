#!/usr/bin/python3

import json
import sys, os
import math

################################################
# File load/save

def load_data(file_in):
	data = []
	try:
		with open(file_in, 'r') as file_in:
			data = json.load(file_in)
	except Exception:
		print('File {} could not be read'.format(file_in))
	return data

################################################
# Analysis

def analyse(name, data):
	print("Statistics for: {}".format(name))
	count = 0
	sum_linear = 0
	for stats in data:
		sum_linear += stats["steps"]
		count += 1
	
	if count > 0:
		mean = sum_linear / count

		sum_squared = 0
		for stats in data:
			sum_squared += (stats["steps"] - mean)**2
		
		standard_deviation = math.sqrt(sum_squared / count)

		print("\tMean: {}".format(mean))
		print("\tSD:   {}".format(standard_deviation))
	else:
		print("\tNo entries")

	buckets = 100
	bucket_list = [0] * buckets
	for stats in data:
		bucket = math.floor(buckets * stats["target"] / stats["distance"])
		if bucket == buckets:
			bucket -= 1
		bucket_list[bucket] += 1
	
	print("\tBuckets:")
	print("\t", end='')
	for pos in range(buckets):
		print("{}".format(bucket_list[pos]), end='')
		if pos != buckets - 1:
			print(", ", end='')

	print()

################################################
# Application utils

def print_syntax():
	print('Syntax: statistics <input-directory>')

################################################
# Main

if len(sys.argv) != 2:
	print_syntax()
	exit()

# Load the data into memory
directory_in = sys.argv[1]

files = os.listdir(directory_in)
files.sort()
for file_in in files:
	if file_in.endswith('.json'):
		data = load_data(directory_in +"/" + file_in)
		name = file_in[:-5]
		analyse(name, data)




