import cv2
from flask import Flask, render_template,request,redirect, url_for, send_from_directory,session
from process_img import gen_ans
from werkzeug import secure_filename
import pandas as pd
import csv
import os
from flask_session import Session
USERNAME ="admin"
PASSWORD ="admin"
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = os.getenv("SECRET", "not a secret")
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])
@app.route('/', methods=['GET', 'POST'])
def get_signin():
    if request.method == 'POST':
        session['username'] = request.form['fname']
        session['password'] = request.form['fpass']
    else:
        return render_template('signin.html')
    if session['username'] == USERNAME and session['password'] == PASSWORD:
        return redirect('/main')
    else:
        return redirect('/main')
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template("main.html")
@app.route('/bridge',methods=['GET','POST'])
def bridge():
    if request.method=="POST":
        # print(request.form['check'])
        if request.form['check']=="start":
            return redirect('/chamthi')
        elif request.form['check']=="res":
            return redirect('/dashboard')
        else:
            return redirect('/main')
    else:
        return redirect('/')
@app.route('/chamthi',methods=['GET', 'POST'])
def index():
    return render_template('point.html')

    # else:
    #     return redirect('/')
@app.route('/dashboard',methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html',lres=get_list())
def get_list():
    session['db'] = []
    with open ('./db/result.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        for row in csv_reader:
            session['db'].append(row)
    return session['db']
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file',
                                filename=filename))
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    PATH_TO_TEST_IMAGES_DIR = app.config['UPLOAD_FOLDER']
    # df = pd.read_csv("ketqua.csv")
    TEST_IMAGE_PATHS = [os.path.join(PATH_TO_TEST_IMAGES_DIR,filename.format(i)) for i in range(1, 2)]
    session['point'] = []
    for image_path in TEST_IMAGE_PATHS:
        score,res = gen_ans("dapan.csv",image_path)
        dfp = pd.DataFrame(res)
        dfp.to_csv('{}.csv'.format(image_path))
        session['point'].append([image_path+'.csv',score])
    with open('./db/result.csv', 'a') as f_object:
        writer_object = csv.writer(f_object)
        writer_object.writerow(session['point'])
        f_object.close()  
    session['point']=[]  
    return redirect('/chamthi')
app.run(host = '0.0.0.0',port = 5000)
