import cv2
import numpy as np
from keras import backend as K

def debug_show_image(image_np, name='Image'):
    #image_np = cv2.resize(image_np, (500, 760))
    #cv2.imshow(name, image_np)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    pass

class CodeRecognizer:
    pc_digit_segments_categorical = np.array([  # 1  2  3  4  5  6  7  8  9
        [1, 1, 0, 1, 0, 1, 0, 1, 1],  # 0
        [0, 0, 1, 1, 0, 0, 0, 1, 0],  # 1
        [1, 0, 0, 1, 0, 0, 1, 0, 1],  # 2
        [1, 0, 1, 0, 1, 0, 1, 0, 0],  # 3
        [0, 1, 0, 1, 1, 0, 0, 1, 0],  # 4
        [1, 1, 0, 0, 1, 0, 0, 1, 1],  # 5
        [0, 0, 1, 0, 1, 0, 0, 1, 1],  # 6
        [1, 0, 1, 0, 0, 1, 0, 0, 0],  # 7
        [1, 1, 0, 1, 1, 1, 0, 1, 1],  # 8
        [1, 1, 0, 1, 1, 0, 1, 0, 0]  # 9
    ])

    pc_digit_segments_list = [
        [1, 2, 4, 6, 8, 9],  # 0
        [3, 4, 8],  # 1
        [1, 4, 7, 9],  # 2
        [1, 3, 5, 7],  # 3
        [2, 4, 5, 8],  # 4
        [1, 2, 5, 8, 9],  # 5
        [3, 5, 6, 8, 9],  # 6
        [1, 3, 6],  # 7
        [1, 2, 4, 5, 6, 8, 9],  # 8
        [1, 2, 4, 5, 7]  # 9
    ]

    rnn_pc_img_cols = 50
    rnn_pc_img_rows = 100

    def __init__(self, mode='POST_CODE'):
        self.recognize_digit = None
        if mode == 'POST_CODE':
            self.recognize_digit = self.recognize_pc_digits
        elif mode == 'HAND_DIGITS':
            import keras
            from keras.models import load_model
            self.model = load_model('MNIST_RNN.h5')
            self.recognize_digit = self.recognize_hw_digits
        elif mode == 'POST_CODE_RNN':
            from keras.models import load_model
            self.model = load_model('PC_RNN.h5')
            self.recognize_digit = self.recognize_rnn_pc_digits

    def prepare_image_for_rnn_pc(self, image_np):
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

        gray_image_np = cv2.resize(gray_image_np, (int(CodeRecognizer.rnn_pc_img_cols), int(CodeRecognizer.rnn_pc_img_rows)))
        return gray_image_np

    def recognize_rnn_pc_digits(self, image_np_list):
        img_cols = CodeRecognizer.rnn_pc_img_cols
        img_rows = CodeRecognizer.rnn_pc_img_rows

        images_np_prepared = []
        for image_np in image_np_list:
            images_np_prepared.append(self.prepare_image_for_rnn_pc(image_np))
        data_np = np.stack(images_np_prepared)

        if K.image_data_format() == 'channels_first':
            data_np = data_np.reshape(data_np.shape[0], 1, img_rows, img_cols)
            input_shape = (1, img_rows, img_cols)
        else:
            data_np = data_np.reshape(data_np.shape[0], img_rows, img_cols, 1)
            input_shape = (img_rows, img_cols, 1)
        data_np = data_np.astype('float32')
        data_np /=255
        digit_value = self.model.predict(data_np, verbose=0)
        digit_value_rate = np.max(digit_value, 1)
        digit_value_pred = np.argmax(digit_value, 1)
        answer = []
        for ind, pred in enumerate(digit_value_pred):
            answer.append((pred, digit_value_rate[ind]))
        return answer

    def recognize_hw_digits(self, image_np_list):
        answer = []
        for image_np in image_np_list:
            answer.append(self.recognize_hw_digit(image_np))
        print(answer)
        return answer

    def recognize_hw_digit(self, image_np):
        """
        Распознавание одной цифры
        """
        image_np = image_np[int(image_np.shape[0]*0.05):int(image_np.shape[0]*0.95),
                            int(image_np.shape[1]*0.05):int(image_np.shape[1]*0.95)]
        gray_image_np = cv2.cvtColor(image_np.copy(), cv2.COLOR_RGB2GRAY)

        _, gray_image_np = cv2.threshold(
            gray_image_np, 200, 255, cv2.THRESH_BINARY)

        kernel_shape = image_np.shape[0] * 0.01
        kernel_shape = int(kernel_shape)
        kernel = np.ones((kernel_shape, kernel_shape), np.uint8)
        #gray_image_np = cv2.morphologyEx(gray_image_np, cv2.MORPH_CLOSE, kernel)
        gray_image_np = cv2.morphologyEx(gray_image_np, cv2.MORPH_OPEN, kernel)
        gray_image_np = cv2.bitwise_not(gray_image_np)
        x, y, w, h = cv2.boundingRect(gray_image_np)
        # Получили обрезанную цифру
        #gray_image_np = gray_image_np[y:y+h, x:x+w]

        # Нормировка под датасет MNIST
        # Размер изображения 28x28, размер цифры 20x20, центровка по центру масс (пока нет)

        scale_rate = 20 / max(gray_image_np.shape)
        newX, newY = gray_image_np.shape[1] * \
            scale_rate, gray_image_np.shape[0]*scale_rate
        gray_image_np = cv2.resize(gray_image_np, (int(newX), int(newY)))

        top_pad = round((28 - gray_image_np.shape[0]) / 2)
        bottom_pad = (28 - gray_image_np.shape[0]) // 2
        if gray_image_np.shape[0] + top_pad + bottom_pad < 28:
            top_pad += 1
        left_pad = round((28 - gray_image_np.shape[1]) / 2)
        right_pad = (28 - gray_image_np.shape[1]) // 2
        if gray_image_np.shape[1] + left_pad + right_pad < 28:
            right_pad += 1
        #print(gray_image_np.shape)
        #print(top_pad, bottom_pad, left_pad, right_pad)
        gray_image_np = np.pad(gray_image_np, ((
            top_pad, bottom_pad), (left_pad, right_pad)), 'constant', constant_values=(0,))

        image4predict = np.expand_dims(gray_image_np.copy(), axis=0)
        image4predict = np.expand_dims(image4predict, axis=-1)
        digit_value = self.model.predict(image4predict, verbose=1)
        digit_value_pred = np.argmax(digit_value, 1)
        #print(digit_value)
        #cv2.imshow('image', gray_image_np)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return digit_value_pred[0], np.max(digit_value, 1)

    def get_segment_weight(self, image_np, mask):
        image_np = cv2.bitwise_or(image_np, image_np, mask=mask)
        return image_np.sum() / mask.sum()

    def get_9_segments_weights(self, image_np):
        w = int(image_np.shape[1])
        newX, newY = w, w*2
        image_np = cv2.resize(image_np.copy(), (int(newX), int(newY)))
        weights = []
        for i in range(1, 10):
            np_mask = self.get_9_segments([i], w)
            weig = self.get_segment_weight(image_np, np_mask)
            weights.append(weig)
        return weights

    def get_9_segments(self, segments, size):
        '''
         -       1
        |/|    2 3 4
         -       5
        |/|    6 7 8
         -       9

        '''
        np_digit = np.zeros((2*size, size), np.uint8)
        thickness = 0.25
        if 1 in segments:
            np_digit = cv2.line(np_digit, (0, int(size*thickness/2)),
                                (size, int(size*thickness/2)), 255, int(size*thickness))
        if 2 in segments:
            np_digit = cv2.line(np_digit, (int(size*thickness/2), 0),
                                (int(size*thickness/2), size), 255, int(size*thickness))
        if 3 in segments:
            np_digit = cv2.line(np_digit, (0, size),
                                (size, 0), 255, int(size*thickness))
        if 4 in segments:
            np_digit = cv2.line(np_digit, (size-int(size*thickness/2), 0),
                                (size-int(size*thickness/2), size), 255, int(size*thickness))
        if 5 in segments:
            np_digit = cv2.line(np_digit, (0, size),
                                (size, size), 255, int(size*thickness))
        if 6 in segments:
            np_digit = cv2.line(np_digit, (int(size*thickness/2), size),
                                (int(size*thickness/2), 2*size), 255, int(size*thickness))
        if 7 in segments:
            np_digit = cv2.line(np_digit, (0, 2*size),
                                (size, size), 255, int(size*thickness))
        if 8 in segments:
            np_digit = cv2.line(np_digit, (size-int(size*thickness/2), size),
                                (size-int(size*thickness/2), 2*size), 255, int(size*thickness))
        if 9 in segments:
            np_digit = cv2.line(np_digit, (0, 2*size-int(size*thickness/2)),
                                (size, 2*size-int(size*thickness/2)), 255, int(size*thickness))
        return np_digit

    def get_pc_digit_segments(self, value):
        return CodeRecognizer.pc_digit_segments_list[value]

    def get_pc_digit(self, value, size):
        segs = self.get_pc_digit_segments(value)
        np_digit = self.get_9_segments(segs, size)
        return np_digit

    def recognize_pc_digits(self, image_np_list):
        answer = []
        for image_np in image_np_list:
            answer.append(self.recognize_pc_digit(image_np))
        return answer

    def recognize_pc_digit(self, image_np):

        gray_image_np = cv2.cvtColor(image_np.copy(), cv2.COLOR_RGB2GRAY)

        #debug_show_image(gray_image_np, 'Digit')

        _, gray_image_np = cv2.threshold(
            gray_image_np, 200, 255, cv2.THRESH_BINARY)

        w = gray_image_np.shape[1]
        #gray_image_np = gray_image_np[:, int(w*0.125):int(w*0.875)]
        gray_image_np = gray_image_np[int(image_np.shape[0]*0.01):int(
            image_np.shape[0]*0.97), int(image_np.shape[1]*0.03):int(image_np.shape[1]*0.97)]
        gray_image_np = cv2.bitwise_not(gray_image_np.copy())

        #debug_show_image(gray_image_np, 'Digit')

        kernel_shape = image_np.shape[0] * 0.03
        kernel_shape = int(kernel_shape)
        kernel = np.ones((kernel_shape, kernel_shape), np.uint8)
        gray_image_np = cv2.morphologyEx(
            gray_image_np, cv2.MORPH_CLOSE, kernel)
        gray_image_np = cv2.morphologyEx(gray_image_np, cv2.MORPH_OPEN, kernel)

        x, y, w, h = cv2.boundingRect(gray_image_np)
        # Получили обрезанную цифру
        gray_image_np = gray_image_np[y:y+h, x:x+w]

        #debug_show_image(gray_image_np, 'Digit')

        kernel_shape = int(gray_image_np.shape[0] * 0.04)
        kernel = np.ones((kernel_shape, kernel_shape), np.uint8)

        #print(gray_image_np.shape)
        gray_image_np = cv2.erode(gray_image_np, kernel, iterations=1)
        gray_image_np = cv2.dilate(gray_image_np, kernel, iterations=1)

        #x,y,w,h = cv2.boundingRect(gray_image_np)
        # gray_image_np = gray_image_np[y:y+h,x:x+w] #Получили обрезанную цифру
        w = gray_image_np.shape[1]
        newX, newY = w, w*2
        gray_image_np = cv2.resize(gray_image_np, (int(newX), int(newY)))

        #debug_show_image(gray_image_np, 'Digit')
        # Находим расстояние
        distances = np.zeros([10, ])
        for i in range(10):
            np_digit = self.get_pc_digit(i, w)
            # Находим точки в шаблоне
            dif_1_image_np = gray_image_np.copy()
            dif_1_image_np = cv2.bitwise_or(
                dif_1_image_np, dif_1_image_np, mask=np_digit)
            #cv2.imshow('dif_1_image_np', dif_1_image_np)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            # Находим точки вне шаблона
            dif_2_image_np = gray_image_np.copy()
            np_digit = cv2.bitwise_not(np_digit)
            dif_2_image_np = cv2.bitwise_or(
                dif_2_image_np, dif_2_image_np, mask=np_digit)


            # Расстояние нормируем на площадь шаблона
            distances[i] = np.abs(dif_1_image_np).sum()/np_digit.sum()
        #print("------------------------------------------------")
        segments_weights = self.get_9_segments_weights(gray_image_np)
        # Убираем тренд
        segments_weights = segments_weights - np.min(segments_weights)
        # Нормируем по максимальному заполнению
        segments_weights = segments_weights / np.max(segments_weights)

        #print(segments_weights)
        #print(CodeRecognizer.pc_digit_segments_categorical)
        #print(distances)
        categorical_rate = segments_weights * CodeRecognizer.pc_digit_segments_categorical
        #print(categorical_rate)
        categorical_error = CodeRecognizer.pc_digit_segments_categorical - segments_weights
        #print(categorical_error)
        rate = categorical_rate.sum(axis=1) / CodeRecognizer.pc_digit_segments_categorical.sum(axis=1)
        #print(rate)
        error = np.abs(categorical_error).sum(axis=1)
        #print(error)
        #print(rate.argmax())

        return error.argmin(), 1/error.min()

    def split_code(self, image_np, length=5):

        digits = []
        digit_width = image_np.shape[1]/length
        for i in range(length):
            digit = image_np[:, int(i*digit_width):int((i+1)*digit_width)].copy()
            digits.append(digit)
        return digits

    def get_code(self, image_np):
        return image_np[int(0.0*image_np.shape[0])+1:int(0.04*image_np.shape[0])+1, int(0.547*image_np.shape[1])+1: int(0.76*image_np.shape[1])+1]

    def recognize_code(self, image_np):

        if image_np is None:
            return None
        #template_image_np = image_np[int(0.055*image_np.shape[0])+1:int(
        #    0.087*image_np.shape[0])+1, int(0.415*image_np.shape[1])+1: int(0.775*image_np.shape[1])+1]
        #templates = []
        #for digit_np in self.split_code(template_image_np, 10):
        #    templates.append(self.recognize_digit(digit_np, alignment=True))
        #print(templates)

        debug_show_image(image_np, 'Src image')
        image_np = self.get_code(image_np)
        #debug_show_image(image_np, 'Number image')

        digits = []
        is_success = True
        for val, rate in self.recognize_digit(self.split_code(image_np)):
            if rate < 0.5:
                print("Not success recognize digit")
                is_success = False
                val = 'X'
            elif val>9:
                print("Not success recognize digit")
                is_success = False
                val = 'X'
            #print(val, rate)
            digits.append(val)
        listToStr = ''.join([str(elem) for elem in digits])
        print(listToStr)
        if is_success:
            return int(listToStr)
        else:
            return listToStr
