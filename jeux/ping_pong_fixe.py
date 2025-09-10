import pygame
import sys
import random
import math

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 800
HAUTEUR = 600
FPS = 60

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
VERT = (0, 128, 0)
BLEU = (0, 100, 200)

class Raquette:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largeur = 15
        self.hauteur = 80
        self.vitesse = 8
    
    def deplacer_haut(self):
        if self.y > 0:
            self.y -= self.vitesse
    
    def deplacer_bas(self):
        if self.y < HAUTEUR - self.hauteur:
            self.y += self.vitesse
    
    def dessiner(self, surface):
        pygame.draw.rect(surface, BLANC, (self.x, self.y, self.largeur, self.hauteur))

class Balle:
    def __init__(self):
        self.x = LARGEUR // 2
        self.y = HAUTEUR // 2
        self.rayon = 10
        self.vitesse_x = random.choice([-5, 5])
        self.vitesse_y = random.uniform(-3, 3)
    
    def deplacer(self):
        self.x += self.vitesse_x
        self.y += self.vitesse_y
        
        # Rebond sur les murs haut et bas
        if self.y <= self.rayon or self.y >= HAUTEUR - self.rayon:
            self.vitesse_y = -self.vitesse_y
    
    def reinitialiser(self):
        self.x = LARGEUR // 2
        self.y = HAUTEUR // 2
        self.vitesse_x = random.choice([-5, 5])
        self.vitesse_y = random.uniform(-3, 3)
    
    def dessiner(self, surface):
        pygame.draw.circle(surface, BLANC, (int(self.x), int(self.y)), self.rayon)

class JeuPingPong:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Ping Pong")
        self.horloge = pygame.time.Clock()
        
        # Raquettes
        self.raquette_gauche = Raquette(30, HAUTEUR // 2 - 40)
        self.raquette_droite = Raquette(LARGEUR - 45, HAUTEUR // 2 - 40)
        
        # Balle
        self.balle = Balle()
        
        # Scores
        self.score_gauche = 0
        self.score_droite = 0
        
        # Interface
        self.font = pygame.font.Font(None, 72)
        self.font_petit = pygame.font.Font(None, 36)
    
    def verifier_collisions(self):
        # Collision avec raquette gauche
        if (self.balle.x - self.balle.rayon <= self.raquette_gauche.x + self.raquette_gauche.largeur and
            self.raquette_gauche.y <= self.balle.y <= self.raquette_gauche.y + self.raquette_gauche.hauteur and
            self.balle.vitesse_x < 0):
            
            self.balle.vitesse_x = -self.balle.vitesse_x
            # Ajouter un effet selon la position de contact
            contact_relatif = (self.balle.y - (self.raquette_gauche.y + self.raquette_gauche.hauteur/2)) / (self.raquette_gauche.hauteur/2)
            self.balle.vitesse_y = contact_relatif * 5
        
        # Collision avec raquette droite
        if (self.balle.x + self.balle.rayon >= self.raquette_droite.x and
            self.raquette_droite.y <= self.balle.y <= self.raquette_droite.y + self.raquette_droite.hauteur and
            self.balle.vitesse_x > 0):
            
            self.balle.vitesse_x = -self.balle.vitesse_x
            # Ajouter un effet selon la position de contact
            contact_relatif = (self.balle.y - (self.raquette_droite.y + self.raquette_droite.hauteur/2)) / (self.raquette_droite.hauteur/2)
            self.balle.vitesse_y = contact_relatif * 5
    
    def verifier_points(self):
        # Point pour le joueur de droite
        if self.balle.x < 0:
            self.score_droite += 1
            self.balle.reinitialiser()
        
        # Point pour le joueur de gauche
        elif self.balle.x > LARGEUR:
            self.score_gauche += 1
            self.balle.reinitialiser()
    
    def ia_raquette_droite(self):
        # IA simple qui suit la balle
        centre_raquette = self.raquette_droite.y + self.raquette_droite.hauteur // 2
        
        if centre_raquette < self.balle.y - 10:
            self.raquette_droite.deplacer_bas()
        elif centre_raquette > self.balle.y + 10:
            self.raquette_droite.deplacer_haut()
    
    def dessiner_terrain(self):
        # Fond
        self.ecran.fill(VERT)
        
        # Ligne centrale
        for y in range(0, HAUTEUR, 20):
            pygame.draw.rect(self.ecran, BLANC, (LARGEUR//2 - 2, y, 4, 10))
    
    def dessiner_scores(self):
        # Score gauche
        texte_gauche = self.font.render(str(self.score_gauche), True, BLANC)
        self.ecran.blit(texte_gauche, (LARGEUR//4, 50))
        
        # Score droite
        texte_droite = self.font.render(str(self.score_droite), True, BLANC)
        self.ecran.blit(texte_droite, (3*LARGEUR//4, 50))
        
        # Instructions
        texte_instructions = self.font_petit.render("W/S: Raquette gauche | R: Reset", True, BLANC)
        self.ecran.blit(texte_instructions, (10, HAUTEUR - 40))
    
    def reinitialiser(self):
        self.score_gauche = 0
        self.score_droite = 0
        self.balle.reinitialiser()
        self.raquette_gauche.y = HAUTEUR // 2 - 40
        self.raquette_droite.y = HAUTEUR // 2 - 40
    
    def dessiner(self):
        self.dessiner_terrain()
        
        # Objets du jeu
        self.raquette_gauche.dessiner(self.ecran)
        self.raquette_droite.dessiner(self.ecran)
        self.balle.dessiner(self.ecran)
        
        # Interface
        self.dessiner_scores()
        
        pygame.display.flip()
    
    def executer(self):
        en_cours = True
        
        while en_cours:
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reinitialiser()
            
            # Contrôles continus
            touches = pygame.key.get_pressed()
            if touches[pygame.K_w]:
                self.raquette_gauche.deplacer_haut()
            if touches[pygame.K_s]:
                self.raquette_gauche.deplacer_bas()
            
            # IA pour la raquette droite
            self.ia_raquette_droite()
            
            # Mise à jour du jeu
            self.balle.deplacer()
            self.verifier_collisions()
            self.verifier_points()
            
            # Dessiner
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuPingPong()
    jeu.executer()