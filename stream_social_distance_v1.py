# -*- coding: utf-8 -*-

"""

Created on Thu Nov 14 18:57:44 2019

@author: seraj

"""

import time

import cv2 
import math
import numpy as np

import itertools
import cx_Oracle
from datetime import datetime
from datetime import date
# Oracle ADW Connection
connection = cx_Oracle.connect('ADMIN/M1P4s5_w0rd#@dbml_high')
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
DISTANCE_MINIMUM=100

Tamy=600
Tamx=1200
Lat0=19.428589
Long0=-99.206125
Lat1=19.42819
Long1=-99.205351
cuenta=0

#from bird_view_transfo_functions import compute_perspective_transform,compute_point_perspective_transformation
from flask import Flask, render_template, Response

from tf_model_object_detection import Model 



app = Flask(__name__)

sub = cv2.createBackgroundSubtractorMOG2()  # create background subtractor



@app.route('/')

def index():

    """Video streaming home page."""

    return render_template('index.html')



def get_human_box_detection(boxes,scores,classes,height,width):

	""" 

	For each object detected, check if it is a human and if the confidence >> our threshold.

	Return 2 coordinates necessary to build the box.

	@ boxes : all our boxes coordinates

	@ scores : confidence score on how good the prediction is -> between 0 & 1

	@ classes : the class of the detected object ( 1 for human )

	@ height : of the image -> to get the real pixel value

	@ width : of the image -> to get the real pixel value

	"""

	array_boxes = list() # Create an empty list

	for i in range(boxes.shape[1]):

		# If the class of the detected object is 1 and the confidence of the prediction is > 0.6

		if int(classes[i]) == 1 and scores[i] > 0.75:

			# Multiply the X coordinnate by the height of the image and the Y coordinate by the width

			# To transform the box value into pixel coordonate values.

			box = [boxes[0,i,0],boxes[0,i,1],boxes[0,i,2],boxes[0,i,3]] * np.array([height, width, height, width])

			# Add the results converted to int

			array_boxes.append((int(box[0]),int(box[1]),int(box[2]),int(box[3])))

	return array_boxes





def get_centroids(array_boxes_detected):

	"""

	For every bounding box, compute the centroid and the point located on the bottom center of the box

	@ array_boxes_detected : list containing all our bounding boxes 

	"""

	array_centroids = [] # Initialize empty centroid lists 

	for index,box in enumerate(array_boxes_detected):

		# Draw the bounding box 

		# c

		# Get the both important points

		centroid = get_points_from_box(box)

		array_centroids.append(centroid)

	return array_centroids



def get_points_from_box(box):

	"""

	Get the center of the bounding and the point "on the ground"

	@ param = box : 2 points representing the bounding box

	@ return = centroid (x1,y1) and ground point (x2,y2)

	"""

	# Center of the box x = (x1+x2)/2 et y = (y1+y2)/2

	center_x = int(((box[1]+box[3])/2))

	center_y = int(((box[0]+box[2])/2))

	return (center_x,center_y)



def gen():

    """Video streaming generator function."""

    cap = cv2.VideoCapture('768x576.avi')

    model_path="./models/frozen_inference_graph.pb" 

    model = Model(model_path)
    cuenta = 0


    # Read until video is completed

    while(cap.isOpened()):

        ret, frame = cap.read()  # import image

        if not ret: #if vid finish repeat

            frame = cv2.VideoCapture("768x576.avi")

            continue

        if ret:  # if there is a frame continue with code

            image = cv2.resize(frame, (0, 0), None, 1, 1)  # resize image

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # converts image to gray

            fgmask = sub.apply(gray)  # uses the background subtraction

            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))  # kernel to apply to the morphology

            closing = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel)

            opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)

            dilation = cv2.dilate(opening, kernel)

            retvalbin, bins = cv2.threshold(dilation, 220, 255, cv2.THRESH_BINARY)  # removes the shadows

            contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)



            # Make the predictions for this frame

            (boxes, scores, classes) =  model.predict(frame)

	    # Get the human detected in the frame and return the 2 points to build the bounding box  

            array_boxes_detected = get_human_box_detection(boxes,scores[0].tolist(),classes[0].tolist(),frame.shape[0],frame.shape[1])


            array_already_drawn = list() # Initialize empty drawn lists 


            # Check if 2 or more people have been detected (otherwise no need to detect)
            cuenta=cuenta+1
            today = datetime.now()
            if len(array_boxes_detected) >= 2:
               for i,pair in enumerate(itertools.combinations(array_boxes_detected, r=2)):
               #for i in range(len(contours)):  # cycles through all contours in current frame

                   # calculating centroids of contours

                   cnt1 = pair[0]

                   cx1 = int(((cnt1[0]+cnt1[2])/2))

                   cy1 = int(((cnt1[1]+cnt1[3])/2))

                   cnt2 = pair[1]

                   cx2 = int(((cnt2[0]+cnt2[2])/2))

                   cy2 = int(((cnt2[1]+cnt2[3])/2))
                   human1_drawn=False
                   human1_dist=1
                   j=0
                   while j<len(array_already_drawn):
                       a,b,c= array_already_drawn[j]
                       j+=1
                       if a==cx1 and b==cy1:
                   #       print('FOUND ', j, a, b, c)
                          human1_drawn= True
                          human1_dist= c
                          break
                   human2_drawn=False
                   human2_dist=1
                   j=0
                   while j<len(array_already_drawn):
                       a,b,c= array_already_drawn[j]
                       j+=1
                       if a==cx2 and b==cy2:
                   #       print('FOUND ', j, a, b, c)
                          human2_drawn= True
                          human2_dist= c
                          break
                   # Check if the distance between each combination of points is less than the minimum distance chosen
                   #print(i,cnt1[0],cnt1[1],cnt2[0],cnt2[1],cx1,cy1,cx2,cy2)
                   if math.sqrt( (cx1 - cx2)**2 + (cy1 - cy2)**2 ) < int(DISTANCE_MINIMUM):
                      if human1_drawn==False or human1_dist==1:
                         array_already_drawn.append((cx1,cy1,0))
                         cv2.rectangle(image, (cnt1[1], cnt1[0]), (cnt1[3], cnt1[2]), COLOR_RED, 2)

                         LatN= Lat0 - (cy1*(Lat0-Lat1))/Tamy
                         LongN= Long0 + (cx1*(Long1-Long0))/Tamx
                         print(cuenta,LatN,LongN,today)
                         cursor = connection.cursor()
                         dataToInsert=[(cuenta,LatN,LongN,0,today)]
                         cursor.executemany("INSERT INTO MLUSER.COVID_SOCIAL_DISTANCIA_T VALUES (:1, :2, :3, :4, :5)", dataToInsert)
                         connection.commit()
                   #      print('APPENDED NOT HEALTHY ', cx1, cy1)
                      if human2_drawn==False or human2_dist==1:
                         array_already_drawn.append((cx2,cy2,0))
                         cv2.rectangle(image, (cnt2[1], cnt2[0]), (cnt2[3], cnt2[2]), COLOR_RED, 2)

                         LatN= Lat0 - (cy2*(Lat0-Lat1))/Tamy
                         LongN= Long0 + (cx2*(Long1-Long0))/Tamx
                         print(cuenta,LatN,LongN,today)
                         cursor = connection.cursor()
                         dataToInsert=[(cuenta,LatN,LongN,0,today)]
                         cursor.executemany("INSERT INTO MLUSER.COVID_SOCIAL_DISTANCIA_T VALUES (:1, :2, :3, :4, :5)", dataToInsert)
                         connection.commit()
                   #      print('APPENDED NOT HEALTHY ',cx2,cy2)
                   #   print('NOT healthy - ALERT')
                   else:
                      if human1_drawn==False:
                         array_already_drawn.append((cx1,cy1,1))
                         cv2.rectangle(image, (cnt1[1], cnt1[0]), (cnt1[3], cnt1[2]), COLOR_GREEN, 2)

                         LatN= Lat0 - (cy1*(Lat0-Lat1))/Tamy
                         LongN= Long0 + (cx1*(Long1-Long0))/Tamx
                         print(cuenta,LatN,LongN,today)
                         cursor = connection.cursor()
                         dataToInsert=[(cuenta,LatN,LongN,1,today)]
                         cursor.executemany("INSERT INTO MLUSER.COVID_SOCIAL_DISTANCIA_T VALUES (:1, :2, :3, :4, :5)", dataToInsert)
                         connection.commit()
                   #      print('APPENDED HEALTHY ',cx1,cy1)
                      if human2_drawn==False:
                         array_already_drawn.append((cx2,cy2,1))
                         cv2.rectangle(image, (cnt2[1], cnt2[0]), (cnt2[3], cnt2[2]), COLOR_GREEN, 2)

                         LatN= Lat0 - (cy2*(Lat0-Lat1))/Tamy
                         LongN= Long0 + (cx2*(Long1-Long0))/Tamx
                         print(cuenta,LatN,LongN,today)
                         cursor = connection.cursor()
                         dataToInsert=[(cuenta,LatN,LongN,1,today)]
                         cursor.executemany("INSERT INTO MLUSER.COVID_SOCIAL_DISTANCIA_T VALUES (:1, :2, :3, :4, :5)", dataToInsert)
                         connection.commit()
                   #      print('APPENDED HEALTHY ',cx2,cy2)
                   #   print('Healthy - nothing to do')
                   # creates a rectangle around contour

                   #cv2.rectangle(image, (cnt1[1], cnt1[0]), (cnt1[3], cnt1[2]), (0, 255, 0), 2)

                   #cv2.rectangle(image, (cnt2[1], cnt2[0]), (cnt2[3], cnt2[2]), (0, 255, 0), 2)


            #minarea = 400

            #maxarea = 50000

            #for i in range(len(contours)):  # cycles through all contours in current frame

            #    if hierarchy[0, i, 3] == -1:  # using hierarchy to only count parent contours (contours not within others)

            #        area = cv2.contourArea(contours[i])  # area of contour

            #        if minarea < area < maxarea:  # area threshold for contour

                        # calculating centroids of contours

            #            cnt = contours[i]

            #            M = cv2.moments(cnt)

            #            cx = int(M['m10'] / M['m00'])

            #            cy = int(M['m01'] / M['m00'])

                        # gets bounding points of contour to create rectangle

                        # x,y is top left corner and w,h is width and height

            #            x, y, w, h = cv2.boundingRect(cnt)

                        # creates a rectangle around contour

           #             cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                        # Prints centroid text in order to double check later on

           #             cv2.putText(image, str(cx) + "," + str(cy), (cx + 10, cy + 10), cv2.FONT_HERSHEY_SIMPLEX,.3, (0, 0, 255), 1)

           #             cv2.drawMarker(image, (cx, cy), (0, 255, 255), cv2.MARKER_CROSS, markerSize=8, thickness=3,line_type=cv2.LINE_8)

        #cv2.imshow("countours", image)

        frame = cv2.imencode('.jpg', image)[1].tobytes()

        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        #time.sleep(0.1)

        key = cv2.waitKey(20)

        if key == 27:

           break

   

        



@app.route('/video_feed')

def video_feed():

    """Video streaming route. Put this in the src attribute of an img tag."""

    return Response(gen(),

                    mimetype='multipart/x-mixed-replace; boundary=frame')