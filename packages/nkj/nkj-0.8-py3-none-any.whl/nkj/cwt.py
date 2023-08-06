#
# [name] nkj.cwt.py
# [exec] python -m nkj.cwt
#
# Written by Yoshikazu NAKAJIMA
#
_LIB_DEBUGLEVEL = 0

import os
import sys
import gc
from math import *
import numpy as np
from numpy import *
import matplotlib.pyplot as plt
import h5py as h5

sys.path.append(os.path.abspath(".."))
from nkj.str import *
from nkj.fa  import *
from nkj.filter import *

_DEFAULT_WAVELET_SCALE = 1.0 # wavelet_scale = f / f_w
_DEFAULT_FREQUENCY = 1.0
_DEFAULT_ERROR_PADDING = 0

_WAVELET_DATA_BIAS_ELIMINATION_FLAG = False   # data bias elimination flag
_WAVELET_DATA_GAIN_NORMALIZATION_FLAG = False # data gain normalization flag

_WAVELET_SCALE = _DEFAULT_WAVELET_SCALE # wavelet scale
_WAVELET_GAUSS_SIGMA = 3.5 # Wavelet gauss sigma. It shows gauss function spread scale for sigma size.
_WAVELET_FUNCTION = "morlet" # {"morlet_wt", "morlet"}
_MIN_WAVELET_SCALE = 1.0
_MIN_WAVELET_GAUSS_SIGMA = 3.5

_ERROR_PADDING = _DEFAULT_ERROR_PADDING

def error_padding(padding=None):
	global _ERROR_PADDING
	if (padding == None):
		return _ERROR_PADDING
	else:
		_ERROR_PADDING = padding
		return True

def data_bias_elimination_flag(flag=None):
	global _WAVELET_DATA_BIAS_ELIMINATION_FLAG
	if (flag == None):
		return _WAVELET_DATA_BIAS_ELIMINATION_FLAG
	else:
		_WAVELET_DATA_BIAS_ELIMINATION_FLAG = flag
		return True

def data_gain_normalization_flag(flag=None):
	global _WAVELET_DATA_GAIN_NORMALIZATION_FLAG
	if (flag == None):
		return _WAVELET_DATA_GAIN_NORMALIZATION_FLAG
	else:
		_WAVELET_DATA_GAIN_NORMALIZATION_FLAG = flag
		return True

def wavelet_scale(s=None):
	global _WAVELET_SCALE
	if (s == None):
		return _WAVELET_SCALE
	else:
		if (s <= 0.0):
			print_error("Illegal wavelet scale.")
			return False
		elif (s < _MIN_WAVELET_SCALE):
			print_warning("Wavelet scale might be too small.")
		_WAVELET_SCALE = s
		return True

def wavelet_pseudo_frequency_scale(fw=None):
	if (fw == None):
		return 1.0 / wavelet_scale()
	else:
		wavelet_scale(1.0 / fw)
		return True

def wavelet_gauss_sigma(s=None): # DON'T CALL THIS FROM THE OUTSIDE IF NOT NEEDED.
	global _WAVELET_GAUSS_SIGMA
	if (s == None):
		return _WAVELET_GAUSS_SIGMA
	elif (s < _MIN_WAVELET_GAUSS_SIGMA):
		print_warning("Wavelet gauss sigma might be too small.")
	_WAVELET_GAUSS_SIGMA = s
	return True

def _wavelet_gauss_sigma_2(s=None): # DON'T CALL THIS FROM THE OUTSIDE IF NOT NEEDED.
	if (s == None):
		return 2.0 * wavelet_gauss_sigma()
	else:
		return wavelet_gauss_sigma(s / 2.0)

def _wavelet_gauss_scale(s=None): # This returns how many waves are included with the kernel.
	if (s == None):
		return wavelet_scale() * _wavelet_gauss_sigma_2()
	else:
		wavelet_scale(s / wavelet_gauss_sigma_2())
		return True

def wavelet_gauss_waves(s=None):
	return _wavelet_gauss_scale(s)

def wavelet_kernel_waves(s=None):
	return wavelet_gauss_waves(s)

def wavelet_frequency(f):
	return wavelet_scale() * f

def wave_frequency(fw): # fw: wavelet frequency
	return fw / wavelet_scale()

def wavelet_cycle(T): # T: cycle interval(time/length)
	return _wavelet_gauss_scale() * T

def wave_cycle(Tw): # Tw: wavelet cycle interval(time/length)
	return Tw / _wavelet_gauss_scale()

def wavelet_time(t): # t: time
	return t / _wavelet_gauss_scale()

def wavelet_gauss_time(t): # t: time
	return t / wavelet_scale()

def wave_time(tw): # tw: wavelet time
	return tw * wavelet_scale()

def morlet(x, f0): # x: time/length, f0: analyzed frequency
	gx = f0 * wavelet_gauss_time(x)
	g = exp(-sq(gx) / 2.0) # gauss
	wx = omega(f0) * x
	re = g * cos(wx)
	im = g * sin(wx)
	"""
	re = cos(wx)
	im = sin(wx)
	"""
	return re, im

def morlet_wt(wt): # wt: angle [-np.pi, np.pi]
	gx = wavelet_gauss_time(wt / (2.0 * np.pi))
	g = exp(-sq(gx) / 2.0) # gauss
	re = g * cos(wt)
	im = g * sin(wt)
	return re, im

def normalize_kernel(kernel_re, kernel_im):
	__VERSION = 2

	if (__VERSION == 1):
		# bias elimination

		dmean = mean([mean(kernel_re), mean(kernel_im)])
		kernel_re -= dmean
		kernel_im -= dmean

		dsum = 0.0
		for i in range(len(kernel_re)):
			dsum += sqrt(sq(kernel_re[i]) + sq(kernel_im[i]))
		dsum /= 2.0 # due to dividing to real and imaginary

		if (dsum != 0.0):
			kernel_re /= dsum
			kernel_im /= dsum

	elif (__VERSION == 2):
		#
		# kernel の re, im それぞれに対して、さらに +, - 成分をそれぞれで算出し、各々の重み和が 0.5 になるように補正する．
		#
		rpsum = 0.0  # real positive
		rnsum = 0.0  # real negative
		ipsum = 0.0  # imaginary positive
		insum = 0.0  # imaginary negative

		for i in range(len(kernel_re)):
			re = kernel_re[i]
			if (re >= 0.0):
				rpsum += re
			else:
				rnsum -= re   # += -re

		for j in range(len(kernel_im)):
			im = kernel_im[j]
			if (im >= 0.0):
				ipsum += im
			else:
				insum -= im   # += -im

		rpsum *= 2.0   # /= 0.5
		rnsum *= 2.0   # /= 0.5
		ipsum *= 2.0   # /= 0.5
		insum *= 2.0   # /= 0.5

		for i in range(len(kernel_re)):
			if (kernel_re[i] >= 0.0):
				if (rpsum != 0.0):
					kernel_re[i] /= rpsum
			else:
				if (rnsum != 0.0):
					kernel_re[i] /= rnsum

		for j in range(len(kernel_im)):
			if (kernel_im[j] >= 0.0):
				if (ipsum != 0.0):
					kernel_im[j] /= ipsum
			else:
				if (insum != 0.0):
					kernel_im[j] /= insum

	else: # other versions
		kernel_re = gain_normalization(bias_elimination(kernel_re))
		kernel_im = gain_normalization(bias_elimination(kernel_im))

	return kernel_re, kernel_im

def morlet_kernel(f, dt):
	#
	# f:  Analyzed frequency [Hz]
	# dt: Sampling interval(time/length)
	#
	ldprint2(["Analized frequency: ", f])

	fs = 1.0 / dt
	ldprint2(["Sampling frequency: ", fs])

	if (fs < 2.0 * f):
		print_error("Too low sampling frequency.")
		os.sys.exit()

	if (fs < 5.0 * f):
		print_warning("Low sampling frequency.")

	T = 1.0 / f
	ldprint2(["Cycle:         ", T])
	Tw = wavelet_cycle(T)
	ldprint2(["Wavelet scale: ", wavelet_scale()])
	ldprint2(["Wavelet cycle: ", Tw])
	ldprint2(["dt           : ", dt])
	kernelsize = refresh_size(Tw / dt + 1)
	ldprint2(["Kernel size: ", Tw / dt + 1, " -> ", kernelsize])

	footsize = foot_size(kernelsize)
	ldprint2(["Foot size:   ", footsize])

	kernel_re = []
	kernel_im = []
	for i in range(-footsize, footsize + 1):
		ldprint3(["Index: ", i])
		t = -(dt * i)
		ldprint3(["Time:  ", t])
		if (_WAVELET_FUNCTION == "morlet_wt"):
			wt = omega(f) * t
			re, im = morlet_wt(wt)
		elif (_WAVELET_FUNCTION == "morlet"):
			re, im = morlet(t, f)
		else:
			print_error("Illegal _WAVELET_FUNCTION specification.")
			os.sys.exit()
		kernel_re.append(re)
		kernel_im.append(im)

	kernel_re = np.array(kernel_re)
	kernel_im = np.array(kernel_im)

	# kernel normalization

	kernel_re, kernel_im = normalize_kernel(kernel_re, kernel_im)

	return kernel_re, kernel_im, kernelsize

def wavelet_f(data, dt, f): # dt: sampling interval [sec], f: analyzed frequency [Hz]
	ldprint2(["--> wavelet_f(data[", len(data), "], ", dt, ", ", f, ")"])

	datasize = len(data)
	ldprint2(["Data size: ", datasize])

	kr, ki, ks = morlet_kernel(f, dt)  # 周波数とサンプリング間隔（秒）からカーネルを生成
	ldprint2(["Filter size: ", ks])

	footsize = foot_size(ks)
	ldprint2(["Foot size:   ", footsize])

	offset = kernel_offset(ks)
	ldprint2(["Offset:      ", offset])

	wt = []
	wt_re = []
	wt_im = []

	index = 0
	while (index < offset):
		left = index - offset
		right = ks + left
		ldprint3(["Less[", index, "]: [", left, ", ", right - 1, "]"])
		ldata = data[-left : 0 : -1]
		rdata = data[0 : right]
		ldprint3(["Ldata size: ", len(ldata)])
		ldprint3(["Rdata size: ", len(rdata)])
		if (data_bias_elimination_flag()):
			signal = bias_elimination(np.array(concatenate([ldata, rdata])))
		else:
			signal = np.array(concatenate([ldata, rdata]))
		ldprint2(["Signal size: ", len(signal)])
		ldprint2(["Kernel size: ", ks])
		if (len(signal) != ks):
			'''
			print_error("Too short data compared with the analyzed frequency of {0:0.3f} Hz. Wavelet cycle length exceeded over the data size. Data are padded with {1:0.3f}.".format(f, error_padding()))
			'''
			dlen = len(data)
			return False, np.full(dlen, error_padding(), dtype=np.float), np.full(dlen, error_padding(), dtype=np.float), np.full(dlen, error_padding(), dtype=np.float)
		re = np.dot(signal, kr)   # 信号とカーネルの内積をとる
		im = np.dot(signal, ki)   # 信号とカーネルの内積をとる
		wt.append(sqrt(sq(re) + sq(im)))   # 実部と虚部からパワーを計算
		wt_re.append(re)
		wt_im.append(im)
		index += 1
		if (data_bias_elimination_flag()):
			del signal
			gc.collect()

	while (index < datasize - offset):
		left = index - offset
		right = left + ks
		ldprint3(["Contained[", index, "]: [", left, ", ", right - 1, "]"])
		if (data_bias_elimination_flag()):
			signal = bias_elimination(data[left : right])
		else:
			signal = data[left : right]
		re = np.dot(signal, kr)
		im = np.dot(signal, ki)
		wt.append(sqrt(sq(re) + sq(im)))
		wt_re.append(re)
		wt_im.append(im)
		index += 1
		if (data_bias_elimination_flag()):
			del signal
			gc.collect()

	while (index < datasize):
		left = index - offset
		exceed = left + ks + - datasize
		right = datasize - 1 - exceed
		ldprint3(["Exceeding[", index, "]: [", left, ", +++", exceed, "(", right, ")]"])
		ldata = data[left : datasize]
		rdata = data[datasize - 1 : right : -1]
		ldprint3(["Ldata size:", len(ldata)])
		ldprint3(["Rdata size:", len(rdata)])
		if (data_bias_elimination_flag()):
			signal = bias_elimination(np.array(concatenate([ldata, rdata])))
		else:
			signal = np.array(concatenate([ldata, rdata]))
		re = np.dot(signal, kr)
		im = np.dot(signal, ki)
		wt.append(sqrt(sq(re) + sq(im)))
		wt_re.append(re)
		wt_im.append(im)
		index += 1
		if (data_bias_elimination_flag()):
			del signal
			gc.collect()

	ldprint2(["<-- wavelet_f()"])

	return True, np.array(wt), np.array(wt_re), np.array(wt_im)

def cwt_f(data, dt, f):
	return wavelet_f(data, dt, f)

def wavelet(data, dt, flist): # flist: frequency list
	ldprint(["--> wavelet(data[", len(data), "], ", dt, ")"])
	slist = []
	warray = np.empty((0, len(data)))
	rarray = np.empty((0, len(data)))
	iarray = np.empty((0, len(data)))
	for f in flist:
		ldprint(["f: ", f])
		status, wt, wt_re, wt_im = wavelet_f(data, dt, f)
		ldprint3(["Status: ", status])
		ldprint3(["Data[0]: ", wt.size])
		ldprint3(["Data[1]: ", wt_re.size])
		ldprint3(["Data[2]: ", wt_im.size])
		slist.append(status)
		warray = np.vstack((warray, wt))
		rarray = np.vstack((rarray, wt_re))
		iarray = np.vstack((iarray, wt_im))
	ldprint(["<-- wavelet()"])
	return slist, warray, rarray, iarray

def cwt(data, dt, flist):
	return wavelet(data, dt, flist)

def power_normalize_ws(data): # data: wavelet spectra
	ldprint(["--> power_normalize_ws()"])
	ldprint(["Data shape: ", data.shape])

	freqs = data.shape[0]
	samples = data.shape[1]
	ldprint(["Frequencies:  ", freqs])
	ldprint(["Data samples: ", samples])

	ndata = np.copy(data)
	for i in range(samples):
		sum = 0.0
		for fid in range(freqs):
			sum += sq(ndata[fid, i])
		if (sum != 0.0):
			sum = sqrt(sum)
			ldprint2(["Data norm: ", sum])
			ndata[:, i] /= sum

	ldprint(["<-- power_normalize_ws()"])
	return ndata

def statistics(data): # data: wavelet spectra
	ldprint(["--> statistics()"])
	ldprint(["Data shape: ", data.shape])
	freqs = data.shape[0]
	samples = data.shape[1]
	ldprint(["Frequencies:  ", freqs])
	ldprint(["Data samples: ", samples])
	spectra_av = np.mean(data, axis=1)  # axis=0: vertically(column-directionally) averaging, axis=1: horizontally(row-directionally) averaging
	spectra_sd = np.std(data, axis=1)
	ldprint(["<-- statistics()"])
	return spectra_av, spectra_sd, samples

def sd_normalize_array(data, biasadjustment=True):
	ldprint(["--> sd_normalize_array(, ", biasadjustment, ")"])
	if (biasadjustment is True):
		av = np.mean(data)
		data -= av
		sd = np.std(data)
	else:
		dlen = len(data)
		sd = 0.0
		if (dlen != 0):
			for i in range(len(data)):
				sd += (data[i])**2
			sd /= dlen
			sd = np.sqrt(sd)
	if (sd != 0.0):
		data /= sd
	ldprint(["<-- sd_normalize_array()"])
	return data

def sum_normalize_array(data, biasadjustment=True):
	if (biasadjustment is True):
		av = np.mean(data)
		data -= av
	sum = np.sum(np.abs(data))
	if (sum != 0.0):
		data /= sum
	data *= float(len(data))
	return data

def sd_abs_normalize_array(data):
	return sd_normalize_array(data, False)

def sum_abs_normalize_array(data): # DOESN'T ADJUST THE BIAS
	return sum_normalize_array(data, False)

def normalize_array(data):
	return sd_normalize_array(data)

def abs_normalize_array(data):
	return sd_abs_normalize_array(data)

def sequential_correlation(data, basesignal): # signal: signal data sequence, basesignal: a signal
	ldprint(["--> sequential_correlation()"])

	ldprint(["Data shape: ", data.shape])
	freqs = data.shape[0]
	samples = data.shape[1]
	ldprint(["Frequencies:  ", freqs])
	ldprint(["Data samples: ", samples])

	if (debuglevel() > 0):
		if (len(basesignal) != freqs):
			print_error("Illegal algorithm. ERROR#: NKJWAVELET-00402.")
			os.sys.exit()

	corr = []
	for i in range(samples):
		nsig = normalize_array(data[:, i])
		nbase = normalize_array(basesignal)
		corr.append(np.dot(nbase, nsig) / float(freqs))
		del nsig
		del nbase
		gc.collect()

	ldprint(["Corr data #:  ", len(corr)])
	ldprint(["<-- sequential_correlation()"])
	return np.array(corr)

def sequential_abs_correlation(data, basesignal): # signal: signal data sequence, basesignal: a signal
	ldprint(["--> sequential_abs_correlation()"])

	ldprint(["Data shape: ", data.shape])
	freqs = data.shape[0]
	samples = data.shape[1]
	ldprint(["Frequencies:  ", freqs])
	ldprint(["Data samples: ", samples])

	if (debuglevel() > 0):
		if (len(basesignal) != freqs):
			print_error("Illegal algorithm. ERROR#: NKJWAVELET-00426.")
			os.sys.exit()

	corr = []
	for i in range(samples):
		nsig = abs_normalize_array(data[:, i])
		nbase = abs_normalize_array(basesignal)
		corr.append(np.dot(nbase, nsig) / float(freqs))

	ldprint(["Corr data #:  ", len(corr)])
	ldprint(["<-- sequential_abs_correlation()"])
	return np.array(corr)

def sequential_average_correlation(data): # data: wavelet spectra
	av, sd, n = statistics(data)
	return sequential_correlation(data, av)

def sequential_average_abs_correlation(data): # data: wavelet spectra
	av, sd, n = statistics(data)
	return sequential_abs_correlation(data, av)

def temporal_correlation(data, base):
	return sequential_correlation(data, base)

def temporal_abs_correlation(data, base):
	return sequential_abs_correlation(data, base)

def temporal_average_correlation(data):
	return sequential_average_correlation(data)

def temporal_average_abs_correlation(data):
	return sequential_average_abs_correlation(data)

def correlate_ndarray(sig, base):
	ldprint(["--> correlate_ndarray()"])
	if (sig.shape != base.shape):
		ldprint0(["sig.shape:  ", sig.shape])
		ldprint0(["base.shape: ", base.shape])
		print_error("Data size mismatch. ERROR#: NKJWAVELET-00468.")
		return ValueError
	nsig = normalize_array(sig.flatten())
	nbase = normalize_array(base.flatten())
	corr = np.dot(nbase, nsig)
	datanum = len(nsig)
	if (datanum != 0):
		corr /= float(datanum)
	del nsig
	del nbase
	gc.collect()
	ldprint(["<-- correlate_ndarray()"])
	return corr

def correlate_phaseshifted_2darray(sig, base, phase):
	ldprint(["--> correlate_phaseshifted_2darray(,, ", phase, ")"])
	ldprint(["phase:  ", phase])
	if (sig.ndim != 2):
		print_error("Illegal data dimension. Data dimension is {0}. ERROR#: NKJWAVELET-00481.".format(sig.ndim))
		return ValueError
	if (base.ndim != 2):
		print_error("Illegal data dimension. Data dimension is {0}. ERROR#: NKJWAVELET-00486.".format(base.ndim))
		return ValueError
	ldprint(["sig.shape:  ", sig.shape])
	ldprint(["base.shape: ", base.shape])
	if (sig.shape != base.shape):
		print_error("Data size mismatch. ERROR#: NKJWAVELET-00495.")
		ldprint0(["sig.shape:  ", sig.shape])
		ldprint0(["base.shape: ", base.shape])
		return ValueError
	dlen = sig.shape[1]
	dt = phase
	ldprint(["dlen: ", dlen])
	ldprint(["dt:   ", dt])
	if (dt < -dlen or dlen - 1 < dt):
		print_error("Illegal phase. ERROR#: NKJWAVELET-00485.")
		return ValueError
	if (dt < 0):
		dlen = base.shape[1]
		csig = sig[:, -dt:]
		cbase = base[:, :dlen+dt]
		ldprint(["csig.shape:  ", csig.shape])
		ldprint(["cbase.shape: ", cbase.shape])
		if (debuglevel() > 0):
			if (csig.shape != cbase.shape):
				print_error("Illegal algorithm. ERROR#: NKJWAVELET-00492.")
				os.sys.exit()
	else:
		dlen = base.shape[1]
		csig = sig[:, :dlen-dt]
		cbase = base[:, dt:]
		ldprint(["csig.shape:  ", csig.shape])
		ldprint(["cbase.shape: ", cbase.shape])
		if (debuglevel() > 0):
			if (csig.shape != cbase.shape):
				print_error("Illegal algorithm. ERROR#: NKJWAVELET-00492.")
				os.sys.exit()
	corr = correlate_ndarray(csig, cbase)
	return corr

"""
def interval_correlation(data): # data: wavelet spectra
	ldprint(["--> interval_correlation()"])
	ldprint(["Data shape: ", data.shape])

	av, sd, n = statistics(data)

	freqs = data.shape[0]
	samples = data.shape[1]
	ldprint(["Frequencies:  ", freqs])
	ldprint(["Data samples: ", samples])

	ldprint(["<-- interval_correlation()"])
	return corr
"""

#-- main

if __name__ == '__main__':
	lib_debuglevel(1)

	# FLAGS

	FLAG_MORLET_TEST = False
	FLAG_WAVELET_KERNEL_TEST = True
	FLAG_WAVELET_TRANSFORM_TEST = True
	FLAG_WAVELET_TRANSFORM_TEST2 = True
	FLAG_2DARRAY_CORRELATION_TEST = False
	FLAG_PHASESHIFTED_2DARRAY_CORRELATION_TEST = False

	# CONSATNTS

	OPTIONS = "[analyzed frequency [wavelet_scale]]"
	SAMPLINGS = 300
	SAMPLING_INTERVAL =  0.1 # sampling interval [sec]
	ANALYZED_FREQUENCY = 2.0 # analyzed frequency [Hz]

	# args

	argc = len(sys.argv)
	ldprint(["Argc: ", argc])
	if (argc == 3):
		ANALYZED_FREQUENCY = float(sys.argv[1])
		if (wavelet_scale(float(sys.argv[2])) is False):
			os.sys.exit()
	elif (argc == 2):
		argv1 = sys.argv[1]
		if (argv1 == "help"):
			print_usage(OPTIONS)
			os.sys.exit()
		else:
			ANALYZED_FREQUENCY = float(sys.argv[1])
	elif (argc == 1):
		pass
	else:
		print_error("Illegal arguments.")

	# morlet test

	if (FLAG_MORLET_TEST):
		print("-- Morlet test.")

		xlist = []
		rlist = []
		ilist = []
		for x in np.arange(-0.5, 0.5, 0.001):
			xlist.append(x)
			if (_WAVELET_FUNCTION == "morlet_wt"):
				wt = omega(f) * t
				re, im = morlet_wt(omega(1.0) * x)
			elif (_WAVELET_FUNCTION == "morlet"):
				re, im = morlet(x, 1.0)
			else:
				print_error("Illegal _WAVELET_FUNCTION specification.")
				os.sys.exit()
			rlist.append(re)
			ilist.append(im)
		rlist = np.array(rlist)
		ilist = np.array(ilist)

		plt.plot(xlist, rlist, color='black')
		plt.plot(xlist, ilist, color='black', linestyle='dashed')
		plt.title("Morlet kernel")
		plt.xlabel("Time [sec]")
		plt.ylabel("Amplitude")
		plt.show()
		plt.close()

	# wavelet kernel test

	if (FLAG_WAVELET_KERNEL_TEST):
		print("-- wavelet kernel test.")

		ldprint(["Wavelet scale:       ", wavelet_scale()])
		ldprint(["Wavelet gauss sigma: ", wavelet_gauss_sigma()])
		ldprint(["Wavelet gauss waves: ", wavelet_gauss_waves()])

		dt = SAMPLING_INTERVAL

		ldprint(["Sampling frequency: ", 1.0 / dt])

		f = ANALYZED_FREQUENCY # analyzed frequenccy [Hz]
		ldprint(["Analyzed frequency: ", f])

		rkernel, ikernel, kernelsize = morlet_kernel(f, dt)
		ldprint(["Kernel size: ", kernelsize])

		footsize = foot_size(kernelsize)
		ldprint(["Foot size:   ", footsize])

		tlist = []
		for i in range(-footsize, footsize + 1):
			t = dt * i
			tlist.append(t)
		tlist = np.array(tlist)

		plt.plot(tlist, rkernel, color='black')
		plt.plot(tlist, ikernel, color='black', linestyle='dashed')
		plt.axvline(0.0)
		if (footsize * dt >= 1.0):
			plt.axvline(1.0)
		plt.title("Morlet kernel ({0:.3f} [Hz])".format(f))
		plt.xlabel("Time [sec]")
		plt.ylabel("Amplitude")
		plt.show()
		plt.close()

	# wavelet transform test

	if (FLAG_WAVELET_TRANSFORM_TEST):
		print("-- wavelet transform test.")

		dt = SAMPLING_INTERVAL
		data_samplings = SAMPLINGS
		f = ANALYZED_FREQUENCY # analyzed frequenccy [Hz]

		data = []
		for i in range(data_samplings):
			t = dt * i
			"""
			signal = sin(omega(2.0) * t) + cos(omega(5.0) * t)
			signal = cos(omega(f) * t)
			signal = 2.0 * sin(omega(0.2) * t) + cos(omega(f) * t) + cos(omega(3.0) * t) + 3.0 * cos(omega(5.0) * t)
			"""
			signal = 2.0 * sin(omega(0.2) * t) + cos(omega(3.0) * t) + 3.0 * cos(omega(5.0) * t)
			data.append(signal)
		data = np.array(data)

		status, wt, wt_re, wt_im = wavelet_f(data, dt, f)

		tlist = []
		for i in range(len(data)):
			t = dt * i
			tlist.append(t)
		tlist = np.array(tlist)

		# Plot

		fig = plt.figure()

		axis = []
		for i in range(2):
			axis.append(fig.add_subplot(2, 1, i + 1))

		axis[0].plot(tlist, data, color='black')
		axis[0].set_title("Orignal signal")
		axis[0].set_xlabel("Time [sec]")
		axis[0].set_ylabel("Amplitude")
		axis[1].plot(tlist, wt, color='black', linestyle='dotted')
		axis[1].plot(tlist, wt_re, color='black', linestyle='solid')
		axis[1].plot(tlist, wt_im, color='black', linestyle='dashed')
		axis[1].set_title("Wavelet spectra ({0:.3} [Hz])".format(f))
		axis[1].set_xlabel("Time [sec]")
		axis[1].set_ylabel("Spectra")
		plt.show()
		plt.close()

	# wavelet transform test #2

	if (FLAG_WAVELET_TRANSFORM_TEST2):
		print("-- wavelet transform test #2.")

		dt = SAMPLING_INTERVAL
		data_samplings = SAMPLINGS
		f = ANALYZED_FREQUENCY # analyzed frequenccy [Hz]

		data = []
		for i in range(data_samplings):
			t = dt * i
			"""
			signal = sin(omega(2.0) * t) + cos(omega(5.0) * t)
			signal = cos(omega(f) * t)
			"""
			signal = 2.0 * sin(omega(0.2) * t) + cos(omega(f) * t) + cos(omega(3.0) * t) + 3.0 * cos(omega(5.0) * t)
			data.append(signal)
		data = np.array(data)

		statuslist, wt, wt_r, wt_i = wavelet(data, dt, pseudo_logticks(0.01, 2.0)[::-1]) # RETURN: statuslist: status list, wt: wavelet power array, wt_r: wavelet real component array, wt_i: wavelet imaginary component array

	# 2D array correlation test

	if (FLAG_2DARRAY_CORRELATION_TEST):
		print("-- 2D array correlation test.")
		#with h5.File("./data/HDF5/Format/TMDU001_data_L.h5", 'r') as f:
		with h5.File("../data/resp/TMDU001_data_L.h5", 'r') as f:
			index = "{0}/{1}/{2}/Data".format(0, 'NOR', 0)
			print("Index:", index)
			d = f[index][()]
		corr = correlate_ndarray(d, d)
		print("Corr: ", corr)

	# Phase-shifted 2D array correlation test

	if (FLAG_PHASESHIFTED_2DARRAY_CORRELATION_TEST):
		print("-- phase-shifted 2D array correlation test.")
		#with h5.File("./waveletdata/TMDU001_L_NOR_0000_0000_ws.h5", 'r') as f:
		with h5.File("../data/resp/TMDU001_NOR_L_0000_0000_ws.h5", 'r') as f:
			d = f['Data'][()]
		for i in range(-50, 50):
			corr = correlate_phaseshifted_2darray(d, d, i)
			print("Corr: ", corr)

