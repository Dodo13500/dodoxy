import pygame
import math
import sys

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 800
HAUTEUR = 600
FPS = 60

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
BLEU = (0, 0, 255)
JAUNE = (255, 255, 0)
MARRON = (139, 69, 19)

class JeuCordeASauter:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Corde à Sauter")
        self.horloge = pygame.time.Clock()
        
        # Position du joueur
        self.joueur_x = LARGEUR // 2
        self.joueur_y = HAUTEUR - 150
        self.joueur_largeur = 40
        self.joueur_hauteur = 80
        
        # Saut
        self.en_saut = False
        self.vitesse_saut = 0
        self.hauteur_saut = 0
        self.gravite = 0.8
        self.force_saut = -15
        
        # Corde
        self.angle_corde = 0
        self.vitesse_corde = 5
        self.rayon_corde = 200
        self.centre_corde_x = LARGEUR // 2
        self.centre_corde_y = HAUTEUR - 50
        
        # Score
        self.score = 0
        self.sauts_reussis = 0
        self.corde_passee = False
        
        # Interface
        self.font = pygame.font.Font(None, 36)
        self.font_grand = pygame.font.Font(None, 48)
        
        # État du jeu
        self.jeu_termine = False
        self.message_fin = ""
    
    def sauter(self):
        if not self.en_saut:
            self.en_saut = True
            self.vitesse_saut = self.force_saut
    
    def mettre_a_jour_joueur(self):
        if self.en_saut:
            self.vitesse_saut += self.gravite
            self.hauteur_saut += self.vitesse_saut
            
            # Vérifier si le joueur touche le sol
            if self.hauteur_saut >= 0:
                self.hauteur_saut = 0
                self.vitesse_saut = 0
                self.en_saut = False
    
    def mettre_a_jour_corde(self):
        self.angle_corde += self.vitesse_corde
        if self.angle_corde >= 360:
            self.angle_corde = 0
    
    def obtenir_position_corde(self):
        # Calculer les positions des extrémités de la corde
        angle_rad = math.radians(self.angle_corde)
        
        # Point gauche de la corde
        x1 = self.centre_corde_x - self.rayon_corde * math.cos(angle_rad)
        y1 = self.centre_corde_y - self.rayon_corde * math.sin(angle_rad)
        
        # Point droit de la corde
        x2 = self.centre_corde_x + self.rayon_corde * math.cos(angle_rad)
        y2 = self.centre_corde_y - self.rayon_corde * math.sin(angle_rad)
        
        return (x1, y1), (x2, y2)
    
    def verifier_collision(self):
        # Position du joueur
        joueur_bas = self.joueur_y - self.hauteur_saut
        joueur_gauche = self.joueur_x - self.joueur_largeur // 2
        joueur_droite = self.joueur_x + self.joueur_largeur // 2
        
        # Position de la corde
        (x1, y1), (x2, y2) = self.obtenir_position_corde()
        
        # Vérifier si la corde passe au niveau du joueur
        hauteur_corde = min(y1, y2)
        
        # Si la corde est au niveau des pieds du joueur
        if abs(hauteur_corde - joueur_bas) < 10:
            # Vérifier si le joueur est dans la zone de la corde
            if joueur_gauche < max(x1, x2) and joueur_droite > min(x1, x2):
                # Collision détectée
                if not self.en_saut:
                    return True
        
        return False
    
    def verifier_saut_reussi(self):
        # Vérifier si le joueur a sauté au bon moment
        (x1, y1), (x2, y2) = self.obtenir_position_corde()
        hauteur_corde = min(y1, y2)
        
        # Si la corde passe sous le joueur et qu'il est en l'air
        if (hauteur_corde > self.joueur_y - 20 and 
            self.en_saut and 
            self.hauteur_saut < -30 and 
            not self.corde_passee):
            
            self.sauts_reussis += 1
            self.score += 10
            self.corde_passee = True
            
            # Augmenter la vitesse progressivement
            if self.sauts_reussis % 5 == 0:
                self.vitesse_corde += 0.5
        
        # Réinitialiser le flag quand la corde est passée
        if hauteur_corde < self.joueur_y - 100:
            self.corde_passee = False
    
    def dessiner_joueur(self):
        # Position du joueur avec le saut
        y_joueur = self.joueur_y - self.hauteur_saut
        
        # Corps (rectangle)
        pygame.draw.rect(self.ecran, BLEU, 
                        (self.joueur_x - self.joueur_largeur//2, 
                         y_joueur - self.joueur_hauteur, 
                         self.joueur_largeur, 
                         self.joueur_hauteur))
        
        # Tête (cercle)
        pygame.draw.circle(self.ecran, JAUNE, 
                          (self.joueur_x, y_joueur - self.joueur_hauteur - 15), 15)
        
        # Bras
        pygame.draw.line(self.ecran, NOIR,
                        (self.joueur_x - 20, y_joueur - self.joueur_hauteur + 20),
                        (self.joueur_x - 30, y_joueur - self.joueur_hauteur + 40), 3)
        pygame.draw.line(self.ecran, NOIR,
                        (self.joueur_x + 20, y_joueur - self.joueur_hauteur + 20),
                        (self.joueur_x + 30, y_joueur - self.joueur_hauteur + 40), 3)
        
        # Jambes
        pygame.draw.line(self.ecran, NOIR,
                        (self.joueur_x - 10, y_joueur),
                        (self.joueur_x - 15, y_joueur + 20), 3)
        pygame.draw.line(self.ecran, NOIR,
                        (self.joueur_x + 10, y_joueur),
                        (self.joueur_x + 15, y_joueur + 20), 3)
    
    def dessiner_corde(self):
        (x1, y1), (x2, y2) = self.obtenir_position_corde()
        
        # Dessiner la corde
        pygame.draw.line(self.ecran, MARRON, (x1, y1), (x2, y2), 5)
        
        # Dessiner les poignées
        pygame.draw.circle(self.ecran, ROUGE, (int(x1), int(y1)), 8)
        pygame.draw.circle(self.ecran, ROUGE, (int(x2), int(y2)), 8)
    
    def dessiner_interface(self):
        # Score
        texte_score = self.font.render(f"Score: {self.score}", True, NOIR)
        self.ecran.blit(texte_score, (10, 10))
        
        # Sauts réussis
        texte_sauts = self.font.render(f"Sauts: {self.sauts_reussis}", True, NOIR)
        self.ecran.blit(texte_sauts, (10, 50))
        
        # Vitesse
        texte_vitesse = self.font.render(f"Vitesse: {self.vitesse_corde:.1f}", True, NOIR)
        self.ecran.blit(texte_vitesse, (10, 90))
        
        # Instructions
        if self.sauts_reussis == 0:
            texte_instruction = self.font.render("Appuyez sur ESPACE pour sauter!", True, VERT)
            self.ecran.blit(texte_instruction, (LARGEUR//2 - 150, 50))
    
    def dessiner_fin_jeu(self):
        # Fond semi-transparent
        overlay = pygame.Surface((LARGEUR, HAUTEUR))
        overlay.set_alpha(128)
        overlay.fill(NOIR)
        self.ecran.blit(overlay, (0, 0))
        
        # Message de fin
        texte_fin = self.font_grand.render(self.message_fin, True, ROUGE)
        rect_fin = texte_fin.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 50))
        self.ecran.blit(texte_fin, rect_fin)
        
        # Score final
        texte_score_final = self.font.render(f"Score final: {self.score}", True, BLANC)
        rect_score = texte_score_final.get_rect(center=(LARGEUR//2, HAUTEUR//2))
        self.ecran.blit(texte_score_final, rect_score)
        
        # Sauts réussis
        texte_sauts_final = self.font.render(f"Sauts réussis: {self.sauts_reussis}", True, BLANC)
        rect_sauts = texte_sauts_final.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 30))
        self.ecran.blit(texte_sauts_final, rect_sauts)
        
        # Instructions pour recommencer
        texte_recommencer = self.font.render("Appuyez sur R pour recommencer ou Q pour quitter", True, JAUNE)
        rect_recommencer = texte_recommencer.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 80))
        self.ecran.blit(texte_recommencer, rect_recommencer)
    
    def reinitialiser(self):
        self.en_saut = False
        self.vitesse_saut = 0
        self.hauteur_saut = 0
        self.angle_corde = 0
        self.vitesse_corde = 5
        self.score = 0
        self.sauts_reussis = 0
        self.corde_passee = False
        self.jeu_termine = False
        self.message_fin = ""
    
    def dessiner(self):
        self.ecran.fill(BLANC)
        
        # Dessiner le sol
        pygame.draw.rect(self.ecran, VERT, (0, HAUTEUR - 30, LARGEUR, 30))
        
        if not self.jeu_termine:
            self.dessiner_corde()
            self.dessiner_joueur()
            self.dessiner_interface()
        else:
            self.dessiner_corde()
            self.dessiner_joueur()
            self.dessiner_interface()
            self.dessiner_fin_jeu()
        
        pygame.display.flip()
    
    def executer(self):
        en_cours = True
        
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                elif event.type == pygame.KEYDOWN:
                    if not self.jeu_termine:
                        if event.key == pygame.K_SPACE:
                            self.sauter()
                    else:
                        if event.key == pygame.K_r:
                            self.reinitialiser()
                        elif event.key == pygame.K_q:
                            en_cours = False
            
            if not self.jeu_termine:
                # Mettre à jour le jeu
                self.mettre_a_jour_joueur()
                self.mettre_a_jour_corde()
                
                # Vérifier les collisions
                if self.verifier_collision():
                    self.jeu_termine = True
                    self.message_fin = "GAME OVER!"
                
                # Vérifier les sauts réussis
                self.verifier_saut_reussi()
            
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuCordeASauter()
    jeu.executer()