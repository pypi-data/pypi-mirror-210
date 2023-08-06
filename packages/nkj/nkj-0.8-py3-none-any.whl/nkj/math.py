#
# [name] nkj.math.py
# [exec] python -m nkj.math
#
# Written by Yoshikazu NAKAJIMA
#
_LIB_DEBUGLEVEL = 0

import os
import sys
import numpy as np
import math
from scipy.spatial.transform import Rotation as R
import copy
import numbers
from functools import singledispatch

sys.path.append(os.path.abspath(".."))
import nkj.str as ns
from nkj.str import *
import nkj.prob as p

#-- flags

ENABLE_MULOPERATOR_FOR_GEOMETRYCOMPUTATION = False
ENABLE_MULOPERATOR_FOR_CSTRANS3D_CLASS = ENABLE_MULOPERATOR_FOR_GEOMETRYCOMPUTATION
ENABLE_MULOPERATOR_FOR_MAT4X4_CLASS = ENABLE_MULOPERATOR_FOR_GEOMETRYCOMPUTATION
ENABLE_MULOPERATOR_FOR_POINT3D_CLASS = ENABLE_MULOPERATOR_FOR_GEOMETRYCOMPUTATION
ENABLE_MULOPERATOR_FOR_LINE3D_CLASS = ENABLE_MULOPERATOR_FOR_GEOMETRYCOMPUTATION
ENABLE_MULOPERATOR_FOR_PLANE3D_CLASS = ENABLE_MULOPERATOR_FOR_GEOMETRYCOMPUTATION

#-- global functions

def is_scalar(x):
	return isinstance(x, numbers.Number)

def is_geometric_primitive(x):
	ty = type(x)
	flag = False
	for object in [point3d, line3d, plane3d]:
		flag |= ty is object
	return flag

def is_geometric(x):
	return is_geometric_primitive(x)

def ndim(x):
	return np.ndim(x)

def shape(x):
	return np.shape(x)

def sq(x):
	return x * x

def sqrt(x):
	return np.sqrt(x)

def rad2deg(x):
	#return (x * 180.0 / np.pi)
	return math.degrees(x)

def deg2rad(x):
	#return (x * np.pi / 180.0)
	return math.radians(x)

def rad2deg4list(radlist):
	deglist = []
	for i in range(len(radlist)):
		deglist.append(rad2deg(radlist[i]))
	return deglist

def deg2rad4list(deglist):
	radlist = []
	for i in range(len(deglist)):
		radlist.append(deg2rad(deglist[i]))
	return radlist

def sigmoid(x, tau=1.0, x0=0.0):
	return 1.0 / (1.0 + np.exp(-(x - x0) / tau))

def vecnorm(v):
	if (type(v) is not np.ndarray):
		v = np.array(v)
	return np.linalg.norm(v)

def norm(x):
	if (type(x) is np.ndarray):
		if (x.ndim == 1):
			return vecnorm(x)
		else:
			___ERROR___
	else:
		___ERROR___

def vecnormalize(v):
	ty = type(v)
	if (ty is list or ty is tuple):
		v = np.array(v)
	vlen = vecnorm(v)
	if (vlen != 0):
		v = v / vlen   # np.array の要素に対して、v /= vlen はできない
	if (ty is np.ndarray):
		pass
	elif  (ty is list):
		v = [v[0], v[1], v[2]]
	elif  (ty is tuple):
		v = (v[0], v[1], v[2])
	return v

def normalize(x):
	if (type(x) is np.ndarray):
		if (x.ndim == 1):
			return vecnormalize(x)
		else:
			___ERROR___
	else:
		___ERROR___

def vecangle(basev, v):
	u = basev
	nu = vecnorm(u)
	nv = vecnorm(v)
	if (nu == 0.0):
		return 0.0
	if (nv == 0.0):
		return 0.0
	u = u / nu # normalize
	v = v / nv # normalize
	c = np.inner(u, v)
	s = np.linalg.norm(np.cross(u, v)) # np.cross() は、ベクトルが両方とも2次元の場合はスカラー返すが、3次元の場合は3次元ベクトルを返す。
	return np.arctan2(s, c)

def angle(base, target):
	if (base is None or target is None):
		___ERROR___
	if (type(base) is list or type(base) is tuple):
		base = np.array(base)
	if (type(target) is list or type(target) is tuple):
		base = np.array(target)
	if (type(base) is np.ndarray and type(target) is np.ndarray):
		return vecangle(base, target)
	elif (type(base) is vec3d and type(target) is vec3d):
		return vecangle(base.get(), target.get())
	elif (type(base) is line3d and type(target) is line3d):
		return vecangle(base.getVector(), target.getVector())
	elif (type(base) is plane3d and type(target) is plane3d):
		return vecangle(base.getNormal(), target.getNormal())
	elif (type(base) is plane3d and type(target) is line3d):
		return np.pi / 2.0 - vecangle(base.getNormal(), target.getVector())
	elif (type(base) is line3d and type(target) is plane3d):
		return np.pi / 2.0 - vecangle(base.getVector(), target.getNormal())
	else:
		___ERROR___

def normalized(x):
	return x.normalized()

def inversed(x):
	return x.inversed()

def transposed(x):
	return x.transposed()

def conjugated(x):
	return x.conjugated()

def decimal_unit(x):
	if (x == 0.0):
		return 0.0
	elif (x > 0.0):
		sign = 1.0
	else:
		sign = -1.0
		x = -x
	unit = 1.0
	if (x > 1.0):
		while (unit < x):
			unit *= 10.0
		if (unit > x):
			unit /= 10.0
	else: # 0.0 < x < 1.0
		while (unit > x):
			unit /= 10.0
	return sign * unit

def logticks(min, max, ticks=10):
	ldprint2(["--> logticks({0}, {1}, {2})".format(min, max, ticks)])
	if (min < 0.0 or max < 0.0):
		print_error("Illegal arguments.")
		return None
	if (min > max):
		print_error("Illegal arguments.")
		return None
	if (ticks < 0):
		print_error("Illegal ticks.")
		return None
	tick_interval = 1.0 / float(ticks)
	ldprint3(["Tick interval: {0}".format(tick_interval)])
	min_log10 = np.log10(min)
	max_log10 = np.log10(max)
	unit_min_log10 = int(np.ceil(min_log10 * ticks))
	unit_max_log10 = int(np.floor(max_log10 * ticks))
	ldprint3(["min: {0} -> log10(min): {1} -> {2}".format(min, min_log10, unit_min_log10)])
	ldprint3(["max: {0} -> log10(max): {1} -> {2}".format(max, max_log10, unit_max_log10)])
	xlist = []
	if (min_log10 * ticks < unit_min_log10):
		xlist.append(min)
	for unit_tick_log10 in range(unit_min_log10, unit_max_log10 + 1):
		tick_log10 = unit_tick_log10 * tick_interval
		ldprint3(["Tick_log10: {0}".format(tick_log10)])
		tick = np.power(10.0, tick_log10)
		xlist.append(tick)
	if (max_log10 * ticks > unit_max_log10):
		xlist.append(max)
	ldprint(["xlist: ", xlist])
	ldprint2(["<-- logticks()"])
	return xlist

def pseudo_logticks(min, max, tick_scale=1.0):
	ldprint2(["--> pseudo_logticks({0}, {1}, {2})".format(min, max, tick_scale)])
	if (min < 0.0 or max < 0.0):
		print_error("Illegal arguments.")
		return None
	if (min > max):
		print_error("Illegal arguments.")
		return None
	if (tick_scale <= 0.0 or tick_scale > 1.0):
		print_error("Illegal tick scale.")
		return None
	min_unit = decimal_unit(min)
	max_unit = decimal_unit(max)
	if (max_unit < max):
		max_unit *= 10.0
	ldprint3(["unit: ", min, " -> ", min_unit])
	ldprint3(["unit: ", max, " -> ", max_unit])
	min_log10 = int(np.log10(min_unit))
	max_log10 = int(np.log10(max_unit))
	ldprint3(["log10: ", min_unit, " -> ", min_log10])
	ldprint3(["log10: ", max_unit, " -> ", max_log10])
	xlist = []
	for i in range(min_log10, max_log10):
		ldprint3(["log10: ", i])
		unit = np.power(10.0, i)
		ldprint3(["unit: ", unit])
		j_max = int(10.0 / tick_scale)
		for j in range(1, j_max):
			val = unit * tick_scale * j
			if (val < min):
				hval = unit * tick_scale * (j + 1)
				if (min < hval):
					xlist.append(min)
			elif (val < max):
				xlist.append(val)
			else:
				xlist.append(max)
				break
		if (val < max and max <= np.power(10.0, i + 1)):
			xlist.append(max)
	"""
	xlist = list(set(xlist))
	xlist = xlist.sort()
	"""
	ldprint2(["xlist: ", xlist])
	ldprint2(["<-- pseudo_logticks()"])
	return xlist

def _mat_4x4to3x3(m4):
	ty = type(m4)
	if (ty is cstrans3d):
		m43 = m4.getMatrix()
		ty = type(m4)
	if (ty is list):
		return [[m4[0, 0], m4[0, 1], m4[0, 2]],
		        [m4[1, 0], m4[1, 1], m4[1, 2]],
		        [m4[2, 0], m4[2, 1], m4[2, 2]]]
	elif (ty is tuple):
		return ((m4[0, 0], m4[0, 1], m4[0, 2]),
		        (m4[1, 0], m4[1, 1], m4[1, 2]),
		        (m4[2, 0], m4[2, 1], m4[2, 2]))
	elif (ty is np.ndarray):
		return np.array([[m4[0, 0], m4[0, 1], m4[0, 2]],
		                 [m4[1, 0], m4[1, 1], m4[1, 2]],
		                 [m4[2, 0], m4[2, 1], m4[2, 2]]])
	else:
		___ERROR___

def to3x3(m4):
	return _mat_4x4to3x3(m4)

def _mat_3x3to4x4(m3):
	ty = type(m3)
	if (ty is csrot3d):
		m3 = m3.getMatrix()
		ty = type(m3)
	if (ty is list):
		m = [[m3[0, 0], m3[0, 1], m3[0, 2], 0.0],
		     [m3[1, 0], m3[1, 1], m3[1, 2], 0.0],
		     [m3[2, 0], m3[2, 1], m3[2, 2], 0.0],
		     [0.0, 0.0, 0.0, 1.0]]
	elif (ty is tuple):
		m = ((m3[0, 0], m3[0, 1], m3[0, 2], 0.0),
		     (m3[1, 0], m3[1, 1], m3[1, 2], 0.0),
		     (m3[2, 0], m3[2, 1], m3[2, 2], 0.0),
		     (0.0, 0.0, 0.0, 1.0))
	elif (ty is np.ndarray):
		m = np.array([[m3[0, 0], m3[0, 1], m3[0, 2], 0.0],
		              [m3[1, 0], m3[1, 1], m3[1, 2], 0.0],
		              [m3[2, 0], m3[2, 1], m3[2, 2], 0.0],
		              [0.0, 0.0, 0.0, 1.0]])
	else:
		___ERROR___
	return m

def to4x4(m3):
	return _mat_3x3to4x4(m3)

def tovec3(v):
	return v[0:3]

def vec3(v):
	return tovec3(v)

def tovec4(v):
	dprint2('--> nkj.math.tovec4')
	dprint2('v: {0}'.format(v))
	if (len(v) == 3):
		if (type(v) is np.ndarray):
			v = np.append(v, 1.0)
		elif (type(v) is list or type(v) is tuple):
			v = v.append(1.0)
		else:
			___ERROR___
	elif (len(v) == 4):
		if (type(v) is np.ndarray):
			pass
		else:
			v = np.array(v)
	else:
		___ERROR___
	dprint2('v: {0}'.format(v))
	dprint2('<-- nkj.math.tovec4')
	return v

def vec4(v):
	return tovec4(v)

def offsetTransform(r, base):
	if (type(r) is np.ndarray):
		r = to4x4(r)
	else:
		return base @ r @ base.inv

def offset_transform(r, base):
	return offsetTransformation(r, base)

def offset(a, base):
	ty = type(a)
	if (ty is np.ndarray):
		sh = a.shape
		if (sh == (4, 4) or sh == (3, 4)):
			return offsetTransformation(a, base)
		else:
			___ERROR___
	elif (ty is list or ty is tuple):
		sh = shape(a)
		___NOT_IMPLEMENTED___
	elif (ty is trans3d):
		return offsetTransformation(a, base)
	else:
		___ERROR___

#-- classes

class complex():
	_classname = "nkj.math.complex"
	
	def __init__(self, x, y):
		#-- instance variables
		self._x = x
		self._y = y
	
	def __str__(self):
		return ns.concat(["(x, y): (", str(self.re()), ", ", str(self.im()), ")"])

	def __not__(self):
		return complex(self.re(), -self.im())

	def __add__(self, second):
		return complex(self.re() + second.re(), self.im() + second.im())

	def __sub__(self, second):
		return complex(self.re() - second.re(), self.im() - second.im())

	def __mul__(self, second): # 複素共役を掛け算
		ldprint(["self:   ", str(self)])
		ldprint(["second: ", str(second)])
		return self.re() * second.re() + self.im() * second.im()

	def __inv__(self): # '~'
		return self.normalized()

	def __getitem__(self, i):
		if (i == 0):
			return self._x
		elif (i == 1):
			return self._y
		else:
			return ValueError

	def __setitem__(self, i, second):
		if (i == 0):
			self._x = second
		elif (i == 1):
			self._y = second
		else:
			None

	@classmethod
	def getClassName(cls):
		return complex._classname

	@classmethod
	@property
	def classname(cls):
		return cls.getClassName()

	def set(self, x, y):
		self._x = x
		self._y = y

	def re(self):
		return self._x

	def im(self):
		return self._y

	def conjugated(self):
		return complex(self.re(), -self.im())

	def conj(self):
		return self.conjugated()

	def norm(self):
		return sq(self.re()) + sq(self.im())

	def normalized(self):
		norm = self.norm()
		if (norm == 0.0):
			return ValueError
		else:
			return complex(self.re() / norm, self.im() / norm)

	def phase(self): # 戻り値の範囲は [-pi, pi]
		return np.arctan2(self.im(), self.re())

#--- geometry

_DEFAULT_ROT2D = 0.0   # degree

class csrot2d():
	_classname = 'nkj.math.csrot2d'

	def __init__(self, a=None):
		self._a = a

_DEFAULT_QUAT = np.array([1.0, 0.0, 0.0, 0.0])   # (w, x, y, z)
_DEFAULT_CSROT3D = _DEFAULT_QUAT

class csrot3d():
	_classname = 'nkj.math.csrot3d'

	def __init__(self, a=None, flag=None, axis=None):
		if (a is None):
			self.set(_DEFAULT_CSROT3D)
		else:
			self.set(a, flag, axis)

	def __str__(self, title=None):
		return self.getPrintStr(title)

	def __mul__(self, second):
		return self.getMultipliedLocal(second)

	def __rmul__(self, first):
		return self.getMultipliedGlobal(first)

	def __matmul__(self, second):
		return self.__mul__(second)

	def __rmatmul__(self, first):
		return self.__rmul__(first)

	def __invert__(self):
		return self.getInversed()

	@classmethod
	def getClassName(cls):
		return quat._classname

	@classmethod
	@property
	def classname(cls):
		return cls.getClassName()

	def get(self):
		return self.array()

	def getAngle(self):
		return self.R.magnitude()

	def getAxis(self):
		return vecnormalize(self.R.as_rotvec())

	def getInversed(self):
		return csrot3d(self._r.inv())

	def getConjugated(self):
		return csrot3d(self.npquat.conjugate())

	def getMultipliedScalar(self, value):
		return carot3d(value * self.as_rotvec(), 'rotvec')

	def getMultipliedLocal(self, second):
		ldprint(["--> getMultipliedLocal()"])
		if (type(second) is csrot3d):
			return csrot3d(self._r @ second._r)
		elif (type(second) is R):
			return csrot3d(self._r @ second)
		elif (type(second) is list or type(second) is tuple):
			if (ndim(second) == 2):
				if (shape(second) == (3, 3)):
					return self.getMultipliedLocal(csrot3d(second))
				else:
					___ERROR___
			else:
				___ERROR___
		elif (type(second) is np.ndarray):
			if (second.dim == 2):
				if (second.shape == (3, 3)):
					return self.getMultipliedLocal(csrot3d(second))
				else:
					___ERROR___
			else:
				___ERROR___
		elif (is_scalar(second)):
			return getMultipliedScalar(second)
		else:
			___ERROR___

	def multipliedLocal(self, second):
		return self.getMultipliedLocal(second)

	def getMultipliedGlobal(self, first):
		if (type(first) is csrot3d):
			return csrot3d(first._r @ self._r)
		elif (type(first) is R):
			return csrot3d(first @ self._r)
		elif (type(first) is list or type(first) is tuple):
			if (ndim(first) == 2):
				if (shape(first) == (3, 3)):
					return self.getMultipliedGlobal(csrot3d(first))
				else:
					___ERROR___
			else:
				___ERROR___
		elif (type(first) is np.ndarray):
			if (first.dim == 2):
				if (first.shape == (3, 3)):
					return self.getMultipliedGlobal(csrot3d(first))
				else:
					___ERROR___
			else:
				___ERROR___
		elif (is_scalar(first)):
			return getMultipliedScalar(first)
		else:
			___ERROR___

	def multipliedGlobal(self, second):
		return self.getMultipliedGlobal(second)

	def getRotatedLocal(self, r, flag=None):
		return self.getMultiplinedLocal(csrot3d(r, flag))

	def rotatedLocal(self, r, flag=None):
		return self.getRotatedLocal(r, flag)

	def getRotatedGlobal(self, r, flag=None):
		return self.getMultiplinedGlobal(csrot3d(r, flag))

	def rotatedGlobal(self, second):
		return self.getRotatedGlobal(second)

	def getPrintStr(self, title=None):
		if (title is None):
			mesg = ''
		else:
			mesg = '{0}: '.format(title)
		q = self.quat
		w = q[0]; x = q[1]; y = q[2]; z = q[3]
		c = w
		s = np.sqrt(x**2 + y**2 + z**2)
		angle = 2.0 * np.arctan2(s, c)
		if (s == 0.0):
			rotaxis = (x, y, z)
		else:
			rotaxis = (x / s, y / s, z / s)
		mesg += 'angle: {0:.3f} deg, '.format(rad2deg(angle))
		mesg += 'axis: ({0:.3f}, {1:.3f}, {2:.3f})'.format(rotaxis[0], rotaxis[1], rotaxis[2])
		return mesg

	def _normalize(self, a):
		mag = np.sqrt(a[0]**2 + a[1]**2 + a[2]**2 + a[3]**2)
		if (mag == 0.0):
			return a
		else:
			return a / mag 

	def _array_np2r(self, a):
		a = self._normalize(a)
		return [a[1], a[2], a[3], a[0]] # (w, x, y, z) to (x, y, z, w)

	def _array_r2np(self, a):
		a = self._normalize(a)
		return [a[3], a[0], a[1], a[2]] # (x, y, z, w) to (w, x, y, z)

	def set(self, a, flag=None, axis=None):
		ldprint('--> csrot3d.set()')
		ty = type(a)
		if (ty is csrot3d):
			self._r = a._r
		elif (ty is R):
			self._r = a
		elif (ty is list or ty is tuple):
			dim = ndim(a)
			if (dim == 1):
				sh = shape(a)
				if (sh == (4,)):
					if (flag is None or flag == 'quaternion' or flag == 'quat'):
						self._r = R.from_quat(self._array_np2r(a)) # quaternion
					elif (flag == 'R.quaternion' or flag == 'rquat'):
						self._r = R.from_quat(copy.copy(a))
					else:
						___ERROR___
				elif (sh == (3,)):
					if (flag is None or flag == 'rotationalvector' or flag == 'rotvec'):
						self._r = R.from_rotvec(copy.copy(a))
					elif (flag == 'directioncosines' or flag == 'dircos'):
						if (axis is None):
							axis = np.array([0, 0, 1])
						x = vecnormalize(copy.copy(a))
						axis = vecnormalize(axis)
						raxis = np.cross(axis, x)
						angle = vecangle(axis, x)
						rvec = angle * raxis
						self.set(rvec, 'rotvec')
					elif (flag == 'directionangles' or flag == 'dirang'):
						r = [np.cos(a[0]), np.cos(a[1]), np.cos(a[2])]
						self.set(r, 'dircos')
					elif (flag == 'euler_zyx'):
						self._r = R.from_euler('zyx', copy.copy(a)) # extrinsic rotation
					elif (flag == 'euler_ZYX'):
						self._r = R.from_euler('ZYX', copy.copy(a)) # intrinsic rotation
					elif (flag == 'euler_xyx'):
						self._r = R.from_euler('xyx', copy.copy(a))
					elif (flag == 'euler_XYX'):
						self._r = R.from_euler('XYX', copy.copy(a))
					else:
						___ERROR___
				elif (sh == (2,)):
					if (flag is None or flag == 'anglevec' or flag == 'angleaxis'):
						angle = a[0]
						if (not is_scalar(angle)):
							___ERROR___
						vec = a[1]
						if (shape(vec) == (3,)):
							rvec = angle * vecnormalize(np.array(vec))
							self.set(rvec, 'rotvec')
						else:
							___ERROR___
					else:
						___ERROR___
				else:
					___ERROR___
			elif (dim == 2):
				sh = shape(a)
				if (sh == (3, 3)):
					if (flag is None or flag == 'matrix' or flag == 'mat'):
						self._r = R.from_matrix(copy.copy(a))
					else:
						___ERROR___
				else:
					___ERROR___
			else:
				___ERROR___
		elif (ty is np.ndarray):
			dim = a.ndim
			if (dim == 1):
				sh = a.shape
				if (sh == (4,)):
					if (flag is None or flag == 'quaternion' or flag == 'quat'):
						self._r = R.from_quat(self._array_np2r(a))
					elif (flag == 'R.quaternion' or flag == 'rquat'):
						self._r = R.from_quat(copy.copy(a))
					else:
						___ERROR___
				elif (sh == (3,)):
					if (flag is None or flag == 'rotationalvector' or flag == 'rotvec'):
						self._r = R.from_rotvec(copy.copy(a))
					elif (flag == 'euler_zyx'):
						self._r = R.from_euler('zyx', copy.copy(a)) # extrinsic rotation
					elif (flag == 'euler_ZYX'):
						self._r = R.from_euler('ZYX', copy.copy(a)) # intrinsic rotation
					elif (flag == 'euler_xyx'):
						self._r = R.from_euler('xyx', copy.copy(a))
					elif (flag == 'euler_XYX'):
						self._r = R.from_euler('XYX', copy.copy(a))
					else:
						___ERROR___
				elif (sh == (2,)):
					if (flag is None or flag == 'anglevec' or flag == 'angleaxis'):
						angle = a[0]
						if (not is_scalar(angle)):
							___ERROR___
						vec = a[1]
						if (shape(vec) == (3,)):
							rvec = angle * vecnormalize(np.array(vec))
							self.set(rvec, 'rotvec')
						else:
							___ERROR___
					else:
						___ERROR___
				else:
					___ERROR___
			elif (dim == 2):
				sh = a.shape
				if (sh == (3, 3)):
					self._r = R.from_matrix(copy.deepcopy(a)) # 3x3 matrix
				elif (sh == (4, 4)):
					self._r = R.from_matrix(_mat_4x4to3x3(a)) # 4x4 matrix
				else:
					___ERROR___
			else:
				___ERROR___
		else:
			___ERROR___
		ldprint('<-- csrot3d.set()')

	def getR(self):
		return self._r

	@property
	def R(self):
		return self.getR()

	def setR(self, r):
		self.set(r)

	@R.setter
	def R(self, second):
		self.setR(second)

	@property
	def rquatarray(self):
		return self._r.as_quat()

	@rquatarray.setter
	def rquatarray(self, second):
		set.set(second)

	@property
	def rquat(self):
		return self.rquatarray

	@rquat.setter
	def rquat(self, second):
		self.set(second)

	@property
	def npquatarray(self):
		return self._array_r2np(self._r.as_quat())

	@npquatarray.setter
	def npquatarray(self, second):
		self.set(second, 'np.quaternion')

	@property
	def quat(self):
		return self.rquatarray

	@quat.setter
	def quat(self, second):
		self.set(second, 'quaternion')

	def getMatrix(self):
		return self._r.as_matrix()

	@property
	def matrix(self):
		return self.getMatrix()

	@property
	def mat(self):
		return self.getMatrix()

	@property
	def m(self):
		return self.getMatrix()

	def setMatrix(self, second):
		self.set(second)

	@matrix.setter
	def matrix(self, second):
		self.setMatrix(second)

	@mat.setter
	def mat(self, second):
		self.setMatrix(second)

	@m.setter
	def m(self, second):
		self.setMatrix(second)

	@property
	def rotvec(self):
		return self._r.as_rotvec()

	@rotvec.setter
	def rotvec(self, second):
		self.set(second, 'rotvec')

	@property
	def mrp(self): # Modified Rodrigues Parameters (MRPs)
		return self._r.as_mrp()

	@mrp.setter
	def mrp(self, second):
		self.set(second, 'mrp')

	def euler(self, flag=None):
		if (flag is None):
			return self._r.as_euler()
		else:
			return self._r.as_euler(flag)

	@property
	def w(self):
		return self.rquat[3]

	@property
	def x(self):
		return self.rquat[0]

	@property
	def y(self):
		return self.rquat[1]

	@property
	def z(self):
		return self.rquat[2]

	@property
	def rx(self):
		return self.rotvec[0]

	@property
	def ry(self):
		return self.rotvec[1]

	@property
	def rz(self):
		return self.rotvec[2]

	@property
	def angle(self):
		return self.getAngle()

	@property
	def ang(self):
		return self.angle

	@property
	def axis(self):
		return self.getAxis()

	@property
	def vec(self):
		return self.axis

	@property
	def v(self):
		return self.axis

	@property
	def inversed(self):
		return self.getInversed()

	@property
	def inv(self):
		return self.inversed

	@property
	def i(self):
		return self.inversed

	def inverse(self):
		self.set(self.getInversed())

	@property
	def conjugated(self):
		return self.getConjugated()

	@property
	def conj(self):
		return self.conjugated

	@property
	def c(self):
		return self.conjugated

	def conjugate(self):
		self.set(self.GetConjugated())

	def rorated(self, a):
		return self.getRotated()

	def rorate(self, a):
		self.set(self.rorated(a))

	def print(self, title=None):
		print(self.getPrintStr(title))

_DEFAULT_CSTRANS3D = [np.array([1.0, 0.0, 0.0, 0.0]), np.array([0.0, 0.0, 0.0])]

class cstrans3d():
	_classname = 'nkj.math.cstrans3d'

	def __init__(self, a=None, flag=None):
		if (a is None):
			self.set(_DEFAULT_CSTRANS3D)
		else:
			self.set(a, flag)

	def __str__(self, title=None):
		return self.getPrintStr(title)

	def __matmul__(self, second):
		return self.getMultipliedGlobal(second)

	def __rmatmul__(self, first):
		return self.getMultipliedLocal(first)

	if (ENABLE_MULOPERATOR_FOR_CSTRANS3D_CLASS):
		def __mul__(self, second):
			return self.__matmul__(second)

		def __rmul__(self, first):
			return self.__rmatmul__(first)

	def __invert__(self):
		return self.getInversed()

	@classmethod
	def getClassName(cls):
		return cstrans3d._classname

	@classmethod
	@property
	def classname(cls):
		return cls.getClassName()

	def getMultipliedScalar(self, value):
		r = value * self._r.rotvec
		t = value * self._t
		return cstrans3d([r.quat, t])

	def multipliedScalar(self, value):
		return self.getMultipliedScalar(value)

	def getMultipliedGlobal(self, second):
		ty = type(second)
		if (ty is csrot3d):
			return cstrans3d(self.matrix @ to4x4(second.getMatrix()))
		elif (ty is cstrans3d):
			return cstrans3d(self.matrix @ second.getMatrix())
		elif (ty is list or ty is tuple):
			if (ndim(second) == 2):
				m = second
				if (shape(m) == (3, 3)):
					return self.getMultipliedGlobal(csrot3d(m))
				elif (shape(m) == (4, 4)):
					return self.getMultipliedGlobal(cstrans3d(m))
				else:
					___ERROR___
			elif (ndim(second) == 1): # vector
				v = second
				return self.getMultipliedGlobal(np.array(v, dtype=np.float32))
			else:
				___ERROR___
		elif (ty is np.ndarray):
			if (second.ndim == 2):
				m = second
				if (m.shape == (3, 3)):
					return self.getMultipliedGlobal(csrot3d(m))
				elif (m.shape == (4, 4)):
					return self.getMultipliedGlobal(cstrans3d(m))
				else:
					___ERROR___
			elif (second.ndim == 1): # vector
				v = second
				if (v.shape == (3,)):
					return tovec3(self.getMultipliedGlobal(tovec4(v)))
				elif (v.shape == (4,)):
					m = self.matrix
					return m @ v
				else:
					___NOT_IMPLEMENTED___
			else:
				___ERROR___
		elif (is_scalar(second)):
			return getMultipliedScalar(second)
		elif (is_geometric(second)):
			return second.getMultiplied(self)
		else:
			___ERROR___

	def multipliedGlobal(self, second):
		return getMultipliedGlobal(second)

	def getMultipliedLocal(self, first):
		ty = type(first)
		if (ty is csrot3d):
			return cstrans3d(to4x4(first.getMatrix()) @ self.matrix)
		elif (ty is cstrans3d):
			return cstrans3d(first.getMatrix() @ self.matrix)
		elif (ty is list or ty is tuple):
			if (ndim(first) == 2):
				m = first
				if (shape(m) == (3, 3)):
					return self.getMultipliedLocal(csrot3d(m))
				elif (shape(m) == (4, 4)):
					return self.getMultipliedLocal(cstrans3d(m))
				else:
					___ERROR___
			elif (ndim(first) == 1): # vector
				v = first
				return self.getMultipliedLocal(np.array(v, dtype=np.float32))
			else:
				___ERROR___
		elif (ty is np.ndarray):
			if (first.ndim == 2):
				m = first
				if (m.shape == (3, 3)):
					return self.getMultipliedLocal(csrot3d(m))
				elif (m.shape == (4, 4)):
					return self.getMultipliedLocal(cstrans3d(m))
				else:
					___ERROR___
			elif (first.ndim == 1): # vector
				v = first
				return self.getMultipliedGlobal(v) # The same value is returned.
			else:
				___ERROR___
		elif (is_scalar(secon)):
			return getMultipliedScalar(secon)
		elif (is_geometric(secon)):
			return first.getMultiplied(self)
		else:
			___ERROR___

	def multipliedLocal(self, first):
		return getMultipliedLocal(first)

	def getPrintStr(self, title=None):
		if (title is None):
			mesg = ''
		else:
			mesg = '{0}: '.format(title)
		mesg += 'r:('
		mesg += self._r.getPrintStr()
		mesg += '), t:({0:.3f}, {1:.3f}, {2:.3f})'.format(self._t[0], self._t[1], self._t[2])
		return mesg

	def set(self, a, flag=None):
		ldprint(['--> set({0}, \'{1}\')'.format(a, flag)])
		ty = type(a)
		if (ty is cstrans3d):
			self._r = a._r
			self._t = a._t
			if (flag is not None):
				___ERROR___
		elif (ty is list or ty is tuple):
			sh = shape(a)
			if (sh == (2,) or sh == (2, 3)):
				r = a[0]
				t = a[1]
				ldprint("r: {0}".format(r))
				ldprint("t: {0}".format(t))
				self._r = csrot3d(r, flag)
				self._t = np.array([t[0], t[1], t[2]])
			else:
				___ERROR___
		elif (ty is np.ndarray):
			sh = a.shape
			if (sh == (3, 3)):
				self._r = csrot3d([[a[0, 0], a[0, 1], a[0, 2]],
				                   [a[1, 0], a[1, 1], a[1, 2]],
				                   [a[2, 0], a[2, 1], a[2, 2]]])
			elif (sh == (3, 4) or sh == (4, 4)):
				self._r = csrot3d([[a[0, 0], a[0, 1], a[0, 2]],
				                   [a[1, 0], a[1, 1], a[1, 2]],
				                   [a[2, 0], a[2, 1], a[2, 2]]])
				self._t = np.array([a[0, 3], a[1, 3], a[2, 3]])
		else:
			___ERROR___

	@property
	def R(self):
		return self._r.R

	@R.setter
	def R(self, second):
		self._r.set(R)

	@property
	def rquatarray(self):
		return self._r.rquatarray

	@rquatarray.setter
	def rquatarray(self, second):
		self._r.set(second)

	@property
	def rquat(self):
		return self.rquatarray

	@rquat.setter
	def rquat(self, second):
		self.set(second)

	@property
	def npquatarray(self):
		return self._r.npquatarray

	def getQuat(self):
		return self._r.quat

	@property
	def quat(self):
		return self.getQuat()

	def setQuat(self, second):
		self.set(second, 'quaternion')

	@quat.setter
	def quat(self, second):
		self.setQuat(second)

	def getRotationalMatrix(self):
		return self._r.matrix

	def getRotationMatrix(self):
		return self.getRotationalMatrix()

	def getRotMatrix(self):
		return self.getRotationalMatrix()

	def getRM(self):
		return self.getRotationalMatrix()

	@property
	def rotmatrix(self):
		return self.getRotMatrix()

	@property
	def rotmat(self):
		return self.getRotMatrix()

	@property
	def rmat(self):
		return self.getRotMatrix()

	@property
	def rm(self):
		return self.getRotMatrix()

	def setRotationalMatrix(self, second):
		self.set(second)

	def setRotationMatrix(self, second):
		self.setRotationalMatrix(second)

	def setRotMatrix(self, second):
		self.setRotationalMatrix(second)

	def setRM(self, second):
		self.setRotationalMatrix(second)

	@rotmatrix.setter
	def rotmatrix(self, second):
		self.setRotationalMatrix(second)

	@rotmat.setter
	def rotmat(self, second):
		self.setRotationalMatrix(second)

	@rmat.setter
	def rmat(self, second):
		self.setRotationalMatrix(second)

	@rm.setter
	def rm(self, second):
		self.setRotationalMatrix(second)

	def getMatrix(self):
		m3 = self._r.matrix
		m4 = np.array(to4x4(m3))
		t = self._t
		m4[0, 3] = t[0]
		m4[1, 3] = t[1]
		m4[2, 3] = t[2]
		return m4

	@property
	def matrix(self):
		return self.getMatrix()

	@property
	def setRotMatrix(self, second):
		self.setRotationalMatrix(second)

	@rotmatrix.setter
	def rotmatrix(self, second):
		self.setRotMatrix(second)

	@rotmat.setter
	def rotmat(self, second):
		self.setRotMatrix(second)

	@rmat.setter
	def rmat(self, second):
		self.setRotMatrix(second)

	@rm.setter
	def rm(self, second):
		self.setRotMatrix(second)

	def getMatrix(self):
		m3 = self._r.matrix
		m4 = np.array(to4x4(m3))
		t = self._t
		m4[0, 3] = t[0]
		m4[1, 3] = t[1]
		m4[2, 3] = t[2]
		return m4

	@property
	def matrix(self):
		return self.getMatrix()

	@property
	def mat(sef):
		return self.getMatrix()

	@property
	def m(sef):
		return self.getMatrix()

	def setMatrix(self, second):
		self.set(second)

	@matrix.setter
	def matrix(self, second):
		self.setMatrix(second)

	@mat.setter
	def mat(self, second):
		self.setMatrix(second)

	@m.setter
	def m(self, second):
		self.setMatrix(second)

	def getRotvec(self):
		return self._r.as_rotvec()

	@property
	def rotvec(self):
		return self.getRotvec()

	@property
	def rvec(self):
		return self.getRotvec()

	def setRotvec(self, second):
		self.set(second, 'rotvec')

	@rotvec.setter
	def rotvec(self, second):
		self.setRotvec(second)

	@rvec.setter
	def rvec(self, second):
		self.setRotvec(second)

	def getAxes(self):
		rm = self.getRotationalMatrix()
		xaxis = rm[:, 0]
		yaxis = rm[:, 1]
		zaxis = rm[:, 2]
		return xaxis, yaxis, zaxis

	@property
	def axes(self):
		return self.getAxes()

	def setAxes(self, xaxis, yaxis, zaxis):
		rm = np.zeros((3, 3), dtype=np.float32)
		rm[:, 0] = xaxis
		rm[:, 1] = yaxis
		rm[:, 2] = zaxis
		ldprint(f'xaxis: {xaxis}')
		ldprint(f'yaxis: {yaxis}')
		ldprint(f'zaxis: {zaxis}')
		ldprint(f'{rm}')
		self.setRotationalMatrix(rm)

	@axes.setter
	def axes(self, axes):
		ldprint(f'xaxis: {axes[0]}')
		ldprint(f'yaxis: {axes[1]}')
		ldprint(f'zaxis: {axes[2]}')
		self.setAxes(axes[0], axes[1], axes[2])

	def getTranslation(self):
		return self._t

	def getTrans(self):
		return self.getTranslation()

	def getT(self):
		return self.getTranslation()

	def getOrigin(self):
		return self.getTranslation()

	def getOrig(self):
		return self.getOrigin()

	@property
	def translation(self):
		return self.getTranslation()

	@property
	def trans(self):
		return self.getTranslation()

	@property
	def t(self):
		return self.getTranslation()

	@property
	def origin(self):
		return self.getOrigin()

	@property
	def orig(self):
		return self.getOrigin()

	def setTranslation(self, second):
		self._t = np.array(second)

	def setTrans(self, second):
		self.setTranslation(second)

	def setT(self, second):
		self.setTranslation(second)

	def setOrigin(self, second):
		self.setTranslation(second)

	def setOrig(self, second):
		self.setOrigin(second)

	@translation.setter
	def translation(self, second):
		self.setTranslation(second)

	@trans.setter
	def trans(self, second):
		self.setTranslation(second)

	@t.setter
	def t(self, second):
		self.setTranslation(second)

	@origin.setter
	def origin(self, second):
		self.setOrigin(second)

	@orig.setter
	def orig(self, second):
		self.setOrigin(second)

	def getXaxis(self):
		return self.getRotMatrix()[:, 0]

	@property
	def xaxis(self):
		return getXaxis()
	
	def getYaxis(self):
		return self.getRotMatrix()[:, 1]

	@property
	def yaxis(self):
		return getYaxis()
	
	def getZaxis(self):
		return self.getRotMatrix()[:, 2]

	@property
	def zaxis(self):
		return getZaxis()
	
	def getInversed(self):
		return cstrans3d(np.linalg.inv(self.matrix))

	@property
	def inversed(self):
		return self.getInversed()

	@property
	def inv(self):
		return self.getInversed()

	@property
	def i(self):
		return self.getInversed()

	def inverse(self):
		self.set(self.getInversed())

	def getRotatedLocal(self, a, flag=None):
		return self.getMultipliedLocal(csrot3d(a, flag))

	def getRotatedGlobal(self, a, flag=None):
		return self.getMultipliedGlobal(to4x4(csrot3d(a, flag).getMatrix()))

	def getTranslatedLocal(self, a):
		t = copy.deepcopy(self)
		t.translateLocal(a)
		return t

	def getTranslatedGlobal(self, a):
		t = copy.deepcopy(self)
		t.translateGlobal(a)
		return t

	def rotateLocal(self, a, flag=None):
		self.set(self.getRotatedLocal(a, flag))

	def rotateGlobal(self, a, flag=None):
		self.set(self.getRotatedGlobal(a, flag))

	def rotate_local(self, a, flag=None):
		self.rotateLocal(a, flag)

	def rotate_global(self, a, flag=None):
		self.rotateGlobal(a, flag)

	def rotate(self, a, flag=None):
		self.rotate_local(a, flag)

	def translateLocal(self, a):
		dprint2('--> {0}.translateLocal()'.format(self.getClassName()))
		dprint2('a:    {0}'.format(a))
		dprint2('vec4: {0}'.format(tovec4(a)))
		dprint2('-- m --\n{0}\n--\n'.format(self.getMatrix()))
		dprint2('dot:  {0}'.format(self.getMatrix().dot(tovec4(a))))
		self.setTranslation(self.getTranslation() + tovec3(self.getMatrix().dot(tovec4(a))))
		dprint2('<-- {0}.translateLocal()'.format(self.getClassName()))

	def translateGlobal(self, a):
		self.setTranslation(self.getTranslation() + tovec3(a))

	def translate_local(self, a):
		self.translateLocal(self, a)

	def translate_global(self, a):
		self.translateGlobal(self, a)

	def translate(self, a):
		self.translate_local(a, flag)

	def print(self, title=None):
		print(self.getPrintStr(title))

_DEFAULT_MAT3X3 = np.identity(3)

class mat3x3():
	_classname = 'nkj.math.mat3x3'

	def __init__(self, a=None):
		if (a is None):
			self.set(_DEFAULT_MAT3X3)
		else:
			self.set(a)

	def __str__(self, title=None):
		if (title is None):
			mesg = "---\n"
		else:
			mesg = "--- {0} ---\n".format(title)
		mesg += "{0: .3f}, {1: .3f}, {2: .3f}\n".format(self._m[0][0], self._m[0][1], self._m[0][2])
		mesg += "{0: .3f}, {1: .3f}, {2: .3f}\n".format(self._m[1][0], self._m[1][1], self._m[1][2])
		mesg += "{0: .3f}, {1: .3f}, {2: .3f}\n".format(self._m[2][0], self._m[2][1], self._m[2][2])
		mesg += "---"
		return mesg

	@classmethod
	def getClassName(cls):
		return mat3x3._classname

	@classmethod
	@property
	def classname(cls):
		return cls.getClassName()

	def set(self, m):
		ldprint2(["--> set()"])
		if (type(a) is mat4x4):
			self._m = m._m
		elif (type(m) is np.ndarray):
			ldprint(["shape: {0}".format(m.shape)])
			if (m.shape == (3, 3)):
				self._m = copy.deepcopy(m) # copy を使わないと、元の配列書換えで要素が変更されてしまう。また、copy.copy()だとネストする配列には対応しないので、copy.deepcopy()を使う。
			elif (m.shape == (4,)): # 要素が'4'のみのタプル．要素が一つの場合、'(4)'ではなく、'(4,)'（カンマが必要）と書く。
				ldprint(["angle: {0:.3f}, vector: ({1: .3f}, {2: .3f}, {3: .3f})".format(rad2deg(m[0]), m[1], m[2], m[3])])
				"""
				self._m = 
				■実装すること
				"""
			else:
				___ERROR___
		else:
			___ERROR___
		ldprint2(["<-- set()"])

	def identity(self):
		self.set(np.identity(4))

	def inverse(self):
		self.set(np.linalg.inv(self.get()))

_DEFAULT_MAT4X4 = np.identity(4)

class mat4x4(): # python 3.5 より @ 演算子がサポートされたので、あえてこのクラスを使うメリットはない。
	_classname = 'nkj.math.mat4x4'
	
	def __init__(self, a=None):
		if (a is None):
			self.set(_DEFAULT_MAT4X4)
		else:
			self.set(a)

	def __str__(self, title=None):
		return getPrintStr(title)

	def __invert__(self): # '~'単項演算子
		return self.getInversed()

	def __matmul__(self, second):
		"""
		m = np.zeros((4, 4))
		for j in range(4):
			for i in range(4):
				for ii in range(4):
					m[j][i] = m[j][i] + self.array()[j][ii] * second.array()[ii][i]
		"""
		ldprint2(["second type: ", type(second)])
		if (type(second) is mat4x4):
			m = self.array() @ second.array() # np.matmul() あるいは np.dot() でも良い
		else:
			___ERROR___
		return m

	if (ENABLE_MULOPERATOR_FOR_MAT4X4_CLASS):
		def __mul__(self, second):
			return self.__matmul__(second)

	@classmethod
	def getClassName(cls):
		return mat4x4._classname

	@classmethod
	@property
	def classname(cls):
		return cls.getClassName()

	@property
	def dim(self):
		return self.array().ndim

	@property
	def size(self):
		return self.array().shape

	@property
	def array(self):
		return self._m

	def get(self):
		return self.array()

	def getInversed(self):
		return mat4x4(np.linalg.inv(self.get()))

	@property
	def inversed(self):
		return self.getInversed()

	@property
	def inv(self):
		return self.getInversed()

	@property
	def i(self):
		return self.getInversed()

	def getIdentity(self):
		return mat4x4(np.identity(4))

	@property
	def identity(self):
		return self.getIdentity()

	def getPrintStr(self, title=None):
		if (title is None):
			mesg = "---\n"
		else:
			mesg = "--- {0} ---\n".format(title)
		mesg += "{0: .3f}, {1: .3f}, {2: .3f}, {3: .3f}\n".format(self._m[0][0], self._m[0][1], self._m[0][2], self._m[0][3])
		mesg += "{0: .3f}, {1: .3f}, {2: .3f}, {3: .3f}\n".format(self._m[1][0], self._m[1][1], self._m[1][2], self._m[1][3])
		mesg += "{0: .3f}, {1: .3f}, {2: .3f}, {3: .3f}\n".format(self._m[2][0], self._m[2][1], self._m[2][2], self._m[2][3])
		mesg += "{0: .3f}, {1: .3f}, {2: .3f}, {3: .3f}\n".format(self._m[3][0], self._m[3][1], self._m[3][2], self._m[3][3])
		mesg += "---"
		return mesg

	@property
	def printstr(self):
		return self.getPrintStr()

	@property
	def str(self):
		return self.getPrintStr()

	def array(self):
		return self._m

	def set(self, m):
		ldprint2(["--> set()"])
		if (type(m) is mat4x4):
			self._m = m._m
		elif (type(m) is cstrans3d):
			self._m = m.matrix
		elif (type(m) is np.ndarray):
			ldprint(["shape: {0}".format(m.shape)])
			if (m.shape == (4, 4)):
				self._m = copy.deepcopy(m)
			elif (m.shape == (4,)): # 要素が'4'のみのタプル．要素が一つの場合、'(4)'ではなく、'(4,)'（カンマが必要）と書く。
				ldprint(["angle: {0:.3f}, vector: ({1: .3f}, {2: .3f}, {3: .3f})".format(rad2deg(m[0]), m[1], m[2], m[3])])
				"""
				self._m = 
				実装すること
				"""
				___ERROR___
			else:
				___ERROR___
		else:
			___ERROR___
		"""
		self._m = np.ndarray((4, 4))
		for j in range(4):
			for i in range(4):
				self._m[j][i] = m[j][i]
		"""
		ldprint2(["<-- set()"])

	def inverse(self):
		self.set(self.getInversed())

	def getRotation(self):
		return to3x3(self._m)

	def getColumn3(self, i):
		return self._m[:3, i]

	def getXaxis(self):
		return self.getColumn3(0)

	@property
	def xaxis(self):
		return self.getXaxis()

	def getYaxis(self):
		return self.getColumn3(0)

	@property
	def yaxis(self):
		return self.getYaxis()

	def getZaxis(self):
		return self.getColumn3(0)

	@property
	def zaxis(self):
		return self.getZaxis()

	def getTranslation(self):
		return self._m[:3, 3]

	def getTrans(self):
		return self.getTranslation()

	@property
	def translation(self):
		return self.getTranslation()

	@property
	def trans(self):
		return self.getTranslation()

	@property
	def t(self):
		return self.getTranslation()

	"""
	def rotate(self, angle, base=None):
		if (type(base) is np.ndarray):
		elif (base is None):
		else:
			___ERROR___
	"""

	def print(self, title=None):
		print(self.getPrintStr(title))

_DEFAULT_VEC3D = np.array([0.0, 0.0, 0.0])

class vec3d:
	_classname = 'nkj.math.vec3d'

	def __init__(self, v=None):
		if (v is None):
			self._v = _DEFAULT_VEC3D
		else:
			self.set(v)

	def __str__(self, title=None):
		return self.getPrintStr(title)

	def __pos__(self):
		return self

	def __neg__(self):
		return vec3d(-self.array())

	def __invert__(self):
		return self.__neg__()

	def __rmatmul__(self, first):
		return self.getMultiplied(first)

	if (ENABLE_MULOPERATOR_FOR_LINE3D_CLASS):
		def __rmul__(self, first):
			return self.__rmatmul__(first)

	@classmethod
	def getClassName(cls):
		return point3d._classname

	@classmethod
	@property
	def classname(cls):
		return cls.getClassName()

	def set(self, p):
		if (type(p) is vec3d):
			self._v = p._v
		elif (type(p) is np.ndarray):
			self._v = p
		elif (type(p) is list or type(p) is tuple):
			self._v = np.array(p)
		else:
			___ERROR___

	def get(self):
		return self._v

	def getArray(self):
		return np.array(self.get(), dtype=np.float32)

	@property
	def array(self):
		return self.getArray()

	def setArray(self):
		self.set(v)

	@array.setter
	def array(self, v):
		self.setArray(v)

	def getList(self):
		return list(self.getArray())

	@property
	def list(self):
		return self.getList()

	def getX(self):
		return self._v[0]

	def getY(self):
		return self._v[1]

	def getZ(self):
		return self._v[2]

	@property
	def x(self):
		return self.getX()

	@property
	def y(self):
		return self.getY()

	@property
	def z(self):
		return self.getZ()

	def setX(self, v):
		self._v[0] = v

	def setY(self, v):
		self._v[1] = v

	def setZ(self, v):
		self._v[2] = v

	@x.setter
	def x(self, v):
		return self.setX(v)

	@y.setter
	def y(self, v):
		return self.setY(v)

	@z.setter
	def z(self, v):
		return self.setZ(v)

	def getMultiplied(self, r):
		if (type(r) is csrot3d):
			return self.getMultiplied(r.getMatrix())
		elif (type(r) is cstrans3d):
			return self.getMultiplied(r.getMatrix())
		elif (type(r) is list or type(r) is tuple):
			return self.getMultiplied(np.array(r))
		elif (type(r) is np.ndarray):
			if (r.ndim == 2):
				if (r.shape == (3, 3)):
					v = r @ self._v
					return vec3d(v)
				elif (r.shape == (4, 4)):
					v = vec3(r @ vec4(self._v))
					return vec3d(v)
				else:
					___ERROR___
			else:
				___ERROR___
		else:
			___ERROR___

	def multiplied(self, r):
		return self.getMultiplied(r)

	def getRotated(self, r):
		if (type(r) is csrot3d):
			return self.getMultiplied(r.getMatrix())
		elif (type(r) is cstrans3d):
			return self.getMultiplied(r.getMatrix())
		elif (type(r) is list or type(r) is tuple):
			return self.getMultiplied(np.array(r))
		elif (type(r) is np.ndarray):
			if (r.shape == (3, 3)):
				v = r @ self._v
				return vec3d(v)
			elif (r.shape == (4, 4)):
				v = vec3(r @ vec4(self._v))
				return vec3d(v)
			else:
				___ERROR___
		else:
			___ERROR___

	def rotated(self, r):
		return getRotated(r)

	def getTranslated(self, t):
		if (type(t) is cstrans3d):
			return self.getTranslated(t.getTranslation())
		elif (type(t) is list or type(t) is tuple):
			return self.getTranslated(np.array(t))
		elif (type(t) is np.ndarray):
			v = self._v + t
			return vec3d(v)
		else:
			___ERROR___

	def translated(self, t):
			return self.getTranslated(t)

	def getTransformed(self, t):
		return self.getMultiplied(t)

	def transformed(self, t):
		return self.getTransformed(t)

	def getPrintStr(self, title=None):
		if (title is None):
			mesg = ''
		else:
			mesg = title + ': '
		mesg += "({0: .3f}, {1: .3f}, {2: .3f})".format(self._v[0], self._v[1], self._v[2])
		return mesg

	@property
	def printstr(self):
		return self.getPrintStr()

	@property
	def str(self):
		return self.getPrintStr()

	def print(self, title=None):
		print(self.getPrintStr(title))

	def getDataStr(self):
		return '{0:21.12f}, {1:21.12f}, {2:21.12f}\n'.format(self._v[0], self._v[1], self._v[2])

	@property
	def datastr(self):
		return self.getDataStr()

	def setDataStr(self, s):
		s = s.split(',')
		for i in range(len(s)):
			s[i] = float(s[i].strip())
		self.set([s[0], s[1], s[2]])

	@datastr.setter
	def datastr(self, s):
		return setDataStr(s)

	def load(self, filename):
		with open(filename, 'r') as f:
			self.setDataStr(f.read())

	def save(self, filename):
		with open(filename, 'w') as f:
			f.write(self.getDataStr())

class point3d(vec3d):
	_classname = 'nkj.math.point3d'

	def __init__(self, p=None):
		super().__init__(p)

	@classmethod
	def getClassName(cls):
		return point3d._classname

	def set(self, p):
		if (type(p) is point3d):
			super().set(p._v)
		else:
			super().set(p)

_DEFAULT_LINE3D_POINT1 = np.array([0.0, 0.0, 0.0])
_DEFAULT_LINE3D_POINT2 = np.array([0.0, 0.0, 1.0])

class line3d:
	_classname = 'nkj.math.line3d'

	def __init__(self, p1=None, p2=None):
		if (p1 is None and p2 is None):
			p1 = _DEFAULT_LINE3D_POINT1
			p2 = _DEFAULT_LINE3D_POINT2
		self.set(p1, p2)

	def __str__(self, title=None):
		return self.getPrintStr(title)

	def __rmatmul__(self, first):
		return self.getMultiplied(first)

	if (ENABLE_MULOPERATOR_FOR_LINE3D_CLASS):
		def __rmul__(self, first):
			return self.__rmatmul__(first)

	@classmethod
	def getClassName(cls):
		return line3d._classname

	@classmethod
	@property
	def classname(cls):
		return cls.getClassName()

	def getArray(self):
		return self._pt

	@property
	def array(self):
		return self.getArray()

	@array.setter
	def array(self, second):
		self.set(second)

	def get(self):
		return self.array()

	def getPoint(self, index=None):
		if (index is None):
			return getPoints()
		else:
			return self._pt[index]

	@property
	def point0(self):
		return self.getPoint(0)

	@property
	def point1(self):
		return self.getPoint(1)

	@property
	def p0(self):
		return self.getPoint(0)

	@property
	def p1(self):
		return self.getPoint(1)

	def getPoints(self):
		return self.array()

	@property
	def points(self):
		return self.getPoints()

	def getOrigin(self):
		return self._pt[0]

	@property
	def origin(self):
		return self.getOrigin()

	@property
	def orig(self):
		return self.getOrigin()

	def getVector(self):
		return self._pt[1] - self._pt[0]

	@property
	def vector(self):
		return self.getVector()

	@property
	def vec(self):
		return self.getVector()

	@property
	def v(self):
		return self.getVector()

	def getLength(self):
		return np.linalg.norm(self.getVector())

	@property
	def length(self):
		return self.getLength()

	@property
	def len(self):
		return self.getLength()

	@property
	def l(self):
		return self.getLength()

	def getDirection(self):
		return vecnormalize(self.getVector())

	@property
	def direction(self):
		return self.getDirection()

	@property
	def direct(self):
		return self.getDirection()

	def set(self, p1, p2=None):
		if (p2 is None):
			if (type(p1) is list or type(p1) is tuple):
				if (len(p1) == 2):
					p2 = p1[1]
					p1 = p1[0]
				else:
				 	___ERROR___
			else:
			 	___ERROR___
		if (type(p1) is np.ndarray):
			pass
		elif (type(p1) is list or type(p1) is tuple):
			p1 = np.array(p1)
		else:
			___ERROR___
		if (type(p2) is np.ndarray):
			pass
		elif (type(p2) is list or type(p2) is tuple):
			p2 = np.array(p2)
		else:
			___ERROR___
		self._pt = [p1, p2]

	def setPoints(self, pts):
		self._pt = pts

	@points.setter
	def points(self, pts):
		self.setPoints(pts)

	def setPoint(self, index, pt):
		self._pt[index] = pt

	def setPoint0(self, p):
		self.setPoint(0, pt)

	def setPoint1(self, p):
		self.setPoint(1, pt)

	@point0.setter
	def point0(self, pt):
		self.setPoint0(pt)

	@point1.setter
	def point1(self, pt):
		self.setPoint1(pt)

	@p0.setter
	def p0(self, pt):
		self.setPoint0(pt)

	@p1.setter
	def p1(self, pt):
		self.setPoint1(pt)

	def setOrigin(self, p):
		self.setPoint0(p)

	@origin.setter
	def origin(self, p):
		self.setOrigin(p)

	@orig.setter
	def orig(self, p):
		self.setOrigin(p)

	def setVector(self, v):
		self._pt[1] = self._pt[0] + v

	@vector.setter
	def vector(self, v):
		self.setVector(v)

	@vec.setter
	def vec(self, v):
		self.setVector(v)

	@v.setter
	def v(self, vec):
		self.setVector(v)

	def setLength(self, len):
		self.setVector(len * self.getDirection())

	@length.setter
	def length(self, len):
		self.setLength(len)

	@len.setter
	def len(self, len):
		self.setLength(len)

	@l.setter
	def l(self, len):
		self.setLength(len)

	def getMultiplied(self, r):
		if (type(r) is csrot3d):
			return self.getMultiplied(r.getMatrix())
		elif (type(r) is cstrans3d):
			return self.getMultiplied(r.getMatrix())
		elif (type(r) is list or type(r) is tuple):
			return self.getMultiplied(np.array(r))
		elif (type(r) is np.ndarray):
			if (r.ndim == 2):
				if (r.shape == (3, 3)):
					p0 = r @ self._pt[0]
					p1 = r @ self._pt[1]
					return line3d(p0, p1)
				elif (r.shape == (4, 4)):
					p0 = vec3(r @ vec4(self._pt[0]))
					p1 = vec3(r @ vec4(self._pt[1]))
					return line3d(p0, p1)
				else:
					___ERROR___
			else:
				___ERROR___
		else:
			___ERROR___

	def multiplied(self, r):
		return self.getMultiplied(r)

	def getRotated(self, r):
		if (type(r) is csrot3d):
			return self.getMultiplied(r.getMatrix())
		elif (type(r) is cstrans3d):
			return self.getMultiplied(r.getMatrix())
		elif (type(r) is list or type(r) is tuple):
			return self.getMultiplied(np.array(r))
		elif (type(r) is np.ndarray):
			if (r.shape == (3, 3)):
				p0 = r @ self._p[0]
				p1 = r @ self._p[1]
				return line3d(p0, p1)
			elif (r.shape == (4, 4)):
				r = to3x3(r)
				p0 = r @ self._p[0]
				p1 = r @ self._p[1]
				return line3d(p0, p1)
			else:
				___ERROR___
		else:
			___ERROR___

	def rotated(self, r):
		return getRotated(r)

	def getTranslated(self, t):
		if (type(t) is cstrans3d):
			return self.getTranslated(t.getTranslation())
		elif (type(t) is list or type(t) is tuple):
			return self.getTranslated(np.array(t))
		elif (type(t) is np.ndarray):
			p0 = self._p[0] + t
			p1 = self._p[1] + t
			return line3d(p0, p1)
		else:
			___ERROR___

	def translated(self, t):
			return self.getTranslated(t)

	def getTransformed(self, t):
		return self.getMultiplied(t)

	def transformed(self, t):
		return self.getTransformed(t)

	def getPrintStr(self, title=None):
		if (title is None):
			mesg = ''
		else:
			mesg = title + ': '
		p0 = self._pt[0]
		p1 = self._pt[1]
		mesg += "({0: .3f}, {1: .3f}, {2: .3f}) - ({3: .3f}, {4: .3f}, {5: .3f})".format(p0[0], p0[1], p0[2], p1[0], p1[1], p1[2])
		return mesg

	@property
	def printstr(self):
		return self.getPrintStr()

	@property
	def str(self):
		return self.getPrintStr()

	def print(self, title=None):
		print(self.getPrintStr(title))

	def getDataStr(self):
		return '{0:21.12f}, {1:21.12f}, {2:21.12f}, {3:21.12f}, {4:21.12f}, {5:21.12f}\n'.format(
		self._pt[0][0], self._pt[0][1], self._pt[0][2],
		self._pt[1][0], self._pt[1][1], self._pt[1][2])

	@property
	def datastr(self):
		return self.getDataStr()

	def setDataStr(self, s):
		s = s.split(',')
		for i in range(len(s)):
			s[i] = float(s[i].strip())
		self.set([(s[0], s[1], s[2]), (s[3], s[4], s[5])])

	@datastr.setter
	def datastr(self, s):
		return setDataStr(s)

	def load(self, filename):
		with open(filename, 'r') as f:
			self.setDataStr(f.read())

	def save(self, filename):
		with open(filename, 'w') as f:
			f.write(self.getDataStr())

_DEFAULT_PLANE3D_ORIGIN = [0.0, 0.0, 0.0]
_DEFAULT_PLANE3D_NORMAL = [0.0, 0.0, 1.0]

class plane3d:
	_classname = 'nkj.math.plane3d'

	def __init__(self, origin=None, normal=None):
		if (origin is None and normal is None):
			origin = _DEFAULT_PLANE3D_ORIGIN
			normal = _DEFAULT_PLANE3D_NORMAL
		self.set(origin, normal)
	
	def __str__(self, title=None):
		return self.getPrintStr(title)

	@classmethod
	def getClassName(cls):
		return plane3d._classname

	@classmethod
	@property
	def classname(cls):
		return cls.getClassName()

	def getOrigin(self):
		return self._origin

	@property
	def origin(self):
		return self.getOrigin()

	@property
	def orig(self):
		return self.getOrigin()

	def getNormal(self):
		return self._normal

	@property
	def normal(self):
		return self.getNormal()

	@property
	def n(self):
		return self.getNormal()

	def getVector(self):
		return self.getNormal()

	@property
	def vector(self):
		return self.getNormal()

	@property
	def v(self):
		return self.getNormal()

	def set(self, origin, normal=None):
		if (normal is None):
			if (type(origin) is list or type(origin) is tuple):
				if (len(origin) == 2):
					normal = origin[1]
					origin = origin[0]
				else:
				 	___ERROR___
			else:
			 	___ERROR___
		if (type(origin) is np.ndarray):
			pass
		elif (type(origin) is list or type(origin) is tuple):
			origin = np.array(origin)
		else:
			___ERROR___
		if (type(normal) is np.ndarray):
			pass
		elif (type(normal) is list or type(normal) is tuple):
			normal = np.array(normal)
		else:
			___ERROR___
		self._origin = origin
		self._normal = vecnormalize(normal)

	def setOrigin(self, origin):
		self._origin = origin

	@origin.setter
	def origin(self, origin):
		self.setOrigin(origin)

	@orig.setter
	def orig(self, origin):
		self.setOrigin(origin)

	def setNormal(self, normal):
		self._normal = normal

	@normal.setter
	def normal(self, n):
		self.setNormal(n)

	@n.setter
	def n(self, normal):
		self.setNormal(normal)

	def getMultiplied(self, r):
		if (type(r) is csrot3d):
			return self.getMultiplied(r.getMatrix())
		elif (type(r) is cstrans3d):
			return self.getMultiplied(r.getMatrix())
		elif (type(r) is list or type(r) is tuple):
			return self.getMultiplied(np.array(r))
		elif (type(r) is np.ndarray):
			if (r.ndim == 2):
				if (r.shape == (3, 3)):
					origin = r @ self._origin
					normal = r @ self._normal
					return plane3d(origin, normal)
				elif (r.shape == (4, 4)):
					origin = vec3(r @ vec4(self._origin))
					normal = to3x3(r) @ self._normal
					return plane3d(origin, normal)
				else:
					___ERROR___
			else:
				___ERROR___
		else:
			___ERROR___

	def multiplied(self, r):
		return self.getMultiplied(r)

	def getRotated(self, r):
		if (type(r) is csrot3d):
			return self.getMultiplied(r.getMatrix())
		elif (type(r) is cstrans3d):
			return self.getMultiplied(r.getMatrix())
		elif (type(r) is list or type(r) is tuple):
			return self.getMultiplied(np.array(r))
		elif (type(r) is np.ndarray):
			if (r.shape == (3, 3)):
				normal = r @ self._normal
				return plane3d(self._origin, normal)
			elif (r.shape == (4, 4)):
				m = to3x3(r)
				normal = m @ self._normal
				return plane3d(self._origin, normal)
			else:
				___ERROR___
		else:
			___ERROR___

	def rotated(self, r):
		return getRotated(r)

	def getTranslated(self, t):
		if (type(t) is cstrans3d):
			return self.getTranslated(t.getTranslation())
		elif (type(t) is list or type(t) is tuple):
			return self.getTranslated(np.array(t))
		elif (type(t) is np.ndarray):
			origin = self._origin + t
			return plane3d(origin, self._normal)
		else:
			___ERROR___

	def translated(self, t):
			return self.getTranslated(t)

	def getTransformed(self, t):
		return self.getMultiplied(t)

	def transformed(self, t):
		return self.getTransformed(t)

	def getPrintStr(self, title=None):
		if (title is None):
			mesg = ''
		else:
			mesg = title + ': '
		mesg += "Origin: ({0: .3f}, {1: .3f}, {2: .3f}), Normal: ({3: .3f}, {4: .3f}, {5: .3f})".format(self._origin[0], self._origin[1], self._origin[2], self._normal[0], self._normal[1], self._normal[2])
		return mesg

	@property
	def printstr(self):
		return self.getPrintStr()

	@property
	def str(self):
		return self.getPrintStr()

	def print(self, title=None):
		print(self.getPrintStr(title))

	def getDataStr(self):
		return '{0:21.12f}, {1:21.12f}, {2:21.12f}, {3:21.12f}, {4:21.12f}, {5:21.12f}\n'.format(
		self._origin[0], self._origin[1], self._origin[2], self._normal[0], self._normal[1], self._normal[2])

	@property
	def datastr(self):
		return self.getDataStr()

	def setDataStr(self, s):
		s = s.split(',')
		for i in range(len(s)):
			s[i] = float(s[i].strip())
		self.set([(s[0], s[1], s[2]), (s[3], s[4], s[5])])

	@datastr.setter
	def datastr(self, s):
		return setDataStr(s)

	def load(self, filename):
		with open(filename, 'r') as f:
			self.setDataStr(f.read())

	def save(self, filename):
		with open(filename, 'w') as f:
			f.write(self.getDataStr())

class nkjlist(list):
	_classname = 'nkj.math.nkjlist'

	def __init__(self, ls=None):
		super().__init__()
		self.set(ls)

	def __str__(self, title=None):
		return self.getPrintStr(title)

	@classmethod
	def getClassName(cls):
		return line3dlist._classname

	def get(self, index):
		return self[index]

	def set(self, ls=None):
		if (ls is None):
			super().clear()
		else:
			super().clear()
			super().extend(ls)   # 他のリストの要素を追加

	def getListLength(self):
		return len(self)

	def getLength(self):
		return self.getListLength()

	@property
	def listlength(self):
		return self.getListLength()

	@property
	def length(self):
		return self.getListLength()

	@property
	def len(self):
		return self.getListLength()

	@property
	def l(self):
		return self.getListLength()

	def getArray(self):
		outarray = []
		for i in range(len(self)):
			outarray.append(self[i].getArray())
		return np.array(outarray, dtype=np.float32)

	@property
	def array(self):
		return self.getArray()

	def getList(self):
		outlist = []
		for i in range(len(self)):
			outlist.append(self[i].getList())
		return outlist

	@property
	def list(self):
		return self.getList()

	def getPrintStr(self, title=None):
		listlen = self.getListLength()
		if (title is None):
			mesg = '--- [{0}] ---\n'.format(listlen)
		else:
			mesg = '--- {0}[{1}] ---\n'.format(title, listlen)
		for i in range(listlen):
			mesg += '{0}\n'.format(self[i])
		mesg += '---'
		return mesg

	@property
	def printstr(self):
		return self.getPrintStr()

	@property
	def str(self):
		return self.getPrintStr()

	def print(self, title=None):
		print(self.getPrintStr(title))

	def load(self, filename, datatype=None):
		self.clear()
		if (datatype is None):
			pass
		elif (datatype == 'point3d'):
			x = point3d()
		elif (datatype == 'line3d'):
			x = line3d()
		elif (datatype == 'plane3d'):
			x = plane3d()
		else:
			___NOT_SUPPORTED___
		if (datatype is None):
			with open(filename, 'r') as f:
				s = f.read()
				s = s.strip()
				s = s.split('\n')
				for linestr in s:
					self.append(linestr)
		else:
			with open(filename, 'r') as f:
				s = f.read()
				s = s.strip()
				s = s.split('\n')
				for linestr in s:
					x.setDataStr(linestr)
					self.append(copy.deepcopy(x))

	def save(self, filename):
		with open(filename, 'w') as f:
			for i in range(self.getListLength()):
				x = self[i]
				if (is_geometric(x)):
					f.write(x.getDataStr())
				else:
					f.write('{0}\n'.format(x))

class point3dlist(nkjlist):
	_classname = 'nkj.math.point3dlist'

	def __init__(self, ls=None):
		super().__init__()
		if (ls is not None):
			self.set(ls)

	def __str__(self, title=None):
		return self.getPrintStr(title)

	@classmethod
	def getClassName(cls):
		return line3dlist._classname

	def set(self, ls=None):
		super().clear()
		ty = type(ls)
		if (ls is None):
			super().clear()
		elif (ty is list):
			self.extend(ls)
		else: # リストでなく、要素が入力された
			self.append(ls)
	
	def append(self, x):
		ty = type(x)
		if (ty is point3d):
			super().append(x)
		elif (ty is list or ty is tuple or ty is np.ndarray):
			if (shape(x) == (3, )):
				super().append(point3d(x))
			else:
				___ERROR___
		else:
			___ERROR___

	def extend(self, ls):
		ty = type(ls)
		if (ty is list or ty is point3dlist):
			for x in ls:
				self.append(x)
		else:
			___ERROR___

	def load(self, filename):
		super().load(filename, 'point3d')

	def save(self, filename):
		super().save(filename, 'point3d')

class line3dlist(nkjlist):
	_classname = 'nkj.math.line3dlist'

	def __init__(self, ls=None):
		super().__init__()
		if (ls is not None):
			self.set(ls)

	def __str__(self, title=None):
		return self.getPrintStr(title)

	@classmethod
	def getClassName(cls):
		return line3dlist._classname

	def set(self, ls=None):
		super().clear()
		ty = type(ls)
		if (ls is None):
			super().clear()
		elif (ty is list):
			self.extend(ls)
		else: # リストでなく、要素が入力された
			self.append(ls)
	
	def append(self, x):
		if (type(x) is line3d):
			super().append(x)
		else:
			___ERROR___

	def extend(self, ls):
		ty = type(ls)
		if (ty is list or ty is line3dlist):
			for x in ls:
				self.append(x)
		else:
			___ERROR___

	def load(self, filename):
		super().load(filename, 'line3d')

class plane3dlist(nkjlist):
	_classname = 'nkj.math.plane3dlist'

	def __init__(self, ls=None):
		super().__init__()
		if (ls is not None):
			self.set(ls)

	def __str__(self, title=None):
		return self.getPrintStr(title)

	@classmethod
	def getClassName(cls):
		return plane3dlist._classname

	def set(self, ls=None):
		super().clear()
		ty = type(ls)
		if (ls is None):
			super().clear()
		elif (ty is list):
			self.extend(ls)
		else: # リストでなく、要素が入力された
			self.append(ls)
	
	def append(self, x):
		if (type(x) is plane3d):
			super().append(x)
		else:
			___ERROR___

	def extend(self, ls):
		ty = type(ls)
		if (ty is list or ty is plane3dlist):
			for x in ls:
				self.append(x)
		else:
			___ERROR___

	def load(self, filename):
		super().load(filename, 'plane3d')

#-- main

if __name__ == '__main__':

	ns.lib_debuglevel(_LIB_DEBUGLEVEL)

	if (True):
		print("===== complex =====")

		c = complex(1, 2)
		print(c.getClassName())
		print(c)

		print(c.normalized())
		print(normalized(c))

		print(c.conjugated())
		print(conjugated(c))

		c[0] = 10
		c[1] = 20
		print(c)

		c2 = complex(1, 3)
		print(c2)
		print(c * c2)

	if (False):
		print("===== quaternion =====")

	if (False):
		print("===== csrot3d =====")

		theta = 90 # degrees
		v = np.array([0, 0, 1])

		theta = theta / 180 * np.pi # degrees to rad
		hftheta = theta / 2
		c = np.cos(hftheta)
		s = np.sin(hftheta)
		r3 = csrot3d([c, s * v[0], s * v[1], s * v[2]])

		print("r3.w:  {0}".format(r3.w))
		print("r3.x:  {0}".format(r3.x))
		print("r3.y:  {0}".format(r3.y))
		print("r3.z:  {0}".format(r3.z))

		print("r3.rx: {0}".format(r3.rx))
		print("r3.ry: {0}".format(r3.ry))
		print("r3.rz: {0}".format(r3.rz))

		print("quat:    {0}".format(r3.quat))
		print("np.quat: {0}".format(r3.npquat))
		print("np.quat: {0} (array)".format(r3.npquatarray))
		print("R.quat:  {0}".format(r3.rquat))
		print("R.quat:  {0} (array)".format(r3.rquatarray))

		print("--- csrot3d.matrix ---")
		print(r3.matrix)
		print("---")

	if (False):
		print("===== cstrans3d =====")

		theta = 90.0 # degrees
		rv = np.array([0, 0, 1])
		tv = np.array([2, 3, 4])

		theta = theta / 180.0 * np.pi # deg 2 rad
		hftheta = theta / 2.0
		c = np.cos(hftheta)
		s = np.sin(hftheta)

		t = cstrans3d([np.array([c, s * rv[0], s * rv[1], s * rv[2]]), tv])
		t.print("cstrans3d")
		print("--- matrix ---")
		print(t.matrix)
		print("---")
		print("--- rotmat ---")
		print(t.rotmat)
		print("---")
		print("translation vector: {0}".format(t.trans))

		t_i = t.inv
		t_i.print("inversed")
		print("--- inversed matrix ---")
		print(t_i.matrix)
		print("---")

		t2 = t @ t_i
		print("--- matrix ---")
		print(t2.matrix)
		print("---")
		mat4x4(t2).print('test matrix')

		t3 = t_i @ t
		print("--- matrix ---")
		print(t3.matrix)
		print("---")
		mat4x4(t3).print('test matrix')

	if (False):
		print("===== matrix =====")

		a = np.array([[1, 0], [0, 2]])
		print(a)
		print(type(a))

		m = mat4x4()
		print("class name: ", str_bracket(m.getClassName()))
		print("type:       ", type(m))
		print("dimension:  ", m.dim())
		print("size:       ", m.size())
		m.print("m")
		print("--- m.array() ---")
		print(m.array())
		print("---")

		m.array()[0][1] = 3.0
		print(m)

		m2 = mat4x4()

		print(m @ m2)

		m3 = m @ m2
		print(m3)

		m3.getInversed().print('inversed')

		m3.print('original')

		m4 = mat4x4(m3.get())
		m4.print('m4')

		"""
		m5 = mat4x4(np.array([deg2rad(30), 0, 0, 1]))
		m5.print('m5')
		"""

		(~m3).print('invert')

		(~m3 * m3).print('validation')
		(~m3 @ m3).print('validation')

		m3.inverse()
		m3.print('inverse')

		m3.identity()
		m3.print('identity')

	if (False):
		print("===== sigmoid =====")
		import matplotlib.pyplot as plt

		x = np.arange(-10, 10, 0.1)
		ta = 1.0
		x0 = 2.5
		#y = sigmoid(x, tau=tau, x0=x0)
		y = sigmoid(x, x0=x0)
		plt.plot(x, y)
		plt.show()

	if (False):
		print("===== log ticks =====")

		ticks = logticks(0.01, 2.0)
		print(ticks)

	if (False):
		print("===== vec3d =====")

		print(vec3d())

		v = vec3d(np.array([1, 0, 0]))
		print(v)

		v0 = vec3d(np.array([0, 1, 0]))

		print("angle: {0} degrees".format(rad2deg(angle(v0, v))))

	if (True):
		print("===== point3d =====")

		print(point3d())

		p = point3d(np.array([1, 1, 2]))
		print(p)

	if (False):
		print("===== line3d =====")

		print(line3d())

		l = line3d(np.array([0, 0, 0]), np.array([0, 0, 100]))
		l.print('line3d')
		print('origin: {0}'.format(l.getOrigin()))
		print('length: {0}'.format(l.getLength()))
		print('vector: {0}'.format(l.getVector()))
		print('direction: {0}'.format(l.getDirection()))

		l2 = line3d([[1, 1, 1], [2, 2, 2]])
		l2.print('line3d 2')

		theta = deg2rad(90)
		t = cstrans3d()
		ver = 1
		if (ver == 1):
			t.rotateGlobal([deg2rad(45), (0, 1, 0)], 'angleaxis')
			t.rotateGlobal([deg2rad(theta), (0, 0, 1)], 'angleaxis')
		elif (ver == 2):
			t.rotateGlobal([deg2rad(45), (np.cos(theta), np.sin(theta), 0)], 'angleaxis')
		else:
			___ERROR___
		t.print('transformation')
		#l2 = l.transformed(t)
		l2 = t @ l
		l2.print('line3d (transformed)')

		l2.save('testdata/test.line')
		l2.load('testdata/test.line')
		l2.print('reload')

		#-- direction cosine test

		xlist = []
		zlist = []
		philist = []
		thetalist = []
		for zdeg in range(-90, 91, 5):
			ztheta = deg2rad(zdeg)
			for xdeg in range(-90, 91, 5):
				xtheta = deg2rad(xdeg)
				dprint('ztheta:{0:.3f}, xtheta:{1:.3f}'.format(rad2deg(ztheta), rad2deg(xtheta)))
				phi = np.sqrt(ztheta**2 + xtheta**2)
				if (phi > np.pi / 2):
					phi = np.pi - phi
				dprint('phi:{0:.3f}'.format(rad2deg(phi)))
				c_phi = np.cos(phi)
				s_phi = np.sin(phi)
				theta = np.arctan2(ztheta, xtheta)
				c = s_phi * np.cos(theta)
				s = s_phi * np.sin(theta)
				dprint([c, c_phi, s])
				r = csrot3d([c, c_phi, s], 'dircos', [0, 1, 0])
				#r.print('direction cosine')
				xlist.append(xdeg)
				zlist.append(zdeg)
				philist.append(rad2deg(phi))
				thetalist.append(theta)
		xlist = np.array(xlist)
		zlist = np.array(zlist)
		philist = np.array(philist)
		thetalist = np.array(thetalist)

		ticks = int(np.sqrt(len(xlist)))
		xlist = xlist.reshape(ticks, ticks)
		zlist = zlist.reshape(ticks, ticks)
		philist = philist.reshape(ticks, ticks)
		thetalist = thetalist.reshape(ticks, ticks)
		dprint('xlist[{0}]: {1}'.format(len(xlist), xlist))
		dprint('zlist[{0}]: {1}'.format(len(zlist), zlist))
		dprint('philist[{0}]: {1}'.format(len(philist), philist))

		from matplotlib import pyplot as plt

		plt.pcolor(xlist, zlist, philist, cmap='inferno', vmin=0, vmax=90)
		""" #--- colormaps
		plt.pcolor(xlist, zlist, philist, cmap='plasma', vmin=0, vmax=90)
		plt.pcolor(xlist, zlist, philist, cmap='bwr', vmin=0, vmax=90)
		plt.pcolor(xlist, zlist, philist, cmap='coolwarm', vmin=0, vmax=90)
		plt.pcolor(xlist, zlist, philist, cmap='seismic', vmin=0, vmax=90)
		plt.pcolor(xlist, zlist, philist, cmap='RdYlBu_r', vmin=0, vmax=90)
		plt.pcolor(xlist, zlist, thetalist)
		"""
		plt.xticks([-90, -60, -30, 0, 30, 60, 90], fontsize=15)
		plt.yticks([-90, -60, -30, 0, 30, 60, 90], fontsize=15)
		plt.xlabel('Angle of x direction cosine', fontsize=18)
		plt.ylabel('Angle of z direction cosine', fontsize=18)
		plt.tight_layout()   # フォントサイズを変更したとき、図で文字が見切れないように調整する。
		colorbar_ticks = np.linspace(0, 90, 7, endpoint=True)
		if (True):
			cb = plt.colorbar(ticks=colorbar_ticks)
			for t in cb.ax.get_yticklabels():
				t.set_fontsize(12)
		else:
			plt.colorbar(ticks=colorbar_ticks)
		plt.savefig('testdata/test.png')
		plt.show()

	if (False):
		print("===== plane3d =====")

		pl = plane3d(np.array([0, 0, 0]), np.array([0, 0, 100]))
		pl.print('plane3d')

		pl2 = plane3d([np.array([0, 0, 0]), np.array([0, 10, 0])])
		pl2.print('plane3d 2')

		pl3 = plane3d([[0, 0, 0], [1, 1, 0]])
		pl3.print('plane3d 3')

		print('{0} degree'.format(rad2deg(angle(pl, pl2))))
		print('{0} degree'.format(rad2deg(angle(pl2, pl3))))

		theta = deg2rad(45)
		phi = deg2rad(45)
		print('theta:{0:.3f}, phi:{1:.3f}'.format(rad2deg(theta), rad2deg(phi)))
		t = cstrans3d()
		ver = 2
		if (ver == 1):
			t.rotateGlobal([phi, (np.cos(theta), np.sin(theta), 0)], 'angleaxis')
		elif (ver == 2):
			t.rotateGlobal([phi, (1, 0, 0)], 'angleaxis')
			t.rotateGlobal([theta, (0, 0, 1)], 'angleaxis')
		else:
			___ERROR___
		t.translateGlobal([10, 10, 0])
		t.print('transformation')
		pl2 = t @ pl
		pl2.print('plane3d (transformed)')

		pl2.save('testdata/test.plane')
		pl2.load('testdata/test.plane')
		pl2.print('reload')

	if (False):
		print("===== nkjlist =====")

		ls = nkjlist()
		ls.print('nkjlist')

		ls.append('test')
		ls.append('test2')
		ls.print('nkjlist')

		ls.set(['test3'])
		ls.print('nkjlist (test 3)')

		ls.clear()
		ls.print('nkjlist')

		ls.clear()
		ls.append([1, 2, 3])  # リストを一要素として追加
		ls.extend([3, 4, 5])  # 要素をリストで追加
		ls.save('testdata/test.list')
		ls.load('testdata/test.list')
		ls.print('nkjlist')

	"""
	if (False):
		print("===== vec3dlist =====")

		ls = vec3dlist()
		ls.append([0, 1, 2])
		ls.append([3, 4, 5])
		ls.extend([[6, 7, 8], [9, 10, 11]])
		ls.print('vec3dlist')
		ls.save('testdata/test.pts')
		ls.load('testdata/test.pts')
		ls.print('vec3dlist')
	"""

	if (False):
		print("===== point3dlist =====")

		ls = point3dlist()
		ls.append([0, 1, 2])
		ls.append([3, 4, 5])
		ls.extend([[6, 7, 8], [9, 10, 11]])
		ls.print('point3dlist')
		ls.save('testdata/test.pts')
		ls.load('testdata/test.pts')
		ls.print('point3dlist')

	if (False):
		print("===== line3dlist =====")

		ls = line3dlist()
		ls.append(line3d([0, 1, 2], [0, 1, 0]))
		ls.append(line3d([3, 4, 5], [3, 4, 0]))
		ls.print('line3dlist')
		ls.save('testdata/test.lines')
		ls.load('testdata/test.lines')
		ls.print('line3dlist')

	if (False):
		print("===== plane3dlist =====")

		ls = plane3dlist()
		ls.append(plane3d([0, 1, 2], [0, 1, 0]))
		ls.append(plane3d([3, 4, 5], [3, 4, 0]))
		ls.extend(copy(ls))
		ls.print('plane3dlist')
		ls.save('testdata/test.planes')
		ls.load('testdata/test.planes')
		ls.print('plane3dlist')
