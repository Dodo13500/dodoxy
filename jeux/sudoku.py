# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import random
import time
import copy
import ttkbootstrap as ttk
import threading
from ttkbootstrap.constants import *


class SudokuCell(ttk.Frame):
    """Widget personnalisé pour une seule case de Sudoku, gérant la valeur principale et les notes."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pack_propagate(False)

        self.main_value = 0
        self.notes = set()
        self.is_fixed = False

        # Label pour la valeur principale
        self.main_label = ttk.Label(self, text="", font=("Segoe UI", 24, "bold"), anchor="center")

        # Frame pour les notes
        self.notes_frame = ttk.Frame(self)
        self.note_labels = {}
        for i in range(1, 10):
            row, col = (i - 1) // 3, (i - 1) % 3
            self.notes_frame.grid_rowconfigure(row, weight=1)
            self.notes_frame.grid_columnconfigure(col, weight=1)
            lbl = ttk.Label(self.notes_frame, text=str(i), font=("Segoe UI", 8), anchor="center")
            lbl.grid(row=row, column=col, sticky="nsew")
            self.note_labels[i] = lbl

    def set_fixed_value(self, value):
        """Définit une valeur fixe (chiffre de départ)."""
        self.main_value = value
        self.is_fixed = True
        self.main_label.config(text=str(value), bootstyle="secondary")
        self.show_main_value()

    def set_user_value(self, value): # Removed bootstyle here, it will be set by _update_styles_and_validation
        """Définit une valeur entrée par l'utilisateur."""
        if self.is_fixed:
            return
        self.main_value = value
        self.notes.clear()
        self.main_label.config(text=str(value) if value else "") # No bootstyle here
        self.show_main_value()

    def clear(self):
        """Efface la case (valeur et notes)."""
        if self.is_fixed:
            return
        self.main_value = 0
        self.notes.clear()
        self.main_label.pack_forget()
        self.notes_frame.pack_forget()

    def toggle_note(self, note_value):
        """Ajoute ou retire une note."""
        if self.is_fixed or self.main_value:
            return
        if note_value in self.notes:
            self.notes.remove(note_value)
        else:
            self.notes.add(note_value)
        self.show_notes()

    def show_main_value(self):
        """Affiche la valeur principale et cache les notes."""
        self.notes_frame.pack_forget()
        self.main_label.pack(fill=BOTH, expand=True)

    def show_notes(self):
        """Affiche les notes et cache la valeur principale."""
        self.main_label.pack_forget()
        for i in range(1, 10):
            self.note_labels[i].config(text=str(i) if i in self.notes else "")
        self.notes_frame.pack(fill=BOTH, expand=True)


class SudokuGame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=15)
        self.master = master
        self.pack(fill=BOTH, expand=YES)
        self.active_frame = None

        # Couleurs du thème pour une utilisation cohérente
        self.style = ttk.Style.get_instance()
        # Agrandir la police pour les boutons de difficulté en configurant
        # directement les styles de ttkbootstrap. C'est la bonne méthode.
        button_font = ("Segoe UI", 16, "bold")
        for color in ['success', 'info', 'warning', 'danger']:
            self.style.configure(f'{color}.TButton', font=button_font)
        self.highlight_color = self.style.colors.light
        self.selected_highlight_color = self.style.colors.info
        # Lier les événements clavier à la fenêtre principale pour une capture globale
        self.master.bind("<Key>", self._on_key_press)
        self._show_main_menu()

    def _clear_frame(self):
        """Détruit le cadre actif pour afficher le suivant."""
        if self.active_frame:
            self.active_frame.destroy()
        self.active_frame = ttk.Frame(self)
        self.active_frame.pack(fill=BOTH, expand=True)

    def _show_main_menu(self):
        """Affiche le menu principal pour choisir la difficulté."""
        self._clear_frame()

        title = ttk.Label(self.active_frame, text="Sudoku Pro", font=("Segoe UI Black", 52), bootstyle="primary")
        title.pack(pady=(50, 30))

        desc = ttk.Label(self.active_frame, text="Choisissez votre niveau de difficulté", font=("Segoe UI", 14))
        desc.pack(pady=(0, 60))

        buttons_frame = ttk.Frame(self.active_frame)
        buttons_frame.pack(pady=20, fill=X, padx=150)

        self.difficulty_map = {
            "Facile": (40, SUCCESS), # Keep 40 cells
            "Moyen": (32, INFO),    # Keep 32 cells
            "Difficile": (26, WARNING), # Keep 26 cells
            "Expert": (22, DANGER)  # Keep 22 cells
        }

        for diff, (count, style) in self.difficulty_map.items():
            btn = ttk.Button(
                buttons_frame,
                text=diff,
                bootstyle=style,
                command=lambda d=diff: self._start_game(d)
            )
            btn.pack(fill=X, pady=12, ipady=15)

    def _start_game(self, difficulty_name):
        """Initialise et affiche l'interface de jeu."""
        self._clear_frame()
        self.difficulty = difficulty_name

        # --- Initialisation des variables de jeu ---
        self.cells = {}
        self.board = [[0] * 9 for _ in range(9)]
        self.solution = None
        self.start_time = None
        self.timer_running = False
        self.selected_cell_coords = None
        self.notes_mode = False
        self.history = []  # Pour la fonction Annuler

        # --- Création des widgets de jeu ---
        self.create_game_widgets()
        self.new_game()

    def create_game_widgets(self):
        """Crée tous les éléments de l'interface de jeu."""
        game_frame = self.active_frame
        game_frame.focus_set()  # Pour recevoir les événements clavier

        # --- Cadre de contrôle (haut) ---
        top_frame = ttk.Frame(game_frame)
        top_frame.pack(fill=X, pady=(0, 10))

        ttk.Button(top_frame, text="❮ Menu", command=self._show_main_menu, bootstyle=LINK).pack(side=LEFT, padx=5)
        self.difficulty_label = ttk.Label(top_frame, text=self.difficulty, font=("Segoe UI", 14, "bold"))
        self.difficulty_label.pack(side=LEFT, padx=10)
        ttk.Button(top_frame, text="Nouveau Jeu", command=self.new_game, bootstyle=SUCCESS).pack(side=LEFT, padx=5)

        self.timer_label = ttk.Label(top_frame, text="00:00:00", font=("Segoe UI", 14, "bold"))
        self.timer_label.pack(side=RIGHT, padx=5)

        # --- Cadre de la grille (centre) ---
        self.board_frame = ttk.Frame(game_frame, bootstyle=SECONDARY, padding=5) # bootstyle was SECONDARY
        self.board_frame.pack(expand=True)

        for r in range(9):
            for c in range(9):
                cell = SudokuCell(self.board_frame, width=60, height=60, borderwidth=1, relief="solid")
                cell.grid(row=r, column=c)
                # Lier le clic à la cellule elle-même, qui attrapera les clics sur ses enfants
                cell.bind("<Button-1>", lambda e, r=r, c=c: self.on_cell_click(r, c))
                for widget in cell.winfo_children():
                    widget.bind("<Button-1>", lambda e, r=r, c=c: self.on_cell_click(r, c))
                    for sub_widget in widget.winfo_children():
                        sub_widget.bind("<Button-1>", lambda e, r=r, c=c: self.on_cell_click(r, c))

                self.cells[(r, c)] = cell

                padx, pady = (0, 0), (0, 0)
                if (c + 1) % 3 == 0 and c < 8: padx = (0, 5)
                if (r + 1) % 3 == 0 and r < 8: pady = (0, 5)
                cell.grid_configure(padx=padx, pady=pady)

        # --- Cadre des contrôles (bas) ---
        self.controls_container = ttk.Frame(game_frame)
        self.controls_container.pack(pady=20)

        # Pavé numérique
        numpad_frame = ttk.Frame(self.controls_container)
        numpad_frame.pack(pady=(0, 15))
        for i in range(1, 10):
            btn = ttk.Button(numpad_frame, text=str(i), width=4, bootstyle=SECONDARY,
                             command=lambda n=i: self.on_numpad_click(n))
            btn.pack(side=LEFT, padx=3, ipady=8)

        # Outils
        tools_frame = ttk.Frame(self.controls_container)
        tools_frame.pack()
        self.undo_button = ttk.Button(tools_frame, text="Annuler (Ctrl+Z)", command=self.on_undo_click, bootstyle=OUTLINE+SECONDARY, state=DISABLED)
        self.undo_button.pack(side=LEFT, padx=5)
        self.eraser_button = ttk.Button(tools_frame, text="Gomme", command=self.on_eraser_click, bootstyle=OUTLINE+SECONDARY)
        self.eraser_button.pack(side=LEFT, padx=5)
        self.notes_button = ttk.Checkbutton(tools_frame, text="Notes (N)", command=self.on_notes_toggle, bootstyle=OUTLINE+TOOLBUTTON)
        self.notes_button.pack(side=LEFT, padx=5)
        self.hint_button = ttk.Button(tools_frame, text="Indice", command=self.get_hint, bootstyle=OUTLINE+INFO)
        self.hint_button.pack(side=LEFT, padx=5)
        ttk.Button(tools_frame, text="Résoudre", command=self.solve_board_ui, bootstyle=OUTLINE+DANGER).pack(side=LEFT, padx=5)

        # --- Barre de statut (tout en bas) ---
        self.status_label = ttk.Label(game_frame, text="Bienvenue !", font=("Segoe UI", 10, "italic"))
        self.status_label.pack(side=BOTTOM, fill=X, pady=(10, 0), padx=10)

    def set_status(self, message, style="default"):
        """Met à jour le message de la barre de statut."""
        self.status_label.config(text=message, bootstyle=style)

    # --- Gestion des actions utilisateur ---

    def on_cell_click(self, r, c):
        """Gère le clic sur une cellule de la grille."""
        self.selected_cell_coords = (r, c)
        self._update_styles_and_validation()
        self.set_status(f"Cellule ({r+1}, {c+1}) sélectionnée.")

    def _update_styles_and_validation(self):
        """Met à jour le surlignage et la validation de la grille."""
        if not self.selected_cell_coords:
            return

        sel_r, sel_c = self.selected_cell_coords

        # 1. Réinitialiser toutes les cellules et labels
        for r_idx in range(9):
            for c_idx in range(9):
                cell = self.cells[(r_idx, c_idx)]
                cell.config(bootstyle="default")
                if not cell.is_fixed:
                    cell.main_label.config(bootstyle="default")

        # 2. Surligner la ligne, la colonne et le bloc
        start_row, start_col = 3 * (sel_r // 3), 3 * (sel_c // 3)
        for i in range(9):
            self.cells[(sel_r, i)].config(bootstyle="light")
            self.cells[(i, sel_c)].config(bootstyle="light")
            block_r, block_c = start_row + i // 3, start_col + i % 3
            self.cells[(block_r, block_c)].config(bootstyle="light")

        # 3. Surligner les cellules avec le même numéro
        selected_cell = self.cells[(sel_r, sel_c)]
        if selected_cell.main_value != 0:
            for r_idx in range(9):
                for c_idx in range(9):
                    if self.cells[(r_idx, c_idx)].main_value == selected_cell.main_value:
                        self.cells[(r_idx, c_idx)].config(bootstyle=self.selected_highlight_color)

        # 4. Surligner la cellule sélectionnée en dernier
        selected_cell.config(bootstyle="primary")

        # 5. Appliquer la validation des conflits
        self.validate_board_ui_state()

    def on_numpad_click(self, num):
        """Gère le clic sur un bouton du pavé numérique."""
        if not self.selected_cell_coords:
            self.set_status("Veuillez d'abord sélectionner une cellule.", style=WARNING)
            return

        r, c = self.selected_cell_coords
        cell = self.cells[(r, c)]

        if cell.is_fixed:
            return

        if self.notes_mode:
            self._push_to_history(r, c, cell.main_value, cell.notes.copy())
            cell.toggle_note(num)
        else:
            if cell.main_value != num:
                self._push_to_history(r, c, cell.main_value, cell.notes.copy())
                cell.set_user_value(num) # No bootstyle here
                self._update_styles_and_validation()

    def on_eraser_click(self):
        """Efface la valeur ou les notes de la cellule sélectionnée."""
        if not self.selected_cell_coords:
            self.set_status("Veuillez d'abord sélectionner une cellule.", style=WARNING)
            return
        
        r, c = self.selected_cell_coords
        cell = self.cells[(r, c)]
        if not cell.is_fixed and (cell.main_value != 0 or cell.notes):
            self._push_to_history(r, c, cell.main_value, cell.notes.copy())
            cell.clear()
            self._update_styles_and_validation()

    def on_notes_toggle(self):
        """Active ou désactive le mode notes."""
        self.notes_mode = self.notes_button.instate(['selected'])
        if self.notes_mode:
            self.set_status("Mode Notes activé. Cliquez sur les chiffres pour ajouter/retirer des notes.", style=INFO)
        else:
            self.set_status("Mode Notes désactivé.", style=INFO)

    # --- Game Logic (Génération et Résolution) ---

    def find_empty(self, board):
        """Trouve une case vide (représentée par 0) dans la grille."""
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    return (r, c)
        return None

    def is_valid(self, board, num, pos):
        """Vérifie si un nombre est valide dans une case donnée."""
        r, c = pos
        # Vérifier la ligne
        if num in board[r]:
            return False
        # Vérifier la colonne
        if num in [board[i][c] for i in range(9)]:
            return False
        # Vérifier le bloc 3x3
        box_x, box_y = c // 3, r // 3
        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                if board[i][j] == num:
                    return False
        return True

    def solve_sudoku(self, board):
        """Résout la grille de Sudoku en utilisant le backtracking (récursif)."""
        find = self.find_empty(board)
        if not find:
            return True  # La grille est pleine, donc résolue
        else:
            row, col = find

        nums = list(range(1, 10))
        random.shuffle(nums)
        for i in nums:
            if self.is_valid(board, i, (row, col)):
                board[row][col] = i
                if self.solve_sudoku(board):
                    return True
                board[row][col] = 0  # Backtrack
        return False

    def count_solutions(self, board):
        """Compte le nombre de solutions possibles pour une grille (s'arrête si > 1)."""
        find = self.find_empty(board)
        if not find:
            return 1  # Une solution trouvée

        row, col = find
        count = 0
        for i in range(1, 10):
            if self.is_valid(board, i, (row, col)):
                board[row][col] = i
                count += self.count_solutions(board)
                board[row][col] = 0  # Backtrack

                # Optimisation : si on a déjà trouvé plus d'une solution, inutile de continuer
                if count > 1:
                    return 2
        return count

    def generate_puzzle(self):
        """Génère une nouvelle grille de Sudoku avec une solution unique garantie."""
        board = [[0] * 9 for _ in range(9)]
        self.solve_sudoku(board)
        
        # Créer une copie pour la solution avant de retirer des chiffres
        self.solution = [row[:] for row in board]

        # Tenter de retirer des chiffres tout en garantissant une solution unique
        squares = list(range(81))
        random.shuffle(squares)
        
        temp_board = [row[:] for row in board] # Travailler sur une copie

        # Récupérer le nombre cible de cellules à conserver en fonction de la difficulté
        # self.difficulty_map[self.difficulty][0] contient le nombre de cellules à garder
        cells_to_keep = self.difficulty_map[self.difficulty][0] 
        cells_removed = 0
        
        # Itérer à travers les cases mélangées et essayer de retirer des chiffres
        for square_index in squares:
            r, c = divmod(square_index, 9)
            
            if temp_board[r][c] != 0: # Essayer de retirer seulement si la cellule n'est pas déjà vide
                backup = temp_board[r][c]
                temp_board[r][c] = 0 # Retirer temporairement le chiffre
                
                # Créer une copie profonde pour count_solutions afin d'éviter les modifications inattendues
                if self.count_solutions([row[:] for row in temp_board]) == 1: # Vérifier si la solution reste unique
                    cells_removed += 1
                else:
                    temp_board[r][c] = backup # Si non unique, restaurer le chiffre
            
            if (81 - cells_removed) <= cells_to_keep: # Arrêter si suffisamment de cellules ont été retirées
                break
        
        return temp_board

    def _on_key_press(self, event):
        """Gère les entrées clavier pour une expérience de jeu plus fluide."""
        if not self.selected_cell_coords:
            return

        r, c = self.selected_cell_coords
        new_r, new_c = r, c

        if event.keysym in ("Up", "w"):
            new_r = (r - 1) % 9
        elif event.keysym in ("Down", "s"):
            new_r = (r + 1) % 9
        elif event.keysym in ("Left", "a"):
            new_c = (c - 1) % 9
        elif event.keysym in ("Right", "d"):
            new_c = (c + 1) % 9
        elif event.keysym.isdigit() and event.keysym != '0':
            self.on_numpad_click(int(event.keysym))
        elif event.keysym in ("BackSpace", "Delete"):
            self.on_eraser_click()
        elif event.keysym.lower() == 'n':
            self.notes_button.invoke()  # Bascule le mode notes
        elif event.keysym.lower() == 'z' and event.state & 4:  # Ctrl+Z pour Annuler
            self.on_undo_click()

        if (new_r, new_c) != (r, c):
            self.on_cell_click(new_r, new_c)

    def new_game(self):
        """Lance la génération d'une nouvelle grille dans un thread séparé pour ne pas geler l'UI."""
        self.difficulty_label.config(text=self.difficulty)
        self.set_status("Génération d'une nouvelle grille...", style="info")
        
        # Désactiver les contrôles pendant la génération
        for widget in self.controls_container.winfo_children():
            for btn in widget.winfo_children():
                btn.config(state=DISABLED)
        self.update_idletasks()

        def _generate_worker():
            """Tâche exécutée en arrière-plan."""
            new_board = self.generate_puzzle()

            def _update_ui_after_generation():
                """Mise à jour de l'UI une fois la grille prête."""
                self.board = new_board
                self.selected_cell_coords = None
                self.history.clear()
                self.update_board_ui()
                self.start_timer()
                self.set_status("Nouvelle partie commencée. Bonne chance !")

                # Réactiver les contrôles
                for widget in self.controls_container.winfo_children():
                    for btn in widget.winfo_children():
                        btn.config(state=NORMAL)
                # L'historique est vide, donc le bouton Annuler doit rester désactivé
                self.undo_button.config(state=DISABLED)

            # Planifier la mise à jour de l'UI sur le thread principal
            self.after(0, _update_ui_after_generation)

        # Lancer le worker dans un thread
        threading.Thread(target=_generate_worker, daemon=True).start()

    def update_board_ui(self):
        for r in range(9):
            for c in range(9):
                cell = self.cells[(r, c)]
                cell.clear() # Efface la valeur et les notes
                cell.is_fixed = False
                cell.configure(bootstyle="default")
                cell.main_label.config(bootstyle="default")

                if self.board[r][c] != 0:
                    cell.set_fixed_value(self.board[r][c])
        # Appliquer les styles initiaux et la validation après le chargement
        if self.selected_cell_coords:
            self._update_styles_and_validation()
        else:
            self.validate_board_ui_state() # Just validate if no cell is selected

    def _is_cell_valid_in_ui(self, r, c):
        """Vérifie si le chiffre dans la cellule (r, c) est valide par rapport aux autres cellules."""
        cell = self.cells.get((r, c))
        if not cell or not cell.main_value:
            return True  # Les cellules vides n'ont pas de conflits

        value = cell.main_value

        # Vérifie les conflits dans la ligne
        for j in range(9):
            if j != c and self.cells[(r, j)].main_value == value:
                return False

        # Vérifie les conflits dans la colonne
        for i in range(9):
            if i != r and self.cells[(i, c)].main_value == value:
                return False

        # Vérifie les conflits dans le bloc 3x3
        start_row, start_col = 3 * (r // 3), 3 * (c // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if (i, j) != (r, c) and self.cells[(i, j)].main_value == value:
                    return False

        return True

    def validate_board_ui_state(self):
        """Recolore les cellules en conflit et vérifie si la grille est gagnée."""
        is_board_full = True
        conflicts = set()

        # Identifier tous les conflits
        for r_check in range(9):
            for c_check in range(9):
                cell = self.cells[(r_check, c_check)]
                if not cell.main_value:
                    is_board_full = False
                    continue
                if not cell.is_fixed and not self._is_cell_valid_in_ui(r_check, c_check):
                    conflicts.add((r_check, c_check))

        # Appliquer les styles de conflit par-dessus le surlignage
        for r in range(9):
            for c in range(9):
                cell = self.cells[(r, c)]
                if cell.is_fixed or not cell.main_value:
                    continue

                if (r, c) in conflicts:
                    cell.main_label.config(bootstyle="danger")

        if is_board_full and not conflicts:
            self.check_solution()

    def check_solution(self):
        user_board = self.get_board_from_ui()
        if all(all(cell != 0 for cell in row) for row in user_board) and user_board == self.solution:
            self.stop_timer()
            self.set_status(f"Félicitations ! Grille résolue en {self.timer_label.cget('text')}", style=SUCCESS)
            messagebox.showinfo("Gagné !", "Vous avez résolu le Sudoku !")
            for cell in self.cells.values():
                if not cell.is_fixed:
                    cell.main_label.config(bootstyle="success")
        else:
            self.set_status("La solution est incorrecte ou incomplète. Continuez !", style=WARNING)
            messagebox.showwarning("Incorrect", "La grille contient des erreurs ou n'est pas complète.")

    def get_hint(self):
        empty_cells = []
        for r in range(9):
            for c in range(9):
                if not self.cells[(r, c)].main_value and not self.cells[(r, c)].is_fixed:
                    empty_cells.append((r, c))

        if not empty_cells:
            self.set_status("La grille est déjà pleine.", style=INFO)
            return

        r, c = random.choice(empty_cells)
        correct_value = self.solution[r][c]
        cell = self.cells[(r, c)]

        self._push_to_history(r, c, cell.main_value, cell.notes.copy())
        cell.set_user_value(correct_value) # No bootstyle here
        self._update_styles_and_validation()
        self.set_status(f"Indice donné pour la case ({r+1}, {c+1}).", style=INFO)

    def solve_board_ui(self):
        if not messagebox.askyesno("Résoudre ?", "Voulez-vous vraiment afficher la solution ?"):
            return
        self.stop_timer()
        for r in range(9):
            for c in range(9):
                cell = self.cells[(r, c)]
                if not cell.is_fixed:
                    cell.set_user_value(self.solution[r][c]) # No bootstyle here
        self.set_status("Solution affichée.", style="info")
        self._update_styles_and_validation() # Update styles after solving
    # --- Fonctions du Timer ---

    def start_timer(self):
        """Démarre le chronomètre du jeu."""
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self._update_timer()

    def stop_timer(self):
        """Arrête le chronomètre."""
        self.timer_running = False

    def _update_timer(self):
        """Met à jour l'affichage du chronomètre chaque seconde."""
        if self.timer_running:
            elapsed = time.time() - self.start_time
            mins, secs = divmod(elapsed, 60)
            hours, mins = divmod(mins, 60)
            self.timer_label.config(text=f"{int(hours):02}:{int(mins):02}:{int(secs):02}")
            self.after(1000, self._update_timer)

    # --- Gestion de l'état et de l'historique ---

    def get_board_from_ui(self):
        """Récupère l'état actuel de la grille depuis l'interface utilisateur."""
        board = [[0] * 9 for _ in range(9)]
        for r in range(9):
            for c in range(9):
                board[r][c] = self.cells[(r, c)].main_value
        return board

    def _push_to_history(self, r, c, old_value, old_notes):
        """Ajoute une action à l'historique pour la fonction Annuler."""
        self.history.append({'coords': (r, c), 'old_value': old_value, 'old_notes': old_notes})
        self.undo_button.config(state=NORMAL)

    def on_undo_click(self):
        """Annule la dernière action de l'utilisateur."""
        if not self.history:
            return # Correction de l'IndentationError

        last_action = self.history.pop()
        r, c = last_action['coords']
        cell = self.cells[(r, c)]

        # Restaurer l'état précédent
        cell.main_value = last_action['old_value']
        cell.notes = last_action['old_notes']

        # Mettre à jour l'affichage de la cellule
        if cell.main_value:
            cell.main_label.config(text=str(cell.main_value))
            cell.show_main_value()
        elif cell.notes:
            cell.show_notes()
        else:
            # Si la cellule est vide après l'annulation
            cell.main_label.pack_forget()
            cell.notes_frame.pack_forget() # Correction du bug logique
        
        self.on_cell_click(r, c) # Re-sélectionner la cellule pour la cohérence
        self._update_styles_and_validation()

        if not self.history:
            self.undo_button.config(state=DISABLED)


if __name__ == "__main__":
    # Utiliser un thème plus sombre et une fenêtre plus grande pour un look pro
    root = ttk.Window(themename="superhero")
    root.title("Sudoku Pro")
    root.geometry("800x900") # Taille de fenêtre plus confortable
    app = SudokuGame(root)
    root.mainloop()
