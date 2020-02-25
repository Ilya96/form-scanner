from fpdf import FPDF
import numpy as np
import cv2
import os

def save_form_batch(im_files_list:list, target_name):
    if len(im_files_list) == 0:
        return
    pdf = FPDF()
    for im_file in im_files_list:
        filename, file_extension = os.path.splitext(im_file)
        if file_extension != '.jpg':
            f = open(im_file, "rb")
            chunk = f.read()
            chunk_arr = np.frombuffer(chunk, dtype=np.uint8)
            img = cv2.imdecode(chunk_arr, cv2.IMREAD_COLOR)
            f.close()
            os.remove(im_file)
            im_file = filename + '.jpg'
            f = open(im_file, "wb")
            chunk_arr = cv2.imencode('.jpg', img)[1]
            chunk = chunk_arr.tobytes()
            f.write(chunk)
        pdf.add_page()
        pdf.image(im_file, x = 0, y = 0, w = 210)

    pdf.output(target_name, 'F')
    return
