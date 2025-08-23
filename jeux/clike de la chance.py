import tkinter as tk
import random

# --- Classe de l'interface du jeu ---
class LuckyClickGame(tk.Tk):
    """
    Classe principale pour le jeu du Clic de la Chance avec une interface améliorée.
    """
    def __init__(self):
        super().__init__()
        self.title("Le Clic de la Chance Pro")
        self.geometry("600x400")
        self.resizable(False, False)
        self.configure(bg="#2c3e50")  # Fond sombre pour un look moderne

        # Variables d'état du jeu
        self.score = 0
        self.winning_case = None
        self.last_winning_case = None # Pour stocker la dernière case gagnante
        self.buttons = []
        self.play_count = 0  # Compteur de parties
        self.streak = 0  # Compteur de victoires consécutives

        self.create_widgets()

    def create_widgets(self):
        """
        Crée tous les éléments de l'interface utilisateur.
        """
        # Cadre principal pour le contenu
        main_frame = tk.Frame(self, bg="#2c3e50")
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Titre
        tk.Label(main_frame, text="Le Clic de la Chance", font=("Helvetica", 28, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=10)

        # Affichage du score et des statistiques
        stats_frame = tk.Frame(main_frame, bg="#2c3e50")
        stats_frame.pack(pady=5)
        self.score_label = tk.Label(stats_frame, text=f"Score: {self.score}", font=("Arial", 16), bg="#2c3e50", fg="#3498db")
        self.score_label.pack(side=tk.LEFT, padx=10)
        self.streak_label = tk.Label(stats_frame, text=f"Série: {self.streak}", font=("Arial", 16), bg="#2c3e50", fg="#f1c40f")
        self.streak_label.pack(side=tk.LEFT, padx=10)

        # Affichage des instructions/résultats
        self.result_label = tk.Label(main_frame, text="Clique sur la bonne case pour gagner !", font=("Arial", 18, "italic"), bg="#2c3e50", fg="#ecf0f1")
        self.result_label.pack(pady=20)
        
        # Cadre pour les boutons
        button_frame = tk.Frame(main_frame, bg="#2c3e50")
        button_frame.pack(pady=20)
        
        # Crée les boutons dynamiquement
        for i in range(1, 4):
            button = tk.Button(button_frame, text=str(i), font=("Arial", 30, "bold"),
                               command=lambda i=i: self.check_click(i),
                               bg="#e74c3c", fg="white", bd=0, relief=tk.RAISED,
                               activebackground="#c0392b", activeforeground="white",
                               width=5, height=2)  # Définir une dimension uniforme
            button.pack(side=tk.LEFT, padx=15)
            self.buttons.append(button)

        # Démarre la première manche
        self.start_new_round()

    def start_new_round(self):
        """
        Initialise une nouvelle manche du jeu.
        """
        self.play_count += 1
        self.result_label.config(text="Clique sur la bonne case pour gagner !", fg="#ecf0f1")
        for button in self.buttons:
            button.config(bg="#e74c3c", state=tk.NORMAL)
        
        # Logique de randomisation améliorée
        if self.last_winning_case is not None and random.random() > 0.3: # 70% de chance d'éviter la dernière case
            possible_cases = [1, 2, 3]
            possible_cases.remove(self.last_winning_case)
            self.winning_case = random.choice(possible_cases)
        else:
            self.winning_case = random.randint(1, 3)

        self.last_winning_case = self.winning_case

    def check_click(self, choice):
        """
        Vérifie si le joueur a cliqué sur la bonne case.
        """
        if choice == self.winning_case:
            self.result_label.config(text="Bravo, tu as gagné !", fg="#2ecc71")
            self.score += 1
            self.streak += 1  # Incrémente la série de victoires
            self.score_label.config(text=f"Score: {self.score}")
            self.streak_label.config(text=f"Série: {self.streak}")
            self.buttons[choice-1].config(bg="#2ecc71")
        else:
            self.result_label.config(text=f"Dommage, c'était la case {self.winning_case}.", fg="#e74c3c")
            self.streak = 0  # Réinitialise la série de victoires
            self.streak_label.config(text=f"Série: {self.streak}")
            self.buttons[choice-1].config(bg="#c0392b")
            self.buttons[self.winning_case-1].config(bg="#2ecc71")
            
        # Après le clic, lance une nouvelle manche après un court délai
        self.after(1000, self.start_new_round)

# Lancer le jeu
if __name__ == "__main__":
    app = LuckyClickGame()
    app.mainloop()
