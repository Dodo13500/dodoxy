import tkinter as tk
from tkinter import messagebox
import random

# --- Class of the game interface ---
class RockPaperScissorsGame(tk.Tk):
    """
    Main class for the Rock-Paper-Scissors game with an improved interface.
    """
    def __init__(self):
        super().__init__()
        self.title("Pierre-Feuille-Ciseaux Pro")
        self.geometry("600x400")
        self.resizable(False, False)
        self.configure(bg="#212121")  # Dark background for a modern look

        # Game state variables
        self.player_score = 0
        self.computer_score = 0
        self.choices = ["Pierre", "Feuille", "Ciseaux"]
        self.player_history = []  # To store the player's last moves

        self.create_widgets()

    def create_widgets(self):
        """
        Creates all the user interface elements.
        """
        # Main frame for content
        main_frame = tk.Frame(self, bg="#212121")
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Title
        tk.Label(main_frame, text="Pierre-Feuille-Ciseaux", font=("Helvetica", 24, "bold"), bg="#212121", fg="#F5F5F5").pack(pady=10)

        # Score display
        score_frame = tk.Frame(main_frame, bg="#212121")
        score_frame.pack(pady=10)
        
        self.player_score_label = tk.Label(score_frame, text=f"Joueur: {self.player_score}", font=("Arial", 16), bg="#212121", fg="#4CAF50")
        self.player_score_label.pack(side=tk.LEFT, padx=20)
        
        self.computer_score_label = tk.Label(score_frame, text=f"Ordinateur: {self.computer_score}", font=("Arial", 16), bg="#212121", fg="#FF4500")
        self.computer_score_label.pack(side=tk.RIGHT, padx=20)

        # Choice display
        choice_frame = tk.Frame(main_frame, bg="#212121")
        choice_frame.pack(pady=20)
        
        self.player_choice_label = tk.Label(choice_frame, text="Ton choix", font=("Arial", 14), bg="#212121", fg="#F5F5F5", width=15)
        self.player_choice_label.pack(side=tk.LEFT, padx=10)
        
        self.vs_label = tk.Label(choice_frame, text="vs", font=("Arial", 14, "bold"), bg="#212121", fg="#BDBDBD")
        self.vs_label.pack(side=tk.LEFT, padx=10)

        self.computer_choice_label = tk.Label(choice_frame, text="Choix de l'IA", font=("Arial", 14), bg="#212121", fg="#F5F5F5", width=15)
        self.computer_choice_label.pack(side=tk.RIGHT, padx=10)

        # Result display
        self.result_label = tk.Label(main_frame, text="", font=("Arial", 18, "bold"), bg="#212121", fg="#F5F5F5")
        self.result_label.pack(pady=10)

        # Buttons for the player's choices
        button_frame = tk.Frame(main_frame, bg="#212121")
        button_frame.pack(pady=20)
        
        # Using a loop to create buttons dynamically
        for choice in self.choices:
            tk.Button(button_frame, text=choice, font=("Arial", 14, "bold"), 
                      command=lambda c=choice: self.play_round(c), 
                      bg="#4CAF50" if choice == "Pierre" else "#2196F3" if choice == "Feuille" else "#F44336",
                      fg="white", bd=0, relief=tk.RAISED, activebackground="#424242", activeforeground="white",
                      padx=15, pady=8, width=10).pack(side=tk.LEFT, padx=10)

        # Restart button
        restart_button = tk.Button(main_frame, text="Nouvelle partie", command=self.restart_game, font=("Arial", 12), bg="#616161", fg="white", bd=0, relief=tk.FLAT)
        restart_button.pack(pady=10)
    
    def get_computer_choice(self):
        """
        Determines the computer's choice based on a simple strategy.
        """
        # If the player has made at least 3 moves, check for a pattern
        if len(self.player_history) >= 3:
            # Check if the player is repeating the same move
            if self.player_history[-1] == self.player_history[-2] and self.player_history[-2] == self.player_history[-3]:
                # If so, play the move that beats the player's repeated move
                last_move = self.player_history[-1]
                if last_move == "Pierre":
                    return "Feuille"
                elif last_move == "Feuille":
                    return "Ciseaux"
                else: # "Ciseaux"
                    return "Pierre"

        # Otherwise, choose a random move
        return random.choice(self.choices)

    def play_round(self, player_choice):
        """
        Plays a single round of the game.
        """
        computer_choice = self.get_computer_choice()
        result = ""
        
        # Add player's choice to history
        self.player_history.append(player_choice)
        # Keep history size to a manageable number (e.g., 5)
        if len(self.player_history) > 5:
            self.player_history.pop(0)

        # Update choice displays
        self.player_choice_label.config(text=player_choice, fg="#4CAF50")
        self.computer_choice_label.config(text=computer_choice, fg="#FF4500")

        # Determine the winner
        if player_choice == computer_choice:
            result = "Égalité !"
            self.result_label.config(fg="#BDBDBD")
        elif (player_choice == "Pierre" and computer_choice == "Ciseaux") or \
             (player_choice == "Feuille" and computer_choice == "Pierre") or \
             (player_choice == "Ciseaux" and computer_choice == "Feuille"):
            result = "Tu as gagné !"
            self.player_score += 1
            self.player_score_label.config(text=f"Joueur: {self.player_score}")
            self.result_label.config(fg="#4CAF50")
        else:
            result = "L'ordinateur a gagné !"
            self.computer_score += 1
            self.computer_score_label.config(text=f"Ordinateur: {self.computer_score}")
            self.result_label.config(fg="#FF4500")
        
        # Display the result
        self.result_label.config(text=result)

    def restart_game(self):
        """
        Resets the scores and the display for a new game.
        """
        self.player_score = 0
        self.computer_score = 0
        self.player_history = []
        self.player_score_label.config(text=f"Joueur: {self.player_score}")
        self.computer_score_label.config(text=f"Ordinateur: {self.computer_score}")
        self.result_label.config(text="")
        self.player_choice_label.config(text="Ton choix", fg="#F5F5F5")
        self.computer_choice_label.config(text="Choix de l'IA", fg="#F5F5F5")

# Run the game
if __name__ == "__main__":
    app = RockPaperScissorsGame()
    app.mainloop()
