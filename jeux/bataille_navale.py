import pygame
import random
import sys

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 1200
HAUTEUR = 800
FPS = 60
TAILLE_CASE = 30

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU = (0, 100, 200)
BLEU_FONCE = (0, 50, 150)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
GRIS = (128, 128, 128)
GRIS_CLAIR = (200, 200, 200)
JAUNE = (255, 255, 0)
ORANGE = (255, 165, 0)

class Navire:
    def __init__(self, nom, taille, couleur):
        self.nom = nom
        self.taille = taille
        self.couleur = couleur
        self.positions = []
        self.touches = set()
        self.coule = False
        self.horizontal = True
    
    def placer(self, x, y, horizontal=True):
        self.positions = []
        self.horizontal = horizontal
        
        for i in range(self.taille):
            if horizontal:
                self.positions.append((x + i, y))
            else:
                self.positions.append((x, y + i))
    
    def est_touche(self, x, y):
        if (x, y) in self.positions:
            self.touches.add((x, y))
            if len(self.touches) == self.taille:
                self.coule = True
            return True
        return False
    
    def peut_etre_place(self, x, y, horizontal, grille):
        positions_test = []
        
        for i in range(self.taille):
            if horizontal:
                pos_x, pos_y = x + i, y
            else:
                pos_x, pos_y = x, y + i
            
            # Vérifier les limites
            if pos_x < 0 or pos_x >= 10 or pos_y < 0 or pos_y >= 10:
                return False
            
            # Vérifier si la case est libre
            if grille[pos_y][pos_x] != 0:
                return False
            
            positions_test.append((pos_x, pos_y))
        
        # Vérifier qu'aucun navire adjacent
        for pos_x, pos_y in positions_test:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    check_x, check_y = pos_x + dx, pos_y + dy
                    if (0 <= check_x < 10 and 0 <= check_y < 10 and 
                        grille[check_y][check_x] != 0):
                        return False
        
        return True

class Grille:
    def __init__(self):
        # 0 = eau, 1 = navire, 2 = touché, 3 = coulé, 4 = raté
        self.cases = [[0 for _ in range(10)] for _ in range(10)]
        self.navires = []
        self.tirs = set()
    
    def ajouter_navire(self, navire):
        self.navires.append(navire)
        for x, y in navire.positions:
            self.cases[y][x] = 1
    
    def tirer(self, x, y):
        if (x, y) in self.tirs:
            return "déjà tiré"
        
        self.tirs.add((x, y))
        
        # Vérifier si un navire est touché
        for navire in self.navires:
            if navire.est_touche(x, y):
                if navire.coule:
                    # Marquer toutes les cases du navire comme coulées
                    for pos_x, pos_y in navire.positions:
                        self.cases[pos_y][pos_x] = 3
                    return "coulé"
                else:
                    self.cases[y][x] = 2
                    return "touché"
        
        # Raté
        self.cases[y][x] = 4
        return "raté"
    
    def tous_navires_coules(self):
        return all(navire.coule for navire in self.navires)
    
    def placement_automatique(self):
        # Types de navires
        types_navires = [
            ("Porte-avions", 5, GRIS),
            ("Croiseur", 4, ROUGE),
            ("Contre-torpilleur", 3, VERT),
            ("Sous-marin", 3, JAUNE),
            ("Torpilleur", 2, ORANGE)
        ]
        
        for nom, taille, couleur in types_navires:
            navire = Navire(nom, taille, couleur)
            place = False
            tentatives = 0
            
            while not place and tentatives < 100:
                x = random.randint(0, 9)
                y = random.randint(0, 9)
                horizontal = random.choice([True, False])
                
                if navire.peut_etre_place(x, y, horizontal, self.cases):
                    navire.placer(x, y, horizontal)
                    self.ajouter_navire(navire)
                    place = True
                
                tentatives += 1

class IA:
    def __init__(self):
        self.mode = "chasse"  # "chasse" ou "destruction"
        self.derniere_touche = None
        self.cibles_potentielles = []
        self.tirs_effectues = set()
    
    def choisir_cible(self, grille_adversaire):
        if self.mode == "chasse":
            return self.chasse_aleatoire()
        else:
            return self.mode_destruction(grille_adversaire)
    
    def chasse_aleatoire(self):
        # Stratégie en damier pour optimiser
        cibles_possibles = []
        
        for y in range(10):
            for x in range(10):
                if (x, y) not in self.tirs_effectues:
                    # Damier: tirer sur les cases où x+y est pair
                    if (x + y) % 2 == 0:
                        cibles_possibles.append((x, y))
        
        # Si plus de cases en damier, prendre n'importe quelle case libre
        if not cibles_possibles:
            for y in range(10):
                for x in range(10):
                    if (x, y) not in self.tirs_effectues:
                        cibles_possibles.append((x, y))
        
        return random.choice(cibles_possibles) if cibles_possibles else None
    
    def mode_destruction(self, grille_adversaire):
        if not self.cibles_potentielles:
            # Chercher autour de la dernière touche
            if self.derniere_touche:
                x, y = self.derniere_touche
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                
                for dx, dy in directions:
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < 10 and 0 <= new_y < 10 and 
                        (new_x, new_y) not in self.tirs_effectues):
                        self.cibles_potentielles.append((new_x, new_y))
        
        if self.cibles_potentielles:
            return self.cibles_potentielles.pop(0)
        else:
            # Retourner en mode chasse
            self.mode = "chasse"
            return self.chasse_aleatoire()
    
    def traiter_resultat(self, x, y, resultat):
        self.tirs_effectues.add((x, y))
        
        if resultat == "touché":
            self.mode = "destruction"
            self.derniere_touche = (x, y)
            
            # Ajouter les cases adjacentes aux cibles potentielles
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < 10 and 0 <= new_y < 10 and 
                    (new_x, new_y) not in self.tirs_effectues and
                    (new_x, new_y) not in self.cibles_potentielles):
                    self.cibles_potentielles.append((new_x, new_y))
        
        elif resultat == "coulé":
            self.mode = "chasse"
            self.derniere_touche = None
            self.cibles_potentielles = []

class JeuBatailleNavale:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Bataille Navale")
        self.horloge = pygame.time.Clock()
        
        # Grilles
        self.grille_joueur = Grille()
        self.grille_ia = Grille()
        
        # IA
        self.ia = IA()
        
        # État du jeu
        self.phase = "placement"  # "placement", "jeu", "fin"
        self.tour_joueur = True
        self.navire_en_placement = None
        self.navires_a_placer = [
            ("Porte-avions", 5, GRIS),
            ("Croiseur", 4, ROUGE),
            ("Contre-torpilleur", 3, VERT),
            ("Sous-marin", 3, JAUNE),
            ("Torpilleur", 2, ORANGE)
        ]
        self.index_navire_actuel = 0
        self.orientation_horizontale = True
        
        # Interface
        self.font = pygame.font.Font(None, 36)
        self.font_petit = pygame.font.Font(None, 24)
        self.font_grand = pygame.font.Font(None, 48)
        
        # Messages
        self.message = "Placez vos navires. Clic droit pour tourner."
        self.temps_message = 0
        
        # Positions des grilles
        self.pos_grille_joueur = (50, 100)
        self.pos_grille_ia = (650, 100)
        
        # Fin de jeu
        self.gagnant = None
        
        # Placement automatique de l'IA
        self.grille_ia.placement_automatique()
        
        # Créer le premier navire à placer
        if self.navires_a_placer:
            nom, taille, couleur = self.navires_a_placer[self.index_navire_actuel]
            self.navire_en_placement = Navire(nom, taille, couleur)
    
    def obtenir_case_grille(self, pos, pos_grille):
        x_souris, y_souris = pos
        x_grille, y_grille = pos_grille
        
        if (x_grille <= x_souris <= x_grille + 10 * TAILLE_CASE and
            y_grille <= y_souris <= y_grille + 10 * TAILLE_CASE):
            
            case_x = (x_souris - x_grille) // TAILLE_CASE
            case_y = (y_souris - y_grille) // TAILLE_CASE
            
            if 0 <= case_x < 10 and 0 <= case_y < 10:
                return case_x, case_y
        
        return None
    
    def placer_navire(self, x, y):
        if (self.navire_en_placement and 
            self.navire_en_placement.peut_etre_place(x, y, self.orientation_horizontale, 
                                                   self.grille_joueur.cases)):
            
            self.navire_en_placement.placer(x, y, self.orientation_horizontale)
            self.grille_joueur.ajouter_navire(self.navire_en_placement)
            
            # Passer au navire suivant
            self.index_navire_actuel += 1
            
            if self.index_navire_actuel < len(self.navires_a_placer):
                nom, taille, couleur = self.navires_a_placer[self.index_navire_actuel]
                self.navire_en_placement = Navire(nom, taille, couleur)
                self.message = f"Placez votre {nom} ({taille} cases)"
            else:
                self.phase = "jeu"
                self.navire_en_placement = None
                self.message = "À vous de jouer! Cliquez sur la grille adverse."
            
            return True
        
        return False
    
    def tir_joueur(self, x, y):
        resultat = self.grille_ia.tirer(x, y)
        
        if resultat == "déjà tiré":
            self.message = "Vous avez déjà tiré ici!"
            self.temps_message = 120
            return False
        
        if resultat == "touché":
            self.message = "Touché!"
        elif resultat == "coulé":
            self.message = "Coulé!"
        else:
            self.message = "Raté!"
            self.tour_joueur = False
        
        self.temps_message = 120
        
        # Vérifier la victoire
        if self.grille_ia.tous_navires_coules():
            self.phase = "fin"
            self.gagnant = "Joueur"
            self.message = "Victoire! Vous avez coulé tous les navires ennemis!"
        
        return True
    
    def tir_ia(self):
        cible = self.ia.choisir_cible(self.grille_joueur)
        
        if cible:
            x, y = cible
            resultat = self.grille_joueur.tirer(x, y)
            self.ia.traiter_resultat(x, y, resultat)
            
            if resultat == "raté":
                self.tour_joueur = True
                self.message = "L'IA a raté!"
            elif resultat == "touché":
                self.message = "L'IA vous a touché!"
            elif resultat == "coulé":
                self.message = "L'IA a coulé un de vos navires!"
            
            self.temps_message = 120
            
            # Vérifier la défaite
            if self.grille_joueur.tous_navires_coules():
                self.phase = "fin"
                self.gagnant = "IA"
                self.message = "Défaite! L'IA a coulé tous vos navires!"
    
    def dessiner_grille(self, grille, pos_x, pos_y, montrer_navires=True):
        # Fond de la grille
        grille_rect = pygame.Rect(pos_x, pos_y, 10 * TAILLE_CASE, 10 * TAILLE_CASE)
        pygame.draw.rect(self.ecran, BLEU, grille_rect)
        
        # Cases
        for y in range(10):
            for x in range(10):
                case_rect = pygame.Rect(pos_x + x * TAILLE_CASE, pos_y + y * TAILLE_CASE,
                                      TAILLE_CASE, TAILLE_CASE)
                
                case_value = grille.cases[y][x]
                couleur_case = BLEU
                
                if case_value == 1 and montrer_navires:  # Navire
                    # Trouver la couleur du navire
                    for navire in grille.navires:
                        if (x, y) in navire.positions:
                            couleur_case = navire.couleur
                            break
                elif case_value == 2:  # Touché
                    couleur_case = ROUGE
                elif case_value == 3:  # Coulé
                    couleur_case = NOIR
                elif case_value == 4:  # Raté
                    couleur_case = BLANC
                
                pygame.draw.rect(self.ecran, couleur_case, case_rect)
                pygame.draw.rect(self.ecran, NOIR, case_rect, 1)
                
                # Symboles
                if case_value == 2:  # Touché
                    pygame.draw.line(self.ecran, BLANC, 
                                   (case_rect.left + 5, case_rect.top + 5),
                                   (case_rect.right - 5, case_rect.bottom - 5), 3)
                    pygame.draw.line(self.ecran, BLANC, 
                                   (case_rect.right - 5, case_rect.top + 5),
                                   (case_rect.left + 5, case_rect.bottom - 5), 3)
                elif case_value == 4:  # Raté
                    pygame.draw.circle(self.ecran, BLEU, case_rect.center, 8)
                    pygame.draw.circle(self.ecran, NOIR, case_rect.center, 8, 2)
        
        # Bordure
        pygame.draw.rect(self.ecran, NOIR, grille_rect, 3)
        
        # Coordonnées
        font_coord = pygame.font.Font(None, 20)
        
        # Lettres (A-J)
        for i in range(10):
            lettre = chr(ord('A') + i)
            texte = font_coord.render(lettre, True, NOIR)
            self.ecran.blit(texte, (pos_x + i * TAILLE_CASE + TAILLE_CASE//2 - 5, pos_y - 20))
        
        # Chiffres (1-10)
        for i in range(10):
            chiffre = str(i + 1)
            texte = font_coord.render(chiffre, True, NOIR)
            self.ecran.blit(texte, (pos_x - 20, pos_y + i * TAILLE_CASE + TAILLE_CASE//2 - 5))
    
    def dessiner_navire_fantome(self, pos_souris):
        if self.navire_en_placement and self.phase == "placement":
            case = self.obtenir_case_grille(pos_souris, self.pos_grille_joueur)
            
            if case:
                x, y = case
                
                # Vérifier si le placement est valide
                valide = self.navire_en_placement.peut_etre_place(
                    x, y, self.orientation_horizontale, self.grille_joueur.cases)
                
                couleur = (0, 255, 0, 100) if valide else (255, 0, 0, 100)
                
                # Dessiner le navire fantôme
                for i in range(self.navire_en_placement.taille):
                    if self.orientation_horizontale:
                        case_x, case_y = x + i, y
                    else:
                        case_x, case_y = x, y + i
                    
                    if 0 <= case_x < 10 and 0 <= case_y < 10:
                        case_rect = pygame.Rect(
                            self.pos_grille_joueur[0] + case_x * TAILLE_CASE,
                            self.pos_grille_joueur[1] + case_y * TAILLE_CASE,
                            TAILLE_CASE, TAILLE_CASE)
                        
                        # Surface transparente
                        surface = pygame.Surface((TAILLE_CASE, TAILLE_CASE))
                        surface.set_alpha(100)
                        surface.fill(couleur[:3])
                        self.ecran.blit(surface, case_rect)
    
    def dessiner_interface(self):
        # Titre
        texte_titre = self.font_grand.render("BATAILLE NAVALE", True, NOIR)
        rect_titre = texte_titre.get_rect(center=(LARGEUR//2, 30))
        self.ecran.blit(texte_titre, rect_titre)
        
        # Titres des grilles
        texte_joueur = self.font.render("Votre flotte", True, NOIR)
        self.ecran.blit(texte_joueur, (self.pos_grille_joueur[0], self.pos_grille_joueur[1] - 40))
        
        texte_ia = self.font.render("Flotte ennemie", True, NOIR)
        self.ecran.blit(texte_ia, (self.pos_grille_ia[0], self.pos_grille_ia[1] - 40))
        
        # Message principal
        if self.temps_message > 0:
            couleur_message = ROUGE if "raté" in self.message.lower() else VERT if "touché" in self.message.lower() else NOIR
            self.temps_message -= 1
        else:
            couleur_message = NOIR
        
        texte_message = self.font.render(self.message, True, couleur_message)
        rect_message = texte_message.get_rect(center=(LARGEUR//2, HAUTEUR - 100))
        self.ecran.blit(texte_message, rect_message)
        
        # Informations de phase
        if self.phase == "placement":
            if self.navire_en_placement:
                info = f"Navire: {self.navire_en_placement.nom} ({self.navire_en_placement.taille} cases)"
                orientation = "Horizontal" if self.orientation_horizontale else "Vertical"
                
                texte_info = self.font_petit.render(info, True, NOIR)
                texte_orientation = self.font_petit.render(f"Orientation: {orientation}", True, NOIR)
                
                self.ecran.blit(texte_info, (50, HAUTEUR - 150))
                self.ecran.blit(texte_orientation, (50, HAUTEUR - 125))
        
        elif self.phase == "jeu":
            tour = "Votre tour" if self.tour_joueur else "Tour de l'IA"
            texte_tour = self.font.render(tour, True, NOIR)
            self.ecran.blit(texte_tour, (LARGEUR//2 - 100, 70))
            
            # Statistiques
            navires_joueur_coules = sum(1 for n in self.grille_joueur.navires if n.coule)
            navires_ia_coules = sum(1 for n in self.grille_ia.navires if n.coule)
            
            stats_joueur = f"Vos navires coulés: {navires_joueur_coules}/5"
            stats_ia = f"Navires ennemis coulés: {navires_ia_coules}/5"
            
            texte_stats_joueur = self.font_petit.render(stats_joueur, True, NOIR)
            texte_stats_ia = self.font_petit.render(stats_ia, True, NOIR)
            
            self.ecran.blit(texte_stats_joueur, (50, 450))
            self.ecran.blit(texte_stats_ia, (650, 450))
        
        elif self.phase == "fin":
            couleur_fin = VERT if self.gagnant == "Joueur" else ROUGE
            texte_fin = self.font_grand.render(f"{self.gagnant} gagne!", True, couleur_fin)
            rect_fin = texte_fin.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            
            # Fond
            fond_rect = rect_fin.inflate(50, 30)
            pygame.draw.rect(self.ecran, BLANC, fond_rect, border_radius=10)
            pygame.draw.rect(self.ecran, couleur_fin, fond_rect, width=3, border_radius=10)
            
            self.ecran.blit(texte_fin, rect_fin)
            
            # Instructions
            texte_recommencer = self.font_petit.render("R: Recommencer | Q: Quitter", True, NOIR)
            rect_recommencer = texte_recommencer.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 50))
            self.ecran.blit(texte_recommencer, rect_recommencer)
    
    def gerer_clic(self, pos, bouton):
        if self.phase == "placement":
            case = self.obtenir_case_grille(pos, self.pos_grille_joueur)
            
            if case and bouton == 1:  # Clic gauche
                x, y = case
                if not self.placer_navire(x, y):
                    self.message = "Placement impossible ici!"
                    self.temps_message = 60
            
            elif bouton == 3:  # Clic droit - changer orientation
                self.orientation_horizontale = not self.orientation_horizontale
                orientation = "horizontal" if self.orientation_horizontale else "vertical"
                self.message = f"Orientation: {orientation}"
                self.temps_message = 60
        
        elif self.phase == "jeu" and self.tour_joueur:
            case = self.obtenir_case_grille(pos, self.pos_grille_ia)
            
            if case and bouton == 1:
                x, y = case
                self.tir_joueur(x, y)
    
    def reinitialiser(self):
        self.__init__()
    
    def dessiner(self):
        self.ecran.fill(BLEU_FONCE)
        
        # Dessiner les grilles
        self.dessiner_grille(self.grille_joueur, *self.pos_grille_joueur, True)
        self.dessiner_grille(self.grille_ia, *self.pos_grille_ia, self.phase == "fin")
        
        # Dessiner le navire fantôme pendant le placement
        if self.phase == "placement":
            self.dessiner_navire_fantome(pygame.mouse.get_pos())
        
        # Interface
        self.dessiner_interface()
        
        pygame.display.flip()
    
    def executer(self):
        en_cours = True
        
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.gerer_clic(event.pos, event.button)
                
                elif event.type == pygame.KEYDOWN:
                    if self.phase == "fin":
                        if event.key == pygame.K_r:
                            self.reinitialiser()
                        elif event.key == pygame.K_q:
                            en_cours = False
            
            # Tour de l'IA
            if (self.phase == "jeu" and not self.tour_joueur and 
                self.temps_message <= 0):
                pygame.time.wait(1000)  # Délai pour l'IA
                self.tir_ia()
            
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuBatailleNavale()
    jeu.executer()