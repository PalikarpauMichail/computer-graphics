import tkinter as tk
from tkinter import ttk
import time
import math

class RasterizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа: Алгоритмы растеризации")
        self.root.geometry("1000x700")

        # --- Параметры ---
        self.scale = 20  # Размер одной клетки (пикселя) в экранных пикселях
        self.grid_width = 40  # Кол-во клеток по ширине (логические координаты)
        self.grid_height = 30 # Кол-во клеток по высоте

        # --- Интерфейс ---
        # Левая панель (Настройки)
        self.controls_frame = tk.Frame(root, width=250, bg="#f0f0f0", padx=10, pady=10)
        self.controls_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Выбор алгоритма
        tk.Label(self.controls_frame, text="Алгоритм:", bg="#f0f0f0").pack(anchor="w")
        self.algo_var = tk.StringVar(value="step")
        algos = [
            ("Пошаговый алгоритм", "step"),
            ("ЦДА (DDA)", "dda"),
            ("Брезенхем (Линия)", "bresenham_line"),
            ("Брезенхем (Окружность)", "bresenham_circle")
        ]
        for text, val in algos:
            tk.Radiobutton(self.controls_frame, text=text, variable=self.algo_var, value=val, command=self.update_inputs, bg="#f0f0f0").pack(anchor="w")

        # Координаты
        tk.Label(self.controls_frame, text="Координаты:", bg="#f0f0f0").pack(anchor="w", pady=(10, 0))
        
        self.inputs_frame = tk.Frame(self.controls_frame, bg="#f0f0f0")
        self.inputs_frame.pack(anchor="w")

        # Поля ввода (динамические)
        self.entries = {}
        self.create_input_fields()

        # Масштаб
        tk.Label(self.controls_frame, text="Масштаб сетки:", bg="#f0f0f0").pack(anchor="w", pady=(10, 0))
        self.scale_slider = tk.Scale(self.controls_frame, from_=5, to=50, orient=tk.HORIZONTAL, command=self.on_scale_change)
        self.scale_slider.set(self.scale)
        self.scale_slider.pack(fill=tk.X)

        # Кнопки
        tk.Button(self.controls_frame, text="Построить", command=self.draw, bg="#4caf50", fg="white").pack(fill=tk.X, pady=10)
        tk.Button(self.controls_frame, text="Очистить", command=self.clear_canvas).pack(fill=tk.X)

        # Лог вычислений и времени
        tk.Label(self.controls_frame, text="Отчет / Вычисления:", bg="#f0f0f0").pack(anchor="w", pady=(10, 0))
        self.log_text = tk.Text(self.controls_frame, height=15, width=30, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Правая панель (Canvas)
        self.canvas_frame = tk.Frame(root, bg="white")
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Привязка событий отрисовки сетки
        self.canvas.bind("<Configure>", self.refresh_grid)
        
        self.update_inputs()

    def create_input_fields(self):
        # Очистка старых полей
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()
        self.entries = {}
        
        mode = self.algo_var.get()
        
        if mode == "bresenham_circle":
            fields = [("X центра", "0"), ("Y центра", "0"), ("Радиус", "10")]
            keys = ["x1", "y1", "r"]
        else:
            fields = [("X1", "-15"), ("Y1", "0"), ("X2", "15"), ("Y2", "3")]
            keys = ["x1", "y1", "x2", "y2"]

        for i, (label_text, default) in enumerate(fields):
            tk.Label(self.inputs_frame, text=label_text, bg="#f0f0f0").grid(row=i, column=0, sticky="e")
            entry = tk.Entry(self.inputs_frame, width=10)
            entry.insert(0, default)
            entry.grid(row=i, column=1)
            self.entries[keys[i]] = entry

    def update_inputs(self):
        self.create_input_fields()
        self.log_text.delete(1.0, tk.END)

    def on_scale_change(self, val):
        self.scale = int(val)
        self.refresh_grid()

    def refresh_grid(self, event=None):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Центр координат (экранный)
        cx, cy = w // 2, h // 2

        # Рисуем сетку
        # Вертикальные линии
        for i in range(0, cx, self.scale):
            self.canvas.create_line(cx + i, 0, cx + i, h, fill="#e0e0e0")
            self.canvas.create_line(cx - i, 0, cx - i, h, fill="#e0e0e0")
        # Горизонтальные линии
        for i in range(0, cy, self.scale):
            self.canvas.create_line(0, cy + i, w, cy + i, fill="#e0e0e0")
            self.canvas.create_line(0, cy - i, w, cy - i, fill="#e0e0e0")

        # Оси (пожирнее)
        self.canvas.create_line(cx, 0, cx, h, width=2, fill="black") # Y
        self.canvas.create_line(0, cy, w, cy, width=2, fill="black") # X
        
        # Подписи осей
        self.canvas.create_text(w-10, cy+15, text="X", font=("Arial", 12, "bold"))
        self.canvas.create_text(cx+15, 10, text="Y", font=("Arial", 12, "bold"))

        # Подписи координат (каждые 5 клеток)
        step = 5
        for i in range(step, int(cx/self.scale), step):
            # Ось X
            self.canvas.create_text(cx + i*self.scale, cy + 15, text=str(i), font=("Arial", 8))
            self.canvas.create_text(cx - i*self.scale, cy + 15, text=str(-i), font=("Arial", 8))
        for i in range(step, int(cy/self.scale), step):
            # Ось Y (обратите внимание, Y на экране растет вниз, но математически вверх)
            self.canvas.create_text(cx + 15, cy - i*self.scale, text=str(i), font=("Arial", 8))
            self.canvas.create_text(cx + 15, cy + i*self.scale, text=str(-i), font=("Arial", 8))

    def to_screen(self, x, y):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        # Y инвертируем, так как на экране Y растет вниз
        return cx + x * self.scale, cy - y * self.scale

    def draw_pixel(self, x, y, color="red"):
        sx, sy = self.to_screen(x, y)
        # Рисуем квадратик вокруг точки
        half = self.scale // 2
        # Чуть меньше клетки, чтобы было видно сетку
        pad = 1
        self.canvas.create_rectangle(sx - half + pad, sy - half + pad, 
                                     sx + half - pad, sy + half - pad, 
                                     fill=color, outline="")

    def clear_canvas(self):
        self.refresh_grid()
        self.log_text.delete(1.0, tk.END)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")

    def draw(self):
        self.refresh_grid()
        self.log_text.delete(1.0, tk.END)
        
        algo = self.algo_var.get()
        
        try:
            # Считывание параметров
            if algo == "bresenham_circle":
                x1 = int(self.entries["x1"].get())
                y1 = int(self.entries["y1"].get())
                r = int(self.entries["r"].get())
                params = (x1, y1, r)
            else:
                x1 = int(self.entries["x1"].get())
                y1 = int(self.entries["y1"].get())
                x2 = int(self.entries["x2"].get())
                y2 = int(self.entries["y2"].get())
                params = (x1, y1, x2, y2)
        except ValueError:
            self.log("Ошибка: Введите целые числа!")
            return

        # Замер времени
        start_time = time.perf_counter_ns()
        
        points = []
        logs = []
        
        if algo == "step":
            points, logs = self.algo_step(*params)
        elif algo == "dda":
            points, logs = self.algo_dda(*params)
        elif algo == "bresenham_line":
            points, logs = self.algo_bresenham_line(*params)
        elif algo == "bresenham_circle":
            points, logs = self.algo_bresenham_circle(*params)
            
        end_time = time.perf_counter_ns()
        duration_us = (end_time - start_time) / 1000.0  # в микросекундах
        
        # Отрисовка
        for px, py in points:
            self.draw_pixel(px, py)
            
        # Вывод логов
        self.log(f"Время выполнения: {duration_us:.3f} мкс")
        self.log(f"Количество пикселей: {len(points)}")
        self.log("-" * 20)
        self.log("ХОД ВЫЧИСЛЕНИЙ (первые 15 шагов):")
        for line in logs[:15]:
            self.log(line)
        if len(logs) > 15:
            self.log("...")

    # --- АЛГОРИТМЫ ---

    def algo_step(self, x1, y1, x2, y2):
        points = []
        logs = []
        
        if x1 == x2 and y1 == y2:
            return [(x1, y1)], ["Точка совпадает"]
        
        dx = x2 - x1
        dy = y2 - y1
        
        step_count = max(abs(dx), abs(dy))
        
        logs.append(f"dx={dx}, dy={dy}, steps={step_count}")

        # Простой пошаговый (на основе y = kx + b или наоборот)
        # Для корректной работы при крутых наклонах меняем местами оси
        if abs(dx) >= abs(dy):
            # Идем по X
            k = dy / dx if dx != 0 else 0
            b = y1 - k * x1
            start = min(x1, x2)
            end = max(x1, x2)
            
            # Если x1 > x2, надо идти в обратную сторону для правильного порядка логов,
            # но для set пикселей не важно. Для лога лучше идти от x1 к x2
            step = 1 if x2 > x1 else -1
            for x in range(x1, x2 + step, step):
                y = k * x + b
                y_round = round(y)
                points.append((x, y_round))
                logs.append(f"x={x}: y={y:.2f} -> {y_round}")
        else:
            # Идем по Y
            k = dx / dy if dy != 0 else 0
            b = x1 - k * y1
            step = 1 if y2 > y1 else -1
            for y in range(y1, y2 + step, step):
                x = k * y + b
                x_round = round(x)
                points.append((x_round, y))
                logs.append(f"y={y}: x={x:.2f} -> {x_round}")
                
        return points, logs

    def algo_dda(self, x1, y1, x2, y2):
        points = []
        logs = []
        
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        
        if steps == 0:
            return [(x1, y1)], ["Точка"]

        x_inc = dx / steps
        y_inc = dy / steps
        
        x = x1
        y = y1
        
        logs.append(f"dx={dx}, dy={dy}, steps={steps}")
        logs.append(f"x_inc={x_inc:.2f}, y_inc={y_inc:.2f}")

        for i in range(steps + 1):
            points.append((round(x), round(y)))
            logs.append(f"Шаг {i}: x={x:.2f}, y={y:.2f} -> ({round(x)}, {round(y)})")
            x += x_inc
            y += y_inc
            
        return points, logs

    def algo_bresenham_line(self, x1, y1, x2, y2):
        points = []
        logs = []
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        err = dx - dy
        
        x, y = x1, y1
        
        logs.append(f"dx={dx}, dy={dy}, err={err}")
        
        while True:
            points.append((x, y))
            logs.append(f"Point({x}, {y}), err={err}")
            
            if x == x2 and y == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
                
        return points, logs

    def algo_bresenham_circle(self, xc, yc, r):
        points = []
        logs = []
        
        x = 0
        y = r
        d = 3 - 2 * r
        
        logs.append(f"Начало: r={r}, d={d}")
        
        def add_sym_points(cx, cy, x, y, pts):
            # Симметрия для 8 октантов
            p_list = [
                (cx+x, cy+y), (cx-x, cy+y), (cx+x, cy-y), (cx-x, cy-y),
                (cx+y, cy+x), (cx-y, cy+x), (cx+y, cy-x), (cx-y, cy-x)
            ]
            for p in p_list:
                pts.append(p)
        
        while y >= x:
            add_sym_points(xc, yc, x, y, points)
            logs.append(f"x={x}, y={y}, d={d}")
            
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
                
        # Удаляем дубликаты (они могут быть на диагоналях)
        points = list(set(points)) 
        return points, logs

if __name__ == "__main__":
    root = tk.Tk()
    app = RasterizationApp(root)
    root.mainloop()