import matplotlib.pyplot as plt
import matplotlib.patches as patches


def read_input(filename='input.txt'):
    with open(filename, 'r') as f:
        lines = f.readlines()

    lines = [l.strip() for l in lines if l.strip()]
    
    n = int(lines[0])
    
    segments = []
    current_line_idx = 1
    
    for _ in range(n):
        parts = list(map(float, lines[current_line_idx].split()))
        segments.append(parts) # [x1, y1, x2, y2]
        current_line_idx += 1

    window_coords = list(map(float, lines[current_line_idx].split()))
    # Xmin, Ymin, Xmax, Ymax
    
    return segments, window_coords


def liang_barsky_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    t0 = 0.0
    t1 = 1.0
    dx = x2 - x1
    dy = y2 - y1
    
    checks = ((-dx, x1 - xmin), 
              (dx, xmax - x1), 
              (-dy, y1 - ymin), 
              (dy, ymax - y1))
    
    for p, q in checks:
        if p == 0:
            if q < 0:
                return None  # Параллельна и снаружи
        else:
            t = q / p
            if p < 0:
                if t > t1: return None
                if t > t0: t0 = t
            else:
                if t < t0: return None
                if t < t1: t1 = t
                
    if t0 <= t1:
        nx1 = x1 + t0 * dx
        ny1 = y1 + t0 * dy
        nx2 = x1 + t1 * dx
        ny2 = y1 + t1 * dy
        return (nx1, ny1, nx2, ny2)
    
    return None


def cyrus_beck_clip(x1, y1, x2, y2, poly_points):
    t0 = 0.0 # Вход
    t1 = 1.0 # Выход
    dx = x2 - x1
    dy = y2 - y1
    
    n = len(poly_points)
    
    for i in range(n):
        p1 = poly_points[i]
        p2 = poly_points[(i + 1) % n]
        
        # Вектор грани
        edge_x = p2[0] - p1[0]
        edge_y = p2[1] - p1[1]
        
        # Внутренняя нормаль для CCW обхода: (-edge_y, edge_x)
        nx = -edge_y
        ny = edge_x
        
        # Вектор W = P_line - P_edge
        wx = x1 - p1[0]
        wy = y1 - p1[1]
        
        # Скалярные произведения
        dn = dx * nx + dy * ny        # Dir * Normal
        wn = wx * nx + wy * ny        # W * Normal
        
        # Если dn == 0, отрезок параллелен грани
        if dn == 0:
            # Если wn < 0, то точка снаружи (с внешней стороны нормали)
            if wn < 0:
                return None
        else:
            t = -(wn) / dn
            
            if dn > 0: 
                # Отрезок направлен по направлению внутренней нормали -> ВХОДИТ
                # Ищем максимум среди входов
                if t > t0:
                    t0 = t
            else:
                # Отрезок направлен против внутренней нормали -> ВЫХОДИТ
                # Ищем минимум среди выходов
                if t < t1:
                    t1 = t
                    
    # Проверка валидности интервала
    if t0 <= t1:
        nx1 = x1 + t0 * dx
        ny1 = y1 + t0 * dy
        nx2 = x1 + t1 * dx
        ny2 = y1 + t1 * dy
        
        # Дополнительная проверка на случай ошибок плавающей точки:
        # убедимся, что полученный отрезок не вырожден
        if (abs(nx1-nx2) > 1e-9 or abs(ny1-ny2) > 1e-9):
            return (nx1, ny1, nx2, ny2)
            
    return None


def plot_scene(segments, window_coords):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    xmin, ymin, xmax, ymax = window_coords
    
    # --- Сцена 1: Лианг-Барски (Прямоугольник) ---
    ax1 = axes[0]
    ax1.set_title("Часть 1: Алгоритм Лианга-Барски (Вариант 14)")
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # Рисуем окно (синим)
    rect = patches.Rectangle((xmin, ymin), xmax-xmin, ymax-ymin, 
                             linewidth=2, edgecolor='blue', facecolor='none', label='Окно отсечения')
    ax1.add_patch(rect)
    
    # Рисуем отрезки
    for seg in segments:
        x1, y1, x2, y2 = seg
        # Исходный (серый, пунктир)
        ax1.plot([x1, x2], [y1, y2], 'gray', linestyle='--', alpha=0.5)
        
        # Отсечение
        clipped = liang_barsky_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax)
        if clipped:
            cx1, cy1, cx2, cy2 = clipped
            ax1.plot([cx1, cx2], [cy1, cy2], 'red', linewidth=2, marker='o', markersize=4)

    ax1.legend()

    # --- Сцена 2: Отсечение Выпуклым Многоугольником ---
    ax2 = axes[1]
    ax2.set_title("Часть 2: Отсечение выпуклым многоугольником\n(Кирус-Бек, Вариант 14)")
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    poly_verts = [(5, 1), (9, 5), (5, 9), (1, 5)]
    
    poly_patch = patches.Polygon(poly_verts, closed=True, linewidth=2, 
                                 edgecolor='green', facecolor='none', label='Многоугольник')
    ax2.add_patch(poly_patch)
    
    for seg in segments:
        x1, y1, x2, y2 = seg
        # Исходный
        ax2.plot([x1, x2], [y1, y2], 'gray', linestyle='--', alpha=0.5)
        
        # Отсечение
        clipped = cyrus_beck_clip(x1, y1, x2, y2, poly_verts)
        if clipped:
            cx1, cy1, cx2, cy2 = clipped
            ax2.plot([cx1, cx2], [cy1, cy2], 'orange', linewidth=2, marker='o', markersize=4)
            
    ax2.legend()
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    segs, win = read_input()

    print(f"Окно отсечения: {win}")
    print(f"Всего отрезков: {len(segs)}")
    
    plot_scene(segs, win)