#
# [name] nkj.prob.py
# [exec] python prob.py
#
# Written by Yoshikazu NAKAJIMA
#
_LIB_DEBUGLEVEL = 1

import os
import sys

sys.path.append(os.path.abspath(".."))
from nkj.str import *

def p_and(p_a, p_b):
	return p_a * p_b

def p_or(p_a, p_b):
	return (p_a + p_b - p_and(p_a, p_b))

def p_cap(p_a, p_b):
	return p_and(p_a, p_b)

def p_cup(p_a, p_b):
	return p_or(p_a, p_b)

def cap(p_a, p_b):
	return p_cap(p_a, p_b)

def cup(p_a, p_b):
	return p_cup(p_a, p_b)


#-- main

if __name__ == '__main__':
	lib_debuglevel(_LIB_DEBUGLEVEL)

	p_a = 0.3
	p_b = 0.7

	ldprint(["p_a: ", p_a])
	ldprint(["p_b: ", p_b])

	ldprint(["p_a AND p_b: ", p_and(p_a, p_b)])
	ldprint(["p_a OR p_b:  ", p_or(p_a, p_b)])
