import numpy as np
import os
import cv2
import imutils
import math
from random import *
import json

def synthesis(config):
	rotation_ = config['CONFIG']['ROTATION']
	scale_ = config['CONFIG']['SCALE']
	save_folder = config['CONFIG']['SAVE_PATH'] + '/'
	image_path = config['CONFIG']['IMAGE_PATH'] + '/'
	bg_path = config['CONFIG']['BG_PATH'] + '/'
	obj_name = config['CONFIG']['CLASSES']
	num_object_images = np.zeros(len(obj_name), dtype=int)
	# image_path = '/home/irobot/catkin_ws/src/capture_openni/images/'
	# bg_path = '/home/irobot/catkin_ws/src/capture_openni/bg/'

	l = os.listdir(image_path)
	l_bg = os.listdir(bg_path)
	file_names = [x for x in l]
	for j in range(0,len(obj_name)):
		for i in file_names:
			if int(i[0:2]) == j+1:
				num_object_images[j] = num_object_images[j] + 1
	num_BG = len(l_bg)
	min_num_obj = config['CONFIG']['NUM_MIN_OBJ']
	max_num_obj = config['CONFIG']['NUM_MAX_OBJ']
####################
	scale_min = config['CONFIG']['SCALE_MIN']
	scale_max = config['CONFIG']['SCALE_MAX']
####################
	for index in range(0,config['CONFIG']['NUM_IMAGES']):
		print index
		try:
			BG_index = randint(1,num_BG)
			num_obj = randint(min_num_obj, max_num_obj)
			obj_index = np.zeros(num_obj, dtype=int)
			obj_picture_index = np.zeros(num_obj, dtype=int)
			BGRA = []
			object_names = []

			for i in range(0,num_obj):
				obj_index[i] = randint(0,len(obj_name)-1)
				obj_picture_index[i] = randint(1, num_object_images[obj_index[i]])
				BGRA.append(cv2.imread(image_path + '%.2i_%.4i.png'%(obj_index[i]+1, obj_picture_index[i]), cv2.IMREAD_UNCHANGED))
				object_names.append(obj_name[obj_index[i]])

			BG = cv2.imread(bg_path + '%i.jpg'%BG_index)
			# BG_seg = cv2.imread(background_folder_path + 'bg_seg.jpg')

			scale = np.zeros(num_obj,dtype=int)
			angle = np.zeros(num_obj,dtype=int)

			for i in range(0,num_obj):
				scale[i] = randint(scale_min, scale_max)
				angle[i] = randrange(0,360)
				cols = BGRA[i].shape[1]
				rows = BGRA[i].shape[0]
				if scale_:
					if BGRA[i].shape[0] > BGRA[i].shape[1]:
						BGRA[i] = cv2.resize(BGRA[i],(int(round(scale[i]*(float(cols)/float(rows)))), scale[i]))
					else :
						BGRA[i] = cv2.resize(BGRA[i], (scale[i], int(round(scale[i]*(float(rows)/float(cols))))))

				if rotation_:
					BGRA[i] = imutils.rotate_bound(BGRA[i],angle[i])
			BG = cv2.resize(BG, (640, 480))
			BG_seg_sum = cv2.cvtColor(BG,cv2.COLOR_BGR2GRAY) * 0
			BG_seg = []
			for i in range(0,num_obj):
				BG_seg.append(cv2.cvtColor(BG,cv2.COLOR_BGR2GRAY) * 0)

			y_diff = np.zeros(num_obj, dtype=int)
			x_diff = np.zeros(num_obj, dtype=int)
			bbox_ymin = np.zeros(num_obj, dtype=int)
			bbox_xmin = np.zeros(num_obj, dtype=int)
			bbox_ymax = np.zeros(num_obj, dtype=int)
			bbox_xmax = np.zeros(num_obj, dtype=int)

			for i in range(0,num_obj):
				y_diff[i] = BG.shape[0] - BGRA[i].shape[0]
				x_diff[i] = BG.shape[1] - BGRA[i].shape[1]
				bbox_ymin[i] = math.floor(y_diff[i] * random())
				bbox_xmin[i] = math.floor(x_diff[i] * random())
				bbox_ymax[i] = bbox_ymin[i] + BGRA[i].shape[0]
				bbox_xmax[i] = bbox_xmin[i] + BGRA[i].shape[1]

			alpha = []
			BGR = []
			for i in range(0,num_obj):
				alpha.append(BGRA[i][:,:,3])
				alpha[i] = alpha[i].astype(float)/255
				BGR.append(cv2.cvtColor(BGRA[i], cv2.COLOR_BGRA2BGR))

			# cv2.imshow('img',alpha[1])
			# cv2.waitKey(0)
			# for i in range(0,1):
			# 	BG[bbox_ymin[i]:bbox_ymax[i], bbox_xmin[i]:bbox_xmax[i],:] = BGR[i]*alpha[i] + BG[bbox_ymin[i]:bbox_ymax[i], bbox_xmin[i]:bbox_xmax[i],:]*(1-alpha[i])
		
			BGR_array = np.array(BGR)
			alpha_array = np.array(alpha)
			BG_array = np.array(BG)

			for i in range(0,num_obj):
				for j in range(0,3):
					BG_array[bbox_ymin[i]:bbox_ymax[i], bbox_xmin[i]:bbox_xmax[i],j] = np.multiply(BGR_array[i][:,:,j],alpha_array[i]) + np.multiply(BG_array[bbox_ymin[i]:bbox_ymax[i], bbox_xmin[i]:bbox_xmax[i],j],(1-alpha_array[i]))
				BG_seg[i][bbox_ymin[i]:bbox_ymax[i], bbox_xmin[i]:bbox_xmax[i]] = alpha_array[i]
				BG_seg_sum = BG_seg_sum + BG_seg[i]

		except:
			continue

		for i in range(0,num_obj-1):
			for j in range(i+1,num_obj):
				BG_seg[i] = BG_seg[i] - BG_seg[i]*BG_seg[j]

		if not os.path.exists(save_folder + 'Images'):
			os.mkdir(save_folder + 'Images')
		image_save = os.path.join(save_folder,'Images')
			# print(image_save)

		if not os.path.exists(save_folder + 'Masks'):
			os.mkdir(save_folder + 'Masks')
		mask_save = os.path.join(save_folder,'Masks')
			# print(mask_save)

		# if not os.path.exists(save_folder + 'Annotations'):
		# 	os.mkdir(save_folder + 'Annotations')
		# 	annotation_save = os.path.join(save_folder,'Annotations')
		# 	print(annotation_save)

		if not os.path.exists(save_folder + 'labels'):
			os.mkdir(save_folder + 'labels')
		label_save = os.path.join(save_folder,'labels')

		# print annotation_save

		# f_annotation = open(annotation_save + '/%.6d.txt'%index,'w')
		f_label = open(label_save + '/%.6d.txt'%index,'w')

		cv2.imwrite(image_save + '/%.6d.jpg' % index, BG_array)

		for i in range(0,num_obj):
			cv2.imwrite(mask_save + '/%.6d_%.2d.png'%(index,i+1),BG_seg[i])
			# f_annotation.write("%s\n"%object_names[i])
			temp_x_center = ((float(bbox_xmax[i])+float(bbox_xmin[i]))/2)/640
			temp_y_center = ((float(bbox_ymax[i])+float(bbox_ymin[i]))/2)/480
			temp_width = (float(bbox_xmax[i])-float(bbox_xmin[i]))/640
			temp_height = (float(bbox_ymax[i])-float(bbox_ymin[i]))/480
			# print(temp_x_center)
			# print(temp_y_center)
			# print(temp_width)
			# print(temp_height)
			f_label.write("%i %f %f %f %f\n"%(obj_index[i],temp_x_center,temp_y_center,temp_width,temp_height))
		
		# f_annotation.close()
		f_label.close()


config_file = open("config.json",'r')
config = json.load(config_file)

synthesis(config)