#
# [name]    nkj.js.py
# [purpose] library for json
#
# Written by Yoshiakzu NAKAJIMA
#
_LIB_DEBUGLEVEL = 1

import os
import sys
import re
import numpy as np
import json

sys.path.append(os.path.abspath(".."))
import nkj.str as ns
from nkj.str import *

def load_nparrayjson(filename):
	with open(filename, 'r') as f:
		data = json.load(f)
		ndata = {}
		for key in data.keys():
			ndata[key] = ns.extract_float(data[key])
		return ndata
	return None

def save_nparrayjson(filename, data):
	if (type(data) != dict):
		print_error("Illegal data type.")
		return False
	ndata = {}
	for key in data.keys():
		ndata[key] = str(tuple(data[key].tolist()))
	with open(filename, 'w') as f:
		json.dump(ndata, f, indent=2)
		return True
	return False

#-- main

if __name__ == '__main__':
	USAGE = " input.json"

	lib_debuglevel(_LIB_DEBUGLEVEL)

	argc = len(sys.argv)

	if (argc == 2):
		filename = sys.argv[1]
	else:
		print_usage(sys.argv[0] + USAGE)
		os.sys.exit()
	ldprint(["Filename: ", str_bracket(filename)])

	data = load_nparrayjson(filename)
	if (data == None):
		print_error("Can't load input.json")
		os.sys.exit()

	ldprint(["Data: ", data])
