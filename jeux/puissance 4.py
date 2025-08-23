# -*- coding: utf-8 -*-
import tkinter as tk
import math
import random

# Définitions des constantes du jeu
ROWS = 6
COLS = 7
CELL_SIZE = 100
RADIUS = int(CELL_SIZE / 2 - 5)
ANIMATION_SPEED = 20

PLAYER_1 = 1
PLAYER_2 = 2
AI_PLAYER = 2

# Couleurs pour l'interface
BLUE = "#2E86C1"
GRID_BG = "#34495e"
RED = "#E74C3C"
YELLOW = "#F1C40F"
TEXT_COLOR = "#ECF0F1"
BUTTON_BG = "#4A637A"
BUTTON_ACTIVE_BG = "#5E7790"
VICTORY_COLOR = "#2ECC71"
RELIEF_COLOR_LIGHT_RED = "#ff6a5f"
RELIEF_COLOR_DARK_RED = "#ac2116"
RELIEF_COLOR_LIGHT_YELLOW = "#ffdb5c"
RELIEF_COLOR_DARK_YELLOW = "#c09800"

class ConnectFourGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Puissance 4")
        self.master.resizable(False, False)

        self.board = self.create_board()
        self.turn = PLAYER_1
        self.game_over = False
        self.is_animating = False
        self.is_ai_game = False

        self.canvas = None
        self.current_drop_token = None

        self.style = {
            "bg_color": GRID_BG,
            "info_font": ("Arial", 14),
            "info_fg": TEXT_COLOR,
            "result_font": ("Arial", 20, "bold"),
            "btn_bg": BUTTON_BG,
            "btn_active_bg": BUTTON_ACTIVE_BG,
        }
        
        self.main_menu()

    def create_board(self):
        return [[0 for _ in range(COLS)] for _ in range(ROWS)]

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.clear_window()
        self.master.config(bg=self.style["bg_color"])

        title_label = tk.Label(self.master, text="Puissance 4",
                               font=("Arial", 36, "bold"), bg=self.style["bg_color"], fg=self.style["info_fg"])
        title_label.pack(pady=40)

        pvp_button = tk.Button(self.master, text="Joueur vs Joueur", font=self.style["info_font"],
                               bg=self.style["btn_bg"], fg=self.style["info_fg"], relief="flat",
                               activebackground=self.style["btn_active_bg"],
                               command=lambda: self.setup_game(False))
        pvp_button.pack(pady=10, ipadx=40, ipady=15)

        pvai_button = tk.Button(self.master, text="Joueur vs IA", font=self.style["info_font"],
                                bg=self.style["btn_bg"], fg=self.style["info_fg"], relief="flat",
                                activebackground=self.style["btn_active_bg"],
                                command=lambda: self.setup_game(True))
        pvai_button.pack(pady=10, ipadx=55, ipady=15)

    def setup_game(self, is_ai_game):
        self.is_ai_game = is_ai_game
        self.board = self.create_board()
        self.turn = PLAYER_1
        self.game_over = False
        self.is_animating = False
        self.clear_window()
        self.create_game_widgets()
        if self.is_ai_game and self.turn == AI_PLAYER:
            self.master.after(500, self.ai_turn)

    def create_game_widgets(self):
        self.master.config(bg=self.style["bg_color"])

        self.info_label = tk.Label(self.master, text="C'est au tour de Joueur 1 (Rouge)",
                                   font=self.style["info_font"], bg=self.style["bg_color"], fg=self.style["info_fg"])
        self.info_label.pack(pady=10)
        
        self.result_label = tk.Label(self.master, text="",
                                     font=self.style["result_font"], bg=self.style["bg_color"], fg=self.style["info_fg"])
        self.result_label.pack(pady=5)

        self.canvas = tk.Canvas(self.master, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE, bg=BLUE)
        self.canvas.pack()
        self.draw_board()
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

    def draw_board(self):
        self.canvas.delete("all")
        
        for c in range(COLS):
            for r in range(ROWS):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=GRID_BG, outline=BLUE, width=2)
                
                player = self.board[r][c]
                if player != 0:
                    color = RED if player == PLAYER_1 else YELLOW
                    self.draw_relief_circle(c, r, color)

    def draw_relief_circle(self, col, row, color):
        x = col * CELL_SIZE + CELL_SIZE / 2
        y = row * CELL_SIZE + CELL_SIZE / 2
        
        light_color = RELIEF_COLOR_LIGHT_RED if color == RED else RELIEF_COLOR_LIGHT_YELLOW
        dark_color = RELIEF_COLOR_DARK_RED if color == RED else RELIEF_COLOR_DARK_YELLOW
        
        # Ombre foncée
        self.canvas.create_oval(x - RADIUS, y - RADIUS,
                                x + RADIUS, y + RADIUS,
                                fill=dark_color, outline="")
        
        # Cercle principal
        self.canvas.create_oval(x - RADIUS, y - RADIUS,
                                x + RADIUS, y + RADIUS,
                                fill=color, outline="")

        # Cercle avec relief
        self.canvas.create_oval(x - RADIUS, y - RADIUS,
                                x + RADIUS, y + RADIUS,
                                fill=light_color, outline="")
        
        # Ajout du chiffre "4" au centre du jeton
        self.canvas.create_text(x, y + 2, text="4", font=("Arial", 50, "bold"), fill=color)
        self.canvas.create_text(x + 2, y + 4, text="4", font=("Arial", 50, "bold"), fill=dark_color)


    def on_click(self, event):
        if self.game_over or self.is_animating:
            return

        col = int(event.x / CELL_SIZE)
        row = self.get_next_open_row(col)
        
        if row is not None:
            self.is_animating = True
            self.board[row][col] = self.turn
            self.canvas.unbind("<Button-1>")
            self.animate_drop(row, col)

    def animate_drop(self, final_row, col, current_y=0):
        self.canvas.delete("animating_token")
        
        color = RED if self.turn == PLAYER_1 else YELLOW
        x_center = col * CELL_SIZE + CELL_SIZE / 2
        
        self.current_drop_token = self.canvas.create_oval(x_center - RADIUS, current_y - RADIUS,
                                                          x_center + RADIUS, current_y + RADIUS,
                                                          fill=color, outline=color, tags="animating_token")
        
        target_y = final_row * CELL_SIZE + CELL_SIZE / 2
        
        if current_y < target_y:
            new_y = current_y + ANIMATION_SPEED
            self.master.after(10, self.animate_drop, final_row, col, new_y)
        else:
            self.canvas.delete("animating_token")
            self.draw_relief_circle(col, final_row, color)
            self.is_animating = False
            self.check_game_state()
            self.canvas.bind("<Button-1>", self.on_click)

    def animate_victory(self, winning_line, step=0):
        if step >= 10:
            return

        self.canvas.delete("victory_anim")
        for r, c in winning_line:
            x = c * CELL_SIZE + CELL_SIZE / 2
            y = r * CELL_SIZE + CELL_SIZE / 2
            
            if step % 2 == 0:
                self.canvas.create_oval(x - RADIUS, y - RADIUS, x + RADIUS, y + RADIUS,
                                        fill=VICTORY_COLOR, outline="", tags="victory_anim")
            else:
                player_color = RED if self.turn == PLAYER_1 else YELLOW
                self.canvas.create_oval(x - RADIUS, y - RADIUS, x + RADIUS, y + RADIUS,
                                        fill=player_color, outline="", tags="victory_anim")

        self.master.after(200, self.animate_victory, winning_line, step + 1)

    def check_game_state(self):
        winning_line = self.find_win(self.board, self.turn)
        if winning_line:
            self.game_over = True
            winner_text = "Joueur 1 (Rouge) a gagné !" if self.turn == PLAYER_1 else "Joueur 2 (Jaune) a gagné !"
            self.result_label.config(text=winner_text, fg=RED if self.turn == PLAYER_1 else YELLOW)
            self.info_label.config(text="Partie terminée !")
            self.animate_victory(winning_line)
        elif self.is_board_full():
            self.game_over = True
            self.result_label.config(text="Match nul !", fg=self.style["info_fg"])
            self.info_label.config(text="Partie terminée !")
        else:
            self.turn = PLAYER_2 if self.turn == PLAYER_1 else PLAYER_1
            info_text = "C'est au tour de Joueur 1 (Rouge)" if self.turn == PLAYER_1 else "C'est au tour de Joueur 2 (Jaune)"
            self.info_label.config(text=info_text)
            
            if self.is_ai_game and self.turn == AI_PLAYER and not self.game_over:
                self.master.after(500, self.ai_turn)

    def ai_turn(self):
        col = self.get_ai_move(self.board, AI_PLAYER)
        row = self.get_next_open_row(col)
        self.board[row][col] = self.turn
        self.is_animating = True
        self.canvas.unbind("<Button-1>")
        self.animate_drop(row, col)

    def get_ai_move(self, board, player):
        available_cols = [c for c in range(COLS) if self.get_next_open_row_static(board, c) is not None]
        if not available_cols:
            return None
        
        best_score = -math.inf
        best_col = random.choice(available_cols)

        for col in available_cols:
            temp_board = [row[:] for row in board]
            row = self.get_next_open_row_static(temp_board, col)
            temp_board[row][col] = player
            score = self.minimax(temp_board, 5, -math.inf, math.inf, False)
            if score > best_score:
                best_score = score
                best_col = col
        return best_col

    def minimax(self, board, depth, alpha, beta, is_maximizing_player):
        if self.find_win(board, AI_PLAYER):
            return 1000000
        elif self.find_win(board, PLAYER_1):
            return -1000000
        elif self.is_board_full_static(board) or depth == 0:
            return self.score_position(board, AI_PLAYER)

        if is_maximizing_player:
            value = -math.inf
            available_cols = [c for c in range(COLS) if self.get_next_open_row_static(board, c) is not None]
            for col in available_cols:
                row = self.get_next_open_row_static(board, col)
                temp_board = [row[:] for row in board]
                temp_board[row][col] = AI_PLAYER
                new_score = self.minimax(temp_board, depth - 1, alpha, beta, False)
                value = max(value, new_score)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = math.inf
            available_cols = [c for c in range(COLS) if self.get_next_open_row_static(board, c) is not None]
            for col in available_cols:
                row = self.get_next_open_row_static(board, col)
                temp_board = [row[:] for row in board]
                temp_board[row][col] = PLAYER_1
                new_score = self.minimax(temp_board, depth - 1, alpha, beta, True)
                value = min(value, new_score)
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value
    
    def score_position(self, board, player):
        score = 0
        opponent = PLAYER_1 if player == AI_PLAYER else AI_PLAYER
        for r in range(ROWS):
            for c in range(COLS - 3):
                window = [board[r][c+i] for i in range(4)]
                score += self.evaluate_window(window, player, opponent)
        for c in range(COLS):
            for r in range(ROWS - 3):
                window = [board[r+i][c] for i in range(4)]
                score += self.evaluate_window(window, player, opponent)
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [board[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window, player, opponent)
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                window = [board[r-i][c+i] for i in range(4)]
                score += self.evaluate_window(window, player, opponent)
        return score

    def evaluate_window(self, window, player, opponent):
        score = 0
        if window.count(player) == 4:
            score += 100
        elif window.count(player) == 3 and window.count(0) == 1:
            score += 5
        elif window.count(player) == 2 and window.count(0) == 2:
            score += 2
        
        if window.count(opponent) == 3 and window.count(0) == 1:
            score -= 4
        return score

    def find_win(self, board, player):
        for c in range(COLS - 3):
            for r in range(ROWS):
                if all(board[r][c+i] == player for i in range(4)):
                    return [(r, c+i) for i in range(4)]
        for c in range(COLS):
            for r in range(ROWS - 3):
                if all(board[r+i][c] == player for i in range(4)):
                    return [(r+i, c) for i in range(4)]
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                if all(board[r+i][c+i] == player for i in range(4)):
                    return [(r+i, c+i) for i in range(4)]
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                if all(board[r-i][c+i] == player for i in range(4)):
                    return [(r-i, c+i) for i in range(4)]
        return None
    
    def get_next_open_row(self, col):
        for r in range(ROWS - 1, -1, -1):
            if self.board[r][col] == 0:
                return r
        return None

    def get_next_open_row_static(self, board, col):
        for r in range(ROWS - 1, -1, -1):
            if board[r][col] == 0:
                return r
        return None

    def is_board_full(self):
        return all(self.board[0][c] != 0 for c in range(COLS))

    def is_board_full_static(self, board):
        return all(board[0][c] != 0 for c in range(COLS))

    def reset_game(self):
        self.setup_game(self.is_ai_game)

if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectFourGUI(root)
    root.mainloop()