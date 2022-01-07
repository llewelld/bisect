#!/usr/bin/python3

import json
import sys, os
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches

################################################
# File load/save

def load_data(file_in):
	print('Loading data from {}'.format(file_in))
	data = []
	try:
		with open(file_in, 'r') as file_in:
			data = json.load(file_in)
	except Exception:
		print('File {} could not be read'.format(file_in))
	return data

################################################
# Histogram

def create_histogram(ax, data):
	print("\tPlotting histogram")
	bins = 100
	
	values = []
	for stats in data:
		proportion = stats["target"] / stats["distance"]
		values.append(proportion)

	ax.hist(values, bins=bins, color='blue', edgecolor='black')

def create_line(ax, data):
	print("\tPlotting line")

	bins = 100

	x = []
	for pos in range(bins):
		x.append(pos / bins)

	y = [0] * bins
	for stats in data:
		proportion = stats["target"] / stats["distance"]
		pos = math.floor(100 * proportion)
		if pos == bins:
			pos -= 1
		y[pos] += 1

	y2 = [0] * bins
	for pos in range(len(y)):
		#y2[pos] = math.log(y[pos])
		y2[pos] = 1 / y[pos]

	w = []
	for pos in range(len(y)):
		w.append(y[pos])
		#w.append(1)

	model = np.poly1d(np.polyfit(x, y2, 3, w = w))
	print(model)

	yplot = []
	for pos in range(len(y)):
		#yplot.append(math.exp(model(x[pos])))
		yplot.append(1 / model(x[pos]))


	line = np.linspace(0, 1)

	#ax.plot(line, model(line), color='green')
	#ax.plot(x, y2, color='red')

	ax.plot(x, y, color='red')
	ax.plot(x, yplot, color='orange')


def create_plots(figsize, dpi, filename, data):
	print("Plotting graphs")
	fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize, dpi=dpi)

	create_histogram(ax, data)
	create_line(ax, data)

	fig.suptitle("Bisect distances")
	
	ax.set_ylabel("Quantity")
	ax.set_xlabel("Distance")
	ax.autoscale(enable=True, axis='x', tight=True)

	plt.tight_layout(pad=2.0, w_pad=0.5)
	plt.savefig(filename, bbox_inches='tight', transparent=True)

################################################
# Application utils

def print_syntax():
	print('Syntax: graphs <input-file> <output-image>')
	print()
	print('\tPlots a histogram of reverts against distance.')
	print('\t<input-file>   : a preprocessed stats file in json format.')
	print('\t<output-image> : file to save the output png to.')
	print()
	print('Example usage')
	print('\tgraphs stats/c/commits.json out.png')

################################################
# Main

if len(sys.argv) != 3:
	print_syntax()
	exit()

# Load the data into memory
file_in = sys.argv[1]
file_out = sys.argv[2]

data = load_data(file_in)

create_plots((10, 5), 180, file_out, data)



