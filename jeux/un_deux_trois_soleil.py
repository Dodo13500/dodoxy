import pygame
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
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
BLEU = (0, 0, 255)
JAUNE = (255, 255, 0)
GRIS = (128, 128, 128)
ORANGE = (255, 165, 0)

class Joueur:
    def __init__(self, x, y, couleur, nom):
        self.x = x
        self.y = y
        self.couleur = couleur
        self.nom = nom
        self.vitesse = 2
        self.en_mouvement = False
        self.direction_x = 0
        self.direction_y = 0
        self.taille = 20
        self.elimine = False
    
    def deplacer(self, dx, dy, peut_bouger):
        if peut_bouger and not self.elimine:
            self.x += dx * self.vitesse
            self.y += dy * self.vitesse
            self.en_mouvement = (dx != 0 or dy != 0)
            
            # Limiter aux bordures
            self.x = max(self.taille, min(LARGEUR - self.taille, self.x))
            self.y = max(self.taille, min(HAUTEUR - 100, self.y))
    
    def dessiner(self, surface):
        if not self.elimine:
            # Corps
            pygame.draw.circle(surface, self.couleur, (int(self.x), int(self.y)), self.taille)
            pygame.draw.circle(surface, NOIR, (int(self.x), int(self.y)), self.taille, 2)
            
            # Nom
            font = pygame.font.Font(None, 24)
            texte = font.render(self.nom, True, NOIR)
            rect_texte = texte.get_rect(center=(self.x, self.y - self.taille - 15))
            surface.blit(texte, rect_texte)

class JeuUnDeuxTroisSoleil:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("1, 2, 3... Soleil!")
        self.horloge = pygame.time.Clock()
        
        # Joueurs
        self.joueur_humain = Joueur(50, HAUTEUR//2, BLEU, "Vous")
        self.joueurs_ia = [
            Joueur(80, HAUTEUR//2 - 100, ROUGE, "IA 1"),
            Joueur(80, HAUTEUR//2 + 100, VERT, "IA 2"),
            Joueur(120, HAUTEUR//2 - 50, ORANGE, "IA 3"),
            Joueur(120, HAUTEUR//2 + 50, (255, 0, 255), "IA 4")
        ]
        
        # Gardien (celui qui compte)
        self.gardien_x = LARGEUR - 100
        self.gardien_y = HAUTEUR//2
        self.gardien_regarde = False
        
        # Timing du jeu
        self.temps_compte = 0
        self.duree_compte = random.randint(2000, 5000)  # 2-5 secondes
        self.temps_regard = 0
        self.duree_regard = random.randint(1000, 3000)  # 1-3 secondes
        
        # État du jeu
        self.phase = "compte"  # "compte" ou "regarde"
        self.jeu_termine = False
        self.gagnant = None
        self.message = ""
        self.temps_message = 0
        
        # Interface
        self.font = pygame.font.Font(None, 36)
        self.font_grand = pygame.font.Font(None, 48)
        self.font_petit = pygame.font.Font(None, 24)
        
        # Ligne d'arrivée
        self.ligne_arrivee = LARGEUR - 150
    
    def mettre_a_jour_phase(self):
        temps_actuel = pygame.time.get_ticks()
        
        if self.phase == "compte":
            if temps_actuel - self.temps_compte > self.duree_compte:
                self.phase = "regarde"
                self.gardien_regarde = True
                self.temps_regard = temps_actuel
                self.duree_regard = random.randint(1000, 3000)
                self.verifier_mouvements()
        
        elif self.phase == "regarde":
            if temps_actuel - self.temps_regard > self.duree_regard:
                self.phase = "compte"
                self.gardien_regarde = False
                self.temps_compte = temps_actuel
                self.duree_compte = random.randint(2000, 5000)
    
    def verifier_mouvements(self):
        # Vérifier si le joueur humain bouge
        if self.joueur_humain.en_mouvement and not self.joueur_humain.elimine:
            self.joueur_humain.elimine = True
            self.message = "Vous avez été éliminé!"
            self.temps_message = pygame.time.get_ticks()
        
        # Vérifier les IA
        for ia in self.joueurs_ia:
            if ia.en_mouvement and not ia.elimine:
                ia.elimine = True
    
    def deplacer_ia(self):
        if self.phase == "compte":
            for ia in self.joueurs_ia:
                if not ia.elimine:
                    # L'IA avance vers la ligne d'arrivée
                    if random.random() < 0.7:  # 70% de chance de bouger
                        dx = random.uniform(0.5, 1.5)
                        dy = random.uniform(-0.3, 0.3)
                        ia.deplacer(dx, dy, True)
    
    def verifier_victoire(self):
        # Vérifier si le joueur humain a gagné
        if self.joueur_humain.x >= self.ligne_arrivee and not self.joueur_humain.elimine:
            self.jeu_termine = True
            self.gagnant = "Vous"
            return
        
        # Vérifier si une IA a gagné
        for ia in self.joueurs_ia:
            if ia.x >= self.ligne_arrivee and not ia.elimine:
                self.jeu_termine = True
                self.gagnant = ia.nom
                return
        
        # Vérifier si tous les joueurs sauf un sont éliminés
        joueurs_restants = []
        if not self.joueur_humain.elimine:
            joueurs_restants.append("Vous")
        for ia in self.joueurs_ia:
            if not ia.elimine:
                joueurs_restants.append(ia.nom)
        
        if len(joueurs_restants) == 1:
            self.jeu_termine = True
            self.gagnant = joueurs_restants[0]
        elif len(joueurs_restants) == 0:
            self.jeu_termine = True
            self.gagnant = "Personne"
    
    def dessiner_gardien(self):
        # Corps du gardien
        pygame.draw.circle(self.ecran, JAUNE, (self.gardien_x, self.gardien_y), 30)
        pygame.draw.circle(self.ecran, NOIR, (self.gardien_x, self.gardien_y), 30, 3)
        
        # Yeux selon l'état
        if self.gardien_regarde:
            # Yeux ouverts (regarde)
            pygame.draw.circle(self.ecran, ROUGE, (self.gardien_x - 10, self.gardien_y - 10), 5)
            pygame.draw.circle(self.ecran, ROUGE, (self.gardien_x + 10, self.gardien_y - 10), 5)
        else:
            # Yeux fermés (compte)
            pygame.draw.line(self.ecran, NOIR, 
                           (self.gardien_x - 15, self.gardien_y - 10), 
                           (self.gardien_x - 5, self.gardien_y - 10), 3)
            pygame.draw.line(self.ecran, NOIR, 
                           (self.gardien_x + 5, self.gardien_y - 10), 
                           (self.gardien_x + 15, self.gardien_y - 10), 3)
        
        # Bouche
        if self.phase == "compte":
            pygame.draw.arc(self.ecran, NOIR, 
                          (self.gardien_x - 10, self.gardien_y, 20, 15), 0, 3.14, 3)
    
    def dessiner_interface(self):
        # Phase actuelle
        if self.phase == "compte":
            texte_phase = self.font.render("1, 2, 3... BOUGEZ!", True, VERT)
        else:
            texte_phase = self.font.render("SOLEIL! STOP!", True, ROUGE)
        
        rect_phase = texte_phase.get_rect(center=(LARGEUR//2, 50))
        self.ecran.blit(texte_phase, rect_phase)
        
        # Instructions
        if not self.jeu_termine:
            instruction = self.font_petit.render("Utilisez les flèches pour bouger. Arrêtez-vous quand le gardien regarde!", True, NOIR)
            self.ecran.blit(instruction, (10, 10))
        
        # Ligne d'arrivée
        pygame.draw.line(self.ecran, ROUGE, 
                        (self.ligne_arrivee, 0), 
                        (self.ligne_arrivee, HAUTEUR), 5)
        
        texte_arrivee = self.font_petit.render("ARRIVÉE", True, ROUGE)
        self.ecran.blit(texte_arrivee, (self.ligne_arrivee + 10, HAUTEUR//2))
        
        # Messages temporaires
        if self.message and pygame.time.get_ticks() - self.temps_message < 3000:
            texte_message = self.font.render(self.message, True, ROUGE)
            rect_message = texte_message.get_rect(center=(LARGEUR//2, HAUTEUR - 50))
            self.ecran.blit(texte_message, rect_message)
        
        # Joueurs restants
        joueurs_restants = 1 if not self.joueur_humain.elimine else 0
        for ia in self.joueurs_ia:
            if not ia.elimine:
                joueurs_restants += 1
        
        texte_restants = self.font_petit.render(f"Joueurs restants: {joueurs_restants}", True, NOIR)
        self.ecran.blit(texte_restants, (10, HAUTEUR - 30))
    
    def dessiner_fin_jeu(self):
        # Fond semi-transparent
        overlay = pygame.Surface((LARGEUR, HAUTEUR))
        overlay.set_alpha(128)
        overlay.fill(NOIR)
        self.ecran.blit(overlay, (0, 0))
        
        # Message de victoire
        if self.gagnant == "Vous":
            texte_fin = self.font_grand.render("FÉLICITATIONS! VOUS AVEZ GAGNÉ!", True, VERT)
        elif self.gagnant == "Personne":
            texte_fin = self.font_grand.render("TOUS ÉLIMINÉS!", True, ROUGE)
        else:
            texte_fin = self.font_grand.render(f"{self.gagnant} A GAGNÉ!", True, ROUGE)
        
        rect_fin = texte_fin.get_rect(center=(LARGEUR//2, HAUTEUR//2))
        self.ecran.blit(texte_fin, rect_fin)
        
        # Instructions pour recommencer
        texte_recommencer = self.font.render("Appuyez sur R pour recommencer ou Q pour quitter", True, BLANC)
        rect_recommencer = texte_recommencer.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 60))
        self.ecran.blit(texte_recommencer, rect_recommencer)
    
    def reinitialiser(self):
        # Réinitialiser les positions
        self.joueur_humain = Joueur(50, HAUTEUR//2, BLEU, "Vous")
        self.joueurs_ia = [
            Joueur(80, HAUTEUR//2 - 100, ROUGE, "IA 1"),
            Joueur(80, HAUTEUR//2 + 100, VERT, "IA 2"),
            Joueur(120, HAUTEUR//2 - 50, ORANGE, "IA 3"),
            Joueur(120, HAUTEUR//2 + 50, (255, 0, 255), "IA 4")
        ]
        
        # Réinitialiser l'état du jeu
        self.gardien_regarde = False
        self.temps_compte = pygame.time.get_ticks()
        self.duree_compte = random.randint(2000, 5000)
        self.phase = "compte"
        self.jeu_termine = False
        self.gagnant = None
        self.message = ""
    
    def dessiner(self):
        self.ecran.fill(BLANC)
        
        # Dessiner le terrain
        pygame.draw.rect(self.ecran, (144, 238, 144), (0, 100, LARGEUR, HAUTEUR - 200))
        
        if not self.jeu_termine:
            # Dessiner les joueurs
            self.joueur_humain.dessiner(self.ecran)
            for ia in self.joueurs_ia:
                ia.dessiner(self.ecran)
            
            # Dessiner le gardien
            self.dessiner_gardien()
            
            # Interface
            self.dessiner_interface()
        else:
            # Dessiner les joueurs
            self.joueur_humain.dessiner(self.ecran)
            for ia in self.joueurs_ia:
                ia.dessiner(self.ecran)
            
            # Dessiner le gardien
            self.dessiner_gardien()
            
            # Interface
            self.dessiner_interface()
            
            # Écran de fin
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
                    if self.jeu_termine:
                        if event.key == pygame.K_r:
                            self.reinitialiser()
                        elif event.key == pygame.K_q:
                            en_cours = False
            
            if not self.jeu_termine:
                # Déplacement du joueur
                dx, dy = 0, 0
                if touches[pygame.K_LEFT]:
                    dx = -1
                elif touches[pygame.K_RIGHT]:
                    dx = 1
                if touches[pygame.K_UP]:
                    dy = -1
                elif touches[pygame.K_DOWN]:
                    dy = 1
                
                peut_bouger = (self.phase == "compte")
                self.joueur_humain.deplacer(dx, dy, peut_bouger)
                
                # Déplacer les IA
                self.deplacer_ia()
                
                # Mettre à jour la phase du jeu
                self.mettre_a_jour_phase()
                
                # Vérifier les conditions de victoire
                self.verifier_victoire()
            
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuUnDeuxTroisSoleil()
    jeu.executer()