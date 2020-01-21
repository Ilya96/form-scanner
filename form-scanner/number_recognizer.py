import cv2
import numpy as np

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
    _, contours,hierarchy = cv2.findContours(gray_image_np,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours
    x,y,w,h = cv2.boundingRect(gray_image_np)
    print(gray_image_np)
    gray_image_np = gray_image_np[y:y+h,x:x+w] #Получили обрезанные цифры

    # Добавить нормировку под датасет MNIST

    cv2.imshow('image', gray_image_np)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return 0

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

    return -1
