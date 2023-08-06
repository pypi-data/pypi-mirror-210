#
# [name] nkj.ncore.py
# [exec] python -m nkj.core
#
# Written by Yoshikazu NAKAJIMA
#

__ROOTPATH = None
_DEBUGLEVEL = 2

import os
import sys
import platform

sys.path.append(os.path.abspath(".."))
import nkj.str as ns
from nkj.str import *

#-- global functions

def rootpath(rootpath=None):
	global __ROOTPATH
	if (rootpath is None):
		if (__ROOTPATH == None):
			__ROOTPATH = os.getenv('NKJ_ROOT')
		return __ROOTPATH
	else:
		__ROOTPATH = rootpath
		return True

def getPythonVersion():
	major = sys.version_info.major
	minor = sys.version_info.minor
	return major, minor

def checkPythonVersion():
	dprint(["--> checkPythonVersion()"])
	vermajor, verminor = getPythonVersion()
	ldprint(["python version: ", str(vermajor), ".", str(verminor)])
	if (vermajor < 3):
		print_error("python version is too old.")
		exit
	elif (vermajor == 3 and verminor < 6):
		print_error("python version is too old.")
		exit
	dprint(["<-- checkPythonVersion()"])

#-- Global initialization

# Append root path

if (rootpath() == None):
	rootpath(os.path.abspath(".."))

sys.path.append(rootpath())

# !Append root path

#-- main

if __name__ == '__main__':
	#ns.debuglevel(_DEBUGLEVEL)
	dprint(["ROOTPATH: ", rootpath()])
	checkPythonVersion()
