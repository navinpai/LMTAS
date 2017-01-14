from werkzeug.utils import secure_filename
from flask import Flask, request
import cognitive_face as CF
import pymysql.cursors
from PIL import Image
import string
import random
import json
import os

import kairos_face
import constants

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

def kairos_identify(img_file):
    kairos_face.settings.app_id = constants.KAIROS_APPID
    kairos_face.settings.app_key = constants.KAIROS_APPKEY
    recognized_faces = kairos_face.recognize_face('actors', file=img_file)

    return recognized_faces

def make_db_entries(identified_people, userName, amount, img_link):
    individual_share = amount / len(identified_people)
    connection = pymysql.connect(host='localhost', \
                         user=constants.MYSQL_USERNAME, \
                         password=constants.MYSQL_PASSWORD, \
                         db='gohack', \
                         charset='utf8mb4', \
                         cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            for person in identified_people:
                if person != userName:
                    sql = "INSERT  into `txns` (payer, payee, img, amount) values(%s,%s,%s,%f)" # WHERE `email`=%s"
            cursor.execute(sql, (userName, person, "AAAAAA", individual_share))
            result = cursor.fetchone()
            return json.dumps(result)
    finally:
        connection.close()


def recognize_faces(img_file, faceCoords):
    imgMain = Image.open(img_file)
    identified_faces = set()
    for face in faceCoords:
        faceRect = face['faceRectangle']
        cropped = imgMain.crop((faceRect['left'] - 10, faceRect['top'] - 10, faceRect['left'] + faceRect['width'] + 10, faceRect['top']+faceRect['height'] + 10))
        tempImg = os.path.join(app.config['UPLOAD_FOLDER'], "tempFace.jpg")
        cropped.save(tempImg)

        result = kairos_identify(tempImg)
        if len(result) > 0:
            identified_faces.add(result[0].subject)

    return list(identified_faces), len(faceCoords)

@app.route('/')
def hello_world():
    return 'Team FifthEye!'

@app.route('/upload', methods=['POST'])
def upload():
    success = False
    imgData = request.form['file']
    amount = request.form['amount']
    user = request.form['userName']
    img_title = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)) + '.jpg'
    if imgData:
        filename = secure_filename(img_title)
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as fh:
            fh.write(imgData.decode('base64'))
        
        KEY = constants.MS_OXFORD_KEY
        CF.Key.set(KEY) 
        img_file = os.path.join(app.config['UPLOAD_FOLDER'], img_title)
        result = CF.face.detect(img_file)
        (identified_people, num_of_faces) = recognize_faces(img_file, result)

        if num_of_faces < 1:
            message = 'Could not make out any faces! Try with better light or crisper photos'
        else:
            success = True
            if(len(identified_people) == num_of_faces):
                message = 'Success! Get Back to the party!'
                make_db_entries(identified_people, user, float(amount), img_title)
            else:
                message = 'Couldn\'t recognize all faces . Manual intervention required! :('
    else:
        message = 'Dafuq? No Image Data Sent!'
    return {"success": success, "message": message}

@app.route("/test")
def getMys():
    '''
    import pdb;pdb.set_trace()
    connection = pymysql.connect(host='localhost', \
                         user=constants.MYSQL_USERNAME, \
                         password=constants.MYSQL_PASSWORD, \
                         db='gohack', \
                         charset='utf8mb4', \
                         cursorclass=pymysql.cursors.DictCursor)
    #try:
    with connection.cursor() as cursor:
    # Read a single record
        sql = "SELECT `id`FROM `txns`" # WHERE `email`=%s"
        cursor.execute(sql) #, ('webmaster@python.org',))
        result = cursor.fetchone()
        return json.dumps(result)
    #finally:
        connection.close()
       return "Some error"
    '''
    KEY = constants.MS_OXFORD_KEY
    CF.Key.set(KEY) 
    img_file = os.path.join(app.config['UPLOAD_FOLDER'], 'AAAAAA.jpg')
    result = CF.face.detect(img_file)
    faces_detected = len(result)
    recognize_faces(img_file, result)
    return json.dumps(result)


@app.route('/getDetails')
def getDetails():
    dummy_response = {"lastTransactions":["Shubham owes you Rs. 100", "Vishesh owes you Rs. 350", "You owe Archana 300", "You owe Vishesh Rs. 150"], "balances": [{"Archana": "+4300"}, {"Vishesh": "-2300"}, {"Shubham": "+4750" }]}
    return json.dumps(dummy_response)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1337)