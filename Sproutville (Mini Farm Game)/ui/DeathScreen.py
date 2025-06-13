import pygame
import settings
class DeathScreen:
    def __init__(self, screen, play_button_img, background_sprite):
        self.screen = screen
        self.play_button_img = play_button_img
        self.background_sprite = background_sprite
        self.font = pygame.font.SysFont(None, 36)

        self.background_sprite = pygame.transform.scale(
            self.background_sprite,
            (self.background_sprite.get_width() * 4, self.background_sprite.get_height() * 4)
        )
        self.bg_rect = self.background_sprite.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))

        self.play_button_img = pygame.transform.scale(
            self.play_button_img,
            (self.play_button_img.get_width() * 4, self.play_button_img.get_height() * 4)
        )
        self.play_button_rect = self.play_button_img.get_rect()
        self.play_button_rect.centerx = settings.SCREEN_WIDTH // 2
        self.play_button_rect.top = self.bg_rect.top + self.bg_rect.height - 70

    def draw(self):
        # Оновлення rect перед малюванням
        self.bg_rect = self.background_sprite.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
        self.play_button_rect = self.play_button_img.get_rect()
        self.play_button_rect.centerx = self.bg_rect.centerx
        self.play_button_rect.top = self.bg_rect.bottom - 70

        # Темна плівка
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Малюємо підложку і кнопку
        self.screen.blit(self.background_sprite, self.bg_rect)

        text_surface = self.font.render("Ви програли, хочете повторити ще раз?", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, self.bg_rect.top + 50))
        self.screen.blit(text_surface, text_rect)

        self.screen.blit(self.play_button_img, self.play_button_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_button_rect.collidepoint(event.pos):
                return True
        return False
