import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы для игры
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
FPS = 60

# Цвета (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")

# Часы для контроля FPS
clock = pygame.time.Clock()

# Шрифт для отображения текста
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)


class Snake:
    """Класс для змейки"""
    def __init__(self):
        # Инициализация змейки - начинает с 3 блоков в центре
        self.body = [
            (SCREEN_WIDTH // (2 * GRID_SIZE) * GRID_SIZE, SCREEN_HEIGHT // (2 * GRID_SIZE) * GRID_SIZE),
            (SCREEN_WIDTH // (2 * GRID_SIZE) * GRID_SIZE - GRID_SIZE, SCREEN_HEIGHT // (2 * GRID_SIZE) * GRID_SIZE),
            (SCREEN_WIDTH // (2 * GRID_SIZE) * GRID_SIZE - 2 * GRID_SIZE, SCREEN_HEIGHT // (2 * GRID_SIZE) * GRID_SIZE)
        ]
        # Направление движения (вправо)
        self.direction = (GRID_SIZE, 0)
        # Следующее направление (для плавного поворота)
        self.next_direction = (GRID_SIZE, 0)
    
    def update(self):
        """Обновление позиции змейки"""
        # Обновление направления движения
        self.direction = self.next_direction
        
        # Получение текущей головы
        head_x, head_y = self.body[0]
        
        # Расчёт новой позиции головы
        new_head_x = head_x + self.direction[0]
        new_head_y = head_y + self.direction[1]
        
        # Добавление новой головы в начало
        self.body.insert(0, (new_head_x, new_head_y))
        
        # Удаление хвоста
        self.body.pop()
    
    def grow(self):
        """Добавление нового сегмента к змейке (без удаления хвоста)"""
        self.body.append(self.body[-1])
    
    def set_direction(self, direction):
        """Установка нового направления (если оно не противоположно текущему)"""
        # Проверка, чтобы змейка не могла развернуться на 180 градусов
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.next_direction = direction
    
    def get_head(self):
        """Получение позиции головы"""
        return self.body[0]
    
    def check_collision_with_body(self):
        """Проверка столкновения с собственным телом"""
        head = self.body[0]
        return head in self.body[1:]
    
    def check_wall_collision(self):
        """Проверка столкновения со стеной"""
        head_x, head_y = self.get_head()
        
        # Проверка выхода за границы
        if head_x < 0 or head_x >= SCREEN_WIDTH or head_y < 0 or head_y >= SCREEN_HEIGHT:
            return True
        return False
    
    def draw(self, surface):
        """Рисование змейки"""
        # Рисование тела (зелёные блоки)
        for segment in self.body:
            rect = pygame.Rect(segment[0], segment[1], GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, GREEN, rect)
            pygame.draw.rect(surface, (0, 200, 0), rect, 2)  # Граница
        
        # Рисование головы (более яркий зелёный)
        head = self.body[0]
        head_rect = pygame.Rect(head[0], head[1], GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, (0, 255, 100), head_rect)


class Food:
    """Класс для еды"""
    def __init__(self, snake):
        self.position = self.generate_position(snake)
    
    def generate_position(self, snake):
        """Генерирование случайной позиции для еды (не на стене и не на змейке)"""
        while True:
            x = random.randint(0, (SCREEN_WIDTH // GRID_SIZE) - 1) * GRID_SIZE
            y = random.randint(0, (SCREEN_HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
            
            # Проверка, что еда не появляется на змейке
            if (x, y) not in snake.body:
                return (x, y)
    
    def draw(self, surface):
        """Рисование еды"""
        rect = pygame.Rect(self.position[0], self.position[1], GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.circle(surface, YELLOW, (self.position[0] + GRID_SIZE // 2, self.position[1] + GRID_SIZE // 2), 5)


class Game:
    """Основной класс игры"""
    def __init__(self):
        # Инициализация переменных игры
        self.snake = Snake()
        self.food = Food(self.snake)
        
        # Переменные уровня и скорости
        self.level = 1
        self.score = 0
        self.foods_eaten = 0
        self.foods_to_level_up = 3  # Количество еды для повышения уровня
        self.base_speed = 5
        self.current_speed = self.base_speed
        
        # Состояние игры
        self.game_over = False
        self.running = True
    
    def handle_events(self):
        """Обработка событий (клавиши, закрытие окна)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                # Управление змейкой стрелками
                if event.key == pygame.K_UP:
                    self.snake.set_direction((0, -GRID_SIZE))
                elif event.key == pygame.K_DOWN:
                    self.snake.set_direction((0, GRID_SIZE))
                elif event.key == pygame.K_LEFT:
                    self.snake.set_direction((-GRID_SIZE, 0))
                elif event.key == pygame.K_RIGHT:
                    self.snake.set_direction((GRID_SIZE, 0))
                
                # Перезагрузка при нажатии SPACE на экране Game Over
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.__init__()
    
    def update(self):
        """Обновление логики игры"""
        if not self.game_over:
            # Обновление позиции змейки
            self.snake.update()
            
            # Проверка столкновения со стеной
            if self.snake.check_wall_collision():
                self.game_over = True
            
            # Проверка столкновения с собственным телом
            if self.snake.check_collision_with_body():
                self.game_over = True
            
            # Проверка столкновения с едой
            if self.snake.get_head() == self.food.position:
                self.snake.grow()
                self.foods_eaten += 1
                self.score += 10
                self.food = Food(self.snake)
                
                # Проверка повышения уровня
                if self.foods_eaten % self.foods_to_level_up == 0:
                    self.level_up()
    
    def level_up(self):
        """Повышение уровня и увеличение скорости"""
        self.level += 1
        self.current_speed = self.base_speed + (self.level - 1) * 2
    
    def draw(self):
        """Рисование всех элементов игры"""
        # Заполнение экрана чёрным цветом
        screen.fill(BLACK)
        
        # Рисование змейки
        self.snake.draw(screen)
        
        # Рисование еды
        self.food.draw(screen)
        
        # Рисование информации (уровень, скор, счётчик еды)
        level_text = font.render(f"Level: {self.level}", True, BLUE)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        foods_text = small_font.render(f"Foods: {self.foods_eaten}/{self.level * self.foods_to_level_up}", True, YELLOW)
        
        screen.blit(level_text, (10, 10))
        screen.blit(score_text, (10, 50))
        screen.blit(foods_text, (10, 90))
        
        # Если игра закончена, показать Game Over
        if self.game_over:
            game_over_text = font.render("GAME OVER!", True, RED)
            restart_text = small_font.render("Press SPACE to restart", True, WHITE)
            final_score = small_font.render(f"Final Score: {self.score} | Level: {self.level}", True, WHITE)
            
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100))
            screen.blit(final_score, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 20))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))
        
        # Обновление экрана
        pygame.display.flip()
    
    def run(self):
        """Основной цикл игры"""
        while self.running:
            # Обработка событий
            self.handle_events()
            
            # Обновление логики
            self.update()
            
            # Рисование
            self.draw()
            
            # Контроль скорости (зависит от уровня)
            clock.tick(self.current_speed)
        
        # Выход из Pygame
        pygame.quit()
        sys.exit()


# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()
