
#General server function includes
from base64 import encodebytes, b64encode, b64decode
from flask import Flask, flash, request, redirect, url_for, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from PIL import Image

import os
import tensorflow as tf
from cv2 import cv2, data
import json
import gc
import numpy as np
import requests
import io
import pymongo
import binascii
import re

#MongoDB includes
from pymongo import MongoClient

#Kien's server includes
import FacebookApp
import InstagramApp
import requests

#Kien's server vars
instagram = InstagramApp.InstaApp()
facebook = FacebookApp.FacebookApp()

album_urls_dict = {}
img_urls_dict = {}
short_lived_token = ""
long_lived_token = ""

#server setup and functions
ON_HEROKU = os.environ.get('ON_HEROKU')

if ON_HEROKU:
    # get the heroku port
    port = int(os.environ.get('PORT', 17995))  # as per OP comments default is 17995
else:
    port = 5000

app = Flask(__name__, template_folder='template')

#app.config['UPLOAD_FOLDER'] = os.path.join('static', 'people_folder')
#instagram = InstaAppTestUserModule.InstaApp()
#facebook = FacebookApp.FacebookApp()

UPLOAD_FOLDER = 'upload_folder'
PROCESSING_FOLDER = 'processing_folder'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'bmp'])

app.secret_key = 'ah5XAw.|$ZlPviFeFUeM'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSING_FOLDER'] = PROCESSING_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

#mongo client connection & database structure
client = pymongo.MongoClient("mongodb+srv://bwhite19:kVSgkPTVe4Gjthmm@dpsprojectdatabase.ncb54.mongodb.net/DPSData?retryWrites=true&w=majority")
db = client.DPSData
#images
img_data_col = db['images_data']
img_pre_col = db['images_pre']
img_post_col = db['images_post']
#users
usr_col = db['users']

def allowed_file(filename):
     return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def prepare (filepath):
    IMG_SIZE = 128
    img_array = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
    return new_array.reshape(-1, IMG_SIZE, IMG_SIZE, 1)
    
#save an image with processing
def save_img(name, dt_string, hash, faces, faceList, faceArr, user):
    #create separate image buffers for base64 encode
    pre_img_buffer = io.BytesIO()
    post_img_buffer = io.BytesIO()
    #open images in processing folder (will be deleted after this process)
    pre_img = open_pil_image(name)
    post_img = open_pil_image(name + '_POST')
    #save PIL image as PNG, encode as base64 via buffer, decode as ASCII so mongo parses as string
    pre_img.save(pre_img_buffer, format="PNG")
    pre_img_enc = b64encode(pre_img_buffer.getvalue())
    pre_img_b64 = pre_img_enc.decode('ascii')
    #repeat above process for postprocessing image
    post_img.save(post_img_buffer, format="PNG")
    post_img_enc = b64encode(post_img_buffer.getvalue())
    post_img_b64 = post_img_enc.decode('ascii')
    #insert to db
    #res = db.images.insert_one({"name":name,"timestamp":dt_string,"hash":hash,"preprocessing":pre_img_b64,"postprocessing":post_img_b64, "faces":faces})
    _id = db.images_data.insert_one({"name":name,"timestamp":dt_string,"hash":hash,"faces":faces, "faceList":faceList, "faceArr":faceArr, "user":user})
    res2 = db.images_pre.insert_one({"img_data_id":_id.inserted_id, "image_pre":pre_img_b64})
    res3 = db.images_post.insert_one({"img_data_id":_id.inserted_id, "image_post":post_img_b64})
    
    return res3

#save an image without processing (no faces param since image is not processed)
def save_img_single(name, dt_string, hash, user):

    #create separate image buffers for base64 encode
    pre_img_buffer = io.BytesIO()
    #open images in processing folder (will be deleted after this process)
    pre_img = open_pil_image(name)
    #save PIL image as PNG, encode as base64 via buffer, decode as ASCII so mongo parses as string
    pre_img.save(pre_img_buffer, format="PNG")
    pre_img_enc = b64encode(pre_img_buffer.getvalue())
    pre_img_b64 = pre_img_enc.decode('ascii')
    #repeat above process for postprocessing image
    #insert to db
    #res = db.images.insert_one({"name":name,"timestamp":dt_string,"hash":hash,"preprocessing":pre_img_b64,"postprocessing":post_img_b64, "faces":faces})
    _id = db.images_data.insert_one({"user":user,"name":name,"timestamp":dt_string,"hash":hash,"faces":0, "faceArr":None, "user":user})
    res2 = db.images_pre.insert_one({"img_data_id":_id.inserted_id, "image_pre":pre_img_b64})
    
    return res2
    
def save_img_single_post(name, hash, faces):
    db.images_data.find_one_and_update({"hash": hash}, {'$set': {"faces":faces}})
    _id = db.images_data.find_one({"hash":hash})

    #create separate image buffers for base64 encode
    post_img_buffer = io.BytesIO()
    
    #open images in processing folder (will be deleted after this process)
    if faces > 0:#this condition solves a bug where db inserts fail when an image has zero faces
        post_img = open_pil_image(name + '_POST')
    else:
        post_img = open_pil_image(name)
        
    #save PIL image as PNG, encode as base64 via buffer, decode as ASCII so mongo parses as string
    post_img.save(post_img_buffer, format="PNG")
    post_img_enc = b64encode(post_img_buffer.getvalue())
    post_img_b64 = post_img_enc.decode('ascii')
    #insert to db
    res3 = db.images_post.insert_one({"img_data_id":_id['_id'], "image_post":post_img_b64})
    
    return res3
    
def decode_img(img, name):
    img_ascii = img.encode('ascii')
    
    img_bytes = b64decode(img_ascii)
    img_file = io.BytesIO(img_bytes)
    img_pil = Image.open(img_file)
    img_pil.save((os.path.join(app.config['PROCESSING_FOLDER'], name)))
    
    return name

def load_img_hash(hash):
    #find an image based on unique key (hash)
    res = img_data_col.find_one({"hash":hash})
    
    if res is not None:
        return res
    else:
        return None
    
def load_img_name(name):
    #find an image based on unique key (name)
    res = img_data_col.find_one({"name":name})
    if res is not None:
        img_post = img_post_col.find_one({"img_data_id":res['_id']})
        
        if img_post is None:#we have an image that must be on-demand processed
            img_pre = img_pre_col.find_one({"img_data_id":res['_id']})
            img = img_pre['image_pre']
            img_dec = decode_img(img, res['name'])
            
            res2 = facial_detection_single(name, res['timestamp'], res['hash'], open_pil_image(name))
            
            return img_post_col.find_one({"img_data_id":res['_id']})
        else:
            return img_post
    else:
        return None
        
def load_img_face(face_name):
    #retrieve all images that have a certain name in the faceArr
    list = []
    
    print(face_name)
    
    res = img_data_col.find({"faceList": {"$all": face_name }})
    
    if res is not None:
        for r in res:
            x = img_post_col.find_one({"img_data_id":r['_id']})
            if x['_id'] is not None:
                list.append(x)
                
        return list
    else:
        return None
        
def load_img_user_name(user):
    #retrieve all images that have a certain name in the faceArr
    list = []
    
    print(user)
    
    res = img_data_col.find({"user": user})
    
    if res is not None:
        for r in res:
            x = img_post_col.find_one({"img_data_id":r['_id']})
            if x['_id'] is not None:
                list.append(x)
                
        return list
    else:
        return None
    
def hash_img(img):
    #resize the image to 16x16 for average hashing
    resize_img = img.resize((16,16), Image.ANTIALIAS)
    #convert to grayscale
    color_img = resize_img.convert("L")
    img_pixel_data = list(color_img.getdata())
    #calculate average pixel data
    avg_pixel = sum(img_pixel_data)/len(img_pixel_data)
    #now hash the data
    bits = "".join(['1' if (px >= avg_pixel) else '0' for px in img_pixel_data])
    hex_rep = str(hex(int(bits, 2)))[2:][::-1].upper()
    #return the hash
    return hex_rep
    
def assign_img_user(userID, hash):
    #find an image based on unique key (hash)
    res = img_data_col.find_one({'hash':hash})
    if res is not None:
        return img_data_col.update_one({'_id':res['_id']},{"$set":{'user':userID}},upsert=False)
    else:
        return None
        
def update_face_list_data(hash, face_arr, face_list):
    #update the faceArr and faceList parameters based on hash
    res = img_data_col.find_one({'hash':hash})
    if res is not None:
        return img_data_col.update_one({'_id':res['_id']},{"$set":{'faceArr':face_arr, 'faceList':face_list}},upsert=False)
    else:
        return None
        
def open_pil_image(filename):
    pil_img = Image.open((os.path.join(app.config['PROCESSING_FOLDER'], filename)), mode='r')
    return pil_img
    
def remove_local_images(filename):
    #check if image exists, if so remove from processing folder
    if os.path.exists(os.path.join(app.config['PROCESSING_FOLDER'], filename)):
        os.remove(os.path.join(app.config['PROCESSING_FOLDER'], filename))
    
    if os.path.exists(os.path.join(app.config['PROCESSING_FOLDER'], filename + '_POST')):
        os.remove(os.path.join(app.config['PROCESSING_FOLDER'], filename + '_POST'))
 
#image processing for pre+postprocessing images
def process_image(name, dt_string, hash, img):
    #query database for an entry with a matching hash
    query_res = load_img_hash(hash)
    if query_res is None: #if an entry with a matching hash was not found
        #print("doing unique case")
        #pass the image to the facial detection function
        response = facial_detection(name, dt_string, hash, img) #perform processing since this is a new image
    else: #if an entry with a matching hash was found
        #print("doing duplicate case")
        #parse query res since we have the image data (avoid processing)
        response = {"imgurl":query_res['name'], "timestamp":query_res['timestamp'],"faces":query_res['faces']}
        response = jsonify(response)
        
    #remove local images before returning response
    remove_local_images(name)
    return response
    
#image processing for only preprocessing images
def save_without_process_image(name, dt_string, hash, img):
    #query database for an entry with a matching hash
    query_res = load_img_hash(hash)
    if query_res is None: #if an entry with a matching hash was not found
        #print("doing unique case")
        #pass the image to the upload function
        save_img_single(name, dt_string, hash, 0)
        response = {"img":name, "timestamp":dt_string}
    else: #if an entry with a matching hash was found
        #parse query_res since this image already exists
        response = {"imgurl":query_res['name'], "timestamp":query_res['timestamp']}
        response = jsonify(response)
        
    #remove local images before returning response
    remove_local_images(name)
    return response
 
def facial_detection(name, dt_string, hash, pre_img):
    scale = 1.03
    neighbors = 16
    face_cascade = cv2.CascadeClassifier(data.haarcascades + 'haarcascade_frontalface_alt2.xml')
    
    #convert PIL to cv2
    post_img = cv2.cvtColor(np.array(pre_img), cv2.COLOR_RGB2BGR)

    faceArr = []
    faceList = []

    print("trying processing")
    try:
    
       faces = face_cascade.detectMultiScale(post_img, scaleFactor=scale, minNeighbors=neighbors)
       if (len(faces) > 0):
            for (x, y, width, height) in faces:
                cv2.rectangle(post_img, (x, y), (x + width, y + height), (0, 255, 0), 2)
                #append to faceArr
                faceList.append("null")
                faceArr.append([int(x),int(y),int(x+width),int(y+height)])
            #save to processing folder for later (base64 encode)    
            cv2.imwrite(os.path.join(app.config['PROCESSING_FOLDER'], name + '_POST'), post_img)
            
    except Exception as e:
        return(f'{__name__} Has exception: {e}', 0)

    #now that we have a processed image, save it to the db
    
    #name, timestamp, hash, face count, face array, user
    save_img(name, dt_string, hash, len(faces), faceList, faceArr, 0)

    #parse as json and return
    json_arr = {"img":name, "timestamp":dt_string, "faces":len(faces), "faceList":faceList, "faceArr":faceArr, "user":0}

    return jsonify(json_arr)
    
def facial_detection_single(name, dt_string, hash, pre_img):
    scale = 1.03
    neighbors = 16
    face_cascade = cv2.CascadeClassifier(data.haarcascades + 'haarcascade_frontalface_alt2.xml')
    
    #convert PIL to cv2
    post_img = cv2.cvtColor(np.array(pre_img), cv2.COLOR_RGB2BGR)

    print("trying processing")
    try:
    
       faces = face_cascade.detectMultiScale(post_img, scaleFactor=scale, minNeighbors=neighbors)
       if (len(faces) > 0):
            for (x, y, width, height) in faces:
                cv2.rectangle(post_img, (x, y), (x + width, y + height), (0, 255, 0), 2)
            #save to processing folder for later (base64 encode)    
            cv2.imwrite(os.path.join(app.config['PROCESSING_FOLDER'], name + '_POST'), post_img)
            
    except Exception as e:
        return(f'{__name__} Has exception: {e}', 0)

    #now that we have a processed image, save it to the db
    save_img_single_post(name, hash, len(faces))

    #parse as json and return
    json_arr = {"img":name, "timestamp":dt_string, "faces":len(faces)}

    return jsonify(json_arr)
    
#removed encode_image function since it is no longer necessary

#Ben's routes ------------------------------------------------

@app.route("/", methods=['GET'])
def index():
    return render_template("home.html")
    
@app.route("/retrieve", methods=['GET','POST'])
def get_file():
    if request.method == 'GET':
        img_name = parse_qs( urlparse( request.url ).query ).get('image', None)
        if img_name is None: #bad url parameter
            return("No image specified")
              
        #note the [0] index is because the parse_qs function returns a list, and we only want the 0th index since this url has one parameter (image)      
        query_res = load_img_name(img_name[0])
        if query_res is None: #bad url parameter
            return("No Image Specified")
        else: #return postprocessing base64 string
            return "<img src='data:image/png;base64," + query_res['image_post'] + "'/>"
            #return query_res['image_post']
    else:
        return("POST Disallowed")
            
#retrieve all images with a certain name attached to them
@app.route("/retrieve_by_user", methods=['GET','POST'])
def get_file_face():
    if request.method == 'GET':
        #weird hack-y string splitting to turn a list into an array with one element (what?)
        user_name = parse_qs( urlparse( request.url ).query ).get('user_name', None)[0]
        user_name = user_name.split(",")
        
        if user_name is None:
            return("Bad URL Parameter")
        
        list = load_img_face(user_name)
        res = ""
        if list:
            for l in list:    
                res = res + "<img src='data:image/png;base64," + l['image_post'] + "'/><br>"
        
            return res
        else:
            return("No images")
            
    else:
        return("POST Disallowed")
        
#retrieve all images with a certain user field
@app.route("/retrieve_by_username", methods=['GET','POST'])
def get_file_username():
    if request.method == 'GET':
        #only ever one element
        user_name = parse_qs( urlparse( request.url ).query ).get('user_name', None)[0]
        
        if user_name is None:
            return("Bad URL Parameter")
        
        list = load_img_user_name(user_name)
        res = ""
        if list:
            for l in list:    
                res = res + "<img src='data:image/png;base64," + l['image_post'] + "'/><br>"
        
            return res
        else:
            return("No images")
            
    else:
        return("POST Disallowed")
        
@app.route("/assign_to_user", methods=['GET','POST'])
def assign_to_user():
    if request.method == 'POST':
        user_num = parse_qs( urlparse( request.url ).query ).get('userID', None)[0]
        img_hash = parse_qs( urlparse( request.url ).query ).get('hash', None)[0]
        if user_num is None:
            return("No userID specified")
        
        if hash is None:
            return("No hash specified")
            
        res = assign_img_user(user_num, img_hash)
        print(res)
        if res is not None:
            return("Success!")
        else:
            return("Failed to assign user")
        
    else:
        return("GET Disallowed")
    

@app.route("/names", methods=['GET','POST'])
def manage_names():
    if request.method == 'POST':
    #POST new name data
        img_hash = parse_qs( urlparse( request.url ).query ).get('hash', None)[0]
        
        if img_hash is None:
            return('Bad URL Parameter')
    
        if 'faceList' not in request.form:
            return("Bad POST Parameter")
            
        if 'faceArr' not in request.form:
            return("Bad POST Parameter")
            
        face_arr = request.form['faceArr']
        face_list = request.form['faceList']
        
        face_arr = face_arr.split(",")
        face_list = face_list.split(",")
        
        #print(face_arr)
        #print(face_list)
        
        #img_res = load_img_hash(img_hash)
       
        #print(face_arr)
        #print(face_list)
        
        #img_res = load_img_hash(img_hash)
        
        #if img_res['faces'] != len(face_list):
        #    return("Face count mismatch!")
            
        res = update_face_list_data(img_hash, face_arr, face_list)
        
        if res is not None:
            return("Success")
        else:
            return("Failed to update face data")
        
    elif request.method == 'GET':
    #GET current name data
        img_hash = parse_qs( urlparse( request.url ).query ).get('hash', None)[0]
    
        if img_hash is None:
            return("Bad URL Parameter")
        
        res = load_img_hash(img_hash)
    
        if res is None:
            return("No Image Found")
    
        json_arr = {"faces":res['faces'], "faceList": res['faceList'], "faceArr": res['faceArr']}
        return jsonify(json_arr)

#upload route for single images (always processes)
@app.route("/upload", methods=['POST','GET'])
def upload_file():
    if request.method == 'POST':
    
        if 'file' not in request.files:
            if 'image' not in request.form:
                flash('No file part')
                return redirect(request.url)
            file = request.form['image']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                flash('Processing image...')
                filename = dt_string + '_' + secure_filename(file.filename)
                
                #save the pre-processing image to the processing folder
                file.save(os.path.join(app.config['PROCESSING_FOLDER'], filename))
                #open the image with PIL and hash it
                img = open_pil_image(filename)
                hash = hash_img(img)
                #call processing function
                res = process_image(filename, dt_string, hash, img)
                return res
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            flash('Processing image')
            filename = dt_string + '_' + secure_filename(file.filename)
            
            #save the pre-processing image to the processing folder
            file.save(os.path.join(app.config['PROCESSING_FOLDER'], filename))
            #open the image with PIL and hash it
            img = open_pil_image(filename)
            hash = hash_img(img)
            #call processing function
            res = process_image(filename, dt_string, hash, img)
            return res
        else:
            return("Bad file type")
    else:
        return("GET Disallowed")
        
#upload route for fb/ig modules, never processes
@app.route("/upload_module", methods=['POST', 'GET'])
def upload_file_noprocessing():
    if request.method == 'POST':
        if 'file' not in request.files:
            if 'image' not in request.form:
                flash('No file part')
                return redirect(request.url)
            file = request.form['image']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                flash('Saving without processing...')
                filename = dt_string + '_' + secure_filename(file.filename)
                
                #save the pre-processing image to the processing folder
                file.save(os.path.join(app.config['PROCESSING_FOLDER'], filename))
                #open the image with PIL and hash it
                img = open_pil_image(filename)
                hash = hash_img(img)
                #call processing function
                res = save_without_process_image(filename, dt_string, hash, img)
                return res
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            flash('Processing image')
            filename = dt_string + '_' + secure_filename(file.filename)
            
            #save the pre-processing image to the processing folder
            file.save(os.path.join(app.config['PROCESSING_FOLDER'], filename))
            #open the image with PIL and hash it
            img = open_pil_image(filename)
            hash = hash_img(img)
            #call processing function
            res = save_without_process_image(filename, dt_string, hash, img)
            return res
        else:
             return "filename not allowed"
    elif request.method == 'GET':
        return "GET not allowed"
    else:
        return "file not in request.files"

#Kien's routes ---------------------------------------------------

@app.route('/FacebookAuth/user/<string:albumid>', methods=['GET'])
def display_album_fb(albumid):
    try:
        global img_urls_dict
        global short_lived_token, long_lived_token
        if long_lived_token == "":
            return redirect('/')
        else:
            img_urls_dict = facebook.get_images_from_album(albumid, long_lived_token, 1)
    except ValueError as e:
        error_msg = "Can't get user media: " + str(e)
        return render_template("Error.html", error=error_msg)
    else:
        return render_template("index.html", dic=img_urls_dict, s_token=short_lived_token, l_token=long_lived_token)


@app.route('/FacebookAuth/user', methods=['GET'])
def display_info_fb():
    try:
        global album_urls_dict
        global short_lived_token, long_lived_token
        if long_lived_token == "":
            return redirect('/')
        else:
            album_urls_dict = facebook.get_all_albums(long_lived_token)
    except ValueError as e:
        error_msg = "Can't get user media: " + str(e)
        return render_template("Error.html", error=error_msg)
    else:
        return render_template("facebook.html", dic=album_urls_dict, s_token=short_lived_token, l_token=long_lived_token)


# route for displaying the user information
@app.route('/InstagramAuth/user', methods=['GET'])
def display_info_inst():
    try:
        global img_urls_dict
        global short_lived_token, long_lived_token
        post_url = "https://bts630test.herokuapp.com/upload_module" #POST route for uploading
        if long_lived_token == "":
            return redirect('/')
        else:
            img_urls_dict = instagram.get_user_media(long_lived_token, "media_url")
            
            for item in img_urls_dict:
                #POST image to upload_module to enter into database
                dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        
                img_data = requests.get(img_urls_dict[item]).content
                with open(dt_string + ".jpg", 'wb') as handler:
                    handler.write(img_data)
                            
                files = {"file": ( dt_string + ".jpg", open(dt_string + ".jpg", 'rb'), 'multipart/form-data', {'Expires':'0'}) }
                        
                with requests.Session() as s:
                    r = s.post(post_url, files=files)
                    print(r.status_code)
                        
                #remove the temp file after we're done
                os.remove(dt_string + ".jpg")
                
    except ValueError as e:
        error_msg = "Can't get user media: " + str(e)
        return render_template("Error.html", error=error_msg)
    else:
        return render_template("index.html", dic=img_urls_dict, s_token=short_lived_token, l_token=long_lived_token)


# routes for getting user access token
@app.route('/InstagramAuth/', methods=['GET'])
def get_inst_access_token():
    # Retrieve the name from url parameter
    access_code = request.args.get("code", None)

    # For debugging
    print(f"got {access_code}")

    if not access_code:
        return render_template("Error.html", error="no access code found, something when wrong!.")
    else:
        try:
            global short_lived_token, long_lived_token
            short_lived_token = instagram.get_access_token(access_code)
            long_lived_token = instagram.get_long_lived_token(short_lived_token)
            return redirect('/InstagramAuth/user')
        except ValueError as e:
            error_msg = "Can't get user access token: "+str(e)
            return render_template("Error.html", error=error_msg)


@app.route('/FacebookAuth/', methods=['GET'])
def get_fb_access_token():
    # Retrieve the name from url parameter
    access_code = request.args.get("code", None)

    # For debugging
    print(f"got {access_code}")

    if not access_code:
        return render_template("Error.html", error="no access code found, something when wrong!.")
    else:
        try:
            global short_lived_token, long_lived_token
            short_lived_token = facebook.get_token("https://bts630test.herokuapp.com/FacebookAuth/", access_code)
            long_lived_token = facebook.get_long_lived_token(short_lived_token)
            return redirect('/FacebookAuth/user')
        except ValueError as e:
            error_msg = "Can't get user access token: "+str(e)
            return render_template("Error.html", error=error_msg)


# route for logging a user out
@app.route('/logout', methods=['GET'])
def logout():
    global short_lived_token, long_lived_token
    short_lived_token = ""
    long_lived_token = ""
    return redirect('/')


@app.route('/loginInst', methods=['GET'])
def login_inst():
    redirect_url = instagram.get_access_code()
    return redirect(redirect_url)


@app.route('/loginFb', methods=['GET'])
def login_fb():
    redirect_url = facebook.login("https://bts630test.herokuapp.com/FacebookAuth/")
    return redirect(redirect_url)

#Main()

if __name__ == "__main__":
    #server.run(host="0.0.0.0", port=port)
    app.run(threaded="true", port=port)