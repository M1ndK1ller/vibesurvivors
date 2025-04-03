import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (100, 100, 100)
HIGHLIGHT = (200, 200, 200)

# Set up the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Vibe Survivors")
clock = pygame.time.Clock()

# Font setup
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 72)

# Game states
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3
UPGRADING = 4

class Button:
    def __init__(self, x, y, width, height, text, color=WHITE, hover_color=HIGHLIGHT):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, 2)
        
        text_surface = font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

class UpgradeButton(Button):
    def __init__(self, x, y, width, height, option):
        super().__init__(x, y, width, height, "")
        self.option = option
        self.name_text = small_font.render(option['name'], True, WHITE)
        self.desc_text = small_font.render(option['description'], True, WHITE)

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, 2)
        
        # Draw number
        number_text = font.render(str(self.option['number']), True, color)
        surface.blit(number_text, (self.rect.x + self.rect.width // 2 - number_text.get_width() // 2, 
                                  self.rect.y + 10))
        
        # Draw name
        surface.blit(self.name_text, (self.rect.x + self.rect.width // 2 - self.name_text.get_width() // 2, 
                                     self.rect.y + 40))
        
        # Draw description
        surface.blit(self.desc_text, (self.rect.x + self.rect.width // 2 - self.desc_text.get_width() // 2, 
                                     self.rect.y + 70))

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.score = 0
        self.experience = 0
        self.level = 1
        self.experience_to_level = 100
        self.current_level_experience = 0  # Track experience in current level
        self.weapon_cooldown = 0
        self.weapon_cooldown_time = 500  # milliseconds
        self.damage_multiplier = 1.0
        self.weapon_type = "pistol"  # "pistol" or "shotgun"
        self.shotgun_spread = 5  # degrees
        self.shotgun_pellets = 3
        self.leveled_up = False  # New flag to track level ups

    def update(self):
        keys = pygame.key.get_pressed()
        # WASD controls
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        # Keep player on screen
        self.rect.clamp_ip(screen.get_rect())

        # Update weapon cooldown
        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= clock.get_time()

    def add_experience(self, amount):
        self.experience += amount
        self.current_level_experience += amount
        if self.current_level_experience >= self.experience_to_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.current_level_experience = 0  # Reset current level experience
        self.experience_to_level = int(self.experience_to_level * 1.5)
        self.leveled_up = True  # Set flag when leveling up
        return True

    def shoot(self):
        if self.weapon_cooldown <= 0:
            self.weapon_cooldown = self.weapon_cooldown_time
            return True
        return False

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

# Weapon class
class Weapon(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, damage=20, color=BLUE):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        self.damage = damage
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist != 0:
            self.dx = dx / dist
            self.dy = dy / dist

    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        
        # Remove if off screen
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# Enemy base class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, player, color, size, speed, health, points, exp_value):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.speed = speed
        self.player = player
        self.health = health
        self.max_health = health
        self.points = points
        self.exp_value = exp_value
        
        # Spawn enemy at random edge of screen
        side = random.randint(0, 3)
        if side == 0:  # top
            self.rect.x = random.randint(0, WINDOW_WIDTH)
            self.rect.y = -size
        elif side == 1:  # right
            self.rect.x = WINDOW_WIDTH + size
            self.rect.y = random.randint(0, WINDOW_HEIGHT)
        elif side == 2:  # bottom
            self.rect.x = random.randint(0, WINDOW_WIDTH)
            self.rect.y = WINDOW_HEIGHT + size
        else:  # left
            self.rect.x = -size
            self.rect.y = random.randint(0, WINDOW_HEIGHT)

    def update(self):
        # Calculate direction to player
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist != 0:
            dx = dx / dist
            dy = dy / dist
            
            # Move towards player
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.player.score += self.points
            self.player.add_experience(self.exp_value)
            return True
        return False

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
weapons = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# Enemy spawn timer
enemy_spawn_timer = 0
ENEMY_SPAWN_DELAY = 2000  # milliseconds

# Game state
game_state = MENU
game_over = False
showing_upgrades = False
upgrade_options = []
game_paused = False
upgrade_buttons = []

# Create menu buttons
start_button = Button(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 25, 200, 50, "Start Game")
quit_button = Button(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50, 200, 50, "Quit")

def generate_upgrade_options():
    options = []
    # Speed upgrade
    options.append({
        "name": "Speed Boost",
        "description": "Increase movement speed by 1",
        "apply": lambda: setattr(player, 'speed', player.speed + 1),
        "number": 1
    })
    # Health upgrade
    options.append({
        "name": "Health Boost",
        "description": "Increase max health by 20",
        "apply": lambda: setattr(player, 'max_health', player.max_health + 20),
        "number": 2
    })
    # Damage upgrade
    options.append({
        "name": "Damage Boost",
        "description": "Increase damage by 20%",
        "apply": lambda: setattr(player, 'damage_multiplier', player.damage_multiplier * 1.2),
        "number": 3
    })
    # Shotgun upgrade
    options.append({
        "name": "Shotgun",
        "description": "Unlock shotgun weapon",
        "apply": lambda: setattr(player, 'weapon_type', 'shotgun'),
        "number": 4
    })
    # Shotgun spread upgrade
    options.append({
        "name": "Tighter Spread",
        "description": "Reduce shotgun spread by 1 degree",
        "apply": lambda: setattr(player, 'shotgun_spread', max(1, player.shotgun_spread - 1)),
        "number": 5
    })
    # Shotgun pellets upgrade
    options.append({
        "name": "More Pellets",
        "description": "Add 1 more shotgun pellet",
        "apply": lambda: setattr(player, 'shotgun_pellets', player.shotgun_pellets + 1),
        "number": 6
    })
    
    return random.sample(options, 3)

def reset_game():
    global game_state, game_over, showing_upgrades, game_paused, upgrade_buttons
    game_state = PLAYING
    game_over = False
    showing_upgrades = False
    game_paused = False
    upgrade_buttons = []
    
    # Reset player
    player.health = player.max_health
    player.score = 0
    player.experience = 0
    player.level = 1
    player.experience_to_level = 100
    player.speed = 5
    player.damage_multiplier = 1.0
    player.weapon_type = "pistol"
    player.shotgun_spread = 5
    player.shotgun_pellets = 3
    player.leveled_up = False
    
    # Clear sprites
    for enemy in enemies:
        enemy.kill()
    for weapon in weapons:
        weapon.kill()

# Game loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WINDOW_WIDTH, WINDOW_HEIGHT = event.size
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_clicked = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == PLAYING:
                    game_state = PAUSED
                elif game_state == PAUSED:
                    game_state = PLAYING
            elif event.key == pygame.K_r and game_state == GAME_OVER:
                reset_game()

    # Handle menu
    if game_state == MENU:
        start_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        
        if mouse_clicked:
            if start_button.is_clicked(mouse_pos, mouse_clicked):
                reset_game()
            elif quit_button.is_clicked(mouse_pos, mouse_clicked):
                running = False

    # Handle game over
    elif game_state == GAME_OVER:
        if mouse_clicked:
            reset_game()

    # Handle upgrades
    elif game_state == UPGRADING:
        for button in upgrade_buttons:
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                button.option["apply"]()
                game_state = PLAYING
                player.leveled_up = False

    # Handle gameplay
    elif game_state == PLAYING:
        # Handle continuous fire
        if pygame.mouse.get_pressed()[0]:  # Left mouse button
            if player.shoot():
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if player.weapon_type == "pistol":
                    weapon = Weapon(player.rect.centerx, player.rect.centery, mouse_x, mouse_y, 
                                  int(20 * player.damage_multiplier), BLUE)
                    weapons.add(weapon)
                    all_sprites.add(weapon)
                else:  # shotgun
                    for i in range(player.shotgun_pellets):
                        angle = math.atan2(mouse_y - player.rect.centery, mouse_x - player.rect.centerx)
                        spread = random.uniform(-player.shotgun_spread, player.shotgun_spread) * math.pi / 180
                        angle += spread
                        target_x = player.rect.centerx + math.cos(angle) * 1000
                        target_y = player.rect.centery + math.sin(angle) * 1000
                        weapon = Weapon(player.rect.centerx, player.rect.centery, target_x, target_y,
                                      int(10 * player.damage_multiplier), PURPLE)
                        weapons.add(weapon)
                        all_sprites.add(weapon)

        # Spawn enemies
        current_time = pygame.time.get_ticks()
        if current_time - enemy_spawn_timer > ENEMY_SPAWN_DELAY:
            enemy_type = random.randint(0, 2)
            if enemy_type == 0:  # Basic enemy
                enemy = Enemy(player, RED, 20, 3, 20, 10, 10)
            elif enemy_type == 1:  # Fast enemy
                enemy = Enemy(player, YELLOW, 15, 5, 10, 20, 15)
            else:  # Tank enemy
                enemy = Enemy(player, GREEN, 30, 2, 50, 30, 25)
            
            all_sprites.add(enemy)
            enemies.add(enemy)
            enemy_spawn_timer = current_time

        # Update
        all_sprites.update()

        # Check weapon-enemy collisions
        for weapon in weapons:
            enemy_hits = pygame.sprite.spritecollide(weapon, enemies, False)
            for enemy in enemy_hits:
                if enemy.take_damage(weapon.damage):
                    enemy.kill()
                weapon.kill()
                break

        # Check player-enemy collisions
        if pygame.sprite.spritecollide(player, enemies, False):
            if player.take_damage(1):
                game_state = GAME_OVER

        # Check for level up
        if player.leveled_up:
            game_state = UPGRADING
            upgrade_options = generate_upgrade_options()
            upgrade_buttons = []
            
            # Create upgrade buttons
            rect_width = 200
            rect_height = 120
            rect_spacing = 20
            total_width = (rect_width * 3) + (rect_spacing * 2)
            start_x = (WINDOW_WIDTH - total_width) // 2
            
            for i, option in enumerate(upgrade_options):
                rect_x = start_x + (i * (rect_width + rect_spacing))
                rect_y = WINDOW_HEIGHT // 2 - rect_height // 2
                upgrade_buttons.append(UpgradeButton(rect_x, rect_y, rect_width, rect_height, option))

    # Draw
    screen.fill(BLACK)
    
    if game_state == MENU:
        # Draw title
        title = title_font.render("Vibe Survivors", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Draw buttons
        start_button.draw(screen)
        quit_button.draw(screen)
    
    elif game_state in [PLAYING, PAUSED, GAME_OVER, UPGRADING]:
        # Draw game elements
        all_sprites.draw(screen)
        
        # Draw health bar
        health_width = 200
        health_height = 20
        health_x = 10
        health_y = 10
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
        pygame.draw.rect(screen, GREEN, (health_x, health_y, health_width * (player.health / player.max_health), health_height))
        
        # Draw experience bar
        exp_width = 200
        exp_height = 10
        exp_x = 10
        exp_y = 40
        pygame.draw.rect(screen, BLUE, (exp_x, exp_y, exp_width, exp_height))
        pygame.draw.rect(screen, YELLOW, (exp_x, exp_y, exp_width * (player.experience / player.experience_to_level), exp_height))
        
        # Draw score and level
        score_text = font.render(f'Score: {player.score}', True, WHITE)
        level_text = font.render(f'Level: {player.level}', True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH - 150, 10))
        screen.blit(level_text, (WINDOW_WIDTH - 150, 40))
        
        if game_state == PAUSED:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            pause_text = font.render("PAUSED - Press ESC to Resume", True, WHITE)
            screen.blit(pause_text, (WINDOW_WIDTH // 2 - pause_text.get_width() // 2, WINDOW_HEIGHT // 2))
        
        elif game_state == GAME_OVER:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            game_over_text = font.render('GAME OVER - Press R to Restart', True, WHITE)
            screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2))
        
        elif game_state == UPGRADING:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            title = font.render("Choose an Upgrade!", True, WHITE)
            screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
            
            for button in upgrade_buttons:
                button.draw(screen)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit() 