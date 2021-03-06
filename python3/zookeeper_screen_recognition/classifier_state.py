import os
import json
import cv2
import numpy as np
from functools import lru_cache
from . import _util

MODEL_PATH = 'model'
WEIGHT_FILENAME = 'classifier_state.hdf5'
DATA_FILENAME   = 'data.json'

from . import classifier_state_model

WIDTH  = classifier_state_model.WIDTH
HEIGHT = classifier_state_model.HEIGHT

load_img = _util.load_img

def preprocess_img(img):
    img = cv2.resize(img,dsize=(WIDTH,HEIGHT),interpolation=cv2.INTER_AREA)
    img = append_xy_layer(img)
    return img

@lru_cache(maxsize=4)
def xy_layer():
    w = WIDTH
    h = HEIGHT
    xx = np.array(list(range(w))).astype('float32')*2/(w-1)-1
    xx = np.tile(xx,h)
    xx = np.reshape(xx,(h,w,1))
    yy = np.array(list(range(h))).astype('float32')*2/(h-1)-1
    yy = np.repeat(yy,w)
    yy = np.reshape(yy,(h,w,1))
    xxyy = np.append(xx,yy,axis=2)
    return xxyy

def append_xy_layer(img):
    return np.append(img,xy_layer(),axis=2)

class StateClassifier:

    def __init__(self, model_path):
        weight_path = os.path.join(model_path, WEIGHT_FILENAME)
        data_path   = os.path.join(model_path, DATA_FILENAME)
        with open(data_path,'r') as fin:
            self.data = json.load(fin)
        self.model = classifier_state_model.create_model(len(self.data['label_name_list']))
        self.model.load_weights(weight_path)

    def get_state(self, img):
        img = preprocess_img(img)
        p = self.model.predict(np.expand_dims(img, axis=0))
        score = np.max(p)
        label_idx = np.argmax(p)
        return self.data['label_name_list'][label_idx], score

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='state classifier')
    parser.add_argument('img_file', help="img_file")
    args = parser.parse_args()
    
    img = load_img(args.img_file)

    sc = StateClassifier(MODEL_PATH)

    label, score = sc.get_state(img)
    print('{} {}'.format(label, score))
