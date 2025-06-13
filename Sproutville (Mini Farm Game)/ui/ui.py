import pygame


class GameUI:
    def __init__(self, screen, font_path=None):
        self.screen = screen
        self.font = pygame.font.Font(font_path, 26) if font_path else pygame.font.SysFont("Arial", 26,bold=True)

        self.money_bg = pygame.image.load("assets/sprites/ui/money_bg.png").convert_alpha()
        self.money_bg = pygame.transform.scale(self.money_bg, (200, 64))

        self.coin_icon = pygame.image.load("assets/sprites/ui/money.png").convert_alpha()
        self.coin_icon = pygame.transform.scale(self.coin_icon, (48, 48))

        self.health_levels = [0, 25, 50, 75, 100]
        self.stamina_levels = [0, 25, 50, 75, 100]

        target_size = (192, 48) #крок 48 та 16

        self.health_bars = {
            level: pygame.transform.scale(
                pygame.image.load(f"assets/sprites/ui/healthbar/health_{level}.png").convert_alpha(),
                target_size
            )
            for level in self.health_levels

        }

        self.stamina_bars = {
            level: pygame.transform.scale(
                pygame.image.load(f"assets/sprites/ui/staminabar/stamina_{level}.png").convert_alpha(),
                target_size
            )
            for level in self.stamina_levels

        }

    def get_closest_level(self, value, max_value, levels):
        percent = (value / max_value) * 100
        closest = min(levels, key=lambda lvl: abs(lvl - percent))
        return closest

    def draw_bar(self, x, y, value, max_value, color, bg_color, width=200, height=20):
        pygame.draw.rect(self.screen, bg_color, (x, y, width, height))
        fill_width = int((value / max_value) * width)
        pygame.draw.rect(self.screen, color, (x, y, fill_width, height))
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, width, height), 2)

    def render(self, health, max_health, stamina, max_stamina, money):

        health_level = self.get_closest_level(health, max_health, self.health_levels)
        stamina_level = self.get_closest_level(stamina, max_stamina, self.stamina_levels)

        self.screen.blit(self.health_bars[health_level], (10, 10))
        self.screen.blit(self.stamina_bars[stamina_level], (10, 40))

        # Coins
        self.screen.blit(self.money_bg, (10, 85))

        self.screen.blit(self.coin_icon, (35, 92))
        money_text = self.font.render(str(money), True, (255, 255, 255))
        self.screen.blit(money_text, (90, 100))
