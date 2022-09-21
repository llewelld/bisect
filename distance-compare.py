#!/bin/python3

from http.client import HTTPSConnection, RemoteDisconnected
import json, ssl, time, datetime, sys, re
import subprocess, io, codecs
import shutil, os
import matplotlib.pyplot as plt
import numpy

# Local

import bisectlib.plot as bisectplot

################################################
# File load/save

def save_data(file_out, data):
	result = False
	print('Saving data to {}'.format(file_out))
	try:
		with open(file_out, 'w', encoding='utf-8') as file_out:
			json.dump(data, file_out, ensure_ascii=False, indent=2)
			result = True
	except Exception:
		print('File {} could not be saved'.format(file_out))
	return result

def load_data(file_in):
	data = []
	try:
		with open(file_in, 'r') as file_in:
			data = json.load(file_in)
	except Exception:
		print('File {} could not be read'.format(file_in))
	return data

def load_files(results, directory_in):
	# Load all files from directory_in
	print('Loading JSON files in: '.format(directory_in))
	if os.path.isfile(directory_in):
		split = directory_in.rsplit('/', 1)
		directory_in = split[0]
		files = [split[1]]
	else:
		files = os.listdir(directory_in)
		files.sort()
	for file_in in files:
		if file_in.endswith('.json'):
			data = load_data(directory_in +"/" + file_in)
			results['missing'] += data['missing']
			results['disordered'] += data['disordered']
			results['difference'] += data['difference']
			results['total'] += data['total']
			print()
			print('Loaded: {}'.format(data['title']))
			print('Missing: {}'.format(len(data['missing'])))
			print('Disordered: {}'.format(len(data['disordered'])))
			print('Differences: {}'.format(len(data['difference'])))
			print('Total: {}'.format(data['total']))

################################################
# Analysis

def collect_commits(directory):
	print('Structuring commit data')
	# git log --oneline --pretty="%H"
	result = subprocess.run(['git', 'log', '--oneline', '--pretty=%H'], cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
	commit_order = result.stdout[:-1].split('\n')
	return commit_order

def bisect_distances(directory, commit_order):
	print('Reading bisect distances')
	oldest = commit_order[0]
	newest = commit_order[-1]
	distances = dict()
	midpoint = None
	# git rev-list --bisect-all oldest..newest
	result = subprocess.run(['git', 'rev-list', '--bisect-all', newest + '..' + oldest], cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
	print('Analysing bisect distances')
	nexttime = time.monotonic() + 60;
	total = result.stdout.count('\n')
	for line in result.stdout.split('\n'):
		if (len(line) > 0):
			search = re.search('([0-9a-f]+) \(.*dist=([0-9]+)\)', line)
			commit = search.group(1)
			distance = int(search.group(2))
			distances[commit] = distance
			if not midpoint:
				midpoint = commit
		if time.monotonic() > nexttime:
			print('Progress: {:0.3g}'.format((line / total) * 100))
			nexttime = time.monotonic() + 60;

	return midpoint, distances

def reset_dstances(distances, commit_order, midpoint):
	print('Resetting distance origin')

	middist = distances[midpoint]
	midpos = commit_order.index(midpoint)

	missing = 0
	maxdist = 0
	count = 0
	nexttime = time.monotonic() + 60;
	for commit in distances:
		if commit in commit_order:
			if commit_order.index(commit) > midpos:
				distance = (2 * middist) - distances[commit]
				distances[commit] = distance
				if distance > maxdist:
					maxdist = distance
		else:
			missing += 1
		if time.monotonic() > nexttime:
			print('Progress: {:0.3g}'.format((count / total) * 100))
			nexttime = time.monotonic() + 60;
		count += 1

	return missing, maxdist

def find_missing(results, distances, commit_order):
	print('Finding missing commits')

	count = 0
	nexttime = time.monotonic() + 60;
	for commit in distances:
		if not commit in commit_order:
			results['missing'].append(distances[commit] / maxdist)
		if time.monotonic() > nexttime:
			print('Progress: {:0.3g}'.format((count / total) * 100))
			nexttime = time.monotonic() + 60;
		count += 1

def find_disordered(results, distances, commit_order):
	print('Finding disordered commits')

	missing = 0
	out_of_order = 0
	highest = -1
	count = 0
	nexttime = time.monotonic() + 60;
	for commit in commit_order[:-1]:
		if commit in distances:
			distance = distances[commit]
			difference = distance - commit_order.index(commit)
			results['difference'].append(difference / total)
			if distance < highest:
				out_of_order += 1
				results['disordered'].append(commit_order.index(commit) / total)
			highest = distance
		else:
			results['missing'].append(commit_order.index(commit) / total)
			missing += 1
		if time.monotonic() > nexttime:
			print('Progress: {:0.3g}'.format((count / total) * 100))
			nexttime = time.monotonic() + 60;
		count += 1

	return out_of_order, missing

################################################
# Graph plotting

def plot_disordered_histogram(results, bin_count = 10):
	print()
	print('Generating disordered histogram')

	x = [(x + 0.5) / bin_count for x in range(0, bin_count)]
	y = [0] * bin_count

	for position in results['disordered']:
			bin_pos = int(position * bin_count)
			y[bin_pos] += 1

	y = [count / total for count in y]

	plot = bisectplot.Plot(dpi=180)

	plot.addSubplot()
	plot.setTitle('Distribution of disordered commits')
	plot.setAxes('Commit position', 'Quantity (proportion of commits)')

	plot.addBar(x, y, 'SkyBlue')

	plot.show()

def plot_difference_histogram(results, bin_count = 100):
	# Difference histogram
	print()
	print('Generating difference histogram')

	bin_half = int(bin_count / 2)
	x = [(x + 0.5) / bin_half for x in range(-bin_half, bin_half)]
	y = [0] * bin_count

	for difference in results['difference']:
			bin_pos = int(difference * bin_half) + bin_half
			y[bin_pos] += 1

	y = [count / total for count in y]

	plot = bisectplot.Plot(dpi=180)

	plot.addSubplot()
	plot.setTitle('Distribution of difference')
	plot.setAxes('Difference between commits', 'Quantity (proportion of commits)')

	plot.addBar(x, y, 'SkyBlue')

	plot.show()

################################################
# Application utils

def print_syntax():
	print('Syntax: distance-compare <action> <dir> [output-file]')
	print()
	print('\tAnalyses a local git repository to compare the log order with the ')
	print('\tbisect order.')
	print('\t<action>        : these are exclusive, only one may be used at a time.')
	print('\t                  -a analyse the git repository <dir>.')
	print('\t                  -g render graphs for all json files in <dir>.')
	print('\t<dir>           : either a git repository or a directory ')
	print('\t                  containing previously generated json files.')
	print('\t[output-file]   : json file to output the generated results to.')
	print()
	print('Example usage')
	print('\tdistance-compare -a repo distance-comparison/repo.json')
	print('\tdistance-compare -g distance-comparison')

################################################
# Main

analyse = False
graph = False

if len(sys.argv) < 3:
	print_syntax()
	exit()

directory_in = sys.argv[2]
file_out = None

if sys.argv[1] == '-g':
	graph = True
	if len(sys.argv) != 3:
		print_syntax()
		exit()

if sys.argv[1] == '-a':
	analyse = True
	if len(sys.argv) > 4:
		print_syntax()
		exit()
	if len(sys.argv) == 4:
		file_out = sys.argv[3]

if not analyse and not graph:
	print_syntax()
	exit()
		
title = directory_in.rstrip('/ ').rsplit('/',1)[-1]

results = {
	'title' : title,
	'missing' : [],
	'disordered' : [],
	'difference' : [],
	'total' : 0
}

if graph:
	load_files(results, directory_in)

if analyse:
	# Structuring commit data
	commit_order = collect_commits(directory_in)

	total = len(commit_order) - 1
	results['total'] = total
	print('Total: {}'.format(total))

	# Reading bisect distances
	midpoint, distances = bisect_distances(directory_in, commit_order)

	# Resetting distance origin
	missing_from_order, maxdist = reset_dstances(distances, commit_order, midpoint)

	# Finding missing commits
	find_missing(results, distances, commit_order)

	# Finding disordered commits
	out_of_order, missing_from_commits = find_disordered(results, distances, commit_order)

	missing = missing_from_order + missing_from_commits

missing = len(results['missing'])
out_of_order = len(results['disordered'])
total = results['total']

difference_mean = numpy.mean(results['difference'])
difference_sd = numpy.std(results['difference'])

print()
print('########################################')

print()
print('Total commits: {}'.format(total))
print('Missing commits: {}'.format(missing))
print('Out of order commits: {}'.format(out_of_order))

print()
print('Proportion missing: {:0.3g}%'.format(100 * missing / total))
print('Proportion out of order: {:0.3g}%'.format(100 * out_of_order / total))

print()
print('Difference mean: {}'.format(difference_mean))
print('Difference sd: {}'.format(difference_sd))

if file_out:
	save_data(file_out, results)

# Generating disordered histogram
plot_disordered_histogram(results, 10)

# Generating difference histogram
plot_difference_histogram(results, 100)


