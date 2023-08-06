#
# [name] nkj.pygame.py
# [exec] python -m nkj.pygame
# [purpose] wrapping library for pygame
#
# Written by Yoshikazu NAKAJIMA
#

DEBUGLEVEL = 0

import os
import sys
import time
import cv2
import pygame

sys.path.append(os.path.abspath(".."))

import nkj.core as nk
import nkj.str as ns
from nkj.str import ldprint

import nkj.cv as ncv
from nkj.cv import *

class nkjgm():
	#-- class variables
	_classname = "nkjgm"

	def __init__(self):
		ldprint(["classname: ", nkjgm._classname])

#-- main

if __name__ == "__main__":
	WINDOWNAME = "image"
	LINEWIDTH = 5
	LINEBLEND = 2

	ns.LIB_DEBUGLEVEL = DEBUGLEVEL

	pygame.init() # PyGame の初期化

	cap = cv2.VideoCapture(0)

	# Initialize pygame image screen

	ret, frame = cap.read()

	height, width = frame.shape[:2]
	ldprint(["image size: (", str(width), ", ", str(height), ")"])

	screen = pygame.display.set_mode((width, height)) # ベーススクリーン

	# Initialize blended surface

	s = pygame.Surface((width, height)) # ブレンディッドサーフェイス
	s.set_alpha(64) # 0-255

	while True:
		ret, cvimage = cap.read()

		"""
		frame = cv2.hconcat([frame, frame]) # 横に連結
		frame = cv2.vconcat([frame, frame]) # 縦に連結
		"""
		"""
		# Image display with OpenCV
		cv2.imshow(WINDOWNAME, cvimage)
		if (cv2.waitKey(1) == 27):
			break
		"""

		# convert opencv image to pygame image
		rgbimage = cv2.cvtColor(cvimage, cv2.COLOR_BGR2RGB).swapaxes(0, 1)
		gmsurf = pygame.surfarray.make_surface(rgbimage)

		# display pygame image

		screen.blit(gmsurf, (0, 0)) # 指定（左上座標）の位置に画像を描画する

		# draw
		"""
		pygame.draw.aaline(screen, (255, 0, 0), (0, 0), (300, 300), LINEBLEND) # アンチエイリアシングを施した線の描画
		"""
		pygame.draw.line(screen, (255, 0, 0), (0, 0), (300, 300), LINEWIDTH) # 線の描画

		# alpha blending
		"""
		pygame.draw.polygon(s, (255, 255, 255), [(0, 0), (width, 0), (width, height), (0, height)]) # 全体を白で塗る
		pygame.draw.rect(s, (255, 255, 255), s.get_rect()) # 全体を白で塗る
		"""
		s.blit(gmsurf, (0, 0)) # 黒や白の背景ではカメラ画像が暗く（or 白っぽく）なるので、背景画像を描画．surface にも blit() は使える．
		pygame.draw.line(s, (255, 0, 0), (300, 0), (300, 300), LINEWIDTH) # 線の描画
		screen.blit(s, (0, 0)) # スクリーンにアルファブレンドする画像を描画する

		# flush
		pygame.display.update()
		"""
		pygame.display.flip() # ハードウェアアクセラレーションにも対応した update()
		"""

		"""
		pygame.event.get() # update() の後に、pygame プロセスイベントを発生させないとウィンドウが再描画されないことがあるので、プロセスを取得してみる
		"""

		flag = False
		for event in pygame.event.get():
			if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
				x, y = event.pos
				ldprint(["mouse click: (", str(x), ", ", str(y), ")"])

			if (event.type == pygame.QUIT):
				flag = True
				break
			if (event.type == pygame.KEYDOWN):
				if (event.key == pygame.K_ESCAPE):
					flag = True
					break
		if (flag):
			break

		"""
		key = pygame.key.get_pressed()
		if key[pygame.K_ESCAPE]:
			break
		"""

	pygame.quit() # PyGame の終了

	cap.release()
	cv2.destroyAllWindows()

