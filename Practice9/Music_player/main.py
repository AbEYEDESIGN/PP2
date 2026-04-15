import pygame
import sys
from player import Player

pygame.init()

WIDTH, HEIGHT = 500, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("музыкальный плеер")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (200, 200, 200)
BLUE  = (70, 130, 180)

font_big   = pygame.font.SysFont("Arial", 22, bold=True)
font_small = pygame.font.SysFont("Arial", 16)

player = Player("music")
clock  = pygame.time.Clock()

# список клавиш и их действий
CONTROLS = [
    ("P", "play"),
    ("S", "stop"),
    ("N", "next"),
    ("B", "prev"),
    ("Q", "quit"),
]

def draw():
    screen.fill(WHITE)

    # заголовок
    title = font_big.render("music player", True, BLUE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    # текущий трек и статус
    status = "playing" if player.playing else "stopped"
    track  = font_small.render(f"трек: {player.current_name()}", True, BLACK)
    stat   = font_small.render(f"статус: {status}", True, BLUE)
    screen.blit(track, (20, 80))
    screen.blit(stat,  (20, 105))

    # разделитель
    pygame.draw.line(screen, GRAY, (20, 135), (WIDTH - 20, 135), 1)

    # подсказка по управлению
    hint = font_small.render("управление:", True, GRAY)
    screen.blit(hint, (20, 148))
    for i, (key, action) in enumerate(CONTROLS):
        col = i * 90 + 20
        pygame.draw.rect(screen, BLUE, (col, 175, 70, 30), border_radius=5)
        label = font_small.render(f"{key} - {action}", True, WHITE)
        screen.blit(label, (col + 5, 182))

    pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.stopped_manually = True   # помечаем что стоп нажат вручную
                player.stop()
            elif event.key == pygame.K_n:
                player.next()
            elif event.key == pygame.K_b:
                player.prev()
            elif event.key == pygame.K_q:
                pygame.quit(); sys.exit()

        
        # автопереход когда трек заканчивается
        MUSIC_END = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(MUSIC_END)
        if event.type == MUSIC_END:
            if not player.stopped_manually:      # автопереход только если не вручную
                player.next()
            player.stopped_manually = False      # сбрасываем флаг

    draw()
    clock.tick(30)