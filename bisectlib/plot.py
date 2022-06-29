import numpy as np
import matplotlib.pyplot as plt

class Plot():
	rows = 1
	columns = 1
	pos = 0
	fig = None
	fontsize = 18
	plot = None
	
	def __init__(self, rows = 1, columns = 1, dpi=90):
		self.rows = rows
		self.columns = columns
		self.fig = plt.figure(figsize=(5, 4), dpi=dpi)

	def addSubplot(self):
		self.plot = self.fig.add_subplot(self.rows, self.columns, self.pos + 1)
		self.pos += 1
		self.pos = self.pos % (self.rows * self.columns)
		plt.autoscale(enable=True, axis='x', tight=True)

	def setTitle(self, title):
		self.plot.set_title(title, fontsize=self.fontsize)

	def setAxes(self, xaxis, yaxis):
		self.plot.set_xlabel(xaxis)
		self.plot.set_ylabel(yaxis)

	def addGraph(self, regfunc, colour):
		points = 100
		if regfunc.skipZero():
			xvals = np.linspace(1 / points, 1, points - 1)
		else:
			xvals = np.linspace(0, 1, 100)
		
		yvals = regfunc.applyarray(xvals)
		self.plot.plot(xvals, yvals, color=colour)

	def addScatter(self, x, y, colour, size=4, marker='o'):
		self.plot.scatter(x, y, color=colour, s=size, marker=marker)

	def addLine(self, xvals, yvals, colour):
		self.plot.plot(xvals, yvals, color=colour)

	def addBar(self, x, y, colour):
		plt.bar(x, y, color=colour, width=(-1.0 / len(x)), edgecolor='black', align='edge')

	def addError(self, regfunc, j, data, colour):
		distance = 0.3**(j + 1)
		arange = np.linspace(regfunc.constants[j] - distance, regfunc.constants[j] + distance, 100)

		yvals = []
		atest = regfunc.copy()
		for aval in arange:
			atest.constants[j] = aval
			yval = atest.error(data.x, data.y)
			yvals.append(yval)

		self.addLine(arange, yvals, colour)

	def addErrorDeriv(self, regfunc, j, data, colour):
		distance = 2.0 / 10**j
		arange = np.linspace(regfunc.constants[j] - distance, regfunc.constants[j] + distance, 100)

		yvals = []
		atest = regfunc.copy()
		for aval in arange:
			atest.constants[j] = aval
			yval = atest.errorDeriv(j, data.x, data.y)
			yvals.append(yval)

		self.addLine(arange, yvals, colour)

		scatterx = [regfunc.constants[j]]
		scattery = [regfunc.errorDeriv(j, data.x, data.y)]
		self.addScatter(scatterx, scattery, 'black')
		print('Deriv y = {}'.format(scattery[0]))

	def show(self):
		plt.show()		

	def save(self, file_out):
		plt.tight_layout(pad=2.0, w_pad=0.5)
		plt.savefig(file_out, bbox_inches='tight', transparent=True)

