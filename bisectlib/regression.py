import json
import sys, os
import math
import numpy as np
import itertools

from bisectlib.regfunc import RegFunc

class Data():
	file_in = ''
	data = {}
	x = []
	y = []
	bins = 100
	partitions = []
	steps_x = []
	steps_y = []
	steps_mean = 0
	steps_sd = 0

	def load_data(self, file_in, bins = 100):
		"""File load/save"""
		print('Loading data from {}'.format(file_in))
		self.file_in = file_in
		self.bins = bins
		try:
			with open(file_in, 'r') as file_in:
				self.data = json.load(file_in)
		except Exception:
			print('File {} could not be read'.format(file_in))
		self.generate_points()
		self.generate_steps()

	def generate_points(self):
		"""Convert input data into frequency data"""
		print('Converting input data into frequency data with {} bins'.format(self.bins))
		self.x = []
		for pos in range(self.bins):
			self.x.append((1 + pos) / self.bins)

		self.y = [0] * self.bins
		for stats in self.data:
			proportion = stats["target"] / stats["distance"]
			pos = math.floor(100 * proportion)
			if pos == self.bins:
				pos -= 1
			self.y[pos] += 1

	def generate_steps(self):
		steps = self.get_steps()
		self.steps_x = list(range(max(steps) + 1))
		self.steps_y = [0] * (max(steps) + 1)
		for step in steps:
			self.steps_y[step] += 1
		self.steps_mean = np.mean(steps)
		self.steps_sd = np.std(steps)

	def get_steps(self):
		steps = []
		for commit in self.data:
			steps.append(commit['steps'])
		return steps

	def scaleData(self, factor):
		self.y = [y * factor for y in self.y]

	def partition(self, partitions):
		"""Split the data into partitions for n-fold validation"""
		proportions = []

		for stats in self.data:
			proportions.append(stats["target"] / stats["distance"])

		state = np.random.RandomState(np.random.MT19937(np.random.SeedSequence(9262304)))
		proportions = state.permutation(proportions)

		partitionSize = len(proportions) / partitions

		partitions = []
		
		lower = 0
		upper = partitionSize
		while lower < len(proportions):
			partitions.append(proportions[lower:math.floor(upper)])
			lower = math.floor(upper)
			upper += partitionSize

		total = 0
		for pos in range(len(partitions)):
			total += len(partitions[pos])

		self.partitions = partitions

	def regresssion_negpow(self, degree = 3, negpow = 1):
		result = RegFunc()
		m = degree
		# To create polynom

		A = []
		B = []

		n = len(self.x)

		for j in range(0, m):
			row = []
			for i in range(0, m):
				a = 0
				for k in range(0, n):
					a += self.x[k]**(m - 1 + j - (2 * negpow) - i)
				a /= n
				row.append(a)

			b = 0
			for k in range(0, n):
				b += self.y[k] * (self.x[k]**(j - negpow))
			b /= n
			B.append(b)
			A.append(row)

		A = np.vstack(A)
		#print(A)
		#print(B)

		solution = np.linalg.lstsq(A, B, rcond=None)
		#print('Regression solution (negpow): {}'.format(solution))
		negpowpoly = []
		for aval in solution[0]:
			negpowpoly.append(aval)
		negpowpoly.reverse()

		result.setPoly(degree, negpowpoly, negpow)

		return result

	def regression_linear(self, degree):
		"""Perform a linear regression"""
		polynomial = np.polyfit(self.x, self.y, degree)
		apoly = polynomial.tolist()
		apoly.reverse()
		result = RegFunc()
		result.setPoly(degree, apoly)
		return result

	def regression_linear_log(self, degree):
		"""Perform a linear regression on the logarithm of the y values"""
		ylog = [math.log(yval) if yval > 0 else 1 for yval in self.y]

		w = []
		for pos in range(len(self.y)):
			w.append(self.y[pos])
			#w.append(1)

		polynomial = np.polyfit(self.x, ylog, degree, w = w)
		apoly = polynomial.tolist()
		apoly.reverse()
		result = RegFunc()
		result.setExpPoly(degree, apoly)
		return result

	def regression_reciprocal(self, degree):
		"""Perform a linear regression on the reciprocal of the y values"""
		yrecip = [1 / yval if yval > 0 else 1 for yval in self.y]

		w = []
		for pos in range(len(self.y)):
			w.append(self.y[pos])

		polynomial = np.polyfit(self.x, yrecip, degree, w = w)
		apoly = polynomial.tolist()
		apoly.reverse()
		result = RegFunc()
		result.setRecip(degree, apoly)
		return result

	@staticmethod
	def __poly(a, x):
		p = 0
		for j in range(len(a)):
			p += a[j] * x**j
		return p

	@staticmethod
	def __fn(a, x):
		p = Data.__poly(a, x)
		if p > 300:
		  p = 300
		y = math.exp(p)
		return y

	def __fn_error(self, a):
		e = 0
		for i in range(len(self.x)):
			yp = Data.__fn(a, self.x[i])
			e += (self.y[i] - yp)**2
		return e

	def __fn_error_deriv(self, a, j):
		e = 0
		for i in range(len(self.x)):
			e += (2 * self.x[i]**j * Data.__fn(a, self.x[i])**2) - (2 * self.y[i] * self.x[i]**j * Data.__fn(a, self.x[i]))
		return e

	def __fn_error_deriv_2(self, a, j):
		e = 0
		for i in range(len(self.x)):
			e += (4 * self.x[i]**(2 * j) * Data.__fn(a, self.x[i])**2) - (2 * self.y[i] * self.x[i]**(2 * j) * Data.__fn(a, self.x[i]))
		return e

	def __solve(self, acc_diff, acc_deriv2, a, j):
		atest = a.copy()
		yprev = -10
		yval = self.__fn_error_deriv(atest, j)
		while abs(yval - yprev) > acc_diff and abs(self.__fn_error_deriv_2(atest, j)) > acc_deriv2:
			atest[j] = atest[j] - (self.__fn_error_deriv(atest, j) / self.__fn_error_deriv_2(atest, j))
#			if atest[2] > 100:
#				atest[2] = 100
			yprev = yval
			yval = self.__fn_error_deriv(atest, j)
			#print('Difference: {}'.format(abs(yval - yprev)))
		return atest[j]

	def regression_exp_poly(self, degree, acc_diff = 1E-5, acc_total = 1E-20, acc_deriv2 = 1E-4):
		"""Perform Newton-Raphson to determine the linear regression for an exponentiated polynomial"""
		# Newton-Raphson method to find the zero point

		polynomial = self.regression_linear_log(degree - 1)

		atest = polynomial.constants.copy()
		preverror = 0
		error = 1.0
		while abs(error - preverror) > acc_total:
			preverror = error
			for j in range(degree - 1, -1, -1):
				atest[j] = self.__solve(acc_diff, acc_deriv2, atest, j)
			error = self.__fn_error(atest)
			#print('Error delta: {}'.format(abs(error - preverror)))

		result = RegFunc()
		result.setExpPoly(degree, atest)
		return result

	def getLearningSet(self, fold):
		data = Data()
		data.bins = self.bins
		partition = []
		if len(self.partitions) == 0:
			print('Data must be partitioned first')
		else:
			for pos in range(len(self.partitions)):
				if pos != fold:
					partition += list(self.partitions[pos])

		data.x = []
		for pos in range(data.bins):
			data.x.append((1 + pos) / data.bins)

		data.y = [0] * data.bins
		for stats in partition:
			proportion = stats
			pos = math.floor(100 * proportion)
			if pos == data.bins:
				pos -= 1
			data.y[pos] += 1

		return data

	def getValidationSet(self, fold):
		data = Data()
		data.bins = self.bins
		partition = []
		if len(self.partitions) == 0:
			print('Data must be partitioned first')
		else:
			partition = self.partitions[fold]

		data.x = []
		for pos in range(data.bins):
			data.x.append((1 + pos) / data.bins)

		data.y = [0] * data.bins
		for stats in partition:
			proportion = stats
			pos = math.floor(100 * proportion)
			if pos == data.bins:
				pos -= 1
			data.y[pos] += 1

		return data


