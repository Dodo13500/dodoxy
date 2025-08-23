import tkinter as tk
import math
import random
import time

# --- Constantes du jeu ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Dimensions de la carte
MAP_WIDTH = 35
MAP_HEIGHT = 25
CELL_SIZE = 50

# Statistiques et mouvement du joueur
PLAYER_SPEED = 5
PLAYER_SPEED_BOOST = 10 # Vitesse avec le power-up
ROTATION_SPEED = 0.1
FOV = 60
FOV_RADIANS = math.radians(FOV)
BULLET_SPEED = 1

# Limites de population (selon la demande)
MAX_ENEMIES = 7
MAX_ITEMS = 7

# Couleurs
WALL_COLOR = "#333333"
FLOOR_COLOR = "#8B4513"
CEILING_COLOR = "#ADD8E6"
ENEMY_COLOR = "red"
FAST_ENEMY_COLOR = "purple"
STRONG_ENEMY_COLOR = "darkred"
SHOOTER_ENEMY_COLOR = "teal"
BOSS_ENEMY_COLOR = "#FFD700"  # Or
HEALTH_PACK_COLOR = "green"
AMMO_PACK_COLOR = "orange"
SPECIAL_AMMO_COLOR = "cyan"
SPEED_BOOST_COLOR = "yellow"
DAMAGE_BOOST_COLOR = "red"
FIRERATE_BOOST_COLOR = "lime"
BACKGROUND_COLOR = "black"
PLAYER_COLOR = "blue"
DAMAGE_BOOST_CROSSHAIR = "yellow"

# --- Classes pour les objets du jeu ---

class Player:
    """Représente le personnage du joueur."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # Angle de direction en radians
        self.health = 100
        self.ammo = 20
        self.special_ammo = 0 # Munitions spéciales
        self.score = 0
        self.is_firing = False
        self.last_hit_time = time.time()
        
        # Power-ups
        self.speed_boost_time = 0
        self.damage_boost_time = 0
        self.firerate_boost_time = 0

class Enemy:
    """Représente un ennemi avec de la santé et une position."""
    def __init__(self, x, y, enemy_type='normal'):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        if enemy_type == 'normal':
            self.health = 50
            self.move_speed = 0.05
            self.points = 10
        elif enemy_type == 'fast':
            self.health = 30
            self.move_speed = 0.1
            self.points = 20
        elif enemy_type == 'strong':
            self.health = 100
            self.move_speed = 0.03
            self.points = 30
        elif enemy_type == 'shooter':
            self.health = 40
            self.move_speed = 0.06
            self.points = 40
        elif enemy_type == 'boss':
            self.health = 250
            self.move_speed = 0.02
            self.points = 100
        
        self.last_shot_time = time.time()
        self.move_cooldown = 0
    
    def move_randomly(self, game_map):
        """Déplace l'ennemi aléatoirement sur la carte en évitant les murs."""
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return
            
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        valid_moves = []
        
        for direction in directions:
            new_x = self.x + direction[0]
            new_y = self.y + direction[1]
            
            if 0 <= int(new_x) < MAP_WIDTH and 0 <= int(new_y) < MAP_HEIGHT and game_map[int(new_y)][int(new_x)] != "W":
                valid_moves.append(direction)
        
        if valid_moves:
            chosen_direction = random.choice(valid_moves)
            self.x += chosen_direction[0]
            self.y += chosen_direction[1]
        
        cooldown_base = 5 if self.enemy_type == 'fast' else 10
        self.move_cooldown = random.randint(cooldown_base, cooldown_base + 20)
    
    def move_towards_player(self, player_x, player_y, game_map):
        """Déplace l'ennemi vers le joueur."""
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0.5:
            vx = (dx / dist) * self.move_speed
            vy = (dy / dist) * self.move_speed
            
            new_x = self.x + vx
            new_y = self.y + vy
            
            if 0 <= int(new_x) < MAP_WIDTH and 0 <= int(new_y) < MAP_HEIGHT and game_map[int(new_y)][int(new_x)] != "W":
                self.x = new_x
                self.y = new_y
    
    def fire_at_player(self, player_x, player_y):
        """Fait tirer l'ennemi vers le joueur."""
        if time.time() - self.last_shot_time > 2: # Tire toutes les 2 secondes
            angle_to_player = math.atan2(player_y - self.y, player_x - self.x)
            self.last_shot_time = time.time()
            return {
                'x': self.x,
                'y': self.y,
                'angle': angle_to_player,
                'speed': BULLET_SPEED * 0.7,
                'lifetime': 200,
                'type': 'enemy'
            }
        return None

class Item:
    """Représente un objet à ramasser sur la carte."""
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type # 'health', 'ammo', 'special_ammo', 'speed_boost', 'damage_boost', 'firerate_boost'

# --- Classe principale du jeu ---

class FPSGame:
    """Logique principale du jeu et interface graphique."""
    def __init__(self, master):
        self.master = master
        self.master.title("FPS Python")
        self.master.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.master.resizable(False, False)

        self.canvas = tk.Canvas(self.master, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=BACKGROUND_COLOR)
        self.canvas.pack()

        self.stats_frame = tk.Frame(self.master, bg="black")
        self.stats_frame.pack(fill="x", side="bottom")

        # Remplacement du label de santé par une barre de vie
        self.health_frame = tk.Frame(self.stats_frame, bg="#333", height=20, width=150)
        self.health_frame.pack(side="left", padx=10, pady=5)
        self.health_bar = tk.Canvas(self.health_frame, bg="green", height=20, width=150, highlightthickness=0)
        self.health_bar.pack(side="left")
        
        self.health_label = tk.Label(self.stats_frame, text="Santé: 100", bg="black", fg="white", font=("Helvetica", 14))
        self.health_label.pack(side="left", padx=5, pady=5)
        
        self.ammo_label = tk.Label(self.stats_frame, text="", bg="black", fg="white", font=("Helvetica", 14))
        self.ammo_label.pack(side="left", padx=10, pady=5)
        self.score_label = tk.Label(self.stats_frame, text="", bg="black", fg="white", font=("Helvetica", 14))
        self.score_label.pack(side="left", padx=10, pady=5)
        
        self.status_label = tk.Label(self.stats_frame, text="", bg="black", fg="white", font=("Helvetica", 24))
        self.status_label.pack(side="right", padx=10, pady=5)
        
        self.map = [
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "W                                 W",
            "W WWWWWWWWW WWWWW W WWWW WWWWWWW W",
            "W W  W    W     W W W  W       W W",
            "W W  W WWWW W   W W W  WWWWWWW W W",
            "W W  W W  W W   W W W        W W W",
            "W WWWW W  W WWWWWWW W WWWWWWWW W W",
            "W      W  W           W        W W",
            "WWWWWWWWWWWWWWWWWWWWW W WWWWWW W W",
            "W  W  W  W       W    W W  W   W W",
            "W  W  W  W WWWWW W WWWW W  W WWWW",
            "W  W  W  W     W W    W W  W W  W",
            "W  W  WWWWWWWWW W WWWW W WWWW W  W",
            "W  W           W W     W      W  W",
            "W  WWWWWWWWWWWWWWWWWWWWWWWWWWWW  W",
            "W                                W",
            "W WWWWWWW WWWWWW WWWWWWWWWW WWWW W",
            "W   W W W   W  W W  W    W     W W",
            "W WWWWWWW W W  W WWWWWWWWWWWWW W W",
            "W W     W W W  W W           W W W",
            "W W WWW W W W  W W WWWWWWWWW W W W",
            "W W W W W W W  W W W       W W W W",
            "W WWWWWWW W W  W W WWWWWWW W W W W",
            "W           W    W         W     W",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW"
        ]
        
        self.player = Player(1.5, 1.5)
        
        self.enemies = []
        self.items = []
        self.projectiles = []
        
        self.last_enemy_spawn_time = time.time()
        self.last_item_spawn_time = time.time()
        self.last_health_regen_time = time.time()
        self.last_fire_time = time.time()

        self.enemies = self.create_enemies(3)
        self.items = self.create_items(3)
        
        self.master.bind("<z>", self.move_forward)
        self.master.bind("<q>", self.rotate_left)
        self.master.bind("<s>", self.move_backward)
        self.master.bind("<d>", self.rotate_right)
        
        self.canvas.bind("<Button-1>", self.fire_gun)
        
        self.running = True
        self.game_loop()

    def find_valid_spawn_location(self):
        """Trouve une position aléatoire et valide pour un objet ou un ennemi."""
        while True:
            x = random.randint(1, MAP_WIDTH - 2) + 0.5
            y = random.randint(1, MAP_HEIGHT - 2) + 0.5
            
            if self.map[int(y)][int(x)] != "W" and (abs(x - self.player.x) > 4 or abs(y - self.player.y) > 4):
                if all(math.sqrt((obj.x - x)**2 + (obj.y - y)**2) > 1 for obj in self.enemies + self.items):
                    return x, y

    def create_enemies(self, num_enemies):
        """Crée une liste d'ennemis à des positions aléatoires valides."""
        enemies = []
        for _ in range(num_enemies):
            x, y = self.find_valid_spawn_location()
            enemy_type = random.choice(['normal', 'fast', 'strong', 'shooter', 'boss'])
            enemies.append(Enemy(x, y, enemy_type))
        return enemies

    def create_items(self, num_items):
        """Crée une liste d'objets à des positions aléatoires valides."""
        items = []
        for _ in range(num_items):
            x, y = self.find_valid_spawn_location()
            item_type = random.choice(['health', 'ammo', 'special_ammo', 'speed_boost', 'damage_boost', 'firerate_boost'])
            items.append(Item(x, y, item_type))
        return items

    def spawn_new_enemy(self):
        """Fait apparaître un nouvel ennemi si le total est inférieur à la limite."""
        if len(self.enemies) < MAX_ENEMIES:
            x, y = self.find_valid_spawn_location()
            enemy_type = random.choice(['normal', 'fast', 'strong', 'shooter', 'boss'])
            self.enemies.append(Enemy(x, y, enemy_type))
            self.status_label.config(text="Nouvel ennemi apparu !", fg="yellow")

    def spawn_new_item(self):
        """Fait apparaître un nouvel objet si le total est inférieur à la limite."""
        if len(self.items) < MAX_ITEMS:
            x, y = self.find_valid_spawn_location()
            item_type = random.choice(['health', 'ammo', 'special_ammo', 'speed_boost', 'damage_boost', 'firerate_boost'])
            self.items.append(Item(x, y, item_type))
            self.status_label.config(text="Un nouvel objet est apparu !", fg="white")

    def game_loop(self):
        """La boucle principale du jeu."""
        if not self.running:
            return
        
        current_time = time.time()
        
        # Gère la durée des power-ups
        if self.player.speed_boost_time > 0:
            self.player.speed_boost_time -= 1
        if self.player.damage_boost_time > 0:
            self.player.damage_boost_time -= 1
        if self.player.firerate_boost_time > 0:
            self.player.firerate_boost_time -= 1

        # Gestion des apparitions automatiques (toutes les 5 secondes)
        if len(self.enemies) < MAX_ENEMIES and current_time - self.last_enemy_spawn_time > 5:
            self.spawn_new_enemy()
            self.last_enemy_spawn_time = current_time
            
        if len(self.items) < MAX_ITEMS and current_time - self.last_item_spawn_time > 5:
            self.spawn_new_item()
            self.last_item_spawn_time = current_time
            
        # Régénération de la santé
        if current_time - self.player.last_hit_time > 5 and self.player.health < 100:
            self.player.health = min(100, self.player.health + 1)
        
        self.update_enemies()
        self.update_projectiles()
        self.check_item_pickup()
        self.update_stats()
        self.draw_screen()
        
        self.master.after(30, self.game_loop)

    def update_projectiles(self):
        """Met à jour la position des projectiles et gère les collisions."""
        projectiles_to_remove = []
        for p in self.projectiles:
            # Met à jour la position du projectile
            p['x'] += p['speed'] * math.cos(p['angle'])
            p['y'] += p['speed'] * math.sin(p['angle'])
            p['lifetime'] -= 1
            
            # Gère les collisions pour les projectiles du joueur
            if p['type'] != 'enemy':
                for enemy in self.enemies:
                    dx = p['x'] - enemy.x
                    dy = p['y'] - enemy.y
                    dist = math.sqrt(dx**2 + dy**2)
                    
                    if dist < 0.5: 
                        damage_multiplier = 2 if p['type'] == 'special' else 1
                        damage = 25 * damage_multiplier
                        if self.player.damage_boost_time > 0:
                            damage *= 2
                        
                        enemy.health -= damage
                        self.status_label.config(text="Touché !", fg="orange")
                        projectiles_to_remove.append(p)
                        if enemy.health <= 0:
                            self.player.score += enemy.points
                            self.enemies.remove(enemy)
                            self.spawn_new_enemy() 
                        break 
            
            # Gère les collisions pour les projectiles de l'ennemi
            if p['type'] == 'enemy':
                dx = p['x'] - self.player.x
                dy = p['y'] - self.player.y
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist < 0.5:
                    self.player.health -= 10 # Dégâts des projectiles ennemis
                    self.player.last_hit_time = time.time()
                    self.status_label.config(text="Touché par un tir ennemi !", fg="red")
                    projectiles_to_remove.append(p)

            # Vérifie la collision avec un mur
            map_x = int(p['x'])
            map_y = int(p['y'])
            if 0 <= map_x < MAP_WIDTH and 0 <= map_y < MAP_HEIGHT and self.map[map_y][map_x] == "W":
                projectiles_to_remove.append(p)
            
            # Vérifie si la durée de vie du projectile est écoulée
            if p['lifetime'] <= 0:
                projectiles_to_remove.append(p)
                
        for p in projectiles_to_remove: 
            if p in self.projectiles:
                self.projectiles.remove(p)

    def update_stats(self):
        """Met à jour les labels d'interface utilisateur avec les statistiques et le statut, et la barre de vie."""
        # Met à jour la barre de vie
        health_width = (self.player.health / 100) * 150
        self.health_bar.configure(width=health_width)
        
        # Change la couleur de la barre de vie en fonction de la santé
        if self.player.health > 50:
            self.health_bar.configure(bg="green")
        elif self.player.health > 20:
            self.health_bar.configure(bg="yellow")
        else:
            self.health_bar.configure(bg="red")

        self.health_label.config(text=f"Santé: {self.player.health}")
        self.ammo_label.config(text=f"Munitions: {self.player.ammo} | Spéciales: {self.player.special_ammo}")
        self.score_label.config(text=f"Score: {self.player.score}")
        
        status_text = ""
        if self.player.speed_boost_time > 0:
            status_text += "BOOST VITESSE ! "
        if self.player.damage_boost_time > 0:
            status_text += "BOOST DÉGÂTS ! "
        if self.player.firerate_boost_time > 0:
            status_text += "TIR RAPIDE ! "
            
        self.status_label.config(text=status_text, fg="white")

        if self.player.health <= 0 and self.running:
            self.running = False
            self.status_label.config(text="Vous avez perdu !", fg="red")
            
        if not self.running:
            try:
                # Vérifie si le bouton "Recommencer" n'existe pas déjà
                if not any(isinstance(w, tk.Button) and w.cget("text") == "Recommencer" for w in self.stats_frame.winfo_children()):
                    restart_button = tk.Button(self.stats_frame, text="Recommencer", command=self.restart_game, font=("Helvetica", 14), bg="#5cb85c", fg="white", relief="ridge")
                    restart_button.pack(side="right", padx=10, pady=5)
            except tk.TclError:
                pass # Empêche l'erreur si le widget a déjà été détruit

    def restart_game(self):
        """Relance une nouvelle partie."""
        self.player = Player(1.5, 1.5)
        self.enemies = self.create_enemies(3)
        self.items = self.create_items(3)
        self.projectiles = []
        self.running = True
        self.status_label.config(text="")
        
        # Retire le bouton de redémarrage s'il existe
        for widget in self.stats_frame.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == "Recommencer":
                widget.destroy() 
        self.game_loop()

    def update_enemies(self):
        """Gère le mouvement des ennemis et leurs attaques."""
        if not self.running:
            return
        
        for enemy in self.enemies:
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            dist = math.sqrt(dx**2 + dy**2)
            
            # Les ennemis tireurs tirent s'ils sont assez proches et ont une ligne de vue
            if enemy.enemy_type == 'shooter' and dist < 15 and not self.is_line_of_sight_blocked(enemy.x, enemy.y, self.player.x, self.player.y):
                projectile = enemy.fire_at_player(self.player.x, self.player.y)
                if projectile:
                    self.projectiles.append(projectile)
            
            # Les ennemis poursuivent le joueur s'il est assez proche
            if dist < 10 and not self.is_line_of_sight_blocked(enemy.x, enemy.y, self.player.x, self.player.y):
                enemy.move_towards_player(self.player.x, self.player.y, self.map)
            else:
                enemy.move_randomly(self.map)
            
            # L'ennemi inflige des dégâts si la distance est petite
            if dist < 1.0 and random.random() < 0.05:
                self.player.health -= 5
                self.player.last_hit_time = time.time()
                self.status_label.config(text="Touché !", fg="red")

    def check_item_pickup(self):
        """Vérifie si le joueur a ramassé un objet."""
        items_to_remove = []
        for item in self.items:
            dx = self.player.x - item.x
            dy = self.player.y - item.y
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist < 0.5:
                if item.type == 'health':
                    self.player.health = min(100, self.player.health + 25)
                    self.status_label.config(text="Pack de santé ramassé !", fg="green")
                elif item.type == 'ammo':
                    self.player.ammo += 10
                    self.status_label.config(text="Munitions ramassées !", fg="orange")
                elif item.type == 'special_ammo':
                    self.player.special_ammo += 1
                    self.status_label.config(text="Munition spéciale trouvée !", fg="cyan")
                elif item.type == 'speed_boost':
                    self.player.speed_boost_time = 300 # Durée du boost en frames
                    self.status_label.config(text="Boost de vitesse ramassé !", fg="yellow")
                elif item.type == 'damage_boost':
                    self.player.damage_boost_time = 300
                    self.status_label.config(text="Boost de dégâts ramassé !", fg="red")
                elif item.type == 'firerate_boost':
                    self.player.firerate_boost_time = 300
                    self.status_label.config(text="Boost de cadence de tir ramassé !", fg="lime")
                items_to_remove.append(item)
                self.spawn_new_item() 
                
        for item in items_to_remove:
            self.items.remove(item)

    def draw_screen(self):
        """Dessine la vue à la première personne, y compris les murs, les ennemis, les objets et les projectiles."""
        self.canvas.delete("all")
        
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT / 2, fill=CEILING_COLOR, width=0)
        self.canvas.create_rectangle(0, WINDOW_HEIGHT / 2, WINDOW_WIDTH, WINDOW_HEIGHT, fill=FLOOR_COLOR, width=0)
        
        start_angle = self.player.angle - FOV_RADIANS / 2
        
        for ray_num in range(WINDOW_WIDTH):
            ray_angle = start_angle + (ray_num / WINDOW_WIDTH) * FOV_RADIANS
            distance_to_wall = self.ray_cast(self.player.x, self.player.y, ray_angle)
            wall_height = (CELL_SIZE * 50) / (distance_to_wall + 0.001)
            
            top_y = WINDOW_HEIGHT / 2 - wall_height / 2
            bottom_y = WINDOW_HEIGHT / 2 + wall_height / 2
            
            shading = min(1, max(0.2, 1 - distance_to_wall / 20))
            shade_hex = f'#{int(40 * shading):02x}{int(40 * shading):02x}{int(40 * shading):02x}'
            
            self.canvas.create_line(ray_num, top_y, ray_num, bottom_y, fill=shade_hex, width=1)
            
        # Trie et affiche les ennemis et les objets
        all_objects = self.enemies + self.items
        all_objects.sort(key=lambda obj: -math.sqrt((self.player.x - obj.x)**2 + (self.player.y - obj.y)**2))
        
        for obj in all_objects:
            if not self.is_line_of_sight_blocked(self.player.x, self.player.y, obj.x, obj.y):
                self.draw_object(obj)
        
        # Affiche les projectiles (séparément, car ils sont des dictionnaires)
        for p in self.projectiles:
            if not self.is_line_of_sight_blocked(self.player.x, self.player.y, p['x'], p['y']):
                self.draw_projectile(p)

        crosshair_size = 10
        crosshair_color = "white"
        if self.player.special_ammo > 0 or self.player.damage_boost_time > 0:
            crosshair_color = DAMAGE_BOOST_CROSSHAIR
            
        self.canvas.create_line(WINDOW_WIDTH / 2 - crosshair_size, WINDOW_HEIGHT / 2, WINDOW_WIDTH / 2 + crosshair_size, WINDOW_HEIGHT / 2, fill=crosshair_color, width=2)
        self.canvas.create_line(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - crosshair_size, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + crosshair_size, fill=crosshair_color, width=2)
        
        if self.player.is_firing:
            self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="white", stipple="gray25", width=0)
            self.player.is_firing = False
        
        self.canvas.create_text(
            WINDOW_WIDTH / 2, 20,
            text=f"Balles: {self.player.ammo} | Spéciales: {self.player.special_ammo}",
            fill="white",
            font=("Helvetica", 16, "bold"),
            justify="center",
            anchor="center"
        )
        
        self.draw_minimap()

    def is_line_of_sight_blocked(self, x1, y1, x2, y2):
        """Vérifie si un mur bloque la ligne de vue entre deux points."""
        step = 0.1
        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist == 0:
            return False
            
        vx = dx / dist
        vy = dy / dist
        
        current_x = x1
        current_y = y1
        
        for _ in range(int(dist / step)):
            current_x += vx * step
            current_y += vy * step
            
            map_x = int(current_x)
            map_y = int(current_y)
            
            if 0 <= map_x < MAP_WIDTH and 0 <= map_y < MAP_HEIGHT:
                if self.map[map_y][map_x] == "W":
                    return True
        return False


    def draw_object(self, obj):
        """Dessine un ennemi ou un objet, en vérifiant la visibilité."""
        dx = obj.x - self.player.x
        dy = obj.y - self.player.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            angle_to_obj = math.atan2(dy, dx)
            angle_diff = angle_to_obj - self.player.angle
            
            if angle_diff > math.pi: angle_diff -= 2 * math.pi
            if angle_diff < -math.pi: angle_diff += 2 * math.pi
            
            if abs(angle_diff) <= FOV_RADIANS / 2:
                relative_angle = angle_diff + FOV_RADIANS / 2
                screen_x = (relative_angle / FOV_RADIANS) * WINDOW_WIDTH
                
                size_multiplier = 0.5
                fill_color = ""
                
                if isinstance(obj, Enemy):
                    if obj.enemy_type == 'normal':
                        fill_color = ENEMY_COLOR
                    elif obj.enemy_type == 'fast':
                        fill_color = FAST_ENEMY_COLOR
                        size_multiplier = 0.4
                    elif obj.enemy_type == 'strong':
                        fill_color = STRONG_ENEMY_COLOR
                        size_multiplier = 0.6
                    elif obj.enemy_type == 'shooter':
                        fill_color = SHOOTER_ENEMY_COLOR
                        size_multiplier = 0.5
                    elif obj.enemy_type == 'boss':
                        fill_color = BOSS_ENEMY_COLOR
                        size_multiplier = 0.9
                    
                    size = (CELL_SIZE * 50) / (dist + 0.001) * size_multiplier
                    
                    health_bar_width = size
                    health_bar_height = size * 0.1
                    health_max = 50
                    if obj.enemy_type == 'fast': health_max = 30
                    if obj.enemy_type == 'strong': health_max = 100
                    if obj.enemy_type == 'shooter': health_max = 40
                    if obj.enemy_type == 'boss': health_max = 250
                    
                    health_percentage = obj.health / health_max
                    self.canvas.create_rectangle(
                        screen_x - health_bar_width / 2, WINDOW_HEIGHT / 2 - size / 2 - 10,
                        screen_x - health_bar_width / 2 + health_bar_width * health_percentage, WINDOW_HEIGHT / 2 - size / 2 - 5,
                        fill="lime", width=0
                    )
                elif isinstance(obj, Item):
                    if obj.type == 'health':
                        fill_color = HEALTH_PACK_COLOR
                    elif obj.type == 'ammo':
                        fill_color = AMMO_PACK_COLOR
                    elif obj.type == 'special_ammo':
                        fill_color = SPECIAL_AMMO_COLOR
                    elif obj.type == 'speed_boost':
                        fill_color = SPEED_BOOST_COLOR
                    elif obj.type == 'damage_boost':
                        fill_color = DAMAGE_BOOST_COLOR
                    elif obj.type == 'firerate_boost':
                        fill_color = FIRERATE_BOOST_COLOR
                        
                    size_multiplier = 0.2
                    size = (CELL_SIZE * 50) / (dist + 0.001) * size_multiplier
                    
                self.canvas.create_oval(
                    screen_x - size / 2, WINDOW_HEIGHT / 2 - size / 2,
                    screen_x + size / 2, WINDOW_HEIGHT / 2 + size / 2,
                    fill=fill_color, outline="white"
                )

    def draw_projectile(self, p):
        """Dessine un projectile à l'écran."""
        dx = p['x'] - self.player.x
        dy = p['y'] - self.player.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            angle_to_p = math.atan2(dy, dx)
            angle_diff = angle_to_p - self.player.angle
            
            if angle_diff > math.pi: angle_diff -= 2 * math.pi
            if angle_diff < -math.pi: angle_diff += 2 * math.pi
            
            if abs(angle_diff) <= FOV_RADIANS / 2:
                relative_angle = angle_diff + FOV_RADIANS / 2
                screen_x = (relative_angle / FOV_RADIANS) * WINDOW_WIDTH
                
                size = (CELL_SIZE * 50) / (dist + 0.001) / 10
                
                fill_color = "white"
                if p['type'] == 'special':
                    fill_color = SPECIAL_AMMO_COLOR
                elif p['type'] == 'enemy':
                    fill_color = "purple"
                
                self.canvas.create_oval(
                    screen_x - size / 2, WINDOW_HEIGHT / 2 - size / 2,
                    screen_x + size / 2, WINDOW_HEIGHT / 2 + size / 2,
                    fill=fill_color, outline="white"
                )

    def draw_minimap(self):
        """Dessine une mini-carte en haut à droite de l'écran, avec une taille réduite."""
        scale_factor = 6 # Facteur de réduction
        minimap_width = MAP_WIDTH * scale_factor
        minimap_height = MAP_HEIGHT * scale_factor
        minimap_x_offset = WINDOW_WIDTH - minimap_width - 10
        minimap_y_offset = 10
        
        self.canvas.create_rectangle(minimap_x_offset, minimap_y_offset,
                                     minimap_x_offset + minimap_width, minimap_y_offset + minimap_height,
                                     fill="#222", outline="white", width=2)
        
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if 0 <= y < len(self.map) and 0 <= x < len(self.map[y]):
                    if self.map[y][x] == "W":
                        self.canvas.create_rectangle(
                            minimap_x_offset + x * scale_factor, minimap_y_offset + y * scale_factor,
                            minimap_x_offset + (x+1) * scale_factor, minimap_y_offset + (y+1) * scale_factor,
                            fill=WALL_COLOR
                        )
        
        player_mm_x = minimap_x_offset + self.player.x * scale_factor
        player_mm_y = minimap_y_offset + self.player.y * scale_factor
        self.canvas.create_oval(
            player_mm_x - 2, player_mm_y - 2, player_mm_x + 2, player_mm_y + 2,
            fill="blue", outline="blue"
        )
        self.canvas.create_line(
            player_mm_x, player_mm_y,
            player_mm_x + math.cos(self.player.angle) * scale_factor * 2,
            player_mm_y + math.sin(self.player.angle) * scale_factor * 2,
            fill="blue", width=2
        )
        
        # Affiche tous les ennemis sur la mini-carte
        for enemy in self.enemies:
            color = ENEMY_COLOR
            if enemy.enemy_type == 'fast': color = FAST_ENEMY_COLOR
            if enemy.enemy_type == 'strong': color = STRONG_ENEMY_COLOR
            if enemy.enemy_type == 'shooter': color = SHOOTER_ENEMY_COLOR
            if enemy.enemy_type == 'boss': color = BOSS_ENEMY_COLOR
            
            self.canvas.create_oval(
                minimap_x_offset + enemy.x * scale_factor - 2, minimap_y_offset + enemy.y * scale_factor - 2,
                minimap_x_offset + enemy.x * scale_factor + 2, minimap_y_offset + enemy.y * scale_factor + 2,
                fill=color, outline="white"
            )
        
        # Affiche tous les objets sur la mini-carte
        for item in self.items:
            color = HEALTH_PACK_COLOR
            if item.type == 'ammo': color = AMMO_PACK_COLOR
            if item.type == 'special_ammo': color = SPECIAL_AMMO_COLOR
            if item.type == 'speed_boost': color = SPEED_BOOST_COLOR
            if item.type == 'damage_boost': color = DAMAGE_BOOST_COLOR
            if item.type == 'firerate_boost': color = FIRERATE_BOOST_COLOR

            self.canvas.create_oval(
                minimap_x_offset + item.x * scale_factor - 1, minimap_y_offset + item.y * scale_factor - 1,
                minimap_x_offset + item.x * scale_factor + 1, minimap_y_offset + item.y * scale_factor + 1,
                fill=color, outline=color
            )
        
        for p in self.projectiles:
            fill_color = "yellow" if p['type'] == 'normal' else SPECIAL_AMMO_COLOR
            if p['type'] == 'enemy': fill_color = "purple"
            self.canvas.create_oval(
                minimap_x_offset + p['x'] * scale_factor - 1, minimap_y_offset + p['y'] * scale_factor - 1,
                minimap_x_offset + p['x'] * scale_factor + 1, minimap_y_offset + p['y'] * scale_factor + 1,
                fill=fill_color, outline=fill_color
            )


    def ray_cast(self, start_x, start_y, angle):
        """Projete un rayon pour trouver la distance jusqu'au mur le plus proche."""
        step = 0.1
        distance = 0
        
        while distance < 20:
            x = start_x + distance * math.cos(angle)
            y = start_y + distance * math.sin(angle)
            
            map_x = int(x)
            map_y = int(y)
            
            if not (0 <= map_x < MAP_WIDTH and 0 <= map_y < MAP_HEIGHT):
                return 20
                
            if self.map[map_y][map_x] == "W":
                return distance
            
            distance += step
        
        return 20

    def move_forward(self, event):
        """Déplace le joueur vers l'avant (Z)."""
        if not self.running: return
        speed = PLAYER_SPEED
        if self.player.speed_boost_time > 0:
            speed = PLAYER_SPEED_BOOST
            
        new_x = self.player.x + math.cos(self.player.angle) * speed / CELL_SIZE
        new_y = self.player.y + math.sin(self.player.angle) * speed / CELL_SIZE
        
        if 0 <= int(new_x) < MAP_WIDTH and 0 <= int(new_y) < MAP_HEIGHT and self.map[int(new_y)][int(new_x)] != "W":
            self.player.x = new_x
            self.player.y = new_y

    def move_backward(self, event):
        """Déplace le joueur vers l'arrière (S)."""
        if not self.running: return
        speed = PLAYER_SPEED
        if self.player.speed_boost_time > 0:
            speed = PLAYER_SPEED_BOOST
            
        new_x = self.player.x - math.cos(self.player.angle) * speed / CELL_SIZE
        new_y = self.player.y - math.sin(self.player.angle) * speed / CELL_SIZE
        
        if 0 <= int(new_x) < MAP_WIDTH and 0 <= int(new_y) < MAP_HEIGHT and self.map[int(new_y)][int(new_x)] != "W":
            self.player.x = new_x
            self.player.y = new_y

    def rotate_left(self, event):
        """Fait pivoter le joueur à gauche (Q)."""
        if not self.running: return
        self.player.angle -= ROTATION_SPEED

    def rotate_right(self, event):
        """Fait pivoter le joueur à droite (D)."""
        if not self.running: return
        self.player.angle += ROTATION_SPEED

    def fire_gun(self, event=None):
        """Gère l'action de tir. Crée un projectile au lieu de frapper instantanément."""
        if not self.running:
            return

        fire_cooldown = 0.2 # 5 tirs par seconde
        if self.player.firerate_boost_time > 0:
            fire_cooldown = 0.1 # 10 tirs par seconde
        
        if time.time() - self.last_fire_time < fire_cooldown:
            return
            
        self.last_fire_time = time.time()
        
        bullet_type = "normal"
        if self.player.special_ammo > 0:
            self.player.special_ammo -= 1
            bullet_type = "special"
        elif self.player.ammo > 0:
            self.player.ammo -= 1
        else:
            return
            
        self.player.is_firing = True # Active l'effet visuel de tir
        
        new_projectile = {
            'x': self.player.x,
            'y': self.player.y,
            'angle': self.player.angle,
            'speed': BULLET_SPEED,
            'lifetime': 150,
            'type': bullet_type
        }
        self.projectiles.append(new_projectile)
        
# --- Point d'entrée de l'application ---
if __name__ == "__main__":
    root = tk.Tk()
    game = FPSGame(root)
    root.mainloop()
