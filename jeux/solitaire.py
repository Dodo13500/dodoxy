import pygame
import random
import sys

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 1200
HAUTEUR = 800
FPS = 60

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (220, 20, 60)
VERT = (0, 128, 0)
BLEU_FONCE = (25, 25, 112)
GRIS = (128, 128, 128)
GRIS_CLAIR = (200, 200, 200)
OR = (255, 215, 0)

class Carte:
    def __init__(self, couleur, valeur):
        self.couleur = couleur  # 'coeur', 'carreau', 'trefle', 'pique'
        self.valeur = valeur    # 1-13 (As=1, Valet=11, Dame=12, Roi=13)
        self.largeur = 70
        self.hauteur = 100
        self.face_visible = False
        self.x = 0
        self.y = 0
        self.selectionnee = False
        self.en_mouvement = False
    
    def est_rouge(self):
        return self.couleur in ['coeur', 'carreau']
    
    def peut_etre_placee_sur(self, autre_carte):
        # Pour les colonnes du tableau (alternance couleur, valeur décroissante)
        if autre_carte is None:
            return self.valeur == 13  # Seul un Roi peut être placé sur une colonne vide
        
        return (self.est_rouge() != autre_carte.est_rouge() and 
                self.valeur == autre_carte.valeur - 1)
    
    def peut_aller_en_fondation(self, pile_fondation):
        # Pour les piles de fondation (même couleur, valeur croissante)
        if not pile_fondation:
            return self.valeur == 1  # Seul un As peut commencer une fondation
        
        carte_dessus = pile_fondation[-1]
        return (self.couleur == carte_dessus.couleur and 
                self.valeur == carte_dessus.valeur + 1)
    
    def dessiner(self, surface):
        # Ombre
        ombre_rect = pygame.Rect(self.x + 2, self.y + 2, self.largeur, self.hauteur)
        pygame.draw.rect(surface, (50, 50, 50), ombre_rect, border_radius=8)
        
        # Corps de la carte
        carte_rect = pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
        
        if not self.face_visible:
            # Dos de la carte
            pygame.draw.rect(surface, BLEU_FONCE, carte_rect, border_radius=8)
            pygame.draw.rect(surface, BLANC, carte_rect, width=2, border_radius=8)
            
            # Motif du dos
            for i in range(3):
                for j in range(4):
                    cx = self.x + 15 + i * 20
                    cy = self.y + 15 + j * 20
                    pygame.draw.circle(surface, GRIS, (cx, cy), 5)
        else:
            # Face de la carte
            pygame.draw.rect(surface, BLANC, carte_rect, border_radius=8)
            
            # Couleur du texte
            couleur_texte = ROUGE if self.est_rouge() else NOIR
            
            # Bordure
            if self.selectionnee:
                pygame.draw.rect(surface, OR, carte_rect, width=3, border_radius=8)
            else:
                pygame.draw.rect(surface, NOIR, carte_rect, width=2, border_radius=8)
            
            # Symbole de la couleur
            symboles = {
                'coeur': '♥',
                'carreau': '♦',
                'trefle': '♣',
                'pique': '♠'
            }
            
            # Valeur de la carte
            if self.valeur == 1:
                texte_valeur = 'A'
            elif self.valeur == 11:
                texte_valeur = 'J'
            elif self.valeur == 12:
                texte_valeur = 'Q'
            elif self.valeur == 13:
                texte_valeur = 'K'
            else:
                texte_valeur = str(self.valeur)
            
            # Dessiner la valeur et le symbole
            font_valeur = pygame.font.Font(None, 24)
            font_symbole = pygame.font.Font(None, 20)
            
            # Coin supérieur gauche
            texte = font_valeur.render(texte_valeur, True, couleur_texte)
            surface.blit(texte, (self.x + 5, self.y + 5))
            
            symbole = font_symbole.render(symboles[self.couleur], True, couleur_texte)
            surface.blit(symbole, (self.x + 5, self.y + 25))
            
            # Grand symbole au centre
            font_grand = pygame.font.Font(None, 36)
            grand_symbole = font_grand.render(symboles[self.couleur], True, couleur_texte)
            rect_symbole = grand_symbole.get_rect(center=(self.x + self.largeur//2, self.y + self.hauteur//2))
            surface.blit(grand_symbole, rect_symbole)
            
            # Coin inférieur droit (inversé)
            texte_inv = pygame.transform.rotate(texte, 180)
            surface.blit(texte_inv, (self.x + self.largeur - 20, self.y + self.hauteur - 30))
            
            symbole_inv = pygame.transform.rotate(symbole, 180)
            surface.blit(symbole_inv, (self.x + self.largeur - 20, self.y + self.hauteur - 45))
    
    def contient_point(self, x, y):
        return (self.x <= x <= self.x + self.largeur and 
                self.y <= y <= self.y + self.hauteur)

class JeuSolitaire:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Solitaire Klondike")
        self.horloge = pygame.time.Clock()
        
        # Créer le paquet de cartes
        self.creer_paquet()
        
        # Zones de jeu
        self.talon = []  # Cartes non distribuées
        self.defausse = []  # Cartes retournées du talon
        self.fondations = [[] for _ in range(4)]  # 4 piles de fondation
        self.colonnes = [[] for _ in range(7)]  # 7 colonnes du tableau
        
        # Distribuer les cartes
        self.distribuer_cartes()
        
        # État du jeu
        self.carte_selectionnee = None
        self.cartes_selectionnees = []
        self.origine_selection = None
        self.jeu_termine = False
        self.victoire = False
        
        # Interface
        self.font = pygame.font.Font(None, 36)
        self.font_petit = pygame.font.Font(None, 24)
        
        # Positions des zones
        self.pos_talon = (50, 50)
        self.pos_defausse = (130, 50)
        self.pos_fondations = [(450 + i * 80, 50) for i in range(4)]
        self.pos_colonnes = [(50 + i * 90, 200) for i in range(7)]
        
        # Score et temps
        self.score = 0
        self.temps_debut = pygame.time.get_ticks()
        self.mouvements = 0
    
    def creer_paquet(self):
        couleurs = ['coeur', 'carreau', 'trefle', 'pique']
        self.paquet = []
        
        for couleur in couleurs:
            for valeur in range(1, 14):
                carte = Carte(couleur, valeur)
                self.paquet.append(carte)
        
        random.shuffle(self.paquet)
    
    def distribuer_cartes(self):
        # Distribuer les cartes dans les colonnes
        index_carte = 0
        
        for col in range(7):
            for ligne in range(col + 1):
                if index_carte < len(self.paquet):
                    carte = self.paquet[index_carte]
                    carte.face_visible = (ligne == col)  # Seule la dernière carte est visible
                    self.colonnes[col].append(carte)
                    index_carte += 1
        
        # Le reste va dans le talon
        self.talon = self.paquet[index_carte:]
        for carte in self.talon:
            carte.face_visible = False
    
    def mettre_a_jour_positions(self):
        # Talon
        for i, carte in enumerate(self.talon):
            carte.x, carte.y = self.pos_talon
        
        # Défausse
        for i, carte in enumerate(self.defausse):
            carte.x = self.pos_defausse[0]
            carte.y = self.pos_defausse[1]
        
        # Fondations
        for i, pile in enumerate(self.fondations):
            for j, carte in enumerate(pile):
                carte.x = self.pos_fondations[i][0]
                carte.y = self.pos_fondations[i][1]
        
        # Colonnes
        for i, colonne in enumerate(self.colonnes):
            for j, carte in enumerate(colonne):
                carte.x = self.pos_colonnes[i][0]
                carte.y = self.pos_colonnes[i][1] + j * 20
    
    def piocher_talon(self):
        if self.talon:
            carte = self.talon.pop()
            carte.face_visible = True
            self.defausse.append(carte)
        elif self.defausse:
            # Remettre la défausse dans le talon
            while self.defausse:
                carte = self.defausse.pop()
                carte.face_visible = False
                self.talon.append(carte)
    
    def obtenir_carte_cliquee(self, pos_souris):
        x, y = pos_souris
        
        # Vérifier la défausse
        if self.defausse:
            carte = self.defausse[-1]
            if carte.contient_point(x, y):
                return carte, 'defausse', len(self.defausse) - 1
        
        # Vérifier les fondations
        for i, pile in enumerate(self.fondations):
            if pile:
                carte = pile[-1]
                if carte.contient_point(x, y):
                    return carte, 'fondation', i
        
        # Vérifier les colonnes (de bas en haut)
        for i, colonne in enumerate(self.colonnes):
            for j in range(len(colonne) - 1, -1, -1):
                carte = colonne[j]
                if carte.contient_point(x, y) and carte.face_visible:
                    return carte, 'colonne', (i, j)
        
        return None, None, None
    
    def obtenir_zone_cible(self, pos_souris):
        x, y = pos_souris
        
        # Vérifier les fondations
        for i, pos in enumerate(self.pos_fondations):
            zone_rect = pygame.Rect(pos[0], pos[1], 70, 100)
            if zone_rect.collidepoint(x, y):
                return 'fondation', i
        
        # Vérifier les colonnes
        for i, pos in enumerate(self.pos_colonnes):
            # Zone étendue pour les colonnes vides
            hauteur_zone = max(100, len(self.colonnes[i]) * 20 + 100)
            zone_rect = pygame.Rect(pos[0], pos[1], 70, hauteur_zone)
            if zone_rect.collidepoint(x, y):
                return 'colonne', i
        
        return None, None
    
    def peut_deplacer_vers_fondation(self, carte, index_fondation):
        return carte.peut_aller_en_fondation(self.fondations[index_fondation])
    
    def peut_deplacer_vers_colonne(self, carte, index_colonne):
        colonne = self.colonnes[index_colonne]
        if not colonne:
            return carte.valeur == 13  # Seul un Roi peut aller sur une colonne vide
        
        return carte.peut_etre_placee_sur(colonne[-1])
    
    def deplacer_carte(self, carte, origine, cible_type, cible_index):
        # Retirer la carte de son origine
        if origine == 'defausse':
            self.defausse.remove(carte)
        elif origine == 'fondation':
            self.fondations[cible_index].remove(carte)
        elif origine == 'colonne':
            col_index, carte_index = cible_index
            # Retirer toutes les cartes à partir de cette position
            cartes_a_deplacer = self.colonnes[col_index][carte_index:]
            self.colonnes[col_index] = self.colonnes[col_index][:carte_index]
            
            # Révéler la carte suivante si nécessaire
            if self.colonnes[col_index] and not self.colonnes[col_index][-1].face_visible:
                self.colonnes[col_index][-1].face_visible = True
            
            # Ajouter à la destination
            if cible_type == 'colonne':
                self.colonnes[cible_index].extend(cartes_a_deplacer)
            elif cible_type == 'fondation' and len(cartes_a_deplacer) == 1:
                self.fondations[cible_index].append(cartes_a_deplacer[0])
            
            self.mouvements += 1
            self.calculer_score()
            return
        
        # Ajouter à la destination
        if cible_type == 'fondation':
            self.fondations[cible_index].append(carte)
        elif cible_type == 'colonne':
            self.colonnes[cible_index].append(carte)
        
        self.mouvements += 1
        self.calculer_score()
    
    def calculer_score(self):
        # Score basé sur les cartes dans les fondations
        self.score = sum(len(pile) * 10 for pile in self.fondations)
        
        # Bonus pour la vitesse
        temps_ecoule = (pygame.time.get_ticks() - self.temps_debut) // 1000
        if temps_ecoule > 0:
            bonus_temps = max(0, 1000 - temps_ecoule)
            self.score += bonus_temps
    
    def verifier_victoire(self):
        return all(len(pile) == 13 for pile in self.fondations)
    
    def auto_completion(self):
        # Essayer de déplacer automatiquement les cartes vers les fondations
        mouvement_effectue = True
        
        while mouvement_effectue:
            mouvement_effectue = False
            
            # Vérifier la défausse
            if self.defausse:
                carte = self.defausse[-1]
                for i, pile in enumerate(self.fondations):
                    if self.peut_deplacer_vers_fondation(carte, i):
                        self.deplacer_carte(carte, 'defausse', 'fondation', i)
                        mouvement_effectue = True
                        break
            
            # Vérifier les colonnes
            if not mouvement_effectue:
                for i, colonne in enumerate(self.colonnes):
                    if colonne and colonne[-1].face_visible:
                        carte = colonne[-1]
                        for j, pile in enumerate(self.fondations):
                            if self.peut_deplacer_vers_fondation(carte, j):
                                self.deplacer_carte(carte, 'colonne', 'fondation', (i, len(colonne) - 1))
                                mouvement_effectue = True
                                break
                    if mouvement_effectue:
                        break
    
    def dessiner_zones_vides(self):
        # Talon vide
        if not self.talon:
            rect_talon = pygame.Rect(*self.pos_talon, 70, 100)
            pygame.draw.rect(self.ecran, GRIS_CLAIR, rect_talon, border_radius=8)
            pygame.draw.rect(self.ecran, GRIS, rect_talon, width=2, border_radius=8)
        
        # Défausse vide
        if not self.defausse:
            rect_defausse = pygame.Rect(*self.pos_defausse, 70, 100)
            pygame.draw.rect(self.ecran, GRIS_CLAIR, rect_defausse, border_radius=8)
            pygame.draw.rect(self.ecran, GRIS, rect_defausse, width=2, border_radius=8)
        
        # Fondations vides
        for i, pile in enumerate(self.fondations):
            if not pile:
                rect_fondation = pygame.Rect(*self.pos_fondations[i], 70, 100)
                pygame.draw.rect(self.ecran, GRIS_CLAIR, rect_fondation, border_radius=8)
                pygame.draw.rect(self.ecran, GRIS, rect_fondation, width=2, border_radius=8)
                
                # Symbole de la couleur attendue
                couleurs = ['coeur', 'carreau', 'trefle', 'pique']
                symboles = {'coeur': '♥', 'carreau': '♦', 'trefle': '♣', 'pique': '♠'}
                couleurs_texte = {'coeur': ROUGE, 'carreau': ROUGE, 'trefle': NOIR, 'pique': NOIR}
                
                if i < len(couleurs):
                    font_symbole = pygame.font.Font(None, 48)
                    symbole = font_symbole.render(symboles[couleurs[i]], True, couleurs_texte[couleurs[i]])
                    rect_symbole = symbole.get_rect(center=rect_fondation.center)
                    self.ecran.blit(symbole, rect_symbole)
        
        # Colonnes vides
        for i, colonne in enumerate(self.colonnes):
            if not colonne:
                rect_colonne = pygame.Rect(*self.pos_colonnes[i], 70, 100)
                pygame.draw.rect(self.ecran, GRIS_CLAIR, rect_colonne, border_radius=8)
                pygame.draw.rect(self.ecran, GRIS, rect_colonne, width=2, border_radius=8)
    
    def dessiner_interface(self):
        # Score
        texte_score = self.font.render(f"Score: {self.score}", True, NOIR)
        self.ecran.blit(texte_score, (50, 10))
        
        # Temps
        temps_ecoule = (pygame.time.get_ticks() - self.temps_debut) // 1000
        minutes = temps_ecoule // 60
        secondes = temps_ecoule % 60
        texte_temps = self.font.render(f"Temps: {minutes:02d}:{secondes:02d}", True, NOIR)
        self.ecran.blit(texte_temps, (200, 10))
        
        # Mouvements
        texte_mouvements = self.font.render(f"Mouvements: {self.mouvements}", True, NOIR)
        self.ecran.blit(texte_mouvements, (400, 10))
        
        # Instructions
        if not self.jeu_termine:
            instructions = [
                "Cliquez sur le talon pour piocher",
                "Glissez les cartes pour les déplacer",
                "A: Auto-complétion | R: Recommencer"
            ]
            
            for i, instruction in enumerate(instructions):
                texte = self.font_petit.render(instruction, True, GRIS)
                self.ecran.blit(texte, (50, HAUTEUR - 80 + i * 25))
    
    def dessiner_victoire(self):
        if self.victoire:
            # Fond semi-transparent
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(200)
            overlay.fill(NOIR)
            self.ecran.blit(overlay, (0, 0))
            
            # Message de victoire
            texte_victoire = self.font.render("FÉLICITATIONS!", True, OR)
            rect_victoire = texte_victoire.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 50))
            self.ecran.blit(texte_victoire, rect_victoire)
            
            # Score final
            texte_score_final = self.font.render(f"Score final: {self.score}", True, BLANC)
            rect_score_final = texte_score_final.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            self.ecran.blit(texte_score_final, rect_score_final)
            
            # Temps final
            temps_ecoule = (pygame.time.get_ticks() - self.temps_debut) // 1000
            minutes = temps_ecoule // 60
            secondes = temps_ecoule % 60
            texte_temps_final = self.font.render(f"Temps: {minutes:02d}:{secondes:02d}", True, BLANC)
            rect_temps_final = texte_temps_final.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 30))
            self.ecran.blit(texte_temps_final, rect_temps_final)
            
            # Instructions
            texte_recommencer = self.font_petit.render("R: Nouvelle partie | Q: Quitter", True, BLANC)
            rect_recommencer = texte_recommencer.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 80))
            self.ecran.blit(texte_recommencer, rect_recommencer)
    
    def gerer_clic(self, pos_souris):
        x, y = pos_souris
        
        # Clic sur le talon
        talon_rect = pygame.Rect(*self.pos_talon, 70, 100)
        if talon_rect.collidepoint(x, y):
            self.piocher_talon()
            return
        
        # Sélection de carte
        carte, origine, index = self.obtenir_carte_cliquee(pos_souris)
        
        if carte:
            if self.carte_selectionnee is None:
                # Première sélection
                self.carte_selectionnee = carte
                self.origine_selection = (origine, index)
                carte.selectionnee = True
                
                # Si c'est une colonne, sélectionner toutes les cartes à partir de cette position
                if origine == 'colonne':
                    col_index, carte_index = index
                    self.cartes_selectionnees = self.colonnes[col_index][carte_index:]
                    for c in self.cartes_selectionnees:
                        c.selectionnee = True
                else:
                    self.cartes_selectionnees = [carte]
            
            else:
                # Deuxième clic - essayer de déplacer
                if carte == self.carte_selectionnee:
                    # Désélectionner
                    for c in self.cartes_selectionnees:
                        c.selectionnee = False
                    self.carte_selectionnee = None
                    self.cartes_selectionnees = []
                    self.origine_selection = None
                else:
                    # Essayer de placer sur cette carte
                    zone_type, zone_index = self.obtenir_zone_cible(pos_souris)
                    if zone_type:
                        self.essayer_deplacement(zone_type, zone_index)
        
        else:
            # Clic sur une zone vide
            zone_type, zone_index = self.obtenir_zone_cible(pos_souris)
            if zone_type and self.carte_selectionnee:
                self.essayer_deplacement(zone_type, zone_index)
            else:
                # Désélectionner
                if self.carte_selectionnee:
                    for c in self.cartes_selectionnees:
                        c.selectionnee = False
                    self.carte_selectionnee = None
                    self.cartes_selectionnees = []
                    self.origine_selection = None
    
    def essayer_deplacement(self, zone_type, zone_index):
        if not self.carte_selectionnee:
            return
        
        origine, origine_index = self.origine_selection
        carte = self.carte_selectionnee
        
        # Vérifier si le déplacement est valide
        deplacement_valide = False
        
        if zone_type == 'fondation':
            if len(self.cartes_selectionnees) == 1:  # Une seule carte pour les fondations
                deplacement_valide = self.peut_deplacer_vers_fondation(carte, zone_index)
        
        elif zone_type == 'colonne':
            # Vérifier que toutes les cartes sélectionnées forment une séquence valide
            if self.cartes_sont_sequence_valide(self.cartes_selectionnees):
                deplacement_valide = self.peut_deplacer_vers_colonne(carte, zone_index)
        
        if deplacement_valide:
            self.deplacer_carte(carte, origine, zone_type, origine_index if zone_type == 'fondation' else zone_index)
        
        # Désélectionner
        for c in self.cartes_selectionnees:
            c.selectionnee = False
        self.carte_selectionnee = None
        self.cartes_selectionnees = []
        self.origine_selection = None
    
    def cartes_sont_sequence_valide(self, cartes):
        if len(cartes) <= 1:
            return True
        
        for i in range(len(cartes) - 1):
            carte_actuelle = cartes[i]
            carte_suivante = cartes[i + 1]
            
            if (carte_actuelle.est_rouge() == carte_suivante.est_rouge() or
                carte_actuelle.valeur != carte_suivante.valeur + 1):
                return False
        
        return True
    
    def reinitialiser(self):
        self.__init__()
    
    def dessiner(self):
        self.ecran.fill(VERT)
        
        # Dessiner les zones vides
        self.dessiner_zones_vides()
        
        # Mettre à jour les positions
        self.mettre_a_jour_positions()
        
        # Dessiner toutes les cartes
        # Talon
        if self.talon:
            self.talon[-1].dessiner(self.ecran)
        
        # Défausse
        if self.defausse:
            self.defausse[-1].dessiner(self.ecran)
        
        # Fondations
        for pile in self.fondations:
            if pile:
                pile[-1].dessiner(self.ecran)
        
        # Colonnes
        for colonne in self.colonnes:
            for carte in colonne:
                carte.dessiner(self.ecran)
        
        # Interface
        self.dessiner_interface()
        
        # Écran de victoire
        if self.victoire:
            self.dessiner_victoire()
        
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
                    if event.key == pygame.K_r:
                        self.reinitialiser()
                    elif event.key == pygame.K_a and not self.victoire:
                        self.auto_completion()
                    elif event.key == pygame.K_q and self.victoire:
                        en_cours = False
            
            # Vérifier la victoire
            if not self.victoire and self.verifier_victoire():
                self.victoire = True
                self.jeu_termine = True
            
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuSolitaire()
    jeu.executer()