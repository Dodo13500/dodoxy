import tkinter as tk
from tkinter import messagebox
import random
from functools import partial

# Couleurs pour les nombres des cases révélées
COLOR_MAP = {
    1: "#00BFFF",  # Bleu ciel
    2: "#32CD32",  # Vert lime
    3: "#FF4500",  # Rouge orangé
    4: "#4169E1",  # Bleu royal
    5: "#DC143C",  # Rouge cramoisi
    6: "#00CED1",  # Cyan foncé
    7: "#A9A9A9",  # Gris foncé
    8: "#D3D3D3"   # Gris clair
}

# --- Classe de l'interface de démarrage ---
class SettingsWindow:
    """
    Fenêtre de configuration qui permet de choisir la taille du plateau et le nombre de bombes.
    """
    def __init__(self, master):
        self.master = master
        self.master.title("Démineur - Configuration")
        self.master.geometry("300x200")
        self.master.resizable(False, False)
        self.master.configure(bg="#212121")

        # Style pour les labels et les entrées
        label_font = ("Arial", 12, "bold")
        entry_font = ("Arial", 12)

        # Cadre pour les options
        options_frame = tk.Frame(self.master, padx=20, pady=20, bg="#212121")
        options_frame.pack(expand=True)

        # Labels et champs de saisie pour les dimensions et le nombre de bombes
        tk.Label(options_frame, text="Lignes:", font=label_font, bg="#212121", fg="#F5F5F5").grid(row=0, column=0, pady=5)
        self.rows_entry = tk.Entry(options_frame, width=5, font=entry_font, bg="#424242", fg="#F5F5F5", bd=2, relief=tk.FLAT)
        self.rows_entry.grid(row=0, column=1, pady=5)
        self.rows_entry.insert(0, "10")

        tk.Label(options_frame, text="Colonnes:", font=label_font, bg="#212121", fg="#F5F5F5").grid(row=1, column=0, pady=5)
        self.cols_entry = tk.Entry(options_frame, width=5, font=entry_font, bg="#424242", fg="#F5F5F5", bd=2, relief=tk.FLAT)
        self.cols_entry.grid(row=1, column=1, pady=5)
        self.cols_entry.insert(0, "10")

        tk.Label(options_frame, text="Bombes:", font=label_font, bg="#212121", fg="#F5F5F5").grid(row=2, column=0, pady=5)
        self.bombs_entry = tk.Entry(options_frame, width=5, font=entry_font, bg="#424242", fg="#F5F5F5", bd=2, relief=tk.FLAT)
        self.bombs_entry.grid(row=2, column=1, pady=5)
        self.bombs_entry.insert(0, "10")

        # Bouton pour lancer le jeu
        start_button = tk.Button(self.master, text="Commencer", font=("Arial", 14, "bold"), command=self.start_game, bg="#4CAF50", fg="white", bd=0, relief=tk.FLAT)
        start_button.pack(pady=10)

    def start_game(self):
        """
        Récupère les valeurs et lance une nouvelle partie de Démineur.
        """
        try:
            rows = int(self.rows_entry.get())
            cols = int(self.cols_entry.get())
            bombs = int(self.bombs_entry.get())

            if rows < 5 or cols < 5 or bombs < 1 or bombs >= rows * cols:
                messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides.\n(Min 5x5, Max < nombre de cases)")
                return
            
            self.master.destroy()
            game_root = tk.Tk()
            game = MinesweeperGame(game_root, rows, cols, bombs)
            game_root.mainloop()

        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des nombres entiers valides.")

# --- Classe principale du jeu Démineur ---
class MinesweeperGame:
    """
    Cette classe gère toute la logique et l'interface graphique du jeu Démineur.
    """
    def __init__(self, master, rows, cols, bombs):
        self.master = master
        self.master.title("Démineur")
        self.master.configure(bg="#212121")

        # Configuration du jeu
        self.rows = rows
        self.cols = cols
        self.bombs = bombs
        self.revealed_cells = 0
        self.game_over = False
        self.time_elapsed = 0
        self.is_playing = False

        # Création des structures de données pour le tableau de jeu
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.buttons = [[None for _ in range(cols)] for _ in range(rows)]
        self.flagged = [[False for _ in range(cols)] for _ in range(rows)]
        self.first_click = True
        self.bombs_remaining = self.bombs

        self.create_widgets()
        self.place_bombs()
        self.count_adjacent_bombs()

    def create_widgets(self):
        """
        Crée l'interface complète du jeu, y compris le tableau de bord et la grille de jeu.
        """
        # Cadre du tableau de bord (score, bombes, smiley)
        self.scoreboard = tk.Frame(self.master, bg="#303030", relief=tk.FLAT, bd=2, pady=5)
        self.scoreboard.pack(fill=tk.X, padx=10, pady=10)

        # Affichage du nombre de bombes
        self.bomb_count_label = tk.Label(self.scoreboard, text=f"{self.bombs_remaining:03d}", bg="#000000", fg="#00FFFF", font=("DS-Digital", 20, "bold"), relief=tk.SUNKEN, bd=2, padx=5)
        self.bomb_count_label.pack(side=tk.LEFT, padx=10)
        
        # Bouton pour redémarrer la partie (le smiley)
        self.restart_button = tk.Button(self.scoreboard, text="🙂", font=("Arial", 20), command=self.restart_game, bg="#424242", fg="#F5F5F5", relief=tk.FLAT, bd=2)
        self.restart_button.pack(side=tk.LEFT, expand=True)

        # Affichage du temps
        self.timer_label = tk.Label(self.scoreboard, text="000", bg="#000000", fg="#00FFFF", font=("DS-Digital", 20, "bold"), relief=tk.SUNKEN, bd=2, padx=5)
        self.timer_label.pack(side=tk.RIGHT, padx=10)

        # Cadre principal pour les boutons du jeu
        self.frame = tk.Frame(self.master, bg="#212121", relief=tk.FLAT, bd=2)
        self.frame.pack(padx=10, pady=10)

        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(self.frame, text=" ", width=2, height=1, relief=tk.RAISED,
                                bd=2, bg="#424242")
                btn.config(command=partial(self.on_left_click, r, c))
                btn.bind("<Button-3>", partial(self.on_right_click, r, c))
                btn.grid(row=r, column=c, padx=1, pady=1)
                self.buttons[r][c] = btn

    def update_timer(self):
        """
        Met à jour le chronomètre du jeu chaque seconde.
        """
        if self.is_playing:
            self.time_elapsed += 1
            self.timer_label.config(text=f"{self.time_elapsed:03d}")
            self.master.after(1000, self.update_timer)

    def place_bombs(self):
        """
        Place les bombes de manière aléatoire sur le tableau de jeu.
        """
        bomb_positions = random.sample(range(self.rows * self.cols), self.bombs)
        
        for pos in bomb_positions:
            row = pos // self.cols
            col = pos % self.cols
            self.board[row][col] = -1  # -1 représente une bombe

    def count_adjacent_bombs(self):
        """
        Calcule et définit le nombre de bombes adjacentes pour chaque cellule non-bombe.
        """
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == -1:
                    continue
                
                count = 0
                for i in range(r - 1, r + 2):
                    for j in range(c - 1, c + 2):
                        if 0 <= i < self.rows and 0 <= j < self.cols and self.board[i][j] == -1:
                            count += 1
                self.board[r][c] = count

    def on_left_click(self, r, c):
        """
        Gère l'action du clic gauche sur une case.
        """
        if self.game_over or self.flagged[r][c]:
            return

        # Démarre le jeu et le chronomètre au premier clic
        if self.first_click:
            self.is_playing = True
            self.update_timer()
            self.first_click = False

        if self.board[r][c] == -1:
            self.reveal_all_bombs()
            self.restart_button.config(text="☹️")
            response = messagebox.askyesno("Game Over", "BOOM! Vous avez trouvé une bombe. Voulez-vous recommencer ?")
            if response:
                self.restart_game()
            else:
                self.game_over = True
                self.is_playing = False
        else:
            self.reveal_cell(r, c)
            self.check_win()

    def on_right_click(self, r, c, event):
        """
        Gère l'action du clic droit sur une case pour poser un drapeau.
        """
        if self.game_over or self.buttons[r][c]['relief'] == 'sunken':
            return

        if self.flagged[r][c]:
            self.buttons[r][c].config(text=" ", fg="#F5F5F5", font=("Arial", 12))
            self.flagged[r][c] = False
            self.bombs_remaining += 1
            self.bomb_count_label.config(text=f"{self.bombs_remaining:03d}")
        else:
            if self.bombs_remaining > 0:
                self.buttons[r][c].config(text="🚩", fg="#FF4500", font=("Arial", 12))
                self.flagged[r][c] = True
                self.bombs_remaining -= 1
                self.bomb_count_label.config(text=f"{self.bombs_remaining:03d}")

    def reveal_cell(self, r, c):
        """
        Révèle une seule cellule et son contenu.
        """
        if self.buttons[r][c]['relief'] == 'sunken' or self.flagged[r][c]:
            return

        value = self.board[r][c]
        btn = self.buttons[r][c]
        
        # Correction pour maintenir l'espacement
        btn.config(text="")
        if value > 0:
            btn.config(text=str(value), fg=COLOR_MAP.get(value, "white"), font=("Arial", 12, "bold"))
            
        btn.config(relief=tk.SUNKEN, bg="#3c3c3c")
        
        self.revealed_cells += 1

        if value == 0:
            self.reveal_empty_cells(r, c)

    def reveal_empty_cells(self, r, c):
        """
        Révèle récursivement les cellules vides adjacentes.
        """
        for i in range(r - 1, r + 2):
            for j in range(c - 1, c + 2):
                if 0 <= i < self.rows and 0 <= j < self.cols:
                    if self.board[i][j] != -1 and self.buttons[i][j]['relief'] != 'sunken' and not self.flagged[i][j]:
                        self.reveal_cell(i, j)

    def reveal_all_bombs(self):
        """
        Révèle toutes les bombes sur le tableau de jeu.
        """
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == -1:
                    self.buttons[r][c].config(text="💣", fg="black", bg="#FF4500")
    
    def check_win(self):
        """
        Vérifie si le joueur a gagné la partie en révélant toutes les cases non-bombes.
        """
        total_cells = self.rows * self.cols
        if self.revealed_cells + self.bombs == total_cells:
            messagebox.showinfo("Félicitations !", "Vous avez gagné ! Toutes les bombes ont été évitées.")
            self.restart_button.config(text="😎")
            self.game_over = True
            self.is_playing = False
    
    def restart_game(self):
        """
        Réinitialise le jeu et l'interface pour une nouvelle partie.
        """
        self.master.destroy()
        root = tk.Tk()
        SettingsWindow(root)
        root.mainloop()

# --- Lancement du jeu ---
if __name__ == "__main__":
    root = tk.Tk()
    SettingsWindow(root)
    root.mainloop()
