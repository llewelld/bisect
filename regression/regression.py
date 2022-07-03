#!/usr/bin/python3

import math
import numpy as np
import random

# Graph rendering

import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches

# Linear regression

################################################
# Global configuration structure

class PlotConfig:
	rows = 2
	columns = 2
	pos = 1
	fig = plt.figure()
	fontsize = 18
	def add_subplot(self):
		ax = self.fig.add_subplot(self.rows, self.columns, self.pos + 1)
		self.pos += 1
		self.pos = self.pos % (self.rows * self.columns)
		return ax

################################################
# y = f(x) functions

def poly_string(a):
	line = ''

	if len(a) > 2:
		line += '{}x^{}'.format(a[-1], len(a) - 1)

	for j in range(1, len(a) - 2):
		power = len(a) - j - 1
		if a[power] < 0:
			line += " - "
		else:
			line += " + "
		line += '{}x^{}'.format(abs(a[power]), power)
	if len(a) > 1:
		if a[1] < 0:
			line += " - "
		else:
			line += " + "
		line += '{}x'.format(abs(a[1]))
	if len(a) > 0:
		if a[0] < 0:
			line += " - "
		else:
			line += " + "
		line += '{}'.format(abs(a[0]))
	return line

def poly(a, x):
	p = 0
	for j in range(len(a)):
		p += a[j] * x**j
	return p

def fn(a, x):
	y = math.exp(poly(a, x))
	return y

def fn_error(a, x, y):
	e = 0
	for i in range(len(x)):
		yp = fn(a, x[i])
		e += (y[i] - yp)**2
	return e

def fn_error_deriv(a, j, x, y):
	e = 0
	for i in range(len(x)):
		e += (2 * x[i]**j * fn(a, x[i])**2) - (2 * y[i] * x[i]**j * fn(a, x[i]))
	return e

def fn_error_deriv_2(a, j, x, y):
	e = 0
	for i in range(len(x)):
		e += (4 * x[i]**(2 * j) * fn(a, x[i])**2) - (2 * y[i] * x[i]**(2 * j) * fn(a, x[i]))
	return e

################################################
# Convenience output

def print_fn(a):
	print(poly_string(a))

################################################
# Newton-Raphson method to find the zero point

def solve(accuracy, a, j, x, y):
	atest = a.copy()
	yprev = 0
	yval = fn_error_deriv(atest, j, x, y)
	while abs(yval - yprev) > accuracy:
		atest[j] = atest[j] - (fn_error_deriv(atest, j, x, y) / fn_error_deriv_2(atest, j, x, y))
		yprev = yval
		yval = fn_error_deriv(atest, j, x, y)
		#print('Difference: {}'.format(abs(yval - yprev)))
	return atest[j]

################################################
# Graph drawing functions

def draw_graph(config, a):
	xrange = np.linspace(0, 5, 100)
	yvals = [fn(a, x) for x in xrange]

	ax = config.add_subplot()
	ax.set_title('$e^{{ {} }}$'.format(poly_string(a)), fontsize=config.fontsize)
	plt.plot(xrange, yvals, 'g')

def draw_graphs(config, a, atest, polynomial, x, y):
	xrange = np.linspace(0, 5, 100)
	yvals = [fn(a, x) for x in xrange]
	ytest = [fn(atest, x) for x in xrange]

	ax = config.add_subplot()
	ax.set_title('$e^{{ {} }}$'.format(poly_string(a)), fontsize=config.fontsize)
	plt.plot(xrange, yvals, color='g')
	plt.plot(xrange, ytest, color='b')

	ylogvals = [math.exp(yval) for yval in np.poly1d(polynomial)(xrange)]
	plt.plot(xrange, ylogvals, color='orange')
	plt.scatter(x, y, color='black')

def draw_graph_deriv(config, a, j, x, y):
	print('Error for {}: {}'.format(j, fn_error_deriv(a, j, x, y)))
	distance = 2.0 / 10**j
	arange = np.linspace(a[j] - distance, a[j] + distance, 100)

	yvals = []
	atest = a.copy()
	for aval in arange:
		atest[j] = aval
		yval = fn_error_deriv(atest, j, x, y)
		#yval = fn_error(atest, x, y)
		yvals.append(yval)

	ax = config.add_subplot()
	ax.set_title('Error wrt $a_{}$'.format(j), fontsize=config.fontsize)
	plt.plot(arange, yvals, 'r')

	scatterx = [a[j]]
	scattery = [fn_error_deriv(a, j, x, y)]
	plt.scatter(scatterx, scattery, color='black')
	print('Deriv y = {}'.format(scattery[0]))

def draw_graph_error(config, a, j, x, y):
	print('Error for {}: {}'.format(j, fn_error_deriv(a, j, x, y)))
	distance = 0.3**(j + 1)
	arange = np.linspace(a[j] - distance, a[j] + distance, 100)

	yvals = []
	atest = a.copy()
	for aval in arange:
		atest[j] = aval
		yval = fn_error(atest, x, y)
		yvals.append(yval)

	ax = config.add_subplot()
	ax.set_title('Error along $a_{}$'.format(j), fontsize=config.fontsize)
	plt.plot(arange, yvals, 'b')

################################################
# Linear regression

def linear_regression(degree, x, y):
	ylog = [math.log(yval) for yval in y]
	polynomial = np.polyfit(x, ylog, degree)
	return polynomial

################################################
# Main

print('# Calculating')
print()

#random.seed(0)
accuracy_difference = 1E-7
accuracy_total = 1E-10

e = 2.5
a = [2.8, -1.8, 0.3]
print_fn(a)

#x = [1, 2, 3, 4]
x = np.linspace(0.1, 5, 256)

y = []
for xval in x:
	yval = fn(a, xval)
	yval += (2 * random.random() * e) - e
	yval = abs(yval)
	y.append(yval)

polynomial = linear_regression(len(a) - 1, x, y)
apoly = polynomial.tolist()
apoly.reverse()


config = PlotConfig()

atest = apoly.copy()
error = 1.0
while error > accuracy_total:
	error = 0
	for j in range(len(a)):
		atest[j] = solve(accuracy_difference, atest, j, x, y)
		error += abs(fn_error_deriv(atest, j, x, y))
	#print('Total error: {}'.format(error))

for j in range(len(a)):
	draw_graph_deriv(config, atest, j, x, y)

config.pos = 0
draw_graphs(config, a, atest, polynomial, x, y)

print()
print('# Polynomial indices')
print()
print('Ground : {}'.format(a))
print('Linear : {}'.format(apoly))
print('Expone : {}'.format(atest))

print()
print('# Function expressions')
print()
print('Ground f(x) = e^{{{}}}'.format(poly_string(a)))
print('Linear f(x) = e^{{{}}}'.format(poly_string(apoly)))
print('Expone f(x) = e^{{{}}}'.format(poly_string(atest)))


print()
print('# Error comparison')
print()
print('Ground E = {}'.format(fn_error(a, x, y)))
print('Linear E = {}'.format(fn_error(apoly, x, y)))
print('Expone E = {}'.format(fn_error(atest, x, y)))


plt.show()

