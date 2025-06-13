import pygame
import pytmx

class GameMap:
    def __init__(self, filename):
        self.tmx_data = pytmx.load_pygame(filename)
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight

        self.tile_size = self.tile_width

        self.collision_rects = []

        # Шукаємо колізії у тайлах на всіх шарах
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid == 0:
                        continue
                    tile_props = self.tmx_data.get_tile_properties_by_gid(gid)
                    if tile_props and tile_props.get("collision", False):
                        rect = pygame.Rect(x * self.tile_width, y * self.tile_height, self.tile_width, self.tile_height)
                        self.collision_rects.append(rect)

    def get_size(self):
        width = self.tmx_data.width * self.tile_width
        height = self.tmx_data.height * self.tile_height
        return width, height

    def draw(self, surface, camera):
        # Створюємо проміжну поверхню, розміром як камера (екран)
        temp_surf = pygame.Surface((camera.camera_rect.width, camera.camera_rect.height))

        # Заливаємо фон (щоб не було прозорих зон)
        temp_surf.fill((0, 0, 0))  # або інший колір фону

        # Малюємо тайли в координатах без зуму, але з урахуванням камери
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, image in layer.tiles():
                    # Позиція тайла у світі
                    world_x = x * self.tile_size
                    world_y = y * self.tile_size

                    # Позиція відносно камери (без масштабування)
                    pos_x = world_x - camera.offset.x
                    pos_y = world_y - camera.offset.y

                    # Якщо тайл попадає у область камери — малюємо
                    if -self.tile_size < pos_x < camera.camera_rect.width and -self.tile_size < pos_y < camera.camera_rect.height:
                        temp_surf.blit(image, (pos_x, pos_y))

        # Масштабуємо поверхню цілком
        scaled_surf = pygame.transform.smoothscale(temp_surf,
        (int(camera.camera_rect.width * camera.zoom),
        int(camera.camera_rect.height * camera.zoom)))

        # Виводимо на основний surface
        surface.blit(scaled_surf, (0, 0))

        # Для дебагу можна побачити колізійні зони червоними рамками
        #for rect in self.collision_rects:
        #    pygame.draw.rect(surface, (255, 0, 0), rect, 2)

    def get_collision_rects(self):
        return self.collision_rects

    def is_blocked(self, pos):
        x_px = int(pos.x * self.tile_size)
        y_px = int(pos.y * self.tile_size)

        mob_rect = pygame.Rect(x_px, y_px, self.tile_size, self.tile_size)

        for rect in self.collision_rects:
            if mob_rect.colliderect(rect):
                return True
        return False
