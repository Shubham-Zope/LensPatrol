import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
from tensorflow import keras
import pandas as pd
model =  keras.models.load_model('resnet.h5')
  
# creating the dataset


cap = cv2.VideoCapture('Watch_ Two Bike-Borne Men Snatch Gold Chain Of A Woman In Mohali_Trim.mp4')
data = {'Snatch':0, 'Accident':0, 'Weapon':0}
df= pd.DataFrame({'names':list(['Accident_Actual', 'Snatch_actual', 'Weapons_actual']), 'index':list([0, 1, 2])})
fig = plt.figure(figsize = (10, 5))
while(cap.isOpened()):
    ret, img = cap.read()
    if ret == True:
        img = cv2.resize(img, (224, 224))
        X = np.expand_dims(img,axis=0)
        images = np.vstack([X])
        q = model.predict(images)
        # print(q)
        prediction = np.argmax(q)
        print(df.iloc[prediction]['names'] + " " + str(format(q[0][prediction],".2f")))
        sn = float(format(q[0][1],".2f"))
        ac = float(format(q[0][0],".2f"))
        we = float(format(q[0][2],".2f"))
        print(sn*100, ac*100, we*100)
        data['Snatch'] = sn
        data['Accident'] = ac
        data['Weapon'] = we
        courses = list(data.keys())
        values = list(data.values())
        print(values)
        # creating the bar plot
        # plt.bar(courses, values, color ='maroon',width = 0.4)
        plt.xlabel("Classes")
        plt.ylabel("Probability")
        plt.title("Dekhte badmai")
        plt.ion()
        plt.cla()
        plt.bar(courses, values, color ='maroon',width = 0.4)
        plt.pause(0.01)
        # cv2.imshow("Image", img)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    else:
        break

# the video capture object
cap.release()
   
# Closes all the frames
cv2.destroyAllWindows()