import pygame
import sys
import random
import math
import time
from weapons import create_weapon, Pistol, Shotgun, MachineGun, Bazooka
from enemies import create_enemy, Enemy, BasicEnemy, FastEnemy, TankEnemy, RangedEnemy, MiniBoss

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
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
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
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
VICTORY = 5  # New game state for victory

# Game timing constants
GAME_START_TIME = time.time()
MINI_BOSS_SPAWN_TIME = 60  # 1 minute
GAME_DURATION = 900  # 15 minutes in seconds
COUNTDOWN_START = 30  # Start countdown 30 seconds before end
ENEMY_SPAWN_RATE_INCREASE = 0.1  # Decrease spawn delay by 0.1 seconds every second
INITIAL_SPAWN_DELAY = 2.0  # Initial spawn delay in seconds
MIN_SPAWN_DELAY = 0.5  # Minimum spawn delay in seconds
ENEMY_COUNT_INCREASE_INTERVAL = 10  # Increase enemy count every 10 seconds
ENEMY_COUNT_INCREASE_PERCENT = 0.1  # 10% increase in enemy count

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
        # Split description into multiple lines if needed
        desc_words = option['description'].split()
        desc_line1 = ' '.join(desc_words[:len(desc_words)//2])
        desc_line2 = ' '.join(desc_words[len(desc_words)//2:])
        self.name_text = small_font.render(option['name'], True, WHITE)
        self.desc1_text = small_font.render(desc_line1, True, WHITE)
        self.desc2_text = small_font.render(desc_line2, True, WHITE)
        self.number_text = font.render(str(option['number']), True, WHITE)

    def draw(self, surface):
        try:
            # Create a transparent surface for the button
            button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            
            # Draw the button background with transparency
            color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(button_surface, (*color, 128), (0, 0, self.rect.width, self.rect.height), 0)  # Filled with transparency
            pygame.draw.rect(button_surface, color, (0, 0, self.rect.width, self.rect.height), 3)  # Thicker border
            
            # Draw number (larger and at the top)
            button_surface.blit(self.number_text, (self.rect.width // 2 - self.number_text.get_width() // 2, 20))
            
            # Draw name (larger font)
            name_text = font.render(self.option['name'], True, WHITE)  # Use regular font for name
            button_surface.blit(name_text, (self.rect.width // 2 - name_text.get_width() // 2, 60))
            
            # Draw description (split into two lines with more space)
            button_surface.blit(self.desc1_text, (self.rect.width // 2 - self.desc1_text.get_width() // 2, 110))
            button_surface.blit(self.desc2_text, (self.rect.width // 2 - self.desc2_text.get_width() // 2, 140))
            
            # Blit the button surface onto the main surface
            surface.blit(button_surface, self.rect)
        except Exception as e:
            print(f"Error drawing upgrade button: {e}")
            print(f"Button rect: {self.rect}")
            print(f"Option: {self.option}")

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
        self.current_level_experience = 0
        self.weapon_cooldowns = {}  # Track cooldowns for each weapon
        self.weapons = [create_weapon("pistol")]  # Start with pistol
        self.current_weapon_index = 0  # Index of currently selected weapon
        self.weapon_type = "pistol"
        self.leveled_up = False
        self.owned_weapons = ["pistol"]  # Track which weapons the player owns

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
            
        # Weapon switching with number keys
        if keys[pygame.K_1] and len(self.weapons) > 0:
            self.current_weapon_index = 0
            self.weapon_type = self.weapons[0].__class__.__name__.lower()
        elif keys[pygame.K_2] and len(self.weapons) > 1:
            self.current_weapon_index = 1
            self.weapon_type = self.weapons[1].__class__.__name__.lower()
        elif keys[pygame.K_3] and len(self.weapons) > 2:
            self.current_weapon_index = 2
            self.weapon_type = self.weapons[2].__class__.__name__.lower()
        elif keys[pygame.K_4] and len(self.weapons) > 3:
            self.current_weapon_index = 3
            self.weapon_type = self.weapons[3].__class__.__name__.lower()

        # Keep player on screen
        self.rect.clamp_ip(screen.get_rect())

        # Update weapon cooldowns
        current_time = pygame.time.get_ticks()
        for weapon_type, cooldown_time in list(self.weapon_cooldowns.items()):
            if current_time >= cooldown_time:
                del self.weapon_cooldowns[weapon_type]

    def add_experience(self, amount):
        self.experience += amount
        self.current_level_experience += amount
        if self.current_level_experience >= self.experience_to_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.current_level_experience = 0
        self.experience_to_level = int(self.experience_to_level * 1.5)
        self.leveled_up = True
        return True

    def shoot(self, target_x, target_y):
        current_time = pygame.time.get_ticks()
        projectiles_created = False
        
        # Try to fire all weapons that are off cooldown
        for weapon in self.weapons:
            weapon_type = weapon.__class__.__name__.lower()
            
            # Skip if weapon is on cooldown
            if weapon_type in self.weapon_cooldowns and current_time < self.weapon_cooldowns[weapon_type]:
                continue
                
            # Fire the weapon
            if weapon.shoot(self, target_x, target_y):
                projectiles_created = True
                
                # Create projectiles based on weapon type
                if weapon_type == "shotgun":
                    for i in range(weapon.pellets):
                        angle = math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx)
                        spread = random.uniform(-weapon.spread, weapon.spread) * math.pi / 180
                        angle += spread
                        target_x = self.rect.centerx + math.cos(angle) * 1000
                        target_y = self.rect.centery + math.sin(angle) * 1000
                        projectile = Projectile(self.rect.centerx, self.rect.centery, target_x, target_y,
                                             weapon.damage, weapon.projectile_color)
                        projectiles.add(projectile)
                        all_sprites.add(projectile)
                elif weapon_type == "bazooka":
                    # Create explosion immediately at mouse position
                    explosion = Explosion(
                        target_x, 
                        target_y,
                        weapon.explosion_radius,
                        weapon.damage,
                        weapon.particle_count,
                        weapon.particle_size
                    )
                    all_sprites.add(explosion)
                else:
                    angle = math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx)
                    if weapon_type == "machine_gun":
                        spread = random.uniform(-weapon.spread, weapon.spread) * math.pi / 180
                        angle += spread
                    target_x = self.rect.centerx + math.cos(angle) * 1000
                    target_y = self.rect.centery + math.sin(angle) * 1000
                    projectile = Projectile(self.rect.centerx, self.rect.centery, target_x, target_y,
                                         weapon.damage, weapon.projectile_color)
                    projectiles.add(projectile)
                    all_sprites.add(projectile)
        
        return projectiles_created

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

    def add_weapon(self, weapon_type):
        """Add a new weapon if the player doesn't already have it and has less than 4 weapons"""
        if weapon_type not in self.owned_weapons and len(self.weapons) < 4:
            self.weapons.append(create_weapon(weapon_type))
            self.owned_weapons.append(weapon_type)
            self.current_weapon_index = len(self.weapons) - 1  # Switch to the new weapon
            self.weapon_type = weapon_type
            return True
        return False

    def get_current_weapon(self):
        """Get the currently selected weapon"""
        if len(self.weapons) > 0:
            return self.weapons[self.current_weapon_index]
        return None

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, damage, color, is_rocket=False):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        self.damage = damage
        self.is_rocket = is_rocket
        
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

class ExplosionParticle(pygame.sprite.Sprite):
    def __init__(self, x, y, size, color, speed, lifetime):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed
        self.lifetime = lifetime
        self.angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed
        self.alpha = 255
        self.fade_rate = 255 / lifetime

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.alpha = max(0, self.alpha - self.fade_rate)
        self.image.set_alpha(int(self.alpha))
        
        if self.alpha <= 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, damage, particle_count, particle_size):
        super().__init__()
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.radius = radius
        self.damage = damage
        self.particle_count = particle_count
        self.particle_size = particle_size
        self.lifetime = 30  # frames
        self.current_frame = 0
        
        # Load explosion image
        try:
            self.image = pygame.image.load("resources/explosion.png")
            # Scale the image to match the explosion radius
            self.image = pygame.transform.scale(self.image, (radius * 2, radius * 2))
        except Exception as e:
            print(f"Error loading explosion image: {e}")
            # Fallback to a simple circle if image loading fails
            self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 100, 0, 200), (radius, radius), radius)
        
        # Create explosion particles
        self.particles = pygame.sprite.Group()
        for _ in range(particle_count):
            particle = ExplosionParticle(
                x, y, 
                particle_size, 
                (255, 100, 0),  # Orange color
                random.uniform(1, 3),
                random.randint(10, 20)
            )
            self.particles.add(particle)
            all_sprites.add(particle)

    def update(self):
        self.current_frame += 1
        if self.current_frame >= self.lifetime:
            self.kill()
        
        # Check for enemy collisions
        enemies_hit = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in enemies_hit:
            # Calculate distance from explosion center to enemy
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Apply damage based on distance (more damage closer to center)
            if distance <= self.radius:
                damage_multiplier = 1 - (distance / self.radius) * 0.5  # 50% damage reduction at edge
                enemy.take_damage(int(self.damage * damage_multiplier))

class MiniBoss(Enemy):
    def __init__(self, player):
        super().__init__(player)
        self.image = pygame.Surface((60, 60))
        self.image.fill((255, 0, 0))  # Red color for mini-boss
        self.rect = self.image.get_rect()
        self.health = 200
        self.max_health = 200
        self.speed = 2
        self.damage = 5
        self.score_value = 100
        self.experience_value = 50
        
        # Spawn at a random position on the edge of the screen
        side = random.randint(0, 3)
        if side == 0:  # Top
            self.rect.x = random.randint(0, WINDOW_WIDTH)
            self.rect.y = -self.rect.height
        elif side == 1:  # Right
            self.rect.x = WINDOW_WIDTH
            self.rect.y = random.randint(0, WINDOW_HEIGHT)
        elif side == 2:  # Bottom
            self.rect.x = random.randint(0, WINDOW_WIDTH)
            self.rect.y = WINDOW_HEIGHT
        else:  # Left
            self.rect.x = -self.rect.width
            self.rect.y = random.randint(0, WINDOW_HEIGHT)

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

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

# Add these variables at the top of the game loop
game_start_time = time.time()
mini_boss_spawned = False
mini_boss_spawn_time = 60000  # 1 minute in milliseconds

def generate_upgrade_options():
    # Create a pool of all possible upgrades
    all_upgrades = []
    
    # General upgrades (always available)
    all_upgrades.append({
        "name": "Speed Boost",
        "description": "Increase movement speed by 1",
        "apply": lambda: setattr(player, 'speed', player.speed + 1),
        "number": 1,
        "type": "general"
    })
    
    all_upgrades.append({
        "name": "Health Boost",
        "description": "Increase max health by 20",
        "apply": lambda: setattr(player, 'max_health', player.max_health + 20),
        "number": 2,
        "type": "general"
    })
    
    # Weapon unlocks (only if player doesn't have the weapon and has less than 4 weapons)
    if "shotgun" not in player.owned_weapons and len(player.weapons) < 4:
        all_upgrades.append({
            "name": "Shotgun",
            "description": "Unlock shotgun weapon",
            "apply": lambda: player.add_weapon("shotgun"),
            "number": 3,
            "type": "weapon_unlock"
        })
    
    if "machine_gun" not in player.owned_weapons and len(player.weapons) < 4:
        all_upgrades.append({
            "name": "Machine Gun",
            "description": "Unlock machine gun weapon",
            "apply": lambda: player.add_weapon("machine_gun"),
            "number": 4,
            "type": "weapon_unlock"
        })
    
    if "bazooka" not in player.owned_weapons and len(player.weapons) < 4:
        all_upgrades.append({
            "name": "Bazooka",
            "description": "Unlock bazooka weapon",
            "apply": lambda: player.add_weapon("bazooka"),
            "number": 5,
            "type": "weapon_unlock"
        })
    
    # Add weapon-specific upgrades for all owned weapons
    for weapon in player.weapons:
        weapon_upgrades = weapon.get_upgrades()
        for upgrade in weapon_upgrades:
            upgrade["type"] = "weapon_specific"
            all_upgrades.append(upgrade)
    
    # Shuffle all upgrades
    random.shuffle(all_upgrades)
    
    # Select 3 upgrades, prioritizing variety
    selected_upgrades = []
    types_selected = set()
    
    # First pass: try to get one of each type
    for upgrade in all_upgrades:
        if len(selected_upgrades) >= 3:
            break
            
        upgrade_type = upgrade.get("type", "general")
        if upgrade_type not in types_selected:
            selected_upgrades.append(upgrade)
            types_selected.add(upgrade_type)
    
    # Second pass: fill remaining slots with random upgrades
    remaining_upgrades = [u for u in all_upgrades if u not in selected_upgrades]
    while len(selected_upgrades) < 3 and remaining_upgrades:
        selected_upgrades.append(remaining_upgrades.pop(0))
    
    # If we still don't have 3 upgrades, duplicate some
    while len(selected_upgrades) < 3 and all_upgrades:
        selected_upgrades.append(random.choice(all_upgrades))
    
    # Assign numbers 1-3 to the options
    for i, option in enumerate(selected_upgrades[:3]):
        option['number'] = i + 1
    
    return selected_upgrades[:3]

def reset_game():
    global game_state, game_over, showing_upgrades, game_paused, upgrade_buttons, GAME_START_TIME, mini_boss_spawned, enemy_count_multiplier
    game_state = PLAYING
    game_over = False
    showing_upgrades = False
    game_paused = False
    upgrade_buttons = []
    GAME_START_TIME = time.time()  # Reset game start time
    mini_boss_spawned = False  # Reset mini-boss spawned flag
    enemy_count_multiplier = 1.0  # Reset enemy count multiplier
    
    # Reset player
    player.health = player.max_health
    player.score = 0
    player.experience = 0
    player.level = 1
    player.experience_to_level = 100
    player.speed = 5
    player.weapons = [create_weapon("pistol")]  # Reset to pistol
    player.current_weapon_index = 0  # Reset to pistol
    player.weapon_type = "pistol"
    player.leveled_up = False
    player.owned_weapons = ["pistol"]  # Reset owned weapons
    
    # Clear sprites
    for enemy in enemies:
        enemy.kill()
    for projectile in projectiles:
        projectile.kill()

# Game loop
running = True
last_enemy_spawn = time.time()
spawn_delay = INITIAL_SPAWN_DELAY
mini_boss_spawned = False
enemy_count_multiplier = 1.0  # Start with normal enemy count
countdown_active = False
victory_celebration = False
celebration_particles = []
game_start_time = time.time()  # Initialize game start time

while running:
    # Calculate time at the start of each frame
    current_time = time.time()
    elapsed_time = current_time - game_start_time
    time_remaining = max(0, GAME_DURATION - elapsed_time)
    
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
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
                game_start_time = time.time()  # Reset game start time when starting new game
            elif quit_button.is_clicked(mouse_pos, mouse_clicked):
                running = False

    # Handle game over
    elif game_state == GAME_OVER:
        if mouse_clicked:
            reset_game()
            game_start_time = time.time()  # Reset game start time when restarting

    # Handle victory
    elif game_state == VICTORY:
        # Create celebration particles
        if not victory_celebration:
            victory_celebration = True
            for _ in range(100):
                x = random.randint(0, WINDOW_WIDTH)
                y = random.randint(0, WINDOW_HEIGHT)
                color = random.choice([(255, 215, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)])
                size = random.randint(5, 15)
                speed_x = random.uniform(-3, 3)
                speed_y = random.uniform(-3, 3)
                celebration_particles.append({
                    'x': x,
                    'y': y,
                    'color': color,
                    'size': size,
                    'speed_x': speed_x,
                    'speed_y': speed_y,
                    'life': random.randint(30, 60)
                })
        
        # Update celebration particles
        for particle in celebration_particles[:]:
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            particle['life'] -= 1
            if particle['life'] <= 0:
                celebration_particles.remove(particle)
        
        if mouse_clicked:
            reset_game()
            game_start_time = time.time()  # Reset game start time when restarting

    # Handle upgrades
    elif game_state == UPGRADING:
        for button in upgrade_buttons:
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                try:
                    button.option["apply"]()
                    game_state = PLAYING
                    player.leveled_up = False
                except Exception as e:
                    print(f"Error applying upgrade: {e}")
                    game_state = PLAYING
                    player.leveled_up = False
        
        # Handle keyboard selection for upgrades
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1] and len(upgrade_buttons) > 0:
            try:
                upgrade_buttons[0].option["apply"]()
                game_state = PLAYING
                player.leveled_up = False
            except Exception as e:
                print(f"Error applying upgrade: {e}")
                game_state = PLAYING
                player.leveled_up = False
        elif keys[pygame.K_2] and len(upgrade_buttons) > 1:
            try:
                upgrade_buttons[1].option["apply"]()
                game_state = PLAYING
                player.leveled_up = False
            except Exception as e:
                print(f"Error applying upgrade: {e}")
                game_state = PLAYING
                player.leveled_up = False
        elif keys[pygame.K_3] and len(upgrade_buttons) > 2:
            try:
                upgrade_buttons[2].option["apply"]()
                game_state = PLAYING
                player.leveled_up = False
            except Exception as e:
                print(f"Error applying upgrade: {e}")
                game_state = PLAYING
                player.leveled_up = False

    # Handle gameplay
    elif game_state == PLAYING:
        # Check for countdown
        if time_remaining <= COUNTDOWN_START and not countdown_active:
            countdown_active = True
            countdown_text = font.render(f"{int(time_remaining)} seconds remaining!", True, RED)
            screen.blit(countdown_text, (WINDOW_WIDTH // 2 - countdown_text.get_width() // 2, 50))
            pygame.display.flip()
            pygame.time.delay(1000)  # Show for 1 second
        
        if elapsed_time >= GAME_DURATION:
            game_state = VICTORY
            continue
        
        # Handle continuous fire
        if pygame.mouse.get_pressed()[0]:  # Left mouse button
            player.shoot(*mouse_pos)

        # Update enemy count multiplier every 10 seconds
        enemy_count_multiplier = 1.0 + (elapsed_time // ENEMY_COUNT_INCREASE_INTERVAL) * ENEMY_COUNT_INCREASE_PERCENT
        
        # Calculate spawn delay (decreases over time)
        spawn_delay = max(MIN_SPAWN_DELAY, INITIAL_SPAWN_DELAY - (elapsed_time * ENEMY_SPAWN_RATE_INCREASE))
        
        # Spawn enemies
        if current_time - last_enemy_spawn >= spawn_delay:
            # Determine how many enemies to spawn based on the multiplier
            num_enemies = max(1, int(enemy_count_multiplier))
            
            for _ in range(num_enemies):
                # Determine enemy type based on elapsed time
                if elapsed_time < 30:  # First 30 seconds
                    enemy_type = "basic"
                elif elapsed_time < 45:  # 30-45 seconds
                    enemy_type = random.choice(["basic", "fast"])
                elif elapsed_time < 60:  # 45-60 seconds
                    enemy_type = random.choice(["basic", "fast", "tank"])
                else:  # After 60 seconds
                    enemy_type = random.choice(["basic", "fast", "tank", "ranged"])
                
                enemy = create_enemy(enemy_type)
                enemies.add(enemy)
                all_sprites.add(enemy)
            
            last_enemy_spawn = current_time
        
        # Spawn mini-boss after 1 minute if not already spawned
        if elapsed_time >= MINI_BOSS_SPAWN_TIME and not mini_boss_spawned:
            mini_boss = create_enemy("mini_boss")
            enemies.add(mini_boss)
            all_sprites.add(mini_boss)
            mini_boss_spawned = True
            
            # Display mini-boss warning
            warning_text = font.render("MINI-BOSS INCOMING!", True, RED)
            screen.blit(warning_text, (WINDOW_WIDTH // 2 - warning_text.get_width() // 2, 100))
            pygame.display.flip()
            pygame.time.delay(2000)  # Show warning for 2 seconds
        
        # Handle ranged enemy attacks
        for enemy in enemies:
            if isinstance(enemy, RangedEnemy) and enemy.is_attacking:
                # Create enemy projectile
                dx = player.rect.centerx - enemy.rect.centerx
                dy = player.rect.centery - enemy.rect.centery
                dist = math.sqrt(dx * dx + dy * dy)
                
                if dist != 0:
                    # Create a projectile that moves toward the player
                    projectile = Projectile(
                        enemy.rect.centerx, 
                        enemy.rect.centery, 
                        player.rect.centerx, 
                        player.rect.centery, 
                        enemy.damage, 
                        (0, 0, 255)  # Blue color for enemy projectiles
                    )
                    projectiles.add(projectile)
                    all_sprites.add(projectile)
                
                enemy.is_attacking = False  # Reset attack flag
        
        # Update all sprites
        for sprite in all_sprites:
            if isinstance(sprite, Enemy):
                sprite.update(player)
            else:
                sprite.update()
        
        # Check for collisions
        # Player-enemy collisions
        for enemy in enemies:
            # Check if player collides with enemy
            if player.rect.colliderect(enemy.rect):
                player.take_damage(enemy.damage)
                enemy.kill()
                enemies.remove(enemy)
                continue
            
            # Check if projectile collides with enemy
            for projectile in projectiles:
                if projectile.rect.colliderect(enemy.rect):
                    if enemy.take_damage(projectile.damage):
                        player.score += enemy.score_value
                        player.add_experience(enemy.experience_value)
                        enemy.kill()
                        enemies.remove(enemy)
                        projectiles.remove(projectile)
                        break
        
        # Check for level up
        if player.leveled_up:
            game_state = UPGRADING
            upgrade_options = generate_upgrade_options()
            upgrade_buttons = []
            
            # Create upgrade buttons
            for i, option in enumerate(upgrade_options):
                x = WINDOW_WIDTH // 2 - 300 + (i * 200)  # Increased spacing between buttons
                y = WINDOW_HEIGHT // 2 - 100  # Moved up more
                upgrade_buttons.append(UpgradeButton(x, y, 180, 180, option))  # Increased button size
    
    # Draw
    screen.fill(BLACK)
    
    if game_state == MENU:
        # Draw menu
        title_text = font.render("Vibe Game", True, WHITE)
        screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        start_button.draw(screen)
        quit_button.draw(screen)
    
    elif game_state == VICTORY:
        # Draw victory screen
        victory_text = font.render("VICTORY! You survived for 15 minutes!", True, GREEN)
        screen.blit(victory_text, (WINDOW_WIDTH // 2 - victory_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
        
        score_text = font.render(f"Final Score: {player.score}", True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, WINDOW_HEIGHT // 2))
        
        level_text = font.render(f"Final Level: {player.level}", True, WHITE)
        screen.blit(level_text, (WINDOW_WIDTH // 2 - level_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))
        
        restart_text = font.render("Click to play again", True, WHITE)
        screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 100))
        
        # Draw celebration particles
        for particle in celebration_particles:
            pygame.draw.circle(screen, particle['color'], (int(particle['x']), int(particle['y'])), particle['size'])
    
    elif game_state == GAME_OVER:
        # Draw game over screen
        game_over_text = font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
        
        score_text = font.render(f"Final Score: {player.score}", True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, WINDOW_HEIGHT // 2))
        
        restart_text = font.render("Press R to restart", True, WHITE)
        screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))
    
    elif game_state == UPGRADING:
        # Draw upgrade screen
        upgrade_text = font.render("Choose an Upgrade", True, WHITE)
        screen.blit(upgrade_text, (WINDOW_WIDTH // 2 - upgrade_text.get_width() // 2, 50))
        
        for button in upgrade_buttons:
            button.draw(screen)
    
    elif game_state == PAUSED:
        # Draw pause screen
        pause_text = font.render("PAUSED", True, WHITE)
        screen.blit(pause_text, (WINDOW_WIDTH // 2 - pause_text.get_width() // 2, WINDOW_HEIGHT // 2))
        
        resume_text = font.render("Press ESC to resume", True, WHITE)
        screen.blit(resume_text, (WINDOW_WIDTH // 2 - resume_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))
    
    elif game_state == PLAYING:
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
        # Calculate the percentage of XP progress, not the actual width
        xp_percentage = min(1.0, player.current_level_experience / player.experience_to_level)
        pygame.draw.rect(screen, YELLOW, (exp_x, exp_y, exp_width * xp_percentage, exp_height))
        
        # Draw score and level
        score_text = font.render(f'Score: {player.score}', True, WHITE)
        level_text = font.render(f'Level: {player.level}', True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH - 150, 10))
        screen.blit(level_text, (WINDOW_WIDTH - 150, 40))
        
        # Draw time remaining
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        
        # Change color based on time remaining
        if time_remaining <= COUNTDOWN_START:
            time_color = RED
            if int(time_remaining) % 2 == 0:  # Blink every second
                time_text = font.render(f'Time: {minutes:02d}:{seconds:02d}', True, time_color)
                screen.blit(time_text, (WINDOW_WIDTH // 2 - time_text.get_width() // 2, 10))
        else:
            time_color = WHITE
            time_text = font.render(f'Time: {minutes:02d}:{seconds:02d}', True, time_color)
            screen.blit(time_text, (WINDOW_WIDTH // 2 - time_text.get_width() // 2, 10))
        
        # Draw weapon display
        weapon_y = 70
        for i, weapon in enumerate(player.weapons):
            # Draw weapon box
            box_width = 150
            box_height = 30
            box_x = 10
            box_y = weapon_y + (i * (box_height + 5))
            
            # Highlight current weapon
            if i == player.current_weapon_index:
                pygame.draw.rect(screen, HIGHLIGHT, (box_x, box_y, box_width, box_height), 2)
            else:
                pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), 1)
            
            # Draw weapon name and number
            weapon_name = weapon.__class__.__name__.capitalize()
            weapon_text = small_font.render(f"{i+1}: {weapon_name}", True, WHITE)
            screen.blit(weapon_text, (box_x + 5, box_y + 5))
        
        # Draw weapon switching instructions
        if len(player.weapons) > 1:
            switch_text = small_font.render("Press 1-4 to switch weapons", True, WHITE)
            screen.blit(switch_text, (WINDOW_WIDTH - 200, 70))
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit() 