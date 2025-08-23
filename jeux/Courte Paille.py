import tkinter as tk
from tkinter import messagebox
import random

class ShortStrawGame:
    """
    Implémente le jeu de Courte Paille avec une interface graphique moderne et des effets visuels.
    """
    def __init__(self, master):
        self.master = master
        self.master.title("Courte Paille")
        self.master.geometry("900x650")
        self.master.resizable(False, False)
        self.master.configure(bg="#1c2833") # Fond très sombre

        self.players = []
        self.straws = []
        self.current_player_index = 0
        self.game_mode = None
        self.straw_widgets = []
        self.is_game_active = False
        self.is_ai_turn = False  # Ajout d'un drapeau pour gérer le tour de l'IA

        self.setup_main_menu()

    def clear_frame(self):
        """Efface tous les widgets de la fenêtre pour changer d'écran."""
        for widget in self.master.winfo_children():
            widget.destroy()

    def setup_main_menu(self):
        """Crée l'interface du menu principal pour choisir le mode de jeu."""
        self.clear_frame()
        self.is_game_active = False
        
        main_frame = tk.Frame(self.master, bg="#1c2833")
        main_frame.pack(expand=True)

        tk.Label(main_frame, text="COURTE PAILLE", font=("Helvetica", 48, "bold"), bg="#1c2833", fg="#ecf0f1").pack(pady=(20, 5))
        tk.Label(main_frame, text="Qui tirera la paille la plus courte ?", font=("Helvetica", 16, "italic"), bg="#1c2833", fg="#bdc3c7").pack(pady=(0, 50))

        button_style = {
            "font": ("Helvetica", 16, "bold"),
            "fg": "#ffffff",
            "bd": 0,
            "relief": tk.FLAT,
            "highlightthickness": 0,
            "width": 25,
            "pady": 10,
        }

        tk.Button(main_frame, text="Jouer contre l'IA", bg="#2ecc71", **button_style, command=lambda: self.setup_game_mode("ai")).pack(pady=15)
        tk.Button(main_frame, text="Jouer entre amis", bg="#3498db", **button_style, command=lambda: self.setup_game_mode("human")).pack(pady=15)

    def setup_game_mode(self, mode):
        """Configure le jeu en fonction du mode choisi."""
        self.game_mode = mode
        if mode == "ai":
            self.players = ["Vous", "IA"]
            self.start_game()
        else:
            self.setup_players_screen()

    def setup_players_screen(self):
        """Crée l'interface pour saisir les noms des joueurs."""
        self.clear_frame()
        
        entry_frame = tk.Frame(self.master, bg="#1c2833")
        entry_frame.pack(pady=40)

        tk.Label(entry_frame, text="Entrez les noms des joueurs (un par ligne)", font=("Helvetica", 16, "bold"), bg="#1c2833", fg="#ecf0f1").pack(pady=10)

        self.player_names_text = tk.Text(entry_frame, height=6, width=40, font=("Helvetica", 12), bg="#34495e", fg="#ecf0f1", bd=0, relief=tk.FLAT, insertbackground="#ecf0f1")
        self.player_names_text.pack(pady=10)

        tk.Button(
            entry_frame,
            text="Démarrer le jeu",
            font=("Helvetica", 14, "bold"),
            bg="#2ecc71",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            width=20,
            pady=8,
            command=self.get_player_names
        ).pack(pady=10)
        
        tk.Button(
            entry_frame,
            text="Retour au menu",
            font=("Helvetica", 12),
            bg="#e74c3c",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            width=20,
            pady=6,
            command=self.setup_main_menu
        ).pack(pady=5)

    def get_player_names(self):
        """Récupère les noms des joueurs et démarre la partie."""
        names = [name.strip() for name in self.player_names_text.get("1.0", tk.END).split('\n') if name.strip()]
        if len(names) < 2:
            messagebox.showerror("Erreur", "Veuillez entrer au moins deux noms de joueurs.")
            return
        self.players = names
        self.start_game()

    def start_game(self):
        """Initialise la logique du jeu avec 12 pailles."""
        self.clear_frame()
        self.is_game_active = True
        self.current_player_index = 0
        
        self.straws = ["long"] * 11 + ["short"]
        random.shuffle(self.straws)

        self.create_game_ui()
        self.update_turn_label()

    def create_game_ui(self):
        """Construit l'interface principale du jeu, y compris le canevas des pailles."""
        self.turn_label = tk.Label(self.master, text="", font=("Helvetica", 20, "bold"), bg="#1c2833", fg="#ecf0f1")
        self.turn_label.pack(pady=10)

        self.game_frame = tk.Frame(self.master, bg="#1c2833")
        self.game_frame.pack(expand=True)
        
        self.straw_canvas = tk.Canvas(self.game_frame, width=800, height=450, bg="#2c3e50", highlightthickness=0)
        self.straw_canvas.pack(pady=20)

        self.straw_widgets = []
        x_start = 50
        y_start = 100
        straw_width = 30
        straw_spacing = 30
        
        for i, _ in enumerate(self.straws):
            x = x_start + i * (straw_width + straw_spacing)
            
            # Dessine la paille non révélée
            straw_id = self.straw_canvas.create_rectangle(x, y_start, x + straw_width, y_start + 250, fill="#7d5843", outline="#593b2a", width=2, tags=f"straw_{i}")
            
            # Lie le clic à une nouvelle méthode de gestion
            self.straw_canvas.tag_bind(f"straw_{i}", "<Button-1>", lambda event, idx=i: self.on_straw_click(idx))
            self.straw_widgets.append(straw_id)

        self.result_label = tk.Label(self.master, text="", font=("Helvetica", 20, "bold"), bg="#1c2833", fg="#e74c3c")
        self.result_label.pack(pady=10)
        
        self.restart_button = tk.Button(
            self.master,
            text="Recommencer",
            font=("Helvetica", 14, "bold"),
            bg="#e74c3c",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            pady=8,
            width=20,
            command=self.setup_main_menu
        )
        self.restart_button.pack(pady=20)
        self.restart_button.pack_forget() # Cache le bouton au début du jeu

    def on_straw_click(self, index):
        """
        Gère le clic de la souris. 
        Empêche les clics si c'est le tour de l'IA.
        """
        if self.is_ai_turn:
            return  # Ignore le clic si c'est le tour de l'IA

        self.select_straw(index)

    def update_turn_label(self):
        """Met à jour le label indiquant qui doit jouer."""
        if not self.is_game_active:
            return
        
        current_player_name = self.players[self.current_player_index]
        self.turn_label.config(text=f"C'est au tour de : {current_player_name}")
        
        if self.game_mode == "ai" and current_player_name == "IA":
            self.is_ai_turn = True
            self.master.after(1500, self.ai_move)
        else:
            self.is_ai_turn = False

    def ai_move(self):
        """Logique de l'IA pour choisir une paille non encore sélectionnée."""
        if not self.is_game_active:
            return
            
        unpicked_straw_indices = [i for i, _ in enumerate(self.straws) if not self.straw_canvas.find_withtag(f"revealed_{i}")]
        if unpicked_straw_indices:
            choice = random.choice(unpicked_straw_indices)
            self.select_straw(choice)

    def select_straw(self, index):
        """Gère la sélection d'une paille et la logique de fin de tour/partie."""
        if not self.is_game_active or self.straw_canvas.find_withtag(f"revealed_{index}"):
            return
            
        straw_type = self.straws[index]
        current_player = self.players[self.current_player_index]
        x_start = 50 + index * 60
        y_start = 100
        
        self.straw_canvas.delete(f"straw_{index}")
        
        if straw_type == "short":
            self.straw_canvas.create_rectangle(x_start, y_start + 100, x_start + 30, y_start + 200, fill="#e74c3c", outline="#c0392b", width=3, tags=f"revealed_{index}")
            self.straw_canvas.create_text(x_start + 15, y_start + 150, text="X", font=("Helvetica", 40, "bold"), fill="white", tags=f"revealed_{index}")
            
            # Message de résultat corrigé
            if self.game_mode == "ai" and current_player == "IA":
                self.result_label.config(text=f"L'IA a tiré la courte paille ! Vous avez gagné !", fg="#2ecc71")
            elif self.game_mode == "ai" and current_player == "Vous":
                self.result_label.config(text=f"Vous avez tiré la courte paille ! Vous avez perdu.", fg="#e74c3c")
            else: # Human mode
                self.result_label.config(text=f"{current_player} a tiré la courte paille ! Le jeu est terminé.", fg="#e74c3c")

            self.animate_short_straw(index, 0)
            self.end_game()
        else:
            self.straw_canvas.create_rectangle(x_start, y_start, x_start + 30, y_start + 250, fill="#2ecc71", outline="#27ae60", width=3, tags=f"revealed_{index}")
            self.result_label.config(text=f"Paille longue. Le jeu continue.", fg="#2ecc71")
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            self.update_turn_label()

    def animate_short_straw(self, index, step):
        """Anime la courte paille pour créer un effet de tremblement."""
        if step >= 10:
            return
        
        x_start = 50 + index * 60
        shake_offset = random.randint(-5, 5)
        
        self.straw_canvas.move(f"revealed_{index}", shake_offset, 0)
        
        # Rappel de la fonction pour continuer l'animation
        self.master.after(50, lambda: self.animate_short_straw(index, step + 1))

    def end_game(self):
        """Termine la partie et révèle toutes les pailles restantes."""
        self.is_game_active = False
        self.turn_label.config(text="")
        self.restart_button.pack()
        
        # Révèle toutes les pailles non sélectionnées
        for i in range(len(self.straws)):
            if not self.straw_canvas.find_withtag(f"revealed_{i}"):
                self.reveal_all_straws(i)

    def reveal_all_straws(self, index):
        """Révèle les pailles restantes sans affecter l'état du jeu."""
        straw_type = self.straws[index]
        x_start = 50 + index * 60
        y_start = 100
        
        self.straw_canvas.delete(f"straw_{index}")
        
        if straw_type == "short":
            self.straw_canvas.create_rectangle(x_start, y_start + 100, x_start + 30, y_start + 200, fill="#e74c3c", outline="#c0392b", width=3, tags=f"revealed_{index}")
        else:
            self.straw_canvas.create_rectangle(x_start, y_start, x_start + 30, y_start + 250, fill="#2ecc71", outline="#27ae60", width=3, tags=f"revealed_{index}")

# Point d'entrée de l'application
if __name__ == "__main__":
    root = tk.Tk()
    game = ShortStrawGame(root)
    root.mainloop()
