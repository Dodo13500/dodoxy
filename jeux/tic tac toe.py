import pygame
import sys
import random

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 600
HAUTEUR = 700
TAILLE_CASE = 150
FPS = 60

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
GRIS = (128, 128, 128)
BLEU = (0, 100, 200)
ROUGE = (200, 0, 0)
VERT = (0, 200, 0)

class JeuTicTacToe:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Tic Tac Toe")
        self.horloge = pygame.time.Clock()
        
        # Grille 3x3 (0 = vide, 1 = X, 2 = O)
        self.grille = [[0 for _ in range(3)] for _ in range(3)]
        
        # État du jeu
        self.joueur_actuel = 1  # 1 = X, 2 = O
        self.jeu_termine = False
        self.gagnant = None
        self.mode_ia = True
        
        # Interface
        self.font = pygame.font.Font(None, 72)
        self.font_petit = pygame.font.Font(None, 36)
        
        # Scores
        self.scores = {"X": 0, "O": 0, "Égalité": 0}
    
    def obtenir_case_cliquee(self, pos):
        x, y = pos
        # Décaler pour centrer la grille
        offset_x = (LARGEUR - 3 * TAILLE_CASE) // 2
        offset_y = 100
        
        if (offset_x <= x <= offset_x + 3 * TAILLE_CASE and
            offset_y <= y <= offset_y + 3 * TAILLE_CASE):
            
            col = (x - offset_x) // TAILLE_CASE
            ligne = (y - offset_y) // TAILLE_CASE
            
            if 0 <= col < 3 and 0 <= ligne < 3:
                return ligne, col
        
        return None, None
    
    def placer_symbole(self, ligne, col):
        if self.grille[ligne][col] == 0 and not self.jeu_termine:
            self.grille[ligne][col] = self.joueur_actuel
            
            # Vérifier victoire
            if self.verifier_victoire():
                self.jeu_termine = True
                self.gagnant = "X" if self.joueur_actuel == 1 else "O"
                self.scores[self.gagnant] += 1
            elif self.grille_pleine():
                self.jeu_termine = True
                self.gagnant = "Égalité"
                self.scores["Égalité"] += 1
            else:
                # Changer de joueur
                self.joueur_actuel = 2 if self.joueur_actuel == 1 else 1
            
            return True
        return False
    
    def verifier_victoire(self):
        # Vérifier lignes
        for ligne in self.grille:
            if ligne[0] == ligne[1] == ligne[2] != 0:
                return True
        
        # Vérifier colonnes
        for col in range(3):
            if self.grille[0][col] == self.grille[1][col] == self.grille[2][col] != 0:
                return True
        
        # Vérifier diagonales
        if self.grille[0][0] == self.grille[1][1] == self.grille[2][2] != 0:
            return True
        if self.grille[0][2] == self.grille[1][1] == self.grille[2][0] != 0:
            return True
        
        return False
    
    def grille_pleine(self):
        for ligne in self.grille:
            if 0 in ligne:
                return False
        return True
    
    def coup_ia(self):
        # IA simple - cherche à gagner, puis à bloquer, sinon coup aléatoire
        
        # Essayer de gagner
        for ligne in range(3):
            for col in range(3):
                if self.grille[ligne][col] == 0:
                    self.grille[ligne][col] = 2
                    if self.verifier_victoire():
                        self.grille[ligne][col] = 0
                        return ligne, col
                    self.grille[ligne][col] = 0
        
        # Essayer de bloquer
        for ligne in range(3):
            for col in range(3):
                if self.grille[ligne][col] == 0:
                    self.grille[ligne][col] = 1
                    if self.verifier_victoire():
                        self.grille[ligne][col] = 0
                        return ligne, col
                    self.grille[ligne][col] = 0
        
        # Coup aléatoire
        cases_libres = []
        for ligne in range(3):
            for col in range(3):
                if self.grille[ligne][col] == 0:
                    cases_libres.append((ligne, col))
        
        if cases_libres:
            return random.choice(cases_libres)
        
        return None, None
    
    def dessiner_grille(self):
        offset_x = (LARGEUR - 3 * TAILLE_CASE) // 2
        offset_y = 100
        
        # Dessiner les cases
        for ligne in range(3):
            for col in range(3):
                x = offset_x + col * TAILLE_CASE
                y = offset_y + ligne * TAILLE_CASE
                
                rect = pygame.Rect(x, y, TAILLE_CASE, TAILLE_CASE)
                pygame.draw.rect(self.ecran, BLANC, rect)
                pygame.draw.rect(self.ecran, NOIR, rect, 3)
                
                # Dessiner X ou O
                if self.grille[ligne][col] == 1:  # X
                    pygame.draw.line(self.ecran, ROUGE, 
                                   (x + 20, y + 20), (x + TAILLE_CASE - 20, y + TAILLE_CASE - 20), 8)
                    pygame.draw.line(self.ecran, ROUGE, 
                                   (x + TAILLE_CASE - 20, y + 20), (x + 20, y + TAILLE_CASE - 20), 8)
                elif self.grille[ligne][col] == 2:  # O
                    centre = (x + TAILLE_CASE // 2, y + TAILLE_CASE // 2)
                    pygame.draw.circle(self.ecran, BLEU, centre, TAILLE_CASE // 2 - 20, 8)
    
    def dessiner_interface(self):
        # Titre
        texte_titre = self.font_petit.render("TIC TAC TOE", True, NOIR)
        rect_titre = texte_titre.get_rect(center=(LARGEUR//2, 30))
        self.ecran.blit(texte_titre, rect_titre)
        
        # Joueur actuel
        if not self.jeu_termine:
            joueur_nom = "X (Joueur)" if self.joueur_actuel == 1 else "O (IA)"
            texte_joueur = self.font_petit.render(f"Tour de: {joueur_nom}", True, NOIR)
            rect_joueur = texte_joueur.get_rect(center=(LARGEUR//2, 60))
            self.ecran.blit(texte_joueur, rect_joueur)
        
        # Scores
        y_scores = 550
        texte_scores = self.font_petit.render("SCORES", True, NOIR)
        rect_scores = texte_scores.get_rect(center=(LARGEUR//2, y_scores))
        self.ecran.blit(texte_scores, rect_scores)
        
        texte_x = pygame.font.Font(None, 24).render(f"X: {self.scores['X']}", True, ROUGE)
        texte_o = pygame.font.Font(None, 24).render(f"O: {self.scores['O']}", True, BLEU)
        texte_egalite = pygame.font.Font(None, 24).render(f"Égalité: {self.scores['Égalité']}", True, GRIS)
        
        self.ecran.blit(texte_x, (LARGEUR//2 - 100, y_scores + 30))
        self.ecran.blit(texte_o, (LARGEUR//2 - 20, y_scores + 30))
        self.ecran.blit(texte_egalite, (LARGEUR//2 + 60, y_scores + 30))
        
        # Instructions
        if self.jeu_termine:
            if self.gagnant == "Égalité":
                texte_fin = self.font_petit.render("ÉGALITÉ!", True, GRIS)
            else:
                couleur = ROUGE if self.gagnant == "X" else BLEU
                texte_fin = self.font_petit.render(f"{self.gagnant} GAGNE!", True, couleur)
            
            rect_fin = texte_fin.get_rect(center=(LARGEUR//2, 620))
            self.ecran.blit(texte_fin, rect_fin)
            
            texte_restart = pygame.font.Font(None, 24).render("R: Nouvelle partie", True, NOIR)
            rect_restart = texte_restart.get_rect(center=(LARGEUR//2, 650))
            self.ecran.blit(texte_restart, rect_restart)
    
    def reinitialiser(self):
        self.grille = [[0 for _ in range(3)] for _ in range(3)]
        self.joueur_actuel = 1
        self.jeu_termine = False
        self.gagnant = None
    
    def dessiner(self):
        self.ecran.fill(GRIS)
        self.dessiner_grille()
        self.dessiner_interface()
        pygame.display.flip()
    
    def executer(self):
        en_cours = True
        
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not self.jeu_termine:  # Clic gauche
                        ligne, col = self.obtenir_case_cliquee(event.pos)
                        if ligne is not None and col is not None and self.joueur_actuel == 1:
                            self.placer_symbole(ligne, col)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reinitialiser()
            
            # Tour de l'IA
            if self.mode_ia and self.joueur_actuel == 2 and not self.jeu_termine:
                ligne, col = self.coup_ia()
                if ligne is not None and col is not None:
                    self.placer_symbole(ligne, col)
            
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuTicTacToe()
    jeu.executer()