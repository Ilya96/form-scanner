import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from tkinter import filedialog
import tkinter.scrolledtext as tkst
from PIL import Image, ImageTk

from scan_manager import ScanManager


import gui.tkSimpleDialog

class HandRecognizeDialog(gui.tkSimpleDialog.Dialog):
    def __init__(self, image_path, parent, title = None):
        self._image_path = image_path
        gui.tkSimpleDialog.Dialog.__init__(self, parent, title)

    def body(self, master):


        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        load = Image.open(self._image_path)

        w = screen_width//2
        h = int(load.size[1] * (w/load.size[0]))
        load = load.resize((w, h))

        h = load.size[1] // 3
        w = load.size[0]
        load = load.crop((0, 0, w, h))

        render = ImageTk.PhotoImage(load)

        self.e1 = tk.Entry(master)
        self.e1.grid(row=1, column=0)
        self.geometry("{}x{}".format(w, h+100))

        self.img = tk.Label(master, image=render)
        self.img.image = render
        self.img.grid(row=0, column=0)

        return self.e1 # initial focus

    def validate(self):
        try:
            number = int(self.e1.get())
            self.result = number
            return 1
        except ValueError:
            messagebox.showwarning(
                "Bad input",
                "Номер бланка должен быть числом"
            )
            return 0

    def apply(self):
        pass


class MainWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self._scan_manager = None

        self.master = master
        self.master.title("Сортировка бланков")
        self.pack()
        self.create_widgets()
        self.add2log("Программа сортировки бланков")

    def request_src_dir(self):
        dir_name =  filedialog.askdirectory(initialdir = ".",title = "Выберите папку с исходными файлами")
        self._src_dir_entry.delete(0, tk.END)
        self._src_dir_entry.insert(0, dir_name)

    def request_dst_dir(self):
        dir_name =  filedialog.askdirectory(initialdir = ".",title = "Выберите папку с исходными файлами")
        self._dst_dir_entry.delete(0, tk.END)
        self._dst_dir_entry.insert(0, dir_name)

    def start_proccessing(self):
        print("start_proccessing")

        src_dir = self._src_dir_entry.get()
        dst_dir = self._dst_dir_entry.get()
        is_error = False
        if not os.path.isdir(src_dir):
            messagebox.showerror("Error", "Не указан путь к папке с оригиналами или путь не является папкой")
            is_error = True
        if not os.path.isdir(dst_dir):
            messagebox.showerror("Error", "Не указан путь к папке назначения или путь не является папкой")
            is_error = True
        if is_error: return

        self._start_processing_button['state'] = 'disable'
        self._scan_manager = ScanManager(src_dir, dst_dir)
        self._scan_manager.set_log_handler(self.add2log)
        self._scan_manager.recognize()


        for im_path in self._scan_manager.pop_unrecognized():
            d = HandRecognizeDialog(im_path, self.master)
            self._scan_manager.add_handrecognized(d.result, im_path)

        self._scan_manager.save_results()

    def add2log(self, text):
        self._log_text.insert(tk.END, datetime.strftime(datetime.now(), "%H:%M:%S") + ": " + text + '\n')
        self._log_text.see('end')
        self._log_text.update()

    def create_widgets(self):

        self.master.resizable(False, False)

        frame1 = tk.Frame(self)
        frame1.pack(fill=tk.X)

        lbl1 = tk.Label(frame1, text="Папка с исходными файлами")
        lbl1.pack(side=tk.LEFT, padx=5, pady=5)

        entry1 = tk.Entry(frame1)
        entry1.pack(fill=tk.X, side=tk.LEFT,padx=5, expand=True)
        self._src_dir_entry = entry1

        chDir_1 = tk.Button(frame1, text='...', command=self.request_src_dir)
        chDir_1.pack(fill=tk.X, padx=5, expand=True)

        frame2 = tk.Frame(self)
        frame2.pack(fill=tk.X)

        lbl2 = tk.Label(frame2, text="Целевая папка")
        lbl2.pack(side=tk.LEFT, padx=5, pady=5)

        entry2 = tk.Entry(frame2)
        entry2.pack(fill=tk.X, side=tk.LEFT,padx=5, expand=True)
        self._dst_dir_entry = entry2

        chDir_2 = tk.Button(frame2, text='...', command=self.request_dst_dir)
        chDir_2.pack(fill=tk.X, padx=5, expand=True)

        frame3 = tk.Frame(self)
        frame3.pack(fill=tk.BOTH, expand=True)

        lbl3 = tk.Button(frame3, text="Начать обработку", command=self.start_proccessing)
        lbl3.pack(side=tk.RIGHT, anchor=tk.N, padx=5, pady=5)
        self._start_processing_button = lbl3

        self._log_text = tkst.ScrolledText(self)
        #self._log_text = tk.Text(self)
        self._log_text.pack(side=tk.LEFT)
