#!/usr/bin/python3

import sys
import math
import matplotlib.pyplot as plt

# Local

import bisectlib.regression as regression
import bisectlib.plot as bisectplot

# Linear regression

def calculateErrors(learning, validation):
	plot = bisectplot.Plot(1, 3)

	regfuncs = []

	regfunc = learning.regression_linear(degree - 1)
	regfuncs.append(regfunc)

	regfunc = learning.regresssion_negpow(degree, negpow)
	regfuncs.append(regfunc)

	regfunc = learning.regression_exp_poly(degree)
	regfuncs.append(regfunc)

	errors = []
	names = ['Linear', 'Negpow', 'Exponen']
	for pos in range(len(regfuncs)):
		regfunc = regfuncs[pos]

		standardError = regfunc.standardError(validation)
		coefficientOfDetermination = regfunc.coefficientOfDetermination(validation)
		errors.append([standardError, coefficientOfDetermination])
		print('{}'.format(names[pos]))
		print('Coefficients : {2:.3g} & {1:.3g} & {0:.3g}'.format(regfunc.constants[0], regfunc.constants[1], regfunc.constants[2]))
		print('Function : {}'.format(regfunc.toString()))
		print('SE : {}'.format(standardError))
		print('R2 : {}'.format(coefficientOfDetermination))

		plot.addSubplot()
		plot.setTitle('${}$'.format(regfuncs[pos].toString()))
		plot.addScatter(learning.x, learning.y, 'black')
		plot.addScatter(validation.x, validation.y, 'red')
		ylim = plt.ylim()
		plot.addGraph(regfuncs[pos], 'blue')
		plt.ylim(ylim)

	#plot.show()
	return errors


################################################
# Application utils

def print_syntax():
	print('Syntax: regression-nfold.py <input-file>')
	print()
	print('\tPerform n-fold cross-validation regressions.')
	print('\t<input-file>   : a preprocessed stats file in json format.')
	print()
	print('Example usage')
	print('\tregression-nfold.py stats/c/commits.json')

################################################
# Main

degree = 3
negpow = 1

if len(sys.argv) != 2:
	print_syntax()
	exit()

# Load the data into memory
file_in = sys.argv[1]

data = regression.Data()
data.load_data(file_in)
data.scaleData()

print('# Calculating')
print()

calculateErrors(data, data)

print()

print('# Perform n-fold cross-validation')
print()

folds = 10

data.partition(folds)

linearErrors = []
negpowErrors = []
exponeErrors = []

for pos in range(folds):
	print('Fold: {}'.format(pos))
	learning = data.getLearningSet(pos)
	learning.scaleData()
	validation = data.getValidationSet(pos)
	validation.scaleData()
	errors = calculateErrors(learning, validation)
	linearErrors.append(errors[0])
	negpowErrors.append(errors[1])
	exponeErrors.append(errors[2])
	print()

# Output order is:
# 1. Linear standard error
# 2. Linear coefficient of determination
# 3. Negpow standard error
# 4. Negpow coefficient of determination
# 5. Expone standard error
# 6. Expone coefficient of determination

averages = []
averages.append(sum([e[0] for e in linearErrors]) / folds)
averages.append(sum([e[1] for e in linearErrors]) / folds)
averages.append(sum([e[0] for e in negpowErrors]) / folds)
averages.append(sum([e[1] for e in negpowErrors]) / folds)
averages.append(sum([e[0] for e in exponeErrors]) / folds)
averages.append(sum([e[1] for e in exponeErrors]) / folds)

string = ''
for pos in range(0, len(averages), 2):
	string += '{0:.4g} & {1:.6g}'.format(averages[pos], averages[pos + 1])
	if pos < len(averages) - 2:
		string += '& '
string += ' \\\\'

print('Averages:')
print(string)

