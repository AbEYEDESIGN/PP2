import pygame
import sys
from clock import MickeyClock

def main():
    # инициализация графического движка
    pygame.init()
    
    # создание окна приложения
    width, height = 600, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("mickey clock")
    
    # настройка таймера и создание объекта часов
    clock = pygame.time.Clock()
    my_clock = MickeyClock(width, height)

    # цикл обработки событий и обновления экрана
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # вызов метода отрисовки
        my_clock.draw(screen)

        # обновление дисплея
        pygame.display.flip()
        clock.tick(30)

    # корректный выход из программы
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()