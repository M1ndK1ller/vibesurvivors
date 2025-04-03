import pygame
import math
import random

class Weapon:
    def __init__(self, damage, fire_rate, spread, projectile_color):
        self.damage = damage
        self.fire_rate = fire_rate
        self.spread = spread
        self.projectile_color = projectile_color
        self.level = 1
        self.upgrades = []

    def shoot(self, player, target_x, target_y):
        current_time = pygame.time.get_ticks()
        weapon_type = self.__class__.__name__.lower()
        
        # Check if weapon is on cooldown
        if weapon_type in player.weapon_cooldowns and current_time < player.weapon_cooldowns[weapon_type]:
            return False
            
        # Set cooldown for this weapon
        player.weapon_cooldowns[weapon_type] = current_time + self.fire_rate
        return True

    def get_upgrades(self):
        """Return available upgrades for this weapon"""
        return self.upgrades

class Pistol(Weapon):
    def __init__(self):
        super().__init__(damage=20, fire_rate=500, spread=0, projectile_color=(0, 0, 255))
        self.projectile_speed = 10
        self.upgrades = [
            {
                "name": "Damage Up",
                "description": "Increase pistol damage by 5",
                "apply": lambda: setattr(self, 'damage', self.damage + 5)
            },
            {
                "name": "Fire Rate Up",
                "description": "Decrease cooldown by 50ms",
                "apply": lambda: setattr(self, 'fire_rate', max(200, self.fire_rate - 50))
            },
            {
                "name": "Speed Up",
                "description": "Increase projectile speed by 2",
                "apply": lambda: setattr(self, 'projectile_speed', self.projectile_speed + 2)
            }
        ]

class Shotgun(Weapon):
    def __init__(self):
        super().__init__(damage=10, fire_rate=800, spread=5, projectile_color=(128, 0, 128))
        self.pellets = 3
        self.upgrades = [
            {
                "name": "Tighter Spread",
                "description": "Reduce spread by 1 degree",
                "apply": lambda: setattr(self, 'spread', max(1, self.spread - 1))
            },
            {
                "name": "More Pellets",
                "description": "Add 1 more pellet",
                "apply": lambda: setattr(self, 'pellets', self.pellets + 1)
            },
            {
                "name": "Damage Up",
                "description": "Increase pellet damage by 3",
                "apply": lambda: setattr(self, 'damage', self.damage + 3)
            },
            {
                "name": "Faster Reload",
                "description": "Decrease cooldown by 100ms",
                "apply": lambda: setattr(self, 'fire_rate', max(400, self.fire_rate - 100))
            }
        ]

class MachineGun(Weapon):
    def __init__(self):
        super().__init__(damage=15, fire_rate=100, spread=2, projectile_color=(255, 255, 0))
        self.upgrades = [
            {
                "name": "Faster Fire Rate",
                "description": "Decrease cooldown by 10ms",
                "apply": lambda: setattr(self, 'fire_rate', max(50, self.fire_rate - 10))
            },
            {
                "name": "Tighter Spread",
                "description": "Reduce spread by 0.5 degrees",
                "apply": lambda: setattr(self, 'spread', max(0.5, self.spread - 0.5))
            },
            {
                "name": "Damage Up",
                "description": "Increase damage by 3",
                "apply": lambda: setattr(self, 'damage', self.damage + 3)
            },
            {
                "name": "Extended Magazine",
                "description": "Decrease cooldown by 20ms",
                "apply": lambda: setattr(self, 'fire_rate', max(50, self.fire_rate - 20))
            }
        ]

class Bazooka(Weapon):
    def __init__(self):
        super().__init__(damage=50, fire_rate=1500, spread=0, projectile_color=(255, 100, 0))
        self.explosion_radius = 100
        self.particle_count = 20
        self.particle_size = 5
        self.upgrades = [
            {
                "name": "Larger Explosion",
                "description": "Increase explosion radius by 20",
                "apply": lambda: setattr(self, 'explosion_radius', self.explosion_radius + 20)
            },
            {
                "name": "More Particles",
                "description": "Add 5 more explosion particles",
                "apply": lambda: setattr(self, 'particle_count', self.particle_count + 5)
            },
            {
                "name": "Larger Particles",
                "description": "Increase particle size by 1",
                "apply": lambda: setattr(self, 'particle_size', self.particle_size + 1)
            },
            {
                "name": "Faster Reload",
                "description": "Decrease cooldown by 200ms",
                "apply": lambda: setattr(self, 'fire_rate', max(800, self.fire_rate - 200))
            },
            {
                "name": "Damage Up",
                "description": "Increase explosion damage by 10",
                "apply": lambda: setattr(self, 'damage', self.damage + 10)
            }
        ]

# Weapon factory to create weapons
def create_weapon(weapon_type):
    weapons = {
        "pistol": Pistol,
        "shotgun": Shotgun,
        "machine_gun": MachineGun,
        "bazooka": Bazooka
    }
    return weapons.get(weapon_type, Pistol)() 