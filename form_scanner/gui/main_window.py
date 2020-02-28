import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from tkinter import filedialog, Listbox
import tkinter.font as tkFont
import tkinter.scrolledtext as tkst
from PIL import Image, ImageTk

from scan_manager import ScanManager


import gui.tkSimpleDialog

def validate_code(code):
    try:
        number = int(code)
        if (number > 9999 and number < 1000000) or number == 0:
            return True
        else:
            messagebox.showwarning(
                "Bad input",
                "Номер бланка должен быть пятизначным числом"
            )
            return False
    except ValueError:
        messagebox.showwarning(
            "Bad input",
            "Номер бланка должен быть числом"
        )
        return False

class CheckWindow(tk.Frame):
    def __init__(self, scan_manager, master=None):
        super().__init__(master)
        self._scan_manager = scan_manager

        self.master = master
        self.master.title("Проверка результатов")
        self.pack(fill=tk.BOTH, expand=1)
        self.create_widgets()
        self.update_forms_list()


    def update_item(self):
        new_code = self._code_entry.get()
        if validate_code(new_code):
            new_code = int(new_code)
            old_code = self._lbox_forms.get(self._lbox_forms.curselection()[0])
            try:
                old_code = int(old_code)
            except Exception:
                pass

            im_name = self._lbox_scans.get(int(self._lbox_scans.curselection()[0]))
            self._scan_manager.update_key_for_single_scan(old_code, new_code, im_name)
            self.update_forms_list()
            self._code_entry.delete(0, tk.END)

    def update_forms_list(self):
        try:
            old_selection = int(self._lbox_forms.curselection()[0])
        except Exception:
            old_selection = 0

        self._lbox_forms.delete(0, tk.END)
        for code in self._scan_manager.get_all_codes():
            self._lbox_forms.insert(tk.END, code)

        if old_selection < self._lbox_forms.size():
            self._lbox_forms.select_set(old_selection)
        else:
            self._lbox_forms.select_set(0)

        code = self._lbox_forms.get(int(self._lbox_forms.curselection()[0]))
        try:
            code = int(code)
        except Exception:
            pass
        self.update_scans_list(code)

    def update_scans_list(self, code):
        self._lbox_scans.delete(0, tk.END)
        for im_path in self._scan_manager.get_all_scans_by_code(code):
            self._lbox_scans.insert(tk.END, im_path)
        self._lbox_scans.select_set(0)

        if self._lbox_scans.size()>0:
            im_path = self._lbox_scans.get(int(self._lbox_scans.curselection()[0]))
            self.update_preview(im_path)

    def update_preview(self, im_path):
        load = Image.open(im_path)
        load = load.resize((int(self.im_width), int(self.im_height)))
        self._render = ImageTk.PhotoImage(load)
        self.img['image'] = self._render
        self.img.update()
        #self.update_idletasks()
        #self.img.grid(row=0, column=0)
        #self._code_entry.delete(0, tk.END)
        #self._code_entry.insert(0, current_code)

    def _on_form_select(self, evt):
        w = evt.widget
        try:
            index = int(w.curselection()[0])
            value = w.get(index)
            self.update_scans_list(value)
        except Exception:
            pass

    def _on_scan_select(self, evt):
        w = evt.widget
        try:
            index = int(w.curselection()[0])
            value = w.get(index)
            self.update_preview(value)
        except Exception as e:
            pass
            #print(e)

    def create_widgets(self):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        self.master.resizable(False, False)
        self.im_height = int(screen_height * 0.75)
        self.im_width = int(self.im_height / (2**(1/2)))
        w = int(screen_width * 0.75)
        h = self.im_height + 150
        self.master.geometry("{}x{}".format(w, h))

        frame_lbox_forms = tk.LabelFrame(self, width=w//6, text='Номера бланков')
        frame_lbox_forms.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        lbox_forms = tk.Listbox(frame_lbox_forms, selectmode=tk.SINGLE, exportselection=0)
        lbox_forms.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        lbox_forms.bind('<<ListboxSelect>>', self._on_form_select)
        scroll = tk.Scrollbar(frame_lbox_forms, command=lbox_forms.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        lbox_forms.config(yscrollcommand=scroll.set)
        self._lbox_forms = lbox_forms

        frame_lbox_scans = tk.LabelFrame(self, width=4*w//6, text='Список изображений')
        frame_lbox_scans.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        lbox_scans = tk.Listbox(frame_lbox_scans, selectmode=tk.SINGLE, exportselection=0)
        lbox_scans.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        lbox_scans.bind('<<ListboxSelect>>', self._on_scan_select)
        scroll = tk.Scrollbar(frame_lbox_scans, command=lbox_scans.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        lbox_scans.config(yscrollcommand=scroll.set)
        self._lbox_scans = lbox_scans

        frame_edit_image = tk.LabelFrame(self, width=w//3, text='Редактирование')
        frame_edit_image.pack(fill=tk.BOTH, expand=1)
        self.img = tk.Label(frame_edit_image, height=self.im_height, width=self.im_width)
        self.img.grid(row=0, column=0)
        fontStyle = tkFont.Font(family="Lucida Grande", size=20)
        self._code_entry = tk.Entry(frame_edit_image, font=fontStyle, justify="center", width=6)
        self._code_entry.grid(row=1, column=0)
        b_update = tk.Button(frame_edit_image, text="Обновить номер", command=self.update_item)
        b_update.grid(row=2, column=0)


class HandRecognizeDialog(gui.tkSimpleDialog.Dialog):
    def __init__(self, image_path, parent, default_value = None, title = None):
        self._image_path = image_path
        self._default_value = default_value
        gui.tkSimpleDialog.Dialog.__init__(self, parent, title)


    def rotate_image(self):
        screen_width = self._body.winfo_screenwidth()
        screen_height = self._body.winfo_screenheight()

        load = Image.open(self._image_path)

        w = screen_width//2
        h = int(load.size[1] * (w/load.size[0]))
        load = load.resize((w, h))
        load = load.rotate(180)

        h = load.size[1] // 3
        w = load.size[0]
        load = load.crop((0, 0, w, h))

        self._render = ImageTk.PhotoImage(load)
        self.img['image'] = self._render
        self.img.update()

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

        fontStyle = tkFont.Font(family="Lucida Grande", size=40)
        self.e1 = tk.Entry(master, font=fontStyle, justify="center", width=6)
        if self._default_value is not None:
            self.e1.delete(0, tk.END)
            self.e1.insert(0, self._default_value)
        self.e1.grid(row=2, column=0)

        self.rotate_button = tk.Button(master, text='Перевернуть изображение' ,command=self.rotate_image)
        self.rotate_button.grid(row=1, column=0)

        self.geometry("{}x{}".format(w, h+150))

        self.img = tk.Label(master, image=render)
        self.img.image = render
        self.img.grid(row=0, column=0)

        return self.e1 # initial focus

    def validate(self):
        if validate_code(self.e1.get()):
            self.result = int(self.e1.get())
            return 1
        else:
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
        self._show_result_button['state'] = 'disable'
        self._save_result_button['state'] = 'disable'

        self._scan_manager = ScanManager(src_dir, dst_dir)
        self._scan_manager.set_log_handler(self.add2log)
        self._scan_manager.recognize()

        if self._scan_manager.is_has_unrecognized():
            messagebox.showinfo(
                    "Ручное распознаванеи",
                    "Часть бланков не удалось распознать. \n Введине номера вручную."
                )
            # Ручное распознавание нераспознанных
            total_ims = self._scan_manager.get_count_unrecognized()
            current_img = 0
            for im_path in self._scan_manager.pop_unrecognized():
                current_img += 1
                d = HandRecognizeDialog(im_path, self.master, title="Введите номер, {}/{}".format(current_img, total_ims))
                self._scan_manager.add_handrecognized(d.result, im_path)

        messagebox.showinfo(
                "Проверка",
                "Проверьте бланки с возможными ошибками."
            )

        # Проверка распознавания пачек с 1 изображением
        for key, im_path in self._scan_manager.get_single_page_forms():
            d = HandRecognizeDialog(im_path, self.master, default_value=key, title="Проверьте распознавание, возможна ошибка")
            new_key = d.result
            self._scan_manager.update_key_for_single_page_form(key, new_key)

        self._start_processing_button['state'] = 'active'
        self._show_result_button['state'] = 'active'
        self._save_result_button['state'] = 'active'


    def show_results(self):
        w = tk.Toplevel(self)
        checkWindow = CheckWindow(scan_manager=self._scan_manager, master=w)

    def save_results(self):
        self._scan_manager.save_results()
        messagebox.showinfo(
                "Финиш",
                "Все бланки распознаны и сохранены в PDF."
            )

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

        lbl5 = tk.Button(frame3, text="Сохранить в PDF", command=self.save_results)
        lbl5.pack(side=tk.RIGHT, anchor=tk.N, padx=5, pady=5)
        self._save_result_button = lbl5
        self._save_result_button['state'] = 'disable'

        lbl4 = tk.Button(frame3, text="Результат", command=self.show_results)
        lbl4.pack(side=tk.RIGHT, anchor=tk.N, padx=5, pady=5)
        self._show_result_button = lbl4
        self._show_result_button['state'] = 'disable'

        lbl3 = tk.Button(frame3, text="Начать обработку", command=self.start_proccessing)
        lbl3.pack(side=tk.RIGHT, anchor=tk.N, padx=5, pady=5)
        self._start_processing_button = lbl3





        self._log_text = tkst.ScrolledText(self)
        #self._log_text = tk.Text(self)
        self._log_text.pack(side=tk.LEFT)
