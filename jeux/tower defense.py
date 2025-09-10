import tkinter as tk
from tkinter import messagebox, filedialog
import json
import random
import time
import math

# --- Constantes du jeu ---
# Dimensions de la fenêtre
WIDTH = 1000
HEIGHT = 1000
# Taille d'une cellule de la grille
GRID_SIZE = 40

# Couleurs pour une esthétique professionnelle (Palette Flat UI)
BACKGROUND_COLOR = "#2c3e50"  # Bleu marine foncé
PATH_COLOR = "#34495e"      # Gris-bleu
GRASS_COLOR = "#27ae60"     # Vert émeraude
UI_COLOR = "#1f2937"        # Gris très foncé
INFO_TEXT_COLOR = "#ecf0f1" # Blanc cassé
BUTTON_COLOR = "#e67e22"    # Orange (Carrot)
UPGRADE_BUTTON_COLOR = "#3498db" # Bleu (Peter River)
SELL_BUTTON_COLOR = "#e74c3c"    # Rouge (Alizarin)
HEALTH_BAR_COLOR_FULL = "#2ecc71" # Vert (Emerald)
HEALTH_BAR_COLOR_LOW = "#f1c40f"  # Jaune (Sunflower)
HEALTH_BAR_COLOR_CRIT = "#e74c3c" # Rouge (Alizarin)

# Couleurs des tours et des projectiles
TOWER_COLORS = {
    "Base": "#bdc3c7", # Argent
    "Fire": "#e67e22", # Orange
    "Ice": "#3498db",  # Bleu
    "Air": "#95a5a6",  # Gris
    "Sniper": "#7f8c8d", # Gris foncé
    "Poison": "#8e44ad", # Améthyste
    "Lightning": "#f1c40f" # Jaune
}
PROJECTILE_COLORS = {
    "Base": "#bdc3c7",
    "Fire": "#e67e22",
    "Ice": "#3498db",
    "Air": "#95a5a6",
    "Sniper": "#7f8c8d",
    "Poison": "#8e44ad",
    "Lightning": "#f1c40f"
}

# Couleurs des ennemis
ENEMY_COLORS = { # Couleurs Flat UI
    "Base": "#e74c3c",    # Alizarin
    "Tank": "#8e44ad",    # Amethyst
    "Fast": "#f1c40f",    # Sunflower
    "Flying": "#2ecc71",  # Emerald
    "Boss": "#c0392b",    # Pomegranate
    "Ghost": "#bdc3c7",   # Silver
    "Armored": "#7f8c8d", # Asbestos
    "Healer": "#1abc9c"   # Turquoise
}

# Coûts des tours
TOWER_COSTS = {
    "Base": 100,
    "Fire": 150,
    "Ice": 150,
    "Air": 175,
    "Sniper": 250,
    "Poison": 200,
    "Lightning": 225
}

# Données des vagues
WAVE_DATA = {
    1: [("Base", 10)], # Vague 1: 10 ennemis de base
    2: [("Base", 15)], # Vague 2: 15 ennemis de base
    3: [("Base", 10), ("Fast", 5)], # Vague 3: 10 base, 5 rapides
    4: [("Base", 15), ("Armored", 5)], # Vague 4: 15 base, 5 blindés
    5: [("Fast", 20)], # Vague 5: 20 rapides
    6: [("Base", 10), ("Tank", 5)], # Vague 6: 10 base, 5 tanks
    7: [("Base", 15), ("Tank", 10)], # Vague 7: 15 base, 10 tanks
    8: [("Fast", 15), ("Ghost", 5)], # Vague 8: 15 rapides, 5 fantômes
    9: [("Base", 10), ("Fast", 10), ("Tank", 5), ("Flying", 3)], # Vague 9: Mixte
    10: [("Boss", 1)], # Vague 10: 1 Boss
    11: [("Base", 15), ("Fast", 15), ("Tank", 10), ("Flying", 5), ("Ghost", 5)], # Vague 11: Grande vague mixte
    12: [("Fast", 20), ("Tank", 15), ("Flying", 10)], # Vague 12: Rapides, Tanks, Volants
    13: [("Armored", 15), ("Healer", 3)], # Vague 13: Blindés et Soigneurs
    14: [("Ghost", 10), ("Fast", 20)], # Vague 14: Fantômes et Rapides
    15: [("Boss", 1), ("Healer", 2)], # Vague 15: Boss et Soigneurs
    16: [("Tank", 20), ("Armored", 10)], # Vague 16: Tanks et Blindés
    17: [("Flying", 25)], # Vague 17: Que des volants
    18: [("Base", 50), ("Fast", 25)], # Vague 18: Grande vague de base et rapides
    19: [("Armored", 10), ("Tank", 10), ("Healer", 5)], # Vague 19: Blindés, Tanks, Soigneurs
    20: [("Boss", 2)] # Vague 20: 2 Boss
}

# --- Classe Tooltip ---
class Tooltip:
    """Crée une infobulle pour un widget donné."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tip_window, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None

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
        self.effects = []
        self.wave_number = 0
        self.money = 300
        self.health = 100
        self.placing_tower = None  # Type de tour à placer
        self.selected_tower = None
        self.path = []
        self.path_pixels = []
        self.enemy_spawn_queue = []
        self.last_spawn_time = 0
        self.spawn_interval = 0.5  # secondes
        self.current_message = ""
        self.message_end_time = 0
        self.tower_range_circle_id = None
        self.can_place = True
        self.tower_preview_rect = None
        self.last_update_time = time.time()
        self.is_panel_visible = True # Le panneau est visible par défaut
        self.game_speed = 1.0
        self.wave_in_progress = False
        self.interest_rate = 0.05 # 5% d'intérêts par vague

        # Crée l'interface utilisateur et génère le chemin
        self.create_ui()
        self.update_window_geometry() # Définit la taille initiale de la fenêtre
        self.generate_path()
        self.draw_path()

        # Lie les événements du canevas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        
        # Démarre la boucle de jeu
        self.master.after(100, self.game_loop)
        self.show_message("Préparez-vous ! Cliquez sur 'Vague Suivante' pour commencer.", duration=5000)

    def update_window_geometry(self):
        """Ajuste la taille de la fenêtre en fonction de la visibilité du panneau de contrôle."""
        if self.is_panel_visible:
            new_width = WIDTH + 250 + 30  # Largeur du canevas + panneau + marges
            self.master.geometry(f"{new_width}x{HEIGHT + 20}")
        else:
            new_width = WIDTH + 20  # Largeur du canevas + marges
            self.master.geometry(f"{new_width}x{HEIGHT + 20}")

    def create_ui(self):
        """
        Crée tous les éléments de l'interface utilisateur.
        """
        # Canevas pour l'aire de jeu
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg=GRASS_COLOR, highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        
        # Panneau de contrôle
        self.control_panel = tk.Frame(self, width=250, bg=UI_COLOR)
        self.control_panel.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=10)
        self.control_panel.pack_propagate(False)

        # --- Cadre d'informations ---
        info_frame = tk.LabelFrame(self.control_panel, text="Informations", bg=UI_COLOR, fg=INFO_TEXT_COLOR, padx=10, pady=10)
        info_frame.pack(pady=10, padx=10, fill="x")
        self.wave_label = tk.Label(info_frame, text="Vague: 0", font=("Segoe UI", 12, "bold"), bg=UI_COLOR, fg=INFO_TEXT_COLOR)
        self.wave_label.pack(anchor="w")
        self.money_label = tk.Label(info_frame, text=f"Argent: ${self.money}", font=("Segoe UI", 12, "bold"), bg=UI_COLOR, fg=INFO_TEXT_COLOR)
        self.money_label.pack(anchor="w")
        self.health_label = tk.Label(info_frame, text=f"Santé: {self.health}", font=("Segoe UI", 12, "bold"), bg=UI_COLOR, fg=INFO_TEXT_COLOR)
        self.health_label.pack(anchor="w")

        # Message en jeu
        self.message_label = tk.Label(self.control_panel, text="", font=("Segoe UI", 10, "italic"), bg=UI_COLOR, fg="#2ecc71", wraplength=230)
        self.message_label.pack(pady=5, padx=10)

        # --- Cadre de contrôle du jeu ---
        game_control_frame = tk.LabelFrame(self.control_panel, text="Contrôle", bg=UI_COLOR, fg=INFO_TEXT_COLOR, padx=10, pady=10)
        game_control_frame.pack(pady=10, padx=10, fill="x")

        self.next_wave_button = tk.Button(game_control_frame, text="Vague Suivante", font=("Segoe UI", 12, "bold"), command=self.spawn_wave, bg="#27ae60", fg="white", bd=0, relief="flat")
        self.next_wave_button.pack(pady=5, fill="x")

        speed_frame = tk.Frame(game_control_frame, bg=UI_COLOR)
        speed_frame.pack(pady=5)
        tk.Label(speed_frame, text="Vitesse:", bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack(side="left")
        for speed in [1, 2, 4]:
            tk.Button(speed_frame, text=f"x{speed}", command=lambda s=speed: self.set_game_speed(s), bg=BUTTON_COLOR, fg="white", bd=0, relief="flat", width=3).pack(side="left", padx=2)

        self.pause_button = tk.Button(game_control_frame, text="Pause", font=("Segoe UI", 12), command=self.toggle_pause, bg=BUTTON_COLOR, fg="white", bd=0, relief="flat")
        self.pause_button.pack(pady=5, fill="x")

        self.save_button = tk.Button(game_control_frame, text="Sauvegarder", font=("Segoe UI", 12), command=self.save_game, bg=BUTTON_COLOR, fg="white", bd=0, relief="flat")
        self.save_button.pack(pady=5, fill="x")

        # --- Cadre de construction ---
        build_frame = tk.LabelFrame(self.control_panel, text="Construire", bg=UI_COLOR, fg=INFO_TEXT_COLOR, padx=10, pady=10)
        build_frame.pack(pady=10, padx=10, fill="both", expand=True)

        tower_descriptions = {
            "Base": "Tour polyvalente standard.",
            "Fire": "Inflige des dégâts de zone.",
            "Ice": "Ralentit les ennemis.",
            "Air": "Cible uniquement les ennemis volants.",
            "Sniper": "Longue portée, dégâts élevés, chance de critique.",
            "Poison": "Empoisonne les ennemis, infligeant des dégâts sur la durée.",
            "Lightning": "Frappe plusieurs cibles à la fois."
        }

        for tower_type, cost in TOWER_COSTS.items():
            tower_button_frame = tk.Frame(build_frame, bg=UI_COLOR)
            tower_button_frame.pack(fill="x", pady=2)
            
            icon_canvas = tk.Canvas(tower_button_frame, width=20, height=20, bg=TOWER_COLORS[tower_type], highlightthickness=0)
            icon_canvas.pack(side="left", padx=5)
            
            btn = tk.Button(tower_button_frame, text=f"{tower_type} (${cost})", font=("Segoe UI", 11),
                            command=lambda t=tower_type: self.start_placing_tower(t), 
                            bg="#4a5568", fg="white", bd=0, relief="flat", anchor="w")
            btn.pack(side="left", fill="x", expand=True)
            Tooltip(btn, tower_descriptions.get(tower_type, "Aucune description."))

        # --- Cadre d'amélioration/vente ---
        self.upgrade_panel = tk.LabelFrame(self.control_panel, text="Tour sélectionnée", bg=UI_COLOR, fg=INFO_TEXT_COLOR, padx=10, pady=10)
        self.upgrade_panel.pack(pady=10, padx=10, fill="x")
        self.show_upgrade_panel()
        
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
                "Sniper": SniperTower, "Poison": PoisonTower, "Lightning": LightningTower
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

    def set_game_speed(self, speed):
        """
        Définit la vitesse du jeu.
        """
        self.game_speed = speed
        self.show_message(f"Vitesse du jeu réglée sur x{speed}", color="#3498db")

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
        
        # Amélioration de la génération pour des chemins plus sinueux
        while current != end_pos:
            r, c = current
            possible_moves = []
            
            # Priorise le mouvement vers le point de fin
            if c < end_pos[1] and (r, c + 1) not in self.path: possible_moves.append((r, c + 1))
            if r < end_pos[0] and (r + 1, c) not in self.path: possible_moves.append((r + 1, c))
            if r > end_pos[0] and (r - 1, c) not in self.path: possible_moves.append((r - 1, c))
            
            # Si aucune direction directe, essaye d'autres directions
            if not possible_moves:
                # Permet des mouvements "en arrière" pour créer des boucles
                all_directions = [(r, c + 1), (r + 1, c), (r - 1, c), (r, c - 1)]
                for move in all_directions:
                    mr, mc = move
                    if 0 <= mr < rows and 0 <= mc < cols and move not in self.path:
                        # Vérifie que le mouvement ne crée pas une impasse immédiate
                        neighbors_of_move = [(mr, mc+1), (mr+1, mc), (mr-1, mc), (mr, mc-1)]
                        if any(n not in self.path for n in neighbors_of_move if n != current):
                            possible_moves.append(move)
                
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
        elif tower_type == "Lightning":
            new_tower = LightningTower(self, self.canvas, grid_x, grid_y)
        
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

        clicked_tower = None
        for tower in self.towers: # Find the clicked tower
            if math.hypot(x - tower.x, y - tower.y) < 20:
                clicked_tower = tower
                break
        self.selected_tower = clicked_tower # Set selected tower

        self.show_upgrade_panel()

    def show_upgrade_panel(self):
        """
        Affiche le panneau d'amélioration pour la tour sélectionnée.
        """
        for widget in self.upgrade_panel.winfo_children():
            widget.destroy()
            
        if self.selected_tower:
            self.canvas.itemconfigure(self.selected_tower.range_circle, state=tk.NORMAL, dash=())
            
            tk.Label(self.upgrade_panel, text=f"Tour {self.selected_tower.type}", font=("Arial", 16, "bold"), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack(pady=5)
            tk.Label(self.upgrade_panel, text=f"Niveau: {self.selected_tower.level}", font=("Arial", 12), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack()
            tk.Label(self.upgrade_panel, text=f"Dégâts: {self.selected_tower.damage:.1f}", font=("Arial", 12), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack()
            tk.Label(self.upgrade_panel, text=f"Cadence de tir: {self.selected_tower.fire_rate:.2f}s", font=("Arial", 12), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack()
            tk.Label(self.upgrade_panel, text=f"Portée: {self.selected_tower.attack_range:.1f}", font=("Arial", 12), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack()
            tk.Label(self.upgrade_panel, text=f"Dégâts infligés: {self.selected_tower.damage_dealt:.0f}", font=("Arial", 10, "italic"), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack()
            tk.Label(self.upgrade_panel, text=f"Ennemis tués: {self.selected_tower.kills}", font=("Arial", 10, "italic"), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack()
            
            if self.selected_tower.level < 3:
                tk.Button(self.upgrade_panel, text=f"Améliorer Dégâts (${self.selected_tower.upgrade_damage_cost:.0f})", font=("Segoe UI", 11),
                          command=lambda: self.upgrade_tower(self.selected_tower, "damage"), 
                          bg=UPGRADE_BUTTON_COLOR, fg="white", bd=0, relief="flat").pack(pady=5, fill="x")

                tk.Button(self.upgrade_panel, text=f"Améliorer Cadence (${self.selected_tower.upgrade_rate_cost:.0f})", font=("Segoe UI", 11),
                          command=lambda: self.upgrade_tower(self.selected_tower, "rate"), 
                          bg=UPGRADE_BUTTON_COLOR, fg="white", bd=0, relief="flat").pack(pady=5, fill="x")

                tk.Button(self.upgrade_panel, text=f"Améliorer Portée (${self.selected_tower.upgrade_range_cost:.0f})", font=("Segoe UI", 11),
                          command=lambda: self.upgrade_tower(self.selected_tower, "range"), 
                          bg=UPGRADE_BUTTON_COLOR, fg="white", bd=0, relief="flat").pack(pady=5, fill="x")
            
            sell_price = int(self.selected_tower.get_sell_price())
            tk.Button(self.upgrade_panel, text=f"Vendre (${sell_price})", font=("Segoe UI", 11),
                      command=lambda: self.sell_tower(self.selected_tower), 
                      bg=SELL_BUTTON_COLOR, fg="white", bd=0, relief="flat").pack(pady=10, fill="x")

        else:
            for tower in self.towers:
                self.canvas.itemconfigure(tower.range_circle, state=tk.HIDDEN, dash=(5, 5))
            tk.Label(self.upgrade_panel, text="Cliquez sur une tour pour l'améliorer.", font=("Segoe UI", 11, "italic"), bg=UI_COLOR, fg=INFO_TEXT_COLOR).pack()
            
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
        self.wave_in_progress = True
        self.next_wave_button.config(state=tk.DISABLED, bg="#555")
        self.save_button.config(state=tk.DISABLED, bg="#555")
        
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
            enemy_types = [k for k in ENEMY_COLORS.keys() if k != "Boss"]
            if "Boss" in enemy_types: enemy_types.remove("Boss")
            for _ in range(num_enemies):
                self.enemy_spawn_queue.append(random.choice(enemy_types))
            
        random.shuffle(self.enemy_spawn_queue)

    def update_stats(self):
        """
        Met à jour les labels de l'interface utilisateur.
        """
        self.money_label.config(text=f"Argent: ${int(self.money)}")
        self.health_label.config(text=f"Santé: {self.health}")
        
    def game_loop(self):
        """
        Boucle de jeu principale.
        Gère la logique de jeu, les mises à jour et les rendus.
        """
        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now

        if not self.game_running:
            return # No need to call after if game is over

        if self.paused:
            self.master.after(20, self.game_loop)
            return

        # Applique la vitesse du jeu
        dt *= self.game_speed

        # Vérifie si le message est expiré
        if self.current_message and now > self.message_end_time:
            self.message_label.config(text="")

        # Gère les vagues
        if self.wave_in_progress and not self.enemies and not self.enemy_spawn_queue:
            self.wave_in_progress = False
            interest = int(self.money * self.interest_rate)
            self.money += interest
            self.show_message(f"Vague terminée ! +${interest} d'intérêts.", color="#2ecc71")
            self.update_stats()
            self.save_button.config(state=tk.NORMAL, bg=BUTTON_COLOR)
            self.next_wave_button.config(state=tk.NORMAL, bg="#27ae60")
        
        # Fait apparaître les ennemis de la file d'attente
        if self.enemy_spawn_queue and now - self.last_spawn_time > self.spawn_interval:
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
            elif enemy_type == "Armored":
                self.enemies.append(ArmoredEnemy(self, self.canvas, self.path_pixels, 1))
            elif enemy_type == "Healer":
                self.enemies.append(HealerEnemy(self, self.canvas, self.path_pixels, 1))
            self.last_spawn_time = now
        
        # Met à jour les effets
        active_effects = []
        for effect in self.effects:
            if effect.update(dt): # Passe dt aux effets
                active_effects.append(effect) # Garde l'effet s'il est toujours actif
        self.effects = active_effects

        # Met à jour les ennemis
        active_enemies = []
        for enemy in self.enemies:
            if enemy.update(dt):
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
            tower.update(self.enemies, dt)
        
        # Met à jour les projectiles
        active_projectiles = []
        for p in self.projectiles: # Passe dt aux projectiles
            if p.update(dt):
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

    def save_game(self):
        """Sauvegarde l'état actuel du jeu dans un fichier JSON."""
        if self.wave_in_progress:
            self.show_message("Impossible de sauvegarder pendant une vague.", color="#e74c3c")
            return

        game_state = {
            "wave_number": self.wave_number,
            "money": self.money,
            "health": self.health,
            "path": self.path,
            "towers": [tower.to_dict() for tower in self.towers]
        }

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Fichiers de sauvegarde Tower Defense", "*.json")],
            title="Sauvegarder la partie"
        )

        if not filepath:
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=4)
            self.show_message("Partie sauvegardée !", color="#2ecc71")
        except Exception as e:
            self.show_message(f"Erreur de sauvegarde: {e}", color="#e74c3c")
            messagebox.showerror("Erreur", f"Impossible de sauvegarder la partie:\n{e}")

    def load_game(self):
        """Charge un état de jeu à partir d'un fichier JSON."""
        self.paused = True
        filepath = filedialog.askopenfilename(
            filetypes=[("Fichiers de sauvegarde Tower Defense", "*.json")],
            title="Charger une partie"
        )
        if not filepath:
            self.paused = False
            return False

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                game_state = json.load(f)
        except Exception as e:
            self.show_message(f"Erreur de chargement: {e}", color="#e74c3c")
            messagebox.showerror("Erreur", f"Impossible de charger le fichier de sauvegarde:\n{e}")
            self.paused = False
            return False

        self._load_state(game_state)
        self.paused = False
        return True

    def _load_state(self, game_state):
        """Méthode interne pour appliquer l'état chargé."""
        self.canvas.delete("all")
        self.towers.clear()
        self.enemies.clear()
        self.projectiles.clear()
        self.effects.clear()
        self.enemy_spawn_queue.clear()
        self.selected_tower = None

        self.wave_number = game_state.get("wave_number", 0)
        self.money = game_state.get("money", 300)
        self.health = game_state.get("health", 100)
        self.path = game_state.get("path", [])
        
        if not self.path:
            self.generate_path()
        else:
            self.path_pixels = [(p[1] * GRID_SIZE + GRID_SIZE // 2, p[0] * GRID_SIZE + GRID_SIZE // 2) for p in self.path]
        self.draw_path()

        for tower_data in game_state.get("towers", []):
            self.create_tower_from_data(tower_data)

        self.update_stats()
        self.wave_label.config(text=f"Vague: {self.wave_number}")
        self.show_upgrade_panel()
        self.show_message("Partie chargée !", color="#2ecc71")

    def create_tower_from_data(self, data):
        tower_class_map = {"Base": BaseTower, "Fire": FireTower, "Ice": IceTower, "Air": AirTower, "Sniper": SniperTower, "Poison": PoisonTower, "Lightning": LightningTower}
        tower_class = tower_class_map.get(data.get('type'))
        if not tower_class: return
        new_tower = tower_class(self, self.canvas, data['grid_x'], data['grid_y'])
        for key, value in data.items():
            if hasattr(new_tower, key): setattr(new_tower, key, value)
        new_tower.canvas.coords(new_tower.range_circle, new_tower.x - new_tower.attack_range, new_tower.y - new_tower.attack_range, new_tower.x + new_tower.attack_range, new_tower.y + new_tower.attack_range)
        self.towers.append(new_tower)


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
        self.fire_rate = 1.0 # Secondes entre les tirs
        self.damage = 10
        self.last_shot_time = time.time()
        self.upgrade_damage_cost = 50
        self.upgrade_rate_cost = 50
        self.upgrade_range_cost = 50
        self.initial_cost = TOWER_COSTS[self.type]
        self.is_projectile_tower = True
        self.damage_dealt = 0
        self.kills = 0
        
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
        total_cost = self.initial_cost + (self.upgrade_damage_cost - 50) + (self.upgrade_rate_cost - 50) + (self.upgrade_range_cost - 50) # Simplifié pour l'exemple
        return total_cost * 0.75

    def update(self, enemies, dt):
        """
        Met à jour l'état de la tour (cible et tire).
        """
        target = self.find_target(enemies)
        if target and time.time() - self.last_shot_time > self.fire_rate:
            self.fire(target, dt)
            
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
        
    def fire(self, target, dt):
        """
        Tire un projectile sur la cible. (Méthode générique)
        """
        self.game.projectiles.append(Projectile(self.game, self.canvas, self.x, self.y, target, self.damage, PROJECTILE_COLORS[self.type]))
        self.last_shot_time = time.time()
            
    def upgrade_damage(self):
        self.damage *= 1.2
        self.upgrade_damage_cost *= 1.5
        self.level += 1
        self.show_level()

    def to_dict(self):
        return {
            'type': self.type,
            'grid_x': self.grid_x,
            'grid_y': self.grid_y,
            'level': self.level,
            'damage': self.damage,
            'fire_rate': self.fire_rate,
            'attack_range': self.attack_range,
            'upgrade_damage_cost': self.upgrade_damage_cost,
            'upgrade_rate_cost': self.upgrade_rate_cost,
            'upgrade_range_cost': self.upgrade_range_cost,
            'damage_dealt': self.damage_dealt,
            'kills': self.kills,
        }
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
        
# --- Tours Spécialisées ---
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
        self.splash_radius = 30
        self.splash_damage_factor = 0.3
        self.canvas.itemconfigure(self.entity, fill=TOWER_COLORS[self.type])
        self.canvas.itemconfigure(self.range_circle, outline=TOWER_COLORS[self.type])

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'splash_radius': self.splash_radius,
            'splash_damage_factor': self.splash_damage_factor,
        })
        return data
        
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
        
    def fire(self, target, dt):
        self.game.projectiles.append(IceProjectile(self.game, self.canvas, self.x, self.y, target, self.damage, PROJECTILE_COLORS[self.type], self.slow_factor, self.slow_duration))
        self.last_shot_time = time.time()

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'slow_factor': self.slow_factor,
            'slow_duration': self.slow_duration,
        })
        return data
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
        self.crit_chance = 0.15
        self.crit_multiplier = 2.5
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

    def fire(self, target, dt):
        damage = self.damage
        if random.random() < self.crit_chance:
            damage *= self.crit_multiplier
        self.game.projectiles.append(Projectile(self.game, self.canvas, self.x, self.y, target, damage, PROJECTILE_COLORS[self.type]))
        self.last_shot_time = time.time()

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'crit_chance': self.crit_chance,
            'crit_multiplier': self.crit_multiplier,
        })
        return data
        
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
        
    def fire(self, target, dt):
        self.game.projectiles.append(PoisonProjectile(self.game, self.canvas, self.x, self.y, target, self.damage, PROJECTILE_COLORS[self.type]))
        self.last_shot_time = time.time()
class LightningTower(BaseTower):
    initial_range = 130

    def __init__(self, game, canvas, grid_x, grid_y):
        super().__init__(game, canvas, grid_x, grid_y)
        self.type = "Lightning"
        self.attack_range = self.initial_range
        self.fire_rate = 1.2
        self.damage = 20
        self.chain_targets = 3
        self.chain_radius = 80
        self.chain_damage_falloff = 0.7
        self.initial_cost = TOWER_COSTS[self.type]
        self.upgrade_damage_cost = 120
        self.upgrade_rate_cost = 120
        self.upgrade_range_cost = 120
        self.canvas.itemconfigure(self.entity, fill=TOWER_COLORS[self.type])
        self.canvas.itemconfigure(self.range_circle, outline=TOWER_COLORS[self.type])

    def fire(self, target, dt):
        # La logique de tir est gérée dans update pour cette tour
        pass

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'chain_targets': self.chain_targets,
            'chain_radius': self.chain_radius,
            'chain_damage_falloff': self.chain_damage_falloff,
        })
        return data

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
        self.base_speed = 40.0 # Vitesse en pixels/seconde
        self.speed = self.base_speed
        self.max_health = 20 * health_multiplier
        self.health = self.max_health
        self.alive = True
        self.color = ENEMY_COLORS["Base"]
        self.is_flying = False
        self.is_ghost = False
        self.effects = {}
        self.draw()

    def draw(self):
        """
        Dessine l'ennemi et sa barre de vie.
        """
        self.entity = self.canvas.create_rectangle(self.x - 8, self.y - 8, self.x + 8, self.y + 8, fill=self.color, outline="")
        self.health_bar = self.canvas.create_rectangle(self.x - 10, self.y - 12, self.x + 10, self.y - 10, fill=HEALTH_BAR_COLOR_FULL, outline="")

    def update(self, dt):
        """
        Met à jour la position de l'ennemi.
        Retourne True si l'ennemi a atteint la fin du chemin.
        """
        if not self.alive:
            return False

        # Applique les effets de statut
        current_speed = self.speed
        if 'slow' in self.effects:
            current_speed *= self.effects['slow']['factor']

        if self.path_index < len(self.path_pixels):
            target_x, target_y = self.path_pixels[self.path_index]
            
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)
            
            if dist < current_speed * dt: # Mouvement basé sur dt
                self.x, self.y = target_x, target_y
                self.path_index += 1
            else:
                self.x += (dx / dist) * current_speed * dt
                self.y += (dy / dist) * current_speed * dt
            
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
        fill_color = HEALTH_BAR_COLOR_CRIT if self.health < self.max_health * 0.3 else (HEALTH_BAR_COLOR_LOW if self.health < self.max_health * 0.6 else HEALTH_BAR_COLOR_FULL)
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
        self.effects['slow'] = {'factor': factor, 'end_time': time.time() + duration / 1000}
        
    def reset_speed(self):
        self.speed = self.base_speed
class FastEnemy(Enemy):
    def __init__(self, game, canvas, path_pixels, health_multiplier):
        super().__init__(game, canvas, path_pixels, health_multiplier)
        self.base_speed = 75.0
        self.speed = self.base_speed
        self.max_health = 15 * health_multiplier
        self.health = self.max_health # Santé réduite
        self.color = ENEMY_COLORS["Fast"]
        self.canvas.itemconfigure(self.entity, fill=self.color, width=1)
        self.canvas.coords(self.entity, self.x - 6, self.y - 6, self.x + 6, self.y + 6)
        
class TankEnemy(Enemy):
    def __init__(self, game, canvas, path_pixels, health_multiplier):
        super().__init__(game, canvas, path_pixels, health_multiplier)
        self.base_speed = 25.0
        self.speed = self.base_speed
        self.max_health = 50 * health_multiplier # Santé augmentée
        self.health = self.max_health
        self.color = ENEMY_COLORS["Tank"]
        self.canvas.itemconfigure(self.entity, fill=self.color, width=1)
        self.canvas.coords(self.entity, self.x - 10, self.y - 10, self.x + 10, self.y + 10)

class FlyingEnemy(Enemy):
    def __init__(self, game, canvas, path_pixels, health_multiplier):
        super().__init__(game, canvas, path_pixels, health_multiplier)
        self.is_flying = True
        self.base_speed = 60.0
        self.speed = self.base_speed
        self.max_health = 25 * health_multiplier # Santé moyenne
        self.health = self.max_health
        self.color = ENEMY_COLORS["Flying"]
        self.canvas.delete(self.entity)
        self.entity = self.canvas.create_oval(self.x-8, self.y-8, self.x+8, self.y+8, fill=self.color, outline="")
        self.canvas.delete(self.health_bar)
        self.health_bar = self.canvas.create_rectangle(self.x - 10, self.y - 12, self.x + 10, self.y - 10, fill=HEALTH_BAR_COLOR_FULL, outline="")

class BossEnemy(Enemy):
    def __init__(self, game, canvas, path_pixels, health_multiplier):
        super().__init__(game, canvas, path_pixels, health_multiplier)
        self.base_speed = 20.0
        self.speed = self.base_speed
        self.max_health = 500 * health_multiplier # Très haute santé
        self.health = self.max_health
        self.color = ENEMY_COLORS["Boss"]
        self.canvas.itemconfigure(self.entity, fill=self.color, width=1)
        self.canvas.coords(self.entity, self.x - 15, self.y - 15, self.x + 15, self.y + 15)

class GhostEnemy(Enemy):
    def __init__(self, game, canvas, path_pixels, health_multiplier):
        super().__init__(game, canvas, path_pixels, health_multiplier)
        self.base_speed = 50.0
        self.speed = self.base_speed
        self.max_health = 20 * health_multiplier # Santé normale
        self.health = self.max_health
        self.color = ENEMY_COLORS["Ghost"]
        self.is_ghost = True
        self.canvas.itemconfigure(self.entity, fill=self.color, outline=self.color, stipple="gray50")

class ArmoredEnemy(Enemy):
    def __init__(self, game, canvas, path_pixels, health_multiplier):
        super().__init__(game, canvas, path_pixels, health_multiplier)
        self.base_speed = 30.0
        self.speed = self.base_speed
        self.max_health = 80 * health_multiplier # Haute santé
        self.health = self.max_health
        self.color = ENEMY_COLORS["Armored"]
        self.damage_reduction = 0.3 # 30% de réduction de dégâts
        self.canvas.itemconfigure(self.entity, fill=self.color, outline="white", width=2)

    def take_damage(self, damage):
        super().take_damage(damage * (1 - self.damage_reduction))

class HealerEnemy(Enemy):
    def __init__(self, game, canvas, path_pixels, health_multiplier):
        super().__init__(game, canvas, path_pixels, health_multiplier)
        self.base_speed = 45.0
        self.speed = self.base_speed
        self.max_health = 40 * health_multiplier # Santé moyenne
        self.health = self.max_health
        self.color = ENEMY_COLORS["Healer"]
        self.heal_radius = 60
        self.heal_amount = 5
        self.heal_cooldown = 2.0
        self.last_heal_time = time.time()
        self.canvas.itemconfigure(self.entity, fill=self.color)

    def update(self, dt):
        """
        Met à jour la position de l'ennemi et gère le soin.
        """
        if super().update(dt):
            return True # L'ennemi a atteint la fin

        if time.time() - self.last_heal_time > self.heal_cooldown:
            for enemy in self.game.enemies:
                if enemy.is_alive() and enemy != self:
                    dist = math.hypot(self.x - enemy.x, self.y - enemy.y)
                    if dist < self.heal_radius:
                        enemy.health = min(enemy.max_health, enemy.health + self.heal_amount)
                        enemy.update_health_bar()
            self.last_heal_time = time.time()
        return False

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
        self.speed = 300 # Vitesse en pixels/seconde
        self.damage = damage
        self.active = True
        
        self.entity = self.canvas.create_oval(self.x - 3, self.y - 3, self.x + 3, self.y + 3, fill=color, outline="")

    def update(self, dt):
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

        if dist < self.speed * dt: # Utilise dt pour le calcul de la vitesse
            self.target.take_damage(self.damage)
            self.on_impact()
            self.destroy()
            return False
        else:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt
            self.canvas.coords(self.entity, self.x - 3, self.y - 3, self.x + 3, self.y + 3) # Met à jour la position visuelle
            return True

    def on_impact(self):
        pass # Peut être surchargé par les sous-classes

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
        
    def on_impact(self):
        if self.target.is_alive(): # S'assure que la cible est toujours vivante
            self.target.slow(self.slow_factor, self.slow_duration)

class PoisonProjectile(Projectile):
    def __init__(self, game, canvas, x, y, target, damage, color):
        super().__init__(game, canvas, x, y, target, damage, color)

    def on_impact(self):
        if self.target.is_alive():
            self.game.effects.append(PoisonEffect(self.target, self.damage, 3000))

class FireProjectile(Projectile):
    def __init__(self, game, canvas, x, y, target, damage, color, splash_radius, splash_damage_factor):
        super().__init__(game, canvas, x, y, target, damage, color)
        self.splash_radius = splash_radius
        self.splash_damage_factor = splash_damage_factor

    def on_impact(self):
        # Crée un effet visuel d'explosion
        self.game.effects.append(SplashEffect(self.canvas, self.target.x, self.target.y, self.splash_radius))
        # Inflige des dégâts aux ennemis dans le rayon d'explosion
        for enemy in self.game.enemies:
            if enemy.is_alive() and enemy != self.target:
                dist = math.hypot(self.target.x - enemy.x, self.target.y - enemy.y)
                if dist < self.splash_radius:
                    enemy.take_damage(self.damage * self.splash_damage_factor)

# --- Effets de Statut ---
class SplashEffect:
    def __init__(self, canvas, x, y, radius):
        self.canvas = canvas
        self.x, self.y, self.radius = x, y, radius
        self.duration = 0.2
        self.start_time = time.time()
        self.oval = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="", outline="orange", width=2)

    def update(self, dt):
        if time.time() - self.start_time > self.duration:
            self.canvas.delete(self.oval)
            return False
        return True

class PoisonEffect:
    """
    Effet de poison qui inflige des dégâts sur la durée.
    """
    def __init__(self, target, damage, duration):
        self.target = target
        self.damage = damage
        self.duration = duration
        self.start_time = time.time()
        self.last_tick = time.time()
        self.tick_interval = 0.5
        self.total_damage_dealt = 0
        
    def update(self, dt):
        if time.time() - self.start_time > (self.duration/1000): # Vérifie si l'effet est terminé
            return False
            
        if time.time() - self.last_tick > self.tick_interval: # Applique les dégâts périodiquement
            self.target.take_damage(self.damage * self.tick_interval) # Dégâts par tick
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
        
        title_label = tk.Label(self.current_frame, text="Tower Defense", font=("Segoe UI", 48, "bold"), bg=BACKGROUND_COLOR, fg=INFO_TEXT_COLOR)
        title_label.pack(pady=50)

        play_button = tk.Button(self.current_frame, text="Nouvelle Partie", font=("Segoe UI", 20), command=self.start_game, bg=BUTTON_COLOR, fg="white", bd=0, relief="flat", width=15, pady=10)
        play_button.pack(pady=20)
        
        load_button = tk.Button(self.current_frame, text="Charger une Partie", font=("Segoe UI", 20), command=self.load_game_from_menu, bg=UPGRADE_BUTTON_COLOR, fg="white", bd=0, relief="flat", width=15, pady=10)
        load_button.pack(pady=10)
        
        tk.Label(self.current_frame, text="Défendez votre base contre des vagues d'ennemis.", font=("Segoe UI", 12), bg=BACKGROUND_COLOR, fg=INFO_TEXT_COLOR).pack(pady=5)
        tk.Label(self.current_frame, text="Construisez et améliorez des tours pour survivre le plus longtemps possible.", font=("Segoe UI", 12), bg=BACKGROUND_COLOR, fg=INFO_TEXT_COLOR).pack(pady=5)

    def load_game_from_menu(self):
        """Crée une instance de jeu et charge une sauvegarde."""
        if self.current_frame:
            self.current_frame.destroy()
        game_frame = TowerDefenseGame(self)
        self.current_frame = game_frame
        if not game_frame.load_game():
            # Le chargement a été annulé, retour au menu principal
            self.show_main_menu()

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
