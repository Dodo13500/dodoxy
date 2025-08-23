import tkinter as tk
from tkinter import messagebox
import random
import time
import math

# --- Constantes du jeu ---
# Dimensions de la fenêtre
WIDTH = 800
HEIGHT = 600
# Taille d'une cellule de la grille
GRID_SIZE = 40

# Couleurs pour une esthétique professionnelle
BACKGROUND_COLOR = "#1a1a2e"
PATH_COLOR = "#2a3b50"
GRASS_COLOR = "#34495e"
UI_COLOR = "#2d3748"
INFO_TEXT_COLOR = "#ecf0e1"
BUTTON_COLOR = "#f39c12"
UPGRADE_BUTTON_COLOR = "#2980b9"
SELL_BUTTON_COLOR = "#e74c3c"
HEALTH_BAR_COLOR_FULL = "#27ae60"
HEALTH_BAR_COLOR_LOW = "#e74c3c"

# Couleurs des tours et des projectiles
TOWER_COLORS = {
    "Base": "#bdc3c7",
    "Fire": "#e67e22",
    "Ice": "#3498db",
    "Air": "#95a5a6",
    "Sniper": "#7f8c8d",
    "Poison": "#8e44ad"
}
PROJECTILE_COLORS = {
    "Base": "#bdc3c7",
    "Fire": "#e67e22",
    "Ice": "#3498db",
    "Air": "#95a5a6",
    "Sniper": "#7f8c8d",
    "Poison": "#8e44ad"
}

# Couleurs des ennemis
ENEMY_COLORS = {
    "Base": "#e74c3c",
    "Tank": "#8e44ad",
    "Fast": "#f1c40f",
    "Flying": "#2ecc71",
    "Boss": "#c0392b",
    "Ghost": "#bdc3c7"
}

# Coûts des tours
TOWER_COSTS = {
    "Base": 100,
    "Fire": 150,
    "Ice": 150,
    "Air": 175,
    "Sniper": 250,
    "Poison": 200
}

# Données des vagues
WAVE_DATA = {
    1: [("Base", 10)],
    2: [("Base", 15)],
    3: [("Base", 10), ("Fast", 5)],
    4: [("Base", 15), ("Fast", 10)],
    5: [("Boss", 1)],
    6: [("Base", 10), ("Tank", 5)],
    7: [("Base", 15), ("Tank", 10)],
    8: [("Fast", 15), ("Ghost", 5)],
    9: [("Base", 10), ("Fast", 10), ("Tank", 5), ("Flying", 3)],
    10: [("Boss", 1)],
    11: [("Base", 15), ("Fast", 15), ("Tank", 10), ("Flying", 5), ("Ghost", 5)],
    12: [("Fast", 20), ("Tank", 15), ("Flying", 10)]
}

# --- Classe principale du jeu ---
class TowerDefenseGame(tk.Frame):
    """
    Classe principale du jeu Tower Defense.
    Contient la logique du jeu, la gestion des objets et l'interface utilisateur.
    """
    def __init__(self, master):
        super().__init__(master, bg=BACKGROUND_COLOR)
        self.pack(expand=True, fill="both")
        self.master = master

        # Variables d'état du jeu
        self.game_running = True
        self.paused = False
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.wave_number = 0
        self.money = 300
        self.health = 100
        self.placing_tower = None  # Type de tour à placer
        self.selected_tower = None
        self.path = []
        self.path_pixels = []
        self.enemy_spawn_queue = []
        self.last_spawn_time = 0
        self.current_message = ""
        self.message_end_time = 0
        self.tower_range_circle_id = None
        self.can_place = True
        self.effects = []
        self.tower_preview_rect = None

        # Crée l'interface utilisateur et génère le chemin
        self.create_ui()
        self.generate_path()
        self.draw_path()

        # Lie les événements du canevas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        
        # Démarre la boucle de jeu
        self.master.after(100, self.game_loop)
        
    def create_ui(self):
        """
        Crée tous les éléments de l'interface utilisateur.
        """
        # Canevas pour l'aire de jeu
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg=GRASS_COLOR, highlightthickness=0)
        self.canvas.pack(side="left", padx=10, pady=10)
        
        # Panneau de contrôle
        self.control_panel = tk.Frame(self, width=250, bg=UI_COLOR)
        self.control_panel.pack(side="right", fill="y", padx=10, pady=10)
        self.control_panel.pack_propagate(False)

        # Affichage des statistiques
        stats_frame = tk.Frame(self.control_panel, bg=UI_COLOR)
        stats_frame.pack(pady=10)
        self.wave_label = tk.Label(stats_frame, text="Vague: 0", font=("Arial", 16, "bold"), bg=UI_COLOR, fg=INFO_TEXT_COLOR)
        self.wave_label.pack(side="top")
        self.money_label = tk.Label(stats_frame, text=f"Argent: ${self.money}", font=("Arial", 16, "bold"), bg=UI_COLOR, fg=INFO_TEXT_COLOR)
        self.money_label.pack(side="top")
        self.health_label = tk.Label(stats_frame, text=f"Santé: {self.health}", font=("Arial", 16, "bold"), bg=UI_COLOR, fg=INFO_TEXT_COLOR)
        self.health_label.pack(side="top")
        
        # Message en jeu
        self.message_label = tk.Label(self.control_panel, text="", font=("Arial", 10), bg=UI_COLOR, fg="#2ecc71")
        self.message_label.pack(pady=5)

        # Bouton Pause/Reprendre
        self.pause_button = tk.Button(self.control_panel, text="Pause", font=("Arial", 12), command=self.toggle_pause, bg=BUTTON_COLOR, fg="white", bd=0, relief="flat")
        self.pause_button.pack(pady=10, fill="x")

        # Panneau de construction défilant
        tk.Label(self.control_panel, text="Construire une tour:", font=("Arial", 14), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack(pady=5)
        
        scroll_container = tk.Frame(self.control_panel, bg=UI_COLOR)
        scroll_container.pack(expand=True, fill="both")

        self.tower_canvas = tk.Canvas(scroll_container, bg=UI_COLOR, highlightthickness=0)
        self.tower_canvas.pack(side="left", expand=True, fill="both")

        tower_scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=self.tower_canvas.yview)
        tower_scrollbar.pack(side="right", fill="y")
        self.tower_canvas.configure(yscrollcommand=tower_scrollbar.set)

        self.tower_frame = tk.Frame(self.tower_canvas, bg=UI_COLOR)
        self.tower_canvas.create_window((0, 0), window=self.tower_frame, anchor="nw")

        self.tower_frame.bind("<Configure>", lambda e: self.tower_canvas.configure(scrollregion=self.tower_canvas.bbox("all")))
        self.tower_canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

        for tower_type, cost in TOWER_COSTS.items():
            tk.Button(self.tower_frame, text=f"{tower_type} (${cost})", font=("Arial", 12),
                      command=lambda t=tower_type: self.start_placing_tower(t), 
                      bg=TOWER_COLORS[tower_type], fg="white", bd=0, relief="flat").pack(pady=5, fill="x")
        
        # Panneau d'amélioration/vente de tour
        self.upgrade_panel = tk.Frame(self.control_panel, bg=UI_COLOR)
        self.upgrade_panel.pack(pady=20, fill="x")
        self.show_upgrade_panel()
        
    def _on_mouse_wheel(self, event):
        """
        Gère l'événement de la molette de la souris pour le défilement.
        """
        self.tower_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def on_canvas_motion(self, event):
        """
        Gère le mouvement de la souris pour afficher la portée de la tour en cours de placement.
        """
        if self.placing_tower:
            x, y = event.x, event.y
            
            # Supprime le cercle de portée précédent
            if self.tower_range_circle_id:
                self.canvas.delete(self.tower_range_circle_id)
            
            # Détermine la classe de la tour pour obtenir sa portée
            tower_class_map = {
                "Base": BaseTower, "Fire": FireTower, "Ice": IceTower, "Air": AirTower,
                "Sniper": SniperTower, "Poison": PoisonTower
            }
            tower_class = tower_class_map.get(self.placing_tower)
            
            if tower_class:
                tower_range = tower_class.initial_range
                self.tower_range_circle_id = self.canvas.create_oval(
                    x - tower_range, y - tower_range, x + tower_range, y + tower_range,
                    outline=INFO_TEXT_COLOR, dash=(5, 5)
                )

            # Vérifie si le placement est possible à la position actuelle
            grid_x = x // GRID_SIZE
            grid_y = y // GRID_SIZE
            is_on_path = (grid_y, grid_x) in self.path
            is_occupied = any(t.grid_x == grid_x and t.grid_y == grid_y for t in self.towers)
            
            # Supprime la prévisualisation précédente
            if self.tower_preview_rect:
                self.canvas.delete(self.tower_preview_rect)

            fill_color = "red" if is_on_path or is_occupied else "lime"
            self.can_place = not is_on_path and not is_occupied
            
            self.tower_preview_rect = self.canvas.create_rectangle(
                grid_x * GRID_SIZE, grid_y * GRID_SIZE,
                (grid_x + 1) * GRID_SIZE, (grid_y + 1) * GRID_SIZE,
                fill="", outline=fill_color, width=2)
            
    def show_message(self, message, duration=3000, color="#2ecc71"):
        """
        Affiche un message temporaire sur l'interface utilisateur.
        """
        self.current_message = message
        self.message_end_time = time.time() + (duration / 1000)
        self.message_label.config(text=message, fg=color)

    def toggle_pause(self):
        """
        Met le jeu en pause ou le reprend.
        """
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="Reprendre")
            self.show_message("Jeu en pause", color="#f1c40f")
        else:
            self.pause_button.config(text="Pause")
            self.show_message("Jeu repris", color="#2ecc71")
            self.game_loop()

    def on_canvas_click(self, event):
        """
        Gère les clics sur le canevas pour placer et sélectionner des tours.
        """
        x, y = event.x, event.y
        grid_x = x // GRID_SIZE
        grid_y = y // GRID_SIZE
        
        # Supprime le cercle de prévisualisation
        if self.tower_range_circle_id:
            self.canvas.delete(self.tower_range_circle_id)
            self.tower_range_circle_id = None
        if self.tower_preview_rect:
            self.canvas.delete(self.tower_preview_rect)
            self.tower_preview_rect = None

        if self.placing_tower and self.can_place:
            self.place_tower(grid_x, grid_y)
            self.placing_tower = None
        else:
            self.placing_tower = None
            self.select_tower(x, y)
            
    def generate_path(self):
        """
        Génère un chemin aléatoire pour les ennemis.
        """
        rows = HEIGHT // GRID_SIZE
        cols = WIDTH // GRID_SIZE
        
        start_pos = (random.randint(0, rows-1), 0)
        end_pos = (random.randint(0, rows-1), cols-1)
        
        current = start_pos
        self.path.append(current)
        
        while current != end_pos:
            r, c = current
            possible_moves = []
            
            # Priorise le mouvement vers le point de fin
            if c < end_pos[1] and (r, c + 1) not in self.path: possible_moves.append((r, c + 1))
            if r < end_pos[0] and (r + 1, c) not in self.path: possible_moves.append((r + 1, c))
            if r > end_pos[0] and (r - 1, c) not in self.path: possible_moves.append((r - 1, c))
            
            # Si aucune direction directe, essaye d'autres directions
            if not possible_moves:
                if c + 1 < cols and (r, c + 1) not in self.path: possible_moves.append((r, c + 1))
                if r + 1 < rows and (r + 1, c) not in self.path: possible_moves.append((r + 1, c))
                if r - 1 >= 0 and (r - 1, c) not in self.path: possible_moves.append((r - 1, c))
                
            if possible_moves:
                current = random.choice(possible_moves)
                self.path.append(current)
            else:
                self.path = []
                self.generate_path()
                return

        self.path_pixels = [(p[1] * GRID_SIZE + GRID_SIZE // 2, p[0] * GRID_SIZE + GRID_SIZE // 2) for p in self.path]

    def draw_path(self):
        """
        Dessine le chemin généré sur le canevas.
        """
        for r, c in self.path:
            self.canvas.create_rectangle(c*GRID_SIZE, r*GRID_SIZE, (c+1)*GRID_SIZE, (r+1)*GRID_SIZE, fill=PATH_COLOR, outline="")

        # Marqueurs de début et de fin
        self.canvas.create_oval(self.path[0][1]*GRID_SIZE, self.path[0][0]*GRID_SIZE, (self.path[0][1]+1)*GRID_SIZE, (self.path[0][0]+1)*GRID_SIZE, fill="#27ae60", outline="")
        self.canvas.create_oval(self.path[-1][1]*GRID_SIZE, self.path[-1][0]*GRID_SIZE, (self.path[-1][1]+1)*GRID_SIZE, (self.path[-1][0]+1)*GRID_SIZE, fill="#c0392b", outline="")

    def start_placing_tower(self, tower_type):
        """
        Met le jeu en mode "placement de tour" si le joueur a assez d'argent.
        """
        cost = TOWER_COSTS[tower_type]
        if self.money >= cost:
            self.placing_tower = tower_type
            self.show_message(f"Cliquez pour placer une tour de {tower_type}", color=INFO_TEXT_COLOR)
        else:
            self.show_message("Pas assez d'argent !", color="#e74c3c")
            
    def place_tower(self, grid_x, grid_y):
        """
        Place une tour sur la grille.
        """
        tower_type = self.placing_tower
        cost = TOWER_COSTS[tower_type]
        
        new_tower = None
        if tower_type == "Base":
            new_tower = BaseTower(self, self.canvas, grid_x, grid_y)
        elif tower_type == "Fire":
            new_tower = FireTower(self, self.canvas, grid_x, grid_y)
        elif tower_type == "Ice":
            new_tower = IceTower(self, self.canvas, grid_x, grid_y)
        elif tower_type == "Air":
            new_tower = AirTower(self, self.canvas, grid_x, grid_y)
        elif tower_type == "Sniper":
            new_tower = SniperTower(self, self.canvas, grid_x, grid_y)
        elif tower_type == "Poison":
            new_tower = PoisonTower(self, self.canvas, grid_x, grid_y)
        
        self.towers.append(new_tower)
        self.money -= cost
        self.update_stats()
        self.placing_tower = None
        self.show_message(f"Tour de {tower_type} placée !", color="#2ecc71")
    
    def select_tower(self, x, y):
        """
        Sélectionne une tour et affiche ses options d'amélioration.
        """
        # Masque la portée de toutes les tours
        for tower in self.towers:
            self.canvas.itemconfigure(tower.range_circle, state=tk.HIDDEN)
            
        self.selected_tower = None
        for tower in self.towers:
            dist = math.hypot(x - tower.x, y - tower.y)
            if dist < 20:
                self.selected_tower = tower
                break
        
        self.show_upgrade_panel()
        
    def show_upgrade_panel(self):
        """
        Affiche le panneau d'amélioration pour la tour sélectionnée.
        """
        for widget in self.upgrade_panel.winfo_children():
            widget.destroy()
            
        if self.selected_tower:
            self.canvas.itemconfigure(self.selected_tower.range_circle, state=tk.NORMAL)
            
            tk.Label(self.upgrade_panel, text=f"Tour {self.selected_tower.type}", font=("Arial", 16, "bold"), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack(pady=5)
            tk.Label(self.upgrade_panel, text=f"Niveau: {self.selected_tower.level}", font=("Arial", 12), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack()
            tk.Label(self.upgrade_panel, text=f"Dégâts: {self.selected_tower.damage:.1f}", font=("Arial", 12), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack()
            tk.Label(self.upgrade_panel, text=f"Cadence de tir: {self.selected_tower.fire_rate:.2f}s", font=("Arial", 12), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack()
            tk.Label(self.upgrade_panel, text=f"Portée: {self.selected_tower.attack_range:.1f}", font=("Arial", 12), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack()
            
            if self.selected_tower.level < 3:
                tk.Button(self.upgrade_panel, text=f"Améliorer Dégâts (${self.selected_tower.upgrade_damage_cost:.0f})", font=("Arial", 12),
                          command=lambda: self.upgrade_tower(self.selected_tower, "damage"), 
                          bg=UPGRADE_BUTTON_COLOR, fg="white", bd=0, relief="flat").pack(pady=5, fill="x")

                tk.Button(self.upgrade_panel, text=f"Améliorer Cadence (${self.selected_tower.upgrade_rate_cost:.0f})", font=("Arial", 12),
                          command=lambda: self.upgrade_tower(self.selected_tower, "rate"), 
                          bg=UPGRADE_BUTTON_COLOR, fg="white", bd=0, relief="flat").pack(pady=5, fill="x")

                tk.Button(self.upgrade_panel, text=f"Améliorer Portée (${self.selected_tower.upgrade_range_cost:.0f})", font=("Arial", 12),
                          command=lambda: self.upgrade_tower(self.selected_tower, "range"), 
                          bg=UPGRADE_BUTTON_COLOR, fg="white", bd=0, relief="flat").pack(pady=5, fill="x")
            
            sell_price = int(self.selected_tower.get_sell_price())
            tk.Button(self.upgrade_panel, text=f"Vendre (${sell_price})", font=("Arial", 12),
                      command=lambda: self.sell_tower(self.selected_tower), 
                      bg=SELL_BUTTON_COLOR, fg="white", bd=0, relief="flat").pack(pady=10, fill="x")

        else:
            for tower in self.towers:
                self.canvas.itemconfigure(tower.range_circle, state=tk.HIDDEN)
            tk.Label(self.upgrade_panel, text="Cliquez sur une tour pour l'améliorer.", font=("Arial", 12), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack()
            
    def upgrade_tower(self, tower, upgrade_type):
        """
        Améliore les dégâts, la cadence de tir ou la portée de la tour sélectionnée.
        """
        cost = 0
        if upgrade_type == "damage":
            cost = int(tower.upgrade_damage_cost)
            if self.money >= cost:
                self.money -= cost
                tower.upgrade_damage()
                self.show_message("Dégâts améliorés !", color="#f39c12")
            else:
                self.show_message("Pas assez d'argent pour améliorer les dégâts.", color="#e74c3c")
                
        elif upgrade_type == "rate":
            cost = int(tower.upgrade_rate_cost)
            if self.money >= cost:
                self.money -= cost
                tower.upgrade_fire_rate()
                self.show_message("Cadence de tir améliorée !", color="#f39c12")
            else:
                self.show_message("Pas assez d'argent pour améliorer la cadence.", color="#e74c3c")
        
        elif upgrade_type == "range":
            cost = int(tower.upgrade_range_cost)
            if self.money >= cost:
                self.money -= cost
                tower.upgrade_range()
                self.show_message("Portée améliorée !", color="#f39c12")
            else:
                self.show_message("Pas assez d'argent pour améliorer la portée.", color="#e74c3c")
        
        self.update_stats()
        self.show_upgrade_panel()

    def sell_tower(self, tower):
        """
        Vend une tour et rembourse une partie de son coût.
        """
        sell_price = int(tower.get_sell_price())
        self.money += sell_price
        self.towers.remove(tower)
        tower.destroy()
        self.selected_tower = None
        self.show_upgrade_panel()
        self.update_stats()
        self.show_message(f"Tour vendue pour ${sell_price}", color="#e74c3c")
                
    def spawn_wave(self):
        """
        Démarre une nouvelle vague d'ennemis.
        """
        self.wave_number += 1
        self.wave_label.config(text=f"Vague: {self.wave_number}")
        self.show_message(f"Vague {self.wave_number} en approche !", color="#f1c40f")
        
        if self.wave_number in WAVE_DATA:
            wave_info = WAVE_DATA[self.wave_number]
            for enemy_type, count in wave_info:
                for _ in range(count):
                    self.enemy_spawn_queue.append(enemy_type)
        elif self.wave_number % 5 == 0:
            self.enemy_spawn_queue.append("Boss")
        else:
            # Génère une vague personnalisée si les vagues prédéfinies sont terminées
            num_enemies = 10 + self.wave_number * 3
            enemy_types = list(ENEMY_COLORS.keys())
            if "Boss" in enemy_types: enemy_types.remove("Boss")
            for _ in range(num_enemies):
                self.enemy_spawn_queue.append(random.choice(enemy_types))
            
        random.shuffle(self.enemy_spawn_queue)

    def update_stats(self):
        """
        Met à jour les labels de l'interface utilisateur.
        """
        self.money_label.config(text=f"Argent: ${self.money}")
        self.health_label.config(text=f"Santé: {self.health}")
        
    def game_loop(self):
        """
        Boucle de jeu principale.
        Gère la logique de jeu, les mises à jour et les rendus.
        """
        if not self.game_running or self.paused:
            self.master.after(20, self.game_loop)
            return

        # Vérifie si le message est expiré
        if self.current_message and time.time() > self.message_end_time:
            self.message_label.config(text="")

        # Gère les vagues
        if not self.enemies and not self.enemy_spawn_queue:
            self.spawn_wave()
        
        # Fait apparaître les ennemis de la file d'attente
        if self.enemy_spawn_queue and time.time() - self.last_spawn_time > 1:
            enemy_type = self.enemy_spawn_queue.pop(0)
            if enemy_type == "Base":
                self.enemies.append(Enemy(self, self.canvas, self.path_pixels, 1))
            elif enemy_type == "Fast":
                self.enemies.append(FastEnemy(self, self.canvas, self.path_pixels, 1))
            elif enemy_type == "Tank":
                self.enemies.append(TankEnemy(self, self.canvas, self.path_pixels, 1))
            elif enemy_type == "Flying":
                self.enemies.append(FlyingEnemy(self, self.canvas, self.path_pixels, 1))
            elif enemy_type == "Boss":
                self.enemies.append(BossEnemy(self, self.canvas, self.path_pixels, 1))
            elif enemy_type == "Ghost":
                self.enemies.append(GhostEnemy(self, self.canvas, self.path_pixels, 1))
            self.last_spawn_time = time.time()
        
        # Met à jour les effets
        active_effects = []
        for effect in self.effects:
            if effect.update():
                active_effects.append(effect)
        self.effects = active_effects

        # Met à jour les ennemis
        active_enemies = []
        for enemy in self.enemies:
            if enemy.update():
                # L'ennemi a atteint la fin du chemin
                self.health -= 10
                self.update_stats()
                enemy.destroy()
                if self.health <= 0:
                    self.game_over()
            elif enemy.is_alive():
                active_enemies.append(enemy)
        self.enemies = active_enemies

        # Met à jour les tours
        for tower in self.towers:
            tower.update(self.enemies)
        
        # Met à jour les projectiles
        active_projectiles = []
        for p in self.projectiles:
            if p.update():
                active_projectiles.append(p)
        self.projectiles = active_projectiles

        self.master.after(20, self.game_loop)
        
    def game_over(self):
        """
        Met fin au jeu et affiche un message.
        """
        self.game_running = False
        messagebox.showinfo("Game Over", f"Vous avez atteint la vague {self.wave_number}.\n\nCrédits:\nCode Généré par Gemini")
        self.master.destroy()


# --- Classes des Tours ---
class BaseTower:
    """
    Représente une tour de base.
    """
    initial_range = 150
    
    def __init__(self, game, canvas, grid_x, grid_y):
        self.game = game
        self.canvas = canvas
        self.type = "Base"
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = grid_y * GRID_SIZE + GRID_SIZE // 2
        self.level = 1
        self.max_level = 3
        self.attack_range = self.initial_range
        self.fire_rate = 1.0
        self.damage = 10
        self.last_shot_time = time.time()
        self.upgrade_damage_cost = 50
        self.upgrade_rate_cost = 50
        self.upgrade_range_cost = 50
        self.initial_cost = TOWER_COSTS[self.type]
        self.is_projectile_tower = True
        
        self.draw()
        
    def draw(self):
        """
        Dessine la tour sur le canevas.
        """
        self.entity = self.canvas.create_polygon(
            self.x, self.y - 12, self.x - 10, self.y + 6, self.x + 10, self.y + 6,
            fill=TOWER_COLORS[self.type], outline="")
        self.range_circle = self.canvas.create_oval(
            self.x - self.attack_range, self.y - self.attack_range, 
            self.x + self.attack_range, self.y + self.attack_range, 
            outline=TOWER_COLORS[self.type], dash=(5, 5), state=tk.HIDDEN)
        
    def destroy(self):
        self.canvas.delete(self.entity)
        self.canvas.delete(self.range_circle)

    def get_sell_price(self):
        """
        Calcule le prix de vente de la tour.
        """
        total_cost = self.initial_cost + (self.upgrade_damage_cost - 50) + (self.upgrade_rate_cost - 50) + (self.upgrade_range_cost - 50)
        return total_cost * 0.75

    def update(self, enemies):
        """
        Met à jour l'état de la tour (cible et tire).
        """
        target = self.find_target(enemies)
        if target:
            self.fire(target)
            
    def find_target(self, enemies):
        """
        Trouve l'ennemi le plus proche de la fin du chemin dans la portée.
        Les tours au sol ignorent les ennemis volants et fantômes.
        """
        target = None
        max_path_index = -1
        
        for enemy in enemies:
            if not enemy.is_flying and not enemy.is_ghost:
                dist = math.hypot(self.x - enemy.x, self.y - enemy.y)
                if dist < self.attack_range and enemy.path_index > max_path_index:
                    max_path_index = enemy.path_index
                    target = enemy
        return target
        
    def fire(self, target):
        """
        Tire un projectile sur la cible.
        """
        if time.time() - self.last_shot_time > self.fire_rate:
            self.game.projectiles.append(Projectile(self.game, self.canvas, self.x, self.y, target, self.damage, PROJECTILE_COLORS[self.type]))
            self.last_shot_time = time.time()
            
    def upgrade_damage(self):
        self.damage *= 1.2
        self.upgrade_damage_cost *= 1.5
        self.level += 1
        self.show_level()

    def upgrade_fire_rate(self):
        self.fire_rate = max(0.2, self.fire_rate * 0.9)
        self.upgrade_rate_cost *= 1.5
        self.level += 1
        self.show_level()
    
    def upgrade_range(self):
        self.attack_range *= 1.15
        self.upgrade_range_cost *= 1.5
        self.canvas.coords(self.range_circle, self.x - self.attack_range, self.y - self.attack_range, 
                           self.x + self.attack_range, self.y + self.attack_range)
        self.level += 1
        self.show_level()
    
    def show_level(self):
        # Pour une meilleure visibilité, nous pourrions dessiner le niveau sur la tour.
        # Pour l'instant, c'est géré par le panneau d'amélioration.
        pass
        
class FireTower(BaseTower):
    initial_range = 120
    
    def __init__(self, game, canvas, grid_x, grid_y):
        super().__init__(game, canvas, grid_x, grid_y)
        self.type = "Fire"
        self.attack_range = self.initial_range
        self.fire_rate = 0.5
        self.damage = 15
        self.initial_cost = TOWER_COSTS[self.type]
        self.upgrade_damage_cost = 75
        self.upgrade_rate_cost = 75
        self.upgrade_range_cost = 75
        self.canvas.itemconfigure(self.entity, fill=TOWER_COLORS[self.type])
        self.canvas.itemconfigure(self.range_circle, outline=TOWER_COLORS[self.type])
        
class IceTower(BaseTower):
    initial_range = 180
    
    def __init__(self, game, canvas, grid_x, grid_y):
        super().__init__(game, canvas, grid_x, grid_y)
        self.type = "Ice"
        self.attack_range = self.initial_range
        self.fire_rate = 1.5
        self.damage = 5
        self.slow_factor = 0.5
        self.slow_duration = 1000
        self.initial_cost = TOWER_COSTS[self.type]
        self.upgrade_damage_cost = 75
        self.upgrade_rate_cost = 75
        self.upgrade_range_cost = 75
        self.canvas.itemconfigure(self.entity, fill=TOWER_COLORS[self.type])
        self.canvas.itemconfigure(self.range_circle, outline=TOWER_COLORS[self.type])
        
    def fire(self, target):
        if time.time() - self.last_shot_time > self.fire_rate:
            self.game.projectiles.append(IceProjectile(self.game, self.canvas, self.x, self.y, target, self.damage, PROJECTILE_COLORS[self.type], self.slow_factor, self.slow_duration))
            self.last_shot_time = time.time()
            
class AirTower(BaseTower):
    initial_range = 250

    def __init__(self, game, canvas, grid_x, grid_y):
        super().__init__(game, canvas, grid_x, grid_y)
        self.type = "Air"
        self.attack_range = self.initial_range
        self.fire_rate = 0.7
        self.damage = 25
        self.initial_cost = TOWER_COSTS[self.type]
        self.upgrade_damage_cost = 90
        self.upgrade_rate_cost = 90
        self.upgrade_range_cost = 90
        self.canvas.itemconfigure(self.entity, fill=TOWER_COLORS[self.type])
        self.canvas.itemconfigure(self.range_circle, outline=TOWER_COLORS[self.type])

    def find_target(self, enemies):
        """
        Trouve un ennemi volant dans la portée.
        """
        target = None
        max_path_index = -1
        
        for enemy in enemies:
            if enemy.is_flying:
                dist = math.hypot(self.x - enemy.x, self.y - enemy.y)
                if dist < self.attack_range and enemy.path_index > max_path_index:
                    max_path_index = enemy.path_index
                    target = enemy
        return target
    
class SniperTower(BaseTower):
    initial_range = 350
    
    def __init__(self, game, canvas, grid_x, grid_y):
        super().__init__(game, canvas, grid_x, grid_y)
        self.type = "Sniper"
        self.attack_range = self.initial_range
        self.fire_rate = 3.0
        self.damage = 75
        self.initial_cost = TOWER_COSTS[self.type]
        self.upgrade_damage_cost = 100
        self.upgrade_rate_cost = 100
        self.upgrade_range_cost = 100
        self.canvas.itemconfigure(self.entity, fill=TOWER_COLORS[self.type])
        self.canvas.itemconfigure(self.range_circle, outline=TOWER_COLORS[self.type])
        
    def find_target(self, enemies):
        """
        Cible l'ennemi avec le plus de santé.
        """
        target = None
        max_health = 0
        
        for enemy in enemies:
            dist = math.hypot(self.x - enemy.x, self.y - enemy.y)
            if dist < self.attack_range and enemy.health > max_health:
                max_health = enemy.health
                target = enemy
        return target
        
class PoisonTower(BaseTower):
    initial_range = 100
    
    def __init__(self, game, canvas, grid_x, grid_y):
        super().__init__(game, canvas, grid_x, grid_y)
        self.type = "Poison"
        self.attack_range = self.initial_range
        self.fire_rate = 1.0
        self.damage = 5
        self.initial_cost = TOWER_COSTS[self.type]
        self.upgrade_damage_cost = 80
        self.upgrade_rate_cost = 80
        self.upgrade_range_cost = 80
        self.canvas.itemconfigure(self.entity, fill=TOWER_COLORS[self.type])
        self.canvas.itemconfigure(self.range_circle, outline=TOWER_COLORS[self.type])
        
    def fire(self, target):
        if time.time() - self.last_shot_time > self.fire_rate:
            self.game.projectiles.append(PoisonProjectile(self.game, self.canvas, self.x, self.y, target, self.damage, PROJECTILE_COLORS[self.type]))
            self.last_shot_time = time.time()

# --- Classes des Ennemis ---
class Enemy:
    """
    Représente un ennemi qui se déplace le long du chemin.
    """
    def __init__(self, game, canvas, path_pixels, health_multiplier):
        self.game = game
        self.canvas = canvas
        self.path_pixels = path_pixels
        self.path_index = 0
        self.x, self.y = path_pixels[0]
        self.base_speed = 1.0
        self.speed = self.base_speed
        self.max_health = 20 * health_multiplier
        self.health = self.max_health
        self.alive = True
        self.color = ENEMY_COLORS["Base"]
        self.is_flying = False
        self.is_ghost = False
        self.draw()

    def draw(self):
        """
        Dessine l'ennemi et sa barre de vie.
        """
        self.entity = self.canvas.create_rectangle(self.x - 8, self.y - 8, self.x + 8, self.y + 8, fill=self.color, outline="")
        self.health_bar = self.canvas.create_rectangle(self.x - 10, self.y - 12, self.x + 10, self.y - 10, fill=HEALTH_BAR_COLOR_FULL, outline="")

    def update(self):
        """
        Met à jour la position de l'ennemi.
        Retourne True si l'ennemi a atteint la fin du chemin.
        """
        if not self.alive:
            return False

        if self.path_index < len(self.path_pixels):
            target_x, target_y = self.path_pixels[self.path_index]
            
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)
            
            if dist < self.speed:
                self.x, self.y = target_x, target_y
                self.path_index += 1
            else:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
            
            self.canvas.coords(self.entity, self.x - 8, self.y - 8, self.x + 8, self.y + 8)
            self.update_health_bar()
            return False
        
        return True
        
    def take_damage(self, damage):
        """
        Inflige des dégâts à l'ennemi.
        """
        self.health -= damage
        self.update_health_bar()
        if self.health <= 0:
            self.die()

    def update_health_bar(self):
        """
        Met à jour la barre de vie visuelle.
        """
        bar_width = 20 * (self.health / self.max_health) if self.max_health > 0 else 0
        fill_color = HEALTH_BAR_COLOR_LOW if self.health < self.max_health * 0.5 else HEALTH_BAR_COLOR_FULL
        self.canvas.coords(self.health_bar, self.x - 10, self.y - 12, self.x - 10 + bar_width, self.y - 10)
        self.canvas.itemconfigure(self.health_bar, fill=fill_color)

    def die(self):
        """
        Gère la défaite de l'ennemi.
        """
        if self.alive:
            self.alive = False
            self.canvas.delete(self.entity)
            self.canvas.delete(self.health_bar)
            self.game.money += 10
            self.game.update_stats()
            
    def is_alive(self):
        return self.alive
        
    def slow(self, factor, duration):
        """
        Applique un effet de ralentissement.
        """
        if self.speed > self.base_speed * factor:
            self.speed = self.base_speed * factor
            self.game.master.after(duration, self.reset_speed)
        
    def reset_speed(self):
        self.speed = self.base_speed

class FastEnemy(Enemy):
    def __init__(self, game, canvas, path_pixels, health_multiplier):
        super().__init__(game, canvas, path_pixels, health_multiplier)
        self.base_speed = 1.8
        self.speed = self.base_speed
        self.max_health = 15 * health_multiplier
        self.health = self.max_health
        self.color = ENEMY_COLORS["Fast"]
        self.canvas.itemconfigure(self.entity, fill=self.color, width=1)
        self.canvas.coords(self.entity, self.x - 6, self.y - 6, self.x + 6, self.y + 6)
        
class TankEnemy(Enemy):
    def __init__(self, game, canvas, path_pixels, health_multiplier):
        super().__init__(game, canvas, path_pixels, health_multiplier)
        self.base_speed = 0.6
        self.speed = self.base_speed
        self.max_health = 50 * health_multiplier
        self.health = self.max_health
        self.color = ENEMY_COLORS["Tank"]
        self.canvas.itemconfigure(self.entity, fill=self.color, width=1)
        self.canvas.coords(self.entity, self.x - 10, self.y - 10, self.x + 10, self.y + 10)

class FlyingEnemy(Enemy):
    def __init__(self, game, canvas, path_pixels, health_multiplier):
        super().__init__(game, canvas, path_pixels, health_multiplier)
        self.is_flying = True
        self.base_speed = 1.5
        self.speed = self.base_speed
        self.max_health = 25 * health_multiplier
        self.health = self.max_health
        self.color = ENEMY_COLORS["Flying"]
        self.canvas.delete(self.entity)
        self.entity = self.canvas.create_oval(self.x-8, self.y-8, self.x+8, self.y+8, fill=self.color, outline="")
        self.canvas.delete(self.health_bar)
        self.health_bar = self.canvas.create_rectangle(self.x - 10, self.y - 12, self.x + 10, self.y - 10, fill=HEALTH_BAR_COLOR_FULL, outline="")

class BossEnemy(Enemy):
    def __init__(self, game, canvas, path_pixels, health_multiplier):
        super().__init__(game, canvas, path_pixels, health_multiplier)
        self.base_speed = 0.5
        self.speed = self.base_speed
        self.max_health = 500 * health_multiplier
        self.health = self.max_health
        self.color = ENEMY_COLORS["Boss"]
        self.canvas.itemconfigure(self.entity, fill=self.color, width=1)
        self.canvas.coords(self.entity, self.x - 15, self.y - 15, self.x + 15, self.y + 15)

class GhostEnemy(Enemy):
    def __init__(self, game, canvas, path_pixels, health_multiplier):
        super().__init__(game, canvas, path_pixels, health_multiplier)
        self.base_speed = 1.6
        self.speed = self.base_speed
        self.max_health = 20 * health_multiplier
        self.health = self.max_health
        self.color = ENEMY_COLORS["Ghost"]
        self.is_ghost = True
        self.canvas.itemconfigure(self.entity, fill=self.color, outline=self.color, stipple="gray50")

# --- Classes des Projectiles et Effets ---
class Projectile:
    """
    Représente un projectile tiré par une tour.
    """
    def __init__(self, game, canvas, x, y, target, damage, color):
        self.game = game
        self.canvas = canvas
        self.x = x
        self.y = y
        self.target = target
        self.speed = 10
        self.damage = damage
        self.active = True
        
        self.entity = self.canvas.create_oval(self.x - 3, self.y - 3, self.x + 3, self.y + 3, fill=color, outline="")

    def update(self):
        """
        Met à jour la position du projectile.
        Retourne True si le projectile est toujours actif.
        """
        if not self.active or not self.target.is_alive():
            self.destroy()
            return False
            
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        
        if dist < self.speed:
            self.target.take_damage(self.damage)
            self.destroy()
            return False
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            self.canvas.coords(self.entity, self.x - 3, self.y - 3, self.x + 3, self.y + 3)
            return True

    def destroy(self):
        self.active = False
        self.canvas.delete(self.entity)
        
class IceProjectile(Projectile):
    """
    Projectile qui ralentit également la cible.
    """
    def __init__(self, game, canvas, x, y, target, damage, color, slow_factor, slow_duration):
        super().__init__(game, canvas, x, y, target, damage, color)
        self.slow_factor = slow_factor
        self.slow_duration = slow_duration
        
    def update(self):
        is_active = super().update()
        if not is_active and self.target.is_alive():
            self.target.slow(self.slow_factor, self.slow_duration)
        return is_active

class PoisonProjectile(Projectile):
    def __init__(self, game, canvas, x, y, target, damage, color):
        super().__init__(game, canvas, x, y, target, damage, color)

    def update(self):
        is_active = super().update()
        if not is_active and self.target.is_alive():
            self.game.effects.append(PoisonEffect(self.target, self.damage, 3000))
        return is_active

class PoisonEffect:
    def __init__(self, target, damage, duration):
        self.target = target
        self.damage = damage
        self.duration = duration
        self.start_time = time.time()
        self.last_tick = time.time()
        self.tick_interval = 0.5
        
    def update(self):
        if time.time() - self.start_time > (self.duration/1000):
            return False
            
        if time.time() - self.last_tick > self.tick_interval:
            self.target.take_damage(self.damage * self.tick_interval)
            self.last_tick = time.time()
            
        return True

# --- Classe d'application principale ---
class Application(tk.Tk):
    """
    Fenêtre principale de l'application.
    """
    def __init__(self):
        super().__init__()
        self.title("Tower Defense")
        self.geometry(f"{WIDTH + 250}x{HEIGHT + 20}")
        self.configure(bg=BACKGROUND_COLOR)
        
        self.current_frame = None
        self.show_main_menu()
        
    def show_main_menu(self):
        """
        Affiche le menu principal.
        """
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        self.current_frame.pack(expand=True, fill="both")
        
        title_label = tk.Label(self.current_frame, text="Tower Defense", font=("Arial", 60, "bold"), bg=BACKGROUND_COLOR, fg=INFO_TEXT_COLOR)
        title_label.pack(pady=50)

        play_button = tk.Button(self.current_frame, text="Jouer", font=("Arial", 20), command=self.start_game, bg=BUTTON_COLOR, fg="white", bd=0, relief="flat", width=15)
        play_button.pack(pady=20)
        
        tk.Label(self.current_frame, text="Le but est de défendre votre base contre les vagues d'ennemis.", font=("Arial", 12), bg=BACKGROUND_COLOR, fg=INFO_TEXT_COLOR).pack(pady=5)
        tk.Label(self.current_frame, text="Construisez des tours pour les arrêter avant qu'ils n'atteignent la fin du chemin.", font=("Arial", 12), bg=BACKGROUND_COLOR, fg=INFO_TEXT_COLOR).pack(pady=5)


    def start_game(self):
        """
        Démarre le jeu.
        """
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = TowerDefenseGame(self)

if __name__ == "__main__":
    app = Application()
    app.mainloop()
