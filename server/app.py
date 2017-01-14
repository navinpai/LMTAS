from flask import Flask, request
from werkzeug.utils import secure_filename
import os
import json

import constants

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'


@app.route('/')
def hello_world():
    return 'Team FifthEye!'

@app.route('/upload', methods=['POST'])
def upload():
    imgData = request.form['file']
    if imgData:
        filename = secure_filename("pic.jpg")
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "wb") as fh:
            fh.write(imgData.decode('base64'))
        return 'Image Saved'

    return 'Dafuq? No Image Data Sent!'


@app.route('/getDetails')
def getDetails():
    dummy_response = {"lastTransactions":["Shubham owes you Rs. 100", "Vishesh owes you Rs. 350", "You owe Archana 300", "You owe Vishesh Rs. 150"], "balances": [{"Archana": "+4300"}, {"Vishesh": "-2300"}, {"Shubham": "+4750" }]}
    return json.dumps(dummy_response)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1337)