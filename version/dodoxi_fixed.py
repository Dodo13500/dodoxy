# -*- coding: utf-8 -*-
# Dodoxi - Lanceur de Jeux Corrigé et Stabilisé
# Version corrigée des bugs principaux

import os
import sys
import json
import datetime
import random
import subprocess
import traceback
import time
import tkinter as tk
import threading
from tkinter import messagebox, filedialog, simpledialog

# Vérification et installation des dépendances
missing_deps = []
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from ttkbootstrap.scrolled import ScrolledFrame
    from ttkbootstrap.tooltip import ToolTip
    from ttkbootstrap.widgets import Meter
except ImportError:
    missing_deps.append("ttkbootstrap")

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
except ImportError:
    missing_deps.append("Pillow")

if missing_deps:
    root = tk.Tk()
    root.withdraw()
    if messagebox.askyesno("Dépendances manquantes", 
                          f"Installer {', '.join(missing_deps)} ?"):
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_deps)
        messagebox.showinfo("Installation", "Redémarrez l'application")
    sys.exit()

# --- Constants ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FOLDER = os.path.join(SCRIPT_DIR, "settings")
GAMES_FOLDER = os.path.join(SCRIPT_DIR, "jeux")
IMAGES_FOLDER = os.path.join(SCRIPT_DIR, "images")

# Créer les dossiers nécessaires
for folder in [SETTINGS_FOLDER, IMAGES_FOLDER]:
    os.makedirs(folder, exist_ok=True)

SETTINGS_FILE = os.path.join(SETTINGS_FOLDER, "settings.json")
GAMES_FILE = os.path.join(SETTINGS_FOLDER, "games.json")
ACHIEVEMENTS_FILE = os.path.join(SETTINGS_FOLDER, "achievements.json")
CRASH_LOG_FILE = os.path.join(SETTINGS_FOLDER, "crash_log.txt")

VERSION = "v0.17.0-Fixed"
APP_NAME = "Dodoxi - Corrigé"

THEMES = ["darkly", "solar", "cyborg", "superhero", "lumen", "cosmo", "flatly"]

def log_crash(message: str, exception: Exception = None):
    """Log des erreurs dans un fichier"""
    try:
        with open(CRASH_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] {message}\n")
            if exception:
                f.write(f"Erreur: {exception}\n")
                f.write(traceback.format_exc())
            f.write("-" * 50 + "\n")
    except:
        print(f"Erreur de log: {message}")

class DodoxiFixed(ttk.Window):
    def __init__(self):
        # Charger le thème avant l'initialisation
        theme = self.load_theme()
        super().__init__(themename=theme, title=APP_NAME)
        
        # Initialisation des attributs AVANT leur utilisation
        self.pages_dirty = {"main": True, "games": True, "achievements": True}
        self.games = []
        self.settings = {}
        self.achievements_data = {}
        self.current_page = "main"
        self.game_widgets = {}
        
        # Style personnalisé (éviter le conflit avec self.style)
        self.app_style = ttk.Style()
        
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Chargement des données
        self.load_all_data()
        
        # Interface
        self.create_interface()
        
        # Scan initial
        self.after(1000, self.initial_scan)
        
    def load_theme(self):
        """Charge le thème depuis les paramètres"""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return settings.get("theme", "darkly")
        except:
            pass
        return "darkly"
    
    def load_all_data(self):
        """Charge toutes les données nécessaires"""
        self.settings = self.load_settings()
        self.games = self.load_games()
        self.achievements_data = self.load_achievements()
    
    def load_settings(self):
        """Charge les paramètres"""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            log_crash("Erreur chargement settings", e)
        return {"theme": "darkly", "username": "Joueur"}
    
    def load_games(self):
        """Charge la liste des jeux"""
        try:
            if os.path.exists(GAMES_FILE):
                with open(GAMES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            log_crash("Erreur chargement games", e)
        return []
    
    def load_achievements(self):
        """Charge les succès"""
        default_achievements = {
            "first_launch": {
                "name": "Premier Lancement",
                "desc": "Lancer l'application pour la première fois",
                "unlocked": False,
                "icon": "🚀"
            },
            "first_game": {
                "name": "Premier Jeu",
                "desc": "Lancer votre premier jeu",
                "unlocked": False,
                "icon": "🎮"
            },
            "theme_changer": {
                "name": "Changeur de Thème",
                "desc": "Changer le thème de l'application",
                "unlocked": False,
                "icon": "🎨"
            }
        }
        
        try:
            if os.path.exists(ACHIEVEMENTS_FILE):
                with open(ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Fusionner avec les succès par défaut
                    for key, value in default_achievements.items():
                        if key not in data:
                            data[key] = value
                    return data
        except Exception as e:
            log_crash("Erreur chargement achievements", e)
        
        return default_achievements
    
    def save_games(self):
        """Sauvegarde la liste des jeux"""
        try:
            with open(GAMES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.games, f, indent=2, ensure_ascii=False)
            self.mark_dirty(["games", "main"])
        except Exception as e:
            log_crash("Erreur sauvegarde games", e)
    
    def save_settings(self):
        """Sauvegarde les paramètres"""
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_crash("Erreur sauvegarde settings", e)
    
    def save_achievements(self):
        """Sauvegarde les succès"""
        try:
            with open(ACHIEVEMENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.achievements_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_crash("Erreur sauvegarde achievements", e)
    
    def mark_dirty(self, pages):
        """Marque les pages comme nécessitant une mise à jour"""
        for page in pages:
            if page in self.pages_dirty:
                self.pages_dirty[page] = True
    
    def create_interface(self):
        """Crée l'interface principale"""
        # Configuration de la grille
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.create_sidebar()
        
        # Zone de contenu
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Pages
        self.create_pages()
        
        # Afficher la page principale
        self.show_page("main")
        
        # Débloquer le succès du premier lancement
        self.unlock_achievement("first_launch")
    
    def create_sidebar(self):
        """Crée la barre latérale"""
        sidebar = ttk.Frame(self, style="Card.TFrame")
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # Logo/Titre
        title_label = ttk.Label(sidebar, text=APP_NAME, font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Boutons de navigation
        self.nav_buttons = {}
        
        pages = [
            ("main", "🏠 Accueil"),
            ("games", "🎮 Jeux"),
            ("achievements", "🏆 Succès"),
            ("settings", "⚙️ Paramètres")
        ]
        
        for page_id, text in pages:
            btn = ttk.Button(sidebar, text=text, 
                           command=lambda p=page_id: self.show_page(p),
                           style="Outline.TButton")
            btn.pack(fill="x", padx=10, pady=5)
            self.nav_buttons[page_id] = btn
        
        # Informations utilisateur
        user_frame = ttk.LabelFrame(sidebar, text="Profil", padding=10)
        user_frame.pack(fill="x", padx=10, pady=20)
        
        username = self.settings.get("username", "Joueur")
        ttk.Label(user_frame, text=f"👤 {username}").pack()
        ttk.Label(user_frame, text=f"🎮 {len(self.games)} jeux").pack()
        
        unlocked_count = sum(1 for ach in self.achievements_data.values() if ach.get("unlocked", False))
        total_count = len(self.achievements_data)
        ttk.Label(user_frame, text=f"🏆 {unlocked_count}/{total_count}").pack()
    
    def create_pages(self):
        """Crée toutes les pages"""
        self.pages = {}
        
        # Page principale
        self.pages["main"] = self.create_main_page()
        
        # Page des jeux
        self.pages["games"] = self.create_games_page()
        
        # Page des succès
        self.pages["achievements"] = self.create_achievements_page()
        
        # Page des paramètres
        self.pages["settings"] = self.create_settings_page()
    
    def create_main_page(self):
        """Crée la page d'accueil"""
        frame = ttk.Frame(self.content_frame)
        
        # Titre de bienvenue
        welcome_label = ttk.Label(frame, text=f"Bienvenue, {self.settings.get('username', 'Joueur')} !",
                                font=("Arial", 24, "bold"))
        welcome_label.pack(pady=20)
        
        # Statistiques rapides
        stats_frame = ttk.LabelFrame(frame, text="📊 Statistiques", padding=20)
        stats_frame.pack(fill="x", pady=10)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack()
        
        # Nombre de jeux
        games_count = len([g for g in self.games if not g.get("deleted", False)])
        ttk.Label(stats_grid, text="🎮 Jeux", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=20)
        ttk.Label(stats_grid, text=str(games_count), font=("Arial", 20)).grid(row=1, column=0, padx=20)
        
        # Succès débloqués
        unlocked = sum(1 for ach in self.achievements_data.values() if ach.get("unlocked", False))
        total = len(self.achievements_data)
        ttk.Label(stats_grid, text="🏆 Succès", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=20)
        ttk.Label(stats_grid, text=f"{unlocked}/{total}", font=("Arial", 20)).grid(row=1, column=1, padx=20)
        
        # Lancements totaux
        total_launches = sum(g.get("launches", 0) for g in self.games)
        ttk.Label(stats_grid, text="🚀 Lancements", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=20)
        ttk.Label(stats_grid, text=str(total_launches), font=("Arial", 20)).grid(row=1, column=2, padx=20)
        
        # Actions rapides
        actions_frame = ttk.LabelFrame(frame, text="⚡ Actions Rapides", padding=20)
        actions_frame.pack(fill="x", pady=10)
        
        actions_grid = ttk.Frame(actions_frame)
        actions_grid.pack()
        
        ttk.Button(actions_grid, text="🔍 Scanner Jeux", 
                  command=self.scan_games).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(actions_grid, text="➕ Ajouter Jeu", 
                  command=self.add_game_manual).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(actions_grid, text="🎲 Jeu Aléatoire", 
                  command=self.launch_random_game).grid(row=0, column=2, padx=10, pady=5)
        
        # Jeu suggéré
        if self.games:
            suggestion_frame = ttk.LabelFrame(frame, text="💡 Suggestion", padding=20)
            suggestion_frame.pack(fill="x", pady=10)
            
            # Choisir un jeu peu joué
            least_played = min(self.games, key=lambda g: g.get("launches", 0))
            ttk.Label(suggestion_frame, text=f"Que diriez-vous de jouer à '{least_played.get('name', 'Jeu')}'?",
                     font=("Arial", 12)).pack()
            ttk.Button(suggestion_frame, text="🚀 Lancer", 
                      command=lambda: self.launch_game(least_played)).pack(pady=10)
        
        return frame
    
    def create_games_page(self):
        """Crée la page des jeux"""
        frame = ttk.Frame(self.content_frame)
        
        # Titre et barre d'outils
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(header_frame, text="🎮 Ma Bibliothèque", 
                 font=("Arial", 20, "bold")).pack(side="left")
        
        # Boutons d'action
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side="right")
        
        ttk.Button(btn_frame, text="🔍 Scanner", 
                  command=self.scan_games).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="➕ Ajouter", 
                  command=self.add_game_manual).pack(side="left", padx=5)
        
        # Zone de recherche
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Recherche:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_games)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Liste des jeux avec scrollbar
        self.games_scrolled = ScrolledFrame(frame)
        self.games_scrolled.pack(fill="both", expand=True)
        
        self.games_container = self.games_scrolled
        
        self.refresh_games_list()
        
        return frame
    
    def create_achievements_page(self):
        """Crée la page des succès"""
        frame = ttk.Frame(self.content_frame)
        
        # Titre
        ttk.Label(frame, text="🏆 Succès", font=("Arial", 20, "bold")).pack(pady=(0, 20))
        
        # Progression globale
        unlocked = sum(1 for ach in self.achievements_data.values() if ach.get("unlocked", False))
        total = len(self.achievements_data)
        progress = (unlocked / total * 100) if total > 0 else 0
        
        progress_frame = ttk.LabelFrame(frame, text="Progression", padding=10)
        progress_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(progress_frame, text=f"{unlocked}/{total} succès débloqués ({progress:.1f}%)",
                 font=("Arial", 12)).pack()
        
        progress_bar = ttk.Progressbar(progress_frame, value=progress, length=400)
        progress_bar.pack(pady=10)
        
        # Liste des succès
        achievements_scrolled = ScrolledFrame(frame)
        achievements_scrolled.pack(fill="both", expand=True)
        
        for ach_id, ach_data in self.achievements_data.items():
            self.create_achievement_card(achievements_scrolled, ach_id, ach_data)
        
        return frame
    
    def create_achievement_card(self, parent, ach_id, ach_data):
        """Crée une carte de succès"""
        is_unlocked = ach_data.get("unlocked", False)
        
        card_frame = ttk.Frame(parent, style="Card.TFrame")
        card_frame.pack(fill="x", padx=10, pady=5)
        
        # Icône
        icon = ach_data.get("icon", "🏆" if is_unlocked else "🔒")
        ttk.Label(card_frame, text=icon, font=("Arial", 24)).pack(side="left", padx=10)
        
        # Informations
        info_frame = ttk.Frame(card_frame)
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        name_style = "TLabel" if is_unlocked else "Secondary.TLabel"
        ttk.Label(info_frame, text=ach_data.get("name", "Succès"), 
                 font=("Arial", 12, "bold"), style=name_style).pack(anchor="w")
        ttk.Label(info_frame, text=ach_data.get("desc", "Description"), 
                 style=name_style).pack(anchor="w")
        
        if is_unlocked and "unlocked_date" in ach_data:
            ttk.Label(info_frame, text=f"Débloqué le {ach_data['unlocked_date']}", 
                     font=("Arial", 9), style="Secondary.TLabel").pack(anchor="w")
    
    def create_settings_page(self):
        """Crée la page des paramètres"""
        frame = ttk.Frame(self.content_frame)
        
        # Titre
        ttk.Label(frame, text="⚙️ Paramètres", font=("Arial", 20, "bold")).pack(pady=(0, 20))
        
        # Paramètres utilisateur
        user_frame = ttk.LabelFrame(frame, text="👤 Profil", padding=20)
        user_frame.pack(fill="x", pady=10)
        
        ttk.Label(user_frame, text="Nom d'utilisateur:").pack(anchor="w")
        self.username_var = tk.StringVar(value=self.settings.get("username", "Joueur"))
        username_entry = ttk.Entry(user_frame, textvariable=self.username_var)
        username_entry.pack(fill="x", pady=(5, 10))
        
        ttk.Button(user_frame, text="💾 Sauvegarder", 
                  command=self.save_username).pack()
        
        # Paramètres d'apparence
        appearance_frame = ttk.LabelFrame(frame, text="🎨 Apparence", padding=20)
        appearance_frame.pack(fill="x", pady=10)
        
        ttk.Label(appearance_frame, text="Thème:").pack(anchor="w")
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "darkly"))
        theme_combo = ttk.Combobox(appearance_frame, textvariable=self.theme_var, 
                                  values=THEMES, state="readonly")
        theme_combo.pack(fill="x", pady=(5, 10))
        theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        
        # Maintenance
        maintenance_frame = ttk.LabelFrame(frame, text="🛠️ Maintenance", padding=20)
        maintenance_frame.pack(fill="x", pady=10)
        
        ttk.Button(maintenance_frame, text="🗑️ Nettoyer jeux supprimés", 
                  command=self.clean_deleted_games).pack(fill="x", pady=2)
        ttk.Button(maintenance_frame, text="📊 Ouvrir dossier paramètres", 
                  command=self.open_settings_folder).pack(fill="x", pady=2)
        ttk.Button(maintenance_frame, text="📋 Voir logs d'erreur", 
                  command=self.view_crash_logs).pack(fill="x", pady=2)
        
        return frame
    
    def show_page(self, page_name):
        """Affiche une page"""
        # Cacher toutes les pages
        for page in self.pages.values():
            page.pack_forget()
        
        # Afficher la page demandée
        if page_name in self.pages:
            self.pages[page_name].pack(fill="both", expand=True)
            self.current_page = page_name
            
            # Mettre à jour les boutons de navigation
            for btn_id, btn in self.nav_buttons.items():
                if btn_id == page_name:
                    btn.configure(style="Accent.TButton")
                else:
                    btn.configure(style="Outline.TButton")
    
    def refresh_games_list(self):
        """Actualise la liste des jeux"""
        # Nettoyer les widgets existants
        for widget in self.games_container.winfo_children():
            widget.destroy()
        
        # Filtrer les jeux
        search_term = getattr(self, 'search_var', tk.StringVar()).get().lower()
        filtered_games = [g for g in self.games 
                         if not g.get("deleted", False) 
                         and search_term in g.get("name", "").lower()]
        
        if not filtered_games:
            ttk.Label(self.games_container, text="Aucun jeu trouvé", 
                     font=("Arial", 14)).pack(expand=True)
            return
        
        # Créer les cartes de jeux
        for game in filtered_games:
            self.create_game_card(self.games_container, game)
    
    def create_game_card(self, parent, game):
        """Crée une carte de jeu"""
        card_frame = ttk.Frame(parent, style="Card.TFrame")
        card_frame.pack(fill="x", padx=10, pady=5)
        
        # Informations du jeu
        info_frame = ttk.Frame(card_frame)
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        # Nom du jeu
        name = game.get("name", "Jeu sans nom")
        ttk.Label(info_frame, text=name, font=("Arial", 14, "bold")).pack(anchor="w")
        
        # Chemin (tronqué)
        path = game.get("path", "")
        if len(path) > 50:
            path = "..." + path[-47:]
        ttk.Label(info_frame, text=path, style="Secondary.TLabel").pack(anchor="w")
        
        # Statistiques
        launches = game.get("launches", 0)
        last_played = game.get("last_played", "Jamais")
        if last_played != "Jamais":
            try:
                last_played = datetime.datetime.fromisoformat(last_played).strftime("%d/%m/%Y")
            except:
                last_played = "Inconnu"
        
        stats_text = f"🚀 {launches} fois • 📅 {last_played}"
        ttk.Label(info_frame, text=stats_text, font=("Arial", 10), 
                 style="Secondary.TLabel").pack(anchor="w")
        
        # Boutons d'action
        btn_frame = ttk.Frame(card_frame)
        btn_frame.pack(side="right", padx=10)
        
        ttk.Button(btn_frame, text="▶️ Lancer", 
                  command=lambda g=game: self.launch_game(g)).pack(pady=2)
        ttk.Button(btn_frame, text="✏️ Modifier", 
                  command=lambda g=game: self.edit_game(g)).pack(pady=2)
        ttk.Button(btn_frame, text="🗑️ Supprimer", 
                  command=lambda g=game: self.delete_game(g)).pack(pady=2)
    
    def filter_games(self, *args):
        """Filtre les jeux selon la recherche"""
        self.refresh_games_list()
    
    def launch_game(self, game):
        """Lance un jeu"""
        path = game.get("path", "")
        if not os.path.exists(path):
            messagebox.showerror("Erreur", "Le fichier n'existe plus!")
            return
        
        try:
            subprocess.Popen([path], shell=True)
            
            # Mettre à jour les statistiques
            game["launches"] = game.get("launches", 0) + 1
            game["last_played"] = datetime.datetime.now().isoformat()
            
            self.save_games()
            self.refresh_games_list()
            
            # Débloquer le succès du premier jeu
            self.unlock_achievement("first_game")
            
            self.show_toast(f"🚀 {game.get('name', 'Jeu')} lancé!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lancer le jeu: {e}")
    
    def launch_random_game(self):
        """Lance un jeu aléatoire"""
        available_games = [g for g in self.games if not g.get("deleted", False)]
        if not available_games:
            messagebox.showinfo("Info", "Aucun jeu disponible!")
            return
        
        random_game = random.choice(available_games)
        self.launch_game(random_game)
    
    def scan_games(self):
        """Scanne le dossier des jeux"""
        if not os.path.exists(GAMES_FOLDER):
            messagebox.showwarning("Attention", f"Le dossier {GAMES_FOLDER} n'existe pas!")
            return
        
        extensions = ['.py', '.exe', '.bat', '.lnk']
        found_games = []
        
        for root, dirs, files in os.walk(GAMES_FOLDER):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    full_path = os.path.join(root, file)
                    name = os.path.splitext(file)[0]
                    
                    # Vérifier si le jeu existe déjà
                    if not any(g.get("path") == full_path for g in self.games):
                        found_games.append({
                            "name": name,
                            "path": full_path,
                            "launches": 0,
                            "added_date": datetime.datetime.now().isoformat()
                        })
        
        if found_games:
            self.games.extend(found_games)
            self.save_games()
            self.refresh_games_list()
            messagebox.showinfo("Scan terminé", f"{len(found_games)} nouveaux jeux trouvés!")
        else:
            messagebox.showinfo("Scan terminé", "Aucun nouveau jeu trouvé.")
    
    def add_game_manual(self):
        """Ajoute un jeu manuellement"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un jeu",
            filetypes=[("Tous les fichiers", "*.*"), ("Python", "*.py"), ("Exécutables", "*.exe")]
        )
        
        if not file_path:
            return
        
        name = simpledialog.askstring("Nom du jeu", "Nom:", 
                                     initialvalue=os.path.splitext(os.path.basename(file_path))[0])
        if not name:
            return
        
        new_game = {
            "name": name,
            "path": file_path,
            "launches": 0,
            "added_date": datetime.datetime.now().isoformat()
        }
        
        self.games.append(new_game)
        self.save_games()
        self.refresh_games_list()
        
        messagebox.showinfo("Succès", f"Jeu '{name}' ajouté!")
    
    def edit_game(self, game):
        """Modifie un jeu"""
        dialog = tk.Toplevel(self)
        dialog.title("Modifier le jeu")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (200)
        y = (dialog.winfo_screenheight() // 2) - (100)
        dialog.geometry(f"+{x}+{y}")
        
        # Champs d'édition
        ttk.Label(dialog, text="Nom:").pack(pady=5)
        name_var = tk.StringVar(value=game.get("name", ""))
        ttk.Entry(dialog, textvariable=name_var).pack(fill="x", padx=20, pady=5)
        
        ttk.Label(dialog, text="Chemin:").pack(pady=5)
        path_var = tk.StringVar(value=game.get("path", ""))
        ttk.Entry(dialog, textvariable=path_var).pack(fill="x", padx=20, pady=5)
        
        # Boutons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        def save_changes():
            game["name"] = name_var.get()
            game["path"] = path_var.get()
            self.save_games()
            self.refresh_games_list()
            dialog.destroy()
            messagebox.showinfo("Succès", "Jeu modifié!")
        
        ttk.Button(btn_frame, text="💾 Sauvegarder", command=save_changes).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="❌ Annuler", command=dialog.destroy).pack(side="left", padx=10)
    
    def delete_game(self, game):
        """Supprime un jeu"""
        if messagebox.askyesno("Confirmer", f"Supprimer '{game.get('name', 'ce jeu')}'?"):
            game["deleted"] = True
            self.save_games()
            self.refresh_games_list()
            self.show_toast("🗑️ Jeu supprimé")
    
    def save_username(self):
        """Sauvegarde le nom d'utilisateur"""
        old_username = self.settings.get("username", "Joueur")
        new_username = self.username_var.get().strip()
        
        if new_username and new_username != old_username:
            self.settings["username"] = new_username
            self.save_settings()
            messagebox.showinfo("Succès", "Nom d'utilisateur sauvegardé!")
            
            # Recréer la sidebar pour mettre à jour l'affichage
            self.create_sidebar()
    
    def change_theme(self, event=None):
        """Change le thème de l'application"""
        new_theme = self.theme_var.get()
        old_theme = self.settings.get("theme", "darkly")
        
        if new_theme != old_theme:
            self.settings["theme"] = new_theme
            self.save_settings()
            
            # Débloquer le succès changeur de thème
            self.unlock_achievement("theme_changer")
            
            messagebox.showinfo("Thème", "Redémarrez l'application pour appliquer le nouveau thème.")
    
    def clean_deleted_games(self):
        """Nettoie les jeux marqués comme supprimés"""
        before_count = len(self.games)
        self.games = [g for g in self.games if not g.get("deleted", False)]
        after_count = len(self.games)
        
        cleaned = before_count - after_count
        
        if cleaned > 0:
            self.save_games()
            self.refresh_games_list()
            messagebox.showinfo("Nettoyage", f"{cleaned} jeu(x) supprimé(s) définitivement.")
        else:
            messagebox.showinfo("Nettoyage", "Aucun jeu à nettoyer.")
    
    def open_settings_folder(self):
        """Ouvre le dossier des paramètres"""
        try:
            os.startfile(SETTINGS_FOLDER)
        except:
            messagebox.showerror("Erreur", "Impossible d'ouvrir le dossier.")
    
    def view_crash_logs(self):
        """Affiche les logs d'erreur"""
        if os.path.exists(CRASH_LOG_FILE):
            try:
                os.startfile(CRASH_LOG_FILE)
            except:
                messagebox.showerror("Erreur", "Impossible d'ouvrir le fichier de logs.")
        else:
            messagebox.showinfo("Info", "Aucun log d'erreur trouvé.")
    
    def unlock_achievement(self, achievement_id):
        """Débloque un succès"""
        if achievement_id in self.achievements_data:
            ach = self.achievements_data[achievement_id]
            if not ach.get("unlocked", False):
                ach["unlocked"] = True
                ach["unlocked_date"] = datetime.datetime.now().strftime("%d/%m/%Y à %H:%M")
                self.save_achievements()
                
                # Notification
                self.show_toast(f"🏆 Succès débloqué: {ach.get('name', 'Succès')}")
    
    def show_toast(self, message):
        """Affiche une notification temporaire"""
        toast = tk.Toplevel(self)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        
        # Position en bas à droite
        toast.update_idletasks()
        x = self.winfo_rootx() + self.winfo_width() - 300
        y = self.winfo_rooty() + self.winfo_height() - 100
        toast.geometry(f"280x60+{x}+{y}")
        
        # Style
        toast.configure(bg="#2d3748")
        
        label = tk.Label(toast, text=message, bg="#2d3748", fg="white", 
                        font=("Arial", 10), wraplength=260)
        label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Auto-destruction après 3 secondes
        toast.after(3000, toast.destroy)
    
    def initial_scan(self):
        """Scan initial au démarrage"""
        if not self.games:  # Seulement si aucun jeu n'est présent
            self.scan_games()

if __name__ == "__main__":
    try:
        app = DodoxiFixed()
        app.mainloop()
    except Exception as e:
        log_crash("Erreur fatale au démarrage", e)
        messagebox.showerror("Erreur Fatale", f"L'application a rencontré une erreur: {e}")