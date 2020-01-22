import cv2
import numpy as np

import keras
from keras.models import load_model

model = load_model('MNIST_RNN.h5')

def recognize_digit(image_np):
    """
    Распознавание одной цифры
    """
    image_np = image_np[int(image_np.shape[0]*0.05):int(image_np.shape[0]*0.95),int(image_np.shape[1]*0.05):int(image_np.shape[1]*0.95)]
    gray_image_np = cv2.cvtColor(image_np.copy(), cv2.COLOR_RGB2GRAY)

    _, gray_image_np = cv2.threshold(
        gray_image_np, 200, 255, cv2.THRESH_BINARY)

    kernel_shape = image_np.shape[0] * 0.01
    kernel_shape = int(kernel_shape)
    kernel = np.ones((kernel_shape, kernel_shape), np.uint8)
    #gray_image_np = cv2.morphologyEx(gray_image_np, cv2.MORPH_CLOSE, kernel)
    gray_image_np = cv2.morphologyEx(gray_image_np, cv2.MORPH_OPEN, kernel)
    gray_image_np = cv2.bitwise_not(gray_image_np)
    x,y,w,h = cv2.boundingRect(gray_image_np)
    gray_image_np = gray_image_np[y:y+h,x:x+w] #Получили обрезанную цифру

    # Нормировка под датасет MNIST
    # Размер изображения 28x28, размер цифры 20x20, центровка по центру масс (пока нет)

    scale_rate = 20 / max(gray_image_np.shape)
    newX,newY = gray_image_np.shape[1]*scale_rate, gray_image_np.shape[0]*scale_rate
    gray_image_np = cv2.resize(gray_image_np,(int(newX),int(newY)))

    top_pad =  round((28 - gray_image_np.shape[0]) / 2)
    bottom_pad = (28 - gray_image_np.shape[0]) // 2
    if gray_image_np.shape[0] + top_pad + bottom_pad < 28 : top_pad+=1
    left_pad = round((28 - gray_image_np.shape[1]) / 2)
    right_pad = (28 - gray_image_np.shape[1]) // 2
    if gray_image_np.shape[1] + left_pad + right_pad < 28: right_pad+=1
    print(gray_image_np.shape)
    print(top_pad, bottom_pad, left_pad, right_pad)
    gray_image_np = np.pad(gray_image_np, ((top_pad, bottom_pad), (left_pad, right_pad)), 'constant', constant_values=(0,))

    image4predict = np.expand_dims(gray_image_np.copy(), axis=0)
    image4predict = np.expand_dims(image4predict, axis=-1)
    digit_value = model.predict(image4predict, verbose=1)
    digit_value = np.argmax(digit_value, 1)
    print(digit_value)
    #cv2.imshow('image', gray_image_np)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    return digit_value[0]

def split_code(image_np):

    digits = []
    digit_width = image_np.shape[1]/5
    for i in range(5):
        digit = image_np[:,int(i*digit_width):int((i+1)*digit_width)].copy()
        digits.append(digit)
    return digits

def recognize_code(image_np):
    digits = []

    for digit_np in split_code(image_np):
        digits.append(recognize_digit(digit_np))
    listToStr = ''.join([str(elem) for elem in digits])
    print(listToStr)
    int(listToStr)
    return -1
