#
# [name] nkj.os.py
#
# Written by Yoshikazu NAKAJIMA
#
_LIB_DEBUGLEVEL = 0

import os
import sys
import re
import glob

sys.path.append(os.path.abspath(".."))
from nkj.str import *

def parse_args(args):
	params = {}
	args = (' ' + ' '.join(args)).split(' -') 
	args = [a for a in args if a]   # remove blank elements

	for arg in args:
		split_arg = arg.split(' ')
		key = re.sub('^-*', '', split_arg[0])
		val = ' '.join(split_arg[1:])
		params[key] = val 

	return params

def get_filelist(dir=".", ext="*", refinement=None, elimination=None):
	ldprint(["Dir:    ", str_bracket(dir)])
	ldprint(["Ext:    ", str_bracket(ext)])
	filename = "*"
	if (type(refinement) is list):
		if (refinement != None):
			for refine in refinement:
				ldprint2(["Refine: ", str_bracket(refine)])
				filename += refine + "*"
	else:
		if (refinement != None):
			ldprint(["Refine: ", str_bracket(refinement)])
			filename += refinement + "*"
	if (ext[0] == '.'):
		filename += ext
	else:
		filename += "." + ext
	ldprint(["Filename: ", str_bracket(filename)])
	filelist = glob.glob(os.path.join(dir, filename))
	ldprint(["Filelist: ", filelist])
	if (elimination != None):
		newfilelist = []
		if (type(elimination) is list):
			for file in filelist:
				flag = True
				for elim in elimination:
					ldprint2(["Elim:   ", str_bracket(elim)])
					if (elim in file):
						flag = False
						break
				if (flag):
					newfilelist.append(file)
		else:
			for file in filelist:
				ldprint2(["Elim:   ", str_bracket(elimination)])
				if (elimination not in file):
					newfilelist.append(file)
		filelist = newfilelist
	filelist.sort()
	return filelist
