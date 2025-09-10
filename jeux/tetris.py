import pygame
import sys
import random

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 800
HAUTEUR = 600
TAILLE_CASE = 30
LARGEUR_GRILLE = 10
HAUTEUR_GRILLE = 20
FPS = 60

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
GRIS = (128, 128, 128)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
BLEU = (0, 0, 255)
JAUNE = (255, 255, 0)
ORANGE = (255, 165, 0)
VIOLET = (128, 0, 128)
CYAN = (0, 255, 255)

# Formes des pièces Tetris
PIECES = [
    # I
    [['.....',
      '..#..',
      '..#..',
      '..#..',
      '..#..'],
     ['.....',
      '.....',
      '####.',
      '.....',
      '.....']],
    
    # O
    [['.....',
      '.....',
      '.##..',
      '.##..',
      '.....']],
    
    # T
    [['.....',
      '.....',
      '.#...',
      '###..',
      '.....'],
     ['.....',
      '.....',
      '.#...',
      '.##..',
      '.#...'],
     ['.....',
      '.....',
      '.....',
      '###..',
      '.#...'],
     ['.....',
      '.....',
      '.#...',
      '##...',
      '.#...']],
    
    # S
    [['.....',
      '.....',
      '.##..',
      '##...',
      '.....'],
     ['.....',
      '.....',
      '.#...',
      '.##..',
      '..#..']],
    
    # Z
    [['.....',
      '.....',
      '##...',
      '.##..',
      '.....'],
     ['.....',
      '.....',
      '..#..',
      '.##..',
      '.#...']],
    
    # J
    [['.....',
      '.....',
      '.#...',
      '.#...',
      '##...'],
     ['.....',
      '.....',
      '.....',
      '#....',
      '###..'],
     ['.....',
      '.....',
      '.##..',
      '.#...',
      '.#...'],
     ['.....',
      '.....',
      '.....',
      '###..',
      '..#..']],
    
    # L
    [['.....',
      '.....',
      '.#...',
      '.#...',
      '.##..'],
     ['.....',
      '.....',
      '.....',
      '###..',
      '#....'],
     ['.....',
      '.....',
      '##...',
      '.#...',
      '.#...'],
     ['.....',
      '.....',
      '.....',
      '..#..',
      '###..']]
]

COULEURS_PIECES = [CYAN, JAUNE, VIOLET, VERT, ROUGE, BLEU, ORANGE]

class Piece:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(PIECES) - 1)
        self.rotation = 0
        self.couleur = COULEURS_PIECES[self.type]
    
    def forme(self):
        return PIECES[self.type][self.rotation]
    
    def tourner(self):
        self.rotation = (self.rotation + 1) % len(PIECES[self.type])

class JeuTetris:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Tetris")
        self.horloge = pygame.time.Clock()
        
        # Grille de jeu
        self.grille = [[NOIR for _ in range(LARGEUR_GRILLE)] for _ in range(HAUTEUR_GRILLE)]
        
        # Pièce actuelle
        self.piece_actuelle = Piece(LARGEUR_GRILLE // 2 - 2, 0)
        
        # Temps de chute
        self.temps_chute = 0
        self.vitesse_chute = 500  # millisecondes
        
        # Score et niveau
        self.score = 0
        self.lignes_completees = 0
        self.niveau = 1
        
        # État du jeu
        self.jeu_termine = False
        
        # Interface
        self.font = pygame.font.Font(None, 36)
        self.font_petit = pygame.font.Font(None, 24)
        
        # Offset pour centrer la grille
        self.offset_x = 50
        self.offset_y = 50
    
    def piece_valide(self, piece, dx=0, dy=0, rotation=None):
        if rotation is None:
            rotation = piece.rotation
        
        forme = PIECES[piece.type][rotation]
        
        for y, ligne in enumerate(forme):
            for x, cellule in enumerate(ligne):
                if cellule == '#':
                    nx = piece.x + x + dx
                    ny = piece.y + y + dy
                    
                    # Vérifier les limites
                    if nx < 0 or nx >= LARGEUR_GRILLE or ny >= HAUTEUR_GRILLE:
                        return False
                    
                    # Vérifier collision avec les pièces existantes
                    if ny >= 0 and self.grille[ny][nx] != NOIR:
                        return False
        
        return True
    
    def placer_piece(self, piece):
        forme = piece.forme()
        
        for y, ligne in enumerate(forme):
            for x, cellule in enumerate(ligne):
                if cellule == '#':
                    nx = piece.x + x
                    ny = piece.y + y
                    if 0 <= ny < HAUTEUR_GRILLE and 0 <= nx < LARGEUR_GRILLE:
                        self.grille[ny][nx] = piece.couleur
    
    def effacer_lignes(self):
        lignes_a_effacer = []
        
        # Trouver les lignes complètes
        for y in range(HAUTEUR_GRILLE):
            if all(cellule != NOIR for cellule in self.grille[y]):
                lignes_a_effacer.append(y)
        
        # Effacer les lignes complètes
        for y in lignes_a_effacer:
            del self.grille[y]
            self.grille.insert(0, [NOIR for _ in range(LARGEUR_GRILLE)])
        
        # Mettre à jour le score
        if lignes_a_effacer:
            self.lignes_completees += len(lignes_a_effacer)
            self.score += len(lignes_a_effacer) * 100 * self.niveau
            self.niveau = self.lignes_completees // 10 + 1
            self.vitesse_chute = max(50, 500 - (self.niveau - 1) * 50)
    
    def nouvelle_piece(self):
        self.piece_actuelle = Piece(LARGEUR_GRILLE // 2 - 2, 0)
        
        # Vérifier si le jeu est terminé
        if not self.piece_valide(self.piece_actuelle):
            self.jeu_termine = True
    
    def dessiner_grille(self):
        # Fond de la grille
        grille_rect = pygame.Rect(self.offset_x, self.offset_y, 
                                LARGEUR_GRILLE * TAILLE_CASE, 
                                HAUTEUR_GRILLE * TAILLE_CASE)
        pygame.draw.rect(self.ecran, GRIS, grille_rect, 2)
        
        # Dessiner les cellules
        for y in range(HAUTEUR_GRILLE):
            for x in range(LARGEUR_GRILLE):
                rect = pygame.Rect(self.offset_x + x * TAILLE_CASE,
                                 self.offset_y + y * TAILLE_CASE,
                                 TAILLE_CASE, TAILLE_CASE)
                
                pygame.draw.rect(self.ecran, self.grille[y][x], rect)
                pygame.draw.rect(self.ecran, BLANC, rect, 1)
    
    def dessiner_piece(self, piece):
        forme = piece.forme()
        
        for y, ligne in enumerate(forme):
            for x, cellule in enumerate(ligne):
                if cellule == '#':
                    rect = pygame.Rect(self.offset_x + (piece.x + x) * TAILLE_CASE,
                                     self.offset_y + (piece.y + y) * TAILLE_CASE,
                                     TAILLE_CASE, TAILLE_CASE)
                    
                    pygame.draw.rect(self.ecran, piece.couleur, rect)
                    pygame.draw.rect(self.ecran, BLANC, rect, 1)
    
    def dessiner_interface(self):
        # Score
        texte_score = self.font.render(f"Score: {self.score}", True, BLANC)
        self.ecran.blit(texte_score, (400, 100))
        
        # Niveau
        texte_niveau = self.font.render(f"Niveau: {self.niveau}", True, BLANC)
        self.ecran.blit(texte_niveau, (400, 140))
        
        # Lignes
        texte_lignes = self.font.render(f"Lignes: {self.lignes_completees}", True, BLANC)
        self.ecran.blit(texte_lignes, (400, 180))
        
        # Instructions
        instructions = [
            "A/D: Déplacer",
            "S: Descendre",
            "W: Tourner",
            "R: Recommencer"
        ]
        
        for i, instruction in enumerate(instructions):
            texte = self.font_petit.render(instruction, True, BLANC)
            self.ecran.blit(texte, (400, 250 + i * 30))
        
        # Game Over
        if self.jeu_termine:
            texte_fin = self.font.render("GAME OVER", True, ROUGE)
            rect_fin = texte_fin.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            self.ecran.blit(texte_fin, rect_fin)
    
    def reinitialiser(self):
        self.grille = [[NOIR for _ in range(LARGEUR_GRILLE)] for _ in range(HAUTEUR_GRILLE)]
        self.piece_actuelle = Piece(LARGEUR_GRILLE // 2 - 2, 0)
        self.temps_chute = 0
        self.vitesse_chute = 500
        self.score = 0
        self.lignes_completees = 0
        self.niveau = 1
        self.jeu_termine = False
    
    def dessiner(self):
        self.ecran.fill(NOIR)
        
        # Grille et pièces
        self.dessiner_grille()
        if not self.jeu_termine:
            self.dessiner_piece(self.piece_actuelle)
        
        # Interface
        self.dessiner_interface()
        
        pygame.display.flip()
    
    def executer(self):
        en_cours = True
        
        while en_cours:
            dt = self.horloge.tick(FPS)
            self.temps_chute += dt
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                
                elif event.type == pygame.KEYDOWN:
                    if not self.jeu_termine:
                        if event.key == pygame.K_a:  # Gauche
                            if self.piece_valide(self.piece_actuelle, dx=-1):
                                self.piece_actuelle.x -= 1
                        
                        elif event.key == pygame.K_d:  # Droite
                            if self.piece_valide(self.piece_actuelle, dx=1):
                                self.piece_actuelle.x += 1
                        
                        elif event.key == pygame.K_s:  # Bas
                            if self.piece_valide(self.piece_actuelle, dy=1):
                                self.piece_actuelle.y += 1
                        
                        elif event.key == pygame.K_w:  # Tourner
                            nouvelle_rotation = (self.piece_actuelle.rotation + 1) % len(PIECES[self.piece_actuelle.type])
                            if self.piece_valide(self.piece_actuelle, rotation=nouvelle_rotation):
                                self.piece_actuelle.rotation = nouvelle_rotation
                    
                    if event.key == pygame.K_r:
                        self.reinitialiser()
            
            # Chute automatique
            if not self.jeu_termine and self.temps_chute >= self.vitesse_chute:
                if self.piece_valide(self.piece_actuelle, dy=1):
                    self.piece_actuelle.y += 1
                else:
                    # La pièce ne peut plus descendre
                    self.placer_piece(self.piece_actuelle)
                    self.effacer_lignes()
                    self.nouvelle_piece()
                
                self.temps_chute = 0
            
            self.dessiner()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuTetris()
    jeu.executer()