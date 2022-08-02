import json
import math

from bisectlib.regfunc import RegFunc

################################################
# Weight classes

class Distance:
	"""
	Distance calculation base class
	"""
	start = 0
	base = 0

	def __init__(self):
		pass

	def compile_weights(self, summary, commits):
		pass

	def compile_sub_weights(self, start, base):
		self.start = start
		self.base = base

	def weight(self, commit):
		return 1

	def distance(self, commit1, commit2):
		distance = 0
		if commit2 < commit1:
			commit1, commit2 = commit2, commit1

		pos = commit1
		end = commit2
		while pos < end:
			distance += self.weight(pos)
			pos += 1
		return distance

class DistanceCached(Distance):
	"""
	Distance calculation base class with caching for reducing calculation time
	"""
	weights = []
	distances = []
	start = 0
	base = 0
	summary = {}
	commits = {}

	def compile_weights(self, summary, commits):
		self.summary = summary
		self.commits = commits
		pass

	def compile_sub_weights(self, start, base):
		self.start = start
		self.base = base
		self.distances.clear()
		pos = start
		weight = 0
		while pos <= base:
			self.distances.append(weight)
			weight += self.weight(pos)
			pos += 1

	def distance(self, commit1, commit2):
		distance = 0
		if commit2 < commit1:
			commit1, commit2 = commit2, commit1
		return self.distances[commit2 - self.start] - self.distances[commit1 - self.start]


class DistanceCommits(DistanceCached):
	"""
	Distance calculation using number of commits as the distance metric
	"""
	pass

class DistanceLines(Distance):
	"""
	Distance calculation using number of lines changed as the distance metric
	"""
	summary = {}
	commits = {}

	def compile_weights(self, summary, commits):
		self.summary = summary
		self.commits = commits
		pass

	def weight(self, pos):
		amount = (self.summary[self.commits[pos]]["lines_added"] + self.summary[self.commits[pos]]["lines_removed"])
		if amount <= 0:
			amount = 1
		return amount

class DistanceBlocks(Distance):
	"""
	Distance calculation using number of changed hunks as the distance metric
	"""
	summary = {}
	commits = {}

	def compile_weights(self, summary, commits):
		self.summary = summary
		self.commits = commits

	def weight(self, pos):
		amount = self.summary[self.commits[pos]]["blocks_changed"]
		if amount <= 0:
			amount = 1
		return amount


class DistanceFiles(Distance):
	"""
	Distance calculation using number of files changed as the distance metric
	"""
	summary = {}
	commits = {}

	def compile_weights(self, summary, commits):
		self.summary = summary
		self.commits = commits

	def weight(self, pos):
		amount = self.summary[self.commits[pos]]["files_changed"]
		if amount <= 0:
			amount = 1
		return amount

class DistanceCommitsRegFunc(DistanceCached):
	"""
	Distance calculation using number of commits as the distance metric,
	weighted using the function provided at initialisation
	"""
	regfunc = None
	def __init__(self, regfunc):
		self.regfunc = regfunc

	def weight(self, commit):
		x = (commit - self.start) / (self.base - self.start)
		y = self.regfunc.apply(x)
		if y < 1:
			y = 1
		return y

class DistanceLinesRegFunc(DistanceCached):
	"""
	Distance calculation using number of lines changed as the distance metric,
	weighted using the function provided at initialisation
	"""
	regfunc = None
	lines_changed = []

	def __init__(self, regfunc):
		self.regfunc = regfunc

	def weight(self, commit):
		x = self.lines_changed[commit - self.start] / self.lines_changed[self.base - self.start]
		y = self.regfunc.apply(x)
		if y < 1:
			y = 1
		return y

	def compile_sub_weights(self, start, base):
		self.start = start
		self.base = base
		self.distances.clear()
		self.lines_changed.clear()

		total_changed = 0
		pos = start
		while pos <= base:
			amount = (self.summary[self.commits[pos]]["lines_added"] + self.summary[self.commits[pos]]["lines_removed"])
			if amount <= 0:
				amount = 1
			total_changed += amount
			self.lines_changed.append(total_changed)
			pos += 1

		pos = start
		weight = 0
		while pos <= base:
			self.distances.append(weight)
			weight += self.weight(pos)
			pos += 1

class DistanceBlocksRegFunc(DistanceCached):
	"""
	Distance calculation using number of changed hunks as the distance metric,
	weighted using the function provided at initialisation
	"""
	regfunc = None
	blocks_changed = []

	def __init__(self, regfunc):
		self.regfunc = regfunc

	def weight(self, commit):
		x = self.blocks_changed[commit - self.start] / self.blocks_changed[self.base - self.start]
		y = self.regfunc.apply(x)
		if y < 1:
			y = 1
		return y

	def compile_sub_weights(self, start, base):
		self.start = start
		self.base = base
		self.distances.clear()
		self.blocks_changed.clear()

		total_changed = 0
		pos = start
		while pos <= base:
			amount = (self.summary[self.commits[pos]]["blocks_changed"])
			if amount <= 0:
				amount = 1
			total_changed += amount
			self.blocks_changed.append(total_changed)
			pos += 1

		pos = start
		weight = 0
		while pos <= base:
			self.distances.append(weight)
			weight += self.weight(pos)
			pos += 1

################################################
# Bisect algorithm

class Bisect:
	"""
	Perform the bisect algorithm on a set of collected data files using the
	provided distance metric
	"""
	distanceFunction = None
	def __init__(self, distanceFunction):
		self.distanceFunction = distanceFunction

	def interpolate(self, commit1, commit2, factor):
		if commit2 < commit1:
			commit1, commit2, factor = commit2, commit1, 1 - factor
		interval = self.distanceFunction.distance(commit1, commit2)
		offset = math.floor(interval * factor + 0.5)
		travelled = 0
		pos = commit1
		while travelled < offset:
			travelled += self.distanceFunction.weight(pos)
			pos += 1
		return pos

	def bisect(self, start, base, target):
		lowest = start
		highest = base
		count = 0
		while highest > target + 1:
			current = self.interpolate(lowest + 1, highest - 1, 0.5)
			if current == highest:
				current -=1
			else:
				if current == lowest:
					current +=1
			if current < target:
				lowest = current
			else:
				highest = current
			count += 1
		return count

	def load_data(self, file_in):
		print('Loading data from {}'.format(file_in))
		data = {'order': [], 'dict': {}}
		try:
			with open(file_in, 'r') as file_in:
				data = json.load(file_in)
		except Exception:
			print('File {} could not be read'.format(file_in))
		return data

	def analyse(self, filein):
		data = self.load_data(filein)
		count = 0
		total = 0
		stats = []
		if 'order' in data and 'dict' in data:
			commits = data['order']
			summary = data['dict']

			print("Number of commits: {}".format(len(commits)))

			reverts = []
			for commit in commits:
				if summary[commit] and 'reverts' in summary[commit]:
					revert = summary[commit]['reverts']
					base = summary[commit]['base']

					testdata = dict()

					if commit in summary and base in summary and revert in summary:
						testdata["start"] = summary[commit]['position']
						testdata["base"] = summary[base]['position']
						testdata["target"] = summary[revert]['position']

						if (testdata["start"] < testdata["target"]) and (testdata["target"] <= testdata["base"]):
							reverts.append(testdata)
						else:
							print("Skipping revert due to inconsistent inequalities")
					else:
						print("Skipping due to missing data")

			progress = 0
			self.distanceFunction.compile_weights(summary, commits)
			for testdata in reverts:
				self.distanceFunction.compile_sub_weights(testdata["start"], testdata["base"])

				steps = self.bisect(testdata["start"], testdata["base"], testdata["target"])
				stat = {}
				stat["distance"] = self.distanceFunction.distance(testdata["start"], testdata["base"])
				stat["target"] = self.distanceFunction.distance(testdata["start"], testdata["target"])
				stat["commits"] = testdata["base"] - testdata["start"]
				stat["steps"] = steps
				stats.append(stat)
				total += steps
				count += 1
				progress += 1
				if len(reverts) > 100 and progress % 100 == 0:
					print("Progress {}%".format(round(100 * progress / len(reverts))))
		else:
			print("File contains no data")
		return count, total, stats


