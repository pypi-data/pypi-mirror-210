#
# [name] nkj.file.py
#
# Written by Yoshiakzu NAKAJIMA
#
_LIB_DEBUGLEVEL = 0

import os
import sys
import json
import numpy as np

sys.path.append(os.path.abspath(".."))
from nkj.os import *
from nkj.np import *

def load_nparray(filename):
	try:
		return np.load(filename)
	except:
		return nparrayerrorval()

def save_nparray(filename, array):
	try:
		np.save(filename, array)
		return True
	except:
		return False

def save_nparraydict(filename, data):
	ldprint(["--> save_nparraydict(", str_bracket(filename), ", ", len(data), ")"])
	ldprint2(["Data type: ", type(data)])
	if (type(data) != dict):
		print_error("Illegal data type.")
		return False
	ndata = {}
	for key in data.keys():
		dprint2(["Key: ", str_bracket(key)])
		ndata[key] = str(tuple(data[key].tolist()))
	with open(filename, 'w') as f:
		json.dump(ndata, f, indent=2)
		return True
	return False

def _csvdictlist(origdict):
	dictlist = []
	for key in origdict:
		dprint2(["Dict key: \'{0}\'".format(key)])
		dict = origdict.get(key)
		if (dict != None):
			csvdict = {}
			csvdict.update(**{'Data label': key}, ** origdict.get(key))
			dictlist.append(csvdict)
	return dictlist

def _savecsv(filename, dictlist):
	try:
		with open(filename, 'w') as f:
			keylist = dictlist[0].keys()
			dprint(["Keys: {0}".format(keylist)])
			dprint(["Keys: {0}".format(list(keylist))])
			print("test")
			writer = csv.DictWriter(f, list(keylist), delimiter=',', quotechar='"')
			print("test")
			writer.writeheader()
			for rowdata in dictlist:
				dprint(["Row:  {0}".format(rowdata)])
				if (rowdata != None):
					writer.writerow(rowdata)
		return True
	except:
		return False

def savecsv(filename, dict):
	dictlist = _csvdictlist(dict)
	if (dictlist == None):
		return False
	if (True):
		dprint(["-- CSV dict list --"])
		for dict in dictlist:
			label = dict['Data label']
			dprint(["Dict[\'{0}\']: {1}".format(label, dict)])
		dprint(["--"])
	return _savecsv(filename, dictlist)

#-- main

if __name__ == '__main__':

	# Save test
	a = np.array([0, 1, 2, 3, 4, 5])
	print(a)

	testfile = "test.npy"

	if (not save_nparray(testfile, a)):
		print_error("Can't save \'{0}\'".format(testfile))
		os.sys.exit()

	# Load test
	b = load_nparray(testfile)
	if (is_nparrayerror(b)):
		print_error("Can't load \'{0}\'".format(testfile))
		os.sys.exit()
	print(b)
