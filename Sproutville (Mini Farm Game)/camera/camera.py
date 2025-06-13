import pygame


class Camera:
    def __init__(self, screen_width, screen_height, world_width, world_height, margin=100):
        self.offset = pygame.Vector2(0, 0)
        self.camera_rect = pygame.Rect(0, 0, screen_width, screen_height)
        self.margin = margin
        self.world_width = world_width
        self.world_height = world_height
        self.zoom = 1.0  # новий параметр — масштаб

    def update(self, target_rect):
        # Центр гравця
        target_center_x = target_rect.centerx
        target_center_y = target_rect.centery

        # Центр екрана з урахуванням масштабу
        half_screen_width = self.camera_rect.width / (2 * self.zoom)
        half_screen_height = self.camera_rect.height / (2 * self.zoom)

        # Камера центрована на гравця
        cam_x = target_center_x - half_screen_width
        cam_y = target_center_y - half_screen_height

        # Обмежуємо межами світу (щоб камера не вилізла за карту)
        cam_x = max(0, min(cam_x, self.world_width - self.camera_rect.width / self.zoom))
        cam_y = max(0, min(cam_y, self.world_height - self.camera_rect.height / self.zoom))

        # Зберігаємо offset (в координатах світу, без зуму)
        self.offset.x = cam_x
        self.offset.y = cam_y

    def apply(self, rect):
        return pygame.Rect(
            int((rect.x - self.offset.x) * self.zoom),
            int((rect.y - self.offset.y) * self.zoom),
            int(rect.width * self.zoom),
            int(rect.height * self.zoom)
        )

    def apply_surface(self, surface):
        return surface


    def change_zoom(self, delta):
        self.zoom += delta
        self.zoom = max(0.5, min(2.5, self.zoom))  # обмеження зуму

    def draw(self, surface, camera):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, image in layer.tiles():
                    pos = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                    image_scaled = camera.apply_surface(image)
                    pos_scaled = camera.apply(pos)
                    surface.blit(image_scaled, pos_scaled)
