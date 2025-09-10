import pygame
import random
import sys
import math

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 900
HAUTEUR = 700
TAILLE_CASE = 25
FPS = 60

# Couleurs réalistes
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
JAUNE_PACMAN = (255, 215, 0)
ROUGE_FANTOME = (220, 20, 60)
ROSE_FANTOME = (255, 182, 193)
CYAN_FANTOME = (0, 191, 255)
ORANGE_FANTOME = (255, 140, 0)
BLEU_LABYRINTHE = (0, 0, 255)
JAUNE_POINT = (255, 255, 0)
BLANC_GROS_POINT = (255, 255, 255)
GRIS = (128, 128, 128)

# Directions
HAUT = (0, -1)
BAS = (0, 1)
GAUCHE = (-1, 0)
DROITE = (1, 0)

# Labyrinthe (1 = mur, 0 = chemin, 2 = point, 3 = gros point)
LABYRINTHE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,3,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,3,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,1,1,1,1],
    [0,0,0,0,0,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,0,0,0,0,0],
    [1,1,1,1,1,1,2,1,1,0,1,1,0,0,0,0,1,1,0,1,1,2,1,1,1,1,1,1],
    [0,0,0,0,0,0,2,0,0,0,1,0,0,0,0,0,0,1,0,0,0,2,0,0,0,0,0,0],
    [1,1,1,1,1,1,2,1,1,0,1,0,0,0,0,0,0,1,0,1,1,2,1,1,1,1,1,1],
    [0,0,0,0,0,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,0,0,0,0,0],
    [1,1,1,1,1,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,3,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,3,1],
    [1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
    [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

class Pacman:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = DROITE
        self.prochaine_direction = DROITE
        self.vitesse = 3
        self.compteur_mouvement = 0
        self.bouche_ouverte = True
        self.compteur_animation = 0
        self.angle_bouche = 0
        
        # Effets visuels
        self.particules = []
        self.invincible = False
        self.temps_invincible = 0
    
    def changer_direction(self, nouvelle_direction):
        self.prochaine_direction = nouvelle_direction
    
    def peut_se_deplacer(self, dx, dy, labyrinthe):
        nouvelle_x = self.x + dx
        nouvelle_y = self.y + dy
        
        # Téléportation horizontale
        if nouvelle_x < 0:
            nouvelle_x = len(labyrinthe[0]) - 1
        elif nouvelle_x >= len(labyrinthe[0]):
            nouvelle_x = 0
        
        # Vérifier les limites verticales
        if nouvelle_y < 0 or nouvelle_y >= len(labyrinthe):
            return False
        
        return labyrinthe[nouvelle_y][nouvelle_x] != 1
    
    def mettre_a_jour(self, labyrinthe):
        self.compteur_mouvement += 1
        
        # Animation de la bouche
        self.compteur_animation += 1
        if self.compteur_animation >= 10:
            self.bouche_ouverte = not self.bouche_ouverte
            self.compteur_animation = 0
        
        # Calculer l'angle de la bouche selon la direction
        if self.direction == DROITE:
            self.angle_bouche = 0
        elif self.direction == GAUCHE:
            self.angle_bouche = 180
        elif self.direction == HAUT:
            self.angle_bouche = 90
        elif self.direction == BAS:
            self.angle_bouche = 270
        
        if self.compteur_mouvement >= self.vitesse:
            # Essayer de changer de direction
            dx, dy = self.prochaine_direction
            if self.peut_se_deplacer(dx, dy, labyrinthe):
                self.direction = self.prochaine_direction
            
            # Se déplacer dans la direction actuelle
            dx, dy = self.direction
            if self.peut_se_deplacer(dx, dy, labyrinthe):
                self.x += dx
                self.y += dy
                
                # Téléportation horizontale
                if self.x < 0:
                    self.x = len(labyrinthe[0]) - 1
                elif self.x >= len(labyrinthe[0]):
                    self.x = 0
            
            self.compteur_mouvement = 0
        
        # Mettre à jour l'invincibilité
        if self.invincible:
            self.temps_invincible -= 1
            if self.temps_invincible <= 0:
                self.invincible = False
        
        # Mettre à jour les particules
        self.mettre_a_jour_particules()
    
    def manger_gros_point(self):
        self.invincible = True
        self.temps_invincible = 300  # 5 secondes à 60 FPS
        
        # Créer des particules d'énergie
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            vitesse = random.uniform(2, 5)
            particule = {
                'x': self.x * TAILLE_CASE + TAILLE_CASE // 2,
                'y': self.y * TAILLE_CASE + TAILLE_CASE // 2,
                'vx': math.cos(angle) * vitesse,
                'vy': math.sin(angle) * vitesse,
                'vie': 30,
                'couleur': BLANC_GROS_POINT
            }
            self.particules.append(particule)
    
    def mettre_a_jour_particules(self):
        for particule in self.particules[:]:
            particule['x'] += particule['vx']
            particule['y'] += particule['vy']
            particule['vx'] *= 0.98
            particule['vy'] *= 0.98
            particule['vie'] -= 1
            
            if particule['vie'] <= 0:
                self.particules.remove(particule)
    
    def dessiner(self, surface):
        centre_x = self.x * TAILLE_CASE + TAILLE_CASE // 2
        centre_y = self.y * TAILLE_CASE + TAILLE_CASE // 2
        rayon = TAILLE_CASE // 2 - 2
        
        # Effet de clignotement si invincible
        if self.invincible and self.temps_invincible % 10 < 5:
            couleur = BLANC
        else:
            couleur = JAUNE_PACMAN
        
        if self.bouche_ouverte:
            # Pac-Man avec bouche ouverte
            angle_debut = self.angle_bouche - 30
            angle_fin = self.angle_bouche + 30
            
            # Corps principal
            pygame.draw.circle(surface, couleur, (centre_x, centre_y), rayon)
            
            # Bouche (triangle)
            angle_rad_debut = math.radians(angle_debut)
            angle_rad_fin = math.radians(angle_fin)
            
            point1 = (centre_x, centre_y)
            point2 = (centre_x + rayon * math.cos(angle_rad_debut),
                     centre_y - rayon * math.sin(angle_rad_debut))
            point3 = (centre_x + rayon * math.cos(angle_rad_fin),
                     centre_y - rayon * math.sin(angle_rad_fin))
            
            pygame.draw.polygon(surface, NOIR, [point1, point2, point3])
        else:
            # Pac-Man avec bouche fermée (cercle complet)
            pygame.draw.circle(surface, couleur, (centre_x, centre_y), rayon)
        
        # Œil
        oeil_x = centre_x + rayon // 3 * math.cos(math.radians(self.angle_bouche + 45))
        oeil_y = centre_y - rayon // 3 * math.sin(math.radians(self.angle_bouche + 45))
        pygame.draw.circle(surface, NOIR, (int(oeil_x), int(oeil_y)), 3)
        
        # Particules
        for particule in self.particules:
            if particule['vie'] > 0:
                pygame.draw.circle(surface, particule['couleur'], 
                                 (int(particule['x']), int(particule['y'])), 2)

class Fantome:
    def __init__(self, x, y, couleur):
        self.x = x
        self.y = y
        self.couleur = couleur
        self.direction = random.choice([HAUT, BAS, GAUCHE, DROITE])
        self.vitesse = 4
        self.compteur_mouvement = 0
        self.mode = "chasse"  # chasse, fuite, retour
        self.temps_mode = 0
        self.animation = 0
        
        # IA
        self.cible_x = x
        self.cible_y = y
    
    def peut_se_deplacer(self, dx, dy, labyrinthe):
        nouvelle_x = self.x + dx
        nouvelle_y = self.y + dy
        
        # Téléportation horizontale
        if nouvelle_x < 0:
            nouvelle_x = len(labyrinthe[0]) - 1
        elif nouvelle_x >= len(labyrinthe[0]):
            nouvelle_x = 0
        
        if nouvelle_y < 0 or nouvelle_y >= len(labyrinthe):
            return False
        
        return labyrinthe[nouvelle_y][nouvelle_x] != 1
    
    def choisir_direction(self, pacman, labyrinthe):
        directions_possibles = []
        
        for direction in [HAUT, BAS, GAUCHE, DROITE]:
            dx, dy = direction
            if self.peut_se_deplacer(dx, dy, labyrinthe):
                # Éviter de faire demi-tour sauf si nécessaire
                direction_opposee = (-self.direction[0], -self.direction[1])
                if direction != direction_opposee or len(directions_possibles) == 0:
                    directions_possibles.append(direction)
        
        if not directions_possibles:
            return self.direction
        
        if self.mode == "chasse":
            # Se diriger vers Pac-Man
            meilleure_direction = directions_possibles[0]
            meilleure_distance = float('inf')
            
            for direction in directions_possibles:
                dx, dy = direction
                nouvelle_x = self.x + dx
                nouvelle_y = self.y + dy
                
                distance = abs(nouvelle_x - pacman.x) + abs(nouvelle_y - pacman.y)
                if distance < meilleure_distance:
                    meilleure_distance = distance
                    meilleure_direction = direction
            
            return meilleure_direction
        
        elif self.mode == "fuite":
            # S'éloigner de Pac-Man
            meilleure_direction = directions_possibles[0]
            meilleure_distance = 0
            
            for direction in directions_possibles:
                dx, dy = direction
                nouvelle_x = self.x + dx
                nouvelle_y = self.y + dy
                
                distance = abs(nouvelle_x - pacman.x) + abs(nouvelle_y - pacman.y)
                if distance > meilleure_distance:
                    meilleure_distance = distance
                    meilleure_direction = direction
            
            return meilleure_direction
        
        else:
            # Mouvement aléatoire
            return random.choice(directions_possibles)
    
    def mettre_a_jour(self, pacman, labyrinthe):
        self.compteur_mouvement += 1
        self.animation += 0.2
        
        # Changer de mode selon l'état de Pac-Man
        if pacman.invincible and self.mode != "fuite":
            self.mode = "fuite"
            self.temps_mode = pacman.temps_invincible
        elif not pacman.invincible and self.mode == "fuite":
            self.mode = "chasse"
        
        if self.compteur_mouvement >= self.vitesse:
            # Choisir une nouvelle direction
            self.direction = self.choisir_direction(pacman, labyrinthe)
            
            # Se déplacer
            dx, dy = self.direction
            if self.peut_se_deplacer(dx, dy, labyrinthe):
                self.x += dx
                self.y += dy
                
                # Téléportation horizontale
                if self.x < 0:
                    self.x = len(labyrinthe[0]) - 1
                elif self.x >= len(labyrinthe[0]):
                    self.x = 0
            
            self.compteur_mouvement = 0
    
    def dessiner(self, surface):
        centre_x = self.x * TAILLE_CASE + TAILLE_CASE // 2
        centre_y = self.y * TAILLE_CASE + TAILLE_CASE // 2
        rayon = TAILLE_CASE // 2 - 2
        
        # Couleur selon le mode
        if self.mode == "fuite":
            couleur_corps = BLEU_LABYRINTHE
        else:
            couleur_corps = self.couleur
        
        # Corps du fantôme (demi-cercle + rectangle)
        pygame.draw.circle(surface, couleur_corps, (centre_x, centre_y - 3), rayon)
        pygame.draw.rect(surface, couleur_corps, 
                        (centre_x - rayon, centre_y - 3, rayon * 2, rayon + 3))
        
        # Base ondulée du fantôme
        ondulation = int(math.sin(self.animation) * 3)
        for i in range(-rayon, rayon, 4):
            hauteur_ondulation = 5 + ondulation if (i // 4) % 2 == 0 else 5 - ondulation
            pygame.draw.rect(surface, couleur_corps,
                           (centre_x + i, centre_y + rayon - 3, 4, hauteur_ondulation))
        
        # Yeux
        oeil_gauche_x = centre_x - rayon // 2
        oeil_droit_x = centre_x + rayon // 2
        oeil_y = centre_y - rayon // 2
        
        # Blanc des yeux
        pygame.draw.circle(surface, BLANC, (oeil_gauche_x, oeil_y), 4)
        pygame.draw.circle(surface, BLANC, (oeil_droit_x, oeil_y), 4)
        
        # Pupilles (regardent vers Pac-Man si en mode chasse)
        if self.mode == "chasse":
            # Direction du regard vers Pac-Man
            dx = centre_x - (self.x * TAILLE_CASE + TAILLE_CASE // 2)
            dy = centre_y - (self.y * TAILLE_CASE + TAILLE_CASE // 2)
            
            pupille_offset = 2
            pygame.draw.circle(surface, NOIR, 
                             (oeil_gauche_x + pupille_offset, oeil_y), 2)
            pygame.draw.circle(surface, NOIR, 
                             (oeil_droit_x + pupille_offset, oeil_y), 2)
        else:
            # Yeux effrayés
            pygame.draw.circle(surface, NOIR, (oeil_gauche_x, oeil_y + 1), 2)
            pygame.draw.circle(surface, NOIR, (oeil_droit_x, oeil_y + 1), 2)

class JeuPacman:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Pac-Man Réaliste")
        self.horloge = pygame.time.Clock()
        
        # Copier le labyrinthe pour pouvoir le modifier
        self.labyrinthe = [ligne[:] for ligne in LABYRINTHE]
        
        # Objets du jeu
        self.pacman = Pacman(13, 16)  # Position de départ
        self.fantomes = [
            Fantome(13, 10, ROUGE_FANTOME),
            Fantome(12, 10, ROSE_FANTOME),
            Fantome(14, 10, CYAN_FANTOME),
            Fantome(13, 11, ORANGE_FANTOME)
        ]
        
        # État du jeu
        self.score = 0
        self.vies = 3
        self.niveau = 1
        self.jeu_termine = False
        self.victoire = False
        
        # Compter les points totaux
        self.points_totaux = sum(ligne.count(2) + ligne.count(3) for ligne in self.labyrinthe)
        self.points_manges = 0
        
        # Interface
        self.font = pygame.font.Font(None, 36)
        self.font_grand = pygame.font.Font(None, 48)
        
        # Effets visuels
        self.particules_score = []
        self.flash_score = 0
    
    def verifier_collisions(self):
        for fantome in self.fantomes:
            if (self.pacman.x == fantome.x and self.pacman.y == fantome.y):
                if self.pacman.invincible:
                    # Manger le fantôme
                    self.score += 200
                    self.creer_particules_score(fantome.x, fantome.y)
                    # Remettre le fantôme au centre
                    fantome.x = 13
                    fantome.y = 10
                    fantome.mode = "chasse"
                else:
                    # Pac-Man meurt
                    self.vies -= 1
                    if self.vies <= 0:
                        self.jeu_termine = True
                    else:
                        # Remettre Pac-Man à sa position de départ
                        self.pacman.x = 13
                        self.pacman.y = 16
                        self.pacman.direction = DROITE
    
    def manger_point(self):
        if self.labyrinthe[self.pacman.y][self.pacman.x] == 2:
            self.labyrinthe[self.pacman.y][self.pacman.x] = 0
            self.score += 10
            self.points_manges += 1
            self.creer_particules_score(self.pacman.x, self.pacman.y)
            
        elif self.labyrinthe[self.pacman.y][self.pacman.x] == 3:
            self.labyrinthe[self.pacman.y][self.pacman.x] = 0
            self.score += 50
            self.points_manges += 1
            self.pacman.manger_gros_point()
            self.creer_particules_score(self.pacman.x, self.pacman.y)
        
        # Vérifier victoire
        if self.points_manges >= self.points_totaux:
            self.victoire = True
            self.jeu_termine = True
    
    def creer_particules_score(self, x, y):
        for _ in range(5):
            particule = {
                'x': x * TAILLE_CASE + TAILLE_CASE // 2,
                'y': y * TAILLE_CASE + TAILLE_CASE // 2,
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-3, -1),
                'vie': 20,
                'couleur': JAUNE_POINT
            }
            self.particules_score.append(particule)
    
    def mettre_a_jour_particules(self):
        for particule in self.particules_score[:]:
            particule['x'] += particule['vx']
            particule['y'] += particule['vy']
            particule['vy'] += 0.2  # Gravité
            particule['vie'] -= 1
            
            if particule['vie'] <= 0:
                self.particules_score.remove(particule)
    
    def dessiner_labyrinthe(self):
        for y, ligne in enumerate(self.labyrinthe):
            for x, case in enumerate(ligne):
                rect = pygame.Rect(x * TAILLE_CASE, y * TAILLE_CASE, 
                                 TAILLE_CASE, TAILLE_CASE)
                
                if case == 1:  # Mur
                    pygame.draw.rect(self.ecran, BLEU_LABYRINTHE, rect)
                    pygame.draw.rect(self.ecran, BLANC, rect, 1)
                elif case == 2:  # Point
                    centre_x = x * TAILLE_CASE + TAILLE_CASE // 2
                    centre_y = y * TAILLE_CASE + TAILLE_CASE // 2
                    pygame.draw.circle(self.ecran, JAUNE_POINT, (centre_x, centre_y), 2)
                elif case == 3:  # Gros point
                    centre_x = x * TAILLE_CASE + TAILLE_CASE // 2
                    centre_y = y * TAILLE_CASE + TAILLE_CASE // 2
                    pygame.draw.circle(self.ecran, BLANC_GROS_POINT, (centre_x, centre_y), 6)
                    pygame.draw.circle(self.ecran, JAUNE_POINT, (centre_x, centre_y), 4)
    
    def dessiner_interface(self):
        # Score
        texte_score = self.font.render(f"Score: {self.score}", True, BLANC)
        self.ecran.blit(texte_score, (10, 10))
        
        # Vies
        texte_vies = self.font.render(f"Vies: {self.vies}", True, BLANC)
        self.ecran.blit(texte_vies, (200, 10))
        
        # Niveau
        texte_niveau = self.font.render(f"Niveau: {self.niveau}", True, BLANC)
        self.ecran.blit(texte_niveau, (350, 10))
        
        # Temps d'invincibilité restant
        if self.pacman.invincible:
            temps_restant = self.pacman.temps_invincible // 60 + 1
            texte_invincible = self.font.render(f"Invincible: {temps_restant}s", True, BLANC_GROS_POINT)
            self.ecran.blit(texte_invincible, (500, 10))
        
        # Particules de score
        for particule in self.particules_score:
            if particule['vie'] > 0:
                pygame.draw.circle(self.ecran, particule['couleur'], 
                                 (int(particule['x']), int(particule['y'])), 2)
        
        # Instructions
        instructions = ["WASD ou Flèches: Déplacer", "R: Redémarrer"]
        for i, instruction in enumerate(instructions):
            texte = pygame.font.Font(None, 24).render(instruction, True, GRIS)
            self.ecran.blit(texte, (10, HAUTEUR - 50 + i * 25))
    
    def dessiner_fin_jeu(self):
        if self.jeu_termine:
            # Fond semi-transparent
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(200)
            overlay.fill(NOIR)
            self.ecran.blit(overlay, (0, 0))
            
            if self.victoire:
                texte_fin = self.font_grand.render("VICTOIRE!", True, JAUNE_PACMAN)
                couleur_fond = JAUNE_PACMAN
            else:
                texte_fin = self.font_grand.render("GAME OVER", True, ROUGE_FANTOME)
                couleur_fond = ROUGE_FANTOME
            
            rect_fin = texte_fin.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 50))
            
            # Fond coloré
            fond_rect = rect_fin.inflate(50, 30)
            pygame.draw.rect(self.ecran, couleur_fond, fond_rect, border_radius=15)
            pygame.draw.rect(self.ecran, BLANC, fond_rect, width=3, border_radius=15)
            
            self.ecran.blit(texte_fin, rect_fin)
            
            # Score final
            texte_score_final = self.font.render(f"Score final: {self.score}", True, BLANC)
            rect_score_final = texte_score_final.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            self.ecran.blit(texte_score_final, rect_score_final)
            
            # Instructions
            texte_recommencer = pygame.font.Font(None, 24).render("R: Recommencer | Q: Quitter", True, BLANC)
            rect_recommencer = texte_recommencer.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 50))
            self.ecran.blit(texte_recommencer, rect_recommencer)
    
    def reinitialiser(self):
        self.__init__()
    
    def mettre_a_jour(self):
        if not self.jeu_termine:
            # Mettre à jour Pac-Man
            self.pacman.mettre_a_jour(self.labyrinthe)
            
            # Manger les points
            self.manger_point()
            
            # Mettre à jour les fantômes
            for fantome in self.fantomes:
                fantome.mettre_a_jour(self.pacman, self.labyrinthe)
            
            # Vérifier les collisions
            self.verifier_collisions()
        
        # Mettre à jour les particules
        self.mettre_a_jour_particules()
    
    def dessiner(self):
        self.ecran.fill(NOIR)
        
        # Labyrinthe
        self.dessiner_labyrinthe()
        
        # Objets du jeu
        self.pacman.dessiner(self.ecran)
        for fantome in self.fantomes:
            fantome.dessiner(self.ecran)
        
        # Interface
        self.dessiner_interface()
        
        # Fin de jeu
        if self.jeu_termine:
            self.dessiner_fin_jeu()
        
        pygame.display.flip()
    
    def executer(self):
        en_cours = True
        
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reinitialiser()
                    elif event.key == pygame.K_q and self.jeu_termine:
                        en_cours = False
                    
                    # Contrôles de Pac-Man
                    elif not self.jeu_termine:
                        if event.key in [pygame.K_UP, pygame.K_w]:
                            self.pacman.changer_direction(HAUT)
                        elif event.key in [pygame.K_DOWN, pygame.K_s]:
                            self.pacman.changer_direction(BAS)
                        elif event.key in [pygame.K_LEFT, pygame.K_a]:
                            self.pacman.changer_direction(GAUCHE)
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                            self.pacman.changer_direction(DROITE)
            
            self.mettre_a_jour()
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuPacman()
    jeu.executer()