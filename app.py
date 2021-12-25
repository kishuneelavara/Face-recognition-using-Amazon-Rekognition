import os
import io
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template,jsonify
from werkzeug.utils import secure_filename
from utils.Create_Collection import list_collections,create,delete
from utils.Register_Faces import add_face_to_collection
from utils.Face_recognize import face_recognition_saving_image
from PIL import Image


UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


@app.route('/')
def start_page():
    return render_template('index.html')

@app.route('/collection_page')
def collection_page():
    count,lst=list_collections()
    return render_template('collection.html', count=count, lst=lst)


@app.route('/create_page', methods=['POST'])
def create_page():
    COLLECTION_NAME = str(request.form['collection-name'])
    COLLECTION_NAME=COLLECTION_NAME.strip()
    print(COLLECTION_NAME)
    statement=create(COLLECTION_NAME)
    print(statement)
    count,lst=list_collections()
    return render_template('collection.html', count=count, lst=lst, statement=statement)


@app.route('/delete_page')
def delete_page():
    COLLECTION_NAME=request.args.get('name')
    statement=delete(COLLECTION_NAME)
    count,lst=list_collections()
    return render_template('collection.html', count=count, lst=lst, statement=statement)


@app.route('/register_page')
def register_page():
    count,lst=list_collections()
    return render_template('register.html', lst=lst)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register_faces', methods=['POST'])
def register_faces():
    if 'file' not in request.files:
        statement='No file part'
        count, lst = list_collections()
        return render_template('register.html', lst=lst,statement=statement)
    file = request.files['file']
    if file.filename == '':
        statement='No image selected for uploading'
        count, lst = list_collections()
        return render_template('register.html', lst=lst, statement=statement)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        Register_image = Image.open('static/uploads/' + filename)
        print(Register_image)
        bytes_array = io.BytesIO()
        Register_image.save(bytes_array, format="PNG")
        source_image_bytes = bytes_array.getvalue()
        name = str(request.form['person-name'])
        name = name.strip()
        COLLECTION_NAME=request.form['collection']
        print(name)
        print(COLLECTION_NAME)
        ount, lst = list_collections()
        registration_result = add_face_to_collection(source_image_bytes, name, COLLECTION_NAME)
        #print('upload_image filename: ' + filename)
        # flash('Image successfully uploaded and displayed below')
        return render_template('register.html', lst=lst, reg_lst=registration_result, filename=filename)
    else:
        statement='Allowed image types are -> png, jpg, jpeg, gif'
        count, lst = list_collections()
        return render_template('register.html', lst=lst, statement=statement)

@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/display/<filename>')
def display_image_recognition(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='result/' + filename), code=301)

@app.route('/recognize_page')
def recognize_page():
    count,lst=list_collections()
    return render_template('recognize.html', lst=lst)

@app.route('/recognize_faces', methods=['POST'])
def recognize_faces():
    if 'file' not in request.files:
        statement='No file part'
        count, lst = list_collections()
        return render_template('recognize.html', lst=lst,statement=statement)
    file = request.files['file']
    if file.filename == '':
        statement='No image selected for uploading'
        count, lst = list_collections()
        return render_template('recognize.html', lst=lst, statement=statement)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        Register_image = Image.open('static/uploads/' + filename)
        print(Register_image)

        COLLECTION_NAME=request.form['collection']
        print(COLLECTION_NAME)
        count, lst = list_collections()

        path="result/"+filename
        result_img,res_lst = face_recognition_saving_image(Register_image, COLLECTION_NAME)
        result_img.save('static/'+path)

        #print('upload_image filename: ' + filename)
        # flash('Image successfully uploaded and displayed below')
        return render_template('recognize.html', lst=lst, filename=path,res_lst=res_lst)
    else:
        statement='Allowed image types are -> png, jpg, jpeg, gif'
        count, lst = list_collections()
        return render_template('recognize.html', lst=lst, statement=statement)

@app.after_request
def add_header(response):
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    app.run(port=5002)