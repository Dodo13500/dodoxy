import pygame
import sys
import math
import random

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 800
HAUTEUR = 700
LIGNES = 6
COLONNES = 7
TAILLE_CASE = 80
RAYON_JETON = 35
FPS = 60

# Couleurs réalistes
BLEU_GRILLE = (30, 144, 255)
BLEU_FONCE = (25, 25, 112)
ROUGE_JOUEUR = (220, 20, 60)
JAUNE_JOUEUR = (255, 215, 0)
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
GRIS = (128, 128, 128)
GRIS_CLAIR = (200, 200, 200)
VERT = (34, 139, 34)
OR = (255, 215, 0)

class JetonAnime:
    def __init__(self, x, y, couleur, colonne, ligne_cible):
        self.x = x
        self.y = y
        self.couleur = couleur
        self.colonne = colonne
        self.ligne_cible = ligne_cible
        self.vitesse_y = 0
        self.gravite = 0.8
        self.rebonds = 0
        self.max_rebonds = 2
        self.termine = False
        
        # Position cible
        self.y_cible = 100 + ligne_cible * TAILLE_CASE + TAILLE_CASE // 2
        
        # Effets visuels
        self.rotation = 0
        self.particules = []
    
    def mettre_a_jour(self):
        if not self.termine:
            # Physique de chute
            self.vitesse_y += self.gravite
            self.y += self.vitesse_y
            self.rotation += 5
            
            # Vérifier si le jeton atteint sa position
            if self.y >= self.y_cible:
                self.y = self.y_cible
                
                if self.rebonds < self.max_rebonds:
                    # Rebond
                    self.vitesse_y = -self.vitesse_y * 0.6
                    self.rebonds += 1
                    self.creer_particules_rebond()
                else:
                    # Arrêter l'animation
                    self.vitesse_y = 0
                    self.termine = True
        
        # Mettre à jour les particules
        self.mettre_a_jour_particules()
    
    def creer_particules_rebond(self):
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            vitesse = random.uniform(2, 5)
            particule = {
                'x': self.x,
                'y': self.y,
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
            particule['vy'] += 0.3  # Gravité
            particule['vx'] *= 0.98
            particule['vie'] -= 1
            
            if particule['vie'] <= 0:
                self.particules.remove(particule)
    
    def dessiner(self, surface):
        # Jeton principal avec effet 3D
        pygame.draw.circle(surface, self.couleur, (int(self.x), int(self.y)), RAYON_JETON)
        
        # Reflet
        reflet_x = int(self.x - RAYON_JETON * 0.3)
        reflet_y = int(self.y - RAYON_JETON * 0.3)
        pygame.draw.circle(surface, BLANC, (reflet_x, reflet_y), RAYON_JETON // 3)
        
        # Bordure
        pygame.draw.circle(surface, NOIR, (int(self.x), int(self.y)), RAYON_JETON, 3)
        
        # Particules
        for particule in self.particules:
            if particule['vie'] > 0:
                pygame.draw.circle(surface, particule['couleur'], 
                                 (int(particule['x']), int(particule['y'])), 2)

class JeuPuissance4:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Puissance 4 Réaliste")
        self.horloge = pygame.time.Clock()
        
        # Grille de jeu (0 = vide, 1 = joueur 1, 2 = joueur 2)
        self.grille = [[0 for _ in range(COLONNES)] for _ in range(LIGNES)]
        
        # État du jeu
        self.joueur_actuel = 1
        self.jeu_termine = False
        self.gagnant = None
        self.ligne_gagnante = []
        
        # Mode de jeu
        self.mode_ia = True
        self.difficulte_ia = "moyen"  # facile, moyen, difficile
        
        # Animations
        self.jetons_animes = []
        self.colonne_hover = -1
        
        # Interface
        self.font = pygame.font.Font(None, 48)
        self.font_moyen = pygame.font.Font(None, 36)
        self.font_petit = pygame.font.Font(None, 24)
        
        # Statistiques
        self.scores = {1: 0, 2: 0, 'Égalité': 0}
        
        # Effets visuels
        self.particules_victoire = []
        self.animation_ligne_gagnante = 0
    
    def obtenir_colonne_clic(self, pos_souris):
        x, y = pos_souris
        if 100 <= y <= 100 + LIGNES * TAILLE_CASE:
            colonne = (x - 100) // TAILLE_CASE
            if 0 <= colonne < COLONNES:
                return colonne
        return -1
    
    def colonne_valide(self, colonne):
        return self.grille[0][colonne] == 0
    
    def obtenir_ligne_libre(self, colonne):
        for ligne in range(LIGNES - 1, -1, -1):
            if self.grille[ligne][colonne] == 0:
                return ligne
        return -1
    
    def placer_jeton(self, colonne):
        if self.colonne_valide(colonne) and not self.jetons_animes:
            ligne = self.obtenir_ligne_libre(colonne)
            
            # Créer l'animation du jeton qui tombe
            x = 100 + colonne * TAILLE_CASE + TAILLE_CASE // 2
            y = 50  # Position de départ au-dessus de la grille
            couleur = ROUGE_JOUEUR if self.joueur_actuel == 1 else JAUNE_JOUEUR
            
            jeton_anime = JetonAnime(x, y, couleur, colonne, ligne)
            self.jetons_animes.append(jeton_anime)
            
            # Placer le jeton dans la grille
            self.grille[ligne][colonne] = self.joueur_actuel
            
            return True
        return False
    
    def verifier_victoire(self, joueur):
        # Vérifier horizontalement
        for ligne in range(LIGNES):
            for col in range(COLONNES - 3):
                if all(self.grille[ligne][col + i] == joueur for i in range(4)):
                    self.ligne_gagnante = [(ligne, col + i) for i in range(4)]
                    return True
        
        # Vérifier verticalement
        for ligne in range(LIGNES - 3):
            for col in range(COLONNES):
                if all(self.grille[ligne + i][col] == joueur for i in range(4)):
                    self.ligne_gagnante = [(ligne + i, col) for i in range(4)]
                    return True
        
        # Vérifier diagonale descendante
        for ligne in range(LIGNES - 3):
            for col in range(COLONNES - 3):
                if all(self.grille[ligne + i][col + i] == joueur for i in range(4)):
                    self.ligne_gagnante = [(ligne + i, col + i) for i in range(4)]
                    return True
        
        # Vérifier diagonale montante
        for ligne in range(3, LIGNES):
            for col in range(COLONNES - 3):
                if all(self.grille[ligne - i][col + i] == joueur for i in range(4)):
                    self.ligne_gagnante = [(ligne - i, col + i) for i in range(4)]
                    return True
        
        return False
    
    def grille_pleine(self):
        return all(self.grille[0][col] != 0 for col in range(COLONNES))
    
    def evaluer_position(self, joueur):
        score = 0
        
        # Évaluer toutes les fenêtres de 4 cases
        # Horizontalement
        for ligne in range(LIGNES):
            for col in range(COLONNES - 3):
                fenetre = [self.grille[ligne][col + i] for i in range(4)]
                score += self.evaluer_fenetre(fenetre, joueur)
        
        # Verticalement
        for ligne in range(LIGNES - 3):
            for col in range(COLONNES):
                fenetre = [self.grille[ligne + i][col] for i in range(4)]
                score += self.evaluer_fenetre(fenetre, joueur)
        
        # Diagonales
        for ligne in range(LIGNES - 3):
            for col in range(COLONNES - 3):
                fenetre = [self.grille[ligne + i][col + i] for i in range(4)]
                score += self.evaluer_fenetre(fenetre, joueur)
                
                fenetre = [self.grille[ligne + 3 - i][col + i] for i in range(4)]
                score += self.evaluer_fenetre(fenetre, joueur)
        
        return score
    
    def evaluer_fenetre(self, fenetre, joueur):
        score = 0
        adversaire = 2 if joueur == 1 else 1
        
        if fenetre.count(joueur) == 4:
            score += 100
        elif fenetre.count(joueur) == 3 and fenetre.count(0) == 1:
            score += 10
        elif fenetre.count(joueur) == 2 and fenetre.count(0) == 2:
            score += 2
        
        if fenetre.count(adversaire) == 3 and fenetre.count(0) == 1:
            score -= 80
        
        return score
    
    def coup_ia_facile(self):
        # IA facile - coups aléatoires
        colonnes_valides = [col for col in range(COLONNES) if self.colonne_valide(col)]
        return random.choice(colonnes_valides) if colonnes_valides else None
    
    def coup_ia_moyen(self):
        # IA moyenne - bloque les victoires et cherche à gagner
        # D'abord, essayer de gagner
        for col in range(COLONNES):
            if self.colonne_valide(col):
                ligne = self.obtenir_ligne_libre(col)
                self.grille[ligne][col] = 2
                if self.verifier_victoire(2):
                    self.grille[ligne][col] = 0
                    return col
                self.grille[ligne][col] = 0
        
        # Ensuite, bloquer l'adversaire
        for col in range(COLONNES):
            if self.colonne_valide(col):
                ligne = self.obtenir_ligne_libre(col)
                self.grille[ligne][col] = 1
                if self.verifier_victoire(1):
                    self.grille[ligne][col] = 0
                    return col
                self.grille[ligne][col] = 0
        
        # Sinon, coup aléatoire
        return self.coup_ia_facile()
    
    def coup_ia_difficile(self):
        # IA difficile - algorithme minimax
        _, meilleure_colonne = self.minimax(4, True, float('-inf'), float('inf'))
        return meilleure_colonne
    
    def minimax(self, profondeur, est_maximisant, alpha, beta):
        colonnes_valides = [col for col in range(COLONNES) if self.colonne_valide(col)]
        
        # Conditions terminales
        if self.verifier_victoire(2):
            return 100000, None
        elif self.verifier_victoire(1):
            return -100000, None
        elif len(colonnes_valides) == 0 or profondeur == 0:
            return self.evaluer_position(2), None
        
        if est_maximisant:
            valeur = float('-inf')
            meilleure_colonne = random.choice(colonnes_valides)
            
            for col in colonnes_valides:
                ligne = self.obtenir_ligne_libre(col)
                self.grille[ligne][col] = 2
                
                nouveau_score, _ = self.minimax(profondeur - 1, False, alpha, beta)
                self.grille[ligne][col] = 0
                
                if nouveau_score > valeur:
                    valeur = nouveau_score
                    meilleure_colonne = col
                
                alpha = max(alpha, valeur)
                if beta <= alpha:
                    break
            
            return valeur, meilleure_colonne
        
        else:
            valeur = float('inf')
            meilleure_colonne = random.choice(colonnes_valides)
            
            for col in colonnes_valides:
                ligne = self.obtenir_ligne_libre(col)
                self.grille[ligne][col] = 1
                
                nouveau_score, _ = self.minimax(profondeur - 1, True, alpha, beta)
                self.grille[ligne][col] = 0
                
                if nouveau_score < valeur:
                    valeur = nouveau_score
                    meilleure_colonne = col
                
                beta = min(beta, valeur)
                if beta <= alpha:
                    break
            
            return valeur, meilleure_colonne
    
    def coup_ia(self):
        if self.difficulte_ia == "facile":
            return self.coup_ia_facile()
        elif self.difficulte_ia == "moyen":
            return self.coup_ia_moyen()
        else:
            return self.coup_ia_difficile()
    
    def creer_particules_victoire(self):
        for _ in range(50):
            x = random.randint(100, 100 + COLONNES * TAILLE_CASE)
            y = random.randint(100, 100 + LIGNES * TAILLE_CASE)
            particule = {
                'x': x,
                'y': y,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-5, -2),
                'vie': 60,
                'couleur': random.choice([ROUGE_JOUEUR, JAUNE_JOUEUR, OR, BLANC])
            }
            self.particules_victoire.append(particule)
    
    def mettre_a_jour_particules(self):
        for particule in self.particules_victoire[:]:
            particule['x'] += particule['vx']
            particule['y'] += particule['vy']
            particule['vy'] += 0.2  # Gravité
            particule['vie'] -= 1
            
            if particule['vie'] <= 0:
                self.particules_victoire.remove(particule)
    
    def dessiner_grille(self):
        # Fond de la grille
        grille_rect = pygame.Rect(100, 100, COLONNES * TAILLE_CASE, LIGNES * TAILLE_CASE)
        pygame.draw.rect(self.ecran, BLEU_GRILLE, grille_rect)
        pygame.draw.rect(self.ecran, BLEU_FONCE, grille_rect, 5)
        
        # Effet hover sur la colonne
        if 0 <= self.colonne_hover < COLONNES and not self.jeu_termine:
            hover_rect = pygame.Rect(100 + self.colonne_hover * TAILLE_CASE, 100, 
                                   TAILLE_CASE, LIGNES * TAILLE_CASE)
            pygame.draw.rect(self.ecran, GRIS_CLAIR, hover_rect, 3)
        
        # Dessiner les trous et les jetons
        for ligne in range(LIGNES):
            for col in range(COLONNES):
                centre_x = 100 + col * TAILLE_CASE + TAILLE_CASE // 2
                centre_y = 100 + ligne * TAILLE_CASE + TAILLE_CASE // 2
                
                # Trou dans la grille
                pygame.draw.circle(self.ecran, NOIR, (centre_x, centre_y), RAYON_JETON + 2)
                
                # Jeton si présent
                if self.grille[ligne][col] != 0:
                    couleur = ROUGE_JOUEUR if self.grille[ligne][col] == 1 else JAUNE_JOUEUR
                    
                    # Effet spécial pour la ligne gagnante
                    if (ligne, col) in self.ligne_gagnante:
                        # Animation de pulsation
                        rayon_pulse = RAYON_JETON + int(math.sin(self.animation_ligne_gagnante * 0.3) * 5)
                        pygame.draw.circle(self.ecran, OR, (centre_x, centre_y), rayon_pulse + 3)
                    
                    # Jeton principal
                    pygame.draw.circle(self.ecran, couleur, (centre_x, centre_y), RAYON_JETON)
                    
                    # Reflet
                    reflet_x = centre_x - RAYON_JETON // 3
                    reflet_y = centre_y - RAYON_JETON // 3
                    pygame.draw.circle(self.ecran, BLANC, (reflet_x, reflet_y), RAYON_JETON // 4)
                    
                    # Bordure
                    pygame.draw.circle(self.ecran, NOIR, (centre_x, centre_y), RAYON_JETON, 2)
                else:
                    # Trou vide avec effet de profondeur
                    pygame.draw.circle(self.ecran, GRIS, (centre_x, centre_y), RAYON_JETON)
    
    def dessiner_interface(self):
        # Titre
        texte_titre = self.font.render("PUISSANCE 4", True, NOIR)
        rect_titre = texte_titre.get_rect(center=(LARGEUR//2, 30))
        self.ecran.blit(texte_titre, rect_titre)
        
        # Joueur actuel
        if not self.jeu_termine:
            couleur_joueur = ROUGE_JOUEUR if self.joueur_actuel == 1 else JAUNE_JOUEUR
            nom_joueur = "Joueur 1" if self.joueur_actuel == 1 else ("IA" if self.mode_ia else "Joueur 2")
            texte_joueur = self.font_moyen.render(f"Tour de: {nom_joueur}", True, couleur_joueur)
            rect_joueur = texte_joueur.get_rect(center=(LARGEUR//2, 70))
            self.ecran.blit(texte_joueur, rect_joueur)
        
        # Scores
        y_scores = 600
        texte_scores = self.font_petit.render("SCORES", True, NOIR)
        rect_scores = texte_scores.get_rect(center=(LARGEUR//2, y_scores))
        self.ecran.blit(texte_scores, rect_scores)
        
        texte_j1 = self.font_petit.render(f"Joueur 1: {self.scores[1]}", True, ROUGE_JOUEUR)
        self.ecran.blit(texte_j1, (LARGEUR//2 - 150, y_scores + 25))
        
        nom_j2 = "IA" if self.mode_ia else "Joueur 2"
        texte_j2 = self.font_petit.render(f"{nom_j2}: {self.scores[2]}", True, JAUNE_JOUEUR)
        self.ecran.blit(texte_j2, (LARGEUR//2 + 20, y_scores + 25))
        
        # Contrôles
        controles = [
            "Cliquez sur une colonne pour jouer",
            "R: Nouvelle partie",
            f"Difficulté IA: {self.difficulte_ia.title()}" if self.mode_ia else "Mode 2 joueurs"
        ]
        
        for i, controle in enumerate(controles):
            texte = self.font_petit.render(controle, True, GRIS)
            self.ecran.blit(texte, (10, HAUTEUR - 80 + i * 25))
    
    def dessiner_fin_partie(self):
        if self.jeu_termine:
            # Fond semi-transparent
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(150)
            overlay.fill(NOIR)
            self.ecran.blit(overlay, (0, 0))
            
            # Message de fin
            if self.gagnant:
                couleur_gagnant = ROUGE_JOUEUR if self.gagnant == 1 else JAUNE_JOUEUR
                nom_gagnant = "Joueur 1" if self.gagnant == 1 else ("IA" if self.mode_ia else "Joueur 2")
                texte_fin = self.font.render(f"{nom_gagnant} gagne!", True, couleur_gagnant)
                couleur_fond = couleur_gagnant
            else:
                texte_fin = self.font.render("ÉGALITÉ!", True, GRIS_CLAIR)
                couleur_fond = GRIS
            
            rect_fin = texte_fin.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 50))
            
            # Fond coloré
            fond_rect = rect_fin.inflate(50, 30)
            pygame.draw.rect(self.ecran, couleur_fond, fond_rect, border_radius=15)
            pygame.draw.rect(self.ecran, BLANC, fond_rect, width=3, border_radius=15)
            
            self.ecran.blit(texte_fin, rect_fin)
            
            # Instructions
            texte_continuer = self.font_petit.render("R: Nouvelle partie | D: Changer difficulté | Q: Quitter", True, BLANC)
            rect_continuer = texte_continuer.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 20))
            self.ecran.blit(texte_continuer, rect_continuer)
        
        # Particules de victoire
        for particule in self.particules_victoire:
            if particule['vie'] > 0:
                pygame.draw.circle(self.ecran, particule['couleur'], 
                                 (int(particule['x']), int(particule['y'])), 3)
    
    def reinitialiser_partie(self):
        self.grille = [[0 for _ in range(COLONNES)] for _ in range(LIGNES)]
        self.joueur_actuel = 1
        self.jeu_termine = False
        self.gagnant = None
        self.ligne_gagnante = []
        self.jetons_animes = []
        self.particules_victoire = []
        self.animation_ligne_gagnante = 0
    
    def mettre_a_jour(self):
        # Mettre à jour les jetons animés
        for jeton in self.jetons_animes[:]:
            jeton.mettre_a_jour()
            if jeton.termine:
                self.jetons_animes.remove(jeton)
                
                # Vérifier victoire après l'animation
                if self.verifier_victoire(self.joueur_actuel):
                    self.jeu_termine = True
                    self.gagnant = self.joueur_actuel
                    self.scores[self.joueur_actuel] += 1
                    self.creer_particules_victoire()
                elif self.grille_pleine():
                    self.jeu_termine = True
                    self.gagnant = None
                    self.scores['Égalité'] += 1
                else:
                    # Changer de joueur
                    self.joueur_actuel = 2 if self.joueur_actuel == 1 else 1
        
        # Animation de la ligne gagnante
        if self.ligne_gagnante:
            self.animation_ligne_gagnante += 1
        
        # Mettre à jour les particules
        self.mettre_a_jour_particules()
    
    def dessiner(self):
        self.ecran.fill(BLANC)
        
        # Grille
        self.dessiner_grille()
        
        # Jetons animés
        for jeton in self.jetons_animes:
            jeton.dessiner(self.ecran)
        
        # Interface
        self.dessiner_interface()
        
        # Fin de partie
        if self.jeu_termine:
            self.dessiner_fin_partie()
        
        pygame.display.flip()
    
    def executer(self):
        en_cours = True
        
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                
                elif event.type == pygame.MOUSEMOTION:
                    self.colonne_hover = self.obtenir_colonne_clic(event.pos)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not self.jeu_termine:  # Clic gauche
                        colonne = self.obtenir_colonne_clic(event.pos)
                        if colonne != -1 and self.joueur_actuel == 1:
                            self.placer_jeton(colonne)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reinitialiser_partie()
                    elif event.key == pygame.K_d:
                        # Changer difficulté IA
                        difficultes = ["facile", "moyen", "difficile"]
                        index_actuel = difficultes.index(self.difficulte_ia)
                        self.difficulte_ia = difficultes[(index_actuel + 1) % len(difficultes)]
                    elif event.key == pygame.K_q and self.jeu_termine:
                        en_cours = False
            
            # Tour de l'IA
            if (self.mode_ia and self.joueur_actuel == 2 and 
                not self.jeu_termine and not self.jetons_animes):
                colonne = self.coup_ia()
                if colonne is not None:
                    self.placer_jeton(colonne)
            
            self.mettre_a_jour()
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuPuissance4()
    jeu.executer()