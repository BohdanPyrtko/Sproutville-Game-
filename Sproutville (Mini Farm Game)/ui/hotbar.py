import pygame
import json

import os



class Hotbar:
    def __init__(self, item_data_path, sprite_folder, hotbar_sprite_path, screen_width, screen_height):
        self.slots = [None] * 10
        self.active_slot_index = 0
        with open(item_data_path, 'r') as f:
            self.item_data = json.load(f)

        self.item_sprites = {}
        self.load_item_sprites(sprite_folder)

        self.slot_size = 40
        self.slot_margin = 6

        self.hotbar_image = pygame.image.load(hotbar_sprite_path).convert_alpha()
        self.hotbar_image = pygame.transform.scale(self.hotbar_image, (self.slot_size * 10 + self.slot_margin * 9 + 24, 64))
        self.hotbar_rect = self.hotbar_image.get_rect()

    def update_position(self, screen_width, screen_height):
        self.hotbar_rect.centerx = screen_width // 2
        self.hotbar_rect.bottom = screen_height - 10

    def load_item_sprites(self, folder):
        for item_id, data in self.item_data.items():
            if "sprite" in data:
                path = os.path.join(folder, data["sprite"])
                if os.path.exists(path):
                    sprite = pygame.image.load(path).convert_alpha()
                    self.item_sprites[item_id] = sprite
                else:
                    print(f"Sprite file not found: {path}")

    def add_item(self, item_id, amount=1):
        # Шукаємо слот, де вже є такий предмет
        for i in range(10):
            slot = self.slots[i]
            if slot and slot['item_id'] == item_id:
                slot['count'] += amount
                return

        # Якщо нема — шукаємо порожній слот
        for i in range(10):
            if self.slots[i] is None:
                self.slots[i] = {'item_id': item_id, 'count': amount}
                return

        print("Hotbar is full!")

    def select_slot(self, index):
        if 0 <= index < 10:
            self.active_slot_index = index

    def get_active_item(self):
        item_id = self.slots[self.active_slot_index]
        return self.item_data.get(item_id) if item_id else None

    def use_item(self, slot_index, player):
        if not (0 <= slot_index < 10):
            return
        slot = self.slots[slot_index]
        if slot is None:
            return

        item_id = slot['item_id']
        item = self.item_data[item_id]

        if item['type'] == 'consumable':
            player.stats.heal(item['heal_amount'])
            print(f"Used {item['name']}, healed {item['heal_amount']} HP")
            slot['count'] -= 1
            if slot['count'] <= 0:
                self.slots[slot_index] = None

        elif item['type'] == 'weapon':
            player.equip_weapon(item_id)
            print(f"Equipped {item['name']}")

    def draw(self, surface):
        # Малюємо фон хотбару
        surface.blit(self.hotbar_image, self.hotbar_rect)

        # Розрахунок координат слотів
        start_x = self.hotbar_rect.left + 12
        y = self.hotbar_rect.top + 10
        for i in range(10):
            x = start_x + i * (self.slot_size + self.slot_margin)

            # Підсвічування активного слота
            if i == self.active_slot_index:
                pygame.draw.rect(surface, (255, 255, 0), (x - 2, y - 2, self.slot_size + 4, self.slot_size + 4), 2)

            # Спрайт предмета
            slot_data = self.slots[i]
            if slot_data and slot_data['item_id'] in self.item_sprites:
                item_id = slot_data['item_id']
                icon = self.item_sprites[item_id]
                icon_rect = icon.get_rect(center=(x + self.slot_size // 2, y + self.slot_size // 2))
                surface.blit(icon, icon_rect)

            if isinstance(self.slots[i], dict) and self.slots[i]['count'] > 1:
                font = pygame.font.SysFont(None, 18)
                count_text = font.render(str(self.slots[i]['count']), True, (255, 255, 255))
                surface.blit(count_text, (x + self.slot_size - 14, y + self.slot_size - 16))
