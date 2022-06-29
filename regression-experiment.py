#!/usr/bin/python3

import sys
import math

# Local

import bisectlib.regression as regression
import bisectlib.plot as bisectplot

# Linear regression

################################################
# Graph drawing functions

def draw_graph(plot, regfunc):
	plot.addSubplot()
	plot.setTitle('${}$'.format(regfunc.toString()))
	plot.addGraph(regfunc, 'green')

def draw_graphs(plot, regfuncs, x, y):
	colours = ['blue', 'orange', 'green']
	if len(regfuncs) > 0 and len(regfuncs) < len(colours):
		plot.addSubplot()
		plot.setTitle('${}$'.format(regfuncs[0].toString()))
		for pos in range(len(regfuncs)):
			plot.addGraph(regfuncs[pos], colours[pos])
		plot.addScatter(x, y, 'black')
	else:
		print('Cannot display {} graphs'.format(len(regfuncs)))

def draw_graph_deriv(plot, a, j, data):
	print('Error for {}: {}'.format(j, a.errorDeriv(j, data.x, data.y)))
	plot.addSubplot()
	plot.setTitle('Error wrt $a_{}$'.format(j))
	plot.addErrorDeriv(a, j, data, "red")

def draw_graph_error(plot, a, j, data):
	print('Error for {}: {}'.format(j, a.errorDeriv(j, data.x, data.y)))
	plot.addSubplot()
	plot.setTitle('Error along $a_{}$'.format(j))
	plot.addError(a, j, data, "blue")

################################################
# Application utils

def print_syntax():
	print('Syntax: regression-experiment.py <type> <input-file>')
	print()
	print('\tPerforms an exponential regression using data from the file provided.')
	print('\t<type>         : the type of regression to perform. One of:')
	print('\t                 exp    : exponential polynomial regression ')
	print('\t                 deriv  : exp poly regression with derivative graphs')
	print('\t                 error  : exp poly regression with error graphs')
	print('\t                 negpow : negative power regression')
	print('\t<input-file>   : a preprocessed stats file in json format.')
	print()
	print('Example usage')
	print('\tregression-experiment.py exp stats/c/commits.json')

################################################
# Main

degree = 3
negpow = 1

if len(sys.argv) != 3:
	print_syntax()
	exit()

# Load the data into memory
regressionType = sys.argv[1]
file_in = sys.argv[2]

if regressionType not in ["exp", "deriv", "error", "negpow"]:
	print_syntax()
	exit()

data = regression.Data()
data.load_data(file_in)

print('# Calculating frequencies')
print()

print('x values: {}'.format(data.x))
print()
print('y values: {}'.format(data.y))
print()

print('# Calculating')
print()

result = None
name = ""
ytest = []
plot = None

if regressionType in ["deriv", "error"]:
	plot = bisectplot.Plot(2, 3)
else:
	plot = bisectplot.Plot()

if regressionType in ["exp", "deriv", "error"]:
	name = "Expone"
	accuracy_difference = 1E-5
	accuracy_total = 1E-20

	## TODO: check degree - 1
	polynomial = data.regression_linear_log(degree - 1)

	result = data.regression_exp_poly(degree)

	for x in range(len(data.y)):
		xpos = 0.01 + x / 100
		ypos = int(math.ceil(result.apply(xpos)))
		ytest.append(ypos)
elif regressionType in ["negpow"]:
	name = "Negpow"
	result = data.regresssion_negpow(degree, negpow)
	print('Neg power solution: {}'.format(result.toString()))

	polynomial = data.regression_linear_log(degree - negpow)

	for i in range(len(data.y)):
		ytest.append(round(result.apply(data.x[i])))

print(polynomial.constants)
draw_graphs(plot, [result, polynomial], data.x, data.y)
#draw_graph(plot, polynomial)

if regressionType in ["deriv", "error"]:
	for j in range(degree):
		if regressionType == "deriv":
			draw_graph_deriv(plot, result, j, data)
		else:
			draw_graph_error(plot, result, j, data)

print()
print('# Polynomial indices')
print()
print('Linear : {}'.format(polynomial.constants))
print('{} : {}'.format(name, result.constants))

print()
print('# Function expressions')
print()
print('Linear f(x) = {}'.format(polynomial.toString()))
print('{} f(x) = {}'.format(name, result.toString()))


print()
print('# Error comparison')
print()
print('Linear E = {}'.format(polynomial.error(data.x, data.y)))
print('{} E = {}'.format(name, result.error(data.x, data.y)))

print()
print('# Value comparison')
print()

line1 = ''
line2 = ''
for i in range(len(data.y)):
	line1 += '{:5}'.format(data.y[i])
	line2 += '{:5}'.format(ytest[i])
	if ((i + 1) % 10 == 0) or i == len(data.y) - 1:
		print(line1)
		print(line2)
		print()
		line1 = ''
		line2 = ''
	else:
		line1 +=', '
		line2 +=', '

plot.show()

