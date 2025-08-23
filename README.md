# Dodoxi - Lanceur de Jeux
![Dodoxi Logo](https://raw.githubusercontent.com/Dodo13500/dodoxy/main/images/default_icon.png)

**Dodoxi** est un lanceur de jeux moderne, élégant et hautement personnalisable, conçu pour organiser et lancer votre collection de jeux développés en Python. Construit avec Python et `ttkbootstrap`, il offre une interface riche en fonctionnalités et une expérience utilisateur fluide.

*(Insérer ici une capture d'écran de l'application)*

## ✨ Fonctionnalités

-   **Bibliothèque Intelligente :**
    -   **Scan Automatique :** Détecte et ajoute automatiquement les jeux (`.py`) dans le dossier de votre choix.
    -   **Vues Multiples :** Affichez vos jeux en mode **Grille** visuelle ou en **Liste** compacte.
    -   **Recherche et Tri Avancés :** Retrouvez facilement vos jeux grâce à la recherche instantanée et aux multiples options de tri (Nom A-Z/Z-A, Plus/Moins joué, Plus/Moins récent, Mieux/Moins bien noté).
    -   **Filtres Puissants :** Filtrez votre bibliothèque par favoris, catégories ou collections personnalisées.
    -   **Dépendances de Jeu :** Spécifiez les modules Python requis par vos jeux ; Dodoxi vous proposera de les installer automatiquement si nécessaire.

-   **Personnalisation Poussée :**
    -   **Thèmes Dynamiques :** Choisissez parmi plus de 15 thèmes prédéfinis ou **créez le vôtre** avec l'éditeur de couleurs intégré.
    -   **Apparence Flexible :** Personnalisez le fond d'écran (image ou dégradé), la taille de la police, l'arrondi des angles des boutons et la visibilité des barres de défilement.
    -   **Animations Fluides :** Profitez de transitions animées entre les pages (glissement ou fondu) et d'effets de révélation pour les nouveaux éléments.
    -   **Sons de Notification :** Activez ou désactivez les retours sonores pour les actions importantes.
    -   **Gestion de Fenêtre :** Démarrez en plein écran et réinitialisez la position/taille de la fenêtre à tout moment.

-   **Suivi et Gamification :**
    -   **Statistiques Détaillées :** Suivez votre temps de jeu total, les jeux les plus joués, les statistiques de votre bibliothèque (descriptions, icônes, jeux manquants) et exportez-les en CSV.
    -   **Système de Succès :** Débloquez des dizaines de succès en explorant les fonctionnalités du lanceur, avec des animations de confettis pour les plus rares !
    -   **Notation par Étoiles :** Notez vos jeux de 1 à 5 étoiles pour organiser et évaluer votre collection.
    -   **Suggestions Intelligentes :** La section "À la une" vous propose des jeux que vous n'avez pas lancés depuis longtemps.

-   **Gestion Avancée :**
    -   **Éditeur de Jeux Complet :** Modifiez facilement le nom, la description, l'icône, les dépendances, les catégories et la note de chaque jeu.
    -   **Gestionnaire de Catégories :** Renommez ou supprimez des catégories existantes.
    -   **Gestionnaire de Collections :** Créez, renommez et supprimez des collections pour regrouper vos jeux.
    -   **Mode Portable :** Créez un fichier `portable.txt` à la racine pour que Dodoxi stocke toutes ses données dans un dossier local, idéal pour une clé USB.
    -   **Outils de Maintenance :** Importez/exportez votre base de données (ZIP), créez des sauvegardes, marquez/supprimez les jeux manquants, et dédupliquez votre bibliothèque.
    -   **Réinitialisation :** Option de réinitialisation complète de l'application ou des seuls succès.

-   **Connectivité :**
    -   **Mises à Jour Automatiques :** Soyez notifié lorsqu'une nouvelle version est disponible sur GitHub.
    -   **Notes de Version en Ligne :** La fenêtre "Nouveautés" charge dynamiquement les dernières informations depuis le dépôt.

## 🚀 Installation

Dodoxi est conçu pour être simple à lancer.

1.  **Prérequis :** Assurez-vous d'avoir Python 3 installé sur votre système.

2.  **Téléchargement :**
    -   Clonez ce dépôt : `git clone https://github.com/Dodo13500/dodoxy.git`
    -   Ou téléchargez le ZIP directement depuis la page Releases.

3.  **Dépendances :**
    Le lanceur gère ses propres dépendances. Au premier lancement, s'il manque `ttkbootstrap`, `Pillow`, `playsound`, `matplotlib` ou `platformdirs`, il vous proposera de les installer automatiquement. Sur Windows, l'installation de `matplotlib` peut nécessiter les "Outils de compilation C++" de Visual Studio.

4.  **Lancement :**
    Exécutez simplement le script principal :
    ```bash
    python lancer1.py
    ```

## 🎮 Utilisation

1.  **Premier Lancement :** L'application vous demandera de sélectionner le dossier principal où se trouvent vos jeux Python.
2.  **Scanner :** Appuyez sur **F5** ou utilisez le bouton "Scanner" sur la page "Jeux" pour ajouter de nouveaux jeux à votre bibliothèque.
3.  **Explorer :** Naviguez entre les différentes pages (Accueil, Jeux, Succès, Paramètres, Aperçu) via la barre latérale.
4.  **Personnaliser :** Rendez-vous dans les **Paramètres** pour changer le thème, le fond d'écran et bien plus encore !
5.  **Raccourcis Clavier :**
    -   `F5` : Scanner les jeux.
    -   `Ctrl+F` : Accéder à la barre de recherche.
    -   `F11` : Activer/désactiver le mode plein écran.
    -   `Ctrl+R` : Lancer un jeu aléatoire.

## 📦 Mode Portable

Pour utiliser Dodoxi sur une clé USB ou sans installation permanente :
1.  Créez un fichier texte vide nommé `portable.txt`.
2.  Placez ce fichier dans le même dossier que `lancer1.py`.
3.  Au prochain lancement, Dodoxi créera un dossier `data` à côté de lui pour y stocker tous les paramètres et bases de données.

## 🤝 Contribution

Les contributions sont les bienvenues ! Si vous avez des idées d'amélioration ou des corrections de bugs, n'hésitez pas à ouvrir une *issue* ou à soumettre une *pull request* sur notre dépôt GitHub.

## 📜 Licence

Ce projet est distribué sous la licence MIT. Voir le fichier `LICENSE` pour plus de détails.
