import os
import glob
import cv2
import number_recognizer
import form_saver
from tqdm import tqdm


class ScanManager:
    NOT_RECOGNIZED_FORM_NAME = 'NOT_RECOGNIZED'

    def __init__(self, src_dir, dst_dir):
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.src_files = []
        self.load_dir(src_dir)
        self.prepare_target_dir(dst_dir)
        self.batches = {}

    def prepare_target_dir(self, dst_dir):

        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        if not os.path.exists(os.path.join(dst_dir, ScanManager.NOT_RECOGNIZED_FORM_NAME)):
            os.makedirs(os.path.join(
                dst_dir, ScanManager.NOT_RECOGNIZED_FORM_NAME))

    def load_dir(self, path):
        mask = "{path}/*.jpg".format(path=path)
        self.src_files = glob.glob(mask)

    def im_load(self, name):
        full_name = os.path.join(self.src_dir, name)
        return cv2.imread(full_name)

    def recognize(self):
        """
        return total_forms, not_recognized
        """
        self.batches[ScanManager.NOT_RECOGNIZED_FORM_NAME] = []
        print("Recognizing form numbers")
        for im_name in tqdm(self.src_files):
            image_np = self.im_load(im_name)
            number = number_recognizer.recognize_code(image_np)
            if number is None:
                self.batches[ScanManager.NOT_RECOGNIZED_FORM_NAME].append(
                    im_name)
            else:
                if number not in self.batches.keys():
                    self.batches[number] = []
                self.batches[number].append(im_name)

        return len(self.src_files), len(self.batches[ScanManager.NOT_RECOGNIZED_FORM_NAME])

    def save_results(self):
        print("Saving results to pdfs'")
        for im_id, im_name_list in tqdm(self.batches.items()):
            im_full_name_list = []
            for im_name in im_name_list:
                im_full_name_list.append(os.path.join(self.src_dir, im_name))
            form_saver.save_form_batch(im_full_name_list, im_id)
