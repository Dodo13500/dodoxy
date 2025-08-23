import pygame
import random
import sys
import math

# Initialisation de Pygame
# Le module de mixage est désactivé pour éviter les erreurs de compatibilité et de lancement.
pygame.init()

# --- Constantes et Configuration ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
FPS = 60
CARD_WIDTH, CARD_HEIGHT = 90, 135
CARD_SPACING = 15
DECK_POS = (SCREEN_WIDTH // 2 - CARD_WIDTH - CARD_SPACING - 10, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2)
DISCARD_POS = (SCREEN_WIDTH // 2 + CARD_SPACING + 10, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2)

# Couleurs (plus proches du jeu UNO original)
UNO_RED = (202, 30, 26)
UNO_GREEN = (0, 150, 64)
UNO_BLUE = (0, 114, 188)
UNO_YELLOW = (255, 222, 0)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (50, 50, 50)
BG_COLOR = (25, 25, 25)
BUTTON_COLOR = (45, 45, 45)
BUTTON_HOVER_COLOR = (75, 75, 75)
MESSAGE_BG_COLOR = (25, 25, 25, 200)

COLOR_MAP = {
    "red": UNO_RED,
    "green": UNO_GREEN,
    "blue": UNO_BLUE,
    "yellow": UNO_YELLOW,
    "black": BLACK
}

# Charger les polices
try:
    font_large = pygame.font.SysFont("Arial", 60, bold=True)
    font_medium = pygame.font.SysFont("Arial", 40, bold=True)
    font_small = pygame.font.SysFont("Arial", 28)
    font_card_value = pygame.font.SysFont("Arial", 50, bold=True)
    font_card_corner = pygame.font.SysFont("Arial", 16, bold=True)
except:
    # Utilisation d'une police de secours en cas d'échec
    font_large = pygame.font.SysFont(None, 60, bold=True)
    font_medium = pygame.font.SysFont(None, 40, bold=True)
    font_small = pygame.font.SysFont(None, 28)
    font_card_value = pygame.font.SysFont(None, 50, bold=True)
    font_card_corner = pygame.font.SysFont(None, 16, bold=True)

# Classe Carte
class Card:
    """Représente une seule carte UNO avec une couleur, une valeur et des propriétés visuelles."""
    def __init__(self, color, value):
        self.color = color
        self.value = value
        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        self.is_wild = (value == "wild" or value == "+4")

    def draw(self, surface, x, y):
        """Dessine la carte sur la surface à la position et l'angle donnés."""
        self.rect.topleft = (x, y)
        card_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        
        card_color = COLOR_MAP.get(self.color, BLACK)
        text_color = WHITE if self.is_wild else BLACK

        # Dessiner le corps de la carte avec les coins arrondis
        pygame.draw.rect(card_surface, card_color, (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=10)
        pygame.draw.rect(card_surface, WHITE, (0, 0, CARD_WIDTH, CARD_HEIGHT), 3, border_radius=10)

        if self.is_wild:
            self.draw_wild_card_design(card_surface)
        else:
            self.draw_card_design(card_surface)
        
        surface.blit(card_surface, self.rect)
    
    def draw_wild_card_design(self, surface):
        """Dessine le design des cartes Wild et +4 avec des couleurs vives et un texte au centre."""
        center_x, center_y = CARD_WIDTH // 2, CARD_HEIGHT // 2
        colors = [UNO_RED, UNO_GREEN, UNO_BLUE, UNO_YELLOW]
        
        # Dessiner les quadrants de couleurs
        pygame.draw.rect(surface, colors[0], (0, 0, center_x, center_y))
        pygame.draw.rect(surface, colors[1], (center_x, 0, center_x, center_y))
        pygame.draw.rect(surface, colors[2], (0, center_y, center_x, center_y))
        pygame.draw.rect(surface, colors[3], (center_x, center_y, center_x, center_y))

        # Dessiner un cercle noir au centre avec un contour blanc
        pygame.draw.circle(surface, BLACK, (center_x, center_y), CARD_WIDTH // 4 + 5)
        pygame.draw.circle(surface, WHITE, (center_x, center_y), CARD_WIDTH // 4 + 5, 3)

        # Dessiner la valeur de la carte au centre
        value_text = self.value.upper()
        if self.value == "wild":
            value_text = "JOKER"
        text_surf = font_card_value.render(value_text, True, WHITE)
        text_rect = text_surf.get_rect(center=(center_x, center_y))
        surface.blit(text_surf, text_rect)

    def draw_card_design(self, surface):
        """Dessine le design des cartes numérotées et des cartes d'action."""
        card_color = COLOR_MAP.get(self.color, BLACK)
        text_color = BLACK

        # Dessiner le symbole central
        if self.value.isdigit():
            text_surf = font_large.render(str(self.value), True, text_color)
            text_rect = text_surf.get_rect(center=(CARD_WIDTH // 2, CARD_HEIGHT // 2))
            surface.blit(text_surf, text_rect)
        elif self.value == "+2":
            text_surf = font_large.render("+2", True, text_color)
            text_rect = text_surf.get_rect(center=(CARD_WIDTH // 2, CARD_HEIGHT // 2))
            surface.blit(text_surf, text_rect)
        elif self.value == "skip":
            self.draw_skip_symbol(surface, text_color, (CARD_WIDTH // 2, CARD_HEIGHT // 2))
        elif self.value == "reverse":
            self.draw_reverse_symbol(surface, text_color, (CARD_WIDTH // 2, CARD_HEIGHT // 2))
            
        # Dessiner les coins avec des valeurs
        self.draw_corner_value(surface, text_color, (10, 10))
        self.draw_corner_value(surface, text_color, (CARD_WIDTH - 10, CARD_HEIGHT - 10), True)

    def draw_corner_value(self, surface, text_color, pos, rotated=False):
        """Dessine la petite valeur de la carte dans un coin."""
        value_text = str(self.value)
        if self.value == "+2": value_text = "+2"
        elif self.value == "skip": value_text = "SAUT"
        elif self.value == "reverse": value_text = "REV"
        
        text_surf = font_card_corner.render(value_text, True, text_color)
        if rotated:
            text_surf = pygame.transform.rotate(text_surf, 180)
        
        text_rect = text_surf.get_rect(center=pos)
        surface.blit(text_surf, text_rect)

    def draw_skip_symbol(self, surface, text_color, center):
        """Dessine le symbole de saut."""
        pygame.draw.line(surface, text_color, (center[0] - 25, center[1] - 15), (center[0] + 25, center[1] - 15), 5)
        pygame.draw.line(surface, text_color, (center[0] - 25, center[1] + 15), (center[0] + 25, center[1] + 15), 5)

    def draw_reverse_symbol(self, surface, text_color, center):
        """Dessine le symbole de flèche inversée."""
        pygame.draw.line(surface, text_color, (center[0] - 20, center[1]), (center[0] + 20, center[1]), 5)
        pygame.draw.polygon(surface, text_color, [(center[0] - 20, center[1]), (center[0] - 10, center[1] - 10), (center[0] - 10, center[1] + 10)])
        pygame.draw.polygon(surface, text_color, [(center[0] + 20, center[1]), (center[0] + 10, center[1] - 10), (center[0] + 10, center[1] + 10)])

    def is_playable(self, top_card, selected_color=None):
        """Vérifie si la carte peut être jouée sur la carte du dessus de la pile de défausse."""
        if self.is_wild:
            return True
        if self.color == top_card.color:
            return True
        if self.value == top_card.value:
            return True
        if top_card.is_wild and self.color == selected_color:
            return True
        return False

# Classe Paquet de cartes
class Deck:
    """Représente le paquet de pioche et la pile de défausse."""
    def __init__(self):
        self.cards = []
        self.discard_pile = []
        self.create_deck()
        random.shuffle(self.cards)

    def create_deck(self):
        """Génère un paquet UNO standard."""
        colors = ["red", "green", "blue", "yellow"]
        values = [str(i) for i in range(10)] + ["skip", "reverse", "+2"]
        wild_cards = ["wild", "+4"]

        self.cards = []
        for color in colors:
            self.cards.append(Card(color, "0"))
            for _ in range(2):
                for value in values:
                    self.cards.append(Card(color, value))
        for _ in range(4):
            for value in wild_cards:
                self.cards.append(Card("black", value))

    def draw_card(self):
        """Pioche une seule carte du paquet. Mélange la pile de défausse si le paquet est vide."""
        if not self.cards:
            self.shuffle_discard_to_deck()
        if self.cards:
            return self.cards.pop()
        return None

    def shuffle_discard_to_deck(self):
        """Déplace toutes les cartes de la pile de défausse vers le paquet et les mélange."""
        if len(self.discard_pile) > 1:
            top_card = self.discard_pile.pop()
            self.cards.extend(self.discard_pile)
            self.discard_pile = [top_card]
            random.shuffle(self.cards)
            
    def get_top_card(self):
        """Retourne la carte du dessus de la pile de défausse sans la retirer."""
        if self.discard_pile:
            return self.discard_pile[-1]
        return None

# Classe Joueur
class Player:
    """Représente un joueur (humain ou IA) avec une main de cartes."""
    def __init__(self, name, is_human=True):
        self.name = name
        self.hand = []
        self.is_human = is_human

    def play_card(self, card_index):
        """Retire une carte de la main du joueur et la retourne."""
        if 0 <= card_index < len(self.hand):
            return self.hand.pop(card_index)
        return None

    def add_card(self, card):
        """Ajoute une carte à la main du joueur."""
        self.hand.append(card)

    def has_playable_card(self, top_card, selected_color=None):
        """Vérifie si le joueur a une carte jouable dans sa main."""
        for card in self.hand:
            if card.is_playable(top_card, selected_color):
                return True
        return False

# Logique du jeu UNO
class UnoGame:
    """Classe principale pour gérer l'état du jeu UNO et l'interface graphique."""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pygame UNO")
        self.clock = pygame.time.Clock()
        self.state = "MENU"
        self.deck = None
        self.players = None
        self.current_player_index = 0
        self.current_player = None
        self.direction = 1
        self.is_game_over = False
        self.wild_color_selection_active = False
        self.message = "Bienvenue à UNO !"
        self.num_bots = 1
        self.game_state = "IDLE"

    def start_game(self, num_bots):
        """Initialise un nouveau jeu avec un nombre de bots donné."""
        self.num_bots = num_bots
        self.deck = Deck()
        self.players = [Player("Vous")] + [Player(f"IA {i+1}", is_human=False) for i in range(num_bots)]
        self.current_player_index = 0
        self.current_player = self.players[self.current_player_index]
        self.direction = 1
        self.is_game_over = False
        self.wild_color_selection_active = False
        self.game_state = "IDLE"
        
        # Distribution initiale
        for player in self.players:
            for _ in range(7):
                card = self.deck.draw_card()
                if card:
                    player.add_card(card)
        
        # Commencer la pile de défausse
        while True:
            first_card = self.deck.draw_card()
            if first_card and not first_card.is_wild and first_card.value not in ["skip", "reverse", "+2"]:
                self.deck.discard_pile.append(first_card)
                break
            elif first_card:
                self.deck.cards.append(first_card)
                random.shuffle(self.deck.cards)
                
        self.top_card = self.deck.get_top_card()
        self.selected_wild_color = self.top_card.color if self.top_card and not self.top_card.is_wild else None
        
        self.game_state = "PLAYER_TURN" if self.players[0].is_human else "AI_TURN"
        self.update_game_message()

    def update_game_message(self):
        """Met à jour le message basé sur l'état du jeu actuel."""
        top_card_value = self.top_card.value if self.top_card else "VIDE"
        top_card_color_name = self.top_card.color if self.top_card and self.top_card.color != "black" else self.selected_wild_color
        top_card_color_fr = {
            "red": "rouge", "green": "vert", "blue": "bleu", "yellow": "jaune", "black": "noir"
        }.get(top_card_color_name, "")
        
        self.message = f"C'est le tour de {self.current_player.name}. Carte du dessus : {top_card_value.upper()} {top_card_color_fr.upper()}."

    def play_card(self, player, card_to_play_index):
        """Gère un joueur qui joue une carte."""
        try:
            card_to_play = player.hand[card_to_play_index]
        except IndexError:
            return False

        top_card = self.deck.get_top_card()
        if not top_card or not card_to_play.is_playable(top_card, self.selected_wild_color):
            if player.is_human:
                self.message = "Cette carte ne peut pas être jouée. Piochez ou passez votre tour."
            return False

        played_card = player.hand.pop(card_to_play_index)
        self.deck.discard_pile.append(played_card)
        self.top_card = played_card
        
        if len(player.hand) == 1:
            self.message = "UNO!"

        return True

    def draw_card_for_player(self, player, count=1):
        """Gère le fait de piocher une carte du paquet pour un joueur donné."""
        for i in range(count):
            drawn_card = self.deck.draw_card()
            if drawn_card:
                player.add_card(drawn_card)

    def handle_special_card(self, card):
        """Applique l'effet des cartes spéciales."""
        if card.value == "skip":
            self.message = f"Le tour de {self.players[self.next_player_index()].name} est sauté !"
            self.current_player_index = (self.current_player_index + 2 * self.direction) % len(self.players)
            self.next_turn()
        elif card.value == "reverse":
            self.direction *= -1
            self.message = "Direction inversée !"
            self.next_turn()
        elif card.value == "+2":
            player_to_draw = self.players[self.next_player_index()]
            self.message = f"{player_to_draw.name} pioche 2 cartes !"
            self.draw_card_for_player(player_to_draw, 2)
            self.current_player_index = (self.current_player_index + self.direction) % len(self.players)
            self.next_turn()
        elif card.value == "+4":
            self.wild_color_selection_active = True
            if self.current_player.is_human:
                self.message = "Sélectionnez une couleur pour le +4."
            else:
                chosen_color = random.choice(["red", "green", "blue", "yellow"])
                self.selected_wild_color = chosen_color
                player_to_draw = self.players[self.next_player_index()]
                self.draw_card_for_player(player_to_draw, 4)
                self.message = f"L'IA a joué un +4 et a choisi {chosen_color.upper()}. {player_to_draw.name} pioche 4 cartes."
                self.next_turn()
        elif card.value == "wild":
            self.wild_color_selection_active = True
            if self.current_player.is_human:
                self.message = "Sélectionnez une couleur pour le Joker."
            else:
                chosen_color = random.choice(["red", "green", "blue", "yellow"])
                self.selected_wild_color = chosen_color
                self.message = f"L'IA a joué un JOKER et a choisi {chosen_color.upper()}."
                self.next_turn()
        else:
             self.next_turn()

    def next_turn(self):
        """Passe le tour au joueur suivant."""
        if self.is_game_over:
            return
        
        self.current_player_index = (self.current_player_index + self.direction) % len(self.players)
            
        self.current_player = self.players[self.current_player_index]
        self.update_game_message()
        self.check_game_over()
        
        if not self.is_game_over:
            if self.current_player.is_human:
                self.game_state = "PLAYER_TURN"
            else:
                self.game_state = "AI_TURN"

    def next_player_index(self):
        """Calcule l'index du joueur suivant en fonction de la direction."""
        return (self.current_player_index + self.direction) % len(self.players)

    def ai_turn(self):
        """Gère le tour du joueur IA."""
        top_card = self.deck.get_top_card()
        
        playable_cards = [c for c in self.current_player.hand if c.is_playable(top_card, self.selected_wild_color)]
        
        if playable_cards:
            card_to_play = random.choice(playable_cards)
            card_index = self.current_player.hand.index(card_to_play)
            if self.play_card(self.current_player, card_index):
                self.game_state = "IDLE"
                self.handle_special_card(card_to_play)
        else:
            self.draw_card_for_player(self.current_player)
            self.message = f"{self.current_player.name} a pioché une carte."
            drawn_card = self.current_player.hand[-1]
            if drawn_card.is_playable(top_card, self.selected_wild_color):
                self.play_card(self.current_player, len(self.current_player.hand) - 1)
            else:
                self.next_turn()
        
        self.game_state = "PLAYER_TURN"

    def check_game_over(self):
        """Vérifie si un joueur a gagné la partie."""
        if not self.current_player.hand:
            self.message = f"{self.current_player.name} gagne la partie !"
            self.is_game_over = True
            
    def reset_game(self):
        """Réinitialise le jeu à son état initial."""
        self.state = "MENU"
        self.message = "Bienvenue à UNO !"
        self.deck = None
        self.players = None
        self.current_player = None
        self.game_state = "IDLE"

    def run(self):
        """Boucle principale du jeu."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.state == "MENU":
                    self.handle_menu_events(event)
                elif self.state == "PLAYER_COUNT_MENU":
                    self.handle_player_count_menu_events(event)
                elif self.state == "GAME":
                    self.handle_game_events(event)

            if self.game_state == "AI_TURN":
                self.ai_turn()
            
            self.draw_screen()
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

    def handle_menu_events(self, event):
        """Gère les événements du menu de démarrage."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            menu_button_rect = self.draw_menu_button()
            if menu_button_rect.collidepoint(event.pos):
                self.state = "PLAYER_COUNT_MENU"

    def handle_player_count_menu_events(self, event):
        """Gère les événements du menu de sélection du nombre de joueurs IA."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(self.draw_player_count_menu()):
                if rect.collidepoint(event.pos):
                    self.start_game(i + 1)
                    self.state = "GAME"
                    break

    def handle_game_events(self, event):
        """Gère les événements du jeu principal."""
        if self.is_game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                reset_button_rect = self.draw_reset_button()
                if reset_button_rect.collidepoint(event.pos):
                    self.reset_game()
            return
        
        if self.game_state == "PLAYER_TURN":
            if event.type == pygame.MOUSEBUTTONDOWN:
                card_played = False
                for i, card in enumerate(self.current_player.hand):
                    if card.rect.collidepoint(event.pos):
                        if self.play_card(self.current_player, i):
                            card_played = True
                            self.handle_special_card(self.top_card)
                            break
                
                deck_rect = pygame.Rect(DECK_POS, (CARD_WIDTH, CARD_HEIGHT))
                if not card_played and deck_rect.collidepoint(event.pos):
                    self.draw_card_for_player(self.current_player)
                    self.message = "Vous avez pioché une carte."
                    drawn_card = self.current_player.hand[-1]
                    if not drawn_card.is_playable(self.top_card, self.selected_wild_color):
                        self.next_turn()
                    else:
                        self.message = "Vous pouvez jouer la carte que vous venez de piocher."

        elif self.game_state == "WILD_SELECTION":
            if event.type == pygame.MOUSEBUTTONDOWN:
                color_options = ["red", "green", "blue", "yellow"]
                for i, color_name in enumerate(color_options):
                    rect = pygame.Rect(SCREEN_WIDTH//2 - 200 + i*100, SCREEN_HEIGHT//2, 80, 80)
                    if rect.collidepoint(event.pos):
                        self.selected_wild_color = color_name
                        self.wild_color_selection_active = False
                        self.update_game_message()
                        self.next_turn()
                        break
    
    def get_hand_positions(self, player, position):
        """Calcule les positions des cartes pour une main donnée."""
        num_cards = len(player.hand)
        positions = []
        if position == "bottom":
            total_hand_width = num_cards * CARD_WIDTH + (num_cards - 1) * CARD_SPACING
            spacing = CARD_SPACING
            if total_hand_width > SCREEN_WIDTH * 0.9:
                max_width = SCREEN_WIDTH * 0.9
                spacing = (max_width - num_cards * CARD_WIDTH) / (num_cards - 1) if num_cards > 1 else 0
                total_hand_width = max_width
            
            start_x = (SCREEN_WIDTH - total_hand_width) // 2
            y_pos = SCREEN_HEIGHT - CARD_HEIGHT - 50
            
            for i in range(num_cards):
                x = start_x + i * (CARD_WIDTH + spacing)
                positions.append((x, y_pos))
        return positions


    def draw_screen(self):
        """Dessine tous les éléments du jeu sur l'écran."""
        self.screen.fill(BG_COLOR)

        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "PLAYER_COUNT_MENU":
            self.draw_player_count_menu()
        elif self.state == "GAME":
            self.draw_header()
            self.draw_deck()
            self.draw_discard_pile()
            
            # Dessiner la main des joueurs
            for i, player in enumerate(self.players):
                if player.is_human:
                    self.draw_hand(player, "bottom")
                else:
                    if self.num_bots == 1:
                        self.draw_hand(player, "top")
                    elif self.num_bots == 2:
                        if i == 1: self.draw_hand(player, "left")
                        if i == 2: self.draw_hand(player, "right")
                    elif self.num_bots == 3:
                        if i == 1: self.draw_hand(player, "left")
                        if i == 2: self.draw_hand(player, "top")
                        if i == 3: self.draw_hand(player, "right")

            self.draw_message_box()

            if self.wild_color_selection_active:
                self.draw_color_selection()
            
            if self.is_game_over:
                self.draw_game_over_screen()
                self.draw_reset_button()


    def draw_menu(self):
        """Dessine l'écran du menu de démarrage."""
        title_surf = font_large.render("Pygame UNO", True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(title_surf, title_rect)
        self.draw_menu_button()

    def draw_menu_button(self):
        """Dessine le bouton du menu et retourne son rect."""
        button_text = font_medium.render("JOUER", True, WHITE)
        button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        button_bg = pygame.Rect(0, 0, button_rect.width + 40, button_rect.height + 20)
        button_bg.center = button_rect.center
        
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER_COLOR if button_bg.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, button_bg, border_radius=10)
        
        self.screen.blit(button_text, button_rect)
        return button_bg

    def draw_player_count_menu(self):
        """Dessine le menu de sélection du nombre de joueurs IA et retourne les rects des boutons."""
        title_surf = font_medium.render("Combien d'adversaires ?", True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(title_surf, title_rect)

        button_rects = []
        for i in range(1, 4):
            button_text = font_medium.render(f"{i} BOT{'S' if i > 1 else ''}", True, WHITE)
            button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50 + i * 80))
            button_bg = pygame.Rect(0, 0, button_rect.width + 40, button_rect.height + 20)
            button_bg.center = button_rect.center
            
            mouse_pos = pygame.mouse.get_pos()
            color = BUTTON_HOVER_COLOR if button_bg.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(self.screen, color, button_bg, border_radius=10)
            self.screen.blit(button_text, button_rect)
            button_rects.append(button_bg)
        
        return button_rects

    def draw_header(self):
        """Dessine les noms des joueurs et l'indicateur de direction du jeu."""
        direction_text = "-->" if self.direction == 1 else "<--"
        direction_surf = font_medium.render(direction_text, True, WHITE)
        self.screen.blit(direction_surf, (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + CARD_HEIGHT // 2 + 10))

        for player in self.players:
            player_name_surf = font_small.render(f"{player.name} ({len(player.hand)} cartes)", True, WHITE)
            if player.is_human:
                self.screen.blit(player_name_surf, (20, SCREEN_HEIGHT - 50))
            else:
                if self.num_bots == 1:
                    ai_name_rect = player_name_surf.get_rect(center=(SCREEN_WIDTH//2, 20))
                    self.screen.blit(player_name_surf, ai_name_rect)
                elif self.num_bots == 2:
                    if player == self.players[1]:
                        self.screen.blit(player_name_surf, (20, SCREEN_HEIGHT//2 - 50))
                    else:
                        self.screen.blit(player_name_surf, (SCREEN_WIDTH - 250, SCREEN_HEIGHT//2 - 50))
                elif self.num_bots == 3:
                    if player == self.players[1]:
                        self.screen.blit(player_name_surf, (20, SCREEN_HEIGHT//2 - 50))
                    elif player == self.players[2]:
                        ai_name_rect = player_name_surf.get_rect(center=(SCREEN_WIDTH//2, 20))
                        self.screen.blit(player_name_surf, ai_name_rect)
                    else:
                        self.screen.blit(player_name_surf, (SCREEN_WIDTH - 250, SCREEN_HEIGHT//2 - 50))

    def draw_card_back(self, surface, x, y):
        """Dessine le dos d'une carte UNO pour les adversaires."""
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(surface, UNO_BLUE, rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, rect, 3, border_radius=10)
        
        uno_text = font_large.render("UNO", True, WHITE)
        uno_rect = uno_text.get_rect(center=rect.center)
        surface.blit(uno_text, uno_rect)


    def draw_deck(self):
        """Dessine la pile de pioche."""
        deck_rect = pygame.Rect(DECK_POS, (CARD_WIDTH, CARD_HEIGHT))
        self.draw_card_back(self.screen, DECK_POS[0], DECK_POS[1])


    def draw_discard_pile(self):
        """Dessine la pile de défausse."""
        if self.deck.discard_pile:
            top_card = self.deck.discard_pile[-1]
            top_card.draw(self.screen, DISCARD_POS[0], DISCARD_POS[1])


    def draw_hand(self, player, position):
        """Dessine la main d'un joueur, en ajustant la position et l'orientation."""
        hand = player.hand
        num_cards = len(hand)
        
        if position == "bottom":
            total_hand_width = num_cards * CARD_WIDTH + (num_cards - 1) * CARD_SPACING
            spacing = CARD_SPACING
            if total_hand_width > SCREEN_WIDTH * 0.9:
                max_width = SCREEN_WIDTH * 0.9
                spacing = (max_width - num_cards * CARD_WIDTH) / (num_cards - 1) if num_cards > 1 else 0
                total_hand_width = max_width
            
            start_x = (SCREEN_WIDTH - total_hand_width) // 2
            y_pos = SCREEN_HEIGHT - CARD_HEIGHT - 50
            
            for i, card in enumerate(hand):
                x = start_x + i * (CARD_WIDTH + spacing)
                card.draw(self.screen, x, y_pos)
                card.rect.topleft = (x, y_pos)

        elif position == "top":
            total_hand_width = num_cards * CARD_WIDTH + (num_cards - 1) * 5
            start_x = (SCREEN_WIDTH - total_hand_width) // 2
            y_pos = 50
            for i in range(num_cards):
                self.draw_card_back(self.screen, start_x + i * (CARD_WIDTH + 5), y_pos)
        
        elif position == "left":
            total_hand_height = num_cards * CARD_WIDTH + (num_cards - 1) * 5
            start_y = (SCREEN_HEIGHT - total_hand_height) // 2
            x_pos = 50
            for i in range(num_cards):
                self.draw_card_back(self.screen, x_pos, start_y + i * (CARD_WIDTH + 5))
        
        elif position == "right":
            total_hand_height = num_cards * CARD_WIDTH + (num_cards - 1) * 5
            start_y = (SCREEN_HEIGHT - total_hand_height) // 2
            x_pos = SCREEN_WIDTH - CARD_HEIGHT - 50
            for i in range(num_cards):
                self.draw_card_back(self.screen, x_pos, start_y + i * (CARD_WIDTH + 5))


    def draw_message_box(self):
        """Dessine la boîte de message du jeu."""
        message_surf = font_small.render(self.message, True, WHITE)
        message_rect = message_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - CARD_HEIGHT - 30))
        
        message_bg = pygame.Surface((message_rect.width + 20, message_rect.height + 10), pygame.SRCALPHA)
        message_bg.fill(MESSAGE_BG_COLOR)
        message_bg_rect = message_bg.get_rect(center=message_rect.center)
        self.screen.blit(message_bg, message_bg_rect)
        
        self.screen.blit(message_surf, message_rect)

    def draw_color_selection(self):
        """Dessine les boutons de sélection de couleur pour une carte joker."""
        colors = [UNO_RED, UNO_GREEN, UNO_BLUE, UNO_YELLOW]
        x_start = SCREEN_WIDTH // 2 - 200
        for i, color in enumerate(colors):
            rect = pygame.Rect(x_start + i * 100, SCREEN_HEIGHT // 2, 80, 80)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)
            
    def draw_game_over_screen(self):
        """Dessine le message de fin de partie."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        message_surf = font_large.render(self.message, True, WHITE)
        message_rect = message_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(message_surf, message_rect)

    def draw_reset_button(self):
        """Dessine le bouton de réinitialisation et retourne son rect."""
        button_text = font_medium.render("Rejouer ?", True, BLACK)
        button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        button_bg = pygame.Rect(0, 0, button_rect.width + 20, button_rect.height + 20)
        button_bg.center = button_rect.center
        pygame.draw.rect(self.screen, WHITE, button_bg, border_radius=10)
        self.screen.blit(button_text, button_rect)
        return button_bg

# Exécuter le jeu
if __name__ == "__main__":
    game = UnoGame()
    game.run()
