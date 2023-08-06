#
# [name] nkj.fa.py
# [exec] python fa.py
# [purpose] library for frequency analysis
#
# [reference] https://qiita.com/yukiB/items/59f8484e72bb0471ad47
#             https://qiita.com/MuAuan/items/8850e037babcff991b8e
#             https://qiita.com/MuAuan/items/858aab2879708668e2bb
#
# Written by Yoshikazu NAKAJIMA
#

import os
import sys
import math
import cmath
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(".."))
from nkj.str import *
from nkj.math import *
from nkj.filter import *

#-- global functions

def omega(f): # frequency to omega
	return (2.0 * np.pi * f)

def freq(f):  # omega to frequency
	return f / (2.0 * np.pi)

def f2cycletime(f): # ct: cycle time
	if (f == 0.0):
		return ValueError
	else:
		return 1.0 / f

def f2ct(f):
	return f2cycletime(f)

def cycletime2f(ct):
	if (ct == 0.0):
		return ValueError
	else:
		return 1.0 / ct

def ct2f(ct):
	return cycletime2f(ct)

def phase2time(theta, f):
	omega = f2omega(f)
	if (omega == ValueError):
		return ValueError
	else:
		return theta / omega

def time2phase(t, f):
	return f2omega(f) * t

def spiffphase(theta): # reshape phase to [0.0, 2.0 * pi]
	dpi = 2.0 * np.pi
	while (theta < 0.0):
		theta = theta + dpi
	while (theta >= dpi):
		theta = theta - dpi
	return theta

def cphase(c, t=None, f=None):
	if (t == None):
		phase = cmath.phase(c)
	else:
		phase = cmath.phase(c) - time2phase(t, f)
	return spiffphase(phase)

#-- classes

class nkjfa():
	#-- class variables
	_classname = "nkjfa"

	def __init__(self):
		ldprint("Classname: ", str_bracket(nkjfa._classname))

	def __str__(self):
		return concat("Classname: ", str_bracket(nkjfa._classname))

#-- main

if __name__ == '__main__':

	print(nkjfa)

	#-- FFT

	"""
	fs = 1024
	N = 10 * fs
	nperseg = 512
	amp = 2 * np.sqrt(2)
	noise_power = 0.001 * fs / 2
	time = np.arange(N) / float(fs)
	carrier = amp * np.sin(2 * np.pi * 50 * time)

	noise = np.random.normal(scale=np.sqrt(noise_power), size=time.shape)

	x = carrier + noise

	f, t, Zxx = sp.stft(x, fs=fs, nperseg=nperseg)

	plt.figure()
	plt.pcolormesh(t, f, np.abs(Zxx), vmin=0, vmax=amp)
	plt.ylim([f[1], f[-1]])
	plt.title('STFT magnitude')
	plt.ylabel('Frequency [Hz]')
	plt.xlabel('Time [sec]')
	plt.yscale('log')
	plt.show()
	"""

	print("phase:", rad2deg(spiffphase(deg2rad(718.2))))
	print("phase:", rad2deg(spiffphase(deg2rad(-90.2))))
