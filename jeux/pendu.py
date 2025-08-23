import tkinter as tk
from tkinter import messagebox
import random
from functools import partial

# Dictionnaire de mots par difficulté
WORDS_BY_DIFFICULTY = {
    "Facile": ["python", "clavier", "souris", "fenetre", "code"],
    "Moyen": ["ordinateur", "programme", "developpement", "intelligence", "interface"],
    "Difficile": ["cryptographie", "algorithme", "fonctionnalite", "personnalisation", "environnement"]
}

# Nombre d'erreurs maximales par difficulté
MAX_GUESSES = {
    "Facile": 10,
    "Moyen": 8,
    "Difficile": 6
}

# --- Classe de l'interface de démarrage ---
class StartWindow:
    """
    Fenêtre de démarrage pour choisir le niveau de difficulté.
    """
    def __init__(self, master):
        self.master = master
        self.master.title("Trouve le mot - Démarrage")
        self.master.geometry("300x200")
        self.master.resizable(False, False)
        self.master.configure(bg="#212121")

        tk.Label(self.master, text="Choisissez la difficulté :", font=("Arial", 14, "bold"), bg="#212121", fg="#F5F5F5").pack(pady=20)
        
        self.difficulty_var = tk.StringVar(value="Facile")

        # Ajout d'une frame pour les radiobuttons pour améliorer l'alignement
        difficulty_frame = tk.Frame(self.master, bg="#212121")
        difficulty_frame.pack(pady=10)

        for difficulty in WORDS_BY_DIFFICULTY.keys():
            # Utilise une fonction partielle pour passer l'argument `difficulty` à la fonction de vérification
            tk.Radiobutton(difficulty_frame, text=difficulty, variable=self.difficulty_var, value=difficulty,
                           font=("Arial", 12), bg="#212121", fg="#F5F5F5", selectcolor="#424242",
                           activebackground="#424242", activeforeground="#F5F5F5",
                           indicatoron=0, width=20, padx=5, pady=5,
                           command=partial(self.ask_for_confirmation, difficulty)).pack()

        # Le bouton OK est maintenant correctement positionné sous les boutons radio
        # Son action a été déplacée vers la fonction de confirmation
        start_button = tk.Button(self.master, text="OK", font=("Arial", 14, "bold"), command=self.start_game, bg="#4CAF50", fg="white", bd=2, relief=tk.RAISED)
        start_button.pack(pady=10)

    def ask_for_confirmation(self, difficulty):
        """
        Affiche une boîte de dialogue pour confirmer le choix de la difficulté.
        """
        confirmation = messagebox.askyesno("Confirmation de la difficulté",
                                          f"Voulez-vous vraiment commencer avec la difficulté '{difficulty}' ?")
        if confirmation:
            self.start_game()

    def start_game(self):
        """
        Détruit la fenêtre de démarrage et lance le jeu principal.
        """
        difficulty = self.difficulty_var.get()
        self.master.destroy()
        game_root = tk.Tk()
        game = GuessTheWordGame(game_root, difficulty)
        game_root.mainloop()


# --- Classe principale du jeu ---
class GuessTheWordGame:
    """
    Classe principale pour le jeu "Trouve le mot" avec une interface améliorée.
    """
    def __init__(self, master, difficulty):
        self.master = master
        self.master.title(f"Trouve le mot Pro - {difficulty}")
        self.master.resizable(False, False)
        self.master.configure(bg="#212121")

        self.difficulty = difficulty
        self.words = WORDS_BY_DIFFICULTY[self.difficulty]
        self.max_guesses = MAX_GUESSES[self.difficulty]
        self.secret_word = ""
        self.hidden_word = []
        self.guesses_left = self.max_guesses
        self.wrong_letters = []

        # Sélection du mot secret pour pouvoir calculer la taille de la fenêtre
        self.secret_word = random.choice(self.words)
        
        # Calcul de la taille de la fenêtre en fonction de la longueur du mot
        # On estime la largeur requise pour le mot et on ajoute une marge
        base_width = 400
        word_width = len(self.secret_word) * 40 # 40 pixels par lettre pour la police 'Courier', 36
        window_width = max(base_width, word_width + 100) # Assure une largeur minimale
        self.master.geometry(f"{window_width}x500")

        self.create_widgets()
        self.start_new_game()

    def create_widgets(self):
        """
        Crée les éléments de l'interface utilisateur.
        """
        # Titre
        tk.Label(self.master, text="Devine le mot !", font=("Helvetica", 20, "bold"), bg="#212121", fg="#F5F5F5").pack(pady=10)
        
        # Zone de dessin pour le pendu
        self.drawing_area = tk.Canvas(self.master, width=200, height=200, bg="#212121", highlightthickness=0)
        self.drawing_area.pack(pady=10)
        
        # Affichage du mot caché
        self.hidden_word_label = tk.Label(self.master, text="", font=("Courier", 36, "bold"), bg="#212121", fg="#4CAF50")
        self.hidden_word_label.pack(pady=10)

        # Affichage des lettres déjà dites
        tk.Label(self.master, text="Lettres déjà dites :", font=("Arial", 12), bg="#212121", fg="#F5F5F5").pack(pady=5)
        self.wrong_letters_label = tk.Label(self.master, text="", font=("Arial", 14), bg="#212121", fg="#FF4500")
        self.wrong_letters_label.pack()

        # Cadre pour la saisie de la lettre
        input_frame = tk.Frame(self.master, bg="#212121")
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Entre une lettre :", font=("Arial", 12), bg="#212121", fg="#F5F5F5").pack(side=tk.LEFT)
        self.letter_entry = tk.Entry(input_frame, width=5, font=("Arial", 12), bg="#424242", fg="#F5F5F5", bd=2, relief=tk.FLAT)
        self.letter_entry.pack(side=tk.LEFT, padx=5)
        self.letter_entry.bind("<Return>", lambda event: self.check_letter())

        # Bouton pour vérifier la lettre
        check_button = tk.Button(input_frame, text="Vérifier", command=self.check_letter, font=("Arial", 12), bg="#4CAF50", fg="white", bd=0, relief=tk.FLAT)
        check_button.pack(side=tk.LEFT)
        
        # Affichage des messages d'erreur
        self.error_label = tk.Label(self.master, text="", font=("Arial", 12), bg="#212121", fg="#FF4500")
        self.error_label.pack(pady=5)

        # Bouton pour recommencer le jeu
        self.restart_button = tk.Button(self.master, text="Recommencer", command=self.restart_app, font=("Arial", 12), bg="#303030", fg="#F5F5F5", bd=0, relief=tk.FLAT)
        self.restart_button.pack(pady=10)
        
    def start_new_game(self):
        """
        Initialise une nouvelle partie du jeu.
        """
        # Le mot secret est déjà choisi dans __init__, donc on ne le change pas ici.
        self.hidden_word = ["_" for _ in self.secret_word]
        self.guesses_left = self.max_guesses
        self.wrong_letters = []
        self.error_label.config(text="")
        
        self.hidden_word_label.config(text=" ".join(self.hidden_word), fg="#4CAF50")
        self.wrong_letters_label.config(text="", fg="#FF4500")
        self.letter_entry.delete(0, tk.END)
        self.draw_hangman()

    def draw_hangman(self):
        """
        Dessine le pendu en fonction du nombre de tentatives restantes.
        """
        self.drawing_area.delete("all")
        
        # Calcule le nombre de parties du corps à dessiner
        parts_to_draw = self.max_guesses - self.guesses_left
        
        # Poteau du pendu
        if self.max_guesses > 0:
            self.drawing_area.create_line(50, 180, 150, 180, fill="#F5F5F5", width=3)
            self.drawing_area.create_line(70, 180, 70, 20, fill="#F5F5F5", width=3)
            self.drawing_area.create_line(70, 20, 130, 20, fill="#F5F5F5", width=3)
        if self.max_guesses > 1:
            self.drawing_area.create_line(130, 20, 130, 40, fill="#F5F5F5", width=3)
        
        # Corps du pendu, dessiné étape par étape
        if parts_to_draw >= 1:
            self.drawing_area.create_oval(115, 40, 145, 70, outline="#F5F5F5", width=2) # Tête
        if parts_to_draw >= 2:
            self.drawing_area.create_line(130, 70, 130, 120, fill="#F5F5F5", width=2) # Corps
        if parts_to_draw >= 3:
            self.drawing_area.create_line(130, 80, 100, 100, fill="#F5F5F5", width=2) # Bras gauche
        if parts_to_draw >= 4:
            self.drawing_area.create_line(130, 80, 160, 100, fill="#F5F5F5", width=2) # Bras droit
        if parts_to_draw >= 5:
            self.drawing_area.create_line(130, 120, 110, 160, fill="#F5F5F5", width=2) # Jambe gauche
        if parts_to_draw >= 6:
            self.drawing_area.create_line(130, 120, 150, 160, fill="#F5F5F5", width=2) # Jambe droite
        if parts_to_draw >= 7:
            self.drawing_area.create_line(120, 50, 125, 55, fill="#F5F5F5", width=1) # Œil gauche
            self.drawing_area.create_line(125, 50, 130, 55, fill="#F5F5F5", width=1)
            self.drawing_area.create_line(135, 50, 140, 55, fill="#F5F5F5", width=1) # Œil droit
            self.drawing_area.create_line(140, 50, 145, 55, fill="#F5F5F5", width=1)
            self.drawing_area.create_arc(120, 60, 140, 70, start=180, extent=180, outline="#F5F5F5", style=tk.ARC) # Bouche triste
            
    def check_letter(self):
        """
        Vérifie si la lettre proposée est dans le mot secret.
        """
        letter = self.letter_entry.get().lower()
        self.letter_entry.delete(0, tk.END)

        if len(letter) != 1 or not letter.isalpha():
            self.error_label.config(text="Veuillez entrer une seule lettre.")
            return

        if letter in self.hidden_word or letter in self.wrong_letters:
            self.error_label.config(text="Cette lettre a déjà été proposée.")
            return
        
        self.error_label.config(text="")

        if letter in self.secret_word:
            for i, char in enumerate(self.secret_word):
                if char == letter:
                    self.hidden_word[i] = letter
        else:
            self.wrong_letters.append(letter)
            self.guesses_left -= 1
            self.wrong_letters.sort()
            self.wrong_letters_label.config(text=" ".join(self.wrong_letters))
            self.draw_hangman()

        self.hidden_word_label.config(text=" ".join(self.hidden_word))
        self.check_game_status()

    def check_game_status(self):
        """
        Vérifie si le joueur a gagné ou perdu.
        """
        if "_" not in self.hidden_word:
            messagebox.showinfo("Gagné !", f"Bravo ! Tu as trouvé le mot '{self.secret_word}' en {self.max_guesses - self.guesses_left} erreurs.")
            self.hidden_word_label.config(fg="#F5F5F5")
            self.master.after(5000, self.restart_app)
            return

        if self.guesses_left <= 0:
            messagebox.showinfo("Perdu !", f"Dommage ! Le mot était '{self.secret_word}'.")
            self.hidden_word_label.config(fg="#FF4500")
            self.master.after(5000, self.restart_app)
            return
            
    def restart_app(self):
        """
        Redémarre l'application en affichant la fenêtre de démarrage.
        """
        self.master.destroy()
        root = tk.Tk()
        StartWindow(root)
        root.mainloop()

# Lancement du jeu
if __name__ == "__main__":
    root = tk.Tk()
    StartWindow(root)
    root.mainloop()
