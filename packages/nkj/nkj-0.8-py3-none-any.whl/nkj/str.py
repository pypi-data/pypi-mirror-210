#
# [name] nkj.str.py
# [purpose] nkj.str library
# [exec] python -m nkj.str
#
# Written by Yoshikazu NAKAJIMA (Wed Sep 23 14:38:26 JST 2020)
#

__DEBUGLEVEL = 0
__LIB_DEBUGLEVEL = 0

NULLSTR = ''
CR = '\r' # 行頭へ復帰
LF = '\n' # 改行
CRLF = '\r\n'

PRINTEND_CR = CR
PRINTEND_LF = LF
PRINTEND_CRLF = CRLF
PRINTEND_NONE = ''
DEFAULT_PRINTEND = PRINTEND_LF
DEFAULT_BRACKET = '\"'  # {'\'', '\"'}
DEFAULT_DOTPRINT = True

import os
import sys
import re
import numpy as np

_BRACKET = DEFAULT_BRACKET
_VERBOSE_DOTPRINT = DEFAULT_DOTPRINT
_VERBOSE_DOTPRINT_COUNTER = 0

def debuglevel(level=None):
	global __DEBUGLEVEL
	if (level is None):
		return __DEBUGLEVEL
	else:
		__DEBUGLEVEL = level
		return True

def lib_debuglevel(level=None):
	global __LIB_DEBUGLEVEL
	if (level is None):
		return __LIB_DEBUGLEVEL
	else:
		__LIB_DEBUGLEVEL = level
		return True

def verbose_dotprint(flag=None, interval=None):
	global _VERBOSE_DOTPRINT
	global _VERBOSE_DOTPRINT_COUNTER
	if (flag is None):
		if (_VERBOSE_DOTPRINT is True):
			if (interval == None):
				print(".", end='', file=sys.stderr)
				sys.stderr.flush()
			elif (_VERBOSE_DOTPRINT_COUNTER >= interval - 1):
				print(".", end='', file=sys.stderr)
				sys.stderr.flush()
				_VERBOSE_DOTPRINT_COUNTER = 0
			else:
				_VERBOSE_DOTPRINT_COUNTER += 1
	elif (flag == 'end'):
		print("", file=sys.stderr)
		sys.stderr.flush()
	elif (flag == 'flag'):
		return _VERBOSE_DOTPRINT
	elif (flag == 'enable'):
		_VERBOSE_DOTPRINT = True
	elif (flag == 'disable'):
		_VERBOSE_DOTPRINT = False
	else:
		_VERBOSE_DOTPRINT = flag
		return True

def bracket(type=None):
	global _BRACKET
	if (type is None):
		return _BRACKET
	else:
		if (type == 1):
			_BRACKET = '\''
		elif (type == 2):
			_BRACKET = '\"'
		else:
			print_error("Illegal bracket type. ERROR#: NKJSTR-00055.")

def str_bracket(in_str, type=1):
	if (in_str is None):
		s = bracket() + bracket()
	elif (in_str == ""):
		s = bracket() + bracket()
	else:
		s = bracket() + str(in_str) + bracket()
	return s

def str_float(in_str):
	return "{0:8.3f}".format(in_str)

def concat(strlist):
	retstr = NULLSTR
	if (len(strlist) != 0):
		for i in range(len(strlist)):
			if (strlist[i] != None and strlist[i] != NULLSTR):
				retstr += str(strlist[i])
	return retstr

def concat_path(pathlist):
	retstr = NULLSTR
	for path in pathlist[:-1]:
		dprint3(["PATH: ", str_bracket(path)])
		if (path[-1] != '/'):
			path += '/'
		retstr = concat([retstr, path])
	dprint3(["PATH: ", str_bracket(pathlist[-1])])
	retstr += pathlist[-1]
	return retstr

def print_usage(msg):
	print("Usage: python " + sys.argv[0] + " " + msg, flush=True)
	sys.stdout.flush()

def print_message(msg):
	print(msg, flush=True)
	sys.stdout.flush()

def print_warning(msg):
	print("WARNING: " + msg, flush=True)
	sys.stdout.flush()

def print_error(msg):
	print("ERROR: " + msg, flush=True)
	sys.stdout.flush()

def _dprint(level, strlist, end=DEFAULT_PRINTEND): # '_' で始まる関数は import * で読み込まれない
	if (__DEBUGLEVEL >= level):
		message = NULLSTR
		for i in range(len(strlist)):
			s = str(strlist[i])
			if (s != NULLSTR):
				message += s
			else:
				message += "NULL"
		print(message, flush=True, end=end)
		sys.stdout.flush()
	else:
		pass

def _ldprint(level, strlist, end=DEFAULT_PRINTEND):
	if (__LIB_DEBUGLEVEL >= level):
		message = NULLSTR
		for i in range(len(strlist)):
			s = str(strlist[i])
			if (s != NULLSTR):
				message += s
			else:
				message += "NULL"
		print(message, flush=True, end=end)
		sys.stdout.flush()
	else:
		pass

def dprint0(strlist, end=DEFAULT_PRINTEND):
	_dprint(0, strlist, end)

def dprint1(strlist, end=DEFAULT_PRINTEND):
	_dprint(1, strlist, end)

def dprint2(strlist, end=DEFAULT_PRINTEND):
	_dprint(2, strlist, end)

def dprint3(strlist, end=DEFAULT_PRINTEND):
	_dprint(3, strlist, end)

def dprint(strlist, end=DEFAULT_PRINTEND):
	dprint1(strlist, end)

def ldprint0(strlist, end=DEFAULT_PRINTEND):
	_ldprint(0, strlist, end)

def ldprint1(strlist, end=DEFAULT_PRINTEND):
	_ldprint(1, strlist, end)

def ldprint2(strlist, end=DEFAULT_PRINTEND):
	_ldprint(2, strlist, end)

def ldprint3(strlist, end=DEFAULT_PRINTEND):
	_ldprint(3, strlist, end)

def ldprint(strlist, end=DEFAULT_PRINTEND):
	ldprint1(strlist, end)

def is_none(str):
	if (str is None):
		return True
	elif (str == NULLSTR):
		return True
	else:
		return False

def isnot_none(str):
	return (not isNone(str))

def extract_float(istr):
	strs = re.findall(r"[-]*[0-9][0-9]*[.]*[0-9]*[e+-]*[0-9]*", istr)
	vals = []
	for s in strs:
		vals.append(float(s))
	return np.array(vals)

def atoi(s):
	return int(s.strip())

def linestr2int(s_line):
	dlist = []
	for s in s_line.split(','):
		dlist.append(atoi(s))
	return dlist

def l2i(linestr):
	return linestr2int(linestr)

def atof(s):
	return float(s.strip())

def linestr2float(s_line):
	linestr = s_line.split(',')
	if (len(linestr) == 1):
		linestr = s_line.split(' ')
	dlist = []
	for s in linestr:
		dlist.append(atof(s))
	return dlist

def l2f(linestr):
	return linestr2float(linestr)


#-- main

if __name__ == '__main__':
	import os
	import sys

	sys.path.append(os.path.abspath(".."))

	import nkj.core as nc
	print(["ROOTPATH: ", nc.rootpath()])

	import nkj.str as ns
	ns.debuglevel(5)
	ns.dprint(["test1, ", "test2, ", "test3"])

	"""
	debuglevel(5)
	"""
	print("test")
	__DEBUGLEVEL = 5
	dprint(["test, ", "test2, ", ""])

	print(concat_path(["test", "test2"]))
	print(concat_path(["test/", "test2"]))
	print(concat_path(["test/", "test2", "test3"]))

	print(linestr2float('   0.00123, 2.345,  -12.356'))
