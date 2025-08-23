import tkinter as tk
import random
import time

class CrossyChicken:
    """
    Une version complète du jeu Crossy Chicken, avec des graphismes pro,
    un défilement fluide et des fonctionnalités avancées.
    Cette version a été entièrement reconstruite pour corriger tous les bugs majeurs.
    """
    def __init__(self, master):
        self.master = master
        self.master.title("Crossy Chicken Pro")
        
        # Dimensions de la fenêtre
        self.WINDOW_WIDTH = 1000
        self.WINDOW_HEIGHT = 800
        self.master.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.master.resizable(False, False)
        self.master.configure(bg="#1e1e1e")

        # Variables d'état du jeu
        self.is_game_active = False
        self.score = 0
        self.high_score = 0
        self.lanes = []
        self.animation_id = None
        
        # Position du joueur sur la grille logique (commence en bas et se dirige vers 0)
        self.player_x = self.WINDOW_WIDTH // 2
        self.player_y_logical = 1000
        self.player_size = 30
        
        # Le joueur est dessiné à une position fixe sur l'écran pour l'effet de caméra
        self.player_y_visual = self.WINDOW_HEIGHT - 150
        
        # Position de la "caméra" virtuelle pour le défilement
        self.camera_y = self.player_y_logical
        self.target_camera_y = self.player_y_logical
        self.last_move_time = 0

        # Références aux widgets pour pouvoir les manipuler
        self.canvas = None
        self.score_label = None
        self.message_box = None
        self.game_over_frame = None

        self.setup_main_menu()

    def clear_frame(self):
        """Détruit tous les widgets enfants de la fenêtre principale."""
        for widget in self.master.winfo_children():
            widget.destroy()

    def setup_main_menu(self):
        """Crée l'interface du menu principal avec un style moderne."""
        self.clear_frame()
        self.is_game_active = False
        
        main_frame = tk.Frame(self.master, bg="#2c3e50")
        main_frame.pack(expand=True, fill="both")
        
        title_label = tk.Label(main_frame, text="CROSSY CHICKEN", font=("Arial", 60, "bold"), bg="#2c3e50", fg="#ecf0f1")
        title_label.pack(pady=(100, 20))
        
        high_score_label = tk.Label(main_frame, text=f"Meilleur score : {self.high_score}", font=("Arial", 28), bg="#2c3e50", fg="#f1c40f")
        high_score_label.pack(pady=(0, 30))
        
        subtitle_label = tk.Label(main_frame, text="Traversez la route et la rivière !", font=("Arial", 20, "italic"), bg="#2c3e50", fg="#bdc3c7")
        subtitle_label.pack(pady=(0, 60))
        
        start_button = tk.Button(main_frame, text="Démarrer le jeu", font=("Arial", 24, "bold"), bg="#27ae60", fg="#ecf0f1", bd=0, relief=tk.FLAT, highlightthickness=0, width=25, pady=20, command=self.start_game)
        start_button.pack(pady=20)
        start_button.bind("<Enter>", lambda e: start_button.config(bg="#2ecc71"))
        start_button.bind("<Leave>", lambda e: start_button.config(bg="#27ae60"))
        
        self.master.bind("<Return>", lambda event: self.start_game())

    def start_game(self):
        """Initialise le jeu avec le canevas et les objets."""
        self.clear_frame()
        self.is_game_active = True
        self.score = 0
        self.lanes = []
        # Le joueur commence en bas et se dirige vers le haut
        self.player_x = self.WINDOW_WIDTH // 2
        self.player_y_logical = 1000
        self.camera_y = self.player_y_logical
        self.target_camera_y = self.player_y_logical
        
        self.canvas = tk.Canvas(self.master, width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT, bg="#2c3e50", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.score_label = tk.Label(self.master, text="Score: 0", font=("Arial", 28, "bold"), bg="#2c3e50", fg="#ecf0f1")
        self.score_label.place(relx=0.5, y=30, anchor=tk.N)
        
        self.message_box = tk.Label(self.master, text="", font=("Arial", 20), bg="#2c3e50", fg="#c0392b")
        self.message_box.place(relx=0.5, y=70, anchor=tk.N)

        self.generate_initial_lanes()
        
        # Liaison des touches du clavier
        self.master.bind("<Up>", self.move_player)
        self.master.bind("<Left>", self.move_player)
        self.master.bind("<Right>", self.move_player)
        self.master.bind("<Down>", self.move_player)
        self.master.bind("z", self.move_player)
        self.master.bind("q", self.move_player)
        self.master.bind("s", self.move_player)
        self.master.bind("d", self.move_player)

        self.animate()

    def generate_initial_lanes(self):
        """Génère les voies initiales du jeu."""
        # Crée une voie de départ sûre en bas de la zone de jeu
        self.lanes.append({"type": "safe", "y_logical": 1000, "objects": []})
        
        # Génère des voies aléatoires vers le haut
        for i in range(1, 30):
            lane_type = random.choice(["road", "road", "road", "water", "safe", "safe", "safe", "train_track"])
            lane = {"type": lane_type, "y_logical": 1000 - i * 50, "objects": []}
            
            if lane_type in ["road", "water", "train_track"]:
                lane["direction"] = random.choice([-1, 1])
                lane["speed"] = random.choice([2, 3, 4])
                if lane_type == "train_track":
                    lane["speed"] = 15
                lane["objects"] = self.generate_lane_objects(lane_type, lane["direction"])
            
            self.lanes.append(lane)

    def generate_lane_objects(self, lane_type, direction):
        """
        Génère des objets pour une voie sans chevauchement.
        """
        objects = []
        
        if lane_type == "train_track":
            # Crée un seul objet train très long
            train_width = random.randint(500, 800)
            train_x = -train_width if direction == 1 else self.WINDOW_WIDTH
            objects.append({"x": train_x, "width": train_width, "height": 30})
            return objects
        
        current_x = -self.WINDOW_WIDTH // 2  # Commence la génération hors de l'écran
        
        while current_x < self.WINDOW_WIDTH + self.WINDOW_WIDTH // 2:
            space_between = random.randint(150, 300)
            obj_width = random.randint(80, 200)
            
            new_x = current_x + space_between
            
            objects.append({"x": new_x, "width": obj_width, "height": 30})
            
            current_x = new_x + obj_width
        
        return objects

    def draw_lane(self, y, lane_type):
        """Dessine une voie isométrique avec des détails visuels."""
        if lane_type == "road":
            color = "#34495e"
            self.canvas.create_rectangle(0, y, self.WINDOW_WIDTH, y + 50, fill=color, outline="", tags="lane")
            for i in range(int(self.WINDOW_WIDTH / 50)):
                self.canvas.create_rectangle(i * 50, y + 22, i * 50 + 30, y + 28, fill="#ffffff", outline="")
        elif lane_type == "water":
            color = "#2c7bb1"
            self.canvas.create_rectangle(0, y, self.WINDOW_WIDTH, y + 50, fill=color, outline="", tags="lane")
        elif lane_type == "train_track":
            color = "#555555"
            self.canvas.create_rectangle(0, y, self.WINDOW_WIDTH, y + 50, fill=color, outline="", tags="lane")
            # Rails
            self.canvas.create_rectangle(0, y + 15, self.WINDOW_WIDTH, y + 20, fill="#333333", outline="")
            self.canvas.create_rectangle(0, y + 30, self.WINDOW_WIDTH, y + 35, fill="#333333", outline="")
        else: # safe (herbe)
            color = "#2ecc71"
            self.canvas.create_rectangle(0, y, self.WINDOW_WIDTH, y + 50, fill=color, outline="", tags="lane")
            
    def draw_car(self, x, y, width, height):
        """Dessine une voiture isométrique stylisée avec un effet 3D."""
        color = "#e74c3c"
        darker_color = "#c0392b"
        iso_depth = 10

        self.canvas.create_rectangle(x, y, x + width, y + height, fill=color, outline="#2c3e50", width=2)
        
        self.canvas.create_polygon(
            x, y,
            x + width, y,
            x + width + iso_depth, y - iso_depth,
            x + iso_depth, y - iso_depth,
            fill="#ff6b6b", outline="#e74c3c", width=2
        )
        self.canvas.create_polygon(
            x + width, y,
            x + width, y + height,
            x + width + iso_depth, y + height - iso_depth,
            x + width + iso_depth, y - iso_depth,
            fill=darker_color, outline="#2c3e50", width=2
        )
        
    def draw_log(self, x, y, width, height):
        """Dessine un tronc d'arbre isométrique."""
        color = "#7f5d47"
        darker_color = "#5c412f"
        iso_depth = 10
        
        self.canvas.create_rectangle(x, y, x + width, y + height, fill=color, outline="#2c3e50", width=2)
        
        self.canvas.create_polygon(
            x, y,
            x + width, y,
            x + width + iso_depth, y - iso_depth,
            x + iso_depth, y - iso_depth,
            fill="#a08064", outline="#7f5d47", width=2
        )
        self.canvas.create_polygon(
            x + width, y,
            x + width, y + height,
            x + width + iso_depth, y + height - iso_depth,
            x + width + iso_depth, y - iso_depth,
            fill=darker_color, outline="#2c3e50", width=2
        )

    def draw_train(self, x, y, width, height):
        """Dessine un train isométrique."""
        color = "#c0392b"
        darker_color = "#a93226"
        iso_depth = 10

        self.canvas.create_rectangle(x, y, x + width, y + height, fill=color, outline="#8c2e24", width=2)
        
        self.canvas.create_polygon(
            x, y,
            x + width, y,
            x + width + iso_depth, y - iso_depth,
            x + iso_depth, y - iso_depth,
            fill="#e74c3c", outline="#c0392b", width=2
        )
        self.canvas.create_polygon(
            x + width, y,
            x + width, y + height,
            x + width + iso_depth, y + height - iso_depth,
            x + width + iso_depth, y - iso_depth,
            fill=darker_color, outline="#8c2e24", width=2
        )
        # Fenêtre du conducteur
        self.canvas.create_rectangle(x + 15, y + 10, x + 40, y + 25, fill="#95a5a6", outline="#7f8c8d")

    def draw_chicken(self, x, y, size):
        """Dessine le personnage de poulet avec plus de détails."""
        # Corps
        self.canvas.create_oval(x - size/2, y - size/2, x + size/2, y + size/2, fill="#f9e79f", outline="#f1c40f", width=2)
        # Tête
        self.canvas.create_oval(x - size/4, y - size, x + size/4, y - size/2, fill="#f9e79f", outline="#f1c40f", width=2)
        # Yeux
        self.canvas.create_oval(x - size/6, y - size*0.8, x - size/10, y - size*0.7, fill="black")
        self.canvas.create_oval(x + size/10, y - size*0.8, x + size/6, y - size*0.7, fill="black")
        # Bec
        self.canvas.create_polygon(x, y - size/2, x - size/8, y - size/4, x + size/8, y - size/4, fill="#e67e22", outline="#d35400", width=2)
        # Pattes
        self.canvas.create_line(x - size/6, y + size/2, x - size/6, y + size/2 + 5, fill="#e67e22", width=2)
        self.canvas.create_line(x + size/6, y + size/2, x + size/6, y + size/2 + 5, fill="#e67e22", width=2)

    def move_player(self, event):
        """Déplace le joueur et met à jour le score."""
        if not self.is_game_active:
            return

        current_time = time.time()
        # Empêche les mouvements trop rapides
        if current_time - self.last_move_time < 0.1:
            return
        self.last_move_time = current_time

        if event.keysym in ["Left", "q"]:
            # Empêche le joueur de sortir de l'écran à gauche
            self.player_x = max(self.player_size / 2, self.player_x - 50)
        elif event.keysym in ["Right", "d"]:
            # Empêche le joueur de sortir de l'écran à droite
            self.player_x = min(self.WINDOW_WIDTH - self.player_size / 2, self.player_x + 50)
        elif event.keysym in ["Up", "z"]:
            # Le joueur se déplace vers le haut (vers 0)
            self.player_y_logical -= 50
            self.score = (1000 - self.player_y_logical) // 50
            self.score_label.config(text=f"Score: {self.score}")
            self.target_camera_y = self.player_y_logical
        elif event.keysym in ["Down", "s"] and self.player_y_logical < 1000:
            # Le joueur se déplace vers le bas (vers 1000)
            self.player_y_logical += 50
            self.target_camera_y = self.player_y_logical
            
    def animate(self):
        """Boucle principale du jeu pour le défilement et la mise à jour."""
        if not self.is_game_active:
            return

        self.canvas.delete("all")
        
        # Mouvement de la caméra avec un effet d'inertie
        self.camera_y += (self.target_camera_y - self.camera_y) * 0.1

        # Déplacement des objets sur les voies
        for lane in self.lanes:
            if lane["type"] in ["road", "water", "train_track"]:
                for obj in lane["objects"]:
                    obj["x"] += lane["speed"] * lane["direction"]
                    # Gère le bouclage des objets à travers l'écran
                    if lane["direction"] == 1 and obj["x"] > self.WINDOW_WIDTH + 200:
                        obj["x"] = -obj["width"] - random.randint(100, 300)
                    elif lane["direction"] == -1 and obj["x"] < -200:
                        obj["x"] = self.WINDOW_WIDTH + random.randint(100, 300)
        
        # Suppression des voies hors écran et ajout de nouvelles (rend le jeu infini)
        if len(self.lanes) > 0 and self.lanes[-1]["y_logical"] > self.player_y_logical + self.WINDOW_HEIGHT + 100:
            self.lanes.pop(-1)
            
        if len(self.lanes) > 0 and self.lanes[0]["y_logical"] < self.player_y_logical - self.WINDOW_HEIGHT - 100:
            lane_type = random.choice(["road", "road", "road", "water", "safe", "safe", "safe", "train_track"])
            new_lane = {"type": lane_type, "y_logical": self.lanes[0]["y_logical"] - 50, "objects": []}
            
            if new_lane["type"] in ["road", "water", "train_track"]:
                new_lane["direction"] = random.choice([-1, 1])
                new_lane["speed"] = random.choice([2, 3, 4])
                if new_lane["type"] == "train_track":
                    new_lane["speed"] = 15
                new_lane["objects"] = self.generate_lane_objects(new_lane["type"], new_lane["direction"])
            
            self.lanes.insert(0, new_lane)

        # Dessin de toutes les voies et de leurs objets
        for lane in self.lanes:
            y_visual = self.player_y_visual + (self.player_y_logical - self.camera_y) + (self.camera_y - lane["y_logical"])
            if -50 <= y_visual <= self.WINDOW_HEIGHT + 50:
                self.draw_lane(y_visual, lane["type"])
                for obj in lane["objects"]:
                    if lane["type"] == "road":
                        self.draw_car(obj["x"], y_visual, obj["width"], obj["height"])
                    elif lane["type"] == "water":
                        self.draw_log(obj["x"], y_visual, obj["width"], obj["height"])
                    elif lane["type"] == "train_track":
                        self.draw_train(obj["x"], y_visual, obj["width"], obj["height"])

        # Dessin du poulet à sa position visuelle fixe
        self.draw_chicken(self.player_x, self.player_y_visual, self.player_size)
        
        # Vérification des collisions
        self.check_collisions()

        self.animation_id = self.master.after(20, self.animate)

    def check_collisions(self):
        """
        Vérifie les collisions avec les obstacles.
        Logique de collision reconstruite pour plus de fiabilité.
        """
        current_lane = None
        # Trouve la bonne voie en fonction de la position Y logique du joueur
        for lane in self.lanes:
            # Vérifie si la position du joueur est à l'intérieur de la voie
            if self.player_y_logical == lane["y_logical"]:
                current_lane = lane
                break

        # S'il n'y a pas de voie correspondante, il y a un problème de logique
        if current_lane is None:
            self.game_over("PERDU ! Le jeu a rencontré une erreur.")
            return

        # Vérifie si le joueur est sur un danger (route ou train)
        if current_lane["type"] in ["road", "train_track"]:
            player_left = self.player_x - self.player_size / 2
            player_right = self.player_x + self.player_size / 2
            
            for obj in current_lane["objects"]:
                obj_left = obj["x"]
                obj_right = obj["x"] + obj["width"]
                
                # Collision check
                if player_right > obj_left and player_left < obj_right:
                    self.game_over("PERDU ! Vous avez été écrasé.")
                    return

        # Vérifie si le joueur est sur l'eau
        elif current_lane["type"] == "water":
            on_log = False
            player_left = self.player_x - self.player_size / 2
            player_right = self.player_x + self.player_size / 2
            
            for obj in current_lane["objects"]:
                log_left = obj["x"]
                log_right = obj["x"] + obj["width"]
                
                if player_right > log_left and player_left < log_right:
                    on_log = True
                    # Le joueur est porté par le tronc d'arbre
                    self.player_x += current_lane["speed"] * current_lane["direction"]
                    break
            
            if not on_log:
                self.game_over("PERDU ! Vous êtes tombé à l'eau.")
                return

    def game_over(self, message):
        """Arrête le jeu et affiche l'écran de fin de partie."""
        self.is_game_active = False
        if self.animation_id:
            self.master.after_cancel(self.animation_id)
        
        # Met à jour le meilleur score
        if self.score > self.high_score:
            self.high_score = self.score
            
        # Délie les événements du clavier
        self.master.unbind("<Up>")
        self.master.unbind("<Down>")
        self.master.unbind("<Left>")
        self.master.unbind("<Right>")
        self.master.unbind("z")
        self.master.unbind("q")
        self.master.unbind("s")
        self.master.unbind("d")

        # Détruit l'ancien écran de fin de partie s'il existe
        if self.game_over_frame:
            self.game_over_frame.destroy()
            
        self.game_over_frame = tk.Frame(self.master, bg="#2c3e50")
        self.game_over_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=600, height=400)
        
        tk.Label(self.game_over_frame, text="GAME OVER", font=("Arial", 40, "bold"), bg="#2c3e50", fg="#e74c3c").pack(pady=(30, 15))
        tk.Label(self.game_over_frame, text=message, font=("Arial", 20), bg="#2c3e50", fg="white").pack(pady=10)
        
        final_score_label = tk.Label(self.game_over_frame, text=f"Votre score final : {self.score}", font=("Arial", 24), bg="#2c3e50", fg="#f1c40f")
        final_score_label.pack(pady=10)
        
        high_score_label = tk.Label(self.game_over_frame, text=f"Meilleur score : {self.high_score}", font=("Arial", 20), bg="#2c3e50", fg="#f1c40f")
        high_score_label.pack(pady=10)
        
        if self.score >= self.high_score:
            tk.Label(self.game_over_frame, text="Nouveau record !", font=("Arial", 18, "italic"), bg="#2c3e50", fg="#2ecc71").pack(pady=10)
            
        choice_frame = tk.Frame(self.game_over_frame, bg="#2c3e50")
        choice_frame.pack(pady=30)
        
        restart_button = tk.Button(choice_frame, text="Recommencer", font=("Arial", 16, "bold"), bg="#27ae60", fg="white", width=18, bd=0, relief=tk.FLAT, command=self.restart_game)
        restart_button.pack(side=tk.LEFT, padx=15)
        restart_button.bind("<Enter>", lambda e: restart_button.config(bg="#2ecc71"))
        restart_button.bind("<Leave>", lambda e: restart_button.config(bg="#27ae60"))
        
        menu_button = tk.Button(choice_frame, text="Retour au menu", font=("Arial", 16, "bold"), bg="#3498db", fg="white", width=18, bd=0, relief=tk.FLAT, command=self.go_to_main_menu)
        menu_button.pack(side=tk.LEFT, padx=15)
        menu_button.bind("<Enter>", lambda e: menu_button.config(bg="#3daee9"))
        menu_button.bind("<Leave>", lambda e: menu_button.config(bg="#3498db"))

    def restart_game(self):
        """Relance une nouvelle partie."""
        self.game_over_frame.destroy()
        self.start_game()
        
    def go_to_main_menu(self):
        """Retourne au menu principal."""
        self.game_over_frame.destroy()
        self.setup_main_menu()

# Point d'entrée de l'application
if __name__ == "__main__":
    root = tk.Tk()
    game = CrossyChicken(root)
    root.mainloop()
