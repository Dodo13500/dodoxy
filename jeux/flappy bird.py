import pygame
import sys
import random

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 400
HAUTEUR = 600
FPS = 60

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU_CIEL = (135, 206, 235)
VERT = (0, 128, 0)
JAUNE = (255, 255, 0)

class Oiseau:
    def __init__(self):
        self.x = 50
        self.y = HAUTEUR // 2
        self.rayon = 20
        self.vitesse_y = 0
        self.gravite = 0.8
        self.force_saut = -12
    
    def sauter(self):
        self.vitesse_y = self.force_saut
    
    def mettre_a_jour(self):
        self.vitesse_y += self.gravite
        self.y += self.vitesse_y
        
        # Limites de l'écran
        if self.y < self.rayon:
            self.y = self.rayon
            self.vitesse_y = 0
        elif self.y > HAUTEUR - self.rayon:
            self.y = HAUTEUR - self.rayon
            self.vitesse_y = 0
    
    def dessiner(self, surface):
        pygame.draw.circle(surface, JAUNE, (int(self.x), int(self.y)), self.rayon)
        pygame.draw.circle(surface, NOIR, (int(self.x), int(self.y)), self.rayon, 2)
        
        # Œil
        pygame.draw.circle(surface, NOIR, (int(self.x + 8), int(self.y - 5)), 3)

class Tuyau:
    def __init__(self, x):
        self.x = x
        self.largeur = 80
        self.hauteur_haut = random.randint(50, HAUTEUR - 200)
        self.hauteur_bas = HAUTEUR - self.hauteur_haut - 150  # Espace de 150 pixels
        self.vitesse = -3
        self.passe = False
    
    def mettre_a_jour(self):
        self.x += self.vitesse
    
    def dessiner(self, surface):
        # Tuyau du haut
        pygame.draw.rect(surface, VERT, (self.x, 0, self.largeur, self.hauteur_haut))
        pygame.draw.rect(surface, NOIR, (self.x, 0, self.largeur, self.hauteur_haut), 2)
        
        # Tuyau du bas
        y_bas = HAUTEUR - self.hauteur_bas
        pygame.draw.rect(surface, VERT, (self.x, y_bas, self.largeur, self.hauteur_bas))
        pygame.draw.rect(surface, NOIR, (self.x, y_bas, self.largeur, self.hauteur_bas), 2)
    
    def collision(self, oiseau):
        # Vérifier si l'oiseau touche les tuyaux
        if (oiseau.x + oiseau.rayon > self.x and oiseau.x - oiseau.rayon < self.x + self.largeur):
            if (oiseau.y - oiseau.rayon < self.hauteur_haut or 
                oiseau.y + oiseau.rayon > HAUTEUR - self.hauteur_bas):
                return True
        return False

class JeuFlappyBird:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Flappy Bird")
        self.horloge = pygame.time.Clock()
        
        # Objets du jeu
        self.oiseau = Oiseau()
        self.tuyaux = []
        self.compteur_tuyaux = 0
        
        # État du jeu
        self.score = 0
        self.jeu_termine = False
        
        # Interface
        self.font = pygame.font.Font(None, 48)
        self.font_petit = pygame.font.Font(None, 36)
    
    def ajouter_tuyau(self):
        if self.compteur_tuyaux % 90 == 0:  # Nouveau tuyau toutes les 1.5 secondes
            self.tuyaux.append(Tuyau(LARGEUR))
        self.compteur_tuyaux += 1
    
    def mettre_a_jour_tuyaux(self):
        for tuyau in self.tuyaux[:]:
            tuyau.mettre_a_jour()
            
            # Supprimer les tuyaux sortis de l'écran
            if tuyau.x + tuyau.largeur < 0:
                self.tuyaux.remove(tuyau)
            
            # Compter les points
            if not tuyau.passe and tuyau.x + tuyau.largeur < self.oiseau.x:
                tuyau.passe = True
                self.score += 1
            
            # Vérifier collision
            if tuyau.collision(self.oiseau):
                self.jeu_termine = True
    
    def dessiner_fond(self):
        self.ecran.fill(BLEU_CIEL)
        
        # Sol
        pygame.draw.rect(self.ecran, VERT, (0, HAUTEUR - 50, LARGEUR, 50))
    
    def dessiner_interface(self):
        # Score
        texte_score = self.font.render(f"Score: {self.score}", True, BLANC)
        self.ecran.blit(texte_score, (10, 10))
        
        # Instructions
        if not self.jeu_termine:
            texte_instruction = self.font_petit.render("ESPACE: Sauter", True, BLANC)
            self.ecran.blit(texte_instruction, (10, HAUTEUR - 40))
        else:
            texte_fin = self.font.render("Game Over!", True, BLANC)
            rect_fin = texte_fin.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            self.ecran.blit(texte_fin, rect_fin)
            
            texte_restart = self.font_petit.render("R: Recommencer", True, BLANC)
            rect_restart = texte_restart.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 50))
            self.ecran.blit(texte_restart, rect_restart)
    
    def reinitialiser(self):
        self.oiseau = Oiseau()
        self.tuyaux = []
        self.compteur_tuyaux = 0
        self.score = 0
        self.jeu_termine = False
    
    def dessiner(self):
        self.dessiner_fond()
        
        # Tuyaux
        for tuyau in self.tuyaux:
            tuyau.dessiner(self.ecran)
        
        # Oiseau
        self.oiseau.dessiner(self.ecran)
        
        # Interface
        self.dessiner_interface()
        
        pygame.display.flip()
    
    def executer(self):
        en_cours = True
        
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.jeu_termine:
                        self.oiseau.sauter()
                    elif event.key == pygame.K_r and self.jeu_termine:
                        self.reinitialiser()
            
            if not self.jeu_termine:
                # Mise à jour du jeu
                self.oiseau.mettre_a_jour()
                self.ajouter_tuyau()
                self.mettre_a_jour_tuyaux()
                
                # Vérifier si l'oiseau touche le sol
                if self.oiseau.y >= HAUTEUR - 50 - self.oiseau.rayon:
                    self.jeu_termine = True
            
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuFlappyBird()
    jeu.executer()