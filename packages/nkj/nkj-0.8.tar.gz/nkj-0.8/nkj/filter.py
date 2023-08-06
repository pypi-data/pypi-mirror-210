#
# [name] nkj.filter.py
# [exec] python -m nkj.filter
#
# Written by Yoshikazu NAKAJIMA
#

import os
import sys
from math import *
from numpy import *

sys.path.append(os.path.abspath(".."))
from nkj.math import *

def spread_size(foot_size):
	return int(ceil(foot_size)) * 2 + 1

def filter_size(foot_size):
	return spread_size(foot_size)

def foot_size(spread_size):
	return int(ceil((spread_size - 1.0) / 2.0))

def kernel_offset(spread_size):
	return foot_size(spread_size)

def refresh_size(size):
	return spread_size(foot_size(size))

def bias_elimination(data):
	dmean = mean(data)
	data -= dmean
	return data

def gain_normalization(data):
	dsum = sum(abs(data))
	if (dsum != 0.0):
		data /= dsum
	return data

def power_normalization(data):
	sd = sqrt(sum(np.power(data, 2)) / len(data)) # standard deviation
	if (sd != 0.0):
		data /= sd
	return data

class kernel():
	_classname = "nkj.filter.kernel"

	def __init__(self):
		#-- instance variables
		self._positivegain = 1.0
		self._negativegain = 1.0
		self._offset = 0.0

	@classmethod
	def getClassName(cls):
		return kernel._classname

	@classmethod
	@property
	def classname(cls):
		return cls.getClassName()

	def getPositiveGain(self):
		return self._positivegain

	def setPositiveGain(self, g):
		self._positivegain = g

	@property
	def positivegain(self):
		return self.getPositiveGain()

	@positivegain.setter
	def positivegain(self, g):
		self.setPositiveGain(g)

	@property
	def posgain(self):
		return self.getPositiveGain()

	@posgain.setter
	def posgain(self, g):
		self.setPositiveGain(g)

	@property
	def pg(self):
		return self.getPositiveGain()

	@pg.setter
	def pg(self, g):
		self.setPositiveGain(g)

	def getNegativeGain(self):
		return self._negativegain

	def setNegativeGain(self, g):
		self._negativegain = g

	@property
	def negativegain(self):
		return self.getNegativeGain()

	@negativegain.setter
	def negativegain(self, g):
		self.setNegativeGain(g)

	@property
	def neggain(self):
		return self.getNegativeGain()

	@neggain.setter
	def neggain(self, g):
		self.setNegativeGain(g)

	@property
	def ng(self):
		return self.getNegativeGain()

	@ng.setter
	def ng(self, g):
		self.setNegativeGain(g)

	def getGain(self):
		return sqrt((sq(self.getPositiveGain()) + sq(self.getNegativeGain())) / 2.0)

	def setGain(self, g):
		self._positivegain = g
		self._negativegain = g

	@property
	def gain(self):
		return self.getGain()

	@gain.setter
	def gain(self, gg):
		self.setGain(gg)

	@property
	def g(self):
		return self.getGain()

	@g.setter
	def g(self, gg):
		self.setGain(gg)

	def getOffset(self):
		return self._offset

	def setOffset(self, off):
		self._offset = off

	@property
	def offset(self):
		return self.getOffset()

	@offset.setter
	def offset(self, off):
		self.setOffset(off)

	@property
	def o(self):
		return self.offset

	@o.setter
	def o(self, off):
		self.setOffset(off)

	def getKernel(self):
		return None  # NOT implemented

	@property
	def kernel(self):
		return self.getKernel()

	@property
	def k(self):
		return self.getKernel()

#-- main

if __name__ == '__main__':

	if (True):
		filter_size = 7 
		foot = foot_size(filter_size)
		print("Foot size:", foot)
		print("Filter size:", filter_size, "->", spread_size(foot))

		filter_size = 8 
		foot = foot_size(filter_size)
		print("Foot size:", foot)
		print("Filter size:", filter_size, "->", spread_size(foot))

	if (True):
		k = kernel()
		print("Class name: \"{}\"".format(k.getClassName()))
		print("Class name: \"{}\"".format(k.classname))
		k.gain = 3.0
		print("Gain:   {}".format(k.getGain()))
		print("Gain:   {}".format(k.gain))
		print("Gain:   {}".format(k.g))
		k.offset = 2.5
		print("Offset: {}".format(k.getOffset()))
		print("Offset: {}".format(k.offset))
		print("Offset: {}".format(k.o))
		print("Kernel: {}".format(k.getKernel()))
		print("Kernel: {}".format(k.k))
