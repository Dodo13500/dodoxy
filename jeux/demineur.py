import pygame
import random
import sys
import math

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 800
HAUTEUR = 600
TAILLE_CASE = 30
FPS = 60

# Couleurs réalistes
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
GRIS = (128, 128, 128)
GRIS_CLAIR = (200, 200, 200)
GRIS_FONCE = (64, 64, 64)
ROUGE = (220, 20, 60)
VERT = (34, 139, 34)
BLEU = (30, 144, 255)
JAUNE = (255, 215, 0)
ORANGE = (255, 165, 0)
VIOLET = (138, 43, 226)
MARRON = (139, 69, 19)
ROSE = (255, 192, 203)

# Couleurs pour les chiffres
COULEURS_CHIFFRES = {
    1: BLEU,
    2: VERT,
    3: ROUGE,
    4: (75, 0, 130),  # Indigo
    5: MARRON,
    6: (0, 128, 128),  # Teal
    7: NOIR,
    8: GRIS_FONCE
}

class Case:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.est_mine = False
        self.est_revelee = False
        self.est_marquee = False
        self.nombre_mines_adjacentes = 0
        self.animation = 0
        self.particules = []
    
    def creer_particules_explosion(self):
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            vitesse = random.uniform(3, 8)
            particule = {
                'x': self.x * TAILLE_CASE + TAILLE_CASE // 2,
                'y': self.y * TAILLE_CASE + TAILLE_CASE // 2,
                'vx': math.cos(angle) * vitesse,
                'vy': math.sin(angle) * vitesse,
                'vie': 30,
                'couleur': random.choice([ROUGE, ORANGE, JAUNE])
            }
            self.particules.append(particule)
    
    def mettre_a_jour_particules(self):
        for particule in self.particules[:]:
            particule['x'] += particule['vx']
            particule['y'] += particule['vy']
            particule['vx'] *= 0.98
            particule['vy'] += 0.3  # Gravité
            particule['vie'] -= 1
            
            if particule['vie'] <= 0:
                self.particules.remove(particule)
    
    def dessiner(self, surface, offset_x, offset_y, jeu_termine=False, mine_cliquee=False):
        x_ecran = offset_x + self.x * TAILLE_CASE
        y_ecran = offset_y + self.y * TAILLE_CASE
        rect = pygame.Rect(x_ecran, y_ecran, TAILLE_CASE, TAILLE_CASE)
        
        if not self.est_revelee:
            # Case non révélée
            if self.est_marquee:
                # Drapeau
                pygame.draw.rect(surface, GRIS_CLAIR, rect)
                pygame.draw.rect(surface, NOIR, rect, 2)
                
                # Dessiner le drapeau
                pygame.draw.polygon(surface, ROUGE, [
                    (x_ecran + 8, y_ecran + 5),
                    (x_ecran + 22, y_ecran + 8),
                    (x_ecran + 8, y_ecran + 15)
                ])
                pygame.draw.line(surface, NOIR, 
                               (x_ecran + 8, y_ecran + 5), 
                               (x_ecran + 8, y_ecran + 25), 3)
            else:
                # Case normale non révélée avec effet 3D
                pygame.draw.rect(surface, GRIS_CLAIR, rect)
                pygame.draw.rect(surface, BLANC, (x_ecran, y_ecran, TAILLE_CASE-2, TAILLE_CASE-2))
                pygame.draw.rect(surface, GRIS_FONCE, (x_ecran+2, y_ecran+2, TAILLE_CASE-2, TAILLE_CASE-2))
                pygame.draw.rect(surface, GRIS, (x_ecran+1, y_ecran+1, TAILLE_CASE-2, TAILLE_CASE-2))
        
        else:
            # Case révélée
            if self.est_mine:
                # Mine
                couleur_fond = ROUGE if mine_cliquee else GRIS_FONCE
                pygame.draw.rect(surface, couleur_fond, rect)
                pygame.draw.rect(surface, NOIR, rect, 2)
                
                # Dessiner la mine
                centre_x = x_ecran + TAILLE_CASE // 2
                centre_y = y_ecran + TAILLE_CASE // 2
                
                # Corps de la mine
                pygame.draw.circle(surface, NOIR, (centre_x, centre_y), 8)
                
                # Pointes de la mine
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    x_pointe = centre_x + math.cos(rad) * 12
                    y_pointe = centre_y + math.sin(rad) * 12
                    pygame.draw.line(surface, NOIR, (centre_x, centre_y), 
                                   (x_pointe, y_pointe), 2)
                
                # Reflet sur la mine
                pygame.draw.circle(surface, GRIS, (centre_x - 3, centre_y - 3), 3)
                
            else:
                # Case vide ou avec chiffre
                pygame.draw.rect(surface, BLANC, rect)
                pygame.draw.rect(surface, GRIS, rect, 1)
                
                if self.nombre_mines_adjacentes > 0:
                    # Dessiner le chiffre
                    font = pygame.font.Font(None, 24)
                    couleur = COULEURS_CHIFFRES[self.nombre_mines_adjacentes]
                    texte = font.render(str(self.nombre_mines_adjacentes), True, couleur)
                    rect_texte = texte.get_rect(center=(x_ecran + TAILLE_CASE//2, 
                                                      y_ecran + TAILLE_CASE//2))
                    surface.blit(texte, rect_texte)
        
        # Animation de révélation
        if self.animation > 0:
            self.animation -= 2
            alpha = self.animation * 8
            if alpha > 0:
                overlay = pygame.Surface((TAILLE_CASE, TAILLE_CASE))
                overlay.set_alpha(alpha)
                overlay.fill(JAUNE)
                surface.blit(overlay, (x_ecran, y_ecran))
        
        # Particules d'explosion
        for particule in self.particules:
            if particule['vie'] > 0:
                pygame.draw.circle(surface, particule['couleur'], 
                                 (int(particule['x']), int(particule['y'])), 3)

class JeuDemineur:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Démineur Réaliste")
        self.horloge = pygame.time.Clock()
        
        # Paramètres du jeu
        self.largeur_grille = 16
        self.hauteur_grille = 16
        self.nombre_mines = 40
        
        # Calculer les offsets pour centrer la grille
        self.offset_x = (LARGEUR - self.largeur_grille * TAILLE_CASE) // 2
        self.offset_y = 80
        
        # État du jeu
        self.grille = []
        self.jeu_termine = False
        self.victoire = False
        self.premiere_case = True
        self.temps_debut = 0
        self.temps_jeu = 0
        self.mines_marquees = 0
        
        # Interface
        self.font = pygame.font.Font(None, 36)
        self.font_petit = pygame.font.Font(None, 24)
        self.font_grand = pygame.font.Font(None, 48)
        
        # Effets visuels
        self.particules_victoire = []
        self.case_cliquee = None
        
        # Initialiser la grille
        self.initialiser_grille()
    
    def initialiser_grille(self):
        self.grille = []
        for y in range(self.hauteur_grille):
            ligne = []
            for x in range(self.largeur_grille):
                ligne.append(Case(x, y))
            self.grille.append(ligne)
        
        self.jeu_termine = False
        self.victoire = False
        self.premiere_case = True
        self.temps_debut = 0
        self.temps_jeu = 0
        self.mines_marquees = 0
        self.particules_victoire = []
        self.case_cliquee = None
    
    def placer_mines(self, premiere_x, premiere_y):
        mines_placees = 0
        while mines_placees < self.nombre_mines:
            x = random.randint(0, self.largeur_grille - 1)
            y = random.randint(0, self.hauteur_grille - 1)
            
            # Ne pas placer de mine sur la première case cliquée ou ses voisins
            if (abs(x - premiere_x) <= 1 and abs(y - premiere_y) <= 1):
                continue
            
            if not self.grille[y][x].est_mine:
                self.grille[y][x].est_mine = True
                mines_placees += 1
        
        # Calculer les nombres pour chaque case
        for y in range(self.hauteur_grille):
            for x in range(self.largeur_grille):
                if not self.grille[y][x].est_mine:
                    self.grille[y][x].nombre_mines_adjacentes = self.compter_mines_adjacentes(x, y)
    
    def compter_mines_adjacentes(self, x, y):
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.largeur_grille and 0 <= ny < self.hauteur_grille):
                    if self.grille[ny][nx].est_mine:
                        count += 1
        return count
    
    def obtenir_case_cliquee(self, pos_souris):
        x_souris, y_souris = pos_souris
        
        if (self.offset_x <= x_souris <= self.offset_x + self.largeur_grille * TAILLE_CASE and
            self.offset_y <= y_souris <= self.offset_y + self.hauteur_grille * TAILLE_CASE):
            
            x_case = (x_souris - self.offset_x) // TAILLE_CASE
            y_case = (y_souris - self.offset_y) // TAILLE_CASE
            
            if 0 <= x_case < self.largeur_grille and 0 <= y_case < self.hauteur_grille:
                return x_case, y_case
        
        return None, None
    
    def reveler_case(self, x, y):
        if (x < 0 or x >= self.largeur_grille or y < 0 or y >= self.hauteur_grille):
            return
        
        case = self.grille[y][x]
        
        if case.est_revelee or case.est_marquee:
            return
        
        # Première case cliquée
        if self.premiere_case:
            self.placer_mines(x, y)
            self.premiere_case = False
            self.temps_debut = pygame.time.get_ticks()
        
        case.est_revelee = True
        case.animation = 30
        
        if case.est_mine:
            # Mine cliquée - fin de jeu
            self.jeu_termine = True
            self.case_cliquee = (x, y)
            case.creer_particules_explosion()
            
            # Révéler toutes les mines
            for ligne in self.grille:
                for c in ligne:
                    if c.est_mine:
                        c.est_revelee = True
        
        elif case.nombre_mines_adjacentes == 0:
            # Case vide - révéler les cases adjacentes
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    self.reveler_case(x + dx, y + dy)
        
        # Vérifier victoire
        self.verifier_victoire()
    
    def marquer_case(self, x, y):
        if (x < 0 or x >= self.largeur_grille or y < 0 or y >= self.hauteur_grille):
            return
        
        case = self.grille[y][x]
        
        if not case.est_revelee:
            case.est_marquee = not case.est_marquee
            if case.est_marquee:
                self.mines_marquees += 1
            else:
                self.mines_marquees -= 1
    
    def verifier_victoire(self):
        cases_non_revelees = 0
        for ligne in self.grille:
            for case in ligne:
                if not case.est_revelee and not case.est_mine:
                    cases_non_revelees += 1
        
        if cases_non_revelees == 0:
            self.victoire = True
            self.jeu_termine = True
            self.creer_particules_victoire()
    
    def creer_particules_victoire(self):
        for _ in range(100):
            x = random.randint(0, LARGEUR)
            y = random.randint(0, HAUTEUR)
            particule = {
                'x': x,
                'y': y,
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-5, -2),
                'vie': 60,
                'couleur': random.choice([VERT, JAUNE, BLEU, BLANC])
            }
            self.particules_victoire.append(particule)
    
    def mettre_a_jour_particules(self):
        # Particules de victoire
        for particule in self.particules_victoire[:]:
            particule['x'] += particule['vx']
            particule['y'] += particule['vy']
            particule['vy'] += 0.2  # Gravité
            particule['vie'] -= 1
            
            if particule['vie'] <= 0:
                self.particules_victoire.remove(particule)
        
        # Particules des cases
        for ligne in self.grille:
            for case in ligne:
                case.mettre_a_jour_particules()
    
    def dessiner_interface(self):
        # Titre
        texte_titre = self.font.render("DÉMINEUR", True, NOIR)
        rect_titre = texte_titre.get_rect(center=(LARGEUR//2, 25))
        self.ecran.blit(texte_titre, rect_titre)
        
        # Informations de jeu
        y_info = 50
        
        # Mines restantes
        mines_restantes = self.nombre_mines - self.mines_marquees
        texte_mines = self.font_petit.render(f"Mines: {mines_restantes}", True, ROUGE)
        self.ecran.blit(texte_mines, (50, y_info))
        
        # Temps
        if not self.premiere_case and not self.jeu_termine:
            self.temps_jeu = (pygame.time.get_ticks() - self.temps_debut) // 1000
        
        texte_temps = self.font_petit.render(f"Temps: {self.temps_jeu}s", True, BLEU)
        self.ecran.blit(texte_temps, (LARGEUR - 150, y_info))
        
        # Instructions
        if not self.jeu_termine:
            instructions = [
                "Clic gauche: Révéler",
                "Clic droit: Marquer",
                "R: Nouvelle partie"
            ]
            
            for i, instruction in enumerate(instructions):
                texte = self.font_petit.render(instruction, True, GRIS_FONCE)
                self.ecran.blit(texte, (10, HAUTEUR - 80 + i * 25))
    
    def dessiner_fin_jeu(self):
        if self.jeu_termine:
            # Fond semi-transparent
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(200)
            overlay.fill(NOIR)
            self.ecran.blit(overlay, (0, 0))
            
            if self.victoire:
                texte_fin = self.font_grand.render("VICTOIRE!", True, VERT)
                couleur_fond = VERT
            else:
                texte_fin = self.font_grand.render("EXPLOSION!", True, ROUGE)
                couleur_fond = ROUGE
            
            rect_fin = texte_fin.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 50))
            
            # Fond coloré
            fond_rect = rect_fin.inflate(50, 30)
            pygame.draw.rect(self.ecran, couleur_fond, fond_rect, border_radius=15)
            pygame.draw.rect(self.ecran, BLANC, fond_rect, width=3, border_radius=15)
            
            self.ecran.blit(texte_fin, rect_fin)
            
            # Temps final
            texte_temps_final = self.font.render(f"Temps: {self.temps_jeu}s", True, BLANC)
            rect_temps_final = texte_temps_final.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            self.ecran.blit(texte_temps_final, rect_temps_final)
            
            # Instructions
            texte_recommencer = self.font_petit.render("R: Nouvelle partie | D: Changer difficulté | Q: Quitter", True, BLANC)
            rect_recommencer = texte_recommencer.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 50))
            self.ecran.blit(texte_recommencer, rect_recommencer)
        
        # Particules de victoire
        for particule in self.particules_victoire:
            if particule['vie'] > 0:
                pygame.draw.circle(self.ecran, particule['couleur'], 
                                 (int(particule['x']), int(particule['y'])), 3)
    
    def changer_difficulte(self):
        # Cycle entre les difficultés
        if (self.largeur_grille, self.hauteur_grille, self.nombre_mines) == (9, 9, 10):
            # Facile -> Moyen
            self.largeur_grille, self.hauteur_grille, self.nombre_mines = 16, 16, 40
        elif (self.largeur_grille, self.hauteur_grille, self.nombre_mines) == (16, 16, 40):
            # Moyen -> Difficile
            self.largeur_grille, self.hauteur_grille, self.nombre_mines = 30, 16, 99
        else:
            # Difficile -> Facile
            self.largeur_grille, self.hauteur_grille, self.nombre_mines = 9, 9, 10
        
        # Recalculer les offsets
        self.offset_x = (LARGEUR - self.largeur_grille * TAILLE_CASE) // 2
        self.offset_y = 80
        
        # Ajuster la taille de la fenêtre si nécessaire
        nouvelle_largeur = max(LARGEUR, self.largeur_grille * TAILLE_CASE + 100)
        nouvelle_hauteur = max(HAUTEUR, self.hauteur_grille * TAILLE_CASE + 200)
        
        if nouvelle_largeur != LARGEUR or nouvelle_hauteur != HAUTEUR:
            self.ecran = pygame.display.set_mode((nouvelle_largeur, nouvelle_hauteur))
        
        self.initialiser_grille()
    
    def dessiner(self):
        self.ecran.fill(GRIS_CLAIR)
        
        # Grille
        for ligne in self.grille:
            for case in ligne:
                mine_cliquee = (self.case_cliquee == (case.x, case.y))
                case.dessiner(self.ecran, self.offset_x, self.offset_y, 
                            self.jeu_termine, mine_cliquee)
        
        # Bordure de la grille
        grille_rect = pygame.Rect(self.offset_x - 2, self.offset_y - 2,
                                self.largeur_grille * TAILLE_CASE + 4,
                                self.hauteur_grille * TAILLE_CASE + 4)
        pygame.draw.rect(self.ecran, NOIR, grille_rect, 3)
        
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
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.jeu_termine:
                        x_case, y_case = self.obtenir_case_cliquee(event.pos)
                        if x_case is not None and y_case is not None:
                            if event.button == 1:  # Clic gauche
                                self.reveler_case(x_case, y_case)
                            elif event.button == 3:  # Clic droit
                                self.marquer_case(x_case, y_case)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.initialiser_grille()
                    elif event.key == pygame.K_d:
                        self.changer_difficulte()
                    elif event.key == pygame.K_q and self.jeu_termine:
                        en_cours = False
            
            # Mettre à jour les particules
            self.mettre_a_jour_particules()
            
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuDemineur()
    jeu.executer()