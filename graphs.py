#!/usr/bin/python3

import sys
import matplotlib.pyplot as plt

# Local

import bisectlib.regression as regression
import bisectlib.plot as bisectplot

def file_in(dir_in, filestem):
	return '{0}/{1}.json'.format(dir_in, filestem)

def file_out(dir_out, count):
	return '{0}/graph{1:03}.png'.format(dir_out, count)

################################################
# Application utils

def print_syntax():
	print('Syntax: graphs <input-file> <output-image>')
	print()
	print('\tPlots a histogram of reverts against distance.')
	print('\t<input-dir>  : a directory containing preprocessed stats files ')
	print('\t               commits.json, lines.json and blocks.json.')
	print('\t<output-dir> : directory to save the output PNGs to, in the form ')
	print('\t               graph000.png, graph001.png, ...')
	print()
	print('Example usage')
	print('\tgraphs stats/c/ ./graphs')

################################################
# Main

if len(sys.argv) != 3:
	print_syntax()
	exit()

# Load the data into memory
dir_in = sys.argv[1]
dir_out = sys.argv[2]
count = 0
degree = 3
negpow = 1
folds = 10
histogram_dpi = 180
regression_dpi = 180

# Commits histogram
print()
print('Generating commits histogram')

data = regression.Data()
data.load_data(file_in(dir_in, 'commits'))

plot = bisectplot.Plot(dpi=histogram_dpi)

plot.addSubplot()
#plot.setTitle('Regression distribution by commits')
plot.setAxes('Distance (normalised commits)', 'Quantity')

plot.addBar(data.x, data.y, 'blue')

plot.save(file_out(dir_out, count))
count += 1

# Lines histogram
print()
print('Generating lines changed histogram')

data = regression.Data()
data.load_data(file_in(dir_in, 'lines'))

plot = bisectplot.Plot(dpi=histogram_dpi)

plot.addSubplot()
#plot.setTitle('Regression distribution by lines changed')
plot.setAxes('Distance (normalised lines changed)', 'Quantity')

plot.addBar(data.x, data.y, 'blue')

plot.save(file_out(dir_out, count))
count += 1

# Blocks histogram
print()
print('Generating blocks changed histogram')

data = regression.Data()
data.load_data(file_in(dir_in, 'blocks'))

plot = bisectplot.Plot(dpi=histogram_dpi)

plot.addSubplot()
#plot.setTitle('Regression distribution by blocks changed')
plot.setAxes('Distance (normalised blocks changed)', 'Quantity')

plot.addBar(data.x, data.y, 'blue')

plot.save(file_out(dir_out, count))
count += 1

# Load the regression data

print()
print('Loading regression data')
data = regression.Data()
data.load_data(file_in(dir_in, 'commits'))
data.scaleData()
data.partition(folds)

learning = data.getLearningSet(0)
learning.scaleData()
validation = data.getValidationSet(0)
validation.scaleData()

# Linear regression
print()
print('Generating linear regression graph')

regfunc = learning.regression_linear(degree - 1)
print('Function: {}'.format(regfunc.toString()))

plot = bisectplot.Plot(dpi=regression_dpi)

plot.addSubplot()
#plot.setTitle('Linear regression')
plot.setAxes('Distance (normalised commits)', 'Frequency')

plot.addScatter(learning.x, learning.y, 'red')
plot.addScatter(validation.x, validation.y, 'black')
ylim = plt.ylim()
plot.addGraph(regfunc, 'blue')
plt.ylim(ylim)

plot.save(file_out(dir_out, count))
count += 1

# Negative power regression
print()
print('Generating negative power regression graph')

regfunc = learning.regresssion_negpow(degree, negpow)
print('Function: {}'.format(regfunc.toString()))

plot = bisectplot.Plot(dpi=regression_dpi)

plot.addSubplot()
#plot.setTitle('Negative power regression')
plot.setAxes('Distance (normalised commits)', 'Frequency')

plot.addScatter(learning.x, learning.y, 'red')
plot.addScatter(validation.x, validation.y, 'black')
ylim = plt.ylim()
plot.addGraph(regfunc, 'blue')
plt.ylim(ylim)

plot.save(file_out(dir_out, count))
count += 1

# Negative power regression
print()
print('Generating exponential polynomial regression graph')

regfunc = learning.regression_exp_poly(degree)
print('Function: {}'.format(regfunc.toString()))

plot = bisectplot.Plot(dpi=regression_dpi)

plot.addSubplot()
#plot.setTitle('Exponential polynomial regression')
plot.setAxes('Distance (normalised commits)', 'Frequency')

plot.addScatter(learning.x, learning.y, 'red')
plot.addScatter(validation.x, validation.y, 'black')
ylim = plt.ylim()
plot.addGraph(regfunc, 'blue')
plt.ylim(ylim)

plot.save(file_out(dir_out, count))
count += 1






