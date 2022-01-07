#!/usr/bin/python3

import json
import sys, os
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
	rows = 1
	columns = 1
	pos = 1
	fig = plt.figure()
	fontsize = 18
	def add_subplot(self):
		ax = self.fig.add_subplot(self.rows, self.columns, self.pos + 1)
		self.pos += 1
		self.pos = self.pos % (self.rows * self.columns)
		return ax

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
# Convert input data into frequency data

def generate_points(data):
	bins = 100

	x = []
	for pos in range(bins):
		x.append(0.01 + pos / bins)

	y = [0] * bins
	for stats in data:
		proportion = stats["target"] / stats["distance"]
		pos = math.floor(100 * proportion)
		if pos == bins:
			pos -= 1
		y[pos] += 1

	return (x, y)

################################################
# y = f(x) functions

def poly_string(a, d = 0):
	line = ''

	for j in range(0, len(a)):
		power = len(a) - j - 1
		if power == len(a) - 1:
			val = a[power]
		else:
			val = abs(a[power])
			if a[power] < 0:
				line += " - "
			else:
				line += " + "
		if power - d == 1:
			line += '{}x'.format(abs(val))
		elif power - d == 0:
			line += '{}'.format(abs(val))
		else:
			line += '{}x^{{{}}}'.format(abs(val), power - d)
	return line

def poly(a, x, d = 0):
	p = 0
	for j in range(len(a)):
		p += a[j] * x**(j - d)
	return p

def fn(a, x, d = 0):
	y = poly(a, x, d)
	return y

def fn_error(a, x, y, d = 0):
	e = 0
	for i in range(len(x)):
		yp = fn(a, x[i], d)
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

def print_fn(a, d = 0):
	print(poly_string(a, d))

################################################
# Newton-Raphson method to find the zero point

def solve(accuracy, a, j, x, y):
	atest = a.copy()
	yprev = -10
	yval = fn_error_deriv(atest, j, x, y)
	while abs(yval - yprev) > accuracy and fn_error_deriv_2(atest, j, x, y) != 0:
		atest[j] = atest[j] - (fn_error_deriv(atest, j, x, y) / fn_error_deriv_2(atest, j, x, y))
		yprev = yval
		yval = fn_error_deriv(atest, j, x, y)
		#print('Difference: {}'.format(abs(yval - yprev)))
	return atest[j]

def solve_step(a, j, x, y):
	aj = a[j]
	aj = aj - (fn_error_deriv(a, j, x, y) / fn_error_deriv_2(a, j, x, y))
	return aj

################################################
# Graph drawing functions

def draw_graph(config, a):
	xrange = np.linspace(0, 1, 100)
	yvals = [fn(a, x) for x in xrange]

	ax = config.add_subplot()
	ax.set_title('$e^{{ {} }}$'.format(poly_string(a)), fontsize=config.fontsize)
	plt.plot(xrange, yvals, 'g')

def draw_graphs(config, negpow, d, polynomial, x, y):
	xrange = np.linspace(0, 1, 100)
	yvals = [poly(negpow, x[i], d) for i in range(len(x))]

	ax = config.add_subplot()
	ax.set_title('${}$'.format(poly_string(negpow, d)), fontsize=config.fontsize)
	plt.plot(xrange, yvals, color='g')

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

	w = []
	for pos in range(len(y)):
		w.append(y[pos])
		#w.append(1)

	polynomial = np.polyfit(x, ylog, degree, w = w)
	return polynomial

################################################
# Application utils

def print_syntax():
	print('Syntax: regression-from-data <input-file>')
	print()
	print('\tPerforms an exponential regression using data from the file provided.')
	print('\t<input-file>   : a preprocessed stats file in json format.')
	print()
	print('Example usage')
	print('\regression-from-data stats/c/commits.json')

################################################
# Main

if len(sys.argv) != 2:
	print_syntax()
	exit()

# Load the data into memory
file_in = sys.argv[1]

data = load_data(file_in)

print('# Calculating frequencies')
print()

x, y = generate_points(data)
print('x values: {}'.format(x))
print()
print('y values: {}'.format(y))
print()

print('# Calculating')
print()

degree = 3
m = degree
d = 1
# To create polynom

A = []
B = []

n = len(x)

for j in range(0, m):
	row = []
	for i in range(0, m):
		a = 0
		for k in range(0, n):
			a += x[k]**(m - 1 + j - (2 * d) - i)
		a /= n
		row.append(a)

	b = 0
	for k in range(0, n):
		b += y[k] * (x[k]**(j - d))
	b /= n
	B.append(b)
	A.append(row)

A = np.vstack(A)
print(A)
print(B)

solution = np.linalg.lstsq(A, B, rcond=None)
print('Solution: {}'.format(solution))
negpowpoly = []
for aval in solution[0]:
	negpowpoly.append(aval)
negpowpoly.reverse()

print('Neg power solution: {}'.format(poly_string(negpowpoly ,d)))




##random.seed(0)
#accuracy_difference = 1E-5
#accuracy_total = 1E-20

polynomial = linear_regression(degree - 1, x, y)
apoly = polynomial.tolist()
apoly.reverse()

print(apoly)

config = PlotConfig()

#atest = apoly.copy()
#preverror = 0
#error = 1.0
#while abs(error - preverror) > accuracy_total:
#	preverror = error
#	for j in range(degree):
#		atest[j] = solve(accuracy_difference, atest, j, x, y)
#	error = fn_error(atest, x, y)
#	#print('Error delta: {}'.format(abs(error - preverror)))

#for j in range(degree):
#	draw_graph_deriv(config, atest, j, x, y)

config.pos = 0
draw_graphs(config, negpowpoly, d, polynomial, x, y)

print()
print('# Polynomial indices')
print()
print('Linear : {}'.format(apoly))
print('Negpow : {}'.format(negpowpoly))

print()
print('# Function expressions')
print()
print('Linear f(x) = e^{{{}}}'.format(poly_string(apoly)))
print('Negpow f(x) = e^{{{}}}'.format(poly_string(negpowpoly, d)))

print()
print('# Error comparison')
print()
print('Linear E = {}'.format(fn_error(apoly, x, y)))
print('Negpow E = {}'.format(fn_error(negpowpoly, x, y, d)))

print()
print('# Value comparison')
print()

commits = y

line1 = ''
line2 = ''
for i in range(len(commits)):
	line1 += '{:5}'.format(commits[i])
	line2 += '{:5}'.format(round(poly(negpowpoly, x[i], d)))
	if ((i + 1) % 10 == 0) or i == len(commits) - 1:
		print(line1)
		print(line2)
		print()
		line1 = ''
		line2 = ''
	else:
		line1 +=', '
		line2 +=', '


plt.show()

