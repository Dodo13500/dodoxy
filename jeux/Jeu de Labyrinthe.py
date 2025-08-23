import tkinter as tk
import random
import time

# --- Constants for the game ---
WALL_COLOR = "#2c3e50"
PATH_COLOR = "#ecf0f1"
PLAYER_COLOR = "#3498db"
FINISH_COLOR = "#2ecc71"
CELL_SIZE = 30

# --- Menu Class ---
class Menu(tk.Frame):
    """
    Class for the main menu of the game.
    """
    def __init__(self, master, launch_game_callback):
        super().__init__(master, bg="#34495e")
        self.pack(expand=True, fill="both")
        self.launch_game_callback = launch_game_callback

        title_label = tk.Label(self, text="Le Labyrinthe Pro", font=("Helvetica", 36, "bold"), bg="#34495e", fg="#ecf0f1")
        title_label.pack(pady=50)

        subtitle_label = tk.Label(self, text="Choisissez votre difficulté :", font=("Arial", 18), bg="#34495e", fg="#ecf0f1")
        subtitle_label.pack(pady=20)

        # Difficulty buttons
        difficulties = [
            ("Facile", "#2ecc71", 10),
            ("Normal", "#f1c40f", 20),
            ("Difficile", "#e74c3c", 30)
        ]

        for text, color, size in difficulties:
            button = tk.Button(self, text=text, font=("Arial", 16, "bold"),
                               command=lambda s=size: self.launch_game_callback(s),
                               bg=color, fg="white", bd=0, relief=tk.RAISED,
                               activebackground=color, activeforeground="white",
                               width=15, height=2)
            button.pack(pady=10)

# --- Class for the Maze Game ---
class MazeGame(tk.Frame):
    """
    Main class for the Maze Game with a modern interface.
    """
    def __init__(self, master, maze_size):
        super().__init__(master, bg="#34495e")
        self.pack(expand=True, fill="both")

        # Game state variables
        self.rows = maze_size
        self.cols = maze_size
        self.maze = []
        self.player_pos = None
        self.finish_pos = None
        self.start_time = None
        self.timer_running = False
        self.master = master

        self.create_widgets()
        self.generate_new_maze()
        
    def adapt_window_size(self):
        """
        Adapts the window size to the maze dimensions.
        """
        window_width = self.cols * CELL_SIZE + 40  # Add some padding
        window_height = self.rows * CELL_SIZE + 100 # Add some padding for the timer
        self.master.geometry(f"{window_width}x{window_height}")
        self.canvas.config(width=self.cols * CELL_SIZE, height=self.rows * CELL_SIZE)

    def create_widgets(self):
        """
        Creates all the user interface elements.
        """
        # Game statistics frame
        stats_frame = tk.Frame(self, bg="#34495e")
        stats_frame.pack(pady=5)
        self.timer_label = tk.Label(stats_frame, text="Temps: 0s", font=("Arial", 16), bg="#34495e", fg="#f1c40f")
        self.timer_label.pack(side=tk.LEFT, padx=20)

        # Canvas for the maze drawing
        self.canvas = tk.Canvas(self, width=self.cols * CELL_SIZE, height=self.rows * CELL_SIZE, bg="#ecf0f1", bd=0, highlightthickness=0)
        self.canvas.pack(pady=20)
        
        # Bind arrow keys for player movement
        self.master.bind("<Up>", self.move_player)
        self.master.bind("<Down>", self.move_player)
        self.master.bind("<Left>", self.move_player)
        self.master.bind("<Right>", self.move_player)

    def generate_new_maze(self):
        """
        Generates a new maze using a depth-first search algorithm.
        
        This algorithm ensures the maze is solvable and has a single path from start to finish.
        The dimensions are also ensured to be odd for clean wall and path generation.
        """
        # Ensure dimensions are odd for a clean maze generation
        rows = (self.rows // 2) * 2 + 1
        cols = (self.cols // 2) * 2 + 1
        self.rows = rows
        self.cols = cols
        
        # Adapt window size after setting the maze dimensions
        self.adapt_window_size()

        # Initialize maze with all walls
        self.maze = [[1] * self.cols for _ in range(self.rows)]
        
        # Use a list for the stack
        stack = []
        
        # Start at a random cell (must be odd for the algorithm to work)
        start_cell = (1, 1)
        stack.append(start_cell)
        self.maze[1][1] = 0
        
        while stack:
            current_row, current_col = stack[-1]
            
            neighbors = []
            # Check for unvisited neighbors
            possible_moves = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            random.shuffle(possible_moves)
            
            for dr, dc in possible_moves:
                next_row, next_col = current_row + dr, current_col + dc
                if 0 < next_row < self.rows and 0 < next_col < self.cols and self.maze[next_row][next_col] == 1:
                    neighbors.append((next_row, next_col))
            
            if neighbors:
                next_row, next_col = random.choice(neighbors)
                # Carve a path to the new cell
                wall_row, wall_col = current_row + (next_row - current_row) // 2, current_col + (next_col - current_col) // 2
                self.maze[wall_row][wall_col] = 0
                self.maze[next_row][next_col] = 0
                stack.append((next_row, next_col))
            else:
                stack.pop()
        
        # Set start and finish positions
        self.player_pos = (1, 1)
        self.finish_pos = (self.rows - 2, self.cols - 2)
        
        # Reset timer
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

        self.draw_maze()

    def draw_maze(self):
        """
        Draws the maze on the canvas.
        """
        self.canvas.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                color = WALL_COLOR if self.maze[r][c] == 1 else PATH_COLOR
                self.canvas.create_rectangle(c * CELL_SIZE, r * CELL_SIZE, (c + 1) * CELL_SIZE, (r + 1) * CELL_SIZE, fill=color, outline=color)

        # Draw player
        player_x, player_y = self.player_pos
        self.canvas.create_rectangle(player_y * CELL_SIZE, player_x * CELL_SIZE, (player_y + 1) * CELL_SIZE, (player_x + 1) * CELL_SIZE, fill=PLAYER_COLOR, outline=PLAYER_COLOR, tags="player")

        # Draw finish line
        finish_x, finish_y = self.finish_pos
        self.canvas.create_rectangle(finish_y * CELL_SIZE, finish_x * CELL_SIZE, (finish_y + 1) * CELL_SIZE, (finish_x + 1) * CELL_SIZE, fill=FINISH_COLOR, outline=FINISH_COLOR)

    def move_player(self, event):
        """
        Moves the player based on key presses.
        
        This function now includes a check to prevent the player from moving
        out of the maze boundaries.
        """
        if not self.timer_running:
            return
            
        current_row, current_col = self.player_pos
        new_row, new_col = current_row, current_col

        if event.keysym == "Up":
            new_row -= 1
        elif event.keysym == "Down":
            new_row += 1
        elif event.keysym == "Left":
            new_col -= 1
        elif event.keysym == "Right":
            new_col += 1

        # Check for out-of-bounds movement and if the new position is a path
        if 0 <= new_row < self.rows and 0 <= new_col < self.cols and self.maze[new_row][new_col] == 0:
            self.player_pos = (new_row, new_col)
            self.draw_player()
            self.check_win()

    def draw_player(self):
        """
        Draws the player at their current position.
        """
        self.canvas.delete("player")
        player_x, player_y = self.player_pos
        self.canvas.create_rectangle(player_y * CELL_SIZE, player_x * CELL_SIZE, (player_y + 1) * CELL_SIZE, (player_x + 1) * CELL_SIZE, fill=PLAYER_COLOR, outline=PLAYER_COLOR, tags="player")
        
    def update_timer(self):
        """
        Updates the timer display.
        """
        if self.timer_running:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Temps: {elapsed_time}s")
            self.after(1000, self.update_timer)

    def check_win(self):
        """
        Checks if the player has reached the finish line.
        """
        if self.player_pos == self.finish_pos:
            self.timer_running = False
            elapsed_time = int(time.time() - self.start_time)
            win_message = f"Bravo ! Vous avez terminé le labyrinthe en {elapsed_time} secondes.\n" \
                          f"Voulez-vous recommencer ?"
            self.show_end_screen(win_message)
            
    def show_end_screen(self, message):
        """
        Shows the end screen with the final message and a button to return to the menu.
        """
        end_screen = tk.Toplevel(self.master, bg="#34495e")
        end_screen.title("Partie Terminée")
        end_screen.geometry("400x200")
        end_screen.resizable(False, False)
        
        tk.Label(end_screen, text=message, font=("Arial", 16, "bold"), bg="#34495e", fg="#ecf0f1").pack(pady=20)
        
        def return_to_menu():
            end_screen.destroy()
            self.destroy()
            app.show_menu()

        tk.Button(end_screen, text="Retour au menu", command=return_to_menu, font=("Arial", 12), bg="#7f8c8d", fg="white", bd=0, relief=tk.FLAT).pack(pady=10)

# --- Main Application Class ---
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Le Labyrinthe Pro")
        self.geometry("800x600")
        self.resizable(False, False)
        self.configure(bg="#34495e")
        
        self.current_frame = None
        self.show_menu()
        
    def show_menu(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = Menu(self, self.start_game)

    def start_game(self, maze_size):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = MazeGame(self, maze_size)

# Run the application
if __name__ == "__main__":
    app = Application()
    app.mainloop()
