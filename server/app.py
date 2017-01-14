from flask import Flask, request
from werkzeug.utils import secure_filename
import os
import pymysql.cursors
import json
import cognitive_face as CF
from PIL import Image
import constants
import kairos_face

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

def identify_people(img_title):
    # TODO
    return ["navin", "archana", "vishesh"]

def kairos_identify(img_file):
    kairos_face.settings.app_id = constants.KAIROS_APPID
    kairos_face.settings.app_key = constants.KAIROS_APPKEY
    #with open(img_file, 'rb') as image_file:
    recognized_faces = kairos_face.recognize_face('actors', file=img_file)

    return recognized_faces
    # Printing the recognized face candidates info
    for face_candidate in recognized_faces:
        print('{}: {}'.format(face_candidate.subject, face_candidate.confidence))

def recognize_faces(img_file, faceCoords):
    imgMain = Image.open(img_file)
    for face in faceCoords:
        faceRect = face['faceRectangle']
        cropped = imgMain.crop((faceRect['left'] - 10, faceRect['top'] - 10, faceRect['left'] + faceRect['width'] + 10, faceRect['top']+faceRect['height'] + 10))
        tempImg = os.path.join(app.config['UPLOAD_FOLDER'], "tempFace.jpg")
        cropped.save(tempImg)

        result = kairos_identify(tempImg)

        import pdb;pdb.set_trace()
    return ["navin", "archana", "vishesh"]

@app.route('/')
def hello_world():
    return 'Team FifthEye!'

@app.route('/upload', methods=['POST'])
def upload():
    imgData = request.form['file']
    img_title = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)) + '.jpg'
    if imgData:
        filename = secure_filename(img_title)
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "wb") as fh:
            fh.write(imgData.decode('base64'))
        return 'Image Saved'
        
        KEY = constants.MS_OXFORD_KEY
        CF.Key.set(KEY) 
        img_file = os.path.join(app.config['UPLOAD_FOLDER'], img_title)
        result = CF.face.detect(img_file)
        identified_people = recognize_faces(img_file, result)
        connection = pymysql.connect(host='localhost', \
                             user=constants.MYSQL_USERNAME, \
                             password=constants.MYSQL_PASSWORD, \
                             db='gohack', \
                             charset='utf8mb4', \
                             cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
            # Read a single record
                sql = "SELECT `id`FROM `txns`" # WHERE `email`=%s"
                cursor.execute(sql) #, ('webmaster@python.org',))
                result = cursor.fetchone()
                return json.dumps(result)
        finally:
            connection.close()
            return "error"

    return 'Dafuq? No Image Data Sent!'

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