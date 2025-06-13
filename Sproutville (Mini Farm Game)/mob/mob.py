import pygame
import random

from player import Player,PlayerStats
from player import player,playerstats

class Mob(pygame.sprite.Sprite):
    TILE_SIZE = 32

    def __init__(self, spawn_pos, animations, speed=1, attack_power=1, hp=100):
        super().__init__()
        self.grid_position = pygame.Vector2(spawn_pos)
        self.spawn_point = self.grid_position.copy()

        self.animations = animations
        self.current_direction = "down"
        self.frame_index = 0

        # Окремі швидкості анімації
        self.walk_animation_speed = 0.15
        self.attack_animation_speed = 0.3

        self.image = self.animations[self.current_direction][0]
        self.rect = self.image.get_rect()
        self.rect.center = (self.grid_position.x * self.TILE_SIZE + self.TILE_SIZE // 2,
                            self.grid_position.y * self.TILE_SIZE + self.TILE_SIZE // 2)

        self.speed = speed
        self.attack_power = attack_power
        self.hp = hp

        # Таймери та стани
        self.state = "idle"
        self.wander_pause_timer = 0
        self.wander_target = self.spawn_point.copy()
        self.failed_moves = 0
        self.max_failed_moves = 30

        self.detect_radius = 3
        self.max_chase_distance = 5

        self.attack_cooldown = 1.0
        self.attack_timer = 0

    def update(self, player, dt, game_map):
        player_vec = pygame.Vector2(player.grid_position)

        # Стейт-машина
        if self.state in ["idle", "wandering"]:
            if self.can_see_player(player_vec):
                self.state = "chasing"
            else:
                self.wander_behavior(dt, game_map)

        elif self.state == "chasing":
            distance = self.grid_position.distance_to(player_vec)
            if distance <= 1.0:
                self.state = "attacking"
                self.attack_timer = 0
                self.perform_attack(player)  # передаємо об’єкт player
            elif self.too_far_from_spawn(player_vec):
                self.state = "returning"
            else:
                self.move_towards(player_vec, dt, game_map)

        elif self.state == "returning":
            if self.can_see_player(player_vec):
                self.state = "chasing"
            elif self.grid_position.distance_to(self.spawn_point) <= 0.2:
                self.grid_position = self.spawn_point.copy()
                self.state = "idle"
            else:
                self.move_towards(self.spawn_point, dt, game_map)

        elif self.state == "attacking":
            distance = self.grid_position.distance_to(player_vec)
            if distance > 1.0:
                self.state = "chasing"
            else:
                self.attack_timer += dt
                if self.attack_timer >= self.attack_cooldown:
                    self.attack_timer = 0
                    self.perform_attack(player)  # знову передаємо player

        self.animate(dt)
        self.update_rect()

    def can_see_player(self, player_vec):
        return self.grid_position.distance_to(player_vec) <= self.detect_radius

    def too_far_from_spawn(self, player_vec):
        return self.spawn_point.distance_to(player_vec) > self.max_chase_distance

    def perform_attack(self, player):
        self.current_direction = self.get_direction_to_target(player.grid_position)
        player.stats.take_damage(self.attack_power)

    def wander_behavior(self, dt, game_map):
        distance_to_target = (self.grid_position - self.wander_target).length()

        if distance_to_target < 0.1:
            self.wander_pause_timer += dt
            if self.wander_pause_timer >= 2.0:
                self.wander_pause_timer = 0
                self.choose_new_wander_target(game_map)
        else:
            self.wander_pause_timer = 0
            moved = self.move_towards(self.wander_target, dt, game_map)
            if not moved:
                self.failed_moves += 1
            else:
                self.failed_moves = 0

            if self.failed_moves > self.max_failed_moves:
                self.failed_moves = 0
                self.choose_new_wander_target(game_map)

    def choose_new_wander_target(self, game_map):
        max_distance = 5
        for _ in range(10):
            offset = pygame.Vector2(random.randint(-2, 2), random.randint(-2, 2))
            target = self.spawn_point + offset
            # Перевірка меж і колізії на тайлі
            if target.distance_to(self.spawn_point) <= max_distance and not game_map.is_blocked(target):
                self.wander_target = target
                return
        self.wander_target = self.spawn_point.copy()

    def move_towards(self, target_vec, dt, game_map):
        direction_vec = target_vec - self.grid_position
        if direction_vec.length() == 0:
            return True

        direction = direction_vec.normalize()
        step = direction * self.speed * dt
        new_pos = self.grid_position + step

        # Перевірка колізії на новій позиції
        if not game_map.is_blocked(new_pos):
            self.grid_position = new_pos
            self.update_direction(direction)
            return True
        return False

    def update_direction(self, dir_vec):
        if abs(dir_vec.x) > abs(dir_vec.y):
            self.current_direction = "right" if dir_vec.x > 0 else "left"
        else:
            self.current_direction = "down" if dir_vec.y > 0 else "up"

    def get_direction_to_target(self, target_vec):
        direction = target_vec - self.grid_position
        if abs(direction.x) > abs(direction.y):
            return "right" if direction.x > 0 else "left"
        else:
            return "down" if direction.y > 0 else "up"

    def animate(self, dt):
        if self.state == "attacking" and f"attack_{self.current_direction}" in self.animations:
            frames = self.animations[f"attack_{self.current_direction}"]
            animation_speed = self.attack_animation_speed
        else:
            frames = self.animations[self.current_direction]
            animation_speed = self.walk_animation_speed

        self.frame_index += animation_speed
        if self.frame_index >= len(frames):
            self.frame_index = 0

        self.image = frames[int(self.frame_index)]

        self.image = frames[int(self.frame_index)]

    def update_rect(self):
        self.rect = self.image.get_rect()
        self.rect.center = (self.grid_position.x * self.TILE_SIZE + self.TILE_SIZE // 2,
                            self.grid_position.y * self.TILE_SIZE + self.TILE_SIZE // 2)

    def draw(self, surface, camera):
        scaled_image = pygame.transform.scale(
            self.image,
            (int(self.rect.width * camera.zoom), int(self.rect.height * camera.zoom))
        )
        scaled_rect = camera.apply(self.rect)
        surface.blit(scaled_image, scaled_rect)
