import pygame
import datetime
import os
import math

class MickeyClock:
    def __init__(self, screen_width, screen_height):
        self.center = (screen_width // 2, screen_height // 2)
        
        # задаем длину стрелок
        self.sec_len = 180
        self.min_len = 140
        
        # настройка углов для корректного отображения кистей
        self.fist_offset_min = 180    
        self.fist_offset_sec = 0 
        
        # получение путей к изображениям
        current_path = os.path.dirname(__file__)
        path_right = os.path.join(current_path, "images", "right_hand.png")
        path_left = os.path.join(current_path, "images", "left_hand.png")

        # загрузка и масштабирование графических ресурсов
        try:
            original_right = pygame.image.load(path_right).convert_alpha()
            original_left = pygame.image.load(path_left).convert_alpha()

            self.min_fist = pygame.transform.scale(original_right, (60, 40))
            self.sec_fist = pygame.transform.scale(original_left, (70, 30))
        except FileNotFoundError:
            self.min_fist = pygame.Surface((1, 1), pygame.SRCALPHA)
            self.sec_fist = pygame.Surface((1, 1), pygame.SRCALPHA)

    def draw(self, surface):
        # получение системного времени
        now = datetime.datetime.now()
        minutes = now.minute
        seconds = now.second

        # очистка фона и отрисовка циферблата
        surface.fill((255, 255, 255))
        pygame.draw.circle(surface, (0, 0, 0), self.center, 220, 4)
        pygame.draw.circle(surface, (0, 0, 0), self.center, 10)

        # вычисление углов поворота для секунд и минут
        sec_angle_deg = 90 - (seconds * 12)
        min_angle_deg = 90 - (minutes * 6)

        # отрисовка стрелок с кистями
        self._draw_arm_with_fist(surface, self.min_len, min_angle_deg, self.min_fist, self.fist_offset_min)
        self._draw_arm_with_fist(surface, self.sec_len, sec_angle_deg, self.sec_fist, self.fist_offset_sec)

    def _draw_arm_with_fist(self, surface, length, angle_deg, fist_image, offset_deg):
        # перевод углов в радианы для расчета координат
        angle_rad = math.radians(angle_deg)
        end_x = self.center[0] + length * math.cos(angle_rad)
        end_y = self.center[1] - length * math.sin(angle_rad)

        # рисование основной линии стрелки
        pygame.draw.line(surface, (0, 0, 0), self.center, (end_x, end_y), 8)

        # поворот кисти и расчет позиции на конце стрелки
        final_angle = angle_deg + offset_deg
        rotated_fist = pygame.transform.rotate(fist_image, final_angle)
        new_rect = rotated_fist.get_rect(center=(end_x, end_y))
        
        surface.blit(rotated_fist, new_rect.topleft)