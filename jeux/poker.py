import pygame
import random
import sys
from enum import Enum

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 1400
HAUTEUR = 900
FPS = 60

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (220, 20, 60)
VERT_TABLE = (0, 100, 0)
MARRON = (139, 69, 19)
OR = (255, 215, 0)
ARGENT = (192, 192, 192)
BLEU_FONCE = (25, 25, 112)
GRIS = (128, 128, 128)

class Couleur(Enum):
    COEUR = "♥"
    CARREAU = "♦"
    TREFLE = "♣"
    PIQUE = "♠"

class Valeur(Enum):
    DEUX = 2
    TROIS = 3
    QUATRE = 4
    CINQ = 5
    SIX = 6
    SEPT = 7
    HUIT = 8
    NEUF = 9
    DIX = 10
    VALET = 11
    DAME = 12
    ROI = 13
    AS = 14

class Carte:
    def __init__(self, couleur, valeur):
        self.couleur = couleur
        self.valeur = valeur
        self.largeur = 80
        self.hauteur = 110
    
    def dessiner(self, surface, x, y, face_cachee=False):
        # Ombre
        ombre_rect = pygame.Rect(x + 2, y + 2, self.largeur, self.hauteur)
        pygame.draw.rect(surface, (50, 50, 50), ombre_rect, border_radius=8)
        
        # Corps de la carte
        carte_rect = pygame.Rect(x, y, self.largeur, self.hauteur)
        
        if face_cachee:
            # Dos de carte
            pygame.draw.rect(surface, BLEU_FONCE, carte_rect, border_radius=8)
            pygame.draw.rect(surface, BLANC, carte_rect, width=2, border_radius=8)
            
            # Motif du dos
            for i in range(3):
                for j in range(4):
                    cx = x + 15 + i * 20
                    cy = y + 15 + j * 20
                    pygame.draw.circle(surface, ARGENT, (cx, cy), 5)
        else:
            # Face de la carte
            pygame.draw.rect(surface, BLANC, carte_rect, border_radius=8)
            pygame.draw.rect(surface, NOIR, carte_rect, width=2, border_radius=8)
            
            # Couleur du symbole
            couleur_symbole = ROUGE if self.couleur in [Couleur.COEUR, Couleur.CARREAU] else NOIR
            
            # Valeur en haut à gauche
            font_valeur = pygame.font.Font(None, 24)
            if self.valeur == Valeur.VALET:
                texte_valeur = "J"
            elif self.valeur == Valeur.DAME:
                texte_valeur = "Q"
            elif self.valeur == Valeur.ROI:
                texte_valeur = "K"
            elif self.valeur == Valeur.AS:
                texte_valeur = "A"
            else:
                texte_valeur = str(self.valeur.value)
            
            texte = font_valeur.render(texte_valeur, True, couleur_symbole)
            surface.blit(texte, (x + 5, y + 5))
            
            # Symbole en haut à gauche
            font_symbole = pygame.font.Font(None, 20)
            symbole = font_symbole.render(self.couleur.value, True, couleur_symbole)
            surface.blit(symbole, (x + 5, y + 25))
            
            # Grand symbole au centre
            font_grand = pygame.font.Font(None, 48)
            grand_symbole = font_grand.render(self.couleur.value, True, couleur_symbole)
            rect_symbole = grand_symbole.get_rect(center=(x + self.largeur//2, y + self.hauteur//2))
            surface.blit(grand_symbole, rect_symbole)
            
            # Valeur en bas à droite (inversée)
            texte_inv = pygame.transform.rotate(texte, 180)
            surface.blit(texte_inv, (x + self.largeur - 20, y + self.hauteur - 30))
            
            symbole_inv = pygame.transform.rotate(symbole, 180)
            surface.blit(symbole_inv, (x + self.largeur - 20, y + self.hauteur - 45))

class MainPoker:
    def __init__(self, cartes):
        self.cartes = cartes
        self.force, self.nom = self.evaluer_main()
    
    def evaluer_main(self):
        # Trier les cartes par valeur
        cartes_triees = sorted(self.cartes, key=lambda c: c.valeur.value, reverse=True)
        valeurs = [c.valeur.value for c in cartes_triees]
        couleurs = [c.couleur for c in cartes_triees]
        
        # Vérifier les combinaisons
        if self.est_quinte_flush_royale(valeurs, couleurs):
            return (10, "Quinte Flush Royale")
        elif self.est_quinte_flush(valeurs, couleurs):
            return (9, "Quinte Flush")
        elif self.est_carre(valeurs):
            return (8, "Carré")
        elif self.est_full(valeurs):
            return (7, "Full")
        elif self.est_flush(couleurs):
            return (6, "Flush")
        elif self.est_quinte(valeurs):
            return (5, "Quinte")
        elif self.est_brelan(valeurs):
            return (4, "Brelan")
        elif self.est_double_paire(valeurs):
            return (3, "Double Paire")
        elif self.est_paire(valeurs):
            return (2, "Paire")
        else:
            return (1, "Carte Haute")
    
    def est_quinte_flush_royale(self, valeurs, couleurs):
        return (self.est_flush(couleurs) and 
                valeurs == [14, 13, 12, 11, 10])
    
    def est_quinte_flush(self, valeurs, couleurs):
        return self.est_flush(couleurs) and self.est_quinte(valeurs)
    
    def est_carre(self, valeurs):
        compteur = {}
        for v in valeurs:
            compteur[v] = compteur.get(v, 0) + 1
        return 4 in compteur.values()
    
    def est_full(self, valeurs):
        compteur = {}
        for v in valeurs:
            compteur[v] = compteur.get(v, 0) + 1
        return 3 in compteur.values() and 2 in compteur.values()
    
    def est_flush(self, couleurs):
        return len(set(couleurs)) == 1
    
    def est_quinte(self, valeurs):
        if len(set(valeurs)) != 5:
            return False
        return max(valeurs) - min(valeurs) == 4 or valeurs == [14, 5, 4, 3, 2]
    
    def est_brelan(self, valeurs):
        compteur = {}
        for v in valeurs:
            compteur[v] = compteur.get(v, 0) + 1
        return 3 in compteur.values()
    
    def est_double_paire(self, valeurs):
        compteur = {}
        for v in valeurs:
            compteur[v] = compteur.get(v, 0) + 1
        paires = sum(1 for count in compteur.values() if count == 2)
        return paires == 2
    
    def est_paire(self, valeurs):
        compteur = {}
        for v in valeurs:
            compteur[v] = compteur.get(v, 0) + 1
        return 2 in compteur.values()

class Joueur:
    def __init__(self, nom, jetons=1000, est_humain=True):
        self.nom = nom
        self.jetons = jetons
        self.cartes = []
        self.est_humain = est_humain
        self.mise_actuelle = 0
        self.a_fold = False
        self.est_all_in = False
        self.position = (0, 0)
    
    def recevoir_carte(self, carte):
        self.cartes.append(carte)
    
    def miser(self, montant):
        montant = min(montant, self.jetons)
        self.jetons -= montant
        self.mise_actuelle += montant
        if self.jetons == 0:
            self.est_all_in = True
        return montant
    
    def fold(self):
        self.a_fold = True
    
    def reset_pour_nouvelle_main(self):
        self.cartes = []
        self.mise_actuelle = 0
        self.a_fold = False
        self.est_all_in = False

class JeuPoker:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Poker Texas Hold'em")
        self.horloge = pygame.time.Clock()
        
        # Créer le paquet
        self.paquet = self.creer_paquet()
        
        # Créer les joueurs
        self.joueurs = [
            Joueur("Vous", 1000, True),
            Joueur("IA 1", 1000, False),
            Joueur("IA 2", 1000, False),
            Joueur("IA 3", 1000, False)
        ]
        
        # Positions des joueurs autour de la table
        self.joueurs[0].position = (LARGEUR//2 - 40, HAUTEUR - 200)  # Bas
        self.joueurs[1].position = (100, HAUTEUR//2 - 55)  # Gauche
        self.joueurs[2].position = (LARGEUR//2 - 40, 100)  # Haut
        self.joueurs[3].position = (LARGEUR - 180, HAUTEUR//2 - 55)  # Droite
        
        # État du jeu
        self.cartes_communes = []
        self.pot = 0
        self.mise_minimale = 10
        self.grosse_blinde = 20
        self.petite_blinde = 10
        self.joueur_actuel = 0
        self.dealer = 0
        self.phase = "preflop"  # preflop, flop, turn, river, showdown
        
        # Interface
        self.font = pygame.font.Font(None, 36)
        self.font_petit = pygame.font.Font(None, 24)
        self.font_grand = pygame.font.Font(None, 48)
        
        # Boutons
        self.boutons = {}
        self.montant_mise = 0
        
        # État
        self.jeu_termine = False
        self.gagnant = None
        self.message = ""
        self.temps_message = 0
        
        self.nouvelle_main()
    
    def creer_paquet(self):
        paquet = []
        for couleur in Couleur:
            for valeur in Valeur:
                paquet.append(Carte(couleur, valeur))
        random.shuffle(paquet)
        return paquet
    
    def nouvelle_main(self):
        # Reset des joueurs
        for joueur in self.joueurs:
            joueur.reset_pour_nouvelle_main()
        
        # Nouveau paquet
        self.paquet = self.creer_paquet()
        self.cartes_communes = []
        self.pot = 0
        self.phase = "preflop"
        
        # Blindes
        petite_blinde_joueur = (self.dealer + 1) % len(self.joueurs)
        grosse_blinde_joueur = (self.dealer + 2) % len(self.joueurs)
        
        self.pot += self.joueurs[petite_blinde_joueur].miser(self.petite_blinde)
        self.pot += self.joueurs[grosse_blinde_joueur].miser(self.grosse_blinde)
        
        # Distribuer 2 cartes à chaque joueur
        for _ in range(2):
            for joueur in self.joueurs:
                if self.paquet:
                    joueur.recevoir_carte(self.paquet.pop())
        
        self.joueur_actuel = (self.dealer + 3) % len(self.joueurs)
        self.mise_minimale = self.grosse_blinde
    
    def phase_suivante(self):
        if self.phase == "preflop":
            # Flop - 3 cartes communes
            self.paquet.pop()  # Brûler une carte
            for _ in range(3):
                if self.paquet:
                    self.cartes_communes.append(self.paquet.pop())
            self.phase = "flop"
        elif self.phase == "flop":
            # Turn - 1 carte commune
            self.paquet.pop()  # Brûler une carte
            if self.paquet:
                self.cartes_communes.append(self.paquet.pop())
            self.phase = "turn"
        elif self.phase == "turn":
            # River - 1 carte commune
            self.paquet.pop()  # Brûler une carte
            if self.paquet:
                self.cartes_communes.append(self.paquet.pop())
            self.phase = "river"
        elif self.phase == "river":
            self.phase = "showdown"
            self.determiner_gagnant()
        
        # Reset des mises pour la nouvelle phase
        for joueur in self.joueurs:
            joueur.mise_actuelle = 0
        self.mise_minimale = 0
        self.joueur_actuel = (self.dealer + 1) % len(self.joueurs)
    
    def determiner_gagnant(self):
        joueurs_actifs = [j for j in self.joueurs if not j.a_fold]
        
        if len(joueurs_actifs) == 1:
            self.gagnant = joueurs_actifs[0]
        else:
            # Évaluer les mains
            meilleures_mains = []
            for joueur in joueurs_actifs:
                toutes_cartes = joueur.cartes + self.cartes_communes
                # Trouver la meilleure main de 5 cartes
                from itertools import combinations
                meilleures_combinaisons = []
                for combo in combinations(toutes_cartes, 5):
                    main = MainPoker(list(combo))
                    meilleures_combinaisons.append((main.force, main, joueur))
                
                meilleure = max(meilleures_combinaisons, key=lambda x: x[0])
                meilleures_mains.append(meilleure)
            
            # Trouver le gagnant
            meilleure_force = max(meilleures_mains, key=lambda x: x[0])[0]
            gagnants = [m for m in meilleures_mains if m[0] == meilleure_force]
            
            if len(gagnants) == 1:
                self.gagnant = gagnants[0][2]
                self.message = f"{self.gagnant.nom} gagne avec {gagnants[0][1].nom}!"
            else:
                # Égalité - partager le pot
                self.message = "Égalité!"
                for _, _, joueur in gagnants:
                    joueur.jetons += self.pot // len(gagnants)
                self.pot = 0
                self.temps_message = 300
                return
        
        # Donner le pot au gagnant
        if self.gagnant:
            self.gagnant.jetons += self.pot
            self.pot = 0
            self.temps_message = 300
    
    def action_joueur_humain(self, action, montant=0):
        joueur = self.joueurs[0]
        
        if action == "fold":
            joueur.fold()
        elif action == "call":
            mise_necessaire = max(0, self.mise_minimale - joueur.mise_actuelle)
            self.pot += joueur.miser(mise_necessaire)
        elif action == "raise":
            mise_necessaire = max(0, self.mise_minimale - joueur.mise_actuelle)
            self.pot += joueur.miser(mise_necessaire + montant)
            self.mise_minimale = joueur.mise_actuelle
        elif action == "check":
            pass  # Aucune action nécessaire
        
        self.joueur_suivant()
    
    def action_ia(self, joueur):
        # IA simple basée sur la force de la main
        if len(self.cartes_communes) >= 3:
            toutes_cartes = joueur.cartes + self.cartes_communes
            from itertools import combinations
            meilleures_combinaisons = []
            for combo in combinations(toutes_cartes, 5):
                main = MainPoker(list(combo))
                meilleures_combinaisons.append(main.force)
            force_main = max(meilleures_combinaisons)
        else:
            # Évaluation simple avec 2 cartes
            valeurs = [c.valeur.value for c in joueur.cartes]
            if valeurs[0] == valeurs[1]:  # Paire
                force_main = 6
            elif abs(valeurs[0] - valeurs[1]) <= 3:  # Cartes connectées
                force_main = 4
            elif max(valeurs) >= 11:  # Carte haute
                force_main = 3
            else:
                force_main = 1
        
        mise_necessaire = max(0, self.mise_minimale - joueur.mise_actuelle)
        
        if force_main >= 7:  # Main très forte
            if mise_necessaire == 0:
                # Relancer
                montant_relance = random.randint(20, 50)
                self.pot += joueur.miser(montant_relance)
                self.mise_minimale = joueur.mise_actuelle
            else:
                # Suivre
                self.pot += joueur.miser(mise_necessaire)
        elif force_main >= 4:  # Main correcte
            if mise_necessaire <= joueur.jetons // 4:
                # Suivre
                self.pot += joueur.miser(mise_necessaire)
            else:
                # Se coucher
                joueur.fold()
        else:  # Main faible
            if mise_necessaire == 0:
                # Checker
                pass
            else:
                # Se coucher
                joueur.fold()
        
        self.joueur_suivant()
    
    def joueur_suivant(self):
        # Vérifier si le tour de mise est terminé
        joueurs_actifs = [j for j in self.joueurs if not j.a_fold]
        
        if len(joueurs_actifs) <= 1:
            self.phase = "showdown"
            self.determiner_gagnant()
            return
        
        # Vérifier si tous les joueurs actifs ont misé le même montant
        mises_actuelles = [j.mise_actuelle for j in joueurs_actifs if not j.est_all_in]
        if len(set(mises_actuelles)) <= 1 and all(j.mise_actuelle >= self.mise_minimale or j.est_all_in for j in joueurs_actifs):
            self.phase_suivante()
            return
        
        # Passer au joueur suivant
        self.joueur_actuel = (self.joueur_actuel + 1) % len(self.joueurs)
        
        # Passer les joueurs qui ont fold
        while self.joueurs[self.joueur_actuel].a_fold:
            self.joueur_actuel = (self.joueur_actuel + 1) % len(self.joueurs)
    
    def dessiner_table(self):
        # Table de poker
        self.ecran.fill(MARRON)
        
        # Tapis vert ovale
        centre_x, centre_y = LARGEUR // 2, HAUTEUR // 2
        pygame.draw.ellipse(self.ecran, VERT_TABLE, 
                           (centre_x - 300, centre_y - 150, 600, 300))
        pygame.draw.ellipse(self.ecran, MARRON, 
                           (centre_x - 300, centre_y - 150, 600, 300), 5)
    
    def dessiner_cartes_communes(self):
        if self.cartes_communes:
            x_debut = LARGEUR // 2 - (len(self.cartes_communes) * 90) // 2
            y = HAUTEUR // 2 - 55
            
            for i, carte in enumerate(self.cartes_communes):
                carte.dessiner(self.ecran, x_debut + i * 90, y)
    
    def dessiner_joueurs(self):
        for i, joueur in enumerate(self.joueurs):
            x, y = joueur.position
            
            # Cartes du joueur
            if i == 0:  # Joueur humain - montrer les cartes
                for j, carte in enumerate(joueur.cartes):
                    carte.dessiner(self.ecran, x + j * 85, y)
            else:  # IA - cacher les cartes
                if not joueur.a_fold:
                    for j in range(len(joueur.cartes)):
                        carte_cachee = Carte(Couleur.PIQUE, Valeur.AS)
                        carte_cachee.dessiner(self.ecran, x + j * 85, y, True)
            
            # Informations du joueur
            couleur_nom = OR if i == self.joueur_actuel else BLANC
            if joueur.a_fold:
                couleur_nom = GRIS
            
            texte_nom = self.font_petit.render(joueur.nom, True, couleur_nom)
            texte_jetons = self.font_petit.render(f"Jetons: {joueur.jetons}", True, BLANC)
            
            if i == 0:  # Bas
                self.ecran.blit(texte_nom, (x, y - 40))
                self.ecran.blit(texte_jetons, (x, y - 20))
            elif i == 1:  # Gauche
                self.ecran.blit(texte_nom, (x, y - 40))
                self.ecran.blit(texte_jetons, (x, y - 20))
            elif i == 2:  # Haut
                self.ecran.blit(texte_nom, (x, y + 130))
                self.ecran.blit(texte_jetons, (x, y + 150))
            elif i == 3:  # Droite
                self.ecran.blit(texte_nom, (x, y - 40))
                self.ecran.blit(texte_jetons, (x, y - 20))
            
            # Mise actuelle
            if joueur.mise_actuelle > 0:
                texte_mise = self.font_petit.render(f"Mise: {joueur.mise_actuelle}", True, OR)
                if i == 0:
                    self.ecran.blit(texte_mise, (x + 200, y + 50))
                elif i == 1:
                    self.ecran.blit(texte_mise, (x + 200, y + 50))
                elif i == 2:
                    self.ecran.blit(texte_mise, (x, y + 170))
                elif i == 3:
                    self.ecran.blit(texte_mise, (x - 100, y + 50))
            
            # Indicateur fold
            if joueur.a_fold:
                texte_fold = self.font.render("FOLD", True, ROUGE)
                self.ecran.blit(texte_fold, (x + 20, y + 30))
    
    def dessiner_interface(self):
        # Pot
        texte_pot = self.font_grand.render(f"Pot: {self.pot}", True, OR)
        rect_pot = texte_pot.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 100))
        self.ecran.blit(texte_pot, rect_pot)
        
        # Phase
        texte_phase = self.font.render(f"Phase: {self.phase.upper()}", True, BLANC)
        self.ecran.blit(texte_phase, (10, 10))
        
        # Boutons pour le joueur humain
        if self.joueur_actuel == 0 and self.phase != "showdown":
            y_boutons = HAUTEUR - 100
            
            # Fold
            bouton_fold = pygame.Rect(50, y_boutons, 80, 40)
            pygame.draw.rect(self.ecran, ROUGE, bouton_fold, border_radius=5)
            texte_fold = self.font_petit.render("FOLD", True, BLANC)
            rect_fold = texte_fold.get_rect(center=bouton_fold.center)
            self.ecran.blit(texte_fold, rect_fold)
            self.boutons["fold"] = bouton_fold
            
            # Check/Call
            mise_necessaire = max(0, self.mise_minimale - self.joueurs[0].mise_actuelle)
            if mise_necessaire == 0:
                bouton_check = pygame.Rect(150, y_boutons, 80, 40)
                pygame.draw.rect(self.ecran, VERT_TABLE, bouton_check, border_radius=5)
                texte_check = self.font_petit.render("CHECK", True, BLANC)
                rect_check = texte_check.get_rect(center=bouton_check.center)
                self.ecran.blit(texte_check, rect_check)
                self.boutons["check"] = bouton_check
            else:
                bouton_call = pygame.Rect(150, y_boutons, 80, 40)
                pygame.draw.rect(self.ecran, BLEU_FONCE, bouton_call, border_radius=5)
                texte_call = self.font_petit.render(f"CALL {mise_necessaire}", True, BLANC)
                rect_call = texte_call.get_rect(center=bouton_call.center)
                self.ecran.blit(texte_call, rect_call)
                self.boutons["call"] = bouton_call
            
            # Raise
            bouton_raise = pygame.Rect(250, y_boutons, 80, 40)
            pygame.draw.rect(self.ecran, OR, bouton_raise, border_radius=5)
            texte_raise = self.font_petit.render("RAISE", True, NOIR)
            rect_raise = texte_raise.get_rect(center=bouton_raise.center)
            self.ecran.blit(texte_raise, rect_raise)
            self.boutons["raise"] = bouton_raise
        
        # Messages
        if self.temps_message > 0:
            texte_message = self.font.render(self.message, True, OR)
            rect_message = texte_message.get_rect(center=(LARGEUR // 2, 50))
            fond_message = rect_message.inflate(20, 10)
            pygame.draw.rect(self.ecran, NOIR, fond_message, border_radius=5)
            self.ecran.blit(texte_message, rect_message)
            self.temps_message -= 1
        
        # Bouton nouvelle main
        if self.phase == "showdown":
            bouton_nouvelle = pygame.Rect(LARGEUR // 2 - 100, HAUTEUR - 60, 200, 40)
            pygame.draw.rect(self.ecran, VERT_TABLE, bouton_nouvelle, border_radius=5)
            texte_nouvelle = self.font.render("NOUVELLE MAIN", True, BLANC)
            rect_nouvelle = texte_nouvelle.get_rect(center=bouton_nouvelle.center)
            self.ecran.blit(texte_nouvelle, rect_nouvelle)
            self.boutons["nouvelle"] = bouton_nouvelle
    
    def gerer_clic(self, pos):
        for action, bouton in self.boutons.items():
            if bouton.collidepoint(pos):
                if action == "fold":
                    self.action_joueur_humain("fold")
                elif action == "check":
                    self.action_joueur_humain("check")
                elif action == "call":
                    self.action_joueur_humain("call")
                elif action == "raise":
                    self.action_joueur_humain("raise", 20)  # Relance de 20
                elif action == "nouvelle":
                    self.dealer = (self.dealer + 1) % len(self.joueurs)
                    self.nouvelle_main()
                break
    
    def tour_ia(self):
        if (self.joueur_actuel != 0 and 
            self.phase != "showdown" and 
            not self.joueurs[self.joueur_actuel].a_fold):
            
            pygame.time.wait(1000)  # Délai pour l'IA
            self.action_ia(self.joueurs[self.joueur_actuel])
    
    def dessiner(self):
        self.dessiner_table()
        self.dessiner_cartes_communes()
        self.dessiner_joueurs()
        self.dessiner_interface()
        
        pygame.display.flip()
    
    def executer(self):
        en_cours = True
        
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.gerer_clic(event.pos)
            
            # Tour de l'IA
            self.tour_ia()
            
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuPoker()
    jeu.executer()