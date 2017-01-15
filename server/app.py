from werkzeug.utils import secure_filename
from flask import Flask, request, render_template
import cognitive_face as CF
import pymysql.cursors
from PIL import Image
import requests
import string
import random
import json
import os
import pyfcm
from pyfcm import FCMNotification
import kairos_face
import constants

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

def get_db_connection():
    return pymysql.connect(host='localhost', \
                         user=constants.MYSQL_USERNAME, \
                         password=constants.MYSQL_PASSWORD, \
                         db='gohack', \
                         charset='utf8mb4', \
                         cursorclass=pymysql.cursors.DictCursor)

def kairos_identify(img_file):
    kairos_face.settings.app_id = constants.KAIROS_APPID
    kairos_face.settings.app_key = constants.KAIROS_APPKEY
    recognized_faces = kairos_face.recognize_face('actors', file=img_file)

    return recognized_faces

def make_db_entries(identified_people, userName, amount, img_link):
    individual_share = amount * 1.0 / len(identified_people)
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            for person in identified_people:
                if person != userName:
                    sql = "INSERT  into `txns` (`payer`, `payee`, `img`, `amount`) values (%s, %s, %s, %s)"
                    cursor.execute(sql, (userName, person, img_link, str(individual_share)))
        connection.commit()
    finally:
        connection.close()

def firebase_notify(identified_users, user):
    push_service = FCMNotification(api_key=constants.FIREBASE_API_KEY)
    message_title = "Update: " + user + " has added a new bill with you!"
    message_body = "Update: " + user + " has added a new bill with you!"
    #for user in identified_users:
    result = push_service.notify_topic_subscribers(topic_name="updates", message_title=message_title,  message_body=message_body)

def recognize_faces(img_file, faceCoords):
    imgMain = Image.open(img_file)
    identified_faces = set()
    for face in faceCoords:
        faceRect = face['faceRectangle']
        cropped = imgMain.crop((faceRect['left'] - 10, faceRect['top'] - 10, faceRect['left'] + faceRect['width'] + 10, faceRect['top'] + faceRect['height'] + 10))
        tempImg = os.path.join(app.config['UPLOAD_FOLDER'], 'tempFace.jpg')
        cropped.save(tempImg)
        fallback = False
        try:
            result = kairos_identify(tempImg)
        except:
            fallback = True
            result = kairos_identify(img_file)
        if len(result) > 0:
            identified_faces.add(result[0].subject)

    return list(identified_faces), len(faceCoords), fallback

def getUserTxnDetails(user):
    connection = get_db_connection()
    result = []
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * from `txns` where `payee`= %s or `payer`=%s order by id DESC'
            cursor.execute(sql, (user,user))
            result = cursor.fetchall();
    finally:
        connection.close()
 
    txnStrings = []
    balances = {}
    total = 0.0
    for txn in result:
        if(txn["payer"] == user):
            total = total + txn['amount']
            if(txn['payee'] in balances):
                balances[txn['payee']] = balances[txn['payee']] + txn['amount']
            else:
                balances[txn['payee']] = txn['amount']
            txnPT = "You lent Rs." + str(txn["amount"]) +" to "+ txn["payee"].title()
        else:
            total = total - txn['amount']
            if(txn['payer'] in balances):
                balances[txn['payer']] = balances[txn['payer']] - txn['amount']
            else:
                balances[txn['payer']] = txn['amount']
            txnPT = txn["payer"].title() + " lent you Rs." + str(txn["amount"])
        txnImg = txn["img"]
        txnStrings.append({'txnPT': txnPT, 'txnImg': txnImg})
    return (balances, txnStrings, total)

@app.route('/home')
def home():
    (balances, txns, total) = getUserTxnDetails("archana")
    return render_template('index.html', balances=balances, txns=txns, total=total) 

@app.route('/add')
def add():
    return render_template('add_new.html') 

@app.route('/enroll')
def enroll():
    return render_template('enroll.html') 

@app.route('/addToKairos', methods=['POST'])
def addToKairos():
    (balances, txns, total) = getUserTxnDetails("archana")
    return render_template('index.html', balances=balances, txns=txns, total=total) 


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
        (identified_people, num_of_faces, fallback) = recognize_faces(img_file, result)

        if num_of_faces < 1:
            message = 'Could not make out any faces! Try with better light or crisper photos'
        else:
            success = True
            if(len(identified_people) == num_of_faces):
                message = 'Success! Get Back to the party!'
                make_db_entries(identified_people, user, float(amount), img_title)
            else:
                if(user not in identified_people):
                    make_db_entries(identified_people + [user], user, float(amount), img_title)
                    message = 'Was some work, but got it done!'
                else:
                    message = 'Couldn\'t recognize all faces . Manual intervention required! :('
    else:
        message = 'Dafuq? No Image Data Sent!'
    return json.dumps({"success": success, "message": message})

@app.route('/addNew', methods=['POST'])
def addNew():
    img=request.files['file']
    user = request.form['person']
    img_title = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)) + '.jpg'
    if img:
        filename = secure_filename(img_title)
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        KEY = constants.MS_OXFORD_KEY
        CF.Key.set(KEY) 
        img_file = os.path.join(app.config['UPLOAD_FOLDER'], img_title)
        result = CF.face.detect(img_file)
        (identified_people, num_of_faces, fallback) = recognize_faces(img_file, result)

        if num_of_faces < 1:
            message = 'Could not make out any faces! Try with better light or crisper photos'
        else:
            success = True
            if(len(identified_people) == num_of_faces):
                message = 'Success! Get Back to the party!'
                firebase_notify(identified_users, user)
                make_db_entries(identified_people, user, float(amount), img_title)
            else:
                if(user not in identified_people):
                    firebase_notify(identified_users)
                    make_db_entries(identified_people + [user], user, float(amount), img_title)
                    message = 'Was some work, but got it done!'
                else:
                    message = 'Couldn\'t recognize all faces . Manual intervention required! :('
    else:
        message = 'Dafuq? No Image Data Sent!'
    return json.dumps({"success": success, "message": message})
    
@app.route('/enrollNew', methods=['POST'])
def enrollNew():
    img=request.files['file']
    img_title = "ENR" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)) + '.jpg'
    if img:
        filename = secure_filename(img_title)
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
    kairos_face.settings.app_id = constants.KAIROS_APPID
    kairos_face.settings.app_key = constants.KAIROS_APPKEY
    subject_id, success = kairos_face.enroll_face(request.form['person'], 'actors', file=os.path.join(app.config['UPLOAD_FOLDER'], filename))
    if success:
        return "Successfully enrolled " + subject_id
    else:
        return "Failed to enroll. Try a different photo?"

@app.route("/test")
def getMys():
    '''
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
    (balances, txns, total) = getUserTxnDetails("navin")
    response = {"lastTransactions": txns, "balances": balances, "total": total} 
    return json.dumps(response)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1337)