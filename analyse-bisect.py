#!/usr/bin/python3

import json
import sys, os
import math
from functools import partial

import numpy as np
import matplotlib.pyplot as plt


# Local

import bisectlib.bisect as bisect
from bisectlib.regfunc import RegFunc
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

################################################
# Application utils

def print_syntax():
	print('Syntax: analyse <input-directory> <output-file> <metric> [a1 a2 a3]')
	print()
	print('\tReads in details of commits for different projects and applies the')
	print('\tbisect algorithm to them.')
	print('\t<input-directory> : a directory containing json commit files to perform the bisect algorithm on.')
	print('\t<output-file> : a file to output the results to in json format.')
	print('\t<metric> : one of "commits", "lines" or "blocks".')
	print('\t[a1 a2 a3] : optional exponential polynomial coefficients $e^{a3 x^2 + a2 x + a1}$.')
	print()
	print('Example usage')
	print('\ranalysis results/c/ stats/c/result.json')

################################################
# Main

if len(sys.argv) != 4 and len(sys.argv) != 7:
	print_syntax()
	exit()

# Load the data into memory
directory_in = sys.argv[1]
file_out = sys.argv[2]
metric = sys.argv[3]
coefficients = []
if len(sys.argv) == 7:
	coefficients.append(float(sys.argv[4]))
	coefficients.append(float(sys.argv[5]))
	coefficients.append(float(sys.argv[6]))
print('Coefficients: {}'.format(coefficients))

distance = None
if len(coefficients) > 0:
	regfunc = RegFunc()
	regfunc.setExpPoly(3, coefficients)

if (metric == 'commits'):
	if len(coefficients) > 0:
		distance = bisect.DistanceCommitsRegFunc(regfunc)
	else:
		distance = bisect.DistanceCommits()
elif (metric == 'lines'):
	if len(coefficients) > 0:
		distance = bisect.DistanceLinesRegFunc(regfunc)
	else:
		distance = bisect.DistanceLines()
elif (metric == 'blocks'):
	if len(coefficients) > 0:
		distance = bisect.DistanceBlocksRegFunc(regfunc)
	else:
		distance = bisect.DistanceBlocks()
else:
	print_syntax()
	exit()


# Change the following three lines to change the distance metric used
#regfunc = RegFunc()
#regfunc.setExpPoly(3, [6.727548775284648, 8.607986362473621, -7007.765653854204])
#analyser = bisect.Bisect(bisect.DistanceCommits())
#analyser = bisect.Bisect(bisect.DistanceCommitsRegFunc(regfunc))
#analyser = bisect.Bisect(bisect.DistanceLinesRegFunc(regfunc))
#analyser = bisect.Bisect(bisect.DistanceBlocksRegFunc(regfunc))
analyser = bisect.Bisect(distance)

stats_all = []
count_all = 0
total_all = 0

files = os.listdir(directory_in)
files.sort()
for file_in in files:
	if file_in.endswith('.json'):
		count, total, stats = analyser.analyse(directory_in + '/' + file_in)
		count_all += count
		total_all += total
		stats_all += stats
		if (count > 0):
			print('Average: {}'.format(total / count))
			print('Cummulative average: {}'.format(total_all / count_all))
		else:
			print('No average (count is zero)')		
	else:
		print('Skipping non-JSON file')

average = total_all / count_all
sd = 0
pos = 0
max_steps = 0
for stat in stats_all:
	sd += (stat['steps'] - average)**2
	max_steps = max(max_steps, stat['steps'])
sd = math.sqrt(sd / count_all)

counts = [0] * (max_steps + 1)
for stat in stats_all:
	counts[stat['steps']] += 1

plot = bisectplot.Plot(dpi=180)
plot.addSubplot()
plot.addBar(list(range(max_steps + 1)), counts, 'blue')
plot.addMeanSdBars(average, sd)
plot.setAxes("Bisect speed (steps)", "Count")
#plot.save('temp.png')
plot.show()

print()
save_data(file_out, stats_all)

print()
print('########################################')
print()
print('Total mean: {}'.format(average))
print('Total sd: {}'.format(sd))
print()
print('Combined:')
print('{0:0.3g} & {1:0.3g}'.format(average, sd))


