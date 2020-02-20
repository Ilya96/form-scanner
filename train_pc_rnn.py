import os
import matplotlib.pyplot as plt
import numpy as np

import cv2

from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels
from sklearn.datasets import load_files
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import multiprocessing

img_rows, img_cols = 100, 50
num_classes = 11
batch_size = 10
epochs = 15

def load_dataset_item(file):
    image_np = cv2.imread(file)
    image_np = cv2.cvtColor(image_np.copy(), cv2.COLOR_RGB2GRAY)
    return image_np

def train():
    import keras

    data = load_files('./dataset',
                        shuffle=True,
                        encoding=None,
                        load_content=False)
    print(data.keys())
    print(data['target_names'])
    print(data['target'])
    print(data.keys())
    nb_data_samples = len(data['filenames'])
    print("data samples: ", nb_data_samples)

    with multiprocessing.Pool(processes=2) as pool:
        data_images = pool.map(load_dataset_item, data['filenames'])
    data_np = np.stack(data_images)
    x_train, x_test, y_train, y_test = train_test_split(data_np, data['target'], train_size=1900, test_size=2214-1900)

    from keras import backend as K

    if K.image_data_format() == 'channels_first':
        x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
        x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
        input_shape = (1, img_rows, img_cols)
    else:
        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
        input_shape = (img_rows, img_cols, 1)

    x_train = np.array(x_train).astype('float32')
    y_train = np.array(y_train).astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255
    print('x_train shape:', x_train.shape)
    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')

    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)
    print(y_test[0])

    from keras.models import Sequential
    from keras.layers import Dense, Dropout, Flatten, Activation
    from keras.layers import Conv2D, MaxPooling2D

    model = Sequential()
    model.add(Conv2D(32, (3, 3), padding='same',
                    input_shape=x_train.shape[1:]))
    model.add(Activation('relu'))
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation='softmax'))

    model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.Adadelta(),
              metrics=['accuracy'])

    model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=epochs,
          verbose=1,
          validation_data=(x_test, y_test))

    score = model.evaluate(x_test, y_test, verbose=0)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])
    model.save('PC_RNN.h5')  # creates a HDF5 file 'my_model.h5'
    # Размер изображения

def preprocess_digit(image_np):
    gray_image_np = cv2.cvtColor(image_np.copy(), cv2.COLOR_RGB2GRAY)

    _, gray_image_np = cv2.threshold(
        gray_image_np, 200, 255, cv2.THRESH_BINARY)

    w = gray_image_np.shape[1]
    #gray_image_np = gray_image_np[:, int(w*0.125):int(w*0.875)]
    gray_image_np = gray_image_np[int(image_np.shape[0]*0.01):int(
        image_np.shape[0]*0.97), int(image_np.shape[1]*0.03):int(image_np.shape[1]*0.97)]
    gray_image_np = cv2.bitwise_not(gray_image_np.copy())


    kernel_shape = image_np.shape[0] * 0.03
    kernel_shape = int(kernel_shape)
    kernel = np.ones((kernel_shape, kernel_shape), np.uint8)
    gray_image_np = cv2.morphologyEx(
        gray_image_np, cv2.MORPH_CLOSE, kernel)
    gray_image_np = cv2.morphologyEx(gray_image_np, cv2.MORPH_OPEN, kernel)

    x, y, w, h = cv2.boundingRect(gray_image_np)
    # Получили обрезанную цифру
    if w != 0 or h != 0:
        gray_image_np = gray_image_np[y:y+h, x:x+w]

    gray_image_np = cv2.resize(gray_image_np, (int(img_cols), int(img_rows)))
    return gray_image_np

def prepare():
    data = load_files('./dataset', load_content=False)
    print(data)
    for im_name in tqdm(data['filenames']):
        #print(im_name)
        image_np = cv2.imread(im_name)
        image_np = preprocess_digit(image_np)
        #cv2.imshow(im_name, image_np)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        cv2.imwrite(im_name, image_np)

if __name__ == "__main__":
    #prepare()
    train()
