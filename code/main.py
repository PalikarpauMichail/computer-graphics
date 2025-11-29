import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk

class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №2 - Вариант 14")
        self.root.geometry("1200x700")

        self.original_image = None
        self.processed_image = None
        self.cv_image = None # Хранение исходника в формате OpenCV

        self._setup_ui()

    def _setup_ui(self):
        # --- Левая панель управления ---
        control_frame = tk.Frame(self.root, width=300, bg="#f0f0f0")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Загрузка
        btn_load = tk.Button(control_frame, text="Загрузить изображение", command=self.load_image, bg="#4CAF50", fg="white")
        btn_load.pack(fill=tk.X, pady=5)

        # --- Блок 1: Локальная пороговая обработка (Строка задания) ---
        lbl_group1 = tk.Label(control_frame, text="1. Локальная пороговая обработка", font=("Arial", 10, "bold"), bg="#f0f0f0")
        lbl_group1.pack(pady=(20, 5))

        self.thresh_method_var = tk.StringVar(value="Mean")
        
        rb_mean = tk.Radiobutton(control_frame, text="Adaptive Mean", variable=self.thresh_method_var, value="Mean", bg="#f0f0f0")
        rb_mean.pack(anchor="w")
        rb_gauss = tk.Radiobutton(control_frame, text="Adaptive Gaussian", variable=self.thresh_method_var, value="Gaussian", bg="#f0f0f0")
        rb_gauss.pack(anchor="w")

        # Параметры для порога
        tk.Label(control_frame, text="Размер блока (нечетное):", bg="#f0f0f0").pack(anchor="w")
        self.slider_block_size = tk.Scale(control_frame, from_=3, to=99, orient=tk.HORIZONTAL)
        self.slider_block_size.set(11)
        self.slider_block_size.pack(fill=tk.X)

        tk.Label(control_frame, text="Константа C:", bg="#f0f0f0").pack(anchor="w")
        self.slider_c = tk.Scale(control_frame, from_=-20, to=20, orient=tk.HORIZONTAL)
        self.slider_c.set(2)
        self.slider_c.pack(fill=tk.X)

        btn_apply_thresh = tk.Button(control_frame, text="Применить порог", command=self.apply_threshold)
        btn_apply_thresh.pack(fill=tk.X, pady=5)

        # --- Блок 2: Сегментация / Выделение границ (Столбец задания) ---
        lbl_group2 = tk.Label(control_frame, text="2. Сегментация (Точки/Линии/Края)", font=("Arial", 10, "bold"), bg="#f0f0f0")
        lbl_group2.pack(pady=(20, 5))

        self.seg_method_var = tk.StringVar(value="Sobel")
        options = ["Sobel", "Canny"]
        self.combo_seg = ttk.Combobox(control_frame, values=options, state="readonly")
        self.combo_seg.current(0)
        self.combo_seg.pack(fill=tk.X, pady=5)

        btn_apply_seg = tk.Button(control_frame, text="Применить фильтр", command=self.apply_segmentation)
        btn_apply_seg.pack(fill=tk.X, pady=5)

        # Кнопка сброса
        btn_reset = tk.Button(control_frame, text="Сбросить", command=self.reset_image, bg="#f44336", fg="white")
        btn_reset.pack(fill=tk.X, pady=(20, 5))

        # --- Правая часть: Отображение ---
        display_frame = tk.Frame(self.root)
        display_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.lbl_original = tk.Label(display_frame, text="Оригинал")
        self.lbl_original.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)

        self.lbl_processed = tk.Label(display_frame, text="Обработано")
        self.lbl_processed.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")])
        if not file_path:
            return
        
        # Читаем изображение в градациях серого (требование большинства алгоритмов)
        self.cv_image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        
        if self.cv_image is None:
            messagebox.showerror("Ошибка", "Не удалось загрузить изображение")
            return

        self.show_image(self.cv_image, self.lbl_original)
        self.show_image(self.cv_image, self.lbl_processed) # Изначально копируем

    def show_image(self, cv_img, label_widget):
        # Конвертация для tkinter
        h, w = cv_img.shape
        img_pil = Image.fromarray(cv_img)
        
        # Ресайз для отображения, если картинка большая
        display_w, display_h = 500, 600
        img_pil.thumbnail((display_w, display_h))
        
        img_tk = ImageTk.PhotoImage(img_pil)
        label_widget.config(image=img_tk, text="")
        label_widget.image = img_tk

    def get_odd_block_size(self):
        # Размер блока должен быть нечетным и > 1
        val = self.slider_block_size.get()
        return val if val % 2 == 1 else val + 1

    def apply_threshold(self):
        if self.cv_image is None:
            return
        
        block_size = self.get_odd_block_size()
        C = self.slider_c.get()
        method_str = self.thresh_method_var.get()
        
        adaptive_method = cv2.ADAPTIVE_THRESH_MEAN_C
        if method_str == "Gaussian":
            adaptive_method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
            
        # Применение адаптивного порога
        # (src, maxValue, adaptiveMethod, thresholdType, blockSize, C)
        processed = cv2.adaptiveThreshold(
            self.cv_image, 
            255, 
            adaptive_method, 
            cv2.THRESH_BINARY, 
            block_size, 
            C
        )
        
        self.show_image(processed, self.lbl_processed)

    def apply_segmentation(self):
        if self.cv_image is None:
            return

        selection = self.combo_seg.get()
        
        blur = cv2.GaussianBlur(self.cv_image, (3, 3), 0)

        if "Sobel" in selection:
            grad_x = cv2.Sobel(blur, cv2.CV_16S, 1, 0, ksize=3)
            grad_y = cv2.Sobel(blur, cv2.CV_16S, 0, 1, ksize=3)
            
            abs_grad_x = cv2.convertScaleAbs(grad_x)
            abs_grad_y = cv2.convertScaleAbs(grad_y)
            
            # Объединяем градиенты (приближенно)
            processed = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
             
        elif "Canny" in selection:
            processed = cv2.Canny(blur, 50, 150)

        self.show_image(processed, self.lbl_processed)

    def reset_image(self):
        if self.cv_image is not None:
            self.show_image(self.cv_image, self.lbl_processed)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()