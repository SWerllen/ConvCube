"""
Script: record.py
=================

Description:
------------
	
	Records a new video and stores it

Usage:
------

	python record.py

##################
Jay Hack
Winter 2015
jhack@stanford.edu
##################
"""
import time
import numpy as np
import cv2
from ModalDB import ModalClient, Video, Frame

from convcube.db import dbschema
from convcube.cv.preprocess import resize
from convcube.convnets.euclidean import EuclideanConvNet
from convcube.cube import ConvNetCube

if __name__ == '__main__':

	#=====[ Step 1: boot up	and create convcube schema ]=====
	client = ModalClient('./data/db', schema=dbschema)

	#=====[ Step 2: turn on the webcam	]=====
	cap = cv2.VideoCapture(0)
	cv2.namedWindow('DISPLAY')

	#=====[ Step 3: create video name	]=====
	video_name = raw_input('Name this video? [N] ')
	if video_name == '':
		video_name = 'video_' + str(time.time()).split('.')[0]
	video = client.insert(Video, video_name, {})
	print 'Video name: %s' % video_name

	#=====[ Step 4: get convnet	]=====
	loc_convnet = EuclideanConvNet()
	loc_convnet.load('./models/localization/5layer.filter_3333.nfilters_16321632.acc_0035.convnet')
	cube = ConvNetCube(loc_convnet=loc_convnet)

	#=====[ Step 3: capture frames until ESC	]=====
	i = 0
	while True:

		#####[ GRAB IMAGE FROM WEBCAM	]#####
		ret, image = cap.read()
		image = resize(image)

		#####[ INSERT INTO DB	]#####
		frame_name = 'frame_' + str(i)
		frame = client.insert(Frame, frame_name, {}, parent=video, method='mv')
		frame['image'] = image

		#####[ DRAW OUTPUT	]#####
		tl, br = cube.localize(image)
		print [tl, br]
		frame['bounding_box'] = [tl, br]
		disp_img = cube.draw_output(image)
		cv2.imshow('DISPLAY', disp_img)
		i += 1

		#####[ BREAK ON ESCAPE	]#####
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	#=====[ Step 4: cleanup	]=====
	cap.release()
	cv2.destroyAllWindows()


