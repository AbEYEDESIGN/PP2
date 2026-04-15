import pygame
import os

class Player:
    def __init__(self, music_dir="music"):
        pygame.mixer.init()
        # загружаем все wav/mp3 файлы из папки
        self.tracks = [
            os.path.join(music_dir, f)
            for f in os.listdir(music_dir)
            if f.endswith((".wav", ".mp3"))
        ]
        self.index = 0
        self.playing = False
        self.index = 0
        self.playing = False
        self.stopped_manually = False         

    def play(self):
        if not self.tracks:
            return
        pygame.mixer.music.load(self.tracks[self.index])
        pygame.mixer.music.play()
        self.playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False

    def next(self):
        # переходим к следующему треку по кругу
        self.index = (self.index + 1) % len(self.tracks)
        self.play()

    def prev(self):
        # переходим к предыдущему треку по кругу
        self.index = (self.index - 1) % len(self.tracks)
        self.play()

    def current_name(self):
        if not self.tracks:
            return "треки не найдены"
        return os.path.basename(self.tracks[self.index])