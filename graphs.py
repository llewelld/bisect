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
	print('Syntax: graphs <input-dir> <output-dir> [count-start]')
	print()
	print('\tPlots a histogram of reverts against distance.')
	print('\t<input-dir>   : a directory containing preprocessed stats files ')
	print('\t                commits.json, lines.json and blocks.json.')
	print('\t<output-dir>  : directory to save the output PNGs to, in the form ')
	print('\t                graph000.png, graph001.png, ...')
	print('\t[count-start] : value to start the output filename enumeration ')
	print('\t                from; defaults to 0.')
	print()
	print('Example usage')
	print('\tgraphs stats/c/ ./graphs')

################################################
# Main

if len(sys.argv) == 3:
	start_count = 0
elif len(sys.argv) == 4 and sys.argv[3].isnumeric():
	start_count = int(sys.argv[3])
else:
	print_syntax()
	exit()

# Load the data into memory
dir_in = sys.argv[1]
dir_out = sys.argv[2]

count = start_count
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

plot.addBar(data.x, data.y, 'SkyBlue')

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

plot.addBar(data.x, data.y, 'SkyBlue')

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
plot.setAxes('Distance (normalised hunks)', 'Quantity')

plot.addBar(data.x, data.y, 'SkyBlue')

plot.save(file_out(dir_out, count))
count += 1

# Load the regression data

print()
print('Loading regression data')
data = regression.Data()
data.load_data(file_in(dir_in, 'commits'))
data.partition(folds)

learning = data.getLearningSet(0)
learning.scaleData(folds / (folds - 1))
validation = data.getValidationSet(0)
validation.scaleData(folds)

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

# Bisect histograms
print()
print('Generating bisect histograms')

data = []
files_in = ['commits', 'commits-weighted', 'lines-weighted', 'blocks-weighted']
for pos in range(4):
	data.append(regression.Data())
	data[pos].load_data(file_in(dir_in, files_in[pos]))

print('Calculating axes limits')
x_max = max(max(item.steps_x) for item in data)
y_max = max(max(item.steps_y) for item in data)

for pos in range(4):
	print('Generating bisect histogram for {}'.format(files_in[pos]))

	plot = bisectplot.Plot(dpi=histogram_dpi)

	plot.addSubplot()
	plot.setAxes("Bisect speed (steps)", "Count")
	plot.setLimits([-0.5, x_max + 0.5], [0, y_max + 1])

	plot.addBar(data[pos].steps_x, data[pos].steps_y, 'SkyBlue', True)
	plot.addMeanSdBars(data[pos].steps_mean, data[pos].steps_sd)

	plot.save(file_out(dir_out, count))
	count += 1


