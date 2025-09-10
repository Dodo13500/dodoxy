# -*- coding: utf-8 -*-
# Dodoxi Hybrid - Le Meilleur des Deux Mondes
# Version hybride entre simplicité et fonctionnalités avancées

import os
import sys
import json
import datetime
import random
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog

# Vérification des dépendances
missing_deps = []
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from ttkbootstrap.scrolled import ScrolledFrame
except ImportError:
    missing_deps.append("ttkbootstrap")

try:
    from PIL import Image, ImageTk
except ImportError:
    missing_deps.append("Pillow")

if missing_deps:
    root = tk.Tk()
    root.withdraw()
    if messagebox.askyesno("Dépendances", f"Installer {', '.join(missing_deps)} ?"):
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_deps)
        messagebox.showinfo("Info", "Redémarrez l'application")
    sys.exit()

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
GAMES_FOLDER = os.path.join(SCRIPT_DIR, "jeux")
os.makedirs(DATA_DIR, exist_ok=True)

GAMES_FILE = os.path.join(DATA_DIR, "games.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
ACHIEVEMENTS_FILE = os.path.join(DATA_DIR, "achievements.json")

APP_NAME = "🎮 Dodoxi Hybrid"
VERSION = "v1.0"

class DodoxiHybrid(ttk.Window):
    def __init__(self):
        # Charger le thème
        theme = self.load_theme()
        super().__init__(themename=theme, title=APP_NAME)
        
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Données
        self.games = self.load_games()
        self.settings = self.load_settings()
        self.achievements = self.load_achievements()
        
        # Variables d'interface
        self.current_view = "grid"  # grid ou list
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_games)
        
        # Interface
        self.create_interface()
        
        # Scan initial si nécessaire
        if not self.games:
            self.after(1000, self.auto_scan)
        
        # Débloquer le succès de premier lancement
        self.unlock_achievement("first_launch")
    
    def load_theme(self):
        """Charge le thème sauvegardé"""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return settings.get("theme", "darkly")
        except:
            pass
        return "darkly"
    
    def load_games(self):
        """Charge la liste des jeux"""
        try:
            if os.path.exists(GAMES_FILE):
                with open(GAMES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def load_settings(self):
        """Charge les paramètres"""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {"theme": "darkly", "username": "Joueur", "view_mode": "grid"}
    
    def load_achievements(self):
        """Charge les succès avec valeurs par défaut"""
        default_achievements = {
            "first_launch": {"name": "Bienvenue!", "desc": "Premier lancement", "unlocked": False, "icon": "🎉"},
            "first_game": {"name": "Premier Jeu", "desc": "Lancer votre premier jeu", "unlocked": False, "icon": "🚀"},
            "scanner": {"name": "Explorateur", "desc": "Scanner le dossier des jeux", "unlocked": False, "icon": "🔍"},
            "collector": {"name": "Collectionneur", "desc": "Avoir 10 jeux", "unlocked": False, "icon": "📚"},
            "theme_master": {"name": "Styliste", "desc": "Changer de thème", "unlocked": False, "icon": "🎨"},
            "random_player": {"name": "Aventurier", "desc": "Lancer un jeu aléatoire", "unlocked": False, "icon": "🎲"}
        }
        
        try:
            if os.path.exists(ACHIEVEMENTS_FILE):
                with open(ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    # Fusionner avec les defaults
                    for key, value in default_achievements.items():
                        if key not in saved:
                            saved[key] = value
                    return saved
        except:
            pass
        
        return default_achievements
    
    def save_games(self):
        """Sauvegarde les jeux"""
        try:
            with open(GAMES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.games, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur sauvegarde: {e}")
    
    def save_settings(self):
        """Sauvegarde les paramètres"""
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def save_achievements(self):
        """Sauvegarde les succès"""
        try:
            with open(ACHIEVEMENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.achievements, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def create_interface(self):
        """Crée l'interface principale"""
        # Configuration de la grille principale
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Barre supérieure
        self.create_header()
        
        # Zone principale avec onglets
        self.create_main_area()
        
        # Barre de statut
        self.create_status_bar()
    
    def create_header(self):
        """Crée la barre supérieure"""
        header_frame = ttk.Frame(self, style="Card.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo et titre
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        ttk.Label(title_frame, text=APP_NAME, font=("Arial", 18, "bold")).pack(side="left")
        ttk.Label(title_frame, text=f"• {len([g for g in self.games if not g.get('deleted', False)])} jeux", 
                 font=("Arial", 10), style="Secondary.TLabel").pack(side="left", padx=(10, 0))
        
        # Barre de recherche
        search_frame = ttk.Frame(header_frame)
        search_frame.grid(row=0, column=1, sticky="ew", padx=20, pady=10)
        search_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="🔍").grid(row=0, column=0, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, 
                               font=("Arial", 11))
        search_entry.grid(row=0, column=1, sticky="ew")
        
        # Boutons d'action rapide
        actions_frame = ttk.Frame(header_frame)
        actions_frame.grid(row=0, column=2, sticky="e", padx=10, pady=10)
        
        ttk.Button(actions_frame, text="🔍 Scanner", 
                  command=self.scan_games, style="Accent.TButton").pack(side="left", padx=2)
        ttk.Button(actions_frame, text="➕ Ajouter", 
                  command=self.add_game).pack(side="left", padx=2)
        ttk.Button(actions_frame, text="🎲 Aléatoire", 
                  command=self.launch_random).pack(side="left", padx=2)
    
    def create_main_area(self):
        """Crée la zone principale avec onglets"""
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Onglet Jeux
        self.games_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.games_frame, text="🎮 Jeux")
        self.create_games_tab()
        
        # Onglet Succès
        self.achievements_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.achievements_frame, text="🏆 Succès")
        self.create_achievements_tab()
        
        # Onglet Paramètres
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Paramètres")
        self.create_settings_tab()
    
    def create_games_tab(self):
        """Crée l'onglet des jeux"""
        # Barre d'outils
        toolbar = ttk.Frame(self.games_frame)
        toolbar.pack(fill="x", padx=10, pady=(10, 5))
        
        # Mode d'affichage
        ttk.Label(toolbar, text="Affichage:").pack(side="left")
        
        self.view_var = tk.StringVar(value=self.settings.get("view_mode", "grid"))
        view_frame = ttk.Frame(toolbar)
        view_frame.pack(side="left", padx=(5, 20))
        
        ttk.Radiobutton(view_frame, text="🔲 Grille", variable=self.view_var, 
                       value="grid", command=self.change_view).pack(side="left")
        ttk.Radiobutton(view_frame, text="📋 Liste", variable=self.view_var, 
                       value="list", command=self.change_view).pack(side="left", padx=(10, 0))
        
        # Tri
        ttk.Label(toolbar, text="Tri:").pack(side="left")
        self.sort_var = tk.StringVar(value="name")
        sort_combo = ttk.Combobox(toolbar, textvariable=self.sort_var, width=15,
                                 values=["name", "launches", "last_played"], state="readonly")
        sort_combo.pack(side="left", padx=(5, 0))
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_games())
        
        # Zone de jeux avec scrollbar
        self.games_scrolled = ScrolledFrame(self.games_frame)
        self.games_scrolled.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.refresh_games()
    
    def create_achievements_tab(self):
        """Crée l'onglet des succès"""
        # Statistiques des succès
        stats_frame = ttk.LabelFrame(self.achievements_frame, text="📊 Progression", padding=15)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        unlocked = sum(1 for ach in self.achievements.values() if ach.get("unlocked", False))
        total = len(self.achievements)
        progress = (unlocked / total * 100) if total > 0 else 0
        
        ttk.Label(stats_frame, text=f"Succès débloqués: {unlocked}/{total} ({progress:.0f}%)",
                 font=("Arial", 12)).pack()
        
        progress_bar = ttk.Progressbar(stats_frame, value=progress, length=400)
        progress_bar.pack(pady=10)
        
        # Liste des succès
        achievements_scrolled = ScrolledFrame(self.achievements_frame)
        achievements_scrolled.pack(fill="both", expand=True, padx=10, pady=5)
        
        for ach_id, ach_data in self.achievements.items():
            self.create_achievement_widget(achievements_scrolled, ach_id, ach_data)
    
    def create_achievement_widget(self, parent, ach_id, ach_data):
        """Crée un widget de succès"""
        is_unlocked = ach_data.get("unlocked", False)
        
        frame = ttk.Frame(parent, style="Card.TFrame")
        frame.pack(fill="x", padx=5, pady=3)
        
        # Icône
        icon = ach_data.get("icon", "🏆") if is_unlocked else "🔒"
        ttk.Label(frame, text=icon, font=("Arial", 20)).pack(side="left", padx=15, pady=10)
        
        # Informations
        info_frame = ttk.Frame(frame)
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        style = "TLabel" if is_unlocked else "Secondary.TLabel"
        ttk.Label(info_frame, text=ach_data.get("name", "Succès"), 
                 font=("Arial", 11, "bold"), style=style).pack(anchor="w")
        ttk.Label(info_frame, text=ach_data.get("desc", "Description"), 
                 style=style).pack(anchor="w")
        
        if is_unlocked and "date" in ach_data:
            ttk.Label(info_frame, text=f"Débloqué: {ach_data['date']}", 
                     font=("Arial", 9), style="Secondary.TLabel").pack(anchor="w")
    
    def create_settings_tab(self):
        """Crée l'onglet des paramètres"""
        # Profil utilisateur
        profile_frame = ttk.LabelFrame(self.settings_frame, text="👤 Profil", padding=15)
        profile_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(profile_frame, text="Nom d'utilisateur:").pack(anchor="w")
        self.username_var = tk.StringVar(value=self.settings.get("username", "Joueur"))
        username_entry = ttk.Entry(profile_frame, textvariable=self.username_var)
        username_entry.pack(fill="x", pady=(5, 10))
        
        ttk.Button(profile_frame, text="💾 Sauvegarder", 
                  command=self.save_username).pack()
        
        # Apparence
        appearance_frame = ttk.LabelFrame(self.settings_frame, text="🎨 Apparence", padding=15)
        appearance_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(appearance_frame, text="Thème:").pack(anchor="w")
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "darkly"))
        
        themes = ["darkly", "solar", "cyborg", "superhero", "lumen", "cosmo", "flatly", "journal"]
        theme_combo = ttk.Combobox(appearance_frame, textvariable=self.theme_var, 
                                  values=themes, state="readonly")
        theme_combo.pack(fill="x", pady=(5, 10))
        theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        
        # Statistiques
        stats_frame = ttk.LabelFrame(self.settings_frame, text="📊 Statistiques", padding=15)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        total_games = len([g for g in self.games if not g.get("deleted", False)])
        total_launches = sum(g.get("launches", 0) for g in self.games)
        unlocked_achievements = sum(1 for ach in self.achievements.values() if ach.get("unlocked", False))
        
        stats_text = f"""
🎮 Jeux dans la bibliothèque: {total_games}
🚀 Lancements totaux: {total_launches}
🏆 Succès débloqués: {unlocked_achievements}/{len(self.achievements)}
📅 Membre depuis: {self.settings.get('join_date', 'Aujourd\'hui')}
        """.strip()
        
        ttk.Label(stats_frame, text=stats_text, justify="left").pack(anchor="w")
        
        # Maintenance
        maintenance_frame = ttk.LabelFrame(self.settings_frame, text="🛠️ Maintenance", padding=15)
        maintenance_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(maintenance_frame, text="🗑️ Nettoyer jeux supprimés", 
                  command=self.clean_deleted).pack(fill="x", pady=2)
        ttk.Button(maintenance_frame, text="📁 Ouvrir dossier données", 
                  command=lambda: os.startfile(DATA_DIR)).pack(fill="x", pady=2)
        ttk.Button(maintenance_frame, text="🔄 Réinitialiser succès", 
                  command=self.reset_achievements).pack(fill="x", pady=2)
    
    def create_status_bar(self):
        """Crée la barre de statut"""
        status_frame = ttk.Frame(self, style="Card.TFrame")
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        
        # Informations de statut
        active_games = len([g for g in self.games if not g.get("deleted", False)])
        total_launches = sum(g.get("launches", 0) for g in self.games)
        
        status_text = f"📊 {active_games} jeux • {total_launches} lancements • Version {VERSION}"
        ttk.Label(status_frame, text=status_text, style="Secondary.TLabel").pack(side="left", padx=10, pady=5)
        
        # Indicateur de succès récents
        recent_achievements = [ach for ach in self.achievements.values() 
                             if ach.get("unlocked", False) and "date" in ach]
        if recent_achievements:
            ttk.Label(status_frame, text="🏆 Nouveau succès disponible!", 
                     style="Success.TLabel").pack(side="right", padx=10, pady=5)
    
    def refresh_games(self):
        """Actualise l'affichage des jeux"""
        # Nettoyer l'affichage actuel
        for widget in self.games_scrolled.winfo_children():
            widget.destroy()
        
        # Filtrer et trier les jeux
        search_term = self.search_var.get().lower()
        filtered_games = [g for g in self.games 
                         if not g.get("deleted", False) 
                         and search_term in g.get("name", "").lower()]
        
        # Tri
        sort_key = self.sort_var.get()
        if sort_key == "name":
            filtered_games.sort(key=lambda g: g.get("name", "").lower())
        elif sort_key == "launches":
            filtered_games.sort(key=lambda g: g.get("launches", 0), reverse=True)
        elif sort_key == "last_played":
            filtered_games.sort(key=lambda g: g.get("last_played", ""), reverse=True)
        
        if not filtered_games:
            ttk.Label(self.games_scrolled, text="Aucun jeu trouvé", 
                     font=("Arial", 14), style="Secondary.TLabel").pack(expand=True)
            return
        
        # Afficher selon le mode
        if self.view_var.get() == "grid":
            self.show_games_grid(filtered_games)
        else:
            self.show_games_list(filtered_games)
    
    def show_games_grid(self, games):
        """Affiche les jeux en mode grille"""
        container = ttk.Frame(self.games_scrolled)
        container.pack(fill="both", expand=True, padx=10, pady=5)
        
        cols = 3  # Nombre de colonnes
        for i, game in enumerate(games):
            row = i // cols
            col = i % cols
            
            card = self.create_game_card(container, game, mode="grid")
            card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
        # Configurer les colonnes pour qu'elles s'étendent
        for i in range(cols):
            container.grid_columnconfigure(i, weight=1)
    
    def show_games_list(self, games):
        """Affiche les jeux en mode liste"""
        for game in games:
            card = self.create_game_card(self.games_scrolled, game, mode="list")
            card.pack(fill="x", padx=10, pady=2)
    
    def create_game_card(self, parent, game, mode="grid"):
        """Crée une carte de jeu"""
        card = ttk.Frame(parent, style="Card.TFrame")
        
        if mode == "grid":
            # Mode grille - plus compact et vertical
            card.configure(padding=10)
            
            # Nom du jeu
            name = game.get("name", "Jeu sans nom")
            if len(name) > 20:
                name = name[:17] + "..."
            ttk.Label(card, text=name, font=("Arial", 11, "bold")).pack()
            
            # Statistiques
            launches = game.get("launches", 0)
            ttk.Label(card, text=f"🚀 {launches} fois", 
                     style="Secondary.TLabel").pack(pady=(5, 10))
            
            # Bouton de lancement
            ttk.Button(card, text="▶️ Lancer", 
                      command=lambda g=game: self.launch_game(g),
                      style="Accent.TButton").pack(fill="x")
            
            # Menu contextuel (clic droit)
            card.bind("<Button-3>", lambda e, g=game: self.show_game_menu(e, g))
            
        else:
            # Mode liste - plus d'informations horizontales
            card.configure(padding=8)
            
            # Informations principales
            info_frame = ttk.Frame(card)
            info_frame.pack(side="left", fill="both", expand=True)
            
            name = game.get("name", "Jeu sans nom")
            ttk.Label(info_frame, text=name, font=("Arial", 12, "bold")).pack(anchor="w")
            
            # Chemin (tronqué)
            path = game.get("path", "")
            if len(path) > 60:
                path = "..." + path[-57:]
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
            ttk.Label(info_frame, text=stats_text, font=("Arial", 9), 
                     style="Secondary.TLabel").pack(anchor="w")
            
            # Boutons d'action
            btn_frame = ttk.Frame(card)
            btn_frame.pack(side="right", padx=10)
            
            ttk.Button(btn_frame, text="▶️", 
                      command=lambda g=game: self.launch_game(g),
                      width=3).pack(side="left", padx=2)
            ttk.Button(btn_frame, text="✏️", 
                      command=lambda g=game: self.edit_game(g),
                      width=3).pack(side="left", padx=2)
            ttk.Button(btn_frame, text="🗑️", 
                      command=lambda g=game: self.delete_game(g),
                      width=3).pack(side="left", padx=2)
        
        return card
    
    def show_game_menu(self, event, game):
        """Affiche le menu contextuel d'un jeu"""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="▶️ Lancer", command=lambda: self.launch_game(game))
        menu.add_command(label="✏️ Modifier", command=lambda: self.edit_game(game))
        menu.add_separator()
        menu.add_command(label="🗑️ Supprimer", command=lambda: self.delete_game(game))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def filter_games(self, *args):
        """Filtre les jeux selon la recherche"""
        self.refresh_games()
    
    def change_view(self):
        """Change le mode d'affichage"""
        self.settings["view_mode"] = self.view_var.get()
        self.save_settings()
        self.refresh_games()
    
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
            self.refresh_games()
            
            # Débloquer le succès du premier jeu
            self.unlock_achievement("first_game")
            
            # Vérifier le succès collectionneur
            if len([g for g in self.games if not g.get("deleted", False)]) >= 10:
                self.unlock_achievement("collector")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lancer le jeu: {e}")
    
    def launch_random(self):
        """Lance un jeu aléatoire"""
        available_games = [g for g in self.games if not g.get("deleted", False)]
        if not available_games:
            messagebox.showinfo("Info", "Aucun jeu disponible!")
            return
        
        random_game = random.choice(available_games)
        self.launch_game(random_game)
        self.unlock_achievement("random_player")
    
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
            self.refresh_games()
            self.unlock_achievement("scanner")
            messagebox.showinfo("Scan terminé", f"{len(found_games)} nouveaux jeux trouvés!")
        else:
            messagebox.showinfo("Scan terminé", "Aucun nouveau jeu trouvé.")
    
    def add_game(self):
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
        self.refresh_games()
        
        messagebox.showinfo("Succès", f"Jeu '{name}' ajouté!")
    
    def edit_game(self, game):
        """Modifie un jeu"""
        dialog = tk.Toplevel(self)
        dialog.title("Modifier le jeu")
        dialog.geometry("400x150")
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 75
        dialog.geometry(f"+{x}+{y}")
        
        # Champs
        ttk.Label(dialog, text="Nom:").pack(pady=5)
        name_var = tk.StringVar(value=game.get("name", ""))
        ttk.Entry(dialog, textvariable=name_var).pack(fill="x", padx=20, pady=5)
        
        # Boutons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        def save_changes():
            game["name"] = name_var.get()
            self.save_games()
            self.refresh_games()
            dialog.destroy()
        
        ttk.Button(btn_frame, text="💾 Sauvegarder", command=save_changes).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="❌ Annuler", command=dialog.destroy).pack(side="left", padx=10)
    
    def delete_game(self, game):
        """Supprime un jeu"""
        if messagebox.askyesno("Confirmer", f"Supprimer '{game.get('name', 'ce jeu')}'?"):
            game["deleted"] = True
            self.save_games()
            self.refresh_games()
    
    def save_username(self):
        """Sauvegarde le nom d'utilisateur"""
        new_username = self.username_var.get().strip()
        if new_username:
            self.settings["username"] = new_username
            if "join_date" not in self.settings:
                self.settings["join_date"] = datetime.datetime.now().strftime("%d/%m/%Y")
            self.save_settings()
            messagebox.showinfo("Succès", "Nom d'utilisateur sauvegardé!")
    
    def change_theme(self, event=None):
        """Change le thème"""
        new_theme = self.theme_var.get()
        self.settings["theme"] = new_theme
        self.save_settings()
        self.unlock_achievement("theme_master")
        messagebox.showinfo("Thème", "Redémarrez l'application pour appliquer le nouveau thème.")
    
    def clean_deleted(self):
        """Nettoie les jeux supprimés"""
        before = len(self.games)
        self.games = [g for g in self.games if not g.get("deleted", False)]
        after = len(self.games)
        
        if before > after:
            self.save_games()
            self.refresh_games()
            messagebox.showinfo("Nettoyage", f"{before - after} jeu(x) supprimé(s) définitivement.")
        else:
            messagebox.showinfo("Nettoyage", "Aucun jeu à nettoyer.")
    
    def reset_achievements(self):
        """Remet à zéro les succès"""
        if messagebox.askyesno("Confirmer", "Remettre à zéro tous les succès?"):
            for ach in self.achievements.values():
                ach["unlocked"] = False
                if "date" in ach:
                    del ach["date"]
            self.save_achievements()
            self.create_achievements_tab()  # Rafraîchir l'affichage
            messagebox.showinfo("Succès", "Tous les succès ont été remis à zéro.")
    
    def unlock_achievement(self, achievement_id):
        """Débloque un succès"""
        if achievement_id in self.achievements:
            ach = self.achievements[achievement_id]
            if not ach.get("unlocked", False):
                ach["unlocked"] = True
                ach["date"] = datetime.datetime.now().strftime("%d/%m/%Y à %H:%M")
                self.save_achievements()
                
                # Notification simple
                self.after(100, lambda: messagebox.showinfo("🏆 Succès débloqué!", 
                                                           f"{ach.get('name', 'Succès')}\n{ach.get('desc', '')}"))
    
    def auto_scan(self):
        """Scan automatique au premier lancement"""
        if os.path.exists(GAMES_FOLDER):
            self.scan_games()

if __name__ == "__main__":
    try:
        app = DodoxiHybrid()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Erreur Fatale", f"Une erreur est survenue: {e}")
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()