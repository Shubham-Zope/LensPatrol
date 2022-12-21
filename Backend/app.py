from flask import *
import cv2
import numpy as np
import datetime
import imutils
from time import sleep
import subprocess
from pymongo import MongoClient
import numpy as np
import gridfs
import codecs
import base64
from bson.objectid import ObjectId
import smtplib
import ssl
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

app=Flask(__name__)

load_dotenv(dotenv_path='password.env')

APPPASSWORD = os.getenv('APPPASSWORD')

smtp_port = 587                 # Standard secure SMTP port
smtp_server = "smtp.gmail.com"  # Google SMTP Server

connection = MongoClient("localhost", 27017)
database = connection['testpymongo']
dbimage = database.imagepy
dbanalysis = database.analysis

fs = gridfs.GridFS(database)

@app.route('/')
def index():
    a = 1
    subprocess.run(["python", "script.py"])
    return render_template('index.html')


@app.route('/chart')
def chart():
    return render_template('chart.html')


@app.route('/chartapi', methods=['GET', 'POST'])
def chartapi():
    if request.method == 'GET':
        if(not request.args):
            timea = []
            persa = []
            persamax = 0
            chartjson = {
            'time': timea,
            'personcount': persa,
            'persamax': persamax
        }
        elif(request.args.get('fromtime')):
            fromtime = request.args.get('fromtime').split('T')[1]
            totime = request.args.get('totime').split('T')[1]
            fromtimehour = int(fromtime.split(":")[0])
            totimehour = int(totime.split(":")[0])
            fromtimemin = int(fromtime.split(":")[1])
            totimemin = int(totime.split(":")[1])
            datemonthyear = "{}:{}:{}".format(datetime.datetime.now().day, datetime.datetime.now().month,datetime.datetime.now().year)
            data_event = dbanalysis.find_one({'date': datemonthyear})
            if(totimehour - fromtimehour <= 1):
                timea = data_event['time']
                persa = data_event['personcount']
                timeper = []
                personper = []
                for i in range(len(timea)):
                    if fromtime <= timea[i] <= totime:
                        timeper.append(timea[i])
                        personper.append(persa[i])
                persamax = max(personper)
                chartjson = {
                    'time': timeper,
                    'personcount': personper,
                    'persamax': persamax
                }
            if(totimehour - fromtimehour > 1 and totimehour - fromtimehour <= 2):
                timea = data_event['time']
                persa = data_event['personcount']
                timeper = []
                personper = []
                i = 0
                while i !=len(timea)-1:
                    if fromtime <= timea[i] <= totime:
                        timeper.append(timea[i])
                        personper.append(persa[i])
                    i += 2
                persamax = max(personper)
                chartjson = {
                    'time': timeper,
                    'personcount': personper,
                    'persamax': persamax
                }
            if(totimehour - fromtimehour > 2 and totimehour - fromtimehour <= 8):
                timea = data_event['time']
                persa = data_event['personcount']
                timeper = []
                personper = []
                i = 0
                while i !=len(timea)-1:
                    if fromtime <= timea[i] <= totime:
                        timeper.append(timea[i])
                        personper.append(persa[i])
                    i += 4
                persamax = max(personper)
                chartjson = {
                    'time': timeper,
                    'personcount': personper,
                    'persamax': persamax
                }
            if(totimehour - fromtimehour > 8):
                timea = data_event['time']
                persa = data_event['personcount']
                timeper = []
                personper = []
                i = 0
                while i !=len(timea)-1:
                    if fromtime <= timea[i] <= totime:
                        timeper.append(timea[i])
                        personper.append(persa[i])
                    i += 12
                timeper.append(timea[len(timea)-1])
                personper.append(personper[len(personper)-1])
                persamax = max(personper)
                chartjson = {
                    'time': timeper,
                    'personcount': personper,
                    'persamax': persamax
                }

        return jsonify(chartjson)




# @app.route('/danger')
# def danger():
#     print('hi')
#     connection = MongoClient("localhost", 27017)
#     database = connection['testpymongo']
#     dbimage = database.imagepy
#     fs = gridfs.GridFS(database)
#     # image = dbimage.find({'classevent': 'weapon'})['imageevent'][0]
#     # get the image from gridfs
#     imgs = []
#     events = []
#     for x in dbimage.find():
#         ximg = x['imageevent']
#         print(ximg[0]['imageID'])
#         gOut = fs.get(ximg[0]['imageID'])
#         # convert bytes to ndarray
#         img = np.frombuffer(gOut.read(), dtype=np.uint8)
#         img = np.reshape(img, ximg[0]['shape'])
#         retval, buffer = cv2.imencode('.jpg', img)
#         encoded_img_data = base64.b64encode(buffer)
#         decoded_img_data = encoded_img_data.decode('utf-8')
#         imgs.append(decoded_img_data)
#         events.append(x['classevent'])
    
#     # convert bytes to ndarray
#     # img = np.frombuffer(gOut.read(), dtype=np.uint8)
#     # img = np.reshape(img, image['shape'])
#     # retval, buffer = cv2.imencode('.jpg', img)
#     # encoded_img_data = base64.b64encode(buffer)
#     # decoded_img_data = encoded_img_data.decode('utf-8')
#     return render_template('danger.html', imgs = imgs[len(imgs)-1], events = events[len(events)-1], n = len(imgs))

@app.route('/getalertpage')
def getalertpage():
    if(request.method=='GET'):
        return render_template('danger.html')


@app.route('/sendmail', methods=['GET', 'POST'])
def sendmail():
    if(request.method == 'POST'):
        body = f"""Please find the security alert"""
        email_from = "beprojectlens2@gmail.com"
        person = "beprojectlens1@gmail.com"
        pswd = os.getenv('APPPASSWORD')
        subject = "Security Alert"
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = person
        msg['Subject'] = subject
        # Attach the body of the message
        msg.attach(MIMEText(body, 'plain'))

        # Define the file to attach
        filename = "alert.pdf"

        # Open the file in python as a binary
        attachment= open(filename, 'rb')  # r for read and b for binary

        # Encode as base 64
        attachment_package = MIMEBase('application', 'octet-stream')
        attachment_package.set_payload((attachment).read())
        encoders.encode_base64(attachment_package)
        attachment_package.add_header('Content-Disposition', "attachment; filename= " + filename)
        msg.attach(attachment_package)

        # Cast as string
        text = msg.as_string()

        # Connect with the server
        print("Connecting to server...")
        TIE_server = smtplib.SMTP(smtp_server, smtp_port)
        TIE_server.starttls()
        TIE_server.login(email_from, pswd)
        print("Succesfully connected to server")
        print()


        # Send emails to "person" as list is iterated
        print(f"Sending emai to: {person}...")
        TIE_server.sendmail(email_from, person, text)
        print(f"Email sent to: {person}")
        print()

        # Close the port
        TIE_server.quit()

        print(f'ID is {request.form.get("report")}')
        return redirect("http://localhost:5000/previousevents")



@app.route('/suspicious', methods=['GET', 'POST'])
def suspicious():
    if(request.method == 'POST'):
        print(request.form.get('suspicious'))
        print(request.form.get('btnsuspicious'))
        myquery = { "_id": ObjectId(request.form.get('btnsuspicious')) }
        newvalues = { "$set": { "flagged_as":  request.form.get('suspicious')} }
        dbimage.update_one(myquery, newvalues)
        return redirect("http://127.0.0.1:5000/getalertpage?dataid="+request.form.get('btnsuspicious'))


@app.route('/danger')
def dangerper():
    if(request.method == 'GET'):
        print('hi')
        print(request.args.get('dataid'))
        # # image = dbimage.find({'classevent': 'weapon'})['imageevent'][0]
        # # get the image from gridfs
        # imgs = []
        # events = []
        # for x in dbimage.find():
        #     ximg = x['imageevent']
        #     print(ximg[0]['imageID'])
        #     gOut = fs.get(ximg[0]['imageID'])
        #     # convert bytes to ndarray
        #     img = np.frombuffer(gOut.read(), dtype=np.uint8)
        #     img = np.reshape(img, ximg[0]['shape'])
        #     retval, buffer = cv2.imencode('.jpg', img)
        #     encoded_img_data = base64.b64encode(buffer)
        #     decoded_img_data = encoded_img_data.decode('utf-8')
        #     imgs.append(decoded_img_data)
        #     events.append(x['classevent'])
        data_event = dbimage.find_one({'_id': ObjectId(request.args.get('dataid'))})
        ximg = data_event['imageevent'][0]
        print(data_event)
        gOut = fs.get(ximg['imageID'])
        img = np.frombuffer(gOut.read(), dtype=np.uint8)
        img = np.reshape(img, ximg['shape'])
        retval, buffer = cv2.imencode('.jpg', img)
        encoded_img_data = base64.b64encode(buffer)
        decoded_img_data = encoded_img_data.decode('utf-8')
        dataeventjson = {
            'decoded_img_data': decoded_img_data,
            'timestamp': data_event['timestamp'],
            'classevent': data_event['classevent'],
            'flagged_as': data_event['flagged_as'],
            'data_id': request.args.get('dataid')
        }
        # convert bytes to ndarray
        # img = np.frombuffer(gOut.read(), dtype=np.uint8)
        # img = np.reshape(img, image['shape'])
        # retval, buffer = cv2.imencode('.jpg', img)
        # encoded_img_data = base64.b64encode(buffer)
        # decoded_img_data = encoded_img_data.decode('utf-8')
        return jsonify(dataeventjson)

@app.route('/previousevents')
def previousevents():
    if(request.method == 'GET'):
        return render_template('allevents.html')


@app.route('/allevents')
def allevents():
    print('hi')
    connection = MongoClient("localhost", 27017)
    database = connection['testpymongo']
    dbimage = database.imagepy
    fs = gridfs.GridFS(database)
    # image = dbimage.find({'classevent': 'weapon'})['imageevent'][0]
    # get the image from gridfs
    imgs = []
    events = []
    timestamps = []
    ids = []
    if(not request.args):
        for x in dbimage.find().sort("timestamp", -1):
            ximg = x['imageevent']
            print(ximg[0]['imageID'])
            gOut = fs.get(ximg[0]['imageID'])
            # convert bytes to ndarray
            img = np.frombuffer(gOut.read(), dtype=np.uint8)
            img = np.reshape(img, ximg[0]['shape'])
            retval, buffer = cv2.imencode('.jpg', img)
            encoded_img_data = base64.b64encode(buffer)
            decoded_img_data = encoded_img_data.decode('utf-8')
            imgs.append(decoded_img_data)
            events.append(x['classevent'])
            timestamps.append(x['timestamp'])
            ids.append(str(x['_id']))

        print(ids)
        alldataeventjson = {
                'decoded_img_data_all': imgs,
                'timestamp': timestamps,
                'classevent': events,
                'ids': ids
         }

        return jsonify(alldataeventjson)

        
    if(request.args.get('class')):
        print(request.args.get('class'))
        for x in dbimage.find({'classevent': {"$in": [request.args.get('class')]}}).sort("timestamp", -1):
            print(x)
            ximg = x['imageevent']
            print(ximg[0]['imageID'])
            gOut = fs.get(ximg[0]['imageID'])
            # convert bytes to ndarray
            img = np.frombuffer(gOut.read(), dtype=np.uint8)
            img = np.reshape(img, ximg[0]['shape'])
            retval, buffer = cv2.imencode('.jpg', img)
            encoded_img_data = base64.b64encode(buffer)
            decoded_img_data = encoded_img_data.decode('utf-8')
            imgs.append(decoded_img_data)
            events.append(x['classevent'])
            timestamps.append(x['timestamp'])
            ids.append(str(x['_id']))


        print(ids)
        alldataeventjson = {
                'decoded_img_data_all': imgs,
                'timestamp': timestamps,
                'classevent': events,
                'ids': ids
         }

        return jsonify(alldataeventjson)
    elif(request.args.get('fromtime')):
        fromtime = request.args.get('fromtime').split('T')
        totime = request.args.get('totime').split('T')
        for x in dbimage.find().sort("timestamp", -1):
            ximg = x['imageevent']
            gOut = fs.get(ximg[0]['imageID'])
            # convert bytes to ndarray
            img = np.frombuffer(gOut.read(), dtype=np.uint8)
            img = np.reshape(img, ximg[0]['shape'])
            retval, buffer = cv2.imencode('.jpg', img)
            encoded_img_data = base64.b64encode(buffer)
            decoded_img_data = encoded_img_data.decode('utf-8')

            tstr = str(x['timestamp'])[0:16]
            tstra = tstr.split(' ')

            if (fromtime[0] <= tstra[0] <= totime[0]) and (fromtime[1] <= tstra[1] <= totime[1]):
                print(tstra)
                imgs.append(decoded_img_data)
                events.append(x['classevent'])
                timestamps.append(x['timestamp'])
                ids.append(str(x['_id']))

        alldataeventjson = {
                 'decoded_img_data_all': imgs,
                 'timestamp': timestamps,
                 'classevent': events,
                 'ids': ids
          }
 
        return jsonify(alldataeventjson)


    # convert bytes to ndarray
    # img = np.frombuffer(gOut.read(), dtype=np.uint8)
    # img = np.reshape(img, image['shape'])
    # retval, buffer = cv2.imencode('.jpg', img)
    # encoded_img_data = base64.b64encode(buffer)
    # decoded_img_data = encoded_img_data.decode('utf-8')
    # return render_template('allevents.html', imgs = imgs, events = events, n = len(imgs))



if __name__=='__main__':
    app.run(debug=True)