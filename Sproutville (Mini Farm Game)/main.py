# Точка входу в гру
# Ініціалізація PyGame, створення вікна, головний ігровий цикл
import pygame
import sys
import settings

from map import GameMap
from player import Player
from camera import Camera
from ui import GameUI,Hotbar
from npc import Shop
from ui import DeathScreen

def calculate_zoom(screen_width, screen_height, map_width, map_height, tile_size):
    map_width_px = map_width * tile_size
    map_height_px = map_height * tile_size

    zoom_min = min(screen_width / map_width_px, screen_height / map_height_px)

    zoom_max = 3
    default_zoom = 1.0

    zoom = max(min(default_zoom, zoom_max), zoom_min)

    return zoom, zoom_min, zoom_max


def main():


    # --------------------------------------------------
    #               1. Ініціалізація PyGame
    # --------------------------------------------------

    pygame.init()

    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
        pygame.RESIZABLE
    )


    pygame.display.set_caption("Mini Farm Game")

    clock = pygame.time.Clock()


    # --------------------------------------------------
    #       2. Завантаження карти, гравця, мобів
    # --------------------------------------------------

    game_map = GameMap("map.tmx")



    start_pos = (25, 25)
    player = Player(start_pos)
    player.set_collision_rects(game_map.get_collision_rects())

    map_width_px, map_height_px = game_map.get_size()
    map_width = game_map.tmx_data.width
    map_height = game_map.tmx_data.height
    tile_size = game_map.tile_width

    camera = Camera(
        screen_width=settings.SCREEN_WIDTH,
        screen_height=settings.SCREEN_HEIGHT,
        world_width=map_width_px,
        world_height=map_height_px
    )

    camera_zoom = calculate_zoom(screen.get_width(), screen.get_height(), map_width, map_height, tile_size)
    camera.update(player.rect)

    ui = GameUI(screen)

    from mob import Mob
    from mob import mob_stats

    mobs_data = mob_stats

    mob = Mob((20, 20), mobs_data["slime"]["animations"],
              speed=mobs_data["slime"]["speed"],
              attack_power=mobs_data["slime"]["attack_power"],
              hp=mobs_data["slime"]["hp"])

    hotbar = Hotbar("utils/items.json", "assets/sprites/items/icons", "assets/sprites/ui/hotbar.png",
                    settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)

    hotbar.add_item("health_potion", amount=3)
    hotbar.add_item("sword")

    shop = Shop(player, hotbar)

    play_button_img = pygame.image.load('assets/sprites/ui/play_button.png').convert_alpha()
    bg_sprite = pygame.image.load('assets/sprites/ui/death_background.png').convert_alpha()
    death_screen = DeathScreen(screen, play_button_img, bg_sprite)

    game_over = False
    # ------------------------------------------------------------------------------------
    #               3. Основний ігровий цикл: обробка подій, оновлення, рендеринг
    # ------------------------------------------------------------------------------------

    running = True
    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    camera.change_zoom(0.1)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    camera.change_zoom(-0.1)
                elif event.key == pygame.K_e:
                    shop.toggle()
                    print("E pressed, toggling shop")



            elif event.type == pygame.VIDEORESIZE:
                settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                camera_zoom = calculate_zoom(screen.get_width(), screen.get_height(), map_width, map_height, tile_size)
                camera.camera_rect.width = event.w
                camera.camera_rect.height = event.h
                hotbar.update_position(event.w, event.h)

                # Автозум на основі нового розміру
                base_tile_size = game_map.tile_size
                zoom_x = event.w / (base_tile_size * 20)  # 20 тайлів по ширині
                zoom_y = event.h / (base_tile_size * 11)  # 11 тайлів по висоті
                camera.zoom = min(zoom_x, zoom_y)


            shop.handle_event(event)

            if game_over:
                if death_screen.handle_event(event):
                    player.stats.health = 100
                    game_over = False

        keys = pygame.key.get_pressed()
        for i in range(1, 11):  # 1 to 10
            key_code = getattr(pygame, f'K_{i % 10}')  # 1–9, 0 для 10
            if keys[key_code]:
                hotbar.select_slot(i - 1)




        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player.move_manual("up")
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player.move_manual("down")
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player.move_manual("left")
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player.move_manual("right")
        else:
            player.moving = False
            player.update_animation()



        screen.fill((settings.BLACK))
        camera.update(player.rect)

        game_map.draw(screen, camera)

        player_image_scaled = player.get_scaled_frame(camera.zoom)

        pos_x = player.grid_position[0] * player.tile_size * camera.zoom - camera.offset.x * camera.zoom
        pos_y = player.grid_position[1] * player.tile_size * camera.zoom - camera.offset.y * camera.zoom

        screen.blit(player_image_scaled, (pos_x, pos_y))

        mob.update(player, dt, game_map)
        mob.draw(screen, camera)

        ui.render(
            player.stats.health, player.stats.max_health,
            player.stats.stamina, player.stats.max_stamina,
            player.stats.money
        )

        if keys[pygame.K_SPACE]:
            hotbar.use_item(hotbar.active_slot_index, player)

        hotbar.draw(screen)
        shop.draw(screen)

        if not game_over:
            if player.stats.health <= 0:
                game_over = True

        else:
            death_screen.draw()

        pygame.display.flip()
        clock.tick(settings.FPS)

    pygame.quit()
    sys.exit()

    pass


if __name__ == "__main__":
    main()
