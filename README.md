# Dodoxi - Lanceur de Jeux
![Dodoxi Logo](https://raw.githubusercontent.com/Dodo13500/dodoxy/main/images/default_icon.png)

**Dodoxi** est un lanceur de jeux moderne, élégant et personnalisable, conçu pour organiser et lancer votre collection de jeux développés en Python. Construit avec Python et `ttkbootstrap`, il offre une interface riche en fonctionnalités et une expérience utilisateur fluide.

*(Insérer ici une capture d'écran de l'application)*

## ✨ Fonctionnalités

-   **Bibliothèque Intelligente :**
    -   **Scan Automatique :** Détecte automatiquement les jeux (`.py`) dans le dossier de votre choix.
    -   **Vues Multiples :** Affichez vos jeux en mode **Grille** visuelle ou en **Liste** compacte.
    -   **Recherche et Tri :** Retrouvez facilement vos jeux grâce à la recherche instantanée et aux multiples options de tri (nom, date de lancement, popularité, note).
    -   **Filtres Avancés :** Filtrez votre bibliothèque par favoris, catégories ou collections personnalisées.

-   **Personnalisation Poussée :**
    -   **Thèmes :** Choisissez parmi plus de 15 thèmes prédéfinis ou **créez le vôtre** avec l'éditeur de couleurs intégré.
    -   **Apparence :** Personnalisez le fond d'écran, la taille de la police, et même l'arrondi des angles des boutons.
    -   **Animations :** Profitez de transitions fluides entre les pages.

-   **Suivi et Gamification :**
    -   **Statistiques Détaillées :** Suivez votre temps de jeu total, les jeux les plus joués, et la complétion de votre bibliothèque.
    -   **Système de Succès :** Débloquez des dizaines de succès en explorant les fonctionnalités du lanceur.
    -   **Notation par Étoiles :** Notez vos jeux de 1 à 5 étoiles pour organiser votre collection.

-   **Gestion Facile :**
    -   **Éditeur de Jeux :** Modifiez facilement le nom, la description, l'icône, et les catégories de chaque jeu.
    -   **Mode Portable :** Créez un fichier `portable.txt` à la racine pour que Dodoxi stocke toutes ses données dans un dossier local, idéal pour une clé USB.
    -   **Outils de Maintenance :** Importez, exportez ou sauvegardez votre base de données en quelques clics. Nettoyez les jeux manquants ou les doublons.

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
    Le lanceur gère ses propres dépendances. Au premier lancement, s'il manque `ttkbootstrap` ou `Pillow`, il vous proposera de les installer automatiquement.

4.  **Lancement :**
    Exécutez simplement le script principal :
    ```bash
    python lancer1.py
    ```

## 🎮 Utilisation

1.  **Premier Lancement :** L'application vous demandera de sélectionner le dossier où se trouvent vos jeux Python.
2.  **Scanner :** Appuyez sur **F5** ou utilisez le bouton "Scanner" sur la page "Jeux" pour ajouter de nouveaux jeux à votre bibliothèque.
3.  **Explorer :** Naviguez entre les différentes pages (Accueil, Jeux, Succès, Paramètres) via la barre latérale.
4.  **Personnaliser :** Rendez-vous dans les **Paramètres** pour changer le thème, le fond d'écran et bien plus encore !

##  portability Mode Portable

Pour utiliser Dodoxi sur une clé USB ou sans installation permanente :
1.  Créez un fichier texte vide nommé `portable.txt`.
2.  Placez ce fichier dans le même dossier que `lancer1.py`.
3.  Au prochain lancement, Dodoxi créera un dossier `data` à côté de lui pour y stocker tous les paramètres et bases de données.

## 🤝 Contribution

Les contributions sont les bienvenues ! Si vous avez des idées d'amélioration ou des corrections de bugs, n'hésitez pas à ouvrir une *issue* ou à soumettre une *pull request*.

## 📜 Licence

Ce projet est distribué sous la licence MIT. Voir le fichier `LICENSE` pour plus de détails.

