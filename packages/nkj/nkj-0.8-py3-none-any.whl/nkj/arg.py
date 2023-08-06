#
# [name] nkj.arg.py
# [exec] python -m nkj.arg <input.file> [-s <xsize>x<ysize>] [-p <xpitch>,<ypitch>]
#        python -m nkj.arg test
#        python -m nkj.arg test -p 0.01
#        python -m nkj.arg test -p 0.01,0.02 -s 1980x1024
#
# Written by Yoshikazu NAKAJIMA (Fri Mar 25 23:10:42 JST 2022)
#

import argparse
import re
from .str import *
from .math import *

argf_floatpair = lambda x:list(map(float, x.split(',')))

argf_size = lambda x:list(map(int, re.split('[xX]', x)))   # <文字列>.split() と re.split('<正規表現>', <文字列>) は違う関数．

def reshape_argumentpair(s):
	if (type(s) is not list):
		___ERROR___
	if (len(s) == 1): 
		s = [s[0], s[0]]
	elif (len(s) == 2): 
		pass
	else:
		___ERROR___
	return s

def reshape_argument(s):  # alias
	return reshape_argumentpair(s)


#-- main

if __name__ == '__main__':
	_DEBUG_LEVEL = 0
	_DEFAULT_IMAGESIZE = [640, 480]
	_DEFAULT_PIXELPITCH = [0.1, 0.1]

	debuglevel(_DEBUG_LEVEL)

	if (False):   #- preliminary test for lambda, list, map, and split().
		dprint((lambda x:list(map(int, x.split(','))))('100'))
		dprint((lambda x:list(map(int, x.split(','))))('100,200'))

	parser = argparse.ArgumentParser()

	parser.add_argument('input', help='input.file')
	parser.add_argument('-s', '--image_size', type=argf_size, default=_DEFAULT_IMAGESIZE, help='image size: <xsize>x<ysize>, ex) 640x480')
	parser.add_argument('-p', '--pixel_pitch', type=argf_floatpair, default=_DEFAULT_PIXELPITCH, help='pixel pitch')

	args = parser.parse_args()

	filename = args.input
	imagesize = args.image_size
	pixelpitch = reshape_argument(args.pixel_pitch)

	print('input file:   \'{0}\''.format(filename))
	print('image size:  {0}'.format(imagesize))
	print('pixel pitch: {0}'.format(pixelpitch))

