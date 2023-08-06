#
# [name] nkj.cv.py
# [exec] python cv.py
# [reference] https://qiita.com/teraken_/items/c8ac4c0ff60d8856a15c
#
# Written by Yoshikazu NAKAJIMA
#

DEBUGLEVEL = 2

import os
import sys
import cv2 as cv
import json
import sys
import platform

sys.path.append(os.path.abspath(".."))
import nkj.core as nk
import nkj.str as ns
from nkj.str import *

"""
OpenCV camera calibration で使用するデータの型について（参照：https://kamino.hatenablog.com/entry/opencv_calibrate_camera#sec4）

objectPoint:  vector<Point3f>         -> np.array([[x1, y1, z1], [x2, y2, z2], ...], dtype=np.float32)
objectPoints: vector<vector<Point3f>> -> [np.array([[x1, y1, z1], [x2, y2, z2], ...], dtype=np.float32)]  # モデルの姿勢ごとにnp.arrayにまとめてそれをリストにしている。
                                         [[np.array([x, y, z], dtype=np.float32)]] や、np.array([[[x1, y, z1], [x2, y2, z2], ...], ...], dtype=np.float32) では動作し"ない"ので注意。
imagePoint:   vector<Point2f>         -> np.array([[x1, y1], [x2, y2], ...], dtype=np.float32)
imagePoints:  vector<vector<Point2f>> -> [np.array([[x1, y1], [x2, y2], ...], dtype=np.float32)]  # モデルの姿勢ごとにnp.arrayにまとめてそれをリストにしている。
                                         [[np.array([x, y, z], dtype=np.float32)]] や、np.array([[[x1, y, z1], [x2, y2, z2], ...], ...], dtype=np.float32) では動作し"ない"ので注意。
"""

class nkjcv():
	#-- class variables
	_classname = "nkjcv"

	def __init__(self):
		#-- instance variables
		self._pt = []
		self._m = 0
		self._n = 0
		self._p = 0

	@classmethod
	def getClassName(cls):
		return nkjcv._classname

	def mouseevent_callback(self, event, x, y, flags, param):
		if (event == cv.EVENT_LBUTTONDOWN):
			self._m = self._n
			self._pt.append((x, y))
			self._n = self._n + 1
			self._m = self._m + 1
			ldpring(["pt[", str(self._n), "]: ", str(self._pt)])
		if (event == cv.EVENT_RBUTTONDOWN and self._n > 0):
			self._pt.pop(self._m - 1)
			self._m = self._m - 1
			self._n = self._n - 1
			self._p = self._p + 1
			ldpring(["pt[", str(self._n), "]: ", str(self._pt)])

	def clearPoints(self):
		self._pt.clear()
		self._m = 0
		self._n = 0

	def getPoints(self):
		return self._pt

	def getPoint(self, index):
		return self._pt[index]

	def getM(self):
		return self._m

	def getN(self):
		return self._n

	def getP(self):
		return self._p

#-- main

if __name__ == '__main__':
	ns.LIB_DEBUGLEVEL = DEBUGLEVEL

	WINDOW_TITLE = "image"

	nk.checkPythonVersion()

	ncv = nkjcv()

	cap = cv.VideoCapture(0) # カメラを設定
	cv.namedWindow(WINDOW_TITLE, cv.WINDOW_GUI_NORMAL) # ウィンドウの設定

	cv.setMouseCallback(WINDOW_TITLE, ncv.mouseevent_callback) # マウスイベントの設定

	print(">>> start!!")

	while True:
		ret, frame = cap.read()

		if (ncv.getN() >= 1):
			cv.drawMarker(frame, ncv.getPoint(ncv.getM() - 1), (0, 255, 255), markerType=cv.MARKER_TILTED_CROSS, markerSize=15)

		if (ncv.getN() >= 2):
			for i in range(1, ncv.getN()):
				cv.line(frame, ncv.getPoint(i - 1), ncv.getPoint(i), (0, 255, 255), 1)

		cv.imshow(WINDOW_TITLE, frame)

		k = cv.waitKey(1)

		if (k == 27):
			print(">>> Exit")
			break
		elif (k == ord("c")):
			print(">>> Clear coordinates.")
			ncv.clearPoints()
		elif (k == ord("s")):
			pirnt(">>> Save image and coordinates.")
			str = "patient(no:03}.png".format(no = ncv.getP())
			cv.imwrite(str, frame)
			with open("painted.json", "w") as f:
				json.dump(getPoints(), f, indent=4)

	cap.release()
	cv.destroyAllWindows()

