import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 800
HAUTEUR = 800
TAILLE_CASE = LARGEUR // 8
FPS = 60

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BEIGE = (240, 217, 181)
MARRON = (181, 136, 99)
ROUGE = (255, 0, 0)
ROUGE_FONCE = (139, 0, 0)
VERT = (0, 255, 0)
JAUNE = (255, 255, 0)
BLEU = (0, 0, 255)

class Pion:
    def __init__(self, couleur, ligne, colonne):
        self.couleur = couleur  # 'rouge' ou 'noir'
        self.ligne = ligne
        self.colonne = colonne
        self.est_dame = False
    
    def promouvoir_en_dame(self):
        self.est_dame = True
    
    def peut_se_deplacer(self, nouvelle_ligne, nouvelle_colonne, plateau):
        # Vérifier que la destination est dans les limites
        if not (0 <= nouvelle_ligne < 8 and 0 <= nouvelle_colonne < 8):
            return False
        
        # Vérifier que la case de destination est vide
        if plateau[nouvelle_ligne][nouvelle_colonne] is not None:
            return False
        
        dl = nouvelle_ligne - self.ligne
        dc = nouvelle_colonne - self.colonne
        
        # Mouvement diagonal uniquement
        if abs(dl) != abs(dc):
            return False
        
        # Pion normal
        if not self.est_dame:
            # Direction selon la couleur
            if self.couleur == 'rouge':
                direction_autorisee = dl < 0  # Vers le haut
            else:
                direction_autorisee = dl > 0  # Vers le bas
            
            # Mouvement simple (une case)
            if abs(dl) == 1:
                return direction_autorisee
            
            # Saut (deux cases) - doit capturer une pièce
            elif abs(dl) == 2:
                ligne_milieu = self.ligne + dl // 2
                colonne_milieu = self.colonne + dc // 2
                piece_milieu = plateau[ligne_milieu][colonne_milieu]
                
                return (direction_autorisee and 
                       piece_milieu is not None and 
                       piece_milieu.couleur != self.couleur)
        
        # Dame
        else:
            # Peut se déplacer dans toutes les directions diagonales
            # Vérifier qu'il n'y a qu'une seule pièce adverse sur le chemin (pour capture)
            # ou aucune pièce (pour mouvement simple)
            
            direction_l = 1 if dl > 0 else -1
            direction_c = 1 if dc > 0 else -1
            
            pieces_sur_chemin = []
            for i in range(1, abs(dl)):
                ligne_check = self.ligne + i * direction_l
                colonne_check = self.colonne + i * direction_c
                piece_check = plateau[ligne_check][colonne_check]
                if piece_check is not None:
                    pieces_sur_chemin.append(piece_check)
            
            # Mouvement simple (aucune pièce sur le chemin)
            if len(pieces_sur_chemin) == 0:
                return True
            
            # Capture (une seule pièce adverse sur le chemin)
            elif len(pieces_sur_chemin) == 1:
                return pieces_sur_chemin[0].couleur != self.couleur
        
        return False
    
    def obtenir_captures_possibles(self, plateau):
        captures = []
        
        if not self.est_dame:
            # Pion normal - vérifier les 4 directions diagonales pour les sauts
            directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
            for dl, dc in directions:
                nouvelle_ligne = self.ligne + dl
                nouvelle_colonne = self.colonne + dc
                
                if self.peut_se_deplacer(nouvelle_ligne, nouvelle_colonne, plateau):
                    # Vérifier s'il y a une pièce à capturer
                    ligne_milieu = self.ligne + dl // 2
                    colonne_milieu = self.colonne + dc // 2
                    piece_milieu = plateau[ligne_milieu][colonne_milieu]
                    
                    if (piece_milieu is not None and 
                        piece_milieu.couleur != self.couleur):
                        captures.append((nouvelle_ligne, nouvelle_colonne))
        
        else:
            # Dame - vérifier toutes les diagonales
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for direction_l, direction_c in directions:
                for distance in range(2, 8):
                    nouvelle_ligne = self.ligne + distance * direction_l
                    nouvelle_colonne = self.colonne + distance * direction_c
                    
                    if (0 <= nouvelle_ligne < 8 and 0 <= nouvelle_colonne < 8 and
                        self.peut_se_deplacer(nouvelle_ligne, nouvelle_colonne, plateau)):
                        
                        # Vérifier s'il y a exactement une pièce adverse à capturer
                        pieces_sur_chemin = []
                        for i in range(1, distance):
                            ligne_check = self.ligne + i * direction_l
                            colonne_check = self.colonne + i * direction_c
                            piece_check = plateau[ligne_check][colonne_check]
                            if piece_check is not None:
                                pieces_sur_chemin.append((ligne_check, colonne_check, piece_check))
                        
                        if (len(pieces_sur_chemin) == 1 and 
                            pieces_sur_chemin[0][2].couleur != self.couleur):
                            captures.append((nouvelle_ligne, nouvelle_colonne))
        
        return captures

class JeuDames:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Jeu de Dames")
        self.horloge = pygame.time.Clock()
        
        # Plateau de jeu (8x8)
        self.plateau = [[None for _ in range(8)] for _ in range(8)]
        self.initialiser_plateau()
        
        # État du jeu
        self.tour_joueur = 'rouge'
        self.pion_selectionne = None
        self.case_selectionnee = None
        self.mouvements_possibles = []
        self.captures_possibles = []
        self.capture_obligatoire = False
        
        # Scores
        self.score_rouge = 12
        self.score_noir = 12
        
        # Interface
        self.font = pygame.font.Font(None, 36)
        self.font_petit = pygame.font.Font(None, 24)
        
        # État de fin de jeu
        self.jeu_termine = False
        self.gagnant = None
    
    def initialiser_plateau(self):
        # Placer les pions noirs (en haut)
        for ligne in range(3):
            for colonne in range(8):
                if (ligne + colonne) % 2 == 1:  # Cases noires seulement
                    self.plateau[ligne][colonne] = Pion('noir', ligne, colonne)
        
        # Placer les pions rouges (en bas)
        for ligne in range(5, 8):
            for colonne in range(8):
                if (ligne + colonne) % 2 == 1:  # Cases noires seulement
                    self.plateau[ligne][colonne] = Pion('rouge', ligne, colonne)
    
    def obtenir_case_depuis_position(self, pos):
        x, y = pos
        colonne = x // TAILLE_CASE
        ligne = y // TAILLE_CASE
        if 0 <= ligne < 8 and 0 <= colonne < 8:
            return ligne, colonne
        return None
    
    def calculer_mouvements_possibles(self, pion):
        mouvements = []
        captures = pion.obtenir_captures_possibles(self.plateau)
        
        # Si des captures sont possibles, elles sont obligatoires
        if captures:
            return captures
        
        # Sinon, calculer les mouvements normaux
        if not pion.est_dame:
            # Pion normal
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dl, dc in directions:
                nouvelle_ligne = pion.ligne + dl
                nouvelle_colonne = pion.colonne + dc
                if pion.peut_se_deplacer(nouvelle_ligne, nouvelle_colonne, self.plateau):
                    mouvements.append((nouvelle_ligne, nouvelle_colonne))
        else:
            # Dame
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for direction_l, direction_c in directions:
                for distance in range(1, 8):
                    nouvelle_ligne = pion.ligne + distance * direction_l
                    nouvelle_colonne = pion.colonne + distance * direction_c
                    
                    if pion.peut_se_deplacer(nouvelle_ligne, nouvelle_colonne, self.plateau):
                        mouvements.append((nouvelle_ligne, nouvelle_colonne))
                    else:
                        break  # Arrêter dans cette direction
        
        return mouvements
    
    def verifier_captures_obligatoires(self):
        # Vérifier si le joueur actuel a des captures obligatoires
        for ligne in range(8):
            for colonne in range(8):
                pion = self.plateau[ligne][colonne]
                if pion and pion.couleur == self.tour_joueur:
                    captures = pion.obtenir_captures_possibles(self.plateau)
                    if captures:
                        return True
        return False
    
    def effectuer_capture(self, pion, nouvelle_ligne, nouvelle_colonne):
        # Trouver et supprimer la pièce capturée
        if not pion.est_dame:
            # Pion normal
            ligne_milieu = (pion.ligne + nouvelle_ligne) // 2
            colonne_milieu = (pion.colonne + nouvelle_colonne) // 2
            piece_capturee = self.plateau[ligne_milieu][colonne_milieu]
            if piece_capturee:
                self.plateau[ligne_milieu][colonne_milieu] = None
                if piece_capturee.couleur == 'rouge':
                    self.score_rouge -= 1
                else:
                    self.score_noir -= 1
        else:
            # Dame
            direction_l = 1 if nouvelle_ligne > pion.ligne else -1
            direction_c = 1 if nouvelle_colonne > pion.colonne else -1
            
            # Trouver la pièce à capturer
            for i in range(1, abs(nouvelle_ligne - pion.ligne)):
                ligne_check = pion.ligne + i * direction_l
                colonne_check = pion.colonne + i * direction_c
                piece_check = self.plateau[ligne_check][colonne_check]
                
                if piece_check and piece_check.couleur != pion.couleur:
                    self.plateau[ligne_check][colonne_check] = None
                    if piece_check.couleur == 'rouge':
                        self.score_rouge -= 1
                    else:
                        self.score_noir -= 1
                    break
    
    def deplacer_pion(self, pion, nouvelle_ligne, nouvelle_colonne):
        # Vérifier si c'est une capture
        est_capture = (nouvelle_ligne, nouvelle_colonne) in pion.obtenir_captures_possibles(self.plateau)
        
        if est_capture:
            self.effectuer_capture(pion, nouvelle_ligne, nouvelle_colonne)
        
        # Déplacer le pion
        self.plateau[pion.ligne][pion.colonne] = None
        pion.ligne = nouvelle_ligne
        pion.colonne = nouvelle_colonne
        self.plateau[nouvelle_ligne][nouvelle_colonne] = pion
        
        # Vérifier la promotion en dame
        if not pion.est_dame:
            if (pion.couleur == 'rouge' and nouvelle_ligne == 0) or \
               (pion.couleur == 'noir' and nouvelle_ligne == 7):
                pion.promouvoir_en_dame()
        
        # Si c'était une capture, vérifier s'il y a d'autres captures possibles
        if est_capture:
            nouvelles_captures = pion.obtenir_captures_possibles(self.plateau)
            if nouvelles_captures:
                # Le même pion doit continuer à capturer
                self.pion_selectionne = pion
                self.case_selectionnee = (nouvelle_ligne, nouvelle_colonne)
                self.mouvements_possibles = nouvelles_captures
                return  # Ne pas changer de tour
        
        # Changer de tour
        self.tour_joueur = 'noir' if self.tour_joueur == 'rouge' else 'rouge'
        self.capture_obligatoire = self.verifier_captures_obligatoires()
    
    def verifier_fin_jeu(self):
        # Vérifier si un joueur n'a plus de pions
        if self.score_rouge == 0:
            self.jeu_termine = True
            self.gagnant = 'noir'
            return
        elif self.score_noir == 0:
            self.jeu_termine = True
            self.gagnant = 'rouge'
            return
        
        # Vérifier si le joueur actuel peut bouger
        peut_bouger = False
        for ligne in range(8):
            for colonne in range(8):
                pion = self.plateau[ligne][colonne]
                if pion and pion.couleur == self.tour_joueur:
                    mouvements = self.calculer_mouvements_possibles(pion)
                    if mouvements:
                        peut_bouger = True
                        break
            if peut_bouger:
                break
        
        if not peut_bouger:
            self.jeu_termine = True
            self.gagnant = 'noir' if self.tour_joueur == 'rouge' else 'rouge'
    
    def gerer_clic(self, pos):
        if self.jeu_termine:
            return
        
        case = self.obtenir_case_depuis_position(pos)
        if not case:
            return
        
        ligne, colonne = case
        pion_clique = self.plateau[ligne][colonne]
        
        # Si aucun pion n'est sélectionné
        if self.pion_selectionne is None:
            if pion_clique and pion_clique.couleur == self.tour_joueur:
                # Vérifier les captures obligatoires
                if self.capture_obligatoire:
                    captures = pion_clique.obtenir_captures_possibles(self.plateau)
                    if not captures:
                        return  # Ce pion ne peut pas capturer
                
                self.pion_selectionne = pion_clique
                self.case_selectionnee = (ligne, colonne)
                self.mouvements_possibles = self.calculer_mouvements_possibles(pion_clique)
        
        # Si un pion est déjà sélectionné
        else:
            # Cliquer sur le même pion pour le désélectionner
            if (ligne, colonne) == self.case_selectionnee:
                self.pion_selectionne = None
                self.case_selectionnee = None
                self.mouvements_possibles = []
            
            # Cliquer sur un autre pion de la même couleur
            elif pion_clique and pion_clique.couleur == self.tour_joueur:
                # Vérifier les captures obligatoires
                if self.capture_obligatoire:
                    captures = pion_clique.obtenir_captures_possibles(self.plateau)
                    if not captures:
                        return  # Ce pion ne peut pas capturer
                
                self.pion_selectionne = pion_clique
                self.case_selectionnee = (ligne, colonne)
                self.mouvements_possibles = self.calculer_mouvements_possibles(pion_clique)
            
            # Tenter un mouvement
            elif (ligne, colonne) in self.mouvements_possibles:
                self.deplacer_pion(self.pion_selectionne, ligne, colonne)
                
                # Réinitialiser la sélection si le tour change
                if self.pion_selectionne is None or self.pion_selectionne.ligne != ligne or self.pion_selectionne.colonne != colonne:
                    self.pion_selectionne = None
                    self.case_selectionnee = None
                    self.mouvements_possibles = []
            
            # Clic invalide
            else:
                self.pion_selectionne = None
                self.case_selectionnee = None
                self.mouvements_possibles = []
    
    def dessiner_plateau(self):
        for ligne in range(8):
            for colonne in range(8):
                # Couleur de la case
                if (ligne + colonne) % 2 == 0:
                    couleur = BEIGE
                else:
                    couleur = MARRON
                
                # Surligner la case sélectionnée
                if self.case_selectionnee == (ligne, colonne):
                    couleur = JAUNE
                
                # Surligner les mouvements possibles
                elif (ligne, colonne) in self.mouvements_possibles:
                    couleur = VERT
                
                # Dessiner la case
                rect = pygame.Rect(colonne * TAILLE_CASE, ligne * TAILLE_CASE, 
                                 TAILLE_CASE, TAILLE_CASE)
                pygame.draw.rect(self.ecran, couleur, rect)
                pygame.draw.rect(self.ecran, NOIR, rect, 1)
    
    def dessiner_pions(self):
        for ligne in range(8):
            for colonne in range(8):
                pion = self.plateau[ligne][colonne]
                if pion:
                    centre_x = colonne * TAILLE_CASE + TAILLE_CASE // 2
                    centre_y = ligne * TAILLE_CASE + TAILLE_CASE // 2
                    rayon = TAILLE_CASE // 3
                    
                    # Couleur du pion
                    couleur_pion = ROUGE if pion.couleur == 'rouge' else NOIR
                    couleur_contour = ROUGE_FONCE if pion.couleur == 'rouge' else BLANC
                    
                    # Dessiner le pion
                    pygame.draw.circle(self.ecran, couleur_pion, (centre_x, centre_y), rayon)
                    pygame.draw.circle(self.ecran, couleur_contour, (centre_x, centre_y), rayon, 3)
                    
                    # Dessiner la couronne pour les dames
                    if pion.est_dame:
                        pygame.draw.circle(self.ecran, JAUNE, (centre_x, centre_y), rayon // 2)
                        pygame.draw.circle(self.ecran, couleur_contour, (centre_x, centre_y), rayon // 2, 2)
    
    def dessiner_interface(self):
        # Afficher le tour actuel
        couleur_texte = ROUGE if self.tour_joueur == 'rouge' else NOIR
        texte_tour = self.font.render(f"Tour: {self.tour_joueur.capitalize()}", True, couleur_texte)
        self.ecran.blit(texte_tour, (10, 10))
        
        # Afficher les scores
        texte_score_rouge = self.font.render(f"Rouge: {self.score_rouge}", True, ROUGE)
        texte_score_noir = self.font.render(f"Noir: {self.score_noir}", True, NOIR)
        self.ecran.blit(texte_score_rouge, (10, 50))
        self.ecran.blit(texte_score_noir, (10, 90))
        
        # Afficher si capture obligatoire
        if self.capture_obligatoire:
            texte_capture = self.font.render("CAPTURE OBLIGATOIRE!", True, BLEU)
            self.ecran.blit(texte_capture, (10, 130))
        
        # Instructions
        if not self.jeu_termine:
            instructions = [
                "Cliquez sur un pion pour le sélectionner",
                "Cliquez sur une case verte pour déplacer",
                "Les captures sont obligatoires!"
            ]
            
            for i, instruction in enumerate(instructions):
                texte = self.font_petit.render(instruction, True, NOIR)
                self.ecran.blit(texte, (10, HAUTEUR - 80 + i * 25))
    
    def dessiner_fin_jeu(self):
        if self.jeu_termine:
            # Fond semi-transparent
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(128)
            overlay.fill(BLANC)
            self.ecran.blit(overlay, (0, 0))
            
            # Message de victoire
            couleur_gagnant = ROUGE if self.gagnant == 'rouge' else NOIR
            texte_fin = self.font.render(f"{self.gagnant.upper()} A GAGNÉ!", True, couleur_gagnant)
            rect_fin = texte_fin.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            self.ecran.blit(texte_fin, rect_fin)
            
            # Score final
            score_final = f"Score final - Rouge: {self.score_rouge}, Noir: {self.score_noir}"
            texte_score = self.font_petit.render(score_final, True, NOIR)
            rect_score = texte_score.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 40))
            self.ecran.blit(texte_score, rect_score)
            
            # Instructions pour recommencer
            texte_recommencer = self.font_petit.render("Appuyez sur R pour recommencer ou Q pour quitter", True, NOIR)
            rect_recommencer = texte_recommencer.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 80))
            self.ecran.blit(texte_recommencer, rect_recommencer)
    
    def reinitialiser(self):
        self.plateau = [[None for _ in range(8)] for _ in range(8)]
        self.initialiser_plateau()
        self.tour_joueur = 'rouge'
        self.pion_selectionne = None
        self.case_selectionnee = None
        self.mouvements_possibles = []
        self.captures_possibles = []
        self.capture_obligatoire = False
        self.score_rouge = 12
        self.score_noir = 12
        self.jeu_termine = False
        self.gagnant = None
    
    def dessiner(self):
        self.ecran.fill(BLANC)
        self.dessiner_plateau()
        self.dessiner_pions()
        self.dessiner_interface()
        
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
                    if event.button == 1:  # Clic gauche
                        self.gerer_clic(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if self.jeu_termine:
                        if event.key == pygame.K_r:
                            self.reinitialiser()
                        elif event.key == pygame.K_q:
                            en_cours = False
            
            if not self.jeu_termine:
                self.verifier_fin_jeu()
            
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuDames()
    jeu.executer()