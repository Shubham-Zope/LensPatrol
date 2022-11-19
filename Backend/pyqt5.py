from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import sys
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
from centroidtracker import CentroidTracker

os.environ["GIT_PYTHON_REFRESH"] = "quiet"

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
  
        # setting title
        self.setWindowTitle("Python ")
  
        # setting geometry
        self.setGeometry(100, 100, 600, 400)
  
        # calling method
        self.UiComponents()
  
        # showing all the widgets
        self.show()
  
    # method for widgets
    def UiComponents(self):
  
        # creating a push button
        button = QPushButton("CLICK", self)
  
        # setting geometry of button
        button.setGeometry(200, 150, 100, 30)
  
        # adding action to a button
        button.clicked.connect(self.clickme)

    def non_max_suppression_fast(self, boxes, overlapThresh):
        try:
            if len(boxes) == 0:
                return []

            if boxes.dtype.kind == "i":
                boxes = boxes.astype("float")

            pick = []

            x1 = boxes[:, 0]
            y1 = boxes[:, 1]
            x2 = boxes[:, 2]
            y2 = boxes[:, 3]

            area = (x2 - x1 + 1) * (y2 - y1 + 1)
            idxs = np.argsort(y2)

            while len(idxs) > 0:
                last = len(idxs) - 1
                i = idxs[last]
                pick.append(i)

                xx1 = np.maximum(x1[i], x1[idxs[:last]])
                yy1 = np.maximum(y1[i], y1[idxs[:last]])
                xx2 = np.minimum(x2[i], x2[idxs[:last]])
                yy2 = np.minimum(y2[i], y2[idxs[:last]])

                w = np.maximum(0, xx2 - xx1 + 1)
                h = np.maximum(0, yy2 - yy1 + 1)

                overlap = (w * h) / area[idxs[:last]]

                idxs = np.delete(idxs, np.concatenate(([last],
                                                       np.where(overlap > overlapThresh)[0])))

            return boxes[pick].astype("int")
        except Exception as e:
            print("Exception occurred in non_max_suppression : {}".format(e))
  
    # action method
    def clickme(self):
  
        # printing pressed
        # print("pressed")
        global prevminute_1 
        global nextminute_1
        global lpc_count
        global opc_count

        model = torch.hub.load("ultralytics/yolov5", "custom", path = "./best (4).pt", force_reload=True)

        connection = MongoClient("localhost", 27017)
        database = connection['testpymongo']
        dbimage = database.imagepy
        dbanalysis = database.analysis
        fs = gridfs.GridFS(database)

        # Set Model Settings

        protopath = "MobileNetSSD_deploy.prototxt"
        modelpath = "MobileNetSSD_deploy.caffemodel"
        detector = cv2.dnn.readNetFromCaffe(prototxt=protopath, caffeModel=modelpath)

        model.eval()
        model.conf = 0.45  # confidence threshold (0-1)
        model.iou = 0.45  # NMS IoU threshold (0-1) 

        cap=cv2.VideoCapture('test_video.mp4')

        object_id_list = []
        dtime = dict()
        dwell_time = dict()

        CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

        tracker = CentroidTracker(maxDisappeared=80, maxDistance=90)

        # Read until video is completed

        prevminute_1 = datetime.datetime.now().minute
        nextminute_1 = prevminute_1 + 1
        lpc_count = 0
        opc_count = 0
        prev_count = 0





        while(cap.isOpened()):

            # Capture frame-by-fram ## read the camera frame
            success, frame = cap.read()
            if success == True:
                frame = cv2.resize(frame, (416,416))
                #Camer tampering start
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if np.average(gray) < 20:
                    print('Camera tampered')
                    now = datetime.datetime.now()
                    current_time = now.strftime("%d_%m_%Y_%H_%M_%S")
                    imagefilename = "uploads/"+current_time+".jpg"
                    cv2.imwrite(imagefilename, frame)
                    # datafile =  open(imagefilename,"rb")
                    # thedata = datafile.read()
                    # datafile.close()
                    imageString = frame.tobytes()
                    imageID = fs.put(imageString,filename=imagefilename,encoding='utf-8')
                    print(imageID)
                    meta = {
                        'classevent': 'tampering',
                        'imageevent': [
                            {
                                'imageID': imageID,
                                'shape': frame.shape,
                                'dtype': str(frame.dtype)
                            }
                        ],
                        'timestamp': datetime.datetime.now(),
                        'flagged_as': 'suspicious'
                    }
                    dataid = dbimage.insert_one(meta).inserted_id
                    webbrowser.open("http://127.0.0.1:5000/getalertpage?dataid=" + str(dataid))
                    cv2.waitKey()
                    cap.release()
                    cv2.destroyAllWindows()
                #Camera tampering over

                #analysis start

                (H, W) = frame.shape[:2]

                blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
                detector.setInput(blob)
                person_detections = detector.forward()
                rects = []
                for i in np.arange(0, person_detections.shape[2]):
                    confidence = person_detections[0, 0, i, 2]
                    if confidence > 0.5:
                        idx = int(person_detections[0, 0, i, 1])

                        if CLASSES[idx] != "person":
                            continue
                        

                        #post hour intruder start


                        if datetime.datetime.now().hour > 24:
                            print('Post Hour Intruder')
                            now = datetime.datetime.now()
                            current_time = now.strftime("%d_%m_%Y_%H_%M_%S")
                            imagefilename = "uploads/"+current_time+".jpg"
                            cv2.imwrite(imagefilename, frame)
                            # datafile =  open(imagefilename,"rb")
                            # thedata = datafile.read()
                            # datafile.close()
                            imageString = frame.tobytes()
                            imageID = fs.put(imageString,filename=imagefilename,encoding='utf-8')
                            print(imageID)
                            meta = {
                                'classevent': 'Post Hour Intruder',
                                'imageevent': [
                                    {
                                        'imageID': imageID,
                                        'shape': frame.shape,
                                        'dtype': str(frame.dtype)
                                    }
                                ],
                                'timestamp': datetime.datetime.now(),
                                'flagged_as': 'suspicious'
                            }
                            dataid = dbimage.insert_one(meta).inserted_id
                            webbrowser.open("http://127.0.0.1:5000/getalertpage?dataid=" + str(dataid))
                            cv2.waitKey()
                            cap.release()
                            cv2.destroyAllWindows()
                        else:
                            person_box = person_detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                            (startX, startY, endX, endY) = person_box.astype("int")
                            rects.append(person_box)

                        #post hour intruder over

                        


                boundingboxes = np.array(rects)
                boundingboxes = boundingboxes.astype(int)
                rects = self.non_max_suppression_fast(boundingboxes, 0.3)

                objects = tracker.update(rects)
                for (objectId, bbox) in objects.items():
                    x1, y1, x2, y2 = bbox
                    x1 = int(x1)
                    y1 = int(y1)
                    x2 = int(x2)
                    y2 = int(y2)

                    if objectId not in object_id_list:
                        object_id_list.append(objectId)
                        dtime[objectId] = datetime.datetime.now()
                        dwell_time[objectId] = 0
                    else:
                        curr_time = datetime.datetime.now()
                        old_time = dtime[objectId]
                        time_diff = curr_time - old_time
                        dtime[objectId] = datetime.datetime.now()
                        sec = time_diff.total_seconds()
                        dwell_time[objectId] += sec


                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    text = "{}|{}".format(objectId, int(dwell_time[objectId]))
                    cv2.putText(frame, text, (x1, y1-5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)
                
                lpc_count = len(objects)
                opc_count = len(object_id_list)
                
                if(datetime.datetime.now().minute == nextminute_1):
                    datemonthyear = "{}:{}:{}".format(datetime.datetime.now().day, datetime.datetime.now().month,datetime.datetime.now().year)
                    tttext = "{}:{}".format(datetime.datetime.now().hour,datetime.datetime.now().minute-1)
                    percount = opc_count-prev_count
                    print(opc_count-prev_count) 
                    prev_count = opc_count
                    if not dbanalysis.count_documents({"date": datemonthyear}) > 0:
                        meta = {
                                "date": datemonthyear,
                                "time": [tttext],
                                "personcount": [percount]
                               }
                        dataid = dbanalysis.insert_one(meta)
                    else:
                        data_event = dbanalysis.find_one({'date': datemonthyear})
                        timea = data_event['time']
                        persa = data_event['personcount']
                        timea.append(tttext)
                        persa.append(percount)
                        myquery =  {'date': datemonthyear} 
                        newvalues = { "$set": { "time":  timea, "personcount": persa} }
                        dbanalysis.update_one(myquery, newvalues)
  
                    prevminute_1 = datetime.datetime.now().minute
                    if(prevminute_1+1 >= 60):
                        nextminute_1 = 0
                    else:
                        nextminute_1 = prevminute_1 + 1

                
                cv2.imshow('yolov5', frame)
                
                # analysis over

                # yolo start
                # ret,buffer=cv2.imencode('.jpg',frame)
                # frame=buffer.tobytes()

                # #print(type(frame))
                # img = Image.open(io.BytesIO(frame))
                # results = model(img, size=416)
                # #print(results)
                # #print(results.pandas().xyxy[0])
                # #results.render()  # updates results.imgs with boxes and labels
                # # results.print()  # print results to screen
                # df = results.pandas().xyxy[0]
                # # print(df.get(key = 'name'))
                # #convert remove single-dimensional entries from the shape of an array
                # img = np.squeeze(results.render()) #RGB
                # # read image as BGR
                # img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) #BGR
                # cv2.imshow('yolov5', img_BGR)
                # if not df.empty:
                #     print(df._get_value(0,'name'))
                #     # date_string = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")
                #     now = datetime.datetime.now()
                #     current_time = now.strftime("%d_%m_%Y_%H_%M_%S")
                #     imagefilename = "uploads/"+current_time+".jpg"
                #     cv2.imwrite(imagefilename, img_BGR)
                #     # datafile =  open(imagefilename,"rb")
                #     # thedata = datafile.read()
                #     # datafile.close()
                #     imageString = img_BGR.tobytes()
                #     imageID = fs.put(imageString,filename=imagefilename,encoding='utf-8')
                #     print(imageID)
                #     meta = {
                #         'classevent': df._get_value(0,'name'),
                #         'imageevent': [
                #             {
                #                 'imageID': imageID,
                #                 'shape': img_BGR.shape,
                #                 'dtype': str(img_BGR.dtype)
                #             }
                #         ],
                #         'timestamp': datetime.datetime.now(),
                #         'flagged_as': 'suspicious'
                #     }
                #     dataid = dbimage.insert_one(meta).inserted_id
                #     webbrowser.open("http://127.0.0.1:5000/getalertpage?dataid=" + str(dataid))
                #     cv2.waitKey()
                #     cap.release()
                #     cv2.destroyAllWindows()
                # yolo end

                if cv2.waitKey(25) & 0xFF == ord('q'):
                        break
            else:
                break
            
        # the video capture object
        cap.release()

        # Closes all the frames
        cv2.destroyAllWindows()

  
# create pyqt5 app
App = QApplication(sys.argv)
  
# create the instance of our Window
window = Window()
  
# start the app
sys.exit(App.exec())