import math

from enum import Enum

class RegFunc():
	class Functype(Enum):
		UNSET = -1
		POLY = 0
		EXPPOLY = 1
		RECIP = 2
		
	functype = Functype.UNSET
	degree = 0
	negpow = 0
	constants = []
	
	def copy(self):
		other = RegFunc()
		other.functype = self.functype
		other.degree = self.degree
		other.negpow = self.negpow
		other.constants = self.constants.copy()
		return other

	def setPoly(self, degree, constants, negpow = 0):
		self.functype = RegFunc.Functype.POLY
		self.degree = degree
		self.negpow = negpow
		self.constants = constants

	def setExpPoly(self, degree, constants):
		self.functype = RegFunc.Functype.EXPPOLY
		self.degree = degree
		self.negpow = 0
		self.constants = constants

	def setRecip(self, degree, constants):
		self.functype = RegFunc.Functype.RECIP
		self.degree = degree
		self.negpow = 0
		self.constants = constants

	def toString(self):
		line = ''
		for j in range(0, len(self.constants)):
			power = len(self.constants) - j - 1
			if power == len(self.constants) - 1:
				val = self.constants[power]
			else:
				val = abs(self.constants[power])
				if self.constants[power] < 0:
					line += " - "
				else:
					line += " + "
			if power - self.negpow == 1:
				line += '{0:.3f}x'.format(abs(val))
			elif power - self.negpow == 0:
				line += '{0:.3f}'.format(abs(val))
			else:
				line += '{0:.3f}x^{{{1}}}'.format(abs(val), power - self.negpow)

		if self.functype is RegFunc.Functype.EXPPOLY:
			line = 'e^{{{}}}'.format(line)
		elif self.functype is RegFunc.Functype.RECIP:
			line = '({})^{{-1}}'.format(line)

		return line

	def skipZero(self):
		return (self.functype is RegFunc.Functype.RECIP)

	def apply(self, x):
		y = 0
		for j in range(len(self.constants)):
			y += self.constants[j] * x**(j - self.negpow)

		if self.functype is RegFunc.Functype.EXPPOLY:
			y = math.exp(y)
		elif self.functype is RegFunc.Functype.RECIP:
			y = 1 / y

		return y
		
	def applyarray(self, xvals):
		return [self.apply(xvals[i]) for i in range(len(xvals))]

	def error(self, x, y):
		e = 0
		for i in range(len(x)):
			yp = self.apply(x[i])
			e += (y[i] - yp)**2
		return e

	def errorDeriv(self, j, x, y):
		e = 0
		if self.functype is RegFunc.Functype.EXPPOLY:
			for i in range(len(x)):
				e += (2 * x[i]**j * self.apply(x[i])**2) - (2 * y[i] * x[i]**j * self.apply(x[i]))
		else:
			print('ERROR: no derivative for not-exponential polynomial functions')
		return e

	def meanAbsoluteError(self, data):
		e = 0
		n = len(data.x)
		for i in range(n):
			yp = self.apply(data.x[i])
			e += abs(data.y[i] - yp)
		e /= n
		return e

	def meanSquareError(self, data):
		e = self.error(data.x, data.y) / len(data.x)
		return e

	def rootMeanSquareError(self, data):
		e = math.sqrt(self.error(data.x, data.y) / len(data.x))
		return e

	def meanAbsolutePercentageError(self, data):
		e = 0
		n = len(data.x)
		for i in range(n):
			yp = self.apply(data.x[i])
			e += abs((data.y[i] - yp) / data.y[i])
		e /= n
		e *= 100
		return e

	def meanPercentageError(self, data):
		e = 0
		n = len(data.x)
		for i in range(n):
			yp = self.apply(data.x[i])
			e += (data.y[i] - yp) / data.y[i]
		e /= n
		e *= 100
		return e

	def coefficientOfDetermination(self, data):
		""" R^2 """
		n = len(data.x)
		e = self.meanSquareError(data)
		
		totalSumSquares = 0
		mean = sum(data.y) / n
		for i in range(n):
			totalSumSquares += (data.y[i] - mean)**2
		e = 1 - (e / totalSumSquares)
		return e

