import pygame
import sys
import random
import time
from pygame.locals import *

pygame.init()

# настройки
FPS = 60
FramePerSec = pygame.time.Clock()

BLUE   = (0, 0, 255)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
YELLOW = (255, 215, 0)

SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
SPEED = 8
SCORE = 0
COINS_COUNT = 0  # добавил счётчик монет

font       = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over  = font.render("Game Over", True, BLACK)

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Racer")


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.kill()
            e = Enemy()
            enemies.add(e)
            all_sprites.add(e)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-10, 0)
        if pressed_keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(10, 0)


# класс монеты - появляется случайно сверху и падает вниз
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (10, 10), 10)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(20, SCREEN_WIDTH - 20), 0)

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


P1 = Player()
E1 = Enemy()

all_sprites = pygame.sprite.Group()
enemies     = pygame.sprite.Group()
coins       = pygame.sprite.Group()  # группа для монет

all_sprites.add(P1)
all_sprites.add(E1)
enemies.add(E1)

INC_SPEED  = pygame.USEREVENT + 1
SPAWN_COIN = pygame.USEREVENT + 2  # событие для спавна монеты

pygame.time.set_timer(INC_SPEED,  1000)
pygame.time.set_timer(SPAWN_COIN, 3000)  # монета появляется каждые 3 сек


def draw_road():
    DISPLAYSURF.fill((80, 80, 80))
    sw = 10
    sh = 50
    gap = 40
    x = SCREEN_WIDTH // 2 - sw // 2
    for y in range(0, SCREEN_HEIGHT, sh + gap):
        pygame.draw.rect(DISPLAYSURF, WHITE, (x, y, sw, sh))


while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == INC_SPEED:
            SPEED += 0.5

        # спавним монету по таймеру
        if event.type == SPAWN_COIN:
            c = Coin()
            coins.add(c)
            all_sprites.add(c)

    draw_road()

    scores_text = font_small.render("Score: " + str(SCORE), True, WHITE)
    DISPLAYSURF.blit(scores_text, (10, 10))

    # отображаем монеты в правом верхнем углу
    coins_text = font_small.render("Coins: " + str(COINS_COUNT), True, YELLOW)
    coins_rect = coins_text.get_rect()
    coins_rect.topright = (SCREEN_WIDTH - 10, 10)
    DISPLAYSURF.blit(coins_text, coins_rect)

    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # проверяем собрал ли игрок монеты
    collected = pygame.sprite.spritecollide(P1, coins, True)
    COINS_COUNT += len(collected)

    if pygame.sprite.spritecollideany(P1, enemies):
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 40))

        # показываем сколько монет собрал
        final = font_small.render("Coins: " + str(COINS_COUNT), True, WHITE)
        DISPLAYSURF.blit(final, (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 40))

        pygame.display.update()
        time.sleep(2)
        for entity in all_sprites:
            entity.kill()
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)
