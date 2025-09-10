import pygame
import random
import sys
import math

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 1000
HAUTEUR = 600
FPS = 60

# Couleurs réalistes
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
VERT_TABLE = (0, 100, 0)
VERT_FONCE = (0, 80, 0)
BLANC_LIGNE = (255, 255, 255)
ORANGE_BALLE = (255, 165, 0)
ROUGE = (220, 20, 60)
BLEU = (30, 144, 255)
GRIS = (128, 128, 128)
JAUNE = (255, 215, 0)

class Raquette:
    def __init__(self, x, y, couleur, est_joueur=True):
        self.x = x
        self.y = y
        self.largeur = 15
        self.hauteur = 100
        self.vitesse = 8
        self.score = 0
        self.couleur = couleur
        self.est_joueur = est_joueur
        self.vitesse_ia = 6
        
        # Effets visuels
        self.effet_frappe = 0
        self.particules = []
    
    def deplacer_haut(self):
        if self.y > 0:
            self.y -= self.vitesse
    
    def deplacer_bas(self):
        if self.y < HAUTEUR - self.hauteur:
            self.y += self.vitesse
    
    def ia_deplacer(self, balle):
        # IA améliorée avec prédiction
        centre_raquette = self.y + self.hauteur // 2
        
        # Prédire où la balle va arriver
        if balle.vitesse_x > 0 and self.x > LARGEUR // 2:  # Balle va vers la droite
            temps_arrivee = (self.x - balle.x) / balle.vitesse_x
            y_predit = balle.y + balle.vitesse_y * temps_arrivee
            
            # Ajouter un peu d'imprécision pour rendre l'IA battable
            y_predit += random.uniform(-20, 20)
            
            if centre_raquette < y_predit - 10:
                self.y += self.vitesse_ia
            elif centre_raquette > y_predit + 10:
                self.y -= self.vitesse_ia
        
        elif balle.vitesse_x < 0 and self.x < LARGEUR // 2:  # Balle va vers la gauche
            temps_arrivee = (balle.x - self.x) / abs(balle.vitesse_x)
            y_predit = balle.y + balle.vitesse_y * temps_arrivee
            
            y_predit += random.uniform(-20, 20)
            
            if centre_raquette < y_predit - 10:
                self.y += self.vitesse_ia
            elif centre_raquette > y_predit + 10:
                self.y -= self.vitesse_ia
        
        # Limiter les mouvements
        self.y = max(0, min(HAUTEUR - self.hauteur, self.y))
    
    def creer_particules_frappe(self):
        centre_x = self.x + self.largeur // 2
        centre_y = self.y + self.hauteur // 2
        
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            vitesse = random.uniform(2, 5)
            particule = {
                'x': centre_x,
                'y': centre_y,
                'vx': math.cos(angle) * vitesse,
                'vy': math.sin(angle) * vitesse,
                'vie': 20,
                'couleur': self.couleur
            }
            self.particules.append(particule)
    
    def mettre_a_jour_particules(self):
        for particule in self.particules[:]:
            particule['x'] += particule['vx']
            particule['y'] += particule['vy']
            particule['vx'] *= 0.95
            particule['vy'] *= 0.95
            particule['vie'] -= 1
            
            if particule['vie'] <= 0:
                self.particules.remove(particule)
    
    def dessiner(self, surface):
        # Effet de frappe
        if self.effet_frappe > 0:
            self.effet_frappe -= 1
            largeur_effet = self.largeur + 4
            hauteur_effet = self.hauteur + 4
            x_effet = self.x - 2
            y_effet = self.y - 2
            pygame.draw.rect(surface, BLANC, (x_effet, y_effet, largeur_effet, hauteur_effet), border_radius=5)
        
        # Raquette principale avec effet 3D
        pygame.draw.rect(surface, self.couleur, (self.x, self.y, self.largeur, self.hauteur), border_radius=5)
        
        # Reflet
        pygame.draw.rect(surface, BLANC, (self.x + 2, self.y + 2, self.largeur - 4, 10), border_radius=3)
        
        # Bordure
        pygame.draw.rect(surface, NOIR, (self.x, self.y, self.largeur, self.hauteur), width=2, border_radius=5)
        
        # Particules
        for particule in self.particules:
            if particule['vie'] > 0:
                pygame.draw.circle(surface, particule['couleur'], 
                                 (int(particule['x']), int(particule['y'])), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)

class Balle:
    def __init__(self):
        self.reinitialiser()
        self.rayon = 8
        self.vitesse_base = 6
        self.vitesse_max = 12
        
        # Effets visuels
        self.trainee = []
        self.rotation = 0
        self.particules_rebond = []
    
    def reinitialiser(self):
        self.x = LARGEUR // 2
        self.y = HAUTEUR // 2
        
        # Direction aléatoire
        angle = random.uniform(-math.pi/4, math.pi/4)
        if random.choice([True, False]):
            angle += math.pi
        
        self.vitesse_x = math.cos(angle) * self.vitesse_base
        self.vitesse_y = math.sin(angle) * self.vitesse_base
    
    def deplacer(self):
        # Ajouter position à la traînée
        self.trainee.append((self.x, self.y))
        if len(self.trainee) > 8:
            self.trainee.pop(0)
        
        # Déplacement
        self.x += self.vitesse_x
        self.y += self.vitesse_y
        
        # Rotation pour l'effet visuel
        self.rotation += math.sqrt(self.vitesse_x**2 + self.vitesse_y**2) * 0.1
        
        # Rebond sur les murs haut et bas
        if self.y <= self.rayon or self.y >= HAUTEUR - self.rayon:
            self.vitesse_y = -self.vitesse_y
            self.y = max(self.rayon, min(HAUTEUR - self.rayon, self.y))
            self.creer_particules_rebond()
    
    def rebondir_raquette(self, raquette):
        # Calculer l'angle de rebond basé sur où la balle frappe la raquette
        centre_raquette = raquette.y + raquette.hauteur // 2
        distance_centre = self.y - centre_raquette
        angle_rebond = distance_centre / (raquette.hauteur // 2) * math.pi / 3  # Max 60 degrés
        
        # Augmenter légèrement la vitesse
        vitesse_actuelle = math.sqrt(self.vitesse_x**2 + self.vitesse_y**2)
        nouvelle_vitesse = min(self.vitesse_max, vitesse_actuelle * 1.05)
        
        # Inverser la direction X et appliquer l'angle
        if raquette.x < LARGEUR // 2:  # Raquette gauche
            self.vitesse_x = nouvelle_vitesse * math.cos(angle_rebond)
        else:  # Raquette droite
            self.vitesse_x = -nouvelle_vitesse * math.cos(angle_rebond)
        
        self.vitesse_y = nouvelle_vitesse * math.sin(angle_rebond)
        
        # Effet visuel
        raquette.effet_frappe = 10
        raquette.creer_particules_frappe()
        self.creer_particules_rebond()
    
    def creer_particules_rebond(self):
        for _ in range(6):
            angle = random.uniform(0, 2 * math.pi)
            vitesse = random.uniform(1, 3)
            particule = {
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * vitesse,
                'vy': math.sin(angle) * vitesse,
                'vie': 15,
                'couleur': ORANGE_BALLE
            }
            self.particules_rebond.append(particule)
    
    def mettre_a_jour_particules(self):
        for particule in self.particules_rebond[:]:
            particule['x'] += particule['vx']
            particule['y'] += particule['vy']
            particule['vie'] -= 1
            
            if particule['vie'] <= 0:
                self.particules_rebond.remove(particule)
    
    def dessiner(self, surface):
        # Traînée
        for i, (x, y) in enumerate(self.trainee):
            alpha = (i + 1) / len(self.trainee)
            rayon_trainee = int(self.rayon * alpha * 0.7)
            if rayon_trainee > 0:
                couleur_trainee = (int(ORANGE_BALLE[0] * alpha), 
                                 int(ORANGE_BALLE[1] * alpha), 
                                 int(ORANGE_BALLE[2] * alpha))
                pygame.draw.circle(surface, couleur_trainee, (int(x), int(y)), rayon_trainee)
        
        # Balle principale
        pygame.draw.circle(surface, ORANGE_BALLE, (int(self.x), int(self.y)), self.rayon)
        
        # Reflet sur la balle
        reflet_x = int(self.x - self.rayon * 0.3)
        reflet_y = int(self.y - self.rayon * 0.3)
        pygame.draw.circle(surface, BLANC, (reflet_x, reflet_y), self.rayon // 3)
        
        # Motif de rotation
        for i in range(3):
            angle = self.rotation + i * 2 * math.pi / 3
            ligne_x = int(self.x + math.cos(angle) * self.rayon * 0.6)
            ligne_y = int(self.y + math.sin(angle) * self.rayon * 0.6)
            pygame.draw.circle(surface, (200, 100, 0), (ligne_x, ligne_y), 1)
        
        # Bordure
        pygame.draw.circle(surface, NOIR, (int(self.x), int(self.y)), self.rayon, 2)
        
        # Particules de rebond
        for particule in self.particules_rebond:
            if particule['vie'] > 0:
                pygame.draw.circle(surface, particule['couleur'], 
                                 (int(particule['x']), int(particule['y'])), 1)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.rayon, self.y - self.rayon, 
                          self.rayon * 2, self.rayon * 2)

class JeuPingPong:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Ping Pong Réaliste")
        self.horloge = pygame.time.Clock()
        
        # Objets du jeu
        self.raquette_gauche = Raquette(30, HAUTEUR//2 - 50, ROUGE, True)
        self.raquette_droite = Raquette(LARGEUR - 45, HAUTEUR//2 - 50, BLEU, False)
        self.balle = Balle()
        
        # État du jeu
        self.jeu_termine = False
        self.gagnant = None
        self.score_max = 11
        self.pause = False
        
        # Interface
        self.font = pygame.font.Font(None, 72)
        self.font_moyen = pygame.font.Font(None, 48)
        self.font_petit = pygame.font.Font(None, 36)
        
        # Effets visuels
        self.particules_score = []
        self.flash_score = 0
    
    def gerer_collisions(self):
        balle_rect = self.balle.get_rect()
        
        # Collision avec raquette gauche
        if (balle_rect.colliderect(self.raquette_gauche.get_rect()) and 
            self.balle.vitesse_x < 0):
            self.balle.rebondir_raquette(self.raquette_gauche)
        
        # Collision avec raquette droite
        if (balle_rect.colliderect(self.raquette_droite.get_rect()) and 
            self.balle.vitesse_x > 0):
            self.balle.rebondir_raquette(self.raquette_droite)
    
    def verifier_score(self):
        if self.balle.x < 0:
            self.raquette_droite.score += 1
            self.creer_particules_score(LARGEUR - 100, 100)
            self.flash_score = 30
            self.balle.reinitialiser()
            
            if self.raquette_droite.score >= self.score_max:
                self.jeu_termine = True
                self.gagnant = "IA"
        
        elif self.balle.x > LARGEUR:
            self.raquette_gauche.score += 1
            self.creer_particules_score(100, 100)
            self.flash_score = 30
            self.balle.reinitialiser()
            
            if self.raquette_gauche.score >= self.score_max:
                self.jeu_termine = True
                self.gagnant = "Joueur"
    
    def creer_particules_score(self, x, y):
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            vitesse = random.uniform(3, 8)
            particule = {
                'x': x,
                'y': y,
                'vx': math.cos(angle) * vitesse,
                'vy': math.sin(angle) * vitesse,
                'vie': 40,
                'couleur': JAUNE
            }
            self.particules_score.append(particule)
    
    def mettre_a_jour_particules(self):
        for particule in self.particules_score[:]:
            particule['x'] += particule['vx']
            particule['y'] += particule['vy']
            particule['vx'] *= 0.98
            particule['vy'] += 0.2  # Gravité
            particule['vie'] -= 1
            
            if particule['vie'] <= 0:
                self.particules_score.remove(particule)
    
    def dessiner_table(self):
        # Table de ping pong réaliste
        self.ecran.fill(VERT_TABLE)
        
        # Texture de la table
        for i in range(0, LARGEUR, 40):
            for j in range(0, HAUTEUR, 40):
                if (i + j) % 80 == 0:
                    pygame.draw.rect(self.ecran, VERT_FONCE, (i, j, 20, 20))
        
        # Ligne centrale
        pygame.draw.line(self.ecran, BLANC_LIGNE, (LARGEUR//2, 0), (LARGEUR//2, HAUTEUR), 3)
        
        # Lignes de côté
        pygame.draw.line(self.ecran, BLANC_LIGNE, (0, 0), (LARGEUR, 0), 3)
        pygame.draw.line(self.ecran, BLANC_LIGNE, (0, HAUTEUR-3), (LARGEUR, HAUTEUR-3), 3)
        
        # Filet (effet 3D)
        filet_hauteur = 20
        for i in range(0, filet_hauteur, 2):
            couleur = BLANC if i % 4 == 0 else GRIS
            pygame.draw.line(self.ecran, couleur, 
                           (LARGEUR//2 - 1, HAUTEUR//2 - filet_hauteur//2 + i),
                           (LARGEUR//2 + 1, HAUTEUR//2 - filet_hauteur//2 + i), 1)
    
    def dessiner_scores(self):
        # Scores avec effet flash
        couleur_gauche = BLANC if self.flash_score == 0 else JAUNE
        couleur_droite = BLANC if self.flash_score == 0 else JAUNE
        
        if self.flash_score > 0:
            self.flash_score -= 1
        
        # Score joueur
        texte_score_gauche = self.font.render(str(self.raquette_gauche.score), True, couleur_gauche)
        self.ecran.blit(texte_score_gauche, (LARGEUR//4 - 20, 50))
        
        # Score IA
        texte_score_droite = self.font.render(str(self.raquette_droite.score), True, couleur_droite)
        self.ecran.blit(texte_score_droite, (3*LARGEUR//4 - 20, 50))
        
        # Séparateur
        pygame.draw.circle(self.ecran, BLANC, (LARGEUR//2, 80), 5)
        
        # Particules de score
        for particule in self.particules_score:
            if particule['vie'] > 0:
                pygame.draw.circle(self.ecran, particule['couleur'], 
                                 (int(particule['x']), int(particule['y'])), 3)
    
    def dessiner_interface(self):
        # Titre
        if not self.jeu_termine and not self.pause:
            # Vitesse de la balle
            vitesse_balle = math.sqrt(self.balle.vitesse_x**2 + self.balle.vitesse_y**2)
            texte_vitesse = self.font_petit.render(f"Vitesse: {vitesse_balle:.1f}", True, BLANC)
            self.ecran.blit(texte_vitesse, (10, 10))
            
            # Instructions
            instructions = ["W/S: Raquette", "P: Pause", "R: Redémarrer"]
            for i, instruction in enumerate(instructions):
                texte = pygame.font.Font(None, 24).render(instruction, True, GRIS)
                self.ecran.blit(texte, (10, HAUTEUR - 80 + i * 25))
    
    def dessiner_pause(self):
        if self.pause:
            # Fond semi-transparent
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(128)
            overlay.fill(NOIR)
            self.ecran.blit(overlay, (0, 0))
            
            # Message de pause
            texte_pause = self.font.render("PAUSE", True, BLANC)
            rect_pause = texte_pause.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            self.ecran.blit(texte_pause, rect_pause)
            
            texte_continuer = self.font_moyen.render("Appuyez sur P pour continuer", True, BLANC)
            rect_continuer = texte_continuer.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 50))
            self.ecran.blit(texte_continuer, rect_continuer)
    
    def dessiner_fin_jeu(self):
        if self.jeu_termine:
            # Fond semi-transparent
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(200)
            overlay.fill(NOIR)
            self.ecran.blit(overlay, (0, 0))
            
            # Message de fin
            couleur_gagnant = ROUGE if self.gagnant == "Joueur" else BLEU
            texte_fin = self.font.render(f"{self.gagnant} gagne!", True, couleur_gagnant)
            rect_fin = texte_fin.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 50))
            self.ecran.blit(texte_fin, rect_fin)
            
            # Score final
            score_final = f"{self.raquette_gauche.score} - {self.raquette_droite.score}"
            texte_score = self.font_moyen.render(score_final, True, BLANC)
            rect_score = texte_score.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            self.ecran.blit(texte_score, rect_score)
            
            # Instructions
            texte_recommencer = self.font_petit.render("R: Recommencer | Q: Quitter", True, BLANC)
            rect_recommencer = texte_recommencer.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 80))
            self.ecran.blit(texte_recommencer, rect_recommencer)
    
    def reinitialiser(self):
        self.raquette_gauche.score = 0
        self.raquette_droite.score = 0
        self.raquette_gauche.y = HAUTEUR//2 - 50
        self.raquette_droite.y = HAUTEUR//2 - 50
        self.balle.reinitialiser()
        self.jeu_termine = False
        self.gagnant = None
        self.pause = False
        self.particules_score = []
        self.flash_score = 0
    
    def mettre_a_jour(self):
        if not self.jeu_termine and not self.pause:
            # Déplacer la balle
            self.balle.deplacer()
            
            # IA pour la raquette droite
            self.raquette_droite.ia_deplacer(self.balle)
            
            # Gérer les collisions
            self.gerer_collisions()
            
            # Vérifier le score
            self.verifier_score()
            
            # Mettre à jour les particules
            self.balle.mettre_a_jour_particules()
            self.raquette_gauche.mettre_a_jour_particules()
            self.raquette_droite.mettre_a_jour_particules()
        
        self.mettre_a_jour_particules()
    
    def dessiner(self):
        # Table
        self.dessiner_table()
        
        # Objets du jeu
        self.raquette_gauche.dessiner(self.ecran)
        self.raquette_droite.dessiner(self.ecran)
        self.balle.dessiner(self.ecran)
        
        # Interface
        self.dessiner_scores()
        self.dessiner_interface()
        
        # États spéciaux
        if self.pause:
            self.dessiner_pause()
        elif self.jeu_termine:
            self.dessiner_fin_jeu()
        
        pygame.display.flip()
    
    def executer(self):
        en_cours = True
        
        while en_cours:
            touches = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p and not self.jeu_termine:
                        self.pause = not self.pause
                    elif event.key == pygame.K_r:
                        self.reinitialiser()
                    elif event.key == pygame.K_q and self.jeu_termine:
                        en_cours = False
            
            # Contrôles du joueur
            if not self.jeu_termine and not self.pause:
                if touches[pygame.K_w] or touches[pygame.K_UP]:
                    self.raquette_gauche.deplacer_haut()
                if touches[pygame.K_s] or touches[pygame.K_DOWN]:
                    self.raquette_gauche.deplacer_bas()
            
            self.mettre_a_jour()
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuPingPong()
    jeu.executer()