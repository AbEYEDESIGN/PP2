import pygame
import sys
from ball import Ball

pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("движущийся мяч")

WHITE = (255, 255, 255)
RED   = (220, 50, 50)
GRAY  = (180, 180, 180)

font  = pygame.font.SysFont("Arial", 16)
clock = pygame.time.Clock()

# создаём мяч в центре экрана
ball = Ball(WIDTH // 2, HEIGHT // 2, 25, WIDTH, HEIGHT)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            # обрабатываем стрелки
            if event.key == pygame.K_UP:
                ball.move(0, -1)
            elif event.key == pygame.K_DOWN:
                ball.move(0, 1)
            elif event.key == pygame.K_LEFT:
                ball.move(-1, 0)
            elif event.key == pygame.K_RIGHT:
                ball.move(1, 0)

    screen.fill(WHITE)

    # тень под мячом
    pygame.draw.circle(screen, GRAY, (ball.x + 3, ball.y + 3), ball.radius)
    # сам мяч
    pygame.draw.circle(screen, RED, (ball.x, ball.y), ball.radius)

    # текущие координаты мяча
    pos = font.render(f"x: {ball.x}  y: {ball.y}", True, GRAY)
    screen.blit(pos, (10, 10))

    pygame.display.flip()
    clock.tick(60)