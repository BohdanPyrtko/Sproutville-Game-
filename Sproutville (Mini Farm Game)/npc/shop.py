import json
import os
import pygame
from utils.helpers import load_json, sort_list, search_list

class Shop:
    def __init__(self, player, hotbar):
        items_path = os.path.join("utils", "items.json")
        with open(items_path, "r", encoding="utf-8") as f:
            raw_item_data = json.load(f)

        # Завантажуємо іконки у pygame.Surface
        self.item_data = load_json(os.path.join("utils", "items.json"))
        for item_id, data in raw_item_data.items():
            icon_path = os.path.join("assets", "sprites", "items", "icons", data["sprite"])
            icon_surface = pygame.image.load(icon_path).convert_alpha()
            self.item_data[item_id] = {
                "name": data["name"],
                "price": data.get("price", 10),  # ціна за замовчуванням
                "icon": icon_surface
            }

        shop_data = load_json(os.path.join("utils", "shop_items.json"))
        self.all_items_for_sale = shop_data.get("items_for_sale", [])
        self.items_for_sale = list(self.all_items_for_sale)  # копія для фільтрації і сортування

        self.is_open = False
        self.font = pygame.font.Font(None, 24)
        self.rect = pygame.Rect(100, 100, 320, 450)  # збільшив трохи по висоті
        self.selected_index = 0
        self.player = player
        self.hotbar = hotbar

        self.search_text = ""
        self.sort_ascending = True  # стан сортування

    def toggle(self):
        self.is_open = not self.is_open
        if self.is_open:
            # при відкритті скидаємо пошук і сортування
            self.search_text = ""
            self.items_for_sale = list(self.all_items_for_sale)
            self.sort_items_for_sale(self.sort_ascending)
            self.selected_index = 0

    def sort_items_for_sale(self, ascending=True):
        self.items_for_sale.sort(
            key=lambda item_id: self.item_data[item_id]["name"],
            reverse=not ascending
        )

    def filter_items(self, search_text):
        search_text = search_text.lower()
        self.items_for_sale = [
            item_id for item_id in self.all_items_for_sale
            if search_text in self.item_data[item_id]["name"].lower()
        ]
        self.selected_index = 0

    def handle_event(self, event):
        if not self.is_open:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.items_for_sale:
                    self.selected_index = (self.selected_index - 1) % len(self.items_for_sale)
            elif event.key == pygame.K_DOWN:
                if self.items_for_sale:
                    self.selected_index = (self.selected_index + 1) % len(self.items_for_sale)
            elif event.key == pygame.K_RETURN:
                self.buy_selected_item()
            elif event.key == pygame.K_BACKSPACE:
                if len(self.search_text) > 0:
                    self.search_text = self.search_text[:-1]
                    self.filter_items(self.search_text)
            else:
                # Проста обробка текстового вводу для пошуку
                if event.unicode.isprintable():
                    self.search_text += event.unicode
                    self.filter_items(self.search_text)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            sort_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 75, 100, 25)
            if sort_rect.collidepoint(mouse_pos):
                # переключаємо порядок сортування
                self.sort_ascending = not self.sort_ascending
                self.sort_items_for_sale(self.sort_ascending)

    def buy_selected_item(self):
        if not self.items_for_sale:
            return
        item_id = self.items_for_sale[self.selected_index]
        item = self.item_data[item_id]
        price = item["price"]

        if self.player.stats.money >= price:
            self.player.stats.money -= price
            self.hotbar.add_item(item_id)
            print(f"Куплено: {item['name']} за {price} монет")
        else:
            print("Недостатньо грошей")

    def draw(self, surface):
        if not self.is_open:
            return

        pygame.draw.rect(surface, (50, 50, 50), self.rect)

        # Заголовок
        title = self.font.render("Магазин", True, (255, 255, 255))
        surface.blit(title, (self.rect.x + 10, self.rect.y + 10))

        # Поле пошуку
        search_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 40, 300, 25)
        pygame.draw.rect(surface, (100, 100, 100), search_rect)
        search_text_surf = self.font.render(self.search_text, True, (255, 255, 255))
        surface.blit(search_text_surf, (search_rect.x + 5, search_rect.y + 5))

        # Кнопка сортування
        sort_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 75, 120, 25)
        pygame.draw.rect(surface, (70, 70, 150), sort_rect)
        sort_text = "Сортувати ^" if self.sort_ascending else "Сортувати v"
        sort_text_surf = self.font.render(sort_text, True, (255, 255, 255))
        surface.blit(sort_text_surf, (sort_rect.x + 10, sort_rect.y + 5))

        # Список товарів
        x, y = self.rect.x + 10, self.rect.y + 110
        item_height = 40
        highlight_color = (255, 255, 0)

        for idx, item_id in enumerate(self.items_for_sale):
            item = self.item_data[item_id]
            item_rect = pygame.Rect(x, y + idx * item_height, 300, item_height)

            if idx == self.selected_index:
                pygame.draw.rect(surface, highlight_color, item_rect.inflate(10, 5), 3)

            icon = item["icon"]
            icon_rect = icon.get_rect(topleft=(x + 5, y + idx * item_height + 5))
            surface.blit(icon, icon_rect)

            name_surf = self.font.render(item["name"], True, (255, 255, 255))
            surface.blit(name_surf, (x + 50, y + idx * item_height + 10))

            if idx == self.selected_index:
                price_text = f"Ціна: {item['price']}"
                price_surf = self.font.render(price_text, True, (255, 255, 255))
                surface.blit(price_surf, (x + 200, y + idx * item_height + 10))
