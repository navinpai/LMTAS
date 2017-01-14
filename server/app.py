from flask import Flask, request
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'


@app.route('/')
def hello_world():
    return 'Team FifthEye!'

@app.route('/upload', methods=['POST'])
def upload():
    import pdb;pdb.set_trace()
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'Image Saved'

    return 'Dafuq? No File!'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1337)