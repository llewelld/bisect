#!/usr/bin/python3

import sys
import math
import matplotlib.pyplot as plt

# Local

import bisectlib.regression as regression
import bisectlib.plot as bisectplot

# Linear regression

def decimal(value, width=3):
	order = 0
	if abs(value) > 0:
		order = math.floor(math.log(abs(value), 10)) + 1

	if order >= width:
		template = '{{0:.1f}}'.format()
	elif order > 0:
		template = '{{0:.{}f}}'.format(width - order)
	else:
		template = '{{0:.{}g}}'.format(width)
	string = template.format(value)
	return string

def calculateErrors(learning, validation, acc_diff = 1E-5, acc_total = 1E-20, acc_deriv2 = 1E-4, showPlot = False):
	plot = bisectplot.Plot(1, 3, dpi=180)

	regfuncs = []

	regfunc = learning.regression_linear(degree - 1)
	regfuncs.append(regfunc)

	regfunc = learning.regresssion_negpow(degree, negpow)
	regfuncs.append(regfunc)

	regfunc = learning.regression_exp_poly(degree, acc_diff, acc_deriv2, acc_total)
	regfuncs.append(regfunc)

	errors = []
	names = ['Linear', 'Negpow', 'Exponen']
	coefficients = []
	for pos in range(len(regfuncs)):
		regfunc = regfuncs[pos]

		rootMeanSquareError = regfunc.rootMeanSquareError(validation)
		coefficientOfDetermination = regfunc.coefficientOfDetermination(validation)
		errors.append([rootMeanSquareError, coefficientOfDetermination])
		coefficients += regfunc.constants
		print('{}'.format(names[pos]))
		print('Coefficients detail: {}'.format(regfunc.constants))
		print('Function : {}'.format(regfunc.toString()))
		print('RMSE : {}'.format(rootMeanSquareError))
		print('R2   : {}'.format(coefficientOfDetermination))

		plot.addSubplot()
		plot.setTitle('${}$'.format(regfuncs[pos].toString()))
		plot.addScatter(learning.x, learning.y, 'black')
		plot.addScatter(validation.x, validation.y, 'red')
		ylim = plt.ylim()
		plot.addGraph(regfuncs[pos], 'blue')
		plt.ylim(ylim)

	if showPlot == True:
		#plot.save('temp.png')
		plot.show()
	return errors, coefficients


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

print('# Calculating')
print()

acc_diff = 1E-5
acc_total = 1
acc_deriv2 = 1E-4

errors, coefficients = calculateErrors(data, data, acc_diff, acc_total, acc_deriv2, True)

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
	learning.scaleData(folds / (folds - 1))
	validation = data.getValidationSet(pos)
	validation.scaleData(folds)
	errors, coeffs = calculateErrors(learning, validation, acc_diff, acc_total, acc_deriv2, False)
	linearErrors.append(errors[0])
	negpowErrors.append(errors[1])
	exponeErrors.append(errors[2])
	print()

# Output order is:
#  1. Accuracy difference
#  2. Accuracy total
#  3. Accuracy second derivate
#  4. Linear a1 C
#  5. Linear a2 x
#  6. Linear a3 x^2
#  7. Negpow a1 C
#  8. Negpow a2 x
#  9. Negpow a3 x^2
# 10. Expone a1 C
# 11. Expone a2 x
# 12. Expone a3 x^2

print('Results')
print('{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}'.format(acc_diff, acc_total, acc_deriv2, *coefficients))
print()

# Output order is:
# 1. Linear a3 x^2
# 2. Linear a2 x
# 3. Linear a1 C
# 4. Negpow a3 x^2
# 5. Negpow a2 x
# 6. Negpow a1 C
# 7. Expone a3 x^2
# 8. Expone a2 x
# 9. Expone a1 C

string = ''
string += '{2} & {1} & {0}'.format(decimal(coefficients[0]), decimal(coefficients[1]), decimal(coefficients[2]))
string += ' & '
string += '{2} & {1} & {0}'.format(decimal(coefficients[3]), decimal(coefficients[4]), decimal(coefficients[5]))
string += ' & '
string += '{2} & {1} & {0}'.format(decimal(coefficients[6]), decimal(coefficients[7]), decimal(coefficients[8]))
string += ' \\\\'

print('Coefficients:')
print(string)
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
	string += '{0} & {1}'.format(decimal(averages[pos], 4), decimal(averages[pos + 1], 6))
	if pos < len(averages) - 2:
		string += ' & '
string += ' \\\\'

print('Average errors:')
print(string)
print()

