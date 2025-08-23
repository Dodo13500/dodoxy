import pygame
import math
import random

# Initialisation de Pygame
pygame.init()

# --- Paramètres du jeu et de la grille ---
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60
BULLET_SPEED = 400
UPGRADE_MULTIPLIER = 1.5
SELL_MULTIPLIER = 0.75

GRID_ROWS = 20
GRID_COLS = 35
GRID_CELL_SIZE = (SCREEN_HEIGHT - 100) // GRID_ROWS
UI_PANEL_HEIGHT = 100

# Définition des couleurs
COLORS = {
    "background": (34, 40, 49),
    "path": (57, 62, 70),
    "enemy_fast": (231, 76, 60),
    "enemy_tank": (52, 152, 219),
    "enemy_agile": (255, 159, 243),
    "enemy_invisible": (100, 100, 100),
    "enemy_boss": (192, 57, 43),
    "enemy_healer": (127, 255, 0),
    "enemy_armored": (118, 93, 118),
    "enemy_splitter": (153, 204, 255),
    "enemy_kamikaze": (255, 165, 0),
    "bullet": (255, 255, 255),
    "ui_panel": (40, 50, 60),
    "ui_text": (255, 255, 255),
    "selection": (255, 255, 0),
    "upgrade_button": (52, 152, 219),
    "sell_button": (231, 76, 60),
    "base": (192, 57, 43),
    "button_hover": (70, 80, 90),
    "particle_red": (255, 0, 0),
    "particle_yellow": (255, 255, 0),
    "hit_flash": (255, 0, 0),
    "tower_machine_gun": (46, 204, 113),
    "tower_sniper": (241, 196, 15),
    "tower_freeze": (52, 231, 219),
    "tower_poison": (155, 89, 182),
    "tower_splash": (255, 127, 80),
    "tower_mortar": (120, 120, 120),
    "tower_laser": (255, 0, 255),
    "tower_support": (255, 255, 255),
    "tower_mana": (200, 100, 255),
    "button_base": (60, 70, 80),
    "tower_bg": (80, 90, 100)
}

# Initialisation de l'écran et de l'horloge
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense PRO V5")
clock = pygame.time.Clock()
font_ui = pygame.font.Font(None, 28)
font_title = pygame.font.Font(None, 56)
font_small = pygame.font.Font(None, 24)

# Variables globales du jeu
money = 200
lives = 20
selected_tower = None
game_message = ""
message_timer = 0
mouse_pos = (0, 0)
game_grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

# Classe de bouton d'amélioration
class UpgradeButton:
    """Classe pour gérer l'affichage et les clics sur le bouton d'amélioration."""
    def __init__(self, x, y, width, height, tower):
        self.rect = pygame.Rect(x, y, width, height)
        self.tower = tower

    def handle_click(self):
        global selected_tower, money
        if self.tower and self.tower.upgrade():
            game.show_message("Tour améliorée !", 2)
        else:
            game.show_message("Pas assez d'argent !", 2)
            
    def draw(self):
        text = f"Améliorer ({self.tower.upgrade_cost})"
        font = font_ui
        
        button_color = COLORS["upgrade_button"]
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            button_color = (button_color[0] + 20, button_color[1] + 20, button_color[2] + 20)
            
        pygame.draw.rect(screen, button_color, self.rect, border_radius=5)
        text_surface = font.render(text, True, COLORS["ui_text"])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class SellButton:
    """Classe pour gérer l'affichage et les clics sur le bouton de vente."""
    def __init__(self, x, y, width, height, tower):
        self.rect = pygame.Rect(x, y, width, height)
        self.tower = tower

    def handle_click(self):
        global selected_tower, money
        if self.tower:
            money += int(self.tower.cost * SELL_MULTIPLIER)
            game_grid[self.tower.grid_y][self.tower.grid_x] = 0
            game.towers.remove(self.tower)
            selected_tower = None
            game.show_message("Tour vendue !", 2)

    def draw(self):
        text = f"Vendre ({int(self.tower.cost * SELL_MULTIPLIER)})"
        font = font_ui
        
        button_color = COLORS["sell_button"]
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            button_color = (button_color[0] + 20, button_color[1] + 20, button_color[2] + 20)
            
        pygame.draw.rect(screen, button_color, self.rect, border_radius=5)
        text_surface = font.render(text, True, COLORS["ui_text"])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


# Classe de base pour les ennemis
class Enemy:
    """Classe de base pour tous les ennemis."""
    def __init__(self, path, health, speed, reward, color, size, is_armored=False):
        self.path = path
        self.x, self.y = self.path[0]
        self.health = health
        self.max_health = health
        self.speed = speed
        self.initial_speed = speed
        self.reward = reward
        self.color = color
        self.size = size
        self.path_index = 0
        self.alive = True
        self.slow_timer = 0
        self.is_slowed = False
        self.poison_timer = 0
        self.poison_damage = 0
        self.hit_flash_timer = 0
        self.is_armored = is_armored

    def update(self, dt):
        if not self.alive:
            return
        
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
        
        if self.is_slowed:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.is_slowed = False
                self.speed = self.initial_speed # Restore original speed

        if self.poison_timer > 0:
            self.health -= self.poison_damage * dt
            self.poison_timer -= dt
            if self.health <= 0:
                self.alive = False
        
        current_speed = self.speed * 0.5 if self.is_slowed else self.speed
        
        if self.path_index + 1 >= len(self.path):
            global lives
            lives -= 1
            self.alive = False
            return

        target_x, target_y = self.path[self.path_index + 1]
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > current_speed * dt:
            self.x += (dx / distance) * current_speed * dt
            self.y += (dy / distance) * current_speed * dt
        else:
            self.x = target_x
            self.y = target_y
            self.path_index += 1
            
    def draw(self):
        if not self.alive:
            return
        
        draw_color = self.color
        if self.hit_flash_timer > 0:
            draw_color = COLORS["hit_flash"]
        
        pygame.draw.circle(screen, draw_color, (int(self.x), int(self.y)), self.size)
        
        health_percentage = self.health / self.max_health
        health_bar_width = 25
        health_bar_height = 4
        bar_x = self.x - health_bar_width / 2
        bar_y = self.y - self.size - 5
        
        pygame.draw.rect(screen, COLORS["path"], (bar_x, bar_y, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, COLORS["tower_machine_gun"], (bar_x, bar_y, health_bar_width * health_percentage, health_bar_height))
        
        if self.is_slowed:
            pygame.draw.rect(screen, (0, 0, 255), (bar_x - 2, bar_y - 8, 5, 5))
        if self.poison_timer > 0:
            pygame.draw.rect(screen, (0, 255, 0), (bar_x + health_bar_width - 3, bar_y - 8, 5, 5))
            
    def take_damage(self, damage):
        self.health -= damage
        self.hit_flash_timer = 0.1
        if self.health <= 0:
            self.alive = False
            global money
            money += self.reward
            return True
        return False

# Différents types d'ennemis
class FastEnemy(Enemy):
    def __init__(self, path, modifier=1.0):
        super().__init__(path, health=25 * modifier, speed=50 * modifier, reward=10 * modifier, color=COLORS["enemy_fast"], size=10)

class TankEnemy(Enemy):
    def __init__(self, path, modifier=1.0):
        super().__init__(path, health=150 * modifier, speed=20 * modifier, reward=30 * modifier, color=COLORS["enemy_tank"], size=15)
        
class AgileEnemy(Enemy):
    def __init__(self, path, modifier=1.0):
        super().__init__(path, health=50 * modifier, speed=100 * modifier, reward=15 * modifier, color=COLORS["enemy_agile"], size=8)

class InvisibleEnemy(Enemy):
    def __init__(self, path, modifier=1.0):
        super().__init__(path, health=35 * modifier, speed=120 * modifier, reward=20 * modifier, color=COLORS["enemy_invisible"], size=9)
        
class BossEnemy(Enemy):
    def __init__(self, path, modifier=1.0):
        super().__init__(path, health=500 * modifier, speed=40 * modifier, reward=100 * modifier, color=COLORS["enemy_boss"], size=20)

class HealerEnemy(Enemy):
    def __init__(self, path, modifier=1.0):
        super().__init__(path, health=75 * modifier, speed=30 * modifier, reward=25 * modifier, color=COLORS["enemy_healer"], size=12)
        
    def update(self, dt):
        super().update(dt)
        for enemy in game.enemies:
            if enemy != self and enemy.alive:
                dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if dist < 80 and enemy.health < enemy.max_health:
                    enemy.health += 5 * dt
                    enemy.health = min(enemy.health, enemy.max_health)

class ArmoredEnemy(Enemy):
    def __init__(self, path, modifier=1.0):
        super().__init__(path, health=100 * modifier, speed=40 * modifier, reward=35 * modifier, color=COLORS["enemy_armored"], size=14, is_armored=True)

    def take_damage(self, damage):
        if self.is_armored:
            damage *= 0.5 # Réduit les dégâts normaux de 50%
        self.health -= damage
        self.hit_flash_timer = 0.1
        if self.health <= 0:
            self.alive = False
            global money
            money += self.reward
            return True
        return False
        
class SplitterEnemy(Enemy):
    def __init__(self, path, modifier=1.0):
        super().__init__(path, health=50 * modifier, speed=40 * modifier, reward=20 * modifier, color=COLORS["enemy_splitter"], size=12)

    def take_damage(self, damage):
        if super().take_damage(damage):
            if self.size > 5:
                # Crée deux ennemis plus petits
                new_size = self.size // 2
                game.enemies.append(SplitterEnemy(self.path[self.path_index:], self.health // 2, self.speed * 1.2, self.reward // 2, self.color, new_size))
                game.enemies.append(SplitterEnemy(self.path[self.path_index:], self.health // 2, self.speed * 1.2, self.reward // 2, self.color, new_size))
            return True
        return False

class KamikazeEnemy(Enemy):
    def __init__(self, path, modifier=1.0):
        super().__init__(path, health=30 * modifier, speed=60 * modifier, reward=10 * modifier, color=COLORS["enemy_kamikaze"], size=10)

    def update(self, dt):
        if self.path_index + 1 >= len(self.path):
            global lives
            lives -= 5 # Dégâts à la base
            self.alive = False
            return
        super().update(dt)
        
# Classe de base pour les tours
class Tower:
    """Classe de base pour toutes les tours."""
    def __init__(self, grid_x, grid_y, cost, damage, fire_rate, radius, color):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = (grid_x * GRID_CELL_SIZE) + GRID_CELL_SIZE // 2
        self.y = (grid_y * GRID_CELL_SIZE) + GRID_CELL_SIZE // 2
        self.cost = cost
        self.damage = damage
        self.initial_fire_rate = fire_rate
        self.fire_rate = fire_rate
        self.radius = radius
        self.color = color
        self.target = None
        self.bullets = []
        self.fire_timer = 0
        self.level = 1
        self.upgrade_cost = int(cost * UPGRADE_MULTIPLIER)
        
    def get_stats(self):
        return {
            "dégâts": int(self.damage),
            "cadence": round(self.fire_rate, 1),
            "portée": self.radius,
            "coût d'amélioration": self.upgrade_cost
        }

    def update(self, dt, enemies):
        self.target = None
        for enemy in enemies:
            if enemy.alive:
                dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if dist < self.radius:
                    self.target = enemy
                    break
        
        self.fire_timer += dt
        if self.target and self.fire_timer >= 1.0 / self.fire_rate:
            self.bullets.append(Bullet(self.x, self.y, self.target, self.damage))
            self.fire_timer = 0
            
        self.bullets = [bullet for bullet in self.bullets if bullet.alive]
        for bullet in self.bullets:
            bullet.update(dt)

    def draw(self, is_selected):
        pygame.draw.rect(screen, self.color, (self.x - 15, self.y - 15, 30, 30), border_radius=5)
        if is_selected:
            pygame.draw.circle(screen, COLORS["selection"], (self.x, self.y), self.radius, 2)
            
    def upgrade(self):
        global money
        if money >= self.upgrade_cost:
            money -= self.upgrade_cost
            self.level += 1
            self.damage += self.damage * 0.5
            self.fire_rate += self.initial_fire_rate * 0.25
            self.upgrade_cost = int(self.upgrade_cost * UPGRADE_MULTIPLIER)
            return True
        return False
        
# Différents types de tours
class MachineGunTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, cost=50, damage=10, fire_rate=3, radius=120, color=COLORS["tower_machine_gun"])
        
    def draw(self, is_selected):
        super().draw(is_selected)
        pygame.draw.circle(screen, COLORS["background"], (self.x, self.y), 5)
        
class SniperTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, cost=75, damage=50, fire_rate=0.5, radius=200, color=COLORS["tower_sniper"])
        
    def draw(self, is_selected):
        super().draw(is_selected)
        pygame.draw.line(screen, COLORS["background"], (self.x - 10, self.y - 10), (self.x + 10, self.y + 10), 2)
        pygame.draw.line(screen, COLORS["background"], (self.x + 10, self.y - 10), (self.x - 10, self.y + 10), 2)

class FreezeTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, cost=60, damage=0, fire_rate=1.5, radius=150, color=COLORS["tower_freeze"])
        
    def update(self, dt, enemies):
        self.fire_timer += dt
        if self.fire_timer >= 1.0 / self.fire_rate:
            for enemy in enemies:
                if enemy.alive:
                    dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                    if dist < self.radius and not enemy.is_slowed:
                        enemy.is_slowed = True
                        enemy.slow_timer = 2
                        for _ in range(5):
                            game.particles.append(Particle(enemy.x, enemy.y, (52, 231, 219)))
            self.fire_timer = 0
        
    def draw(self, is_selected):
        super().draw(is_selected)
        pygame.draw.circle(screen, COLORS["background"], (self.x, self.y), 10, 2)

class PoisonTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, cost=80, damage=5, fire_rate=1, radius=100, color=COLORS["tower_poison"])
    
    def update(self, dt, enemies):
        self.fire_timer += dt
        if self.fire_timer >= 1.0 / self.fire_rate:
            for enemy in enemies:
                if enemy.alive:
                    dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                    if dist < self.radius:
                        enemy.poison_damage = self.damage
                        enemy.poison_timer = 5
                        
            self.fire_timer = 0
            
    def draw(self, is_selected):
        super().draw(is_selected)
        pygame.draw.polygon(screen, COLORS["background"], [
            (self.x, self.y - 10),
            (self.x + 10, self.y + 5),
            (self.x - 10, self.y + 5)
        ])

class SplashTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, cost=100, damage=25, fire_rate=0.7, radius=150, color=COLORS["tower_splash"])
    
    def update(self, dt, enemies):
        self.target = None
        for enemy in enemies:
            if enemy.alive:
                dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if dist < self.radius:
                    self.target = enemy
                    break
        
        self.fire_timer += dt
        if self.target and self.fire_timer >= 1.0 / self.fire_rate:
            self.bullets.append(SplashBullet(self.x, self.y, self.target, self.damage))
            self.fire_timer = 0
            
        self.bullets = [bullet for bullet in self.bullets if bullet.alive]
        for bullet in self.bullets:
            bullet.update(dt)

    def draw(self, is_selected):
        super().draw(is_selected)
        pygame.draw.rect(screen, COLORS["background"], (self.x - 5, self.y - 5, 10, 10))

class MortarTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, cost=150, damage=100, fire_rate=0.2, radius=300, color=COLORS["tower_mortar"])

    def update(self, dt, enemies):
        self.target = None
        for enemy in enemies:
            if enemy.alive:
                dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if dist < self.radius:
                    self.target = enemy
                    break
        
        self.fire_timer += dt
        if self.target and self.fire_timer >= 1.0 / self.fire_rate:
            self.bullets.append(MortarShell(self.x, self.y, self.target, self.damage, self.radius))
            self.fire_timer = 0
            
        self.bullets = [bullet for bullet in self.bullets if bullet.alive]
        for bullet in self.bullets:
            bullet.update(dt)
    
    def draw(self, is_selected):
        super().draw(is_selected)
        pygame.draw.circle(screen, COLORS["background"], (self.x, self.y), 15, 2)
        pygame.draw.line(screen, COLORS["background"], (self.x, self.y), (self.x, self.y - 10), 3)

class LaserTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, cost=120, damage=2, fire_rate=20, radius=180, color=COLORS["tower_laser"])
        self.target_line = None
        
    def update(self, dt, enemies):
        self.target = None
        self.target_line = None
        for enemy in enemies:
            if enemy.alive:
                dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if dist < self.radius:
                    self.target = enemy
                    break
        
        if self.target:
            self.target_line = (self.x, self.y, self.target.x, self.target.y)
            self.fire_timer += dt
            if self.fire_timer >= 1.0 / self.fire_rate:
                self.target.take_damage(self.damage)
                self.fire_timer = 0
    
    def draw(self, is_selected):
        super().draw(is_selected)
        if self.target_line:
            pygame.draw.line(screen, COLORS["bullet"], (self.x, self.y), (self.target_line[2], self.target_line[3]), 3)

class SupportTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, cost=100, damage=0, fire_rate=0, radius=120, color=COLORS["tower_support"])
        self.buff_amount = 0.25 # 25% de bonus de cadence
        
    def update(self, dt, towers):
        for tower in towers:
            if tower != self and isinstance(tower, Tower):
                dist = math.sqrt((tower.x - self.x)**2 + (tower.y - self.y)**2)
                if dist < self.radius:
                    tower.fire_rate = tower.initial_fire_rate * (1 + self.buff_amount)
                else:
                    tower.fire_rate = tower.initial_fire_rate
    
    def draw(self, is_selected):
        super().draw(is_selected)
        pygame.draw.circle(screen, COLORS["ui_panel"], (self.x, self.y), 10, 2)
        pygame.draw.line(screen, COLORS["ui_panel"], (self.x, self.y-5), (self.x, self.y+5), 2)
        pygame.draw.line(screen, COLORS["ui_panel"], (self.x-5, self.y), (self.x+5, self.y), 2)
        
class ManaTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, cost=70, damage=0, fire_rate=0, radius=0, color=COLORS["tower_mana"])
        self.money_timer = 0
        self.money_per_second = 5
        
    def update(self, dt, enemies):
        self.money_timer += dt
        if self.money_timer >= 1:
            global money
            money += self.money_per_second
            self.money_timer = 0

    def draw(self, is_selected):
        super().draw(is_selected)
        pygame.draw.rect(screen, COLORS["background"], (self.x-5, self.y-10, 10, 20))
        pygame.draw.rect(screen, COLORS["background"], (self.x-10, self.y-5, 20, 10))


class Bullet:
    """Classe pour les projectiles."""
    def __init__(self, x, y, target, damage):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.alive = True
        self.color = COLORS["bullet"]
    
    def update(self, dt):
        if not self.target or not self.target.alive:
            self.alive = False
            return
            
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < 5:
            self.target.take_damage(self.damage)
            if not self.target.alive:
                for _ in range(10):
                    game.particles.append(Particle(self.target.x, self.target.y, COLORS["particle_yellow"]))
            self.alive = False
        else:
            self.x += (dx / distance) * BULLET_SPEED * dt
            self.y += (dy / distance) * BULLET_SPEED * dt
            
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)

class SplashBullet(Bullet):
    """Projectile qui explose et fait des dégâts de zone."""
    def __init__(self, x, y, target, damage):
        super().__init__(x, y, target, damage)
        self.color = COLORS["tower_splash"]
        self.splash_radius = 50
    
    def update(self, dt):
        if not self.target or not self.target.alive:
            self.alive = False
            return
            
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < 5:
            self.splash_damage()
            for _ in range(20):
                game.particles.append(Particle(self.x, self.y, (255, 127, 80)))
            self.alive = False
        else:
            self.x += (dx / distance) * BULLET_SPEED * dt
            self.y += (dy / distance) * BULLET_SPEED * dt
    
    def splash_damage(self):
        for enemy in game.enemies:
            if enemy.alive:
                dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if dist < self.splash_radius:
                    enemy.take_damage(self.damage)

class MortarShell(SplashBullet):
    def __init__(self, x, y, target, damage, radius):
        super().__init__(x, y, target, damage)
        self.color = COLORS["tower_mortar"]
        self.splash_radius = 80
        
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 5)
        
class Particle:
    """Particule pour les effets visuels."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.lifetime = 1.0
        self.vx = random.uniform(-50, 50)
        self.vy = random.uniform(-50, 50)
    
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        self.size = max(0, self.size - 0.1)
        
    def draw(self):
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

# Moteur principal du jeu
class Game:
    def __init__(self):
        self.enemies = []
        self.towers = []
        self.particles = []
        self.placing_tower = None
        self.path = []
        self.base_location = (0, 0)
        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.generate_path()

        self.wave_index = 0
        self.enemies_in_wave = 0
        self.wave_timer = 3.0
        self.game_state = "menu"
        self.message = ""
        self.message_timer = 0
        self.spawn_timer = 0
        self.is_wave_active = False

        self.wave_data = self.generate_waves(50)

    def generate_path(self):
        """
        Génère un chemin simple et linéaire sur la grille, avec quelques virages.
        Cela évite les chemins trop complexes et imprévisibles.
        """
        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        grid_path = []
        
        # Point de départ sur le côté gauche
        current_y = random.randint(2, GRID_ROWS - 3)
        current_x = 0
        
        grid_path.append((current_x, current_y))
        self.grid[current_y][current_x] = 1

        while current_x < GRID_COLS - 1:
            # Choisir une direction principale : toujours vers la droite
            next_x = current_x + 1
            next_y = current_y
            
            # Possibilité de faire un virage vertical une ou deux fois
            if current_x > 5 and current_x < GRID_COLS - 5 and random.random() < 0.2 and self.grid[current_y][current_x - 1] == 1:
                # Choisir une direction verticale (haut ou bas)
                direction = random.choice([-1, 1])
                for _ in range(random.randint(2, 4)):
                    new_y = current_y + direction
                    if 0 <= new_y < GRID_ROWS and self.grid[new_y][current_x] == 0:
                        current_y = new_y
                        grid_path.append((current_x, current_y))
                        self.grid[current_y][current_x] = 1
                    else:
                        break # Arrêter si on touche un mur
            
            # Avancer horizontalement
            if 0 <= next_x < GRID_COLS and self.grid[next_y][next_x] == 0:
                current_x = next_x
                current_y = next_y
                grid_path.append((current_x, current_y))
                self.grid[current_y][current_x] = 1
            else:
                # Si on est bloqué, forcer le chemin vers la droite
                current_x += 1
                grid_path.append((current_x, current_y))
                self.grid[current_y][current_x] = 1

        self.base_location = grid_path[-1]
        
        # Convertit les coordonnées de la grille en coordonnées de pixels
        pixel_path = []
        for gx, gy in grid_path:
            px = gx * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
            py = gy * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
            pixel_path.append((px, py))

        self.path = pixel_path

    def generate_waves(self, num_waves):
        """Génère les données des vagues avec une difficulté progressive."""
        waves = []
        enemy_types = [FastEnemy, TankEnemy, AgileEnemy, InvisibleEnemy, HealerEnemy, ArmoredEnemy, SplitterEnemy]
        for i in range(num_waves):
            difficulty_modifier = 1.0 + (i / 10) * 0.2
            
            wave_type = random.choice(enemy_types)
            count = 10 + i * 2
            
            if (i + 1) % 10 == 0:
                waves.append({"type": BossEnemy, "count": 1, "modifier": difficulty_modifier * 2})
            elif (i + 1) % 5 == 0:
                waves.append({"type": KamikazeEnemy, "count": 3, "modifier": difficulty_modifier})
            else:
                waves.append({"type": wave_type, "count": count, "modifier": difficulty_modifier})
        return waves
    
    def draw_path(self):
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                if self.grid[y][x] == 1:
                    rect = pygame.Rect(x * GRID_CELL_SIZE, y * GRID_CELL_SIZE, GRID_CELL_SIZE, GRID_CELL_SIZE)
                    pygame.draw.rect(screen, COLORS["path"], rect)
                    
        base_rect = pygame.Rect(self.base_location[0] - GRID_CELL_SIZE / 2, self.base_location[1] - GRID_CELL_SIZE / 2, GRID_CELL_SIZE, GRID_CELL_SIZE)
        pygame.draw.rect(screen, COLORS["base"], base_rect)
        pygame.draw.circle(screen, (255, 255, 255), self.base_location, 10)

    def draw_ui(self):
        ui_panel_rect = pygame.Rect(0, SCREEN_HEIGHT - UI_PANEL_HEIGHT, SCREEN_WIDTH, UI_PANEL_HEIGHT)
        pygame.draw.rect(screen, COLORS["ui_panel"], ui_panel_rect)
        
        money_text = font_ui.render(f"Argent: {money}", True, COLORS["ui_text"])
        lives_text = font_ui.render(f"Vies: {lives}", True, COLORS["ui_text"])
        wave_text = font_ui.render(f"Vague: {self.wave_index + 1}/{len(self.wave_data)}", True, COLORS["ui_text"])
        screen.blit(money_text, (20, SCREEN_HEIGHT - 80))
        screen.blit(lives_text, (200, SCREEN_HEIGHT - 80))
        screen.blit(wave_text, (400, SCREEN_HEIGHT - 80))

        if not self.is_wave_active and self.wave_index < len(self.wave_data) - 1:
            timer_text = font_small.render(f"Prochaine vague dans {int(self.wave_timer) + 1}s", True, COLORS["ui_text"])
            screen.blit(timer_text, (400, SCREEN_HEIGHT - 55))

        # Affichage des boutons de tours
        tower_buttons = {
            "mg": (700, SCREEN_HEIGHT - 65, MachineGunTower),
            "sniper": (810, SCREEN_HEIGHT - 65, SniperTower),
            "freeze": (920, SCREEN_HEIGHT - 65, FreezeTower),
            "poison": (1030, SCREEN_HEIGHT - 65, PoisonTower),
            "splash": (1140, SCREEN_HEIGHT - 65, SplashTower),
            "mortar": (1250, SCREEN_HEIGHT - 65, MortarTower),
            "laser": (700, SCREEN_HEIGHT - 30, LaserTower),
            "support": (810, SCREEN_HEIGHT - 30, SupportTower),
            "mana": (920, SCREEN_HEIGHT - 30, ManaTower)
        }
        
        button_rects = {}
        for name, (x, y, tower_class) in tower_buttons.items():
            cost = tower_class(0,0).cost
            rect = pygame.Rect(x, y, 100, 25)
            
            button_color = COLORS["tower_bg"]
            if rect.collidepoint(pygame.mouse.get_pos()):
                button_color = (button_color[0] + 10, button_color[1] + 10, button_color[2] + 10)

            pygame.draw.rect(screen, button_color, rect, border_radius=5)
            
            tower_icon_rect = pygame.Rect(x + 5, y + 5, 15, 15)
            pygame.draw.rect(screen, tower_class(0,0).color, tower_icon_rect)
            
            text_surface = font_small.render(f"{name.capitalize()} ({cost})", True, COLORS["ui_text"])
            screen.blit(text_surface, (x + 25, y + 5))
            button_rects[name] = rect
            
        return button_rects

    def show_message(self, text, duration=3):
        global game_message, message_timer
        game_message = text
        message_timer = duration

    def handle_click(self, pos):
        global money, selected_tower

        ui_buttons = self.draw_ui()
        
        tower_classes = {
            "mg": MachineGunTower, "sniper": SniperTower, "freeze": FreezeTower,
            "poison": PoisonTower, "splash": SplashTower, "mortar": MortarTower,
            "laser": LaserTower, "support": SupportTower, "mana": ManaTower
        }

        # Vérifie si un bouton de tour a été cliqué
        for name, rect in ui_buttons.items():
            if rect.collidepoint(pos):
                tower_class = tower_classes[name]
                if money >= tower_class(0,0).cost:
                    self.placing_tower = tower_class
                    selected_tower = None
                    return
                else:
                    self.show_message("Pas assez d'argent !", 2)
                    return

        # Vérifie si le clic est sur l'UI d'amélioration/vente
        if selected_tower:
            upgrade_button_rect = pygame.Rect(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 80, 100, 30)
            sell_button_rect = pygame.Rect(SCREEN_WIDTH - 140, SCREEN_HEIGHT - 80, 75, 30)
            
            if upgrade_button_rect.collidepoint(pos):
                upgrade_button = UpgradeButton(0, 0, 0, 0, selected_tower)
                upgrade_button.handle_click()
                return
            elif sell_button_rect.collidepoint(pos):
                sell_button = SellButton(0, 0, 0, 0, selected_tower)
                sell_button.handle_click()
                return

        # Vérifie si le clic est sur une tour existante
        clicked_on_tower = False
        for tower in self.towers:
            if pygame.math.Vector2(pos).distance_to((tower.x, tower.y)) < 20:
                selected_tower = tower
                clicked_on_tower = True
                break
        
        if not clicked_on_tower:
            selected_tower = None

        # Si une tour est en cours de placement, la placer sur la grille
        if self.placing_tower:
            x, y = pos
            if y < SCREEN_HEIGHT - UI_PANEL_HEIGHT:
                grid_x = x // GRID_CELL_SIZE
                grid_y = y // GRID_CELL_SIZE
                if grid_x < GRID_COLS and grid_y < GRID_ROWS:
                    if self.grid[grid_y][grid_x] == 0:
                        self.towers.append(self.placing_tower(grid_x, grid_y))
                        self.grid[grid_y][grid_x] = 2 # 2 pour tour
                        money -= self.placing_tower(0,0).cost
                        self.placing_tower = None
                    else:
                        self.show_message("Impossible de placer une tour ici.", 2)
            return
            
    def update(self, dt):
        global lives, game_message, message_timer
        if lives <= 0:
            self.game_state = "game_over"
            return
        if self.wave_index >= len(self.wave_data) and not self.enemies:
            self.game_state = "game_win"
            return

        if message_timer > 0:
            message_timer -= dt
            if message_timer <= 0:
                game_message = ""

        # Logique des vagues
        if not self.enemies and self.enemies_in_wave == 0 and not self.is_wave_active:
            self.wave_timer -= dt
            if self.wave_timer <= 0:
                self.is_wave_active = True
                self.show_message(f"Vague {self.wave_index + 1} en cours !", 2)
        
        if self.is_wave_active and self.enemies_in_wave < self.wave_data[self.wave_index]["count"]:
            self.spawn_timer += dt
            if self.spawn_timer >= 0.5:
                current_wave = self.wave_data[self.wave_index]
                self.enemies.append(current_wave["type"](self.path, current_wave["modifier"]))
                self.enemies_in_wave += 1
                self.spawn_timer = 0
        
        if self.is_wave_active and self.enemies_in_wave >= self.wave_data[self.wave_index]["count"] and not self.enemies:
            self.is_wave_active = False
            self.wave_index += 1
            self.enemies_in_wave = 0
            self.wave_timer = 3.0
            if self.wave_index < len(self.wave_data):
                self.show_message(f"Vague {self.wave_index} terminée !", 2)
            else:
                self.game_state = "game_win"

        for enemy in self.enemies:
            enemy.update(dt)
        for tower in self.towers:
            if isinstance(tower, SupportTower):
                tower.update(dt, self.towers)
            else:
                tower.update(dt, self.enemies)
        for particle in self.particles:
            particle.update(dt)
        
        self.enemies = [enemy for enemy in self.enemies if enemy.alive]
        self.particles = [particle for particle in self.particles if particle.lifetime > 0]
        
    def draw(self):
        screen.fill(COLORS["background"])
        
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "game_over":
            self.draw_end_screen("Partie Terminée !")
        elif self.game_state == "game_win":
            self.draw_end_screen("Victoire ! Vous avez survécu à toutes les vagues.")
        else:
            self.draw_path()
            
            for particle in self.particles:
                particle.draw()
            
            for enemy in self.enemies:
                enemy.draw()
                
            for tower in self.towers:
                tower.draw(is_selected=(tower == selected_tower))
                if not isinstance(tower, (FreezeTower, PoisonTower, SupportTower, ManaTower, LaserTower)):
                    for bullet in tower.bullets:
                        bullet.draw()
                
            if self.placing_tower:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // GRID_CELL_SIZE
                grid_y = mouse_y // GRID_CELL_SIZE
                
                if grid_x < GRID_COLS and grid_y < GRID_ROWS:
                    draw_x = (grid_x * GRID_CELL_SIZE) + GRID_CELL_SIZE // 2
                    draw_y = (grid_y * GRID_CELL_SIZE) + GRID_CELL_SIZE // 2
                    
                    is_valid = self.grid[grid_y][grid_x] == 0
                    
                    temp_tower = self.placing_tower(0, 0)
                    temp_color = temp_tower.color
                    if not is_valid:
                        temp_color = (255, 0, 0)
                    
                    pygame.draw.circle(screen, temp_color, (draw_x, draw_y), temp_tower.radius, 2)
                    pygame.draw.rect(screen, temp_color, (draw_x - 15, draw_y - 15, 30, 30), border_radius=5)
            
            self.draw_ui()
            
            if selected_tower:
                upgrade_button = UpgradeButton(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 80, 100, 30, selected_tower)
                sell_button = SellButton(SCREEN_WIDTH - 140, SCREEN_HEIGHT - 80, 75, 30, selected_tower)
                upgrade_button.draw()
                sell_button.draw()
                
                stats_y = SCREEN_HEIGHT - 80
                stats_x_offset = SCREEN_WIDTH - 500
                stats_text = font_ui.render("Statistiques de la tour", True, COLORS["ui_text"])
                screen.blit(stats_text, (stats_x_offset, stats_y - 30))
                
                for stat, value in selected_tower.get_stats().items():
                    stats_text = font_small.render(f"{stat.capitalize()}: {value}", True, COLORS["ui_text"])
                    screen.blit(stats_text, (stats_x_offset, stats_y))
                    stats_y += 20
                
            if game_message:
                message_box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 50, 500, 100)
                pygame.draw.rect(screen, (43, 108, 176), message_box_rect, border_radius=10)
                text_surface = font_title.render(game_message, True, COLORS["ui_text"])
                text_rect = text_surface.get_rect(center=message_box_rect.center)
                screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
        
    def draw_end_screen(self, message):
        screen.fill(COLORS["background"])
        
        title_text = font_title.render(message, True, COLORS["ui_text"])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100))
        screen.blit(title_text, title_rect)
        
        restart_button_rect = pygame.Rect(SCREEN_WIDTH/2 - 75, SCREEN_HEIGHT/2, 150, 50)
        restart_button_color = COLORS["upgrade_button"]
        if restart_button_rect.collidepoint(pygame.mouse.get_pos()):
             restart_button_color = (restart_button_color[0] + 20, restart_button_color[1] + 20, restart_button_color[2] + 20)
        pygame.draw.rect(screen, restart_button_color, restart_button_rect, border_radius=10)
        
        restart_text = font_ui.render("Recommencer", True, COLORS["ui_text"])
        restart_text_rect = restart_text.get_rect(center=restart_button_rect.center)
        screen.blit(restart_text, restart_text_rect)

    def draw_menu(self):
        screen.fill(COLORS["background"])
        
        title_text = font_title.render("Tower Defense PRO", True, COLORS["ui_text"])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100))
        screen.blit(title_text, title_rect)
        
        start_button_rect = pygame.Rect(SCREEN_WIDTH/2 - 75, SCREEN_HEIGHT/2, 150, 50)
        start_button_color = COLORS["upgrade_button"]
        if start_button_rect.collidepoint(pygame.mouse.get_pos()):
             start_button_color = (start_button_color[0] + 20, start_button_color[1] + 20, start_button_color[2] + 20)
        pygame.draw.rect(screen, start_button_color, start_button_rect, border_radius=10)
        
        start_text = font_ui.render("Démarrer", True, COLORS["ui_text"])
        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        screen.blit(start_text, start_text_rect)
        
        instructions = [
            "Bienvenue dans Tower Defense PRO!",
            "Placez des tours pour défendre votre base contre les vagues d'ennemis.",
            "Cliquez sur les icônes de tours pour les sélectionner et les placer.",
            "Cliquez sur une tour pour l'améliorer ou la vendre.",
        ]
        
        y_pos = SCREEN_HEIGHT/2 + 70
        for text in instructions:
            text_surface = font_small.render(text, True, COLORS["ui_text"])
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH/2, y_pos))
            screen.blit(text_surface, text_rect)
            y_pos += 30

    def handle_menu_click(self, pos):
        start_button_rect = pygame.Rect(SCREEN_WIDTH/2 - 75, SCREEN_HEIGHT/2, 150, 50)
        if start_button_rect.collidepoint(pos):
            self.reset_game()

    def handle_end_screen_click(self, pos):
        restart_button_rect = pygame.Rect(SCREEN_WIDTH/2 - 75, SCREEN_HEIGHT/2, 150, 50)
        if restart_button_rect.collidepoint(pos):
            self.reset_game()
    
    def reset_game(self):
        global money, lives, selected_tower
        money = 200
        lives = 20
        selected_tower = None
        self.enemies = []
        self.towers = []
        self.particles = []
        self.placing_tower = None
        self.wave_index = 0
        self.enemies_in_wave = 0
        self.wave_timer = 3.0
        self.game_state = "playing"
        self.spawn_timer = 0
        self.is_wave_active = False
        self.generate_path()
        self.wave_data = self.generate_waves(50)
        self.show_message(f"Vague {self.wave_index + 1} démarrera dans 3 s", 3)

    def run(self):
        running = True
        while running:
            dt = clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == "menu":
                        self.handle_menu_click(event.pos)
                    elif self.game_state == "playing":
                        self.handle_click(event.pos)
                    elif self.game_state in ["game_over", "game_win"]:
                        self.handle_end_screen_click(event.pos)
            
            if self.game_state == "playing":
                self.update(dt)
            
            self.draw()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
