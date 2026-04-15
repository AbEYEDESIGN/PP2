class Ball:
    def __init__(self, x, y, radius, screen_w, screen_h):
        self.x = x
        self.y = y
        self.radius = radius
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.step = 20  # шаг движения в пикселях

    def move(self, dx, dy):
        # считаем новую позицию до применения
        new_x = self.x + dx * self.step
        new_y = self.y + dy * self.step

        # двигаем только если мяч остаётся в границах экрана
        if self.radius <= new_x <= self.screen_w - self.radius:
            self.x = new_x
        if self.radius <= new_y <= self.screen_h - self.radius:
            self.y = new_y
            