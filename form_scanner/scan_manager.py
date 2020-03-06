import os
import glob
import cv2
import number_recognizer
import numpy as np
from number_recognizer import CodeRecognizer
from form_alignment import align_form
import form_saver
import random
import imutils

class ScanManager:
    NOT_RECOGNIZED_FORM_NAME = 'NOT_RECOGNIZED'

    def __init__(self, src_dir, dst_dir):
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.src_files = []
        self.load_dir(src_dir)
        self.prepare_target_dir(dst_dir)
        self.batches = {}
        self._code_recognizer = CodeRecognizer(mode='POST_CODE_RNN')
        self._log_handler = None

    def set_log_handler(self, fcn):
        self._log_handler = fcn

    def add2log(self, msg):
        try:
            self._log_handler(msg)
        except:
            pass

    def prepare_target_dir(self, dst_dir):

        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        #if not os.path.exists(os.path.join(dst_dir, ScanManager.NOT_RECOGNIZED_FORM_NAME)):
        #    os.makedirs(os.path.join(
        #        dst_dir, ScanManager.NOT_RECOGNIZED_FORM_NAME))

    def load_dir(self, path):
        mask = "{path}/*.jpg".format(path=path)
        self.src_files = glob.glob(mask)
        mask = "{path}/*/*.jpg".format(path=path)
        self.src_files.extend(glob.glob(mask))
        mask = "{path}/*.bmp".format(path=path)
        self.src_files.extend(glob.glob(mask))
        mask = "{path}/*/*.bmp".format(path=path)
        self.src_files.extend(glob.glob(mask))
        mask = "{path}/*.jpeg".format(path=path)
        self.src_files.extend(glob.glob(mask))
        mask = "{path}/*/*.jpeg".format(path=path)
        self.src_files.extend(glob.glob(mask))
        print(self.src_files)
        self.add2log("Список файлов: {}".format(self.src_files))

    def im_load(self, name):
        f = open(name, "rb")
        chunk = f.read()
        chunk_arr = np.frombuffer(chunk, dtype=np.uint8)
        img = cv2.imdecode(chunk_arr, cv2.IMREAD_COLOR)
        f.close()
        return img

    def recognize(self):
        """
        return total_forms, not_recognized
        """
        self.batches[ScanManager.NOT_RECOGNIZED_FORM_NAME] = []
        print("Recognizing form numbers")
        for im_name in self.src_files:
            self.add2log("Распознавание изображения: {}".format(im_name))
            image_np = self.im_load(im_name)
            orig_im = image_np.copy()
            image_np, turned = align_form(image_np)
            if turned != 0:
                f = open(im_name, "wb")
                orig_im = imutils.rotate_bound(orig_im, turned)
                chunk_arr = cv2.imencode('.jpg', orig_im)[1]
                chunk = chunk_arr.tobytes()
                f.write(chunk)
                f.close()
            number = self._code_recognizer.recognize_code(image_np)
            if number is None:
                self.add2log("[WARNING] Номер бланка не распознан.")
                self.batches[ScanManager.NOT_RECOGNIZED_FORM_NAME].append(
                    im_name)
            elif type(number) == int:
                self.add2log("Распознанный номер бланка: {}".format(number))
                if number not in self.batches.keys():
                    self.batches[number] = []
                self.batches[number].append(im_name)
            elif type(number) == str:
                self.add2log("Номер бланка распознан не полностью: {}".format(number))
                self.batches[ScanManager.NOT_RECOGNIZED_FORM_NAME].append(
                    im_name)
            self.add2log("-----------------------------------------")

        return len(self.src_files), len(self.batches[ScanManager.NOT_RECOGNIZED_FORM_NAME])

    def is_has_unrecognized(self):
        return len(self.batches[ScanManager.NOT_RECOGNIZED_FORM_NAME])>0

    def get_count_unrecognized(self):
        return len(self.batches[ScanManager.NOT_RECOGNIZED_FORM_NAME])

    def get_all_codes(self):
        def key_cast(k):
            try:
                return int(k)
            except Exception:
                return 0
        k_list = list(self.batches.keys())
        k_list.sort(key=key_cast)
        return k_list

    def get_all_scans_by_code(self, code):
        return self.batches[code]

    def pop_unrecognized(self):
        while len(self.batches[ScanManager.NOT_RECOGNIZED_FORM_NAME])>0:
            yield self.batches[ScanManager.NOT_RECOGNIZED_FORM_NAME].pop()

    def get_single_page_forms(self):
        single_page_forms = []
        for key, pages in self.batches.items():
            if len(pages) == 1:
                single_page_forms.append((key, pages[0]))
        while len(single_page_forms) > 0:
            yield single_page_forms.pop()

    def update_key_for_single_scan(self, old_key, new_key, im_name):
        new_key = int(new_key)
        if old_key == new_key: return
        if new_key not in self.batches.keys():
            self.batches[new_key] = []
        self.batches[old_key].remove(im_name)
        self.batches[new_key].append(im_name)
        if len(self.batches[old_key]) == 0:
            self.batches.pop(old_key)

    def update_key_for_single_page_form(self, old_key, new_key):
        if old_key == new_key: return
        value = self.batches.pop(old_key)
        if new_key not in self.batches.keys():
            self.batches[new_key] = []
        self.batches[new_key].extend(value)

    def add_handrecognized(self, number, im_name):
        self.add2log("Задан номер {} для бланка {}".format(number, im_name))
        if number not in self.batches.keys():
            self.batches[number] = []
        self.batches[number].append(im_name)

    def save_to_dateset(self, code, im_name_list):
        while len(code)< 5:
            code = '0'+code
        for im_name in im_name_list:
            image_np = self.im_load(im_name)
            if image_np is None:
                continue
            image_np, _ = align_form(image_np)
            if image_np is None:
                continue
            image_np = self._code_recognizer.get_code(image_np)
            if image_np is None:
                continue
            digits = self._code_recognizer.split_code(image_np)
            for i, d in enumerate(digits):
                print('./raw_dataset/'+str(code[i])+'/'+str(random.randint(10000,10000000))+'.jpg')
                cv2.imwrite('./raw_dataset/'+str(code[i])+'/'+str(random.randint(10000,10000000))+'.jpg', d)

    def save_results(self):
        print("Saving results to pdfs'")
        self.add2log("Сохранение работ в pdf")
        for im_id, im_name_list in self.batches.items():
            #im_full_name_list = []
            #for im_name in im_name_list:
            #    im_full_name_list.append(os.path.join(self.src_dir, im_name))
            #if im_id != ScanManager.NOT_RECOGNIZED_FORM_NAME:
            #self.save_to_dateset(str(im_id), im_name_list)
            form_saver.save_form_batch(im_name_list, os.path.join(self.dst_dir, str(im_id)+'.pdf'))
