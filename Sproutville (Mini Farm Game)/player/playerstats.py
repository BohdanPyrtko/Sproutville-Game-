class PlayerStats:
    def __init__(self):
        self.health = 100
        self.max_health = 100
        self.stamina = 100
        self.max_stamina = 100
        self.money = 147

    def take_damage(self, amount):
        self.health = max(self.health - amount, 0)

    def heal(self, amount):
        self.health = min(self.health + amount, self.max_health)

    def use_stamina(self, amount):
        self.stamina = max(self.stamina - amount, 0)

    def restore_stamina(self, amount):
        self.stamina = min(self.stamina + amount, self.max_stamina)

    def add_money(self, amount):
        self.money += amount

    def spend_money(self, amount):
        if self.money >= amount:
            self.money -= amount
            return True
        return False
