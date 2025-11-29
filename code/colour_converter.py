import tkinter as tk
from tkinter import ttk, colorchooser
import colorsys

class ColorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Model Converter (RGB <-> CMYK <-> HSV/HLS)")
        self.root.geometry("900x500")

        # Флаг для предотвращения бесконечного цикла обновлений
        self.is_updating = False

        # --- Переменные хранения состояния ---
        # RGB (0-255)
        self.r_var = tk.IntVar(value=0)
        self.g_var = tk.IntVar(value=128)
        self.b_var = tk.IntVar(value=255)

        # CMYK (0-100)
        self.c_var = tk.DoubleVar()
        self.m_var = tk.DoubleVar()
        self.y_var = tk.DoubleVar()
        self.k_var = tk.DoubleVar()

        # HSV (H: 0-360, S: 0-100, V: 0-100)
        # Если нужен вариант HLS, логика будет аналогичной, меняются только формулы
        self.h_var = tk.DoubleVar()
        self.s_var = tk.DoubleVar()
        self.v_var = tk.DoubleVar()

        # --- Интерфейс ---
        self._create_ui()

        # Первоначальный просчет всех моделей на основе дефолтного RGB
        self.update_from_rgb()

        # --- Привязка событий (Traces) ---
        # При изменении любой переменной вызывается соответствующая функция
        self.r_var.trace_add("write", lambda *args: self.on_rgb_change())
        self.g_var.trace_add("write", lambda *args: self.on_rgb_change())
        self.b_var.trace_add("write", lambda *args: self.on_rgb_change())

        self.c_var.trace_add("write", lambda *args: self.on_cmyk_change())
        self.m_var.trace_add("write", lambda *args: self.on_cmyk_change())
        self.y_var.trace_add("write", lambda *args: self.on_cmyk_change())
        self.k_var.trace_add("write", lambda *args: self.on_cmyk_change())

        self.h_var.trace_add("write", lambda *args: self.on_hsv_change())
        self.s_var.trace_add("write", lambda *args: self.on_hsv_change())
        self.v_var.trace_add("write", lambda *args: self.on_hsv_change())

    def _create_ui(self):
        # Верхняя панель: Цвет и Палитра
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        self.color_preview = tk.Label(top_frame, bg="blue", width=20, height=5, relief="sunken")
        self.color_preview.pack(side=tk.LEFT, padx=10)

        btn_palette = ttk.Button(top_frame, text="Выбрать из палитры", command=self.choose_color_dialog)
        btn_palette.pack(side=tk.LEFT, padx=10)

        # Основная панель с 3 колонками
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Колонки
        col1 = ttk.LabelFrame(main_frame, text="RGB (0-255)", padding="10")
        col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        col2 = ttk.LabelFrame(main_frame, text="CMYK (0-100%)", padding="10")
        col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # ВАЖНО: Для нечетного варианта измените заголовок на HLS
        col3 = ttk.LabelFrame(main_frame, text="HSV (H:0-360, S/V:0-100)", padding="10")
        col3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Генерация контролов
        self._build_slider_group(col1, "Red", self.r_var, 0, 255)
        self._build_slider_group(col1, "Green", self.g_var, 0, 255)
        self._build_slider_group(col1, "Blue", self.b_var, 0, 255)

        self._build_slider_group(col2, "Cyan", self.c_var, 0, 100)
        self._build_slider_group(col2, "Magenta", self.m_var, 0, 100)
        self._build_slider_group(col2, "Yellow", self.y_var, 0, 100)
        self._build_slider_group(col2, "Key (Black)", self.k_var, 0, 100)

        self._build_slider_group(col3, "Hue", self.h_var, 0, 360)
        self._build_slider_group(col3, "Saturation", self.s_var, 0, 100)
        # Для нечетного варианта (HLS) замените "Value" на "Lightness"
        self._build_slider_group(col3, "Value", self.v_var, 0, 100) 

    def _build_slider_group(self, parent, label_text, variable, min_val, max_val):
        """Вспомогательный метод для создания тройки: Лейбл - Энтри - Слайдер"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        lbl = ttk.Label(frame, text=label_text, width=10)
        lbl.pack(side=tk.LEFT)
        
        # Поле ввода
        entry = ttk.Entry(frame, textvariable=variable, width=5)
        entry.pack(side=tk.LEFT, padx=5)
        
        # Ползунок
        scale = ttk.Scale(frame, from_=min_val, to=max_val, variable=variable, orient=tk.HORIZONTAL)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    # --- Логика конвертации ---

    def rgb_to_hex(self, r, g, b):
        return f'#{r:02x}{g:02x}{b:02x}'

    def update_preview(self, r, g, b):
        hex_color = self.rgb_to_hex(r, g, b)
        try:
            self.color_preview.config(bg=hex_color)
        except:
            pass

    def choose_color_dialog(self):
        # Открывает стандартную палитру
        color = colorchooser.askcolor(title="Выберите цвет")
        if color[0]:
            r, g, b = map(int, color[0])
            self.r_var.set(r)
            self.g_var.set(g)
            self.b_var.set(b)
            # Trace сам вызовет обновление остальных моделей

    # --- Обработчики событий ---

    def on_rgb_change(self):
        if self.is_updating: return
        self.is_updating = True
        try:
            self.update_from_rgb()
        except Exception as e:
            print(f"Error in RGB calc: {e}")
        self.is_updating = False

    def on_cmyk_change(self):
        if self.is_updating: return
        self.is_updating = True
        try:
            self.update_from_cmyk()
        except Exception as e:
            print(f"Error in CMYK calc: {e}")
        self.is_updating = False

    def on_hsv_change(self):
        if self.is_updating: return
        self.is_updating = True
        try:
            self.update_from_hsv()
        except Exception as e:
            print(f"Error in HSV calc: {e}")
        self.is_updating = False

    # --- Основные функции пересчета ---

    def update_from_rgb(self):
        """Источник правды - RGB слайдеры. Обновляем CMYK, HSV и превью."""
        # Получаем значения
        r = self._clamp(self.r_var.get(), 0, 255)
        g = self._clamp(self.g_var.get(), 0, 255)
        b = self._clamp(self.b_var.get(), 0, 255)
        
        # Обновляем превью
        self.update_preview(int(r), int(g), int(b))

        # 1. RGB -> CMYK
        # Нормализуем 0..1
        rn, gn, bn = r/255, g/255, b/255
        k = 1 - max(rn, gn, bn)
        if k == 1:
            c = m = y = 0
        else:
            c = (1 - rn - k) / (1 - k)
            m = (1 - gn - k) / (1 - k)
            y = (1 - bn - k) / (1 - k)
        
        self.c_var.set(round(c * 100, 2))
        self.m_var.set(round(m * 100, 2))
        self.y_var.set(round(y * 100, 2))
        self.k_var.set(round(k * 100, 2))

        # 2. RGB -> HSV (Четный вариант)
        h, s, v = colorsys.rgb_to_hsv(rn, gn, bn)
        self.h_var.set(round(h * 360, 2))
        self.s_var.set(round(s * 100, 2))
        self.v_var.set(round(v * 100, 2))

        # ЕСЛИ НУЖЕН HLS (Нечетный вариант):
        # h, l, s_hls = colorsys.rgb_to_hls(rn, gn, bn)
        # self.h_var.set(round(h * 360, 2))
        # self.v_var.set(round(l * 100, 2)) # Тут L пишем в v_var для простоты UI
        # self.s_var.set(round(s_hls * 100, 2))

    def update_from_cmyk(self):
        """Источник правды - CMYK слайдеры. Обновляем RGB, затем HSV."""
        c = self.c_var.get() / 100
        m = self.m_var.get() / 100
        y = self.y_var.get() / 100
        k = self.k_var.get() / 100

        # CMYK -> RGB
        r = 255 * (1 - c) * (1 - k)
        g = 255 * (1 - m) * (1 - k)
        b = 255 * (1 - y) * (1 - k)

        # Ставим в RGB переменные (это НЕ вызовет on_rgb_change из-за флага is_updating)
        self.r_var.set(int(r))
        self.g_var.set(int(g))
        self.b_var.set(int(b))

        self.update_preview(int(r), int(g), int(b))

        # Теперь обновляем 3-ю модель (HSV) на основе нового RGB
        rn, gn, bn = r/255, g/255, b/255
        h, s, v = colorsys.rgb_to_hsv(rn, gn, bn)
        self.h_var.set(round(h * 360, 2))
        self.s_var.set(round(s * 100, 2))
        self.v_var.set(round(v * 100, 2))
        # См. выше комментарий про HLS

    def update_from_hsv(self):
        """Источник правды - HSV слайдеры. Обновляем RGB, затем CMYK."""
        h = self.h_var.get() / 360
        s = self.s_var.get() / 100
        v = self.v_var.get() / 100

        # HSV -> RGB
        rn, gn, bn = colorsys.hsv_to_rgb(h, s, v)
        # ДЛЯ HLS: rn, gn, bn = colorsys.hls_to_rgb(h, v, s) # Обратите внимание на порядок v=L

        r, g, b = rn * 255, gn * 255, bn * 255
        
        self.r_var.set(int(r))
        self.g_var.set(int(g))
        self.b_var.set(int(b))

        self.update_preview(int(r), int(g), int(b))

        # Теперь обновляем CMYK на основе нового RGB
        k = 1 - max(rn, gn, bn)
        if k == 1:
            c = m = y = 0
        else:
            c = (1 - rn - k) / (1 - k)
            m = (1 - gn - k) / (1 - k)
            y = (1 - bn - k) / (1 - k)
        
        self.c_var.set(round(c * 100, 2))
        self.m_var.set(round(m * 100, 2))
        self.y_var.set(round(y * 100, 2))
        self.k_var.set(round(k * 100, 2))

    def _clamp(self, val, min_v, max_v):
        try:
            val = float(val)
        except ValueError:
            return min_v
        return max(min(val, max_v), min_v)

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorApp(root)
    root.mainloop()