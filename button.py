import pygame

class Button:
    def __init__(self, x, y, w, h, text, font, bg_color, text_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = font.render(text, True, text_color)
        self.bg_color = bg_color
        self.text_color = text_color
        self.font = font

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=10)
        text_x = self.rect.x + (self.rect.w - self.text.get_width()) // 2
        text_y = self.rect.y + (self.rect.h - self.text.get_height()) // 2
        screen.blit(self.text, (text_x, text_y))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
