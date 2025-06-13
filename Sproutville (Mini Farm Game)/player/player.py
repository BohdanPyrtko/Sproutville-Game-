import pygame
import os
import settings
from .movement import manual_move
from .playerstats import PlayerStats
from ui import Hotbar

class Player:
    def __init__(self, grid_position):
        self.tile_size = 32
        self.grid_position = grid_position

        self.animations = {}
        self.load_all_animations("assets/sprites/player")

        self.animations_orig = {}
        for key, frames in self.animations.items():
            self.animations_orig[key] = frames.copy()

        self.direction = "down"
        self.moving = False
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 10

        self.image = self.animations["idle_down"][0]
        self.rect = self.image.get_rect(topleft=(grid_position[0] * self.tile_size, grid_position[1] * self.tile_size))

        self.stats = PlayerStats()
        self.collision_rects = []

    def get_scaled_frame(self, zoom):
        if self.moving:
            anim_key = self.direction  # 'left', 'right', 'up', 'down' — рух
        else:
            anim_key = f"idle_{self.direction}"  # 'idle_left' і т.п. — стояння

        frames = self.animations.get(anim_key, [])
        if not frames:
            # Якщо нема анімації, кинь помилку чи підстав дефолтний кадр
            raise ValueError(f"Анімації для ключа '{anim_key}' немає")

        # Впевнись, що current_frame у діапазоні
        if self.current_frame >= len(frames):
            self.current_frame = 0

        frame = frames[self.current_frame]

        scaled_frame = pygame.transform.scale(
            frame,
            (int(frame.get_width() * zoom), int(frame.get_height() * zoom))
        )
        return scaled_frame

    def load_all_animations(self, base_path):
        for folder_name in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder_name)
            if os.path.isdir(folder_path):
                frames = []
                for file_name in sorted(os.listdir(folder_path)):
                    if file_name.endswith(".png"):
                        full_path = os.path.join(folder_path, file_name)
                        image = pygame.image.load(full_path).convert_alpha()
                        frames.append(image)
                self.animations[folder_name] = frames

    def update_animation(self):
        if self.moving:
            self.animation_timer += 2
            if self.animation_timer % self.animation_speed == 0:
                frames = self.animations.get(self.direction, [])
                if frames:
                    self.current_frame = (self.current_frame + 1) % len(frames)
                    self.image = frames[self.current_frame]
        else:
            idle_key = f"idle_{self.direction}"
            if idle_key in self.animations:
                self.image = self.animations[idle_key][0]
            self.current_frame = 0
            self.animation_timer = 0

    def draw(self, surface, camera=None):
        if camera:
            pos = camera.apply(self.rect)
        else:
            pos = self.rect
        surface.blit(self.image, pos)

    def grid_to_pixel(self, grid_pos):
        return grid_pos[0] * self.tile_size, grid_pos[1] * self.tile_size

    def set_collision_rects(self, rects):
        self.collision_rects = rects

    def move_manual(self, direction):
        new_position = manual_move(self.grid_position, direction)
        new_pixel_pos = (new_position[0] * self.tile_size, new_position[1] * self.tile_size)
        new_rect = self.rect.copy()
        new_rect.topleft = new_pixel_pos

        # Перевірка колізії з тайлами-стінами
        for rect in self.collision_rects:
            if new_rect.colliderect(rect):
                self.moving = False
                return  # Колізія — не рухаємось

        # Якщо немає колізії — рухаємось
        self.grid_position = new_position
        self.rect.topleft = new_pixel_pos
        self.direction = direction
        self.moving = True
        self.update_animation()

    def valid_move(self, grid_pos):
        x, y = self.grid_to_pixel(grid_pos)
        return 0 <= x < settings.SCREEN_WIDTH and 0 <= y < settings.SCREEN_HEIGHT
