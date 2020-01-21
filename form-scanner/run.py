from tkinter import filedialog
from tkinter import *
import cv2

from form_alignment import align_form
from number_recognizer import recognize_code

def main():
    root = Tk()
    filename =  filedialog.askopenfilename(initialdir = ".",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    root.destroy()
    print (filename)
    image_np = cv2.imread(filename)
    image_np = align_form(image_np)
    print(image_np.shape)
    code_np = image_np[int(0.041*image_np.shape[0])+1:int(0.0721*image_np.shape[0])+1, int(0.564*image_np.shape[1])+1: int(0.804*image_np.shape[1])+1]
    code = recognize_code(code_np)
    print(code)

    target_X = 500
    imgScale = target_X / image_np.shape[1]
    newX,newY = image_np.shape[1]*imgScale, image_np.shape[0]*imgScale
    image_np = cv2.resize(image_np,(int(newX),int(newY)))
    cv2.imshow('image', code_np)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite("result.jpg", image_np)

if __name__ == "__main__":
    main()
