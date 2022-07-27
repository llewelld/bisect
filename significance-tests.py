#!/usr/bin/python3

import sys
import scipy.stats as stats

# Local

import bisectlib.regression as regression

verbose = True

def output(string = ''):
	if verbose:
		print(string)

################################################
# Application utils

def print_syntax():
	print('Syntax: significance-test [-q] <input-base> <intput-test>')
	print()
	print('\tPerform a Wilcoxon Signed Rank significance test on the two datasets.')
	print('\t[-q]          : only output the results')
	print('\t<input-base>  : a json file containing regressions and bisect steps')
	print('\t                using the standard distance metric.')
	print('\t<input-test>  : a json file containing regressions and bisect steps')
	print('\t                using a weighted distance metric.')
	print()
	print('Example usage')
	print('\tsignificance-test stats/c/commits.json stats/c/commits-weighted.json')

################################################
# Main

if len(sys.argv) == 4:
	if sys.argv[1] == '-q':
		verbose = False
		# Load the data into memory
		file_base = sys.argv[2]
		file_test = sys.argv[3]
	else:
		print_syntax()
		exit()
elif len(sys.argv) == 3:
	# Load the data into memory
	file_base = sys.argv[1]
	file_test = sys.argv[2]
else:
	print_syntax()
	exit()

data_base = regression.Data()
data_base.load_data(file_base)

data_test = regression.Data()
data_test.load_data(file_test)

print()
output('Assuming:')
output('1. Paired data.')
output('2. Not necessarily normal data')
output() 

output('Performing two-sided test')
output()

# Docs: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html
# For z-value: https://github.com/scipy/scipy/issues/2625
# For Wilcoxon Signed-Rank test requirements: https://www.statstest.com/wilcoxon-signed-rank-test/
# For how to report results: https://www.spss-tutorials.com/spss-wilcoxon-signed-ranks-test-simple-example/
# For a nice clear examlpe: https://www.statology.org/wilcoxon-signed-rank-test-python/

statistic, pvalue = stats.wilcoxon(data_base.get_steps(), data_test.get_steps(), alternative='two-sided')
zvalue = abs(stats.norm.ppf(pvalue / 2))

output('Null hypothesis: the data in {} is from the same population as {}'.format(file_base, file_test))
output('Altv hypothesis: the data in {} is not the same as the population as {}'.format(file_base, file_test))
output()

print('Two-sided result for {} and {}'.format(file_base, file_test))
output('Statistic w: {}'.format(statistic))
output('Z-value: {}'.format(zvalue))
output('p-value: {}'.format(pvalue))
print('{:.4g} & {:.4g}'.format(zvalue, pvalue))
print()

if (pvalue < 0.05):
	output('The null hypothesis is rejected at a significance level of 0.05.')
	output()
	output('Performing one-sided test')
	output()

	statistic, pvalue = stats.wilcoxon(data_base.get_steps(), data_test.get_steps(), alternative='greater')
	zvalue = abs(stats.norm.ppf(pvalue / 2))

	output('Null hypothesis: the data in {} shows faster regression detection than {}'.format(file_base, file_test))
	output('Altv hypothesis: the data in {} shows slower regression detection than {}'.format(file_base, file_test))
	output()

	print('One-sided result for {} and {}'.format(file_base, file_test))
	output('Statistic w: {}'.format(statistic))
	output('Z-value: {}'.format(zvalue))
	output('p-value: {}'.format(pvalue))
	print('{:.4g} & {:.4g}'.format(zvalue, pvalue))
	print()
	
	if (pvalue < 0.05):
		output('The null hypothesis is rejected at a significance level of 0.05.')
		output()
		output('The weighted algorithm is significantly faster than the standard bisect aglorithm at a significance level of 0.05')
		output()
		output('A Wilcoxon Signed-Ranks test indicated that the bisect algorithm using a weighted distance metric was faster than the standard bisect algorithm, Z = {}, p = {}.'.format(zvalue, pvalue))
	else:
		output('We cannot reject the null hypothesis at a significance level of 0.05.')

else:
	output('We cannot reject the null hypothesis at a significance level of 0.05.')



