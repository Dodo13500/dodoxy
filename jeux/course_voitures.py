import pygame
import math
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
ROUGE = (255, 0, 0)
BLEU = (0, 0, 255)
VERT = (0, 255, 0)
JAUNE = (255, 255, 0)
GRIS = (128, 128, 128)
GRIS_FONCE = (64, 64, 64)
ORANGE = (255, 165, 0)
VIOLET = (128, 0, 128)

class Voiture:
    def __init__(self, x, y, couleur, nom, est_joueur=False):
        self.x = x
        self.y = y
        self.angle = 0
        self.vitesse = 0
        self.vitesse_max = 8
        self.acceleration = 0.3
        self.deceleration = 0.2
        self.vitesse_rotation = 4
        self.couleur = couleur
        self.nom = nom
        self.est_joueur = est_joueur
        
        # Dimensions de la voiture
        self.largeur = 30
        self.hauteur = 15
        
        # État
        self.sur_piste = True
        self.temps_tour = 0
        self.meilleur_temps = float('inf')
        self.tours_completes = 0
        self.checkpoint_actuel = 0
        self.position_course = 1
        
        # IA
        self.cible_x = x
        self.cible_y = y
        self.vitesse_ia = random.uniform(0.7, 1.0)  # Variabilité de l'IA
    
    def mettre_a_jour(self, touches_pressees=None):
        if self.est_joueur and touches_pressees:
            self.controles_joueur(touches_pressees)
        else:
            self.ia_conduite()
        
        # Appliquer la vitesse
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.vitesse
        self.y += math.sin(rad) * self.vitesse
        
        # Friction
        if self.vitesse > 0:
            self.vitesse = max(0, self.vitesse - 0.1)
        elif self.vitesse < 0:
            self.vitesse = min(0, self.vitesse + 0.1)
    
    def controles_joueur(self, touches):
        # Accélération
        if touches[pygame.K_UP]:
            self.vitesse = min(self.vitesse_max, self.vitesse + self.acceleration)
        elif touches[pygame.K_DOWN]:
            self.vitesse = max(-self.vitesse_max/2, self.vitesse - self.acceleration)
        
        # Direction (seulement si la voiture bouge)
        if abs(self.vitesse) > 0.5:
            if touches[pygame.K_LEFT]:
                self.angle -= self.vitesse_rotation * (abs(self.vitesse) / self.vitesse_max)
            elif touches[pygame.K_RIGHT]:
                self.angle += self.vitesse_rotation * (abs(self.vitesse) / self.vitesse_max)
    
    def ia_conduite(self):
        # IA simple qui suit les checkpoints
        dx = self.cible_x - self.x
        dy = self.cible_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 5:
            # Calculer l'angle vers la cible
            angle_cible = math.degrees(math.atan2(dy, dx))
            
            # Différence d'angle
            diff_angle = angle_cible - self.angle
            while diff_angle > 180:
                diff_angle -= 360
            while diff_angle < -180:
                diff_angle += 360
            
            # Tourner vers la cible
            if abs(diff_angle) > 5:
                if diff_angle > 0:
                    self.angle += self.vitesse_rotation * 0.8
                else:
                    self.angle -= self.vitesse_rotation * 0.8
            
            # Accélérer
            vitesse_cible = self.vitesse_max * self.vitesse_ia
            if abs(diff_angle) > 45:  # Ralentir dans les virages
                vitesse_cible *= 0.6
            
            if self.vitesse < vitesse_cible:
                self.vitesse = min(vitesse_cible, self.vitesse + self.acceleration)
            else:
                self.vitesse = max(vitesse_cible, self.vitesse - self.deceleration)
    
    def dessiner(self, surface):
        # Calculer les coins de la voiture
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        # Points de la voiture (rectangle)
        points = [
            (-self.largeur//2, -self.hauteur//2),
            (self.largeur//2, -self.hauteur//2),
            (self.largeur//2, self.hauteur//2),
            (-self.largeur//2, self.hauteur//2)
        ]
        
        # Rotation et translation
        points_rotates = []
        for px, py in points:
            x_rot = px * cos_a - py * sin_a + self.x
            y_rot = px * sin_a + py * cos_a + self.y
            points_rotates.append((x_rot, y_rot))
        
        # Dessiner la voiture
        pygame.draw.polygon(surface, self.couleur, points_rotates)
        pygame.draw.polygon(surface, NOIR, points_rotates, 2)
        
        # Dessiner la direction (petit triangle à l'avant)
        avant_x = self.x + cos_a * self.largeur//2
        avant_y = self.y + sin_a * self.largeur//2
        pygame.draw.circle(surface, BLANC, (int(avant_x), int(avant_y)), 3)

class Circuit:
    def __init__(self):
        # Points de contrôle du circuit (piste ovale avec virages)
        self.checkpoints = [
            (200, 400), (300, 200), (500, 150), (700, 200), (900, 300),
            (1000, 400), (950, 600), (800, 650), (600, 650), (400, 600),
            (250, 500)
        ]
        
        # Largeur de la piste
        self.largeur_piste = 80
        
        # Générer les bords de la piste
        self.bord_interieur = []
        self.bord_exterieur = []
        self.generer_bords()
    
    def generer_bords(self):
        for i in range(len(self.checkpoints)):
            x, y = self.checkpoints[i]
            
            # Point suivant (boucle)
            next_i = (i + 1) % len(self.checkpoints)
            next_x, next_y = self.checkpoints[next_i]
            
            # Vecteur direction
            dx = next_x - x
            dy = next_y - y
            length = math.sqrt(dx**2 + dy**2)
            
            if length > 0:
                # Vecteur perpendiculaire (normal)
                norm_x = -dy / length
                norm_y = dx / length
                
                # Points des bords
                bord_int_x = x + norm_x * (self.largeur_piste // 2)
                bord_int_y = y + norm_y * (self.largeur_piste // 2)
                bord_ext_x = x - norm_x * (self.largeur_piste // 2)
                bord_ext_y = y - norm_y * (self.largeur_piste // 2)
                
                self.bord_interieur.append((bord_int_x, bord_int_y))
                self.bord_exterieur.append((bord_ext_x, bord_ext_y))
    
    def dessiner(self, surface):
        # Dessiner l'herbe (fond)
        surface.fill(VERT)
        
        # Dessiner la piste (polygone entre les bords)
        if len(self.bord_exterieur) > 2 and len(self.bord_interieur) > 2:
            # Piste complète
            tous_points = self.bord_exterieur + list(reversed(self.bord_interieur))
            pygame.draw.polygon(surface, GRIS, tous_points)
            
            # Bords de la piste
            pygame.draw.polygon(surface, BLANC, self.bord_exterieur, 3)
            pygame.draw.polygon(surface, BLANC, self.bord_interieur, 3)
        
        # Ligne de départ/arrivée
        if len(self.checkpoints) > 0:
            start_x, start_y = self.checkpoints[0]
            # Ligne perpendiculaire à la direction
            if len(self.checkpoints) > 1:
                next_x, next_y = self.checkpoints[1]
                dx = next_x - start_x
                dy = next_y - start_y
                length = math.sqrt(dx**2 + dy**2)
                
                if length > 0:
                    norm_x = -dy / length
                    norm_y = dx / length
                    
                    ligne_start = (start_x - norm_x * self.largeur_piste//2,
                                 start_y - norm_y * self.largeur_piste//2)
                    ligne_end = (start_x + norm_x * self.largeur_piste//2,
                               start_y + norm_y * self.largeur_piste//2)
                    
                    # Damier de départ
                    for i in range(8):
                        couleur = BLANC if i % 2 == 0 else NOIR
                        segment_x = ligne_start[0] + (ligne_end[0] - ligne_start[0]) * i / 8
                        segment_y = ligne_start[1] + (ligne_end[1] - ligne_start[1]) * i / 8
                        next_segment_x = ligne_start[0] + (ligne_end[0] - ligne_start[0]) * (i+1) / 8
                        next_segment_y = ligne_start[1] + (ligne_end[1] - ligne_start[1]) * (i+1) / 8
                        
                        pygame.draw.line(surface, couleur, 
                                       (segment_x, segment_y), 
                                       (next_segment_x, next_segment_y), 5)
        
        # Dessiner les checkpoints (pour debug)
        for i, (x, y) in enumerate(self.checkpoints):
            pygame.draw.circle(surface, ROUGE if i == 0 else JAUNE, (int(x), int(y)), 5)
    
    def point_sur_piste(self, x, y):
        # Vérification simple si un point est sur la piste
        # (Cette fonction pourrait être améliorée avec une détection plus précise)
        for checkpoint in self.checkpoints:
            dist = math.sqrt((x - checkpoint[0])**2 + (y - checkpoint[1])**2)
            if dist < self.largeur_piste:
                return True
        return False

class JeuCourse:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Course de Voitures")
        self.horloge = pygame.time.Clock()
        
        # Créer le circuit
        self.circuit = Circuit()
        
        # Créer les voitures
        start_x, start_y = self.circuit.checkpoints[0]
        self.voitures = [
            Voiture(start_x - 20, start_y, ROUGE, "Joueur", True),
            Voiture(start_x, start_y + 20, BLEU, "IA 1", False),
            Voiture(start_x + 20, start_y, VERT, "IA 2", False),
            Voiture(start_x, start_y - 20, JAUNE, "IA 3", False),
            Voiture(start_x - 20, start_y - 20, ORANGE, "IA 4", False),
            Voiture(start_x + 20, start_y + 20, VIOLET, "IA 5", False)
        ]
        
        # Assigner les cibles initiales aux IA
        for voiture in self.voitures:
            if not voiture.est_joueur:
                voiture.cible_x, voiture.cible_y = self.circuit.checkpoints[1]
        
        # État de la course
        self.course_commencee = False
        self.temps_course = 0
        self.compte_rebours = 3
        self.temps_compte_rebours = 0
        
        # Interface
        self.font = pygame.font.Font(None, 48)
        self.font_petit = pygame.font.Font(None, 32)
        self.font_grand = pygame.font.Font(None, 72)
        
        # Caméra (suit le joueur)
        self.camera_x = 0
        self.camera_y = 0
        
        # Fin de course
        self.course_terminee = False
        self.classement = []
    
    def mettre_a_jour_camera(self):
        # Suivre le joueur
        joueur = self.voitures[0]
        self.camera_x = joueur.x - LARGEUR // 2
        self.camera_y = joueur.y - HAUTEUR // 2
    
    def mettre_a_jour_checkpoints(self):
        for voiture in self.voitures:
            if not voiture.est_joueur:
                # Mettre à jour la cible de l'IA
                checkpoint_actuel = voiture.checkpoint_actuel
                cible_x, cible_y = self.circuit.checkpoints[checkpoint_actuel]
                
                # Vérifier si l'IA a atteint le checkpoint
                dist = math.sqrt((voiture.x - cible_x)**2 + (voiture.y - cible_y)**2)
                if dist < 50:
                    voiture.checkpoint_actuel = (voiture.checkpoint_actuel + 1) % len(self.circuit.checkpoints)
                    if voiture.checkpoint_actuel == 0:
                        voiture.tours_completes += 1
                    
                    # Nouvelle cible
                    voiture.cible_x, voiture.cible_y = self.circuit.checkpoints[voiture.checkpoint_actuel]
            
            else:
                # Joueur - vérifier les checkpoints
                checkpoint_actuel = voiture.checkpoint_actuel
                cible_x, cible_y = self.circuit.checkpoints[checkpoint_actuel]
                
                dist = math.sqrt((voiture.x - cible_x)**2 + (voiture.y - cible_y)**2)
                if dist < 50:
                    voiture.checkpoint_actuel = (voiture.checkpoint_actuel + 1) % len(self.circuit.checkpoints)
                    if voiture.checkpoint_actuel == 0:
                        voiture.tours_completes += 1
                        if voiture.tours_completes >= 3:  # 3 tours pour gagner
                            if voiture not in self.classement:
                                self.classement.append(voiture)
                                if len(self.classement) == 1:
                                    self.course_terminee = True
    
    def calculer_positions(self):
        # Calculer la position de chaque voiture dans la course
        voitures_triees = sorted(self.voitures, 
                               key=lambda v: (v.tours_completes, v.checkpoint_actuel), 
                               reverse=True)
        
        for i, voiture in enumerate(voitures_triees):
            voiture.position_course = i + 1
    
    def dessiner_interface(self):
        # Compte à rebours
        if not self.course_commencee:
            if self.compte_rebours > 0:
                texte_compte = self.font_grand.render(str(self.compte_rebours), True, ROUGE)
                rect_compte = texte_compte.get_rect(center=(LARGEUR//2, HAUTEUR//2))
                
                # Fond semi-transparent
                fond = pygame.Surface((100, 100))
                fond.set_alpha(128)
                fond.fill(BLANC)
                fond_rect = fond.get_rect(center=(LARGEUR//2, HAUTEUR//2))
                self.ecran.blit(fond, fond_rect)
                
                self.ecran.blit(texte_compte, rect_compte)
            else:
                texte_go = self.font_grand.render("GO!", True, VERT)
                rect_go = texte_go.get_rect(center=(LARGEUR//2, HAUTEUR//2))
                self.ecran.blit(texte_go, rect_go)
        
        # Informations de course
        joueur = self.voitures[0]
        
        # Position
        texte_position = self.font.render(f"Position: {joueur.position_course}/6", True, BLANC)
        self.ecran.blit(texte_position, (10, 10))
        
        # Tours
        texte_tours = self.font.render(f"Tours: {joueur.tours_completes}/3", True, BLANC)
        self.ecran.blit(texte_tours, (10, 60))
        
        # Vitesse
        vitesse_kmh = int(abs(joueur.vitesse) * 10)
        texte_vitesse = self.font.render(f"Vitesse: {vitesse_kmh} km/h", True, BLANC)
        self.ecran.blit(texte_vitesse, (10, 110))
        
        # Temps
        if self.course_commencee:
            minutes = int(self.temps_course // 3600)
            secondes = int((self.temps_course % 3600) // 60)
            centimes = int((self.temps_course % 60) * 100 / 60)
            texte_temps = self.font.render(f"Temps: {minutes:02d}:{secondes:02d}.{centimes:02d}", True, BLANC)
            self.ecran.blit(texte_temps, (10, 160))
        
        # Mini-classement
        y_classement = HAUTEUR - 200
        texte_titre = self.font_petit.render("Classement:", True, BLANC)
        self.ecran.blit(texte_titre, (LARGEUR - 200, y_classement))
        
        voitures_triees = sorted(self.voitures, 
                               key=lambda v: (v.tours_completes, v.checkpoint_actuel), 
                               reverse=True)
        
        for i, voiture in enumerate(voitures_triees[:6]):
            couleur_texte = JAUNE if voiture.est_joueur else BLANC
            texte_pos = self.font_petit.render(f"{i+1}. {voiture.nom}", True, couleur_texte)
            self.ecran.blit(texte_pos, (LARGEUR - 200, y_classement + 30 + i * 25))
        
        # Contrôles
        if not self.course_commencee and self.compte_rebours <= 0:
            instructions = [
                "Flèches: Diriger",
                "↑: Accélérer",
                "↓: Freiner"
            ]
            
            for i, instruction in enumerate(instructions):
                texte = self.font_petit.render(instruction, True, BLANC)
                self.ecran.blit(texte, (LARGEUR - 200, 10 + i * 30))
    
    def dessiner_fin_course(self):
        if self.course_terminee:
            # Fond semi-transparent
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(200)
            overlay.fill(NOIR)
            self.ecran.blit(overlay, (0, 0))
            
            # Message de victoire/défaite
            joueur = self.voitures[0]
            if joueur.position_course == 1:
                texte_fin = self.font_grand.render("VICTOIRE!", True, JAUNE)
                couleur_fond = VERT
            else:
                texte_fin = self.font_grand.render(f"Terminé {joueur.position_course}e", True, BLANC)
                couleur_fond = ROUGE
            
            rect_fin = texte_fin.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 100))
            
            # Fond coloré
            fond_rect = rect_fin.inflate(50, 30)
            pygame.draw.rect(self.ecran, couleur_fond, fond_rect, border_radius=10)
            pygame.draw.rect(self.ecran, BLANC, fond_rect, width=3, border_radius=10)
            
            self.ecran.blit(texte_fin, rect_fin)
            
            # Temps final
            minutes = int(self.temps_course // 3600)
            secondes = int((self.temps_course % 3600) // 60)
            centimes = int((self.temps_course % 60) * 100 / 60)
            texte_temps = self.font.render(f"Temps: {minutes:02d}:{secondes:02d}.{centimes:02d}", True, BLANC)
            rect_temps = texte_temps.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 50))
            self.ecran.blit(texte_temps, rect_temps)
            
            # Instructions
            texte_recommencer = self.font_petit.render("Appuyez sur R pour recommencer ou Q pour quitter", True, BLANC)
            rect_recommencer = texte_recommencer.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 50))
            self.ecran.blit(texte_recommencer, rect_recommencer)
    
    def reinitialiser(self):
        self.__init__()
    
    def dessiner(self):
        # Mettre à jour la caméra
        self.mettre_a_jour_camera()
        
        # Dessiner le circuit (avec offset de caméra)
        surface_circuit = pygame.Surface((LARGEUR, HAUTEUR))
        self.circuit.dessiner(surface_circuit)
        
        # Appliquer l'offset de caméra
        self.ecran.blit(surface_circuit, (-self.camera_x, -self.camera_y))
        
        # Dessiner les voitures (avec offset de caméra)
        for voiture in self.voitures:
            voiture_surface = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
            voiture.dessiner(voiture_surface)
            self.ecran.blit(voiture_surface, (-self.camera_x, -self.camera_y))
        
        # Interface (pas d'offset)
        self.dessiner_interface()
        
        # Écran de fin
        if self.course_terminee:
            self.dessiner_fin_course()
        
        pygame.display.flip()
    
    def executer(self):
        en_cours = True
        
        while en_cours:
            touches = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                elif event.type == pygame.KEYDOWN:
                    if self.course_terminee:
                        if event.key == pygame.K_r:
                            self.reinitialiser()
                        elif event.key == pygame.K_q:
                            en_cours = False
            
            # Gestion du compte à rebours
            if not self.course_commencee:
                self.temps_compte_rebours += 1
                if self.temps_compte_rebours >= 60:  # 1 seconde
                    self.temps_compte_rebours = 0
                    self.compte_rebours -= 1
                    if self.compte_rebours < 0:
                        self.course_commencee = True
            
            # Mettre à jour le jeu
            if self.course_commencee and not self.course_terminee:
                self.temps_course += 1
                
                # Mettre à jour les voitures
                for voiture in self.voitures:
                    voiture.mettre_a_jour(touches if voiture.est_joueur else None)
                
                # Mettre à jour les checkpoints
                self.mettre_a_jour_checkpoints()
                
                # Calculer les positions
                self.calculer_positions()
            
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jeu = JeuCourse()
    jeu.executer()