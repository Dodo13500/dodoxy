import pygame
import random
import sys
import math

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 800
HAUTEUR = 600
TAILLE_CASE = 20
FPS = 10

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
VERT = (0, 255, 0)
ROUGE = (255, 0, 0)
BLEU = (0, 0, 255)

class JeuSnake:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Snake")
        self.horloge = pygame.time.Clock()
        
        # Position initiale du serpent
        self.serpent = [(LARGEUR//2, HAUTEUR//2)]
        self.direction = (TAILLE_CASE, 0)  # Droite
        
        # Nourriture
        self.nourriture = self.generer_nourriture()
        
        # Score
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        
        # État du jeu
        self.jeu_termine = False
    
    def generer_nourriture(self):
        while True:
            x = random.randint(0, (LARGEUR - TAILLE_CASE) // TAILLE_CASE) * TAILLE_CASE
            y = random.randint(0, (HAUTEUR - TAILLE_CASE) // TAILLE_CASE) * TAILLE_CASE
            if (x, y) not in self.serpent:
                return (x, y)
    
    def deplacer_serpent(self):
        if self.jeu_termine:
            return
            
        # Nouvelle position de la tête
        tete = self.serpent[0]
        nouvelle_tete = (tete[0] + self.direction[0], tete[1] + self.direction[1])
        
        # Vérifier les collisions avec les murs
        if (nouvelle_tete[0] < 0 or nouvelle_tete[0] >= LARGEUR or
            nouvelle_tete[1] < 0 or nouvelle_tete[1] >= HAUTEUR):
            self.jeu_termine = True
            return
        
        # Vérifier les collisions avec le corps
        if nouvelle_tete in self.serpent:
            self.jeu_termine = True
            return
        
        # Ajouter la nouvelle tête
        self.serpent.insert(0, nouvelle_tete)
        
        # Vérifier si le serpent mange la nourriture
        if nouvelle_tete == self.nourriture:
            self.score += 10
            self.nourriture = self.generer_nourriture()
        else:
            # Retirer la queue si pas de nourriture mangée
            self.serpent.pop()
    
    def changer_direction(self, nouvelle_direction):
        # Empêcher le serpent de faire demi-tour
        if (nouvelle_direction[0] * -1, nouvelle_direction[1] * -1) != self.direction:
            self.direction = nouvelle_direction
    
    def dessiner(self):
        self.ecran.fill(NOIR)
        
        # Dessiner le serpent
        for i, segment in enumerate(self.serpent):
            couleur = VERT if i == 0 else (0, 200, 0)  # Tête plus claire
            pygame.draw.rect(self.ecran, couleur, 
                           (segment[0], segment[1], TAILLE_CASE, TAILLE_CASE))
            pygame.draw.rect(self.ecran, BLANC, 
                           (segment[0], segment[1], TAILLE_CASE, TAILLE_CASE), 1)
        
        # Dessiner la nourriture
        pygame.draw.rect(self.ecran, ROUGE, 
                        (self.nourriture[0], self.nourriture[1], TAILLE_CASE, TAILLE_CASE))
        
        # Afficher le score
        texte_score = self.font.render(f"Score: {self.score}", True, BLANC)
        self.ecran.blit(texte_score, (10, 10))
        
        # Message de fin de jeu
        if self.jeu_termine:
            texte_fin = self.font.render("Game Over! Appuyez sur R pour recommencer", True, BLANC)
            rect_texte = texte_fin.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            self.ecran.blit(texte_fin, rect_texte)
        
        pygame.display.flip()
    
    def reinitialiser(self):
        self.serpent = [(LARGEUR//2, HAUTEUR//2)]
        self.direction = (TAILLE_CASE, 0)
        self.nourriture = self.generer_nourriture()
        self.score = 0
        self.jeu_termine = False
    
    def executer(self):
        en_cours = True
        
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.changer_direction((0, -TAILLE_CASE))
                    elif event.key == pygame.K_DOWN:
                        self.changer_direction((0, TAILLE_CASE))
                    elif event.key == pygame.K_LEFT:
                        self.changer_direction((-TAILLE_CASE, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.changer_direction((TAILLE_CASE, 0))
                    elif event.key == pygame.K_r and self.jeu_termine:
                        self.reinitialiser()
            
            self.deplacer_serpent()
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuSnake()
    jeu.executer()