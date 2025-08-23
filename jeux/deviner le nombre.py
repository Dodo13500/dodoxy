import tkinter as tk
from tkinter import messagebox
import random

# --- Classe principale du jeu "Devine le nombre" ---
class GuessTheNumberGame(tk.Tk):
    """
    Classe principale pour le jeu "Devine le nombre" avec une interface améliorée.
    """
    def __init__(self):
        super().__init__()
        self.title("Devine le nombre Pro")
        self.geometry("400x300")
        self.resizable(False, False)
        self.configure(bg="#212121")  # Fond sombre pour un look moderne

        self.secret_number = 0
        self.attempts = 0

        self.create_widgets()
        self.start_new_game()

    def create_widgets(self):
        """
        Crée les éléments de l'interface utilisateur.
        """
        # Cadre principal pour le contenu
        main_frame = tk.Frame(self, bg="#212121")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Titre
        self.title_label = tk.Label(main_frame, text="Devine le nombre !", font=("Helvetica", 24, "bold"), bg="#212121", fg="#F5F5F5")
        self.title_label.pack(pady=10)

        # Instructions
        self.instruction_label = tk.Label(main_frame, text="Je pense à un nombre entre 1 et 100.", font=("Arial", 14), bg="#212121", fg="#BDBDBD")
        self.instruction_label.pack(pady=5)
        
        # Champ de saisie
        self.guess_entry = tk.Entry(main_frame, width=10, font=("Arial", 16), justify="center", bg="#424242", fg="#F5F5F5", bd=2, relief=tk.FLAT, insertbackground="#F5F5F5")
        self.guess_entry.pack(pady=10)
        self.guess_entry.bind("<Return>", self.check_guess)

        # Bouton de vérification
        self.check_button = tk.Button(main_frame, text="Vérifier", command=self.check_guess, font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", bd=0, relief=tk.FLAT, activebackground="#388E3C", activeforeground="white")
        self.check_button.pack(pady=5, ipadx=10, ipady=5)
        
        # Zone d'affichage des résultats
        self.result_label = tk.Label(main_frame, text="", font=("Arial", 14), bg="#212121", fg="#F5F5F5")
        self.result_label.pack(pady=10)

    def start_new_game(self):
        """
        Initialise une nouvelle partie du jeu.
        """
        self.secret_number = random.randint(1, 100)
        self.attempts = 0
        self.result_label.config(text="")
        self.guess_entry.delete(0, tk.END)
        self.guess_entry.config(state="normal")
        self.check_button.config(state="normal")

    def check_guess(self, event=None):
        """
        Vérifie la devinette de l'utilisateur.
        """
        try:
            guess = int(self.guess_entry.get())
            self.attempts += 1

            if guess < self.secret_number:
                self.result_label.config(text="C'est plus grand !", fg="#FF4500")
            elif guess > self.secret_number:
                self.result_label.config(text="C'est plus petit !", fg="#FF4500")
            else:
                self.result_label.config(text=f"Bravo ! Tu as trouvé en {self.attempts} tentatives.", fg="#4CAF50")
                self.guess_entry.config(state="disabled")
                self.check_button.config(state="disabled")
                
                rejouer = messagebox.askyesno("Partie terminée", f"Bravo ! Tu as trouvé le bon nombre en {self.attempts} tentatives. Veux-tu recommencer une partie ?")
                if rejouer:
                    self.start_new_game()
                else:
                    self.destroy()

        except ValueError:
            messagebox.showerror("Erreur de saisie", "Veuillez entrer un nombre valide.", parent=self)
            self.guess_entry.delete(0, tk.END)

# Lancement du jeu
if __name__ == "__main__":
    app = GuessTheNumberGame()
    app.mainloop()
