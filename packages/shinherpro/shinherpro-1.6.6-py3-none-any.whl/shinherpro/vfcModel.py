from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from bs4 import BeautifulSoup
from keras.utils import img_to_array
from keras.utils import load_img
from keras.models import load_model
from PIL import Image
from io import BytesIO
import requests
import numpy as np
import cv2
import time
import json
import os

def setup(model_path):
    full_path = os.path.abspath(model_path)
    print("模型檔案路徑：", full_path)
    model = load_model(model_path)
    print(model_path + " load Success")
    return model

def official_model(Version):
    current_folder = os.path.dirname(os.path.abspath(__file__))
    print(current_folder)
    current_folder = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_folder, 'vfc_AiModel_5.1_VGG16_black.h5')
    print("vfc_AiModel_5.1_VGG16_black.h5 的完整路徑：", model_path)
    return model_path

def vfcCodeFilter(img):
    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    kernel_d = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 3))
    kernel_e = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    img = cv2.dilate(img, kernel_d)
    img = cv2.erode(img, kernel_e)

    img = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)[1]
    return Image.fromarray(img)

def predict_image(image_path, captcha_image, model):
    image_bytes = BytesIO()
    captcha_image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    image = load_img(image_path, target_size=(224, 224))
    image = img_to_array(image)
    image = image / 255.0
    image = np.expand_dims(image, axis=0)

    predictions = model.predict(image)
    predicted_label = np.argmax(predictions, axis=1)[0]
    confidence = predictions[0][predicted_label]

    return predicted_label, confidence