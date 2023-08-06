#
# [name]    nkj.ea.py
# [comment] library for error analysis
#
# Written by Yoshikazu NAKAJIMA
#

import os
import sys
import numpy as np

sys.path.append(os.path.abspath(".."))
from nkj.str import *
import nkj.math as nm
import nkj.cam as nc

def _correct_convergence_angle(a):
	ldprint(['convergence angle: {0:.3f} degrees'.format(nm.rad2deg(a))])
	if (a < 0.0):
		a = np.abs(a)
		ldprint(['convergence angle: {0:.3f} degrees (corrected)'.format(nm.rad2deg(a))])
	if (a > np.pi / 2.0):
		a = np.pi - a
		ldprint(['convergence angle: {0:.3f} degrees (corrected)'.format(nm.rad2deg(a))])
	return a

def conv_angle_point(pt, cam1, cam2):
	sight1 = cam1.line_of_sight(pt)
	sight2 = cam2.line_of_sight(pt)
	return _correct_convergence_angle(nm.angle(sight1, sight2))

def conv_angle_line(line, cam1, cam2):
	lorig = line.origin
	lv = line.direction
	cv1 = nm.vecnormalize(lorig - cam1.focalpoint)
	xaxis = np.cross(cv1, lv)
	sight1 = np.cross(lv, xaxis)
	cv2 = nm.vecnormalize(lorig - cam2.focalpoint)
	xaxis = np.cross(cv2, lv)
	sight2 = np.cross(lv, xaxis)
	return _correct_convergence_angle(nm.angle(sight1, sight2))

#--- main

if __name__ == '__main__':

	CAMERA_POS = [0.0, 0.0, -1800.0]
	CAMERA_ANGLE = -90.0   # degree
	ROTATION_AXIS = [0.0, 1.0, 0.0]
	POINT = [100.0, 0.0, 0.0]
	LINE_PT0 = [0.0, 0.0, 0.0]
	LINE_PT1 = [0.0, -100.0, 0.0]

	camangle = nm.deg2rad(CAMERA_ANGLE)
	print('camera angle: {0:.1f} degrees'.format(nm.rad2deg(camangle)))
	print('')

	cam1 = nc.nkjcam()
	cam1.translateLocal(CAMERA_POS)
	cam1.print('camera 1')
	print('')

	cam2 = nc.nkjcam()
	cam2.translateLocal(CAMERA_POS)
	cam2.rotateGlobal(camangle * np.array(ROTATION_AXIS), 'rotvec')
	cam2.print('camera 2')
	print('')

	pt = POINT
	print('point: {0}'.format(pt))
	print('')

	line = nm.line3d(LINE_PT0, LINE_PT1)
	line.print('line')
	print('')

	# compute convergence angle

	convergence_p = conv_angle_point(pt, cam1, cam2)
	convergence_l = conv_angle_line(line, cam1, cam2)

	# show result

	print('--- result ---')
	print('camera angle:                    {0:.3f} degrees'.format(nm.rad2deg(_correct_convergence_angle(camangle))))
	print('convergence angle for the point: {0:.3f} degrees'.format(nm.rad2deg(convergence_p)))
	print('convergence angle for the line:  {0:.3f} degrees'.format(nm.rad2deg(convergence_l)))
	print('---')
