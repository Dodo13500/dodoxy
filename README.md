# Dodoxi - Lanceur de Jeux

 <!-- Remplacez par une vraie capture d'écran -->

**Dodoxi** est un lanceur de jeux moderne, personnalisable et open-source, écrit en Python avec Tkinter et ttkbootstrap. Il est conçu pour organiser, lancer et suivre vos jeux Python de manière élégante et efficace.

## ✨ Fonctionnalités

- **Bibliothèque de jeux** : Scanne automatiquement votre dossier de jeux et les affiche dans une vue grille ou liste.
- **Personnalisation** :
    - Choisissez parmi plus de 15 thèmes prédéfinis.
    - Créez votre propre thème avec l'éditeur de couleurs intégré.
    - Personnalisez le fond d'écran avec une image ou un dégradé.
- **Organisation** :
    - **Favoris** : Marquez vos jeux préférés pour un accès rapide.
    - **Notation** : Notez vos jeux de 1 à 5 étoiles.
    - **Collections** : Créez des collections personnalisées pour regrouper vos jeux (par genre, par série, etc.).
    - **Catégories** : Taguez vos jeux avec des catégories pour un filtrage avancé.
- **Suivi et Statistiques** :
    - Temps de jeu total et par jeu.
    - Nombre de lancements.
    - Suivi détaillé des sessions de jeu (date, durée).
    - Graphiques visuels pour le temps de jeu et la répartition par catégorie.
    - Exportation des statistiques au format CSV.
- **Système de Succès** : Débloquez des dizaines de succès en utilisant les différentes fonctionnalités du lanceur.
- **Mode Portable** : Créez un fichier `portable.txt` à la racine pour que Dodoxi sauvegarde ses données dans un dossier `data` local, idéal pour une utilisation sur clé USB.
- **Maintenance Facile** : Outils intégrés pour nettoyer la bibliothèque, supprimer les doublons, et gérer les données.

## 🚀 Installation

### Prérequis
- Python 3.8 ou plus récent
- `pip` et `git`

### 1. Cloner le dépôt

```bash
git clone https://github.com/Dodo13500/dodoxy.git
cd dodoxy
```

### 2. Installer les dépendances

Dodoxi utilise plusieurs bibliothèques Python. Vous pouvez les installer facilement avec le fichier `requirements.txt` fourni :

```bash
pip install -r requirements.txt
```

Si vous n'avez pas les "Outils de compilation C++" de Visual Studio sur Windows, l'installation de `matplotlib` peut échouer. Dans ce cas, l'application vous proposera de les installer au premier lancement.

## 🎮 Utilisation

Pour lancer l'application, exécutez le script principal :

```bash
python lancer1.py
```

Au premier lancement, l'application vous demandera de sélectionner le dossier où se trouvent vos jeux.

### Mode Portable

Pour utiliser Dodoxi en mode portable (par exemple, depuis une clé USB), il suffit de créer un fichier vide nommé `portable.txt` dans le même dossier que `lancer1.py`.

Lorsque ce fichier est présent, toutes les données (paramètres, base de données des jeux, etc.) seront stockées dans un sous-dossier `data`, au lieu du dossier utilisateur standard.

## 🔧 Raccourcis Clavier

- **F5** : Scanner le dossier des jeux.
- **Ctrl+F** : Mettre le focus sur la barre de recherche.
- **F11** : Activer/Désactiver le mode plein écran.
- **Ctrl+R** : Lancer un jeu au hasard.

## 🤝 Contribution

Les contributions sont les bienvenues ! Si vous souhaitez améliorer Dodoxi, n'hésitez pas à forker le projet et à soumettre une Pull Request.

1. Forkez le projet.
2. Créez votre branche de fonctionnalité (`git checkout -b feature/NouvelleFonctionnalite`).
3. Committez vos changements (`git commit -m 'Ajout de NouvelleFonctionnalite'`).
4. Pushez vers la branche (`git push origin feature/NouvelleFonctionnalite`).
5. Ouvrez une Pull Request.

## 📄 Licence

Ce projet est distribué sous la licence MIT. Voir le fichier `LICENSE` pour plus d'informations.

