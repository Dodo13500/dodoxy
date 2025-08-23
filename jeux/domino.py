# -*- coding: utf-8 -*-
import tkinter as tk
import random
import time

# Définitions des constantes
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

TILE_WIDTH = 120
TILE_HEIGHT = 60
TILE_GAP = 10
DOT_RADIUS = 5

# Couleurs pour l'interface
BG_COLOR = "#2C3E50"  # Bleu foncé
GAME_BOARD_COLOR = "#1D5420" # Vert pour le tapis
TEXT_COLOR = "#ECF0F1" # Blanc cassé
BUTTON_BG = "#34495e" # Gris bleu foncé
BUTTON_ACTIVE_BG = "#5e7790" # Gris bleu clair
TILE_BG = "#FDFEFE" # Blanc
TILE_DOT = "#2C3E50" # Bleu foncé
ACCENT_COLOR = "#3498DB" # Bleu clair

class DominoGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Jeu de Dominos")
        self.master.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.master.resizable(False, False)
        
        self.is_ai_game = False
        self.player_hand = []
        self.ai_hand = []
        self.boneyard = []
        self.board = []
        self.turn = 1
        self.game_over = False
        self.is_animating = False
        self.board_offset_x = 0

        self.style = {
            "bg_color": BG_COLOR,
            "info_font": ("Arial", 16),
            "info_fg": TEXT_COLOR,
            "result_font": ("Arial", 24, "bold"),
            "btn_bg": BUTTON_BG,
            "btn_active_bg": BUTTON_ACTIVE_BG,
        }
        
        self.main_menu()

    def create_domino_set(self):
        dominoes = []
        for i in range(7):
            for j in range(i, 7):
                dominoes.append((i, j))
        random.shuffle(dominoes)
        return dominoes

    def deal_dominoes(self, dominoes):
        self.player_hand = sorted(dominoes[:7])
        self.ai_hand = sorted(dominoes[7:14])
        self.boneyard = dominoes[14:]

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.clear_window()
        self.master.config(bg=self.style["bg_color"])

        title_label = tk.Label(self.master, text="Jeu de Dominos",
                               font=("Arial", 48, "bold"), bg=self.style["bg_color"], fg=self.style["info_fg"])
        title_label.pack(pady=100)

        start_button = tk.Button(self.master, text="Jouer", font=self.style["info_font"],
                               bg=self.style["btn_bg"], fg=self.style["info_fg"], relief="flat",
                               activebackground=self.style["btn_active_bg"],
                               command=lambda: self.setup_game(True))
        start_button.pack(pady=10, ipadx=55, ipady=15)

    def setup_game(self, is_ai_game):
        self.is_ai_game = is_ai_game
        self.game_over = False
        self.is_animating = False
        self.board = []
        self.board_offset_x = 0
        self.turn = 1
        self.deal_dominoes(self.create_domino_set())
        
        self.create_game_widgets()
        self.find_first_move()

    def find_first_move(self):
        first_player = None
        highest_double = -1
        first_domino = None

        for domino in self.player_hand + self.ai_hand:
            if domino[0] == domino[1] and domino[0] > highest_double:
                highest_double = domino[0]
                first_domino = domino
                first_player = "player" if domino in self.player_hand else "ai"

        if first_domino:
            self.board.append(first_domino)
            if first_player == "player":
                self.player_hand.remove(first_domino)
                self.turn = 2
                self.info_label.config(text="Joueur 1 commence avec le double le plus élevé.")
            else:
                self.ai_hand.remove(first_domino)
                self.turn = 1
                self.info_label.config(text="L'IA commence avec le double le plus élevé.")
        else:
            self.info_label.config(text="Pas de double, la partie commence. Joueur 1 commence.")
            self.turn = 1
        
        self.update_gui()
        if self.turn == 2 and self.is_ai_game:
            self.master.after(1000, self.ai_turn)

    def create_game_widgets(self):
        self.clear_window()
        self.master.config(bg=self.style["bg_color"])

        self.info_label = tk.Label(self.master, text="",
                                   font=self.style["info_font"], bg=self.style["bg_color"], fg=self.style["info_fg"])
        self.info_label.pack(pady=10)

        self.canvas = tk.Canvas(self.master, width=WINDOW_WIDTH - 40, height=WINDOW_HEIGHT - 350, bg=GAME_BOARD_COLOR, highlightthickness=0)
        self.canvas.pack(pady=20)
        
        info_frame = tk.Frame(self.master, bg=self.style["bg_color"])
        info_frame.pack(fill=tk.X)

        self.boneyard_label = tk.Label(info_frame, text="Pioche : " + str(len(self.boneyard)), font=("Arial", 12, "bold"),
                                       bg=self.style["bg_color"], fg=self.style["info_fg"])
        self.boneyard_label.pack(side=tk.LEFT, padx=20)
        
        self.ai_hand_label = tk.Label(info_frame, text="Main de l'IA : " + str(len(self.ai_hand)), font=("Arial", 12, "bold"),
                                       bg=self.style["bg_color"], fg=self.style["info_fg"])
        self.ai_hand_label.pack(side=tk.RIGHT, padx=20)

        player_hand_label = tk.Label(self.master, text="Votre main", font=("Arial", 12, "bold"),
                                     bg=self.style["bg_color"], fg=self.style["info_fg"])
        player_hand_label.pack(pady=(20, 5))
        
        self.player_hand_frame = tk.Frame(self.master, bg=self.style["bg_color"])
        self.player_hand_frame.pack()
        
        control_frame = tk.Frame(self.master, bg=self.style["bg_color"])
        control_frame.pack(pady=10)
        
        draw_button = tk.Button(control_frame, text="Piocher un domino", font=self.style["info_font"],
                                bg=self.style["btn_bg"], fg=self.style["info_fg"], relief="flat",
                                activebackground=self.style["btn_active_bg"],
                                command=self.draw_tile)
        draw_button.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=10)
        
        menu_button = tk.Button(control_frame, text="Menu Principal", font=self.style["info_font"],
                                bg=self.style["btn_bg"], fg=self.style["info_fg"], relief="flat",
                                activebackground=self.style["btn_active_bg"],
                                command=self.main_menu)
        menu_button.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=10)

        self.update_gui()

    def update_gui(self):
        self.canvas.delete("all")
        self.boneyard_label.config(text="Pioche : " + str(len(self.boneyard)))
        self.ai_hand_label.config(text="Main de l'IA : " + str(len(self.ai_hand)))
        
        if self.game_over:
            pass
        elif self.turn == 1:
            self.info_label.config(text="C'est à vous de jouer (Joueur 1)")
        else:
            self.info_label.config(text="C'est au tour de l'IA (Joueur 2)")
        
        total_width = len(self.board) * (TILE_WIDTH + TILE_GAP)
        max_board_width = self.canvas.winfo_width()
        
        if total_width > max_board_width:
            self.board_offset_x = (max_board_width - total_width) / 2
        else:
            self.board_offset_x = (max_board_width - total_width) / 2
            
        y_pos = self.canvas.winfo_height() / 2 - TILE_HEIGHT / 2
        
        current_x = self.board_offset_x
        for domino in self.board:
            self.draw_domino(self.canvas, current_x, y_pos, domino[0], domino[1])
            current_x += TILE_WIDTH + TILE_GAP
            
        for widget in self.player_hand_frame.winfo_children():
            widget.destroy()
            
        for i, domino in enumerate(self.player_hand):
            tile_canvas = tk.Canvas(self.player_hand_frame, width=TILE_WIDTH + 10, height=TILE_HEIGHT + 10, bg=self.style["bg_color"], highlightthickness=0)
            tile_canvas.pack(side=tk.LEFT, padx=5)
            self.draw_domino(tile_canvas, 5, 5, domino[0], domino[1])
            
            tile_canvas.bind("<Button-1>", lambda e, d=domino: self.animate_and_play_domino(d, tile_canvas, from_player=True))
            tile_canvas.bind("<Button-3>", lambda e, d=domino: self.rotate_domino(d))

    def rotate_domino(self, domino):
        if self.game_over or self.is_animating:
            return
        
        try:
            index = self.player_hand.index(domino)
            self.player_hand[index] = (domino[1], domino[0])
            self.update_gui()
        except ValueError:
            pass

    def animate_and_play_domino(self, domino, tile_canvas, from_player):
        if self.is_animating or self.game_over:
            return
        
        valid_move = self.check_valid_move(domino)
        if not valid_move:
            self.info_label.config(text="Mouvement invalide. Essayez un autre domino.")
            return

        self.is_animating = True
        
        start_x = self.master.winfo_x() + tile_canvas.winfo_x() + (tile_canvas.winfo_width() - TILE_WIDTH) / 2
        start_y = self.master.winfo_y() + tile_canvas.winfo_y() + (tile_canvas.winfo_height() - TILE_HEIGHT) / 2

        board_y = self.canvas.winfo_y() + self.canvas.winfo_height() / 2 - TILE_HEIGHT / 2
        
        if not self.board or domino[0] == self.board[-1][1] or domino[1] == self.board[-1][1]:
            end_x = self.board_offset_x + len(self.board) * (TILE_WIDTH + TILE_GAP)
        else:
            end_x = self.board_offset_x - (TILE_WIDTH + TILE_GAP)
            
        end_y = board_y
        
        domino_id = self.canvas.create_rectangle(start_x, start_y, start_x + TILE_WIDTH, start_y + TILE_HEIGHT, fill=TILE_BG, outline="black", width=2)
        
        for i in range(20):
            x = start_x + (end_x - start_x) * (i/20)
            y = start_y + (end_y - start_y) * (i/20)
            self.canvas.coords(domino_id, x, y, x + TILE_WIDTH, y + TILE_HEIGHT)
            self.master.update()
            time.sleep(0.01)

        self.canvas.delete(domino_id)
        
        self.play_domino(domino)
        self.is_animating = False

    def check_valid_move(self, domino):
        if not self.board:
            return True
            
        left_end = self.board[0][0]
        right_end = self.board[-1][1]
        
        return domino[0] == left_end or domino[1] == left_end or domino[0] == right_end or domino[1] == right_end
    
    def play_domino(self, domino):
        if not self.board:
            self.board.append(domino)
            if domino in self.player_hand: self.player_hand.remove(domino)
            else: self.ai_hand.remove(domino)
        else:
            left_end = self.board[0][0]
            right_end = self.board[-1][1]
            
            if domino[0] == left_end:
                self.board.insert(0, domino)
                if domino in self.player_hand: self.player_hand.remove(domino)
                else: self.ai_hand.remove(domino)
            elif domino[1] == left_end:
                self.board.insert(0, (domino[1], domino[0]))
                if domino in self.player_hand: self.player_hand.remove(domino)
                else: self.ai_hand.remove(domino)
            elif domino[0] == right_end:
                self.board.append(domino)
                if domino in self.player_hand: self.player_hand.remove(domino)
                else: self.ai_hand.remove(domino)
            elif domino[1] == right_end:
                self.board.append((domino[1], domino[0]))
                if domino in self.player_hand: self.player_hand.remove(domino)
                else: self.ai_hand.remove(domino)

        self.check_game_state()
        if not self.game_over:
            self.turn = 2 if self.turn == 1 else 1
            self.update_gui()
            if self.turn == 2 and self.is_ai_game:
                self.master.after(1000, self.ai_turn)
    
    def ai_turn(self):
        if self.game_over or self.turn != 2 or self.is_animating:
            return

        self.info_label.config(text="L'IA réfléchit...")
        self.master.update()
        
        playable_domino = self.find_playable_domino_for_ai(self.ai_hand)

        if playable_domino:
            domino, side = playable_domino
            self.ai_hand.remove(domino)
            
            if side == "left":
                if domino[1] == self.board[0][0]:
                    domino_to_play = (domino[1], domino[0])
                else:
                    domino_to_play = domino
                self.board.insert(0, domino_to_play)
            else:
                if domino[0] == self.board[-1][1]:
                    domino_to_play = domino
                else:
                    domino_to_play = (domino[1], domino[0])
                self.board.append(domino_to_play)
            
            self.check_game_state()
            self.turn = 1
            self.update_gui()
        else:
            self.ai_draw_tile()

    def find_playable_domino_for_ai(self, hand):
        if not self.board:
            return (random.choice(hand), "right") if hand else None

        left_end = self.board[0][0]
        right_end = self.board[-1][1]
        
        playable_dominoes = []
        for domino in hand:
            if domino[0] == left_end or domino[1] == left_end:
                playable_dominoes.append((domino, "left"))
            if domino[0] == right_end or domino[1] == right_end:
                playable_dominoes.append((domino, "right"))
        
        if not playable_dominoes:
            return None
        
        playable_dominoes.sort(key=lambda x: sum(x[0]), reverse=True)
        return playable_dominoes[0]

    def ai_draw_tile(self):
        if not self.boneyard:
            self.info_label.config(text="L'IA ne peut pas jouer ni piocher. Passe son tour.")
        else:
            new_domino = self.boneyard.pop(0)
            self.ai_hand.append(new_domino)
            self.info_label.config(text="L'IA a pioché un domino.")
        
        self.master.after(1000, self.end_ai_turn)

    def end_ai_turn(self):
        playable = self.find_playable_domino_for_ai(self.ai_hand)
        if playable:
            self.ai_turn()
        else:
            self.turn = 1
            self.update_gui()

    def draw_tile(self):
        if self.game_over or self.turn != 1 or self.is_animating:
            return
        
        playable = self.find_playable_domino_for_ai(self.player_hand)
        if playable:
            self.info_label.config(text="Vous pouvez jouer ! Pas besoin de piocher.")
            return

        if not self.boneyard:
            self.info_label.config(text="Pas de dominos à piocher. Vous passez votre tour.")
            self.turn = 2
            self.update_gui()
            if self.is_ai_game:
                self.master.after(1000, self.ai_turn)
            return

        new_domino = self.boneyard.pop(0)
        self.player_hand.append(new_domino)
        self.info_label.config(text="Vous avez pioché un domino.")
        self.update_gui()

    def check_game_state(self):
        if not self.player_hand:
            self.info_label.config(text="Vous avez gagné !")
            self.game_over = True
            return
        
        if not self.ai_hand:
            self.info_label.config(text="L'IA a gagné !")
            self.game_over = True
            return

        player_can_play = self.find_playable_domino_for_ai(self.player_hand)
        ai_can_play = self.find_playable_domino_for_ai(self.ai_hand)
        
        if not player_can_play and not ai_can_play and not self.boneyard:
            player_points = sum(sum(domino) for domino in self.player_hand)
            ai_points = sum(sum(domino) for domino in self.ai_hand)

            if player_points < ai_points:
                self.info_label.config(text=f"Partie bloquée ! Vous avez gagné avec {player_points} points.")
            elif ai_points < player_points:
                self.info_label.config(text=f"Partie bloquée ! L'IA a gagné avec {ai_points} points.")
            else:
                self.info_label.config(text="Partie bloquée ! Égalité.")
            
            self.game_over = True
            return
    
    def draw_domino(self, canvas, x, y, value1, value2, tag=""):
        canvas.create_rectangle(x + 5, y + 5, x + TILE_WIDTH + 5, y + TILE_HEIGHT + 5, fill="#a0a0a0", outline="", tags=tag)
        canvas.create_rectangle(x, y, x + TILE_WIDTH, y + TILE_HEIGHT, fill=TILE_BG, outline="black", width=2, tags=tag)
        
        mid_x = x + TILE_WIDTH / 2
        canvas.create_line(mid_x, y, mid_x, y + TILE_HEIGHT, fill="black", width=2, tags=tag)
        
        self.draw_dots(canvas, x, y, value1, tag)
        self.draw_dots(canvas, mid_x, y, value2, tag)
        
    def draw_dots(self, canvas, start_x, start_y, value, tag=""):
        dot_positions = {
            0: [], 1: [(0, 0)],
            2: [(-1, -1), (1, 1)],
            3: [(-1, -1), (0, 0), (1, 1)],
            4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
            5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
            6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]
        }
        
        for pos_x, pos_y in dot_positions.get(value, []):
            x = start_x + TILE_WIDTH / 4 + pos_x * TILE_GAP
            y = start_y + TILE_HEIGHT / 2 + pos_y * TILE_GAP
            canvas.create_oval(x - DOT_RADIUS, y - DOT_RADIUS,
                               x + DOT_RADIUS, y + DOT_RADIUS,
                               fill=TILE_DOT, outline=TILE_DOT, tags=tag)

if __name__ == "__main__":
    root = tk.Tk()
    app = DominoGUI(root)
    root.mainloop()