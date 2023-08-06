from mtcnn.mtcnn import MTCNN
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
from keras_vggface.utils import decode_predictions
import PIL
# import os
import numpy as np
import cv2

detector = MTCNN()

model = VGGFace(model= 'resnet50')

def get_img(url):
    
    # Read the image using opencv
    img=cv2.imread(url)

    return img

def find_face(img, detector = None):
    # Initialize mtcnn detector
    detector = MTCNN() if detector is None else detector 
    # set face extraction parameters
    target_size = (224,224) # output image size
    border_rel = 0 # increase or decrease zoom on image
    # detect faces in the image
    detections = detector.detect_faces(img)
    x1, y1, width, height = detections[0]['box']
    dw = round(width * border_rel)
    dh = round(height * border_rel)
    x2, y2 = x1 + width + dw, y1 + height + dh
    face = img[y1:y2, x1:x2]
    # resize pixels to the model size
    face = PIL.Image.fromarray(face)
    face = face.resize((224, 224))
    face = np.asarray(face)
    return face

def preprocess_face(face):
    # convert to float32
    face_pp = face.astype('float32')
    face_pp = np.expand_dims(face_pp, axis = 0)
    face_pp = preprocess_input(face_pp, version = 2)
    return face_pp

def predict(face_pp, model=None):
    model = VGGFace(model= 'resnet50') if model is None else model
    return model.predict(face_pp)

def extract_and_display_results(prediction, img):
    # convert predictions into names & probabilities
    results = decode_predictions(prediction)
    # Display results
    
    # for result in results[0]:
    #     print ('%s: %.3f%%' % (result[0], result[1]*100))

    return results[0]

def predict_from_image_url(image, face_detector=None, model=None):
    img = get_img(image)
    face = find_face(img, detector=face_detector)
    face_pp = preprocess_face(face)
    prediction = predict(face_pp, model=model)
    return extract_and_display_results(prediction, img)

