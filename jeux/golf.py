import pygame
import math
import random
import sys

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 1000
HAUTEUR = 700
FPS = 60

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
VERT = (34, 139, 34)
VERT_FONCE = (0, 100, 0)
ROUGE = (255, 0, 0)
BLEU = (0, 0, 255)
JAUNE = (255, 255, 0)
MARRON = (139, 69, 19)
GRIS = (128, 128, 128)
ORANGE = (255, 165, 0)

class Balle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vitesse_x = 0
        self.vitesse_y = 0
        self.rayon = 8
        self.friction = 0.98
        self.en_mouvement = False
    
    def appliquer_force(self, force_x, force_y):
        self.vitesse_x = force_x
        self.vitesse_y = force_y
        self.en_mouvement = True
    
    def mettre_a_jour(self):
        if self.en_mouvement:
            # Appliquer la vitesse
            self.x += self.vitesse_x
            self.y += self.vitesse_y
            
            # Appliquer la friction
            self.vitesse_x *= self.friction
            self.vitesse_y *= self.friction
            
            # Arrêter si la vitesse est très faible
            if abs(self.vitesse_x) < 0.1 and abs(self.vitesse_y) < 0.1:
                self.vitesse_x = 0
                self.vitesse_y = 0
                self.en_mouvement = False
    
    def rebondir_mur(self, largeur, hauteur):
        if self.x - self.rayon <= 0 or self.x + self.rayon >= largeur:
            self.vitesse_x = -self.vitesse_x * 0.8
            self.x = max(self.rayon, min(largeur - self.rayon, self.x))
        
        if self.y - self.rayon <= 0 or self.y + self.rayon >= hauteur:
            self.vitesse_y = -self.vitesse_y * 0.8
            self.y = max(self.rayon, min(hauteur - self.rayon, self.y))
    
    def dessiner(self, surface):
        pygame.draw.circle(surface, BLANC, (int(self.x), int(self.y)), self.rayon)
        pygame.draw.circle(surface, NOIR, (int(self.x), int(self.y)), self.rayon, 2)

class Trou:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rayon = 15
    
    def contient_balle(self, balle):
        distance = math.sqrt((balle.x - self.x)**2 + (balle.y - self.y)**2)
        return distance < self.rayon - balle.rayon + 5
    
    def dessiner(self, surface):
        pygame.draw.circle(surface, NOIR, (int(self.x), int(self.y)), self.rayon)
        pygame.draw.circle(surface, VERT_FONCE, (int(self.x), int(self.y)), self.rayon - 3)

class Obstacle:
    def __init__(self, x, y, largeur, hauteur, type_obstacle="rectangle"):
        self.x = x
        self.y = y
        self.largeur = largeur
        self.hauteur = hauteur
        self.type = type_obstacle
    
    def collision_avec_balle(self, balle):
        if self.type == "rectangle":
            return (self.x <= balle.x + balle.rayon and 
                   balle.x - balle.rayon <= self.x + self.largeur and
                   self.y <= balle.y + balle.rayon and 
                   balle.y - balle.rayon <= self.y + self.hauteur)
        elif self.type == "cercle":
            distance = math.sqrt((balle.x - (self.x + self.largeur/2))**2 + 
                               (balle.y - (self.y + self.hauteur/2))**2)
            return distance < balle.rayon + min(self.largeur, self.hauteur)/2
    
    def gerer_collision(self, balle):
        if self.collision_avec_balle(balle):
            if self.type == "rectangle":
                # Déterminer de quel côté la balle a touché
                centre_x = self.x + self.largeur / 2
                centre_y = self.y + self.hauteur / 2
                
                dx = balle.x - centre_x
                dy = balle.y - centre_y
                
                if abs(dx) > abs(dy):
                    balle.vitesse_x = -balle.vitesse_x * 0.8
                    if dx > 0:
                        balle.x = self.x + self.largeur + balle.rayon
                    else:
                        balle.x = self.x - balle.rayon
                else:
                    balle.vitesse_y = -balle.vitesse_y * 0.8
                    if dy > 0:
                        balle.y = self.y + self.hauteur + balle.rayon
                    else:
                        balle.y = self.y - balle.rayon
            
            elif self.type == "cercle":
                centre_x = self.x + self.largeur / 2
                centre_y = self.y + self.hauteur / 2
                
                # Calculer l'angle de collision
                angle = math.atan2(balle.y - centre_y, balle.x - centre_x)
                
                # Éloigner la balle
                rayon_obstacle = min(self.largeur, self.hauteur) / 2
                balle.x = centre_x + math.cos(angle) * (rayon_obstacle + balle.rayon + 1)
                balle.y = centre_y + math.sin(angle) * (rayon_obstacle + balle.rayon + 1)
                
                # Inverser la vitesse selon l'angle
                vitesse_totale = math.sqrt(balle.vitesse_x**2 + balle.vitesse_y**2)
                balle.vitesse_x = math.cos(angle) * vitesse_totale * 0.8
                balle.vitesse_y = math.sin(angle) * vitesse_totale * 0.8
    
    def dessiner(self, surface):
        if self.type == "rectangle":
            pygame.draw.rect(surface, MARRON, (self.x, self.y, self.largeur, self.hauteur))
            pygame.draw.rect(surface, NOIR, (self.x, self.y, self.largeur, self.hauteur), 2)
        elif self.type == "cercle":
            rayon = min(self.largeur, self.hauteur) // 2
            centre_x = self.x + self.largeur // 2
            centre_y = self.y + self.hauteur // 2
            pygame.draw.circle(surface, GRIS, (centre_x, centre_y), rayon)
            pygame.draw.circle(surface, NOIR, (centre_x, centre_y), rayon, 2)

class Niveau:
    def __init__(self, numero):
        self.numero = numero
        self.balle_depart = None
        self.trou = None
        self.obstacles = []
        self.par = 3
        self.generer_niveau()
    
    def generer_niveau(self):
        if self.numero == 1:
            # Niveau simple
            self.balle_depart = (100, HAUTEUR // 2)
            self.trou = Trou(LARGEUR - 100, HAUTEUR // 2)
            self.obstacles = [
                Obstacle(LARGEUR // 2 - 50, HAUTEUR // 2 - 100, 100, 50),
                Obstacle(LARGEUR // 2 - 50, HAUTEUR // 2 + 50, 100, 50)
            ]
            self.par = 2
        
        elif self.numero == 2:
            # Niveau avec obstacles circulaires
            self.balle_depart = (80, 100)
            self.trou = Trou(LARGEUR - 80, HAUTEUR - 100)
            self.obstacles = [
                Obstacle(300, 200, 80, 80, "cercle"),
                Obstacle(600, 300, 80, 80, "cercle"),
                Obstacle(400, 450, 100, 30)
            ]
            self.par = 3
        
        elif self.numero == 3:
            # Niveau labyrinthe
            self.balle_depart = (50, 50)
            self.trou = Trou(LARGEUR - 50, HAUTEUR - 50)
            self.obstacles = [
                Obstacle(200, 0, 20, 300),
                Obstacle(400, 200, 20, 300),
                Obstacle(600, 0, 20, 400),
                Obstacle(0, 300, 250, 20),
                Obstacle(300, 500, 350, 20)
            ]
            self.par = 4
        
        elif self.numero == 4:
            # Niveau complexe
            self.balle_depart = (LARGEUR // 2, HAUTEUR - 50)
            self.trou = Trou(LARGEUR // 2, 50)
            self.obstacles = [
                Obstacle(200, 200, 60, 60, "cercle"),
                Obstacle(600, 200, 60, 60, "cercle"),
                Obstacle(400, 350, 60, 60, "cercle"),
                Obstacle(100, 400, 200, 20),
                Obstacle(600, 400, 200, 20),
                Obstacle(350, 150, 100, 20)
            ]
            self.par = 4
        
        else:
            # Niveau aléatoire
            self.balle_depart = (random.randint(50, 150), random.randint(50, HAUTEUR - 50))
            self.trou = Trou(random.randint(LARGEUR - 150, LARGEUR - 50), 
                           random.randint(50, HAUTEUR - 50))
            
            self.obstacles = []
            for _ in range(random.randint(3, 6)):
                x = random.randint(200, LARGEUR - 300)
                y = random.randint(100, HAUTEUR - 200)
                if random.choice([True, False]):
                    # Obstacle rectangulaire
                    largeur = random.randint(50, 150)
                    hauteur = random.randint(20, 80)
                    self.obstacles.append(Obstacle(x, y, largeur, hauteur))
                else:
                    # Obstacle circulaire
                    taille = random.randint(40, 80)
                    self.obstacles.append(Obstacle(x, y, taille, taille, "cercle"))
            
            self.par = random.randint(3, 5)

class JeuGolf:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Mini Golf")
        self.horloge = pygame.time.Clock()
        
        # État du jeu
        self.niveau_actuel = 1
        self.niveau = Niveau(self.niveau_actuel)
        self.balle = Balle(*self.niveau.balle_depart)
        self.coups = 0
        self.score_total = 0
        
        # Contrôles
        self.viser = False
        self.position_souris = (0, 0)
        self.force_max = 15
        
        # Interface
        self.font = pygame.font.Font(None, 36)
        self.font_petit = pygame.font.Font(None, 24)
        
        # État de fin de niveau
        self.niveau_termine = False
        self.temps_fin_niveau = 0
        
        # État de fin de jeu
        self.jeu_termine = False
        self.nombre_niveaux = 5
    
    def calculer_force(self, pos_souris):
        dx = pos_souris[0] - self.balle.x
        dy = pos_souris[1] - self.balle.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Limiter la force
        if distance > 100:
            distance = 100
        
        force = distance / 100 * self.force_max
        angle = math.atan2(dy, dx)
        
        force_x = math.cos(angle) * force
        force_y = math.sin(angle) * force
        
        return force_x, force_y
    
    def niveau_suivant(self):
        self.niveau_actuel += 1
        if self.niveau_actuel > self.nombre_niveaux:
            self.jeu_termine = True
            return
        
        self.niveau = Niveau(self.niveau_actuel)
        self.balle = Balle(*self.niveau.balle_depart)
        self.coups = 0
        self.niveau_termine = False
    
    def reinitialiser_niveau(self):
        self.balle = Balle(*self.niveau.balle_depart)
        self.coups = 0
        self.niveau_termine = False
    
    def reinitialiser_jeu(self):
        self.niveau_actuel = 1
        self.niveau = Niveau(self.niveau_actuel)
        self.balle = Balle(*self.niveau.balle_depart)
        self.coups = 0
        self.score_total = 0
        self.niveau_termine = False
        self.jeu_termine = False
    
    def dessiner_visee(self):
        if self.viser and not self.balle.en_mouvement:
            # Ligne de visée
            pygame.draw.line(self.ecran, ROUGE, 
                           (int(self.balle.x), int(self.balle.y)), 
                           self.position_souris, 2)
            
            # Indicateur de force
            dx = self.position_souris[0] - self.balle.x
            dy = self.position_souris[1] - self.balle.y
            distance = math.sqrt(dx**2 + dy**2)
            force_pourcentage = min(distance / 100, 1.0)
            
            # Barre de force
            barre_x = 10
            barre_y = HAUTEUR - 60
            barre_largeur = 200
            barre_hauteur = 20
            
            pygame.draw.rect(self.ecran, GRIS, (barre_x, barre_y, barre_largeur, barre_hauteur))
            pygame.draw.rect(self.ecran, ROUGE, (barre_x, barre_y, 
                           int(barre_largeur * force_pourcentage), barre_hauteur))
            pygame.draw.rect(self.ecran, NOIR, (barre_x, barre_y, barre_largeur, barre_hauteur), 2)
            
            texte_force = self.font_petit.render("Force", True, NOIR)
            self.ecran.blit(texte_force, (barre_x, barre_y - 25))
    
    def dessiner_interface(self):
        # Informations du niveau
        texte_niveau = self.font.render(f"Niveau: {self.niveau_actuel}", True, NOIR)
        self.ecran.blit(texte_niveau, (10, 10))
        
        texte_coups = self.font.render(f"Coups: {self.coups}", True, NOIR)
        self.ecran.blit(texte_coups, (10, 50))
        
        texte_par = self.font.render(f"Par: {self.niveau.par}", True, NOIR)
        self.ecran.blit(texte_par, (10, 90))
        
        texte_score = self.font.render(f"Score total: {self.score_total}", True, NOIR)
        self.ecran.blit(texte_score, (10, 130))
        
        # Instructions
        if self.coups == 0:
            instructions = [
                "Cliquez et glissez pour viser",
                "Relâchez pour frapper la balle"
            ]
            for i, instruction in enumerate(instructions):
                texte = self.font_petit.render(instruction, True, NOIR)
                self.ecran.blit(texte, (LARGEUR - 250, 10 + i * 25))
    
    def dessiner_fin_niveau(self):
        if self.niveau_termine:
            # Calculer le score pour ce niveau
            difference = self.coups - self.niveau.par
            if difference <= -2:
                message = "EAGLE!"
                couleur = BLEU
            elif difference == -1:
                message = "BIRDIE!"
                couleur = VERT
            elif difference == 0:
                message = "PAR!"
                couleur = NOIR
            elif difference == 1:
                message = "BOGEY"
                couleur = ORANGE
            else:
                message = "DOUBLE BOGEY+"
                couleur = ROUGE
            
            # Fond semi-transparent
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(128)
            overlay.fill(BLANC)
            self.ecran.blit(overlay, (0, 0))
            
            # Message
            texte_message = self.font.render(message, True, couleur)
            rect_message = texte_message.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 50))
            self.ecran.blit(texte_message, rect_message)
            
            # Détails
            texte_coups = self.font.render(f"Coups: {self.coups} (Par: {self.niveau.par})", True, NOIR)
            rect_coups = texte_coups.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            self.ecran.blit(texte_coups, rect_coups)
            
            # Instructions
            if self.niveau_actuel < self.nombre_niveaux:
                texte_suivant = self.font_petit.render("Appuyez sur ESPACE pour le niveau suivant", True, NOIR)
                rect_suivant = texte_suivant.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 50))
                self.ecran.blit(texte_suivant, rect_suivant)
            
            texte_recommencer = self.font_petit.render("Appuyez sur R pour recommencer ce niveau", True, NOIR)
            rect_recommencer = texte_recommencer.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 80))
            self.ecran.blit(texte_recommencer, rect_recommencer)
    
    def dessiner_fin_jeu(self):
        if self.jeu_termine:
            # Fond semi-transparent
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(128)
            overlay.fill(BLANC)
            self.ecran.blit(overlay, (0, 0))
            
            # Message de fin
            texte_fin = self.font.render("FÉLICITATIONS!", True, VERT)
            rect_fin = texte_fin.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 80))
            self.ecran.blit(texte_fin, rect_fin)
            
            texte_termine = self.font.render("Vous avez terminé tous les niveaux!", True, NOIR)
            rect_termine = texte_termine.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 40))
            self.ecran.blit(texte_termine, rect_termine)
            
            # Score final
            texte_score_final = self.font.render(f"Score final: {self.score_total}", True, NOIR)
            rect_score_final = texte_score_final.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            self.ecran.blit(texte_score_final, rect_score_final)
            
            # Instructions
            texte_recommencer = self.font_petit.render("Appuyez sur N pour recommencer ou Q pour quitter", True, NOIR)
            rect_recommencer = texte_recommencer.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 50))
            self.ecran.blit(texte_recommencer, rect_recommencer)
    
    def dessiner(self):
        # Fond (herbe)
        self.ecran.fill(VERT)
        
        # Dessiner les obstacles
        for obstacle in self.niveau.obstacles:
            obstacle.dessiner(self.ecran)
        
        # Dessiner le trou
        self.niveau.trou.dessiner(self.ecran)
        
        # Dessiner la balle
        self.balle.dessiner(self.ecran)
        
        # Dessiner la visée
        self.dessiner_visee()
        
        # Interface
        self.dessiner_interface()
        
        # Écrans de fin
        if self.niveau_termine:
            self.dessiner_fin_niveau()
        
        if self.jeu_termine:
            self.dessiner_fin_jeu()
        
        pygame.display.flip()
    
    def executer(self):
        en_cours = True
        
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not self.balle.en_mouvement and not self.niveau_termine:
                        self.viser = True
                        self.position_souris = event.pos
                
                elif event.type == pygame.MOUSEMOTION:
                    if self.viser:
                        self.position_souris = event.pos
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.viser and not self.niveau_termine:
                        force_x, force_y = self.calculer_force(event.pos)
                        self.balle.appliquer_force(force_x, force_y)
                        self.coups += 1
                        self.viser = False
                
                elif event.type == pygame.KEYDOWN:
                    if self.niveau_termine:
                        if event.key == pygame.K_SPACE and self.niveau_actuel < self.nombre_niveaux:
                            self.score_total += self.coups
                            self.niveau_suivant()
                        elif event.key == pygame.K_r:
                            self.reinitialiser_niveau()
                    
                    if self.jeu_termine:
                        if event.key == pygame.K_n:
                            self.reinitialiser_jeu()
                        elif event.key == pygame.K_q:
                            en_cours = False
            
            if not self.niveau_termine and not self.jeu_termine:
                # Mettre à jour la balle
                self.balle.mettre_a_jour()
                
                # Vérifier les collisions avec les murs
                self.balle.rebondir_mur(LARGEUR, HAUTEUR)
                
                # Vérifier les collisions avec les obstacles
                for obstacle in self.niveau.obstacles:
                    obstacle.gerer_collision(self.balle)
                
                # Vérifier si la balle est dans le trou
                if self.niveau.trou.contient_balle(self.balle):
                    self.niveau_termine = True
                    self.temps_fin_niveau = pygame.time.get_ticks()
            
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuGolf()
    jeu.executer()