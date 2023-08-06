#
# [name] nkj.cam.py
#
# Written by Yoshikazu NAKAJIMA
#
_LIB_DEBUGLEVEL = 0

import os
import sys
import numpy as np
import json

sys.path.append(os.path.abspath(".."))
from nkj.str import *
from nkj.math import *

ERROR_FOCALLENGTH = -1.0
ERROR_IMAGESIZE = [-1, -1]

_DEFAULT_IMAGECENTER = [0.0, 0.0]
_DEFAULT_IMAGESIZE = ERROR_IMAGESIZE
_DEFAULT_FOCALLENGTH = [ERROR_FOCALLENGTH, ERROR_FOCALLENGTH]
_DEFAULT_CAMERAMATRIX = np.identity(4)
_DEFAULT_FILENAME = None

class camera:
	#-- Class variables
	_classname = "nkj.cam.camera"

	#--
	def __init__(self, focallength=_DEFAULT_FOCALLENGTH):
		ldprint(["--> nkjcam.camera.__init__()"])
		ldprint(["class name: {0}".format(str_bracket(self.getClassName()))])
		self.setImageCenter(_DEFAULT_IMAGECENTER)
		self.setImageSize(_DEFAULT_IMAGESIZE)
		self.setFocalLength(focallength)
		self.setMatrix(_DEFAULT_CAMERAMATRIX)
		self.setFileName(_DEFAULT_FILENAME)
		ldprint(["<-- nkjcam.camera.__init__()"])

	def __str__(self, title=''):
		return self.getPrintStr(title)

	@classmethod
	def getClassName(cls):
		return camera._classname

	@classmethod
	@property
	def classname(cls):
		return cls.getClassName()

	def getPrintStr(self, title=''):
		if (title == ''):
			mesg = '---\n'
		else:
			mesg = '--- {0} ---\n'.format(title)
		filename = self.getFileName()
		if (filename != None):
			mesg += 'File name:    {0}\n'.format(str_bracket(self.getFileName()))
		mesg += 'Focal length: {0}\n'.format(self.getFocalLength())
		mesg += 'Image center: {0}\n'.format(self.getImageCenter())
		mesg += 'Image size:   {0}\n'.format(self.getImageSize())
		mesg += 'Camera matrix:\n'
		mesg += '{0}\n'.format(mat4x4(self.getMatrix()).getPrintStr())
		mesg += '---'
		return mesg

	@property
	def str(self):
		return self.getPrintStr()

	def getImageCenter(self):
		return self._imagecenter

	@property
	def imagecenter(self):
		return self.getImageCenter()

	@property
	def icen(self):
		return self.getImageCenter()

	def getC0(self):
		return self._imagecenter[0]

	@property
	def c0(self):
		return self.getC0()

	def getR0(self):
		return self._imagecenter[1]

	@property
	def r0(self):
		return self.getR0()

	def getImageSize(self):
		return self._imagesize

	@property
	def imagesize(self):
		return self.getImageSize()

	@property
	def isize(self):
		return self.getImageSize()

	def getFocalLength(self):
		return self._focallength

	@property
	def focallength(self):
		return self.getFocalLength()

	@property
	def f(self):
		return self.getFocalLength()

	def getXFocalLength(self):
		return self._focallength[0]

	@property
	def fx(self):
		return self.getXFocalLength()

	def getYFocalLength(self):
		return self._focallength[1]

	@property
	def fy(self):
		return self.getYFocalLength()

	def getAspectRatio(self):
		if (self.focallength[1] == 0):
			___ERROR___
		return self._focallength[0] / self._focallength[1]

	def getAspect(self):
		return self.getAspectRatio()

	@property
	def aspectratio(self):
		return self.getAspectRatio()

	@property
	def aspect(self):
		return self.getAspectRatio()

	def getMatrix(self):
		return self._cameramatrix.getMatrix()

	@property
	def matrix(self):
		return self.getMatrix()

	@property
	def mat(self):
		return self.getMatrix()

	@property
	def m(self):
		return self.getMatrix()

	def getInverseMatrix(self):
		return np.linalg.inv(self.getMatrix())

	def getInvMatrix(self):
		return self.getInverseMatrix()

	def getIMatrix(self):
		return self.getInverseMatrix()

	@property
	def inversematrix(self):
		return self.getInverseMatrix()

	@property
	def invmatrix(self):
		return self.getInverseMatrix()

	@property
	def imatrix(self):
		return self.getInverseMatrix()

	@property
	def invmat(self):
		return self.getInverseMatrix()

	@property
	def imat(self):
		return self.getInverseMatrix()

	@property
	def im(self):
		return self.getInverseMatrix()

	def getFocalPoint(self):
		return self.getMatrix()[0:3, 3]

	@property
	def focalpoint(self):
		return self.getFocalPoint()

	@property
	def fp(self):
		return self.getFocalPoint()

	def getOrigin(self):
		return self.getFocalPoint()

	@property
	def origin(self):
		return self.getOrigin()

	@property
	def orig(self):
		return self.getOrigin()

	def getXaxis(self):
		return self.getMatrix()[0:3, 0]

	@property
	def xaxis(self):
		return self.getXaxis()

	def getYaxis(self):
		return self.getMatrix()[0:3, 1]

	@property
	def yaxis(self):
		return self.getYaxis()

	def getZaxis(self):
		return self.getMatrix()[0:3, 2]

	@property
	def zaxis(self):
		return self.getZaxis()

	def getDirection(self):
		return self.getZaxis()

	@property
	def direction(self):
		return self.getDirection()

	def getLineOfSight(self, p):
		return line3d(self.getOrigin(), p)

	def line_of_sight(self, p):
		return self.getLineOfSight(p)

	def lineofsight(self, p):
		return self.getLineOfSight(p)

	def sight(self, p):
		return self.getLineOfSight(p)

	def getFileName(self):
		return self._filename

	@property
	def filename(self):
		return self.getFileName()

	def setImageCenter(self, imagecenter):
		self._imagecenter = imagecenter

	@imagecenter.setter
	def imagecenter(self, second):
		self.setImageCenter(second)

	@icen.setter
	def icen(self, second):
		self.setImageCenter(second)

	def setImageSize(self, imagesize):
		self._imagesize = imagesize

	@imagesize.setter
	def imagesize(self, second):
		self.setImageSize(second)

	@isize.setter
	def isize(self, second):
		self.setImageSize(second)

	def setFocalLength(self, focallength):
		ldprint2(["--> setFocalLength()"])
		ldprint2(["Focal length: {0}".format(focallength)])
		ldprint2(["Focal length type: {0}".format(type(focallength))])
		if (type(focallength) == list):
			pass
		elif (type(focallength) == float):
			focallength = [focallength, focallength]
		elif (type(focallength) == tuple):
			focallength = list(focallength)
		ldprint2(["> Focal length: {0}".format(focallength)])
		ldprint2(["> Focal length type: {0}".format(type(focallength))])

		if (len(focallength) != 2):
			print_error("Illegal focal length.")
			___ERROR___

		self._focallength = focallength

	@focallength.setter
	def focallength(self, second):
		self.setFocalLength(second)

	@f.setter
	def f(self, second):
		self.setFocalLength(second)

	def setMatrix(self, cm):
		self._cameramatrix = cstrans3d(np.array(cm))

	@matrix.setter
	def matrix(self, second):
		self.setMatrix(second)

	@mat.setter
	def mat(self, second):
		self.setMatrix(second)

	@m.setter
	def m(self, second):
		self.setMatrix(second)

	def setInverseMatrix(self, cm):
		self.setMatrix(np.linalg.inv(cm))

	@inversematrix.setter
	def inversematrix(self, second):
		self.setInverseMatrix(second)

	@invmatrix.setter
	def invmatrix(self, second):
		self.setInverseMatrix(second)

	@imatrix.setter
	def imatrix(self, second):
		self.setInverseMatrix(second)

	@invmat.setter
	def invmat(self, second):
		self.setInverseMatrix(second)

	@imat.setter
	def imat(self, second):
		self.setInverseMatrix(second)

	@im.setter
	def im(self, second):
		self.setInverseMatrix(second)

	def setFileName(self, fname):
		self._filename = fname

	@filename.setter
	def filename(self, second):
		self.setFileName(second)

	def rotateLocal(self, a, flag=None):
		self._cameramatrix.rotateLocal(a, flag)

	def rotate_local(self, a, flag=None):
		self.rotateLocal(a, flag)

	def rotateGlobal(self, a, flag=None):
		self._cameramatrix.rotateGlobal(a, flag)

	def rotate_global(self, a, flag=None):
		self.rotateGlobal(a, flag)

	def translateLocal(self, v):
		self._cameramatrix.translateLocal(v)

	def translate_local(self, v):
		self.translateLocal(v)

	def translateGlobal(self, v):
		self._cameramatrix.translateGlobalLocal(v)

	def translate_glocal(self, v):
		self.translateGlobal(v)

	def projectPoint3D(self, p3d): # 3D点をカメラ画像上に投影した2D点の座標を返す
		#print("p3d: {0}".format(p3d))
		cm = self.getMatrix()
		#print("cm:  {0}".format(cm))
		p3d4 = np.array((p3d[0], p3d[1], p3d[2], 1.0))
		#print("p3d4: {0}".format(p3d4))
		#lp3d = np.linalg.inv(cm) @ p3d4
		lp3d = cm @ p3d4
		#print("lp3d: {0}".format(lp3d))
		return self.projectLocalPoint3D(lp3d)

	def projectLocalPoint3D(self, p3d): # カメラ座標系の3D点をカメラ画像上に投影した2D点の座標を返す
		x3d = p3d[0]
		y3d = p3d[1]
		z3d = p3d[2]
		ldprint(["p3d: ({0}, {1}, {2})".format(x3d, y3d, z3d)])
		f = self.getFocalLength()
		fx = f[0]
		fy = f[1]
		ldprint(["f:   ({0}, {1})".format(fx, fy)])
		ic = self.getImageCenter()
		icx = ic[0]
		icy = ic[1]
		p2d = np.array(((x3d * fx) / z3d + icx, (y3d * fy) / z3d + icy))
		return p2d

	def projectLine3D(self, l3d): # 3D直線をカメラ画像上に投影した2D直線を返す
		l2d = []
		for i in range(2):
			l2d.append(self.projectPoint3D(l3d[i]))
		return l2d

	def load(self, filename, formatindex=None):
		ldprint2(["--> load({0})".format(str_bracket(filename))])
		self.setFileName(filename)
		if (formatindex is None):
			if (os.path.splitext(filename)[1] == '.cam'):
				formatindex = 'sasama'
		with open(filename, 'r') as f:
			if (formatindex == None or formatindex == 'json'):
				data = json.load(f)
				print(data)
				#ndata = {}
				#for key in data.keys():
				#	ndata[key] = ns.extract_float(data[key])
				#ldprint(["<-- load()"])
				#return ndata
				ldprint(["<-- load()"])
				return data
			elif (formatindex == 'yashima.json'):
				data = json.load(f)
				self.setImageSize((data['width'], data['height']))
				intrinsic = data['intrinsic']
				self.setFocalLength((intrinsic[0][0], intrinsic[1][1]))
				self.setImageCenter((intrinsic[0][2], intrinsic[1][2]))
				r = data['rotation']
				t = data['translation']
				self.setMatrix([[r[0][0], r[0][1], r[0][2], t[0]], [r[1][0], r[1][1], r[1][2], t[1]], [r[2][0], r[2][1], r[2][2], t[2]], [0.0, 0.0, 0.0, 1.0]])
				ldprint2(["<-- load()"])
				return data
			elif (formatindex == 'sasama'):
				with open(filename, 'r') as f:
					print('CAUTION: Sasama format was redefined. Check the .cam format when you will load the file made before 2022.03.')
					s_line = f.readlines()
					self.setFocalLength(l2f(s_line[0]))
					self.setImageCenter(l2f(s_line[1]))
					i = 2
					if (len(l2f(s_line[2])) == 2):
						self.setImageSize(l2i(s_line[2]))
						i += 1
					m = []
					for j in range(i, i + 3):
						m.append(l2f(s_line[j]))
						i += 1
					self.setMatrix(m)
					line = l2f(s_line[i])
					if (line == [0.0, 0.0, 0.0, 1.0]):
						i += 1
						line = l2f(s_line[i])
					if (len(s_line) - i > 0):
						#- Non-linear distortion
						print('--> Non-linear distortion')
						print('___NOT_IMPLEMENTED___')
						print('<-- Non-linear distortion')
			else:
				___NOT_SUPPORTED___
		ldprint2(["<-- load()"])

	def print(self, title=''):
		print(self.getPrintStr(title))

def cam2mat(cam):
	if (type(cam) is camera):
		return cam.getMatrix()
	else:
		return cam

# カメラ輻輳角1. カメラY軸（上向きベクトル）周りの3D回転角度．回転でカメラの上向きベクトルがあまり変化しない（＝カメラの上向きベクトル周りに回転している）と仮定．Headding Up/Down が微小であると仮定して，仰俯角をキャンセル．
def convergence_angle(cam1, cam2): # cam1, cam2: カメラクラス or 基準座標系内でのcamera{1, 2}の位置姿勢
	T_cam1 = cam2mat(cam1)
	T_cam2 = cam2mat(cam2)
	cam1_yaxis = T_cam1[0:3, 1] # [0行目から3行分, 1列目(y-axis)]
	cam2_yaxis = T_cam2[0:3, 1]
	cam_yaxis = (cam1_yaxis + cam2_yaxis) / 2.0 # 2 つの y-axis の平均を y-axis とする
	cam1_zaxis = T_cam1[0:3, 2] # [0行目から3行分, 2列目(z-axis)]
	xaxis = np.cross(cam_yaxis, cam1_zaxis)
	cam1_zaxis = np.cross(xaxis, cam_yaxis)
	cam2_zaxis = T_cam2[0:3, 2]
	xaxis = np.cross(cam_yaxis, cam2_zaxis)
	cam2_zaxis = np.cross(xaxis, cam_yaxis)
	return vecangle(cam1_zaxis, cam2_zaxis)

# カメラ輻輳角2. カメラ視線（カメラ中心線）ベクトル間の3D角度．仰俯角（＝Heading Up/Down による輻輳角の変化）も考慮。
def convergence_angle2(cam1, cam2):
	T_cam1 = cam2mat(cam1)
	T_cam2 = cam2mat(cam2)
	cam1_zaxis = T_cam1[0:3, 2]
	cam2_zaxis = T_cam2[0:3, 2]
	return vecangle(cam1_zaxis, cam2_zaxis)

# カメラ輻輳角3. 計画線周りのカメラの3D角度変化．画像に写り込んだ計画線の位置姿勢（画像面内の回転角および画像中心点からの位置ずれ）を考慮．
def convergence_angle3(cam1, cam2):
	T_cam1 = cam2mat(cam1)
	T_cam2 = cam2mat(cam2)
	plan_vec = np.array([0, 0, 1])
	cam1_vec = T_cam1[0:3, 3] # 原点（＝計画線位置）からカメラ焦点へのベクトル
	xaxis = np.cross(plan_vec, cam1_vec)
	cam1_vec = np.cross(xaxis, plan_vec) # 仰角を取り除いたカメラ焦点から計画直線へ向かう（計画直線に垂直な = 最短距離の）ベクトル
	cam2_vec = T_cam2[0:3, 3]
	xaxis = np.cross(plan_vec, cam2_vec)
	cam2_vec = np.cross(xaxis, plan_vec) # 仰角を取り除いたカメラ焦点から計画直線へ向かう（計画直線に垂直な = 最短距離の）ベクトル
	return vecangle(cam1_vec, cam2_vec)

def convergenceangle(T_cam1, T_cam2):
	return convergence_angle(T_cam1, T_cam2)

def convergenceangle2(T_cam1, T_cam2):
	return convergence_angle2(T_cam1, T_cam2)

def convergenceangle3(T_cam1, T_cam2):
	return convergence_angle3(T_cam1, T_cam2)


#-- main

if __name__ == '__main__':
	lib_debuglevel(_LIB_DEBUGLEVEL)

	ldprint(["DEBUG LEVEL: ", lib_debuglevel()])

	print("Class name: \'{0}\'".format(camera.classname))

	cam = camera((1.0, 2.0))

	print("Image center: ", cam.getImageCenter())
	print("Focal length: ", cam.getFocalLength())
	print("Camera matrix:")
	print(cam.getMatrix())

	filename = "./testdata/camera.json"

	if (cam.load(filename, formatindex='yashima.json') is False):
		print_error("Can't load {0}".format(str_bracket(filename)))
		exit(1)

	cam.print('camera parameter')

	p2d = cam.projectPoint3D((0.0, 0.0, 0.0))
	print(p2d)

	cam2 = camera()
	cam2.load('testdata/test.cam')

	cam3 = camera()
	cam3.load('testdata/test2.cam')
