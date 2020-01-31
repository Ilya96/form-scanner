from tkinter import filedialog
from tkinter import *
import tkinter as tk
import cv2

from form_alignment import align_form
from number_recognizer import CodeRecognizer
from gui.main_window import MainWindow

def main():
    root = Tk()
    filename =  filedialog.askopenfilename(initialdir = ".",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    root.destroy()
    print (filename)
    image_np = cv2.imread(filename)
    image_np = align_form(image_np)

    code_recognizer = CodeRecognizer()
    code = code_recognizer.recognize_code(image_np)
    print(code)

    target_X = 500
    imgScale = target_X / image_np.shape[1]
    newX,newY = image_np.shape[1]*imgScale, image_np.shape[0]*imgScale
    image_np = cv2.resize(image_np,(int(newX),int(newY)))
    cv2.imshow('image', image_np)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite("result.jpg", image_np)

if __name__ == "__main__":
    #main()
    root = tk.Tk()
    app = MainWindow(master=root)
    app.mainloop()
