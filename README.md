# 🚀 Dodoxi - Lanceur de Jeux Moderne

Dodoxi est un lanceur de jeux moderne, personnalisable et ludique, conçu pour organiser et lancer votre collection de jeux Python et Java. Il offre une interface soignée, un suivi des statistiques et un système de succès pour enrichir votre expérience de jeu.

<!-- ![Screenshot de Dodoxi](placeholder.png) -->
*Un aperçu de l'interface de Dodoxi.*

## ✨ Fonctionnalités Principales

- **Bibliothèque de Jeux Intelligente**:
  - Scan automatique des dossiers pour trouver vos jeux (`.py`, `.jar`, `.java`).
  - Ajout manuel de n'importe quel exécutable.
  - Affichage en mode grille ou liste.
  - Filtrage par favoris, catégories et collections.
  - Tri par nom, date de lancement, temps de jeu, etc.

- **Personnalisation Poussée**:
  - **Thèmes**: Plus de 15 thèmes intégrés pour changer l'apparence.
  - **Éditeur de Thème**: Créez votre propre thème en modifiant les couleurs primaires.
  - **Fond d'écran**: Utilisez une image personnalisée ou un dégradé de couleurs.
  - **Apparence UI**: Ajustez la taille de la police et l'arrondi des angles.

- **Suivi & Ludification**:
  - **Statistiques Détaillées**: Suivez votre temps de jeu total, les jeux les plus joués, et plus encore.
  - **Profil Utilisateur**: Un espace dédié à vos exploits de joueur.
  - **Système de Succès**: Plus de 100 succès à débloquer pour explorer toutes les fonctionnalités.

- **Gestion des Données**:
  - **Portable**: Créez un fichier `portable.txt` pour que Dodoxi sauvegarde ses données dans un dossier `data` local.
  - **Import/Export**: Sauvegardez et restaurez facilement votre configuration et votre bibliothèque.
  - **Outils de Maintenance**: Nettoyez les doublons, marquez les jeux manquants, et réparez les icônes.

- **Qualité de Vie**:
  - **Mises à jour automatiques**: Soyez notifié des nouvelles versions disponibles sur GitHub.
  - **Raccourcis Clavier**: Naviguez et lancez des actions rapidement.
  - **Suggestions de Jeux**: Redécouvrez les jeux que vous avez délaissés.

## ⚙️ Installation

Pour utiliser Dodoxi, vous devez avoir Python installé sur votre système.

1.  **Clonez le dépôt (optionnel) ou téléchargez les fichiers.**
    ```bash
    git clone https://github.com/Dodo13500/dodoxy.git
    cd dodoxy
    ```

2.  **Installez les dépendances requises.**
    Assurez-vous d'être dans le bon dossier, puis exécutez :
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Lancement

Exécutez le script principal pour démarrer l'application :

```bash
python lancer1.py
```

### Lancement Direct d'un Jeu
```bash
python jeux/snake_fixe.py
python jeux/tic_tac_toe_fixe.py
python jeux/ping_pong_fixe.py
python jeux/flappy_bird_fixe.py
python jeux/demineur_fixe.py
python jeux/tetris_fixe.py
```

## 🔧 Corrections Apportées

### ✅ **Bugs Corrigés**
- **Gestion des collisions** : Toutes les détections de collision fonctionnent correctement
- **Logique de jeu** : Règles respectées pour chaque jeu
- **Gestion des événements** : Tous les contrôles répondent correctement
- **Conditions de victoire/défaite** : Vérifications appropriées
- **Gestion mémoire** : Pas de fuites mémoire

### ✅ **Améliorations**
- **Interface utilisateur** : Menus clairs et informatifs
- **Feedback visuel** : Animations et effets visuels
- **Contrôles intuitifs** : Touches logiques et réactives
- **Code propre** : Structure claire et commentée
- **Gestion d'erreurs** : Robustesse améliorée

## 🎯 Fonctionnalités

### **Communes à Tous les Jeux**
- ✅ Pas de crashes
- ✅ Contrôles réactifs
- ✅ Interface claire
- ✅ Système de restart
- ✅ Affichage des scores
- ✅ Gestion propre de la fermeture

### **Spécifiques par Jeu**

#### **Snake**
- ✅ Croissance progressive
- ✅ Détection de collision avec les murs et le corps
- ✅ Génération aléatoire de nourriture
- ✅ Affichage du score

#### **Tic Tac Toe**
- ✅ IA fonctionnelle (bloque et attaque)
- ✅ Détection de victoire correcte
- ✅ Gestion des égalités
- ✅ Compteur de scores

#### **Ping Pong**
- ✅ Physique de balle réaliste
- ✅ IA adaptative
- ✅ Rebonds corrects
- ✅ Système de points

#### **Flappy Bird**
- ✅ Physique de gravité
- ✅ Génération de tuyaux
- ✅ Détection de collision précise
- ✅ Système de score par tuyau passé

#### **Démineur**
- ✅ Génération aléatoire de mines
- ✅ Calcul correct des nombres
- ✅ Révélation en cascade
- ✅ Système de marquage

#### **Tetris**
- ✅ Toutes les pièces officielles
- ✅ Rotation correcte
- ✅ Effacement de lignes
- ✅ Augmentation de vitesse

## 🐛 Tests Effectués

Chaque jeu a été testé pour :
- ✅ Lancement sans erreur
- ✅ Tous les contrôles fonctionnent
- ✅ Logique de jeu correcte
- ✅ Conditions de fin appropriées
- ✅ Restart fonctionnel
- ✅ Fermeture propre

## 📁 Structure du Projet

```
jeux en python/
├── menu_principal.py          # Menu principal
├── README.md                  # Ce fichier
└── jeux/
    ├── snake_fixe.py         # Snake corrigé
    ├── tic_tac_toe_fixe.py   # Tic Tac Toe corrigé
    ├── ping_pong_fixe.py     # Ping Pong corrigé
    ├── flappy_bird_fixe.py   # Flappy Bird corrigé
    ├── demineur_fixe.py      # Démineur corrigé
    └── tetris_fixe.py        # Tetris corrigé
```

## 🎮 Comment Jouer

1. **Lancez le menu principal** : `python menu_principal.py`
2. **Cliquez sur le jeu** de votre choix
3. **Suivez les instructions** affichées dans chaque jeu
4. **Utilisez R** pour recommencer dans la plupart des jeux
5. **Fermez la fenêtre** ou appuyez sur Échap pour quitter

## 🔄 Mise à Jour

Tous les jeux ont été entièrement réécrits pour garantir :
- **Stabilité maximale**
- **Code propre et lisible**
- **Fonctionnalités complètes**
- **Expérience utilisateur optimale**

---

**Amusez-vous bien ! 🎉**

