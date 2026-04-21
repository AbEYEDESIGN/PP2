import pygame
import sys

# Инициализация Pygame
pygame.init()

# Константы для экрана
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TOOLBAR_HEIGHT = 100
DRAWING_AREA_HEIGHT = SCREEN_HEIGHT - TOOLBAR_HEIGHT
FPS = 60

# Цвета (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paint Application")

# Часы для контроля FPS
clock = pygame.time.Clock()

# Шрифт для отображения текста
font = pygame.font.Font(None, 24)


class ColorButton:
    """Класс для кнопок выбора цвета"""
    def __init__(self, x, y, color, label):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.color = color
        self.label = label
        self.selected = False
    
    def draw(self, surface):
        """Рисование кнопки цвета"""
        # Рисование квадрата с цветом
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Если кнопка выбрана, нарисовать белую границу
        if self.selected:
            pygame.draw.rect(surface, WHITE, self.rect, 3)
        else:
            pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        # Рисование метки
        label_text = font.render(self.label, True, BLACK)
        surface.blit(label_text, (self.rect.x - 10, self.rect.y + 45))
    
    def is_clicked(self, pos):
        """Проверка, нажата ли кнопка"""
        return self.rect.collidepoint(pos)


class ToolButton:
    """Класс для кнопок инструментов"""
    def __init__(self, x, y, width, height, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.selected = False
    
    def draw(self, surface):
        """Рисование кнопки инструмента"""
        # Цвет фона кнопки
        bg_color = LIGHT_GRAY if self.selected else WHITE
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        # Рисование текста
        label_text = font.render(self.label, True, BLACK)
        text_rect = label_text.get_rect(center=self.rect.center)
        surface.blit(label_text, text_rect)
    
    def is_clicked(self, pos):
        """Проверка, нажата ли кнопка"""
        return self.rect.collidepoint(pos)


class Paint:
    """Основной класс приложения Paint"""
    def __init__(self):
        # Создание полотна для рисования
        self.canvas = pygame.Surface((SCREEN_WIDTH, DRAWING_AREA_HEIGHT))
        self.canvas.fill(WHITE)
        
        # Инструменты рисования
        self.tools = {
            'pen': ToolButton(10, 10, 80, 40, 'Pen'),
            'rectangle': ToolButton(100, 10, 100, 40, 'Rectangle'),
            'circle': ToolButton(210, 10, 80, 40, 'Circle'),
            'eraser': ToolButton(300, 10, 80, 40, 'Eraser')
        }
        self.current_tool = 'pen'
        self.tools['pen'].selected = True
        
        # Кнопка очищения полотна
        self.clear_button = ToolButton(450, 10, 80, 40, 'Clear')
        
        # Кнопки выбора цвета
        self.color_buttons = [
            ColorButton(10, 60, BLACK, 'BK'),
            ColorButton(60, 60, RED, 'R'),
            ColorButton(110, 60, GREEN, 'G'),
            ColorButton(160, 60, BLUE, 'B'),
            ColorButton(210, 60, YELLOW, 'Y'),
            ColorButton(260, 60, PURPLE, 'P'),
            ColorButton(310, 60, ORANGE, 'O'),
            ColorButton(360, 60, CYAN, 'C'),
            ColorButton(410, 60, PINK, 'PK'),
        ]
        self.color_buttons[0].selected = True
        self.current_color = BLACK
        
        # Переменные для отслеживания рисования
        self.drawing = False
        self.start_pos = None
        self.brush_size = 5
        self.eraser_size = 20
        
        # Главный цикл
        self.running = True
    
    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Нажатие мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                
                # Проверка нажатия кнопок инструментов
                for tool_name, tool_button in self.tools.items():
                    if tool_button.is_clicked(pos):
                        # Снять выделение со старого инструмента
                        self.tools[self.current_tool].selected = False
                        # Выделить новый инструмент
                        self.current_tool = tool_name
                        self.tools[tool_name].selected = True
                
                # Проверка нажатия кнопки очистки
                if self.clear_button.is_clicked(pos):
                    self.canvas.fill(WHITE)
                
                # Проверка нажатия кнопок цвета
                for color_button in self.color_buttons:
                    if color_button.is_clicked(pos):
                        # Снять выделение со старой кнопки цвета
                        for cb in self.color_buttons:
                            cb.selected = False
                        # Выделить новую кнопку цвета
                        color_button.selected = True
                        self.current_color = color_button.color
                
                # Начало рисования, если нажимают на полотне
                if pos[1] < DRAWING_AREA_HEIGHT:
                    self.drawing = True
                    self.start_pos = pos
            
            # Отпускание мыши
            if event.type == pygame.MOUSEBUTTONUP:
                self.drawing = False
            
            # Движение мыши во время рисования
            if event.type == pygame.MOUSEMOTION and self.drawing:
                current_pos = event.pos
                
                # Рисование в зависимости от выбранного инструмента
                if self.current_tool == 'pen':
                    self.draw_line(self.start_pos, current_pos, self.current_color, self.brush_size)
                    self.start_pos = current_pos
                
                elif self.current_tool == 'eraser':
                    self.erase(current_pos, self.eraser_size)
                    self.start_pos = current_pos
            
            # Отпускание мыши для прямоугольника и круга (рисуем фигуру)
            if event.type == pygame.MOUSEBUTTONUP and self.drawing == False:
                if self.current_tool == 'rectangle' and self.start_pos is not None:
                    current_pos = event.pos
                    if current_pos[1] < DRAWING_AREA_HEIGHT:
                        self.draw_rectangle(self.start_pos, current_pos, self.current_color)
                        self.start_pos = None
                
                elif self.current_tool == 'circle' and self.start_pos is not None:
                    current_pos = event.pos
                    if current_pos[1] < DRAWING_AREA_HEIGHT:
                        self.draw_circle(self.start_pos, current_pos, self.current_color)
                        self.start_pos = None
    
    def draw_line(self, start_pos, end_pos, color, width):
        """Рисование линии (для инструмента Pen)"""
        pygame.draw.line(self.canvas, color, start_pos, end_pos, width)
    
    def draw_rectangle(self, start_pos, end_pos, color):
        """Рисование прямоугольника"""
        # Расчёт координат прямоугольника
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Убедиться, что x1 < x2 и y1 < y2
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        # Рисование прямоугольника
        pygame.draw.rect(self.canvas, color, (x, y, width, height), 3)
    
    def draw_circle(self, start_pos, end_pos, color):
        """Рисование круга"""
        # Расчёт центра и радиуса
        center_x = (start_pos[0] + end_pos[0]) // 2
        center_y = (start_pos[1] + end_pos[1]) // 2
        radius = int(((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2) ** 0.5 / 2)
        
        # Рисование круга
        pygame.draw.circle(self.canvas, color, (center_x, center_y), radius, 3)
    
    def erase(self, pos, size):
        """Стирание части полотна (замена на белый цвет)"""
        pygame.draw.circle(self.canvas, WHITE, pos, size)
    
    def draw_ui(self):
        """Рисование пользовательского интерфейса"""
        # Заполнение области панели инструментов серым цветом
        toolbar_area = pygame.Rect(0, DRAWING_AREA_HEIGHT, SCREEN_WIDTH, TOOLBAR_HEIGHT)
        pygame.draw.rect(screen, LIGHT_GRAY, toolbar_area)
        pygame.draw.line(screen, BLACK, (0, DRAWING_AREA_HEIGHT), (SCREEN_WIDTH, DRAWING_AREA_HEIGHT), 2)
        
        # Рисование кнопок инструментов
        for tool_button in self.tools.values():
            tool_button.draw(screen)
        
        # Рисование кнопки очистки
        self.clear_button.draw(screen)
        
        # Рисование текста для выбора цвета
        color_label = font.render("Colors:", True, BLACK)
        screen.blit(color_label, (10, DRAWING_AREA_HEIGHT + 55))
        
        # Рисование кнопок цвета
        for color_button in self.color_buttons:
            color_button.draw(screen)
        
        # Рисование текущего инструмента
        tool_info = font.render(f"Tool: {self.current_tool.capitalize()}", True, BLACK)
        screen.blit(tool_info, (SCREEN_WIDTH - 200, DRAWING_AREA_HEIGHT + 10))
    
    def draw(self):
        """Рисование всех элементов приложения"""
        # Вывод полотна на экран
        screen.blit(self.canvas, (0, 0))
        
        # Рисование пользовательского интерфейса
        self.draw_ui()
        
        # Обновление экрана
        pygame.display.flip()
    
    def run(self):
        """Основной цикл приложения"""
        while self.running:
            # Обработка событий
            self.handle_events()
            
            # Рисование
            self.draw()
            
            # Контроль FPS
            clock.tick(FPS)
        
        # Выход из Pygame
        pygame.quit()
        sys.exit()


# Запуск приложения
if __name__ == "__main__":
    paint = Paint()
    paint.run()
