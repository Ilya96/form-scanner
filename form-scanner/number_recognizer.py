import cv2
import numpy as np

def recognize_digit(image_np):
    """
    Распознавание одной цифры
    """
    pass

def split_code(image_np):
    digits = []
    return digits

def recognize_code(image_np):
    digits = []
    for digit_np in split_code(image_np):
        digits.append(recognize_digit(digit_np))

    return -1
