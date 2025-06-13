# Рух гравця, допоміжні функції

def manual_move(position, direction):

    x, y = position
    speed = 0.07

    if direction == "up":
        y -= speed
    elif direction == "down":
        y += speed
    elif direction == "left":
        x -= speed
    elif direction == "right":
        x += speed

    return x, y

    pass

def auto_move_path(start, end, game_map):
    # Повертає шлях з початкової до кінцевої точки
    pass
