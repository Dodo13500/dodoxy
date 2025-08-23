import pygame
import random
import os

# Initialisation de Pygame
pygame.init()

# --- CONSTANTES DE JEU ---
# Taille de la fenêtre
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
# Taille d'un bloc de jeu (pour le serpent et la nourriture)
BLOCK_SIZE = 20
# Vitesse du jeu (plus la valeur est petite, plus c'est rapide)
GAME_SPEED = 100

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 197, 94)  # Tailwind green-500
DARK_GREEN = (21, 128, 61)  # Tailwind green-600
RED = (239, 68, 68)    # Tailwind red-500
GRAY = (75, 85, 99)    # Tailwind gray-600

# Création de la fenêtre de jeu
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Moderne")

# --- CLASSES DE JEU ---

class Snake:
    """Class representing the snake."""
    def __init__(self):
        # The snake's body is a list of coordinates
        self.body = [(15, 15), (14, 15), (13, 15)]
        self.direction = "right"
        self.is_growing = False

    def move(self):
        """Moves the snake's body."""
        head_x, head_y = self.body[0]
        new_head = (0, 0)

        if self.direction == "up":
            new_head = (head_x, head_y - 1)
        elif self.direction == "down":
            new_head = (head_x, head_y + 1)
        elif self.direction == "left":
            new_head = (head_x - 1, head_y)
        elif self.direction == "right":
            new_head = (head_x + 1, head_y)

        # Add new head and remove tail if not growing
        self.body.insert(0, new_head)
        if not self.is_growing:
            self.body.pop()
        else:
            self.is_growing = False

    def change_direction(self, new_dir):
        """Changes the snake's direction, preventing reverse movement."""
        if new_dir == "up" and self.direction != "down":
            self.direction = "up"
        elif new_dir == "down" and self.direction != "up":
            self.direction = "down"
        elif new_dir == "left" and self.direction != "right":
            self.direction = "left"
        elif new_dir == "right" and self.direction != "left":
            self.direction = "right"

    def grow(self):
        """Sets the snake to grow on the next move."""
        self.is_growing = True

    def check_collision(self):
        """Checks for collision with walls or its own body."""
        head_x, head_y = self.body[0]
        # Wall collision
        if head_x < 0 or head_x >= SCREEN_WIDTH // BLOCK_SIZE or head_y < 0 or head_y >= SCREEN_HEIGHT // BLOCK_SIZE:
            return True
        # Body collision (check if head is in the rest of the body)
        if self.body[0] in self.body[1:]:
            return True
        return False
    
    def reset(self):
        """Resets the snake to its initial state."""
        self.body = [(15, 15), (14, 15), (13, 15)]
        self.direction = "right"
        self.is_growing = False

class Food:
    """Class representing the food."""
    def __init__(self):
        self.position = self.get_random_position()
    
    def get_random_position(self):
        """Generates a random position for the food."""
        x = random.randint(0, SCREEN_WIDTH // BLOCK_SIZE - 1)
        y = random.randint(0, SCREEN_HEIGHT // BLOCK_SIZE - 1)
        return (x, y)
    
    def relocate(self, snake_body):
        """Relocates the food, ensuring it doesn't spawn on the snake."""
        new_pos = self.get_random_position()
        while new_pos in snake_body:
            new_pos = self.get_random_position()
        self.position = new_pos

# --- FONCTIONS D'AFFICHAGE ---

def draw_grid():
    """Draws the background grid (optional, can be commented out)."""
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
            rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_snake(snake_body):
    """Draws the snake on the screen."""
    for segment in snake_body:
        rect = pygame.Rect(segment[0] * BLOCK_SIZE, segment[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(screen, GREEN, rect)

def draw_food(food_pos):
    """Draws the food on the screen."""
    rect = pygame.Rect(food_pos[0] * BLOCK_SIZE, food_pos[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(screen, RED, rect)
    
def display_text(text, font_size, color, x, y):
    """Utility function to display text on the screen."""
    font = pygame.font.SysFont('Inter', font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_game_over_screen(score, high_score):
    """Draws the game over screen with final score and a replay button."""
    screen.fill(BLACK)
    
    display_text("GAME OVER", 60, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 80)
    display_text(f"Score: {score}", 40, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 20)
    display_text(f"Meilleur Score: {high_score}", 30, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30)

    # Draw a "Rejouer" button
    button_rect = pygame.Rect(SCREEN_WIDTH / 2 - 80, SCREEN_HEIGHT / 2 + 100, 160, 50)
    pygame.draw.rect(screen, GREEN, button_rect, border_radius=10)
    display_text("Rejouer", 30, BLACK, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 125)
    
    pygame.display.flip()
    return button_rect

# --- BOUCLE PRINCIPALE DU JEU ---

def main():
    """Main game loop."""
    snake = Snake()
    food = Food()
    score = 0
    high_score = 0
    
    # Define the high score file path
    SCORE_FOLDER = "scores"
    HIGH_SCORE_FILE = os.path.join(SCORE_FOLDER, "snake_high_score.txt")
    
    # Create the score directory if it doesn't exist
    if not os.path.exists(SCORE_FOLDER):
        os.makedirs(SCORE_FOLDER)

    # Load high score from a file
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            high_score = int(f.read())
    except (FileNotFoundError, ValueError):
        high_score = 0
    
    # Game states
    running = True
    game_state = "playing" # "playing", "game_over"

    # Pygame clock for consistent game speed
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Event handling based on game state
            if game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        snake.change_direction("up")
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction("down")
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction("left")
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction("right")
            elif game_state == "game_over":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    # Check if the replay button was clicked
                    if button_rect.collidepoint(x, y):
                        # Reset game state
                        snake.reset()
                        food.relocate(snake.body)
                        score = 0
                        game_state = "playing"

        if game_state == "playing":
            snake.move()
            
            # Check for collisions
            if snake.check_collision():
                game_state = "game_over"
                if score > high_score:
                    high_score = score
                    # Save new high score to a file
                    with open(HIGH_SCORE_FILE, "w") as f:
                        f.write(str(high_score))
            
            # Check for food
            if snake.body[0] == food.position:
                snake.grow()
                food.relocate(snake.body)
                score += 10
            
            # Drawing on the screen
            screen.fill(BLACK)
            draw_grid() # Optional grid
            draw_snake(snake.body)
            draw_food(food.position)
            
            # Display score
            display_text(f"Score: {score}", 30, WHITE, 60, 20)
            display_text(f"Meilleur Score: {high_score}", 30, WHITE, SCREEN_WIDTH - 120, 20)
            
            pygame.display.flip()

        elif game_state == "game_over":
            button_rect = draw_game_over_screen(score, high_score)
        
        # Control game speed
        clock.tick(10) # 10 frames per second is a good speed for this game

    pygame.quit()

if __name__ == "__main__":
    main()
