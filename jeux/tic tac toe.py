# -*- coding: utf-8 -*-
import tkinter as tk
import random

class AIPlayer:
    """
    Joueur IA qui utilise l'algorithme Minimax pour un jeu imbattable.
    """
    def __init__(self, letter):
        self.letter = letter

    def get_move(self, board):
        """
        Sélectionne le meilleur coup de l'IA en utilisant Minimax.
        Le premier coup est optimisé pour être stratégique.
        """
        if board.count(' ') == 9:
            # Premier coup, choisir le centre ou un coin pour une stratégie agressive
            if board[4] == ' ':
                return 4
            else:
                return random.choice([0, 2, 6, 8])
        else:
            return self.minimax(board, self.letter)['position']

    def minimax(self, current_board, player):
        """
        Algorithme Minimax pour déterminer le meilleur coup.
        """
        max_player_letter = self.letter
        other_player_letter = 'O' if player == 'X' else 'X'

        if check_winner(current_board, other_player_letter):
            return {'position': None, 'score': 1 * (current_board.count(' ') + 1)}
        elif check_winner(current_board, max_player_letter):
            return {'position': None, 'score': -1 * (current_board.count(' ') + 1)}
        elif ' ' not in current_board:
            return {'position': None, 'score': 0}

        if player == max_player_letter:
            best = {'position': None, 'score': float('-inf')}
        else:
            best = {'position': None, 'score': float('inf')}

        available_moves = [i for i, x in enumerate(current_board) if x == ' ']
        
        for move in available_moves:
            current_board[move] = player
            
            sim_score = self.minimax(current_board, other_player_letter)

            current_board[move] = ' '
            sim_score['position'] = move

            if player == max_player_letter:
                if sim_score['score'] > best['score']:
                    best = sim_score
            else:
                if sim_score['score'] < best['score']:
                    best = sim_score
        
        return best

def check_winner(board, letter):
    """
    Vérifie si un joueur a gagné.
    """
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for condition in win_conditions:
        if all(board[i] == letter for i in condition):
            return True
    return False

class TicTacToeGUI:
    """
    Interface graphique pour le jeu de Morpion.
    """
    def __init__(self, master):
        self.master = master
        self.master.title("Morpion - Tic Tac Toe")
        self.master.resizable(False, False)
        self.current_player = 'X'
        self.board = [' ' for _ in range(9)]
        self.game_mode = None

        self.style = {
            "bg_color": "#2c3e50",
            "info_font": ("Arial", 14),
            "info_fg": "#ecf0f1",
            "result_font": ("Arial", 20, "bold"),
            "canvas_bg": "#34495e",
            "line_color": "#4a637a",
            "x_color": "#e74c3c",
            "o_color": "#3498db",
            "btn_bg": "#4a637a",
            "btn_active_bg": "#5e7790",
        }
        
        self.player_x_wins = 0
        self.player_o_wins = 0

        self.main_menu()

    def main_menu(self):
        """Affiche le menu principal pour choisir le mode de jeu."""
        self.clear_window()
        self.master.config(bg=self.style["bg_color"])

        label = tk.Label(self.master, text="Choisissez un mode de jeu",
                         font=("Arial", 20, "bold"), bg=self.style["bg_color"], fg=self.style["info_fg"])
        label.pack(pady=20)

        pvp_button = tk.Button(self.master, text="Joueur vs Joueur", font=self.style["info_font"],
                               bg=self.style["btn_bg"], fg=self.style["info_fg"], relief="flat",
                               activebackground=self.style["btn_active_bg"],
                               command=lambda: self.setup_game('PvsP'))
        pvp_button.pack(pady=10, ipadx=20, ipady=10)

        pvai_button = tk.Button(self.master, text="Joueur vs IA", font=self.style["info_font"],
                                bg=self.style["btn_bg"], fg=self.style["info_fg"], relief="flat",
                                activebackground=self.style["btn_active_bg"],
                                command=lambda: self.setup_game('PvsAI'))
        pvai_button.pack(pady=10, ipadx=20, ipady=10)

    def setup_game(self, mode):
        """Initialise la partie et l'interface de jeu."""
        self.game_mode = mode
        self.ai_player = AIPlayer('O') if mode == 'PvsAI' else None
        self.current_player = 'X'
        self.board = [' ' for _ in range(9)]
        self.clear_window()
        self.create_widgets()

    def create_widgets(self):
        """Crée les widgets de l'interface de jeu."""
        self.master.config(bg=self.style["bg_color"])
        
        self.info_label = tk.Label(self.master, text=f"C'est le tour de {self.current_player}",
                                   font=self.style["info_font"], bg=self.style["bg_color"], fg=self.style["info_fg"])
        self.info_label.pack(pady=10)
        
        self.result_label = tk.Label(self.master, text="",
                                     font=self.style["result_font"], bg=self.style["bg_color"], fg=self.style["info_fg"])
        self.result_label.pack(pady=5)
        
        self.score_label = tk.Label(self.master, text=f"Score : X {self.player_x_wins} - {self.player_o_wins} O",
                                   font=self.style["info_font"], bg=self.style["bg_color"], fg=self.style["info_fg"])
        self.score_label.pack(pady=5)

        self.canvas = tk.Canvas(self.master, width=300, height=300, bg=self.style["canvas_bg"], highlightthickness=0)
        self.canvas.pack(pady=20)
        self.draw_board_lines()
        self.canvas.bind("<Button-1>", self.on_click)

        button_frame = tk.Frame(self.master, bg=self.style["bg_color"])
        button_frame.pack(pady=10)

        reset_button = tk.Button(button_frame, text="Rejouer", font=self.style["info_font"],
                                 bg=self.style["btn_bg"], fg=self.style["info_fg"], relief="flat",
                                 activebackground=self.style["btn_active_bg"],
                                 command=self.reset_game)
        reset_button.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)
        
        menu_button = tk.Button(button_frame, text="Menu Principal", font=self.style["info_font"],
                                bg=self.style["btn_bg"], fg=self.style["info_fg"], relief="flat",
                                activebackground=self.style["btn_active_bg"],
                                command=self.main_menu)
        menu_button.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)
        
        if self.game_mode == 'PvsAI' and self.current_player == self.ai_player.letter:
            self.master.after(500, self.ai_turn)

    def draw_board_lines(self):
        """Dessine les lignes du plateau de jeu."""
        self.canvas.delete("lines")
        for i in range(1, 3):
            self.canvas.create_line(i * 100, 0, i * 100, 300, fill=self.style["line_color"], width=3)
            self.canvas.create_line(0, i * 100, 300, i * 100, fill=self.style["line_color"], width=3)

    def draw_symbol(self, index, letter):
        """Dessine le symbole 'X' ou 'O' sur le canvas."""
        row, col = divmod(index, 3)
        x_center = col * 100 + 50
        y_center = row * 100 + 50
        
        if letter == 'X':
            self.canvas.create_line(x_center - 35, y_center - 35, x_center + 35, y_center + 35, fill=self.style["x_color"], width=5)
            self.canvas.create_line(x_center + 35, y_center - 35, x_center - 35, y_center + 35, fill=self.style["x_color"], width=5)
        else: # 'O'
            self.canvas.create_oval(x_center - 35, y_center - 35, x_center + 35, y_center + 35, outline=self.style["o_color"], width=5)

    def on_click(self, event):
        """Gère le clic sur le canvas."""
        if self.check_end_game():
            return

        x, y = event.x, event.y
        col = x // 100
        row = y // 100
        index = row * 3 + col

        if self.board[index] == ' ':
            self.board[index] = self.current_player
            self.draw_symbol(index, self.current_player)

            if self.check_winner(self.current_player):
                self.update_score()
                self.result_label.config(text=f"Le joueur {self.current_player} a gagné !")
                self.canvas.unbind("<Button-1>")
            elif ' ' not in self.board:
                self.result_label.config(text="Égalité !")
                self.canvas.unbind("<Button-1>")
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
                self.info_label.config(text=f"C'est le tour de {self.current_player}")
                if self.game_mode == 'PvsAI' and self.current_player == self.ai_player.letter:
                    self.master.after(500, self.ai_turn)

    def ai_turn(self):
        """Déclenche le coup de l'IA."""
        if self.check_end_game():
            return
            
        move = self.ai_player.get_move(self.board)
        if move is not None:
            self.board[move] = self.current_player
            self.draw_symbol(move, self.current_player)
            
            if self.check_winner(self.current_player):
                self.update_score()
                self.result_label.config(text=f"Le joueur {self.current_player} a gagné !")
                self.canvas.unbind("<Button-1>")
            elif ' ' not in self.board:
                self.result_label.config(text="Égalité !")
                self.canvas.unbind("<Button-1>")
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
                self.info_label.config(text=f"C'est le tour de {self.current_player}")


    def check_winner(self, player):
        """Vérifie les conditions de victoire."""
        return check_winner(self.board, player)

    def check_end_game(self):
        """Vérifie si la partie est terminée (victoire ou égalité)."""
        return self.check_winner('X') or self.check_winner('O') or ' ' not in self.board

    def update_score(self):
        """Met à jour l'affichage du score."""
        if self.current_player == 'X':
            self.player_x_wins += 1
        else:
            self.player_o_wins += 1
        self.score_label.config(text=f"Score : X {self.player_x_wins} - {self.player_o_wins} O")
        
    def reset_game(self):
        """Réinitialise le plateau de jeu."""
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
        self.info_label.config(text=f"C'est le tour de {self.current_player}")
        self.result_label.config(text="")
        self.canvas.delete("all")
        self.draw_board_lines()
        self.canvas.bind("<Button-1>", self.on_click)
        
        if self.game_mode == 'PvsAI' and self.current_player == self.ai_player.letter:
            self.master.after(500, self.ai_turn)
            
    def clear_window(self):
        """Supprime tous les widgets de la fenêtre."""
        for widget in self.master.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()