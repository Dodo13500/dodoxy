import pygame
import math
import random
import sys

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 1200
HAUTEUR = 700
FPS = 60

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
VERT_TABLE = (0, 100, 0)
MARRON = (139, 69, 19)
ROUGE = (255, 0, 0)
JAUNE = (255, 255, 0)
BLEU = (0, 0, 255)
VIOLET = (128, 0, 128)
ORANGE = (255, 165, 0)
VERT = (0, 255, 0)
BORDEAUX = (128, 0, 0)

class Bille:
    def __init__(self, x, y, couleur, numero):
        self.x = x
        self.y = y
        self.vitesse_x = 0
        self.vitesse_y = 0
        self.couleur = couleur
        self.numero = numero
        self.rayon = 12
        self.friction = 0.98
        self.en_mouvement = False
        self.dans_trou = False
    
    def mettre_a_jour(self):
        if self.en_mouvement and not self.dans_trou:
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
    
    def appliquer_force(self, force_x, force_y):
        self.vitesse_x = force_x
        self.vitesse_y = force_y
        self.en_mouvement = True
    
    def collision_avec_bords(self, largeur_table, hauteur_table, marge):
        rebond = False
        
        if self.x - self.rayon <= marge:
            self.x = marge + self.rayon
            self.vitesse_x = -self.vitesse_x * 0.8
            rebond = True
        elif self.x + self.rayon >= largeur_table - marge:
            self.x = largeur_table - marge - self.rayon
            self.vitesse_x = -self.vitesse_x * 0.8
            rebond = True
        
        if self.y - self.rayon <= marge:
            self.y = marge + self.rayon
            self.vitesse_y = -self.vitesse_y * 0.8
            rebond = True
        elif self.y + self.rayon >= hauteur_table - marge:
            self.y = hauteur_table - marge - self.rayon
            self.vitesse_y = -self.vitesse_y * 0.8
            rebond = True
        
        return rebond
    
    def collision_avec_bille(self, autre_bille):
        if self.dans_trou or autre_bille.dans_trou:
            return False
        
        dx = autre_bille.x - self.x
        dy = autre_bille.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.rayon + autre_bille.rayon:
            # Normaliser le vecteur de collision
            if distance > 0:
                dx /= distance
                dy /= distance
            else:
                dx, dy = 1, 0
            
            # Séparer les billes
            overlap = self.rayon + autre_bille.rayon - distance
            self.x -= dx * overlap * 0.5
            self.y -= dy * overlap * 0.5
            autre_bille.x += dx * overlap * 0.5
            autre_bille.y += dy * overlap * 0.5
            
            # Calculer les nouvelles vitesses (collision élastique)
            v1_normal = self.vitesse_x * dx + self.vitesse_y * dy
            v2_normal = autre_bille.vitesse_x * dx + autre_bille.vitesse_y * dy
            
            # Conservation de l'énergie et de la quantité de mouvement
            new_v1_normal = v2_normal
            new_v2_normal = v1_normal
            
            # Mettre à jour les vitesses
            self.vitesse_x += (new_v1_normal - v1_normal) * dx * 0.9
            self.vitesse_y += (new_v1_normal - v1_normal) * dy * 0.9
            autre_bille.vitesse_x += (new_v2_normal - v2_normal) * dx * 0.9
            autre_bille.vitesse_y += (new_v2_normal - v2_normal) * dy * 0.9
            
            # Marquer comme en mouvement
            if abs(self.vitesse_x) > 0.1 or abs(self.vitesse_y) > 0.1:
                self.en_mouvement = True
            if abs(autre_bille.vitesse_x) > 0.1 or abs(autre_bille.vitesse_y) > 0.1:
                autre_bille.en_mouvement = True
            
            return True
        return False
    
    def dessiner(self, surface, offset_x, offset_y):
        if not self.dans_trou:
            x_ecran = int(self.x + offset_x)
            y_ecran = int(self.y + offset_y)
            
            # Ombre
            pygame.draw.circle(surface, (50, 50, 50), 
                             (x_ecran + 2, y_ecran + 2), self.rayon)
            
            # Corps de la bille
            pygame.draw.circle(surface, self.couleur, (x_ecran, y_ecran), self.rayon)
            
            # Reflet
            pygame.draw.circle(surface, BLANC, 
                             (x_ecran - 4, y_ecran - 4), self.rayon // 3)
            
            # Numéro sur la bille
            if self.numero > 0:
                font = pygame.font.Font(None, 20)
                couleur_texte = BLANC if self.couleur in [(0, 0, 0), (128, 0, 0), (128, 0, 128)] else NOIR
                texte = font.render(str(self.numero), True, couleur_texte)
                rect_texte = texte.get_rect(center=(x_ecran, y_ecran))
                surface.blit(texte, rect_texte)

class Trou:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rayon = 25
    
    def contient_bille(self, bille):
        if bille.dans_trou:
            return False
        
        dx = bille.x - self.x
        dy = bille.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance < self.rayon - bille.rayon // 2
    
    def dessiner(self, surface, offset_x, offset_y):
        x_ecran = int(self.x + offset_x)
        y_ecran = int(self.y + offset_y)
        
        # Trou noir avec bordure
        pygame.draw.circle(surface, NOIR, (x_ecran, y_ecran), self.rayon)
        pygame.draw.circle(surface, MARRON, (x_ecran, y_ecran), self.rayon, 3)

class JeuBillard:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Billard 8-Ball")
        self.horloge = pygame.time.Clock()
        
        # Dimensions de la table
        self.largeur_table = 800
        self.hauteur_table = 400
        self.marge = 30
        self.offset_x = (LARGEUR - self.largeur_table) // 2
        self.offset_y = (HAUTEUR - self.hauteur_table) // 2
        
        # Créer les billes
        self.billes = []
        self.creer_billes()
        
        # Créer les trous
        self.trous = [
            Trou(self.marge, self.marge),  # Coin haut-gauche
            Trou(self.largeur_table // 2, self.marge),  # Milieu haut
            Trou(self.largeur_table - self.marge, self.marge),  # Coin haut-droit
            Trou(self.marge, self.hauteur_table - self.marge),  # Coin bas-gauche
            Trou(self.largeur_table // 2, self.hauteur_table - self.marge),  # Milieu bas
            Trou(self.largeur_table - self.marge, self.hauteur_table - self.marge)  # Coin bas-droit
        ]
        
        # État du jeu
        self.joueur_actuel = 1  # 1 ou 2
        self.billes_joueur1 = []  # Billes pleines (1-7)
        self.billes_joueur2 = []  # Billes rayées (9-15)
        self.groupes_assignes = False
        
        # Contrôles
        self.viser = False
        self.position_souris = (0, 0)
        self.force_max = 15
        
        # Interface
        self.font = pygame.font.Font(None, 36)
        self.font_petit = pygame.font.Font(None, 24)
        
        # État de fin
        self.jeu_termine = False
        self.gagnant = None
        self.message = ""
        self.temps_message = 0
    
    def creer_billes(self):
        # Bille blanche (cue ball)
        self.bille_blanche = Bille(200, self.hauteur_table // 2, BLANC, 0)
        self.billes.append(self.bille_blanche)
        
        # Couleurs des billes numérotées
        couleurs_billes = {
            1: JAUNE, 2: BLEU, 3: ROUGE, 4: VIOLET, 5: ORANGE, 6: VERT, 7: BORDEAUX,
            8: NOIR,
            9: JAUNE, 10: BLEU, 11: ROUGE, 12: VIOLET, 13: ORANGE, 14: VERT, 15: BORDEAUX
        }
        
        # Position de départ du triangle
        x_triangle = 600
        y_triangle = self.hauteur_table // 2
        
        # Formation triangulaire des billes
        positions = [
            (0, 0),  # 1ère rangée
            (-1, -0.5), (-1, 0.5),  # 2ème rangée
            (-2, -1), (-2, 0), (-2, 1),  # 3ème rangée
            (-3, -1.5), (-3, -0.5), (-3, 0.5), (-3, 1.5),  # 4ème rangée
            (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2)  # 5ème rangée
        ]
        
        # Ordre spécial pour le billard 8-ball
        ordre_billes = [1, 9, 2, 10, 8, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]
        
        for i, numero in enumerate(ordre_billes):
            pos_x, pos_y = positions[i]
            x = x_triangle + pos_x * 25
            y = y_triangle + pos_y * 25
            couleur = couleurs_billes[numero]
            
            bille = Bille(x, y, couleur, numero)
            self.billes.append(bille)
    
    def toutes_billes_arretees(self):
        return not any(bille.en_mouvement for bille in self.billes if not bille.dans_trou)
    
    def verifier_trous(self):
        billes_empochees = []
        
        for bille in self.billes:
            if not bille.dans_trou:
                for trou in self.trous:
                    if trou.contient_bille(bille):
                        bille.dans_trou = True
                        bille.en_mouvement = False
                        billes_empochees.append(bille)
                        break
        
        return billes_empochees
    
    def assigner_groupes(self, bille_empochee):
        if not self.groupes_assignes and bille_empochee.numero != 8:
            if 1 <= bille_empochee.numero <= 7:
                # Joueur actuel prend les pleines
                self.billes_joueur1 = list(range(1, 8)) if self.joueur_actuel == 1 else list(range(9, 16))
                self.billes_joueur2 = list(range(9, 16)) if self.joueur_actuel == 1 else list(range(1, 8))
            elif 9 <= bille_empochee.numero <= 15:
                # Joueur actuel prend les rayées
                self.billes_joueur1 = list(range(9, 16)) if self.joueur_actuel == 1 else list(range(1, 8))
                self.billes_joueur2 = list(range(1, 8)) if self.joueur_actuel == 1 else list(range(9, 16))
            
            self.groupes_assignes = True
            groupe = "pleines" if (self.joueur_actuel == 1 and 1 <= bille_empochee.numero <= 7) or \
                                 (self.joueur_actuel == 2 and 1 <= bille_empochee.numero <= 7) else "rayées"
            self.message = f"Joueur {self.joueur_actuel} a les billes {groupe}!"
            self.temps_message = 180
    
    def verifier_victoire(self, billes_empochees):
        # Vérifier si la bille 8 a été empochée
        bille_8_empochee = any(b.numero == 8 for b in billes_empochees)
        
        if bille_8_empochee:
            # Vérifier si le joueur a fini ses billes
            billes_joueur = self.billes_joueur1 if self.joueur_actuel == 1 else self.billes_joueur2
            billes_restantes = [b for b in self.billes if b.numero in billes_joueur and not b.dans_trou]
            
            if len(billes_restantes) == 0:
                # Victoire légitime
                self.jeu_termine = True
                self.gagnant = self.joueur_actuel
                self.message = f"Joueur {self.joueur_actuel} gagne!"
            else:
                # Défaite (bille 8 empochée trop tôt)
                self.jeu_termine = True
                self.gagnant = 2 if self.joueur_actuel == 1 else 1
                self.message = f"Joueur {self.joueur_actuel} perd! (Bille 8 empochée trop tôt)"
            
            self.temps_message = 300
            return
        
        # Vérifier si la bille blanche est empochée
        if any(b.numero == 0 for b in billes_empochees):
            self.message = "Faute! Bille blanche empochée"
            self.temps_message = 120
            # Remettre la bille blanche en jeu
            self.bille_blanche.dans_trou = False
            self.bille_blanche.x = 200
            self.bille_blanche.y = self.hauteur_table // 2
            self.changer_joueur()
            return
        
        # Vérifier les empochages légitimes
        empochage_legitime = False
        for bille in billes_empochees:
            if self.groupes_assignes:
                billes_joueur = self.billes_joueur1 if self.joueur_actuel == 1 else self.billes_joueur2
                if bille.numero in billes_joueur:
                    empochage_legitime = True
                    break
            else:
                # Premier empochage - assigner les groupes
                self.assigner_groupes(bille)
                empochage_legitime = True
        
        # Changer de joueur si aucun empochage légitime
        if not empochage_legitime and len(billes_empochees) > 0:
            self.changer_joueur()
        elif len(billes_empochees) == 0:
            self.changer_joueur()
    
    def changer_joueur(self):
        self.joueur_actuel = 2 if self.joueur_actuel == 1 else 1
    
    def calculer_force(self, pos_souris):
        if self.bille_blanche.dans_trou:
            return 0, 0
        
        dx = pos_souris[0] - (self.bille_blanche.x + self.offset_x)
        dy = pos_souris[1] - (self.bille_blanche.y + self.offset_y)
        distance = math.sqrt(dx**2 + dy**2)
        
        # Limiter la force
        if distance > 150:
            distance = 150
        
        force = distance / 150 * self.force_max
        if distance > 0:
            force_x = (dx / distance) * force
            force_y = (dy / distance) * force
        else:
            force_x = force_y = 0
        
        return force_x, force_y
    
    def dessiner_table(self):
        # Fond
        self.ecran.fill(MARRON)
        
        # Table de billard
        table_rect = pygame.Rect(self.offset_x, self.offset_y, 
                               self.largeur_table, self.hauteur_table)
        pygame.draw.rect(self.ecran, VERT_TABLE, table_rect)
        pygame.draw.rect(self.ecran, MARRON, table_rect, 5)
        
        # Bandes
        pygame.draw.rect(self.ecran, MARRON, 
                        (self.offset_x, self.offset_y, self.largeur_table, self.marge))
        pygame.draw.rect(self.ecran, MARRON, 
                        (self.offset_x, self.offset_y + self.hauteur_table - self.marge, 
                         self.largeur_table, self.marge))
        pygame.draw.rect(self.ecran, MARRON, 
                        (self.offset_x, self.offset_y, self.marge, self.hauteur_table))
        pygame.draw.rect(self.ecran, MARRON, 
                        (self.offset_x + self.largeur_table - self.marge, self.offset_y, 
                         self.marge, self.hauteur_table))
    
    def dessiner_visee(self):
        if self.viser and not self.bille_blanche.dans_trou and self.toutes_billes_arretees():
            # Ligne de visée
            pygame.draw.line(self.ecran, BLANC, 
                           (int(self.bille_blanche.x + self.offset_x), 
                            int(self.bille_blanche.y + self.offset_y)), 
                           self.position_souris, 2)
            
            # Indicateur de force
            force_x, force_y = self.calculer_force(self.position_souris)
            force_totale = math.sqrt(force_x**2 + force_y**2)
            force_pourcentage = min(force_totale / self.force_max, 1.0)
            
            # Barre de force
            barre_x = 50
            barre_y = HAUTEUR - 80
            barre_largeur = 200
            barre_hauteur = 20
            
            pygame.draw.rect(self.ecran, NOIR, (barre_x, barre_y, barre_largeur, barre_hauteur))
            couleur_force = ROUGE if force_pourcentage > 0.7 else JAUNE if force_pourcentage > 0.4 else VERT
            pygame.draw.rect(self.ecran, couleur_force, (barre_x, barre_y, 
                           int(barre_largeur * force_pourcentage), barre_hauteur))
            pygame.draw.rect(self.ecran, BLANC, (barre_x, barre_y, barre_largeur, barre_hauteur), 2)
            
            texte_force = self.font_petit.render("Force", True, BLANC)
            self.ecran.blit(texte_force, (barre_x, barre_y - 25))
    
    def dessiner_interface(self):
        # Joueur actuel
        texte_joueur = self.font.render(f"Joueur {self.joueur_actuel}", True, BLANC)
        self.ecran.blit(texte_joueur, (10, 10))
        
        # Groupes assignés
        if self.groupes_assignes:
            billes_j1 = "Pleines (1-7)" if 1 in self.billes_joueur1 else "Rayées (9-15)"
            billes_j2 = "Pleines (1-7)" if 1 in self.billes_joueur2 else "Rayées (9-15)"
            
            texte_j1 = self.font_petit.render(f"Joueur 1: {billes_j1}", True, BLANC)
            texte_j2 = self.font_petit.render(f"Joueur 2: {billes_j2}", True, BLANC)
            
            self.ecran.blit(texte_j1, (10, 50))
            self.ecran.blit(texte_j2, (10, 75))
        
        # Messages temporaires
        if self.temps_message > 0:
            texte_message = self.font.render(self.message, True, JAUNE)
            rect_message = texte_message.get_rect(center=(LARGEUR // 2, 50))
            fond_message = rect_message.inflate(20, 10)
            pygame.draw.rect(self.ecran, NOIR, fond_message, border_radius=5)
            self.ecran.blit(texte_message, rect_message)
            self.temps_message -= 1
        
        # Instructions
        if not self.jeu_termine:
            instructions = [
                "Cliquez et glissez pour viser",
                "Relâchez pour tirer",
                "Empoche tes billes puis la noire (8)"
            ]
            
            for i, instruction in enumerate(instructions):
                texte = self.font_petit.render(instruction, True, BLANC)
                self.ecran.blit(texte, (LARGEUR - 300, 10 + i * 25))
    
    def dessiner_fin_jeu(self):
        if self.jeu_termine:
            # Fond semi-transparent
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(128)
            overlay.fill(NOIR)
            self.ecran.blit(overlay, (0, 0))
            
            # Message de victoire
            texte_fin = self.font.render(f"Joueur {self.gagnant} gagne!", True, JAUNE)
            rect_fin = texte_fin.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 50))
            self.ecran.blit(texte_fin, rect_fin)
            
            # Instructions
            texte_recommencer = self.font_petit.render("Appuyez sur R pour recommencer ou Q pour quitter", True, BLANC)
            rect_recommencer = texte_recommencer.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 50))
            self.ecran.blit(texte_recommencer, rect_recommencer)
    
    def reinitialiser(self):
        self.__init__()
    
    def dessiner(self):
        self.dessiner_table()
        
        # Dessiner les trous
        for trou in self.trous:
            trou.dessiner(self.ecran, self.offset_x, self.offset_y)
        
        # Dessiner les billes
        for bille in self.billes:
            bille.dessiner(self.ecran, self.offset_x, self.offset_y)
        
        # Dessiner la visée
        self.dessiner_visee()
        
        # Interface
        self.dessiner_interface()
        
        # Écran de fin
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
                    if event.button == 1 and self.toutes_billes_arretees() and not self.jeu_termine:
                        self.viser = True
                        self.position_souris = event.pos
                
                elif event.type == pygame.MOUSEMOTION:
                    if self.viser:
                        self.position_souris = event.pos
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.viser and not self.jeu_termine:
                        force_x, force_y = self.calculer_force(event.pos)
                        self.bille_blanche.appliquer_force(force_x, force_y)
                        self.viser = False
                
                elif event.type == pygame.KEYDOWN:
                    if self.jeu_termine:
                        if event.key == pygame.K_r:
                            self.reinitialiser()
                        elif event.key == pygame.K_q:
                            en_cours = False
            
            if not self.jeu_termine:
                # Mettre à jour les billes
                for bille in self.billes:
                    bille.mettre_a_jour()
                    bille.collision_avec_bords(self.largeur_table, self.hauteur_table, self.marge)
                
                # Collisions entre billes
                for i in range(len(self.billes)):
                    for j in range(i + 1, len(self.billes)):
                        self.billes[i].collision_avec_bille(self.billes[j])
                
                # Vérifier les trous
                if self.toutes_billes_arretees():
                    billes_empochees = self.verifier_trous()
                    if billes_empochees:
                        self.verifier_victoire(billes_empochees)
            
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuBillard()
    jeu.executer()