#!/usr/bin/python3

import json
import sys, os
import math
from functools import partial

################################################
# File load/save

def load_data(file_in):
	print('Loading data from {}'.format(file_in))
	data = {'order': [], 'dict': {}}
	try:
		with open(file_in, 'r') as file_in:
			data = json.load(file_in)
	except Exception:
		print('File {} could not be read'.format(file_in))
	return data

def save_data(file_out, data):
	result = False
	print('Saving data from {}'.format(file_out))
	try:
		with open(file_out, 'w', encoding='utf-8') as file_out:
			json.dump(data, file_out, ensure_ascii=False, indent=2)
			result = True
	except Exception:
		print('File {} could not be saved'.format(file_out))
	return result

################################################
# Weight functions

def weight_lines(summary, commits, pos):
	amount = (summary[commits[pos]]["lines_added"] + summary[commits[pos]]["lines_removed"])
	if amount <= 0:
		amount = 1
	return amount

def weight_blocks(summary, commits, pos):
	amount = summary[commits[pos]]["blocks_changed"]
	if amount <= 0:
		amount = 1
	return amount

def weight_files(summary, commits, pos):
	amount = summary[commits[pos]]["files_changed"]
	if amount <= 0:
		amount = 1
	return amount

def weight_commits(pos):
	return 1

def weight_centre(start, base, pos):
	half = (base - start) / 2
	x = pos - start
	y = 1 + math.sqrt(half**2 - (half - x)**2)
	return y

def weight_edges(start, base, pos):
	half = (base - start) / 2
	x = pos - start
	y = 1 + half - math.sqrt(half**2 - (half - x)**2)
	return y

def weight_commits_weighted(start, base, pos):
	weights = [16411, 4758, 2983, 2246, 1705, 1177, 937, 880, 665, 638, 591, 527, 424, 348, 343, 325, 317, 204, 306, 188, 265, 219, 228, 219, 142, 202, 173, 145, 145, 172, 151, 175, 264, 169, 124, 121, 167, 121, 114, 110, 161, 139, 122, 98, 92, 116, 126, 100, 87, 102, 132, 100, 88, 100, 139, 125, 119, 103, 77, 87, 84, 96, 111, 104, 74, 100, 115, 85, 82, 80, 126, 91, 131, 132, 103, 91, 96, 97, 87, 98, 98, 103, 88, 109, 109, 139, 115, 146, 130, 138, 154, 147, 140, 206, 183, 211, 223, 232, 336, 446]
	bucket = math.floor(100 * (pos - start) / (base - start))
	if bucket == 100:
		bucket = 99
	return weights[bucket]

def weight_lines_weighted(start, base, pos):
	weights = [19098, 4323, 2894, 1763, 1470, 1014, 848, 833, 596, 540, 464, 418, 307, 288, 400, 317, 263, 265, 250, 200, 178, 229, 151, 202, 154, 148, 157, 130, 150, 146, 117, 117, 160, 105, 131, 132, 273, 148, 106, 85, 118, 97, 120, 107, 103, 96, 82, 91, 84, 98, 121, 93, 129, 90, 91, 83, 70, 77, 67, 83, 94, 113, 88, 72, 76, 81, 78, 98, 118, 117, 78, 115, 80, 106, 67, 88, 91, 89, 99, 110, 71, 111, 89, 87, 126, 158, 116, 135, 130, 131, 162, 111, 155, 159, 168, 245, 237, 291, 384, 654]
	bucket = math.floor(100 * distances[pos - start] / distances[base - start])
	if bucket == 100:
		bucket = 99
	return weights[bucket]

distance_cache = dict()
amounts = []
distances = []

def compile_weights(summary, commits):
	amounts.clear()
	distance_cache.clear()
	pos = 0
	while pos < len(commits):
		amount = (summary[commits[pos]]["lines_added"] + summary[commits[pos]]["lines_removed"])
		if amount <= 0:
			amount = 1
		amounts.append(amount)
		pos += 1

def compile_sub_weights(start, base):
	distances.clear()
	pos = start
	weight = 0
	while pos <= base:
		distances.append(weight)
		weight += amounts[pos]
		pos += 1

def distance_pre_cached(pos1, pos2):
	distance = 0
	if pos2 < pos1:
		pos1, pos2 = pos2, pos1

	pos = pos1
	end = pos2
	while pos < end:
		distance += amounts[pos]
		pos += 1
	return distance

def weight_commits_regression_reciprocal(start, base, pos):
	a0 =  5.87e-05
	a1 =  0.01464
	a2 =  0.0284
	a3 = -0.0409
	x = (pos - start) / (base - start)
	y = 1.0 / (a0 + (a1 * x) + (a2 * x**2) + (a3 * x**3))
	return y

def weight_commits_regression_exp(start, base, pos):
	a0 =  10.62990157111533
	a1 = -95.85268317640823
	a2 =  91.51901815375584
	x = (pos - start) / (base - start)
	y = math.exp(a0 + (a1 * x) + (a2 * x**2))
	if y < 1:
		y = 1
	return y

def weight_commits_regression_negpow(start, base, pos):
	# Neg power solution: 1128.4465367593393x - 902.1175634932937 + 154.74718385160054x^{-1}
	a0 =  154.74718385160054
	a1 = -902.1175634932937
	a2 =  1128.4465367593393
	x = 0.01 + (pos - start) / (base - start)
	y = (a0 * x**-1) + (a1) + (a2 * x)
	if y < 1:
		y = 1
	return y

def weight_commits_regression_reciprocal2(start, base, pos):
	a0 = -8.365336900135387e-05
	a1 =  0.014393745924285843
	a2 =  0.0064667790807488995
	x = 0.01 + (pos - start) / (base - start)
	y = 1.0 / (a0 + (a1 * x) + (a2 * x**2))
	return y

################################################
# Metrics

def distance(weight, pos1, pos2):
	distance = 0
	if pos2 < pos1:
		pos1, pos2 = pos2, pos1

	pos = pos1
	end = pos2
	while pos < end:
		distance += weight(pos)
		pos += 1
	return distance

def interpolate(weight, pos1, pos2, factor):
	if pos2 < pos1:
		pos1, pos2, factor = pos2, pos1, 1 - factor
	interval = distance(weight, pos1, pos2)
	offset = math.floor(interval * factor + 0.5)
	travelled = 0
	pos = pos1
	while travelled < offset:
		travelled += weight(pos)
		pos += 1
	return pos

def bisect(weight, start, base, target):
	lowest = start
	highest = base
	count = 0
	while highest > target + 1:
		current = interpolate(weight, lowest + 1, highest - 1, 0.5)
		if current == highest:
			current -=1
		else:
			if current == lowest:
				current +=1
		if current < target:
			lowest = current
		else:
			highest = current
		count += 1
	return count

def bisect_basic(start, base, target):
	lowest = start
	highest = base
	count = 0
	while highest > target + 1:
		current = math.floor(((lowest + highest) / 2) + 0.5)
		if current < target:
			lowest = current
		else:
			highest = current
		count += 1
	return count

################################################
# Analysis

def analyse(filein):
	data = load_data(filein)
	count = 0
	total = 0
	stats = []
	if 'order' in data and 'dict' in data:
		commits = data['order']
		summary = data['dict']

		print("Number of commits: {}".format(len(commits)))

		reverts = []
		for commit in commits:
			if summary[commit] and 'reverts' in summary[commit]:
				revert = summary[commit]['reverts']
				base = summary[commit]['base']

				testdata = dict()
				
				if commit in summary and base in summary and revert in summary:
					testdata["start"] = summary[commit]['position']
					testdata["base"] = summary[base]['position']
					testdata["target"] = summary[revert]['position']

					if (testdata["start"] < testdata["target"]) and (testdata["target"] <= testdata["base"]):
						reverts.append(testdata)
					else:
						print("Skipping revert due to inconsistent inequalities")
				else:
					print("Skipping due to missing data")

		#weight = partial(weight_files, summary, commits)
		weight = weight_commits
		progress = 0
		#compile_weights(summary, commits)
		for testdata in reverts:
			#compile_sub_weights(testdata["start"], testdata["base"])
			#weight = partial(weight_commits_weighted, testdata["start"], testdata["base"])
			#weight = partial(weight_lines_weighted, testdata["start"], testdata["base"])
			#weight = partial(weight_commits_regression_exp, testdata["start"], testdata["base"])
			#weight = partial(weight_commits_regression_negpow, testdata["start"], testdata["base"])
			#weight = partial(weight_commits_regression_reciprocal2, testdata["start"], testdata["base"])

			steps = bisect(weight, testdata["start"], testdata["base"], testdata["target"])
			stat = {}
			stat["distance"] = distance(weight, testdata["start"], testdata["base"])
			stat["target"] = distance(weight, testdata["start"], testdata["target"])
			stat["commits"] = testdata["base"] - testdata["start"]
			stat["steps"] = steps
			stats.append(stat)
			total += steps
			count += 1
			progress += 1
			if len(reverts) > 100 and progress % 100 == 0:
				print("Progress {}%".format(round(100 * progress / len(reverts))))
	else:
		print("File contains no data")
	return count, total, stats

################################################
# Application utils

def print_syntax():
	print('Syntax: analyse <input-directory> <output-file>')
	print()
	print('\tReads in details of commits for different projects and applies the')
	print('\tbisect algorithm to them.')
	print('\t<input-directory> : a directory containing json commit files to perform the bisect algorithm on.')
	print('\t<output-file> : a file to output the results to in json format.')
	print()
	print('Example usage')
	print('\ranalysis results/c/ stats/c/result.json')

################################################
# Main

if len(sys.argv) != 3:
	print_syntax()
	exit()

# Load the data into memory
directory_in = sys.argv[1]
file_out = sys.argv[2]

stats_all = []
count_all = 0
total_all = 0

files = os.listdir(directory_in)
files.sort()
for file_in in files:
	if file_in.endswith('.json'):
		count, total, stats = analyse(directory_in +"/" + file_in)
		count_all += count
		total_all += total
		stats_all += stats
		if (count > 0):
			print("Average: {}".format(total / count))
			print("Cummulative average: {}".format(total_all / count_all))
		else:
			print("No average (count is zero)")		
	else:
		print("Skipping non-JSON file")

average = total_all / count_all
print("Total average: {}".format(average))
save_data(file_out, stats_all)

