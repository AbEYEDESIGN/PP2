import pygame
import sys
import random
import json
import os
from db import init_db, get_or_create_player, save_session, get_top10, get_personal_best

pygame.init()

CELL  = 20
COLS  = 30
ROWS  = 28
W     = COLS * CELL
H     = ROWS * CELL + 60   # +60 для hud сверху
FPS   = 60

WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GREEN  = (50, 200, 50)
DKGRN  = (30, 140, 30)
RED    = (220, 50, 50)
YELLOW = (240, 210, 0)
ORANGE = (255, 140, 0)
CYAN   = (0, 200, 200)
PURPLE = (160, 50, 200)
DKRED  = (120, 0, 0)
GRAY   = (100, 100, 100)
DKGRAY = (40, 40, 40)
LGRAY  = (160, 160, 160)

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Snake TSIS 4")
clock = pygame.time.Clock()

font_big   = pygame.font.SysFont("Arial", 42, bold=True)
font_med   = pygame.font.SysFont("Arial", 28)
font_small = pygame.font.SysFont("Arial", 18)

SETTINGS_FILE = "settings.json"

def load_settings():
    default = {"snake_color": [50, 200, 50], "grid": True, "sound": True}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            return {**default, **json.load(f)}
    return default

def save_settings_file(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)


def cx(t): return t[0] * CELL
def cy(t): return t[1] * CELL + 60   # +60 смещение для hud


def screen_text(text, font, col, x, y, center=True):
    surf = font.render(text, True, col)
    if center:
        screen.blit(surf, (x - surf.get_width()//2, y - surf.get_height()//2))
    else:
        screen.blit(surf, (x, y))


# --- экраны ---

def get_username():
    name = ""
    while True:
        screen.fill(DKGRAY)
        screen_text("Snake TSIS 4", font_big, GREEN, W//2, 120)
        screen_text("Enter your name:", font_med, WHITE, W//2, 220)
        screen_text(name + "|", font_med, YELLOW, W//2, 270)
        screen_text("Press Enter to start", font_small, GRAY, W//2, 320)
        pygame.display.flip()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode and len(name) < 15:
                    name += event.unicode


def main_menu():
    while True:
        screen.fill(DKGRAY)
        screen_text("SNAKE", font_big, GREEN, W//2, 100)

        buttons = [("Play", 220), ("Leaderboard", 290), ("Settings", 360), ("Quit", 430)]
        mx, my = pygame.mouse.get_pos()
        for label, y in buttons:
            r = pygame.Rect(W//2 - 90, y - 20, 180, 40)
            col = (80, 180, 80) if r.collidepoint(mx, my) else (50, 50, 70)
            pygame.draw.rect(screen, col, r, border_radius=8)
            screen_text(label, font_med, WHITE, W//2, y)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, y in buttons:
                    r = pygame.Rect(W//2 - 90, y - 20, 180, 40)
                    if r.collidepoint(event.pos):
                        return label


def leaderboard_screen():
    rows = get_top10()
    while True:
        screen.fill(DKGRAY)
        screen_text("TOP 10", font_big, YELLOW, W//2, 50)
        headers = ["#", "Name", "Score", "Lvl", "Date"]
        xs = [20, 55, 220, 300, 370]
        for i, h in enumerate(headers):
            screen_text(h, font_small, LGRAY, xs[i], 100, center=False)

        for i, row in enumerate(rows):
            y = 130 + i * 32
            vals = [str(i+1), row[0], str(row[1]), str(row[2]), row[3]]
            for j, v in enumerate(vals):
                screen_text(v, font_small, WHITE, xs[j], y, center=False)

        back = pygame.Rect(W//2 - 60, H - 55, 120, 36)
        pygame.draw.rect(screen, (60, 60, 100), back, border_radius=8)
        screen_text("Back", font_small, WHITE, W//2, H - 37)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


def settings_screen(settings):
    while True:
        screen.fill(DKGRAY)
        screen_text("Settings", font_big, YELLOW, W//2, 60)

        # сетка
        gr = pygame.Rect(W//2 - 80, 130, 160, 36)
        col = (0, 160, 0) if settings["grid"] else (140, 0, 0)
        pygame.draw.rect(screen, col, gr, border_radius=8)
        screen_text("Grid: " + ("ON" if settings["grid"] else "OFF"), font_small, WHITE, W//2, 148)

        # звук
        sr = pygame.Rect(W//2 - 80, 190, 160, 36)
        col = (0, 160, 0) if settings["sound"] else (140, 0, 0)
        pygame.draw.rect(screen, col, sr, border_radius=8)
        screen_text("Sound: " + ("ON" if settings["sound"] else "OFF"), font_small, WHITE, W//2, 208)

        # цвет змейки
        snake_colors = [[50, 200, 50], [50, 100, 220], [200, 150, 50]]
        screen_text("Snake color:", font_small, LGRAY, W//2 - 120, 255, center=False)
        for i, sc in enumerate(snake_colors):
            r = pygame.Rect(W//2 - 90 + i * 70, 280, 60, 30)
            pygame.draw.rect(screen, tuple(sc), r, border_radius=6)
            if settings["snake_color"] == sc:
                pygame.draw.rect(screen, WHITE, r, 2, border_radius=6)

        save_r = pygame.Rect(W//2 - 80, 360, 160, 36)
        pygame.draw.rect(screen, (60, 60, 140), save_r, border_radius=8)
        screen_text("Save & Back", font_small, WHITE, W//2, 378)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if gr.collidepoint(event.pos):
                    settings["grid"] = not settings["grid"]
                if sr.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                for i, sc in enumerate(snake_colors):
                    r = pygame.Rect(W//2 - 90 + i * 70, 280, 60, 30)
                    if r.collidepoint(event.pos):
                        settings["snake_color"] = sc
                if save_r.collidepoint(event.pos):
                    save_settings_file(settings)
                    return


def game_over_screen(score, level, personal_best, username, player_id):
    save_session(player_id, score, level)
    new_best = get_personal_best(player_id)

    while True:
        screen.fill(DKGRAY)
        screen_text("GAME OVER", font_big, RED, W//2, 100)
        screen_text(f"Score: {score}", font_med, WHITE, W//2, 180)
        screen_text(f"Level: {level}", font_small, LGRAY, W//2, 220)
        screen_text(f"Your best: {new_best}", font_small, YELLOW, W//2, 255)

        buttons = [("Retry", 340), ("Main Menu", 400)]
        mx, my = pygame.mouse.get_pos()
        for label, y in buttons:
            r = pygame.Rect(W//2 - 80, y - 18, 160, 36)
            col = (80, 180, 80) if r.collidepoint(mx, my) else (50, 50, 70)
            pygame.draw.rect(screen, col, r, border_radius=8)
            screen_text(label, font_small, WHITE, W//2, y)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, y in buttons:
                    r = pygame.Rect(W//2 - 80, y - 18, 160, 36)
                    if r.collidepoint(event.pos):
                        return label


# --- игровая логика ---

def random_empty_cell(occupied):
    """случайная свободная клетка (не занятая змейкой или стенами)"""
    while True:
        pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
        if pos not in occupied:
            return pos


def generate_obstacles(level, snake_body):
    """с уровня 3 добавляем случайные блоки-стены"""
    if level < 3:
        return set()
    count = (level - 2) * 3
    occupied = set(snake_body)
    walls = set()
    for _ in range(count):
        pos = random_empty_cell(occupied | walls)
        walls.add(pos)
    return walls


def play_game(settings, username, player_id, personal_best):
    snake_col = tuple(settings["snake_color"])
    show_grid = settings["grid"]

    snake  = [(COLS//2, ROWS//2), (COLS//2 - 1, ROWS//2), (COLS//2 - 2, ROWS//2)]
    direction = (1, 0)
    next_dir  = (1, 0)

    score = 0
    level = 1
    foods_eaten = 0
    FOODS_PER_LEVEL = 5

    # базовая скорость — тиков в секунду
    base_speed = 8
    move_delay = 1000 // base_speed   # мс между шагами
    last_move  = pygame.time.get_ticks()

    obstacles = set()

    # еда: (pos, weight, color, spawn_time, timeout)
    # weight 1 = обычная, 3 = золотая, -2 = яд
    def make_food():
        occ = set(snake) | obstacles
        pos = random_empty_cell(occ)
        r = random.random()
        if r < 0.15:
            return {"pos": pos, "w": -2, "col": DKRED, "born": pygame.time.get_ticks(), "timeout": 6000}
        elif r < 0.35:
            return {"pos": pos, "w": 3, "col": YELLOW, "born": pygame.time.get_ticks(), "timeout": 5000}
        else:
            return {"pos": pos, "w": 1, "col": RED, "born": pygame.time.get_ticks(), "timeout": 8000}

    foods = [make_food()]

    # пауэрап
    powerup = None
    active_pw  = None
    pw_end     = 0
    shield_on  = False

    while True:
        now = pygame.time.get_ticks()
        dt  = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP    and direction != (0, 1):
                    next_dir = (0, -1)
                elif event.key == pygame.K_DOWN  and direction != (0, -1):
                    next_dir = (0, 1)
                elif event.key == pygame.K_LEFT  and direction != (1, 0):
                    next_dir = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    next_dir = (1, 0)

        # --- движение змейки по таймеру ---
        speed_mult = 2.0 if active_pw == "speed" else (0.5 if active_pw == "slow" else 1.0)
        effective_delay = int(move_delay / speed_mult)

        if now - last_move >= effective_delay:
            last_move = now
            direction = next_dir
            hx, hy = snake[0]
            new_head = (hx + direction[0], hy + direction[1])

            # столкновение со стеной
            if new_head[0] < 0 or new_head[0] >= COLS or new_head[1] < 0 or new_head[1] >= ROWS:
                if shield_on:
                    shield_on = False
                    active_pw = None
                    new_head = (max(0, min(COLS-1, new_head[0])), max(0, min(ROWS-1, new_head[1])))
                else:
                    return game_over_screen(score, level, personal_best, username, player_id)

            # столкновение с телом
            if new_head in snake[1:]:
                if shield_on:
                    shield_on = False
                    active_pw = None
                else:
                    return game_over_screen(score, level, personal_best, username, player_id)

            # столкновение с препятствием
            if new_head in obstacles:
                if shield_on:
                    shield_on = False
                    active_pw = None
                else:
                    return game_over_screen(score, level, personal_best, username, player_id)

            snake.insert(0, new_head)
            grew = False

            # проверяем съедена ли еда
            for food in foods[:]:
                if new_head == food["pos"]:
                    w = food["w"]
                    if w > 0:
                        score += w * 10
                        foods_eaten += 1
                        # вырастаем на w сегментов
                        for _ in range(w - 1):
                            snake.append(snake[-1])
                        grew = True
                    else:
                        # яд — укорачиваем на 2
                        for _ in range(2):
                            if len(snake) > 1:
                                snake.pop()
                        if len(snake) <= 1:
                            return game_over_screen(score, level, personal_best, username, player_id)
                        grew = True
                    foods.remove(food)
                    foods.append(make_food())
                    break

            if not grew:
                snake.pop()  # двигаемся без роста

            # пауэрап подбор
            if powerup and new_head == powerup["pos"]:
                kind = powerup["kind"]
                active_pw = kind
                if kind == "speed":
                    pw_end = now + 5000
                elif kind == "slow":
                    pw_end = now + 5000
                elif kind == "shield":
                    shield_on = True
                    pw_end = now + 60000  # до первого удара
                powerup = None

            # повышение уровня
            if foods_eaten >= level * FOODS_PER_LEVEL:
                level += 1
                move_delay = max(80, 1000 // (base_speed + (level - 1) * 2))
                obstacles = generate_obstacles(level, snake)

        # истёк таймер пауэрапа
        if active_pw in ("speed", "slow") and now > pw_end:
            active_pw = None

        # еда исчезает по таймеру
        foods = [f for f in foods if now - f["born"] < f["timeout"]]
        if not foods:
            foods.append(make_food())

        # спавн пауэрапа раз в 15 секунд
        if powerup is None and now % 15000 < dt + 100:
            kinds = ["speed", "slow", "shield"]
            occ = set(snake) | obstacles
            pos = random_empty_cell(occ)
            powerup = {"pos": pos, "kind": random.choice(kinds),
                       "born": now, "col": CYAN}

        # пауэрап исчезает через 8 сек
        if powerup and now - powerup["born"] > 8000:
            powerup = None

        # --- отрисовка ---
        screen.fill(DKGRAY)

        # hud
        pygame.draw.rect(screen, (30, 30, 50), (0, 0, W, 60))
        screen_text(f"Score: {score}", font_small, WHITE, 60, 20)
        screen_text(f"Level: {level}", font_small, WHITE, 180, 20)
        screen_text(f"Best: {personal_best}", font_small, YELLOW, 300, 20)
        screen_text(f"Len: {len(snake)}", font_small, LGRAY, 420, 20)
        if active_pw:
            remaining = max(0, (pw_end - now) // 1000)
            screen_text(f"[{active_pw}] {remaining}s", font_small, CYAN, W - 80, 20)

        # фон поля
        pygame.draw.rect(screen, (20, 20, 20), (0, 60, W, ROWS * CELL))

        # сетка
        if show_grid:
            for x in range(COLS):
                for y in range(ROWS):
                    pygame.draw.rect(screen, (30, 30, 30),
                                     (cx((x, y)), cy((x, y)), CELL, CELL), 1)

        # стены-препятствия
        for obs in obstacles:
            pygame.draw.rect(screen, GRAY,
                             (cx(obs), cy(obs), CELL, CELL))
            pygame.draw.rect(screen, LGRAY,
                             (cx(obs), cy(obs), CELL, CELL), 1)

        # еда
        for food in foods:
            fx, fy = food["pos"]
            # таймер убывает — показываем это через размер
            elapsed = now - food["born"]
            ratio = 1 - elapsed / food["timeout"]
            r = max(2, int(CELL // 2 * ratio))
            pygame.draw.circle(screen, food["col"],
                               (cx(food["pos"]) + CELL//2, cy(food["pos"]) + CELL//2), r)

        # пауэрап
        if powerup:
            pw_colors = {"speed": ORANGE, "slow": PURPLE, "shield": CYAN}
            col = pw_colors.get(powerup["kind"], WHITE)
            pygame.draw.rect(screen, col,
                             (cx(powerup["pos"]) + 2, cy(powerup["pos"]) + 2, CELL - 4, CELL - 4),
                             border_radius=4)
            lbl = pygame.font.SysFont("Arial", 10).render(powerup["kind"][:3].upper(), True, WHITE)
            screen.blit(lbl, (cx(powerup["pos"]) + CELL//2 - lbl.get_width()//2,
                              cy(powerup["pos"]) + CELL//2 - lbl.get_height()//2))

        # змейка
        for i, seg in enumerate(snake):
            col = snake_col if i > 0 else DKGRN
            pygame.draw.rect(screen, col,
                             (cx(seg), cy(seg), CELL, CELL))
            pygame.draw.rect(screen, DKGRN,
                             (cx(seg), cy(seg), CELL, CELL), 1)

        pygame.display.flip()


# --- старт ---

try:
    init_db()
    db_ok = True
except Exception as e:
    print(f"бд недоступна: {e}")
    db_ok = False

settings = load_settings()

while True:
    action = main_menu()
    if action == "Play":
        username = get_username()
        if db_ok:
            player_id = get_or_create_player(username)
            personal_best = get_personal_best(player_id)
        else:
            player_id = None
            personal_best = 0

        result = play_game(settings, username, player_id, personal_best)
        while result == "Retry":
            result = play_game(settings, username, player_id, personal_best)

    elif action == "Leaderboard":
        if db_ok:
            leaderboard_screen()
        else:
            print("бд недоступна")

    elif action == "Settings":
        settings_screen(settings)

    elif action == "Quit":
        pygame.quit()
        sys.exit()
