import pygame
import random
import math

# Constants for enemy types
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.health = 30
        self.max_health = 30
        self.speed = 2
        self.damage = 10
        self.score_value = 10
        self.experience_value = 5
        self.attack_cooldown = 0
        self.attack_delay = 2000  # 2 seconds between attacks
        self.is_attacking = False
        
        # Create a default image and rect
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0))  # Default red color
        self.rect = self.image.get_rect()
        
        # Spawn at a random position on the edge of the screen
        side = random.randint(0, 3)
        if side == 0:  # Top
            self.rect.x = random.randint(0, WINDOW_WIDTH)
            self.rect.y = -20
        elif side == 1:  # Right
            self.rect.x = WINDOW_WIDTH + 20
            self.rect.y = random.randint(0, WINDOW_HEIGHT)
        elif side == 2:  # Bottom
            self.rect.x = random.randint(0, WINDOW_WIDTH)
            self.rect.y = WINDOW_HEIGHT + 20
        else:  # Left
            self.rect.x = -20
            self.rect.y = random.randint(0, WINDOW_HEIGHT)
    
    def update(self, player):
        # Move towards player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist != 0:
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed
        
        # Check for attack cooldown
        current_time = pygame.time.get_ticks()
        if current_time - self.attack_cooldown >= self.attack_delay:
            self.is_attacking = True
            self.attack_cooldown = current_time
    
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

    def draw(self, surface):
        """Draw the enemy"""
        pygame.draw.rect(surface, (255, 0, 0), self.rect)

class BasicEnemy(Enemy):
    def __init__(self):
        super().__init__()
        # Override the default image with a green square
        self.image = pygame.Surface((30, 30))
        self.image.fill((0, 255, 0))  # Green square
        self.rect = self.image.get_rect(center=self.rect.center)  # Keep the same position
        self.health = 30
        self.max_health = 30
        self.speed = 2
        self.damage = 10
        self.score_value = 10
        self.experience_value = 5

class FastEnemy(Enemy):
    def __init__(self):
        super().__init__()
        # Override the default image with a yellow circle
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 0), (10, 10), 10)  # Yellow filled circle
        self.rect = self.image.get_rect(center=self.rect.center)  # Keep the same position
        self.health = 20
        self.max_health = 20
        self.speed = 4
        self.damage = 5
        self.score_value = 15
        self.experience_value = 8

class TankEnemy(Enemy):
    def __init__(self):
        super().__init__()
        # Override the default image with a red triangle
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        # Draw a red triangle
        pygame.draw.polygon(self.image, (255, 0, 0), [(20, 0), (0, 40), (40, 40)])
        self.rect = self.image.get_rect(center=self.rect.center)  # Keep the same position
        self.health = 100
        self.max_health = 100
        self.speed = 1
        self.damage = 20
        self.score_value = 30
        self.experience_value = 15

class RangedEnemy(Enemy):
    def __init__(self):
        super().__init__()
        # Override the default image with a blue diamond
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        # Draw a blue diamond
        pygame.draw.polygon(self.image, (0, 0, 255), [(15, 0), (30, 15), (15, 30), (0, 15)])
        self.rect = self.image.get_rect(center=self.rect.center)  # Keep the same position
        self.health = 40
        self.max_health = 40
        self.speed = 1.5
        self.damage = 15
        self.score_value = 20
        self.experience_value = 10
        self.attack_range = 200  # Attack from this distance
        self.attack_delay = 3000  # 3 seconds between attacks
    
    def update(self, player):
        # Move towards player but keep distance
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist != 0:
            # If too far, move closer
            if dist > self.attack_range + 50:
                self.rect.x += (dx / dist) * self.speed
                self.rect.y += (dy / dist) * self.speed
            # If too close, move away
            elif dist < self.attack_range - 50:
                self.rect.x -= (dx / dist) * self.speed
                self.rect.y -= (dy / dist) * self.speed
        
        # Check for attack cooldown
        current_time = pygame.time.get_ticks()
        if current_time - self.attack_cooldown >= self.attack_delay:
            # Only attack if within range
            if dist <= self.attack_range:
                self.is_attacking = True
                self.attack_cooldown = current_time

class MiniBoss(Enemy):
    def __init__(self):
        super().__init__()
        # Override the default image with a larger red square
        self.image = pygame.Surface((60, 60))
        self.image.fill((255, 0, 0))  # Red color for mini-boss
        self.rect = self.image.get_rect(center=self.rect.center)  # Keep the same position
        self.health = 200
        self.max_health = 200
        self.speed = 2
        self.damage = 5
        self.score_value = 100
        self.experience_value = 50

# Create enemy factory
def create_enemy(enemy_type):
    if enemy_type == "basic":
        return BasicEnemy()
    elif enemy_type == "fast":
        return FastEnemy()
    elif enemy_type == "tank":
        return TankEnemy()
    elif enemy_type == "ranged":
        return RangedEnemy()
    elif enemy_type == "mini_boss":
        return MiniBoss()
    else:
        return BasicEnemy()  # Default to basic enemy 