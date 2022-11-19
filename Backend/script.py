"""
Simple app to upload an image via a web form 
and view the inference results on the image in the browser.
"""
import argparse
import io
import os
from PIL import Image
import cv2
import numpy as np
import webbrowser
import torch
from io import BytesIO
import datetime
from pymongo import MongoClient
import gridfs


#'''
# Load Pre-trained Model
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
# force_reload = recache latest code
#'''
# Load Custom Model
model = torch.hub.load("ultralytics/yolov5", "custom", path = "./best (4).pt", force_reload=True)

connection = MongoClient("localhost", 27017)
database = connection['testpymongo']
dbimage = database.imagepy
fs = gridfs.GridFS(database)

# Set Model Settings

model.eval()
model.conf = 0.45  # confidence threshold (0-1)
model.iou = 0.45  # NMS IoU threshold (0-1) 

cap=cv2.VideoCapture('test_videos_weapon/4_Trim.mp4')
# Read until video is completed
while(cap.isOpened()):
    
    # Capture frame-by-fram ## read the camera frame
    success, frame = cap.read()
    if success == True:
        frame = cv2.resize(frame, (416,416))
        ret,buffer=cv2.imencode('.jpg',frame)
        frame=buffer.tobytes()
        
        #print(type(frame))
        img = Image.open(io.BytesIO(frame))
        results = model(img, size=416)
        #print(results)
        #print(results.pandas().xyxy[0])
        #results.render()  # updates results.imgs with boxes and labels
        # results.print()  # print results to screen
        df = results.pandas().xyxy[0]
        # print(df.get(key = 'name'))
        #convert remove single-dimensional entries from the shape of an array
        img = np.squeeze(results.render()) #RGB
        # read image as BGR
        img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) #BGR
        cv2.imshow('yolov5', img_BGR)
        if not df.empty:
            print(df._get_value(0,'name'))
            # date_string = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")
            now = datetime.datetime.now()
            current_time = now.strftime("%d_%m_%Y_%H_%M_%S")
            imagefilename = "uploads/"+current_time+".jpg"
            cv2.imwrite(imagefilename, img_BGR)
            # datafile =  open(imagefilename,"rb")
            # thedata = datafile.read()
            # datafile.close()
            imageString = img_BGR.tobytes()
            imageID = fs.put(imageString,filename=imagefilename,encoding='utf-8')
            print(imageID)
            meta = {
                'classevent': df._get_value(0,'name'),
                'imageevent': [
                    {
                        'imageID': imageID,
                        'shape': img_BGR.shape,
                        'dtype': str(img_BGR.dtype)
                    }
                ]
            }
            dbimage.insert_one(meta)
            webbrowser.open("http://127.0.0.1:5000/danger/" + str(meta['imageevent'][0]['imageId']))
            cv2.waitKey()
            cv2.destroyAllWindows()
        # if(df['name'] == "mask" | df['name'] == "weapon" | df['name'] == "snatch" | df['name'] == "fire"):
        #     print("Ok noted")
        #results.show() 
        #print(results.imgs)
        #print(type(img))
        #print(results)
        #plt.imshow(np.squeeze(results.render()))
        #print(type(img))
        #print(img.mode)
        if cv2.waitKey(25) & 0xFF == ord('q'):
                break
    else:
        break

# the video capture object
cap.release()
   
# Closes all the frames
cv2.destroyAllWindows()
