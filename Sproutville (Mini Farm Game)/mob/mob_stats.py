# mobs/mob_stats.py
import pygame
import os

from pygame import Surface

def load_animation_frames(folder_path):
    frames = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith('.png'):
            path = os.path.join(folder_path, filename)
            image = pygame.image.load(path).convert_alpha()
            frames.append(image)
    return frames

def load_mob_animations(base_path='assets/mob'):
    directions = ["down", "up", "left", "right",
                  "attack_down", "attack_up", "attack_left", "attack_right"]
    animations = {}
    for direction in directions:
        path = os.path.join(base_path, direction)
        animations[direction] = load_animation_frames(path)
    return animations

# Параметри для "slime"
slime_animations = load_mob_animations("assets/sprites/mob/slime")


mob_stats = {
    "slime": {
        "speed": 1.5,
        "attack_power": 25,
        "hp": 80,
        "animations": slime_animations
    },
    "skeleton": {
    }
}
