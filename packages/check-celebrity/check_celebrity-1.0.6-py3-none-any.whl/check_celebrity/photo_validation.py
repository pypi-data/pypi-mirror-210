from deepface import DeepFace
from flask import Flask,request
from flask_restful import Resource, Api
import os
from werkzeug.utils import secure_filename
from mtcnn.mtcnn import MTCNN
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
from keras_vggface.utils import decode_predictions
from keras.utils.layer_utils import get_source_inputs
from celebrity_match import *
import json 

app = Flask(__name__)
api = Api(app)

detector = MTCNN()
model = VGGFace(model= 'resnet50')

@app.route('/verify_image',methods=['POST'])
def verify_image():
    image = request.files['image']
    filename = secure_filename(image.filename) # save file 
    filepath = os.path.join('..\images', filename)
    print(filepath)
    image.save(filepath)
    face_objs = DeepFace.extract_faces(img_path = filepath, target_size = (224, 224),enforce_detection=False)
    print(face_objs)
    print(face_objs[0]['confidence'])
    if face_objs[0]['confidence'] > 0.5:
        return "verified"
    else:
         return "not verified"


         
    
@app.route('/check_celebrity',methods=['POST'])
def check_image():
    image = request.files['image']
    filename = secure_filename(image.filename) # save file 
    print(filename)
    filepath = os.path.join('..\images', filename)
    print(filepath)
    image.save(filepath)
    results = predict_from_image_url(filepath, face_detector=detector, model=model)
    print('result',results)
    scores=[]
    name=[]
    print(len(results))
    for i in range(len(results)):
        name.append(results[i][0])
        scores.append(results[i][1])
    print(name)
    print(scores)
    index =scores.index(max(scores))
    if os.path.exists(filepath):
          os.remove(filepath)
    return name[index]

if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True,port='8082')