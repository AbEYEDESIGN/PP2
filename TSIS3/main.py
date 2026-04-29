import pygame
import sys
import random
import json
import os
import time
from pygame.locals import *

pygame.init()

SCREEN_W, SCREEN_H = 400, 600
FPS = 60

WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (220, 50, 50)
BLUE   = (50, 100, 220)
GREEN  = (50, 200, 50)
YELLOW = (255, 215, 0)
GRAY   = (80, 80, 80)
ORANGE = (255, 140, 0)
CYAN   = (0, 200, 200)
PURPLE = (160, 50, 200)
DKGRAY = (40, 40, 40)

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Racer TSIS 3")
clock = pygame.time.Clock()

font_big   = pygame.font.SysFont("Verdana", 48)
font_med   = pygame.font.SysFont("Verdana", 28)
font_small = pygame.font.SysFont("Verdana", 18)

SETTINGS_FILE    = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

# --- persistence ---

def load_settings():
    default = {"sound": True, "car_color": [50, 100, 220], "difficulty": "normal"}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            return {**default, **json.load(f)}
    return default

def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE) as f:
            return json.load(f)
    return []

def save_leaderboard(lb):
    # сортируем по счёту, оставляем топ 10
    lb.sort(key=lambda x: x["score"], reverse=True)
    lb = lb[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(lb, f, indent=2)
    return lb


# --- спрайты ---

class Player(pygame.sprite.Sprite):
    def __init__(self, car_color):
        super().__init__()
        self.image = pygame.Surface((40, 60), pygame.SRCALPHA)
        self.image.fill(tuple(car_color))
        # нарисуем простые "окна"
        pygame.draw.rect(self.image, (180, 220, 255), (5, 8, 30, 15))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_W // 2, SCREEN_H - 80)
        self.shield = False    # активен ли щит
        self.nitro  = False    # активен ли нитро
        self.nitro_end  = 0
        self.shield_hit = False

    def move(self, speed_mult=1.0):
        keys = pygame.key.get_pressed()
        spd = int(10 * speed_mult)
        if keys[K_LEFT]  and self.rect.left > 0:
            self.rect.x -= spd
        if keys[K_RIGHT] and self.rect.right < SCREEN_W:
            self.rect.x += spd

    def update_powerups(self):
        now = pygame.time.get_ticks()
        if self.nitro and now > self.nitro_end:
            self.nitro = False


class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((40, 60), pygame.SRCALPHA)
        self.image.fill(RED)
        pygame.draw.rect(self.image, (180, 220, 255), (5, 8, 30, 15))
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(30, SCREEN_W - 30)
        self.rect.bottom = 0
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H:
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    """нефтяное пятно или барьер — замедляют или убивают"""
    def __init__(self, speed, obs_type="oil"):
        super().__init__()
        self.obs_type = obs_type
        self.image = pygame.Surface((50, 25), pygame.SRCALPHA)
        if obs_type == "oil":
            pygame.draw.ellipse(self.image, (30, 30, 30), (0, 0, 50, 25))
        else:
            self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(30, SCREEN_W - 30)
        self.rect.bottom = 0
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H:
            self.kill()


class Coin(pygame.sprite.Sprite):
    WEIGHTS = [(1, YELLOW), (3, ORANGE), (5, CYAN)]  # (очки, цвет)

    def __init__(self, speed):
        super().__init__()
        self.value, col = random.choice(self.WEIGHTS)
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, col, (10, 10), 10)
        # число на монете
        lbl = pygame.font.SysFont("Arial", 10).render(str(self.value), True, BLACK)
        self.image.blit(lbl, (10 - lbl.get_width()//2, 10 - lbl.get_height()//2))
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(15, SCREEN_W - 15)
        self.rect.bottom = 0
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    TYPES = ["nitro", "shield", "repair"]
    COLORS = {"nitro": ORANGE, "shield": CYAN, "repair": GREEN}

    def __init__(self, speed):
        super().__init__()
        self.kind = random.choice(self.TYPES)
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.COLORS[self.kind], (0, 0, 30, 30), border_radius=6)
        lbl = pygame.font.SysFont("Arial", 9).render(self.kind[:3].upper(), True, WHITE)
        self.image.blit(lbl, (15 - lbl.get_width()//2, 15 - lbl.get_height()//2))
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(20, SCREEN_W - 20)
        self.rect.bottom = 0
        self.speed = speed
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speed
        # пропадает через 8 секунд если не подобрали
        if pygame.time.get_ticks() - self.spawn_time > 8000:
            self.kill()
        if self.rect.top > SCREEN_H:
            self.kill()


# --- экраны ---

def draw_road(offset):
    screen.fill(GRAY)
    # обочины
    pygame.draw.rect(screen, DKGRAY, (0, 0, 30, SCREEN_H))
    pygame.draw.rect(screen, DKGRAY, (SCREEN_W-30, 0, 30, SCREEN_H))
    # разметка — смещается вниз для эффекта движения
    line_h, gap = 50, 30
    for y in range(-line_h, SCREEN_H + line_h, line_h + gap):
        pygame.draw.rect(screen, WHITE, (SCREEN_W//2 - 5, (y + offset) % (SCREEN_H + line_h) - line_h, 10, line_h))


def screen_text(text, font, col, cx, cy):
    surf = font.render(text, True, col)
    screen.blit(surf, (cx - surf.get_width()//2, cy - surf.get_height()//2))


def main_menu(settings):
    """главное меню"""
    while True:
        screen.fill(DKGRAY)
        screen_text("RACER", font_big, YELLOW, SCREEN_W//2, 100)

        buttons = [("Play",        200),
                   ("Leaderboard", 270),
                   ("Settings",    340),
                   ("Quit",        410)]

        mx, my = pygame.mouse.get_pos()
        for label, y in buttons:
            rect = pygame.Rect(SCREEN_W//2 - 80, y - 20, 160, 40)
            col = (100, 200, 100) if rect.collidepoint(mx, my) else (60, 60, 80)
            pygame.draw.rect(screen, col, rect, border_radius=8)
            screen_text(label, font_med, WHITE, SCREEN_W//2, y)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                for label, y in buttons:
                    rect = pygame.Rect(SCREEN_W//2 - 80, y - 20, 160, 40)
                    if rect.collidepoint(event.pos):
                        if label == "Play":
                            return "play"
                        elif label == "Leaderboard":
                            leaderboard_screen()
                        elif label == "Settings":
                            settings_screen(settings)
                        elif label == "Quit":
                            pygame.quit(); sys.exit()


def get_username():
    """запрашиваем имя игрока перед игрой"""
    name = ""
    while True:
        screen.fill(DKGRAY)
        screen_text("Enter your name:", font_med, WHITE, SCREEN_W//2, 200)
        screen_text(name + "|", font_med, YELLOW, SCREEN_W//2, 270)
        screen_text("Press Enter to start", font_small, GRAY, SCREEN_W//2, 330)
        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN and name.strip():
                    return name.strip()
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode and len(name) < 15:
                    name += event.unicode


def leaderboard_screen():
    lb = load_leaderboard()
    while True:
        screen.fill(DKGRAY)
        screen_text("TOP 10", font_big, YELLOW, SCREEN_W//2, 50)

        for i, entry in enumerate(lb[:10]):
            text = f"{i+1}. {entry['name']}  {entry['score']}  {entry.get('distance',0)}m"
            surf = font_small.render(text, True, WHITE)
            screen.blit(surf, (20, 110 + i * 38))

        back = pygame.Rect(SCREEN_W//2 - 60, 530, 120, 36)
        pygame.draw.rect(screen, (80, 80, 120), back, border_radius=8)
        screen_text("Back", font_small, WHITE, SCREEN_W//2, 548)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    return
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return


def settings_screen(settings):
    while True:
        screen.fill(DKGRAY)
        screen_text("Settings", font_big, YELLOW, SCREEN_W//2, 60)

        # звук
        sound_r = pygame.Rect(SCREEN_W//2 - 80, 140, 160, 36)
        col = (0, 180, 0) if settings["sound"] else (180, 0, 0)
        pygame.draw.rect(screen, col, sound_r, border_radius=8)
        screen_text("Sound: " + ("ON" if settings["sound"] else "OFF"), font_small, WHITE, SCREEN_W//2, 158)

        # сложность
        diffs = ["easy", "normal", "hard"]
        for i, d in enumerate(diffs):
            r = pygame.Rect(20 + i * 120, 220, 110, 36)
            col = (100, 200, 100) if settings["difficulty"] == d else (60, 60, 80)
            pygame.draw.rect(screen, col, r, border_radius=8)
            screen_text(d, font_small, WHITE, 20 + i * 120 + 55, 238)

        # цвет машины — три варианта
        car_colors = [[50, 100, 220], [200, 50, 50], [50, 180, 50]]
        for i, cc in enumerate(car_colors):
            r = pygame.Rect(60 + i * 90, 300, 70, 36)
            pygame.draw.rect(screen, tuple(cc), r, border_radius=8)
            if settings["car_color"] == cc:
                pygame.draw.rect(screen, WHITE, r, 3, border_radius=8)

        lbl = font_small.render("Car color:", True, WHITE)
        screen.blit(lbl, (20, 304))

        save_r = pygame.Rect(SCREEN_W//2 - 70, 400, 140, 36)
        pygame.draw.rect(screen, (80, 80, 180), save_r, border_radius=8)
        screen_text("Save & Back", font_small, WHITE, SCREEN_W//2, 418)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if sound_r.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                for i, d in enumerate(diffs):
                    r = pygame.Rect(20 + i * 120, 220, 110, 36)
                    if r.collidepoint(event.pos):
                        settings["difficulty"] = d
                for i, cc in enumerate(car_colors):
                    r = pygame.Rect(60 + i * 90, 300, 70, 36)
                    if r.collidepoint(event.pos):
                        settings["car_color"] = cc
                if save_r.collidepoint(event.pos):
                    save_settings(settings)
                    return


def game_over_screen(score, distance, coins, username):
    lb = load_leaderboard()
    lb.append({"name": username, "score": score, "distance": distance})
    lb = save_leaderboard(lb)

    while True:
        screen.fill(DKGRAY)
        screen_text("GAME OVER", font_big, RED, SCREEN_W//2, 80)
        screen_text(f"Score: {score}", font_med, WHITE, SCREEN_W//2, 180)
        screen_text(f"Distance: {distance}m", font_small, GRAY, SCREEN_W//2, 230)
        screen_text(f"Coins: {coins}", font_small, YELLOW, SCREEN_W//2, 265)

        buttons = [("Retry", 360), ("Main Menu", 420)]
        mx, my = pygame.mouse.get_pos()
        for label, y in buttons:
            r = pygame.Rect(SCREEN_W//2 - 80, y - 18, 160, 36)
            col = (100, 200, 100) if r.collidepoint(mx, my) else (60, 60, 80)
            pygame.draw.rect(screen, col, r, border_radius=8)
            screen_text(label, font_small, WHITE, SCREEN_W//2, y)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                for label, y in buttons:
                    r = pygame.Rect(SCREEN_W//2 - 80, y - 18, 160, 36)
                    if r.collidepoint(event.pos):
                        return label  # "Retry" или "Main Menu"


# --- основная игра ---

def play_game(settings, username):
    difficulty_speed = {"easy": 5, "normal": 8, "hard": 12}
    base_speed = difficulty_speed.get(settings["difficulty"], 8)
    speed = base_speed

    player = Player(settings["car_color"])
    all_sprites = pygame.sprite.Group()
    enemies_grp  = pygame.sprite.Group()
    coins_grp    = pygame.sprite.Group()
    obstacles_grp = pygame.sprite.Group()
    powerups_grp  = pygame.sprite.Group()

    all_sprites.add(player)

    score = 0
    coins_count = 0
    distance = 0
    road_offset = 0

    SPAWN_ENEMY   = USEREVENT + 1
    SPAWN_COIN    = USEREVENT + 2
    SPAWN_OBS     = USEREVENT + 3
    SPAWN_POWERUP = USEREVENT + 4
    INC_SPEED     = USEREVENT + 5

    pygame.time.set_timer(SPAWN_ENEMY,   1200)
    pygame.time.set_timer(SPAWN_COIN,    2000)
    pygame.time.set_timer(SPAWN_OBS,     3000)
    pygame.time.set_timer(SPAWN_POWERUP, 7000)
    pygame.time.set_timer(INC_SPEED,     1000)

    active_powerup = None   # текущий активный бафф
    powerup_end    = 0

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()

            if event.type == SPAWN_ENEMY:
                # чем выше счёт — тем чаще машины
                count = 1 + score // 10
                for _ in range(min(count, 3)):
                    e = Enemy(speed)
                    enemies_grp.add(e)
                    all_sprites.add(e)

            if event.type == SPAWN_COIN:
                c = Coin(speed)
                coins_grp.add(c)
                all_sprites.add(c)

            if event.type == SPAWN_OBS:
                obs = Obstacle(speed)
                obstacles_grp.add(obs)
                all_sprites.add(obs)

            if event.type == SPAWN_POWERUP:
                # только один пауэрап на дороге за раз
                if len(powerups_grp) == 0:
                    pw = PowerUp(speed)
                    powerups_grp.add(pw)
                    all_sprites.add(pw)

            if event.type == INC_SPEED:
                speed = base_speed + score // 5
                distance += speed // 3

        # движение игрока (нитро = +50% скорость управления)
        nitro_mult = 1.5 if player.nitro else 1.0
        player.move(nitro_mult)
        player.update_powerups()

        all_sprites.update()

        road_offset = (road_offset + speed) % 80
        draw_road(road_offset)
        all_sprites.draw(screen)

        # подбор монет
        collected = pygame.sprite.spritecollide(player, coins_grp, True)
        for c in collected:
            coins_count += c.value
            score += c.value * 2
            # увеличиваем скорость каждые 10 монет (из practice 11)
            if coins_count % 10 == 0:
                speed += 1

        # подбор пауэрапов
        grabbed = pygame.sprite.spritecollide(player, powerups_grp, True)
        for pw in grabbed:
            now = pygame.time.get_ticks()
            active_powerup = pw.kind
            if pw.kind == "nitro":
                player.nitro = True
                player.nitro_end = now + 4000
                powerup_end = player.nitro_end
            elif pw.kind == "shield":
                player.shield = True
                powerup_end = now + 30000  # до первого удара
            elif pw.kind == "repair":
                active_powerup = None  # repair мгновенный

        # столкновение с машинами
        hit_enemies = pygame.sprite.spritecollide(player, enemies_grp, True)
        if hit_enemies:
            if player.shield:
                player.shield = False  # щит поглощает один удар
                active_powerup = None
            else:
                return game_over_screen(score, distance, coins_count, username)

        # столкновение с препятствиями
        hit_obs = pygame.sprite.spritecollide(player, obstacles_grp, True)
        for obs in hit_obs:
            if obs.obs_type == "oil":
                speed = max(base_speed, speed - 2)  # масло замедляет
            else:
                if player.shield:
                    player.shield = False
                    active_powerup = None
                else:
                    return game_over_screen(score, distance, coins_count, username)

        # hud
        screen.blit(font_small.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(font_small.render(f"Coins: {coins_count}", True, YELLOW), (10, 35))
        screen.blit(font_small.render(f"Dist: {distance}m", True, GRAY), (10, 60))

        if active_powerup:
            now = pygame.time.get_ticks()
            remaining = max(0, (powerup_end - now) // 1000)
            screen.blit(font_small.render(f"[{active_powerup.upper()}] {remaining}s", True, CYAN),
                        (SCREEN_W - 120, 10))

        pygame.display.flip()


# --- старт ---

settings = load_settings()

while True:
    action = main_menu(settings)
    if action == "play":
        username = get_username()
        result = play_game(settings, username)
        # result = "Retry" или "Main Menu" — возвращается из game_over_screen
        # если Main Menu — просто повторяем цикл, если Retry — запускаем снова
        if result == "Retry":
            result2 = play_game(settings, username)
