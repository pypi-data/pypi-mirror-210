#
# [name] nkj.np.py
#
# Written by Yoshiakzu NAKAJIMA
#
_LIB_DEBUGLEVEL = 0

import numpy as np

_nparrayerror = None

def nparrayerrorval(val=None):
	global _nparrayerror
	if (val is None):
		return _nparrayerror
	else:
		_nparrayerror = val
		return True

def is_nparrayerror(array):
	return (array.size == 0)

#-- main

if __name__ == '__main__':

	a = np.array([[1, 2], [2, 4], [3, 6]])
	print(a)

	covm = np.cov(a, rowvar=0, bias=1)
	print(covm)

	covm = np.cov(a, rowvar=0, bias=0)
	print(covm)
