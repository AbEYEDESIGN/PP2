import pygame
import sys
import math
from datetime import datetime
from collections import deque

pygame.init()

WIDTH, HEIGHT = 900, 600
TOOLBAR_H = 50
CANVAS_H = HEIGHT - TOOLBAR_H

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint TSIS 2")
clock = pygame.time.Clock()

# цвета интерфейса
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GRAY   = (180, 180, 180)
DARK   = (50, 50, 50)

# холст — рисуем на отдельной поверхности, экран только отображает
canvas = pygame.Surface((WIDTH, CANVAS_H))
canvas.fill(WHITE)

font = pygame.font.SysFont("Arial", 14)

# текущий инструмент, цвет, размер кисти
tool     = "pencil"
color    = BLACK
brush_sz = 2   # размеры: 2, 5, 10

# для инструментов с превью (линия, прямоугольник и т.д.)
start_pos = None

# для текстового инструмента
text_mode   = False
text_pos    = None
typed_text  = ""

# для карандаша — запоминаем предыдущую точку чтобы рисовать непрерывную линию
prev_pos = None

# палитра цветов
PALETTE = [
    (0,0,0), (255,255,255), (255,0,0), (0,200,0),
    (0,0,255), (255,255,0), (255,165,0), (128,0,128),
    (0,200,200), (165,42,42), (128,128,128), (255,192,203),
]

def draw_toolbar():
    """рисуем панель инструментов внизу экрана"""
    pygame.draw.rect(screen, GRAY, (0, CANVAS_H, WIDTH, TOOLBAR_H))

    # кнопки инструментов
    tools_list = ["pencil", "line", "rect", "circle", "square",
                  "rtriangle", "etriangle", "rhombus", "fill", "text", "eraser"]
    for i, t in enumerate(tools_list):
        rect = pygame.Rect(5 + i * 70, CANVAS_H + 5, 65, 20)
        col = (100, 200, 100) if t == tool else DARK
        pygame.draw.rect(screen, col, rect)
        label = font.render(t, True, WHITE)
        screen.blit(label, (rect.x + 3, rect.y + 3))

    # кнопки размера кисти
    sizes = [(2, "S"), (5, "M"), (10, "L")]
    for i, (sz, label) in enumerate(sizes):
        rect = pygame.Rect(5 + i * 30, CANVAS_H + 28, 25, 18)
        col = (100, 200, 100) if sz == brush_sz else DARK
        pygame.draw.rect(screen, col, rect)
        t = font.render(label, True, WHITE)
        screen.blit(t, (rect.x + 5, rect.y + 2))

    # палитра
    for i, c in enumerate(PALETTE):
        rect = pygame.Rect(100 + i * 22, CANVAS_H + 28, 20, 18)
        pygame.draw.rect(screen, c, rect)
        if c == color:
            pygame.draw.rect(screen, (255, 0, 0), rect, 2)

    # подсказка ctrl+s
    hint = font.render("Ctrl+S = save", True, DARK)
    screen.blit(hint, (WIDTH - 100, CANVAS_H + 5))


def handle_toolbar_click(mx, my):
    """проверяем кликнул ли пользователь на кнопку в тулбаре"""
    global tool, brush_sz, color

    tools_list = ["pencil", "line", "rect", "circle", "square",
                  "rtriangle", "etriangle", "rhombus", "fill", "text", "eraser"]
    for i, t in enumerate(tools_list):
        rect = pygame.Rect(5 + i * 70, CANVAS_H + 5, 65, 20)
        if rect.collidepoint(mx, my):
            tool = t
            return True

    sizes = [(2, "S"), (5, "M"), (10, "L")]
    for i, (sz, _) in enumerate(sizes):
        rect = pygame.Rect(5 + i * 30, CANVAS_H + 28, 25, 18)
        if rect.collidepoint(mx, my):
            brush_sz = sz
            return True

    for i, c in enumerate(PALETTE):
        rect = pygame.Rect(100 + i * 22, CANVAS_H + 28, 20, 18)
        if rect.collidepoint(mx, my):
            color = c
            return True

    return False


def draw_equilateral_triangle(surface, col, x1, y1, x2, y2, width):
    """равносторонний треугольник: строим третью вершину геометрически"""
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2
    # высота = base * sqrt(3)/2, перпендикуляр к основанию
    dx = x2 - x1
    dy = y2 - y1
    h = math.sqrt(3) / 2
    # третья вершина — перпендикуляр от середины основания
    tx = mx - dy * h
    ty = my + dx * h
    pygame.draw.polygon(surface, col,
        [(x1, y1), (x2, y2), (int(tx), int(ty))], width)


def draw_right_triangle(surface, col, x1, y1, x2, y2, width):
    """прямоугольный треугольник: вершины (x1,y1), (x2,y2), (x1,y2)"""
    pygame.draw.polygon(surface, col,
        [(x1, y1), (x2, y2), (x1, y2)], width)


def draw_rhombus(surface, col, x1, y1, x2, y2, width):
    """ромб: центр между двумя точками, четыре вершины"""
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    pygame.draw.polygon(surface, col,
        [(cx, y1), (x2, cy), (cx, y2), (x1, cy)], width)


def flood_fill(surface, pos, fill_color):
    """заливка через bfs — обходим пиксели как граф, заменяем целевой цвет"""
    x, y = pos
    if x < 0 or x >= WIDTH or y < 0 or y >= CANVAS_H:
        return

    target_color = surface.get_at((x, y))[:3]
    if target_color == fill_color[:3]:
        return  # уже нужный цвет — ничего не делаем

    visited = set()
    queue = deque()
    queue.append((x, y))

    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) in visited:
            continue
        if cx < 0 or cx >= WIDTH or cy < 0 or cy >= CANVAS_H:
            continue
        if surface.get_at((cx, cy))[:3] != target_color:
            continue

        surface.set_at((cx, cy), fill_color)
        visited.add((cx, cy))

        queue.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])


def commit_shape(surface, t, sx, sy, ex, ey, col, sz):
    """финально рисуем фигуру на холст при отпускании мыши"""
    if t == "line":
        pygame.draw.line(surface, col, (sx, sy), (ex, ey), sz)
    elif t == "rect":
        rx, ry = min(sx, ex), min(sy, ey)
        pygame.draw.rect(surface, col, (rx, ry, abs(ex-sx), abs(ey-sy)), sz)
    elif t == "square":
        side = min(abs(ex-sx), abs(ey-sy))
        rx = sx if ex >= sx else sx - side
        ry = sy if ey >= sy else sy - side
        pygame.draw.rect(surface, col, (rx, ry, side, side), sz)
    elif t == "circle":
        cx, cy = (sx+ex)//2, (sy+ey)//2
        r = max(1, int(math.hypot(ex-sx, ey-sy) // 2))
        pygame.draw.circle(surface, col, (cx, cy), r, sz)
    elif t == "etriangle":
        draw_equilateral_triangle(surface, col, sx, sy, ex, ey, sz)
    elif t == "rtriangle":
        draw_right_triangle(surface, col, sx, sy, ex, ey, sz)
    elif t == "rhombus":
        draw_rhombus(surface, col, sx, sy, ex, ey, sz)


def draw_preview(surface, t, sx, sy, ex, ey, col, sz):
    """превью фигуры пока тащим мышь (рисуем на screen, не на canvas)"""
    commit_shape(surface, t, sx, sy, ex, ey, col, sz)


running = True
drawing = False

while running:
    clock.tick(60)
    mx, my = pygame.mouse.get_pos()
    on_canvas = my < CANVAS_H

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # горячие клавиши
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()

            # ctrl+s — сохранение холста с временем в имени файла
            if event.key == pygame.K_s and keys[pygame.K_LCTRL]:
                fname = "canvas_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
                pygame.image.save(canvas, fname)
                print(f"сохранено: {fname}")

            # размер кисти клавишами 1/2/3
            elif event.key == pygame.K_1:
                brush_sz = 2
            elif event.key == pygame.K_2:
                brush_sz = 5
            elif event.key == pygame.K_3:
                brush_sz = 10

            # текстовый режим — вводим символы
            elif text_mode:
                if event.key == pygame.K_RETURN:
                    # подтверждаем — рисуем текст на холст
                    if typed_text and text_pos:
                        f = pygame.font.SysFont("Arial", 20)
                        rendered = f.render(typed_text, True, color)
                        canvas.blit(rendered, text_pos)
                    text_mode = False
                    typed_text = ""
                    text_pos = None
                elif event.key == pygame.K_ESCAPE:
                    text_mode = False
                    typed_text = ""
                    text_pos = None
                elif event.key == pygame.K_BACKSPACE:
                    typed_text = typed_text[:-1]
                else:
                    if event.unicode:
                        typed_text += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not on_canvas:
                handle_toolbar_click(mx, my)
            else:
                if tool == "fill":
                    flood_fill(canvas, (mx, my), color)
                elif tool == "text":
                    text_mode = True
                    text_pos = (mx, my)
                    typed_text = ""
                elif tool in ("pencil", "eraser"):
                    drawing = True
                    prev_pos = (mx, my)
                else:
                    # фигуры с превью — запоминаем стартовую точку
                    start_pos = (mx, my)
                    drawing = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drawing and start_pos and tool not in ("pencil", "eraser"):
                commit_shape(canvas, tool, start_pos[0], start_pos[1], mx, my, color, brush_sz)
                start_pos = None
            drawing = False
            prev_pos = None

        if event.type == pygame.MOUSEMOTION:
            if drawing and on_canvas:
                if tool == "pencil" and prev_pos:
                    # рисуем линию между предыдущей и текущей позицией мыши
                    pygame.draw.line(canvas, color, prev_pos, (mx, my), brush_sz)
                    prev_pos = (mx, my)
                elif tool == "eraser" and prev_pos:
                    pygame.draw.line(canvas, WHITE, prev_pos, (mx, my), brush_sz * 3)
                    prev_pos = (mx, my)

    # --- отрисовка ---
    screen.blit(canvas, (0, 0))

    # превью фигуры пока тащим
    if drawing and start_pos and tool not in ("pencil", "eraser") and on_canvas:
        draw_preview(screen, tool, start_pos[0], start_pos[1], mx, my, color, brush_sz)

    # превью текста пока печатаем
    if text_mode and text_pos and typed_text:
        f = pygame.font.SysFont("Arial", 20)
        rendered = f.render(typed_text + "|", True, color)
        screen.blit(rendered, text_pos)

    draw_toolbar()
    pygame.display.flip()

pygame.quit()
sys.exit()
