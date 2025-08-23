# -*- coding: utf-8 -*-
# Mon Lanceur de Jeux Propulsé par IA - Version Réparée et Stabilisée

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
import csv
from tkinter import messagebox, filedialog, simpledialog
import urllib.request
import urllib.error
import webbrowser

# Dépendances UI/Images
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from ttkbootstrap.scrolled import ScrolledFrame
    from ttkbootstrap.tooltip import ToolTip
    from ttkbootstrap.widgets import Meter
    from PIL import Image, ImageTk, ImageDraw, ImageFont
except ImportError:
    try:
        resp = messagebox.askyesno(
            "Dépendances manquantes",
            "Ce programme nécessite 'ttkbootstrap' et 'Pillow'.\n" \
            "Souhaitez-vous les installer maintenant ?"
        )
    except Exception:
        resp = False # Default to not installing if messagebox fails

    if resp: # User wants to install missing dependencies.
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "ttkbootstrap", "Pillow"], check=True)
            messagebox.showinfo("Installation réussie", "Modules installés. Veuillez relancer l'application.")
            sys.exit(0)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'installer les dépendances: {e}")
            sys.exit(1)
    else:
        sys.exit(0)

# --- Constants and Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# NEW: Portable Mode Check and SETTINGS_FOLDER definition
if os.path.exists(os.path.join(SCRIPT_DIR, "portable.txt")):
    SETTINGS_FOLDER = os.path.join(SCRIPT_DIR, "data")
else:
    SETTINGS_FOLDER = os.path.join(SCRIPT_DIR, "settings")
GAMES_FOLDER = r"C:\Users\Utilisateur\Desktop\jeux en python\jeux"
IMAGES_FOLDER = os.path.join(SCRIPT_DIR, "images")
SETTINGS_FILE = os.path.join(SETTINGS_FOLDER, "settings.json")
GAMES_FILE = os.path.join(SETTINGS_FOLDER, "games.json")
ACHIEVEMENTS_FILE = os.path.join(SETTINGS_FOLDER, "achievements.json")
COLLECTIONS_FILE = os.path.join(SETTINGS_FOLDER, "collections.json")
CRASH_LOG_FILE = os.path.join(SETTINGS_FOLDER, "crash_log.txt")
GRADIENT_DEFAULT_PATH = os.path.join(IMAGES_FOLDER, "gradient_default.png")
DEFAULT_GAME_ICON = os.path.join(IMAGES_FOLDER, "default_icon.png")

# --- App Info ---
VERSION = "v0.16.3"
COPYRIGHT = "© dodosi 2025"
APP_NAME = "Dodoxi"

# --- Available Themes ---
THEMES = [
    "darkly", "solar", "cyborg", "superhero", "lumen",
    "cosmo", "flatly", "journal", "litera", "minty", # Themes for ttkbootstrap
    "united", "sandstone", "yeti", "pulse", "morph", "vapor"
]

TRASH_ICON = "🗑️" # Using an emoji for the icon
TIPS = [
    "Appuyez sur F5 pour rechercher de nouveaux jeux à tout moment.",
    "Utilisez Ctrl+F pour accéder directement à la barre de recherche.",
    "Personnalisez l'apparence dans les Paramètres pour une expérience unique.",
    "Utilisez le gestionnaire de catégories dans les paramètres pour organiser votre bibliothèque.",
    "Gardez un œil sur les succès pour découvrir de nouvelles façons de jouer.",
    "Le mode 'Liste' dans la page des jeux peut être plus pratique pour les grandes bibliothèques.",
    "Exportez vos données régulièrement depuis les Paramètres pour ne rien perdre.",
    "Le jeu 'À la une' sur la page d'accueil vous suggère des jeux que vous n'avez pas lancés depuis longtemps."
]

# --- Utility Functions ---
def log_crash(message: str, exception: Exception | None = None) -> None:
    try:
        if not os.path.exists(SETTINGS_FOLDER):
            os.makedirs(SETTINGS_FOLDER)
        with open(CRASH_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"Rapport d'erreur - {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n")
            f.write(f"Message: {message}\n")
            if exception:
                f.write(f"Erreur: {exception}\n")
                f.write("Traceback:\n")
                f.write(traceback.format_exc())
            f.write("-" * 40 + "\n")
    except Exception as e:
        print(f"Échec du log crash: {e}")

def check_and_install_module(module_name: str) -> bool:
    try: # Attempt to import the module
        __import__(module_name)
        return True
    except ImportError:
        resp = messagebox.askyesno( # Prompt the user to install the module if not found.
            "Module manquant",
            f"Le module '{module_name}' est nécessaire pour lancer ce jeu.\n"
            f"Souhaitez-vous l'installer maintenant ?"
        )
        if not resp:
            return False
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", module_name], check=True) # Install
            messagebox.showinfo("Installation réussie", f"Le module '{module_name}' a été installé.")
            return True
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'installation de '{module_name}': {e}")
            return False

class SafeScrolledFrame(ScrolledFrame):
    """
    A ScrolledFrame that disables the default mouse-enter/leave bindings
    to prevent crashes when child widgets are destroyed dynamically.
    Scrolling is handled by a global mouse wheel binding instead.
    """
    def _on_enter(self, _):
        pass

    def _on_leave(self, _):
        pass
# --- Classe Principale de l'Application ---
class GameLauncher(ttk.Window): # Main application class
    def __init__(self):
        themename = self._load_theme()
        super().__init__(themename=themename)

        self.app_style = ttk.Style()
        self.show_splash()
        self.title(APP_NAME) # Window title
        self.ensure_directories() # Ensure directories exist early
        self.geometry("1400x1000")
        self.minsize(900, 700)

        # --- Initialisation des variables d'instance ---
        # Il est préférable d'initialiser les attributs avant qu'ils ne soient potentiellement utilisés.
        self.background_label = None
        self.original_background_pil = None
        self.background_image = None
        self.animation_type_var = None # Will be initialized later
        self.is_transitioning = False
        self.filtered_games = []
        self.current_page_frame = None
        self.visited_pages = set()
        self.search_timer = None
        self.spotlight_game = None
        self.session_launched_games = set()
        self.pro_page_notebook = None
        self.session_maintenance_actions = set()
        self._last_ach_cols = 0
        self._last_games_cols = 0
        self.session_pro_pages_visited = set()
        self.scan_in_progress = threading.Event()
        self.games_lock = threading.Lock()
        self.is_updating_view = False # Flag to prevent scrolling during view updates
        self.game_card_widgets = {}
        self.icon_cache = {}
        self.page_map = {}
        self.sidebar_buttons = {}
        self.gradient_cache = {}

        self.collection_filter = None
        # --- Attributs pour les cadres à défilement ---
        self.settings_scrolled_frame = None
        self.games_scrolled_frame = None
        self.games_grid_frame = None
        self.achievements_scrolled_frame = None
        self.achievements_container = None

        self.achievement_headers = {}
        self.achievement_separators = {}
        self.achievement_card_widgets = {} # NEW
        # --- Attributs pour les widgets dynamiques de la page "Aperçu" ---
        self.sidebar_user_label = None
        self.pro_username_label = None
        self.pro_profile_playtime_label = None
        self.pro_profile_launched_label = None
        self.pro_profile_fav_label = None
        self.pro_profile_reg_label = None
        self.pro_stats_ach_meter = None
        self.pro_stats_lib_total_label = None
        self.pro_stats_lib_desc_label = None
        self.pro_stats_lib_icon_label = None
        self.pro_stats_lib_missing_label = None
        self.pro_stats_top_games_tree = None
        self.pro_suggestion_frame = None

        self.pages_dirty = {"main": True, "games": True, "achievements": True}

        # --- Chargement des données et initialisation des variables dépendantes ---
        # Création du conteneur pour les notifications "toast"
        self.toast_container = ttk.Frame(self)
        self.toast_container.place(relx=0.99, rely=0.98, anchor="se")
        self.toast_container.lift()
        # Empêche les toasts d'intercepter les clics de la fenêtre principale
        self.toast_container.bind("<Button-1>", lambda e: "break")

        self.achievements_data = self.load_achievements()
        self.collections = self.load_collections()
        self.settings = self.load_settings()
        self.games = self.load_games()

        # Variables dépendant des 'settings'
        self.current_background_path = self.settings.get("background", "")
        self.theme_change_count = self.settings.get("theme_change_count", 0)
        self.fullscreen_var = tk.BooleanVar(value=self.settings.get("fullscreen", False))
        self.autohide_scrollbars_var = tk.BooleanVar(value=self.settings.get("autohide_scrollbars", True))
        self.font_size_var = tk.StringVar(value=self.settings.get("font_size", "Moyen"))
        self.corner_radius_var = tk.IntVar(value=self.settings.get("corner_radius", 8))
        self.animation_type_var = tk.StringVar(value=self.settings.get("page_transition_animation", "Glissement"))
        self.view_mode = tk.StringVar(value=self.settings.get("view_mode", "Grille"))

        # --- Traitement initial des données ---
        self.initial_scan_for_games()
        self.check_missing_games()
        self.save_games() # Cette ligne ne plantera plus
        self.check_loyalty_achievement()
        self._init_styles()

        # Variables pour les filtres et le tri
        self.sort_order = tk.StringVar(value="Nom (A-Z)")
        self.show_favorites_only = tk.BooleanVar(value=False)
        self.category_filter = tk.StringVar(value="Toutes")

        self.create_default_gradient()
        self.set_background(self.current_background_path)
        self.create_default_icon()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ttk.Frame(self, style="Sidebar.TFrame")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.content_frame = ttk.Frame(self) # Frame for main content
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # --- Création des cadres pour chaque page ---
        self.main_page_frame = ttk.Frame(self.content_frame)
        self.games_page_frame = ttk.Frame(self.content_frame)
        self.settings_page_frame = ttk.Frame(self.content_frame)
        self.achievements_page_frame = ttk.Frame(self.content_frame)
        self.pro_page_frame = ttk.Frame(self.content_frame)

        all_frames = (self.main_page_frame, self.games_page_frame, self.settings_page_frame, self.achievements_page_frame,
                      self.pro_page_frame)
        for frame in all_frames:
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.create_main_page()
        self.create_games_page()
        self.create_settings_page()
        self.create_achievements_page()
        self.create_pro_page()

        self.page_order = ["main", "games", "achievements", "settings", "pro"]
        self.page_map = {
            "main": self.main_page_frame, "games": self.games_page_frame,
            "settings": self.settings_page_frame, "achievements": self.achievements_page_frame,
            "pro": self.pro_page_frame
        }
        self.frame_map = {v: k for k, v in self.page_map.items()}
        
        # Initial page setup without animation
        self.main_page_frame.tkraise()
        self.current_page_frame = self.main_page_frame
        self.update_welcome_message()
        self.update_main_page_stats()
        self.pages_dirty["main"] = False
        # Création de la sidebar après les pages pour que les commandes fonctionnent
        self.create_sidebar()
        self.resize_timer = None
        self.bind("<Configure>", self.delayed_resize)
        self.bind("<Control-o>", self.unlock_achievement_1)
        self.bind("<Control-f>", self.focus_search)
        self.bind("<F5>", lambda e: self.start_manual_scan())
        self.bind("<Control-r>", lambda e: self.lancer_jeu_aleatoire()) # Keybind to launch a random game
        self.bind_all("<MouseWheel>", self._on_global_mouse_wheel)
        self.running_processes = {}
        self.after(2000, self.poll_processes)
        self.after(500, self.verify_dependencies_on_startup)
        self.after(100, lambda: self.attributes("-fullscreen", self.fullscreen_var.get()))
        
        if self.settings.get("first_run", True):
            self.after(500, self.perform_first_run_setup) # Guide the user on first launch

        # Show 'what's new' after an update, but not on the very first run.
        if not self.settings.get("first_run", True) and self.settings.get("last_seen_version") != VERSION: # Show 'what's new' after update.
            self.after(1000, self.show_whats_new_window)

        # Check for portable mode achievement
        if os.path.exists(os.path.join(SCRIPT_DIR, "portable.txt")):
            self.check_and_unlock_achievement("achievement_portable")
        
        self.after(5000, self.start_update_check) # Check for updates a few seconds after launch

    def _on_global_mouse_wheel(self, event):
        """
        Handles mouse wheel scrolling globally and directs it to the
        appropriate ScrolledFrame under the cursor.
        """
        if self.is_updating_view:
            return

        widget = self.winfo_containing(event.x_root, event.y_root)
        while widget:
            if isinstance(widget, (ScrolledFrame, SafeScrolledFrame)):
                if widget.vscroll.winfo_ismapped():
                    widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    return
            if widget == self: break
            widget = widget.master

    # --- Splash & Animations ---
    def show_splash(self):
        self.withdraw()
        splash = tk.Toplevel(self)
        splash.overrideredirect(True)
        w, h = 500, 300
        x = self.winfo_screenwidth()//2 - w//2
        y = self.winfo_screenheight()//2 - h//2
        splash.geometry(f"{w}x{h}+{x}+{y}")

        splash.configure(bg="#2a2a2a")
        lbl = ttk.Label(splash, text=APP_NAME, font=("Segoe UI", 36, "bold"), foreground="#ffffff", background="#2a2a2a")
        lbl.place(relx=0.5, rely=0.5, anchor="center")

        splash.attributes("-alpha", 0.0)
        self.fade_in(splash)

        splash.after(1800, lambda: self.fade_out(splash, splash.destroy))
        self.after(2300, self.deiconify)

    def fade_in(self, widget, step=0.05):
        try:
            alpha = widget.attributes("-alpha") # Fade in animation
            if alpha < 1.0:
                widget.attributes("-alpha", alpha + step)
                self.after(20, lambda: self.fade_in(widget, step))
        except tk.TclError:
            pass

    def fade_out(self, widget, callback=None, step=0.05):
        try:
            alpha = widget.attributes("-alpha") # Fade out animation
            if alpha > 0.0:
                widget.attributes("-alpha", alpha - step)
                self.after(20, lambda: self.fade_out(widget, callback, step))
            elif callback:
                callback()
        except tk.TclError:
            pass

    def staggered_load(self, container, items, creation_callback, delay=20, animate=True):
        """Creates widgets for items with a staggered animation effect."""
        self.is_updating_view = True

        for widget in container.winfo_children():
            widget.destroy()
        if container == self.games_grid_frame:
            self.game_card_widgets.clear()
        
        # Force the UI to process pending events, including widget destruction
        self.update_idletasks()

        def _create_one(index=0):
            if index < len(items):
                widget = creation_callback(items[index], index)
                if widget and animate:
                    self.animate_reveal(widget)
                self.after(delay, lambda: _create_one(index + 1))
            else:
                self.is_updating_view = False

        _create_one()

    def animate_reveal(self, widget, duration=250, steps=20, direction='down'):
        if not widget or not widget.winfo_exists():
            return

        try:
            # A veil with the container's background color is placed over the widget
            # and its height (or width) is animated to zero, revealing the widget.
            container_style = widget.master.cget('style') or 'TFrame'
            veil_color = self.app_style.lookup(container_style, 'background')

            # Create the veil
            veil = tk.Frame(widget.master, background=veil_color, borderwidth=0)

            # Place the veil exactly on top of the widget.
            self.update_idletasks()
            x, y, w, h = widget.winfo_x(), widget.winfo_y(), widget.winfo_width(), widget.winfo_height()
            if w <= 1 or h <= 1: return

            veil.place(x=x, y=y, width=w, height=h)
            veil.lift(widget)

            delay = duration // steps

            def _animate_step(step_num=1):
                if step_num <= steps:
                    # Use an easing function for a smoother effect
                    t = step_num / steps
                    ease_t = 1 - (1 - t)**3 # easeOutCubic

                    if direction == 'down':
                        current_h = h * (1 - ease_t)
                        veil.place_configure(height=current_h)
                    # Can add other directions like 'up', 'left', 'right' later
                    
                    self.after(delay, lambda: _animate_step(step_num + 1))
                elif veil.winfo_exists(): veil.destroy()
            _animate_step()
        except Exception as e:
            log_crash("Reveal animation failed", e)
            if 'veil' in locals() and isinstance(veil, tk.Widget) and veil.winfo_exists(): veil.destroy()

    def animate_page_transition(self, new_page_frame, direction="left", on_complete=None):
        old_page_frame = self.current_page_frame
        if old_page_frame == new_page_frame or self.is_transitioning:
            if on_complete:
                on_complete()
            return

        self.is_transitioning = True

        # Place the new page off-screen
        start_x = 1 if direction == "left" else -1
        new_page_frame.place(relx=start_x, rely=0, relwidth=1, relheight=1)
        new_page_frame.tkraise()

        duration = 400  # ms
        steps = 25
        step_delay = duration // steps

        old_page_start_x = 0
        new_page_start_x = start_x
        old_page_end_x = -start_x
        new_page_end_x = 0

        def _animate_step(step_num=1):
            if step_num <= steps:
                # Easing function (ease-out-quad) for a smoother effect
                t = step_num / steps
                ease_t = 1 - (1 - t) ** 4 # easeOutQuart

                old_x = old_page_start_x + (old_page_end_x - old_page_start_x) * ease_t
                new_x = new_page_start_x + (new_page_end_x - new_page_start_x) * ease_t

                if old_page_frame and old_page_frame.winfo_exists():
                    old_page_frame.place(relx=old_x, rely=0, relwidth=1, relheight=1)
                if new_page_frame and new_page_frame.winfo_exists():
                    new_page_frame.place(relx=new_x, rely=0, relwidth=1, relheight=1)

                self.after(step_delay, lambda: _animate_step(step_num + 1))
            else:
                # Final placement to ensure it's perfectly aligned
                if new_page_frame and new_page_frame.winfo_exists():
                    new_page_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
                # Hide old page completely
                if old_page_frame and old_page_frame.winfo_exists():
                    old_page_frame.place_forget()
                
                self.is_transitioning = False
                if on_complete:
                    on_complete()

        _animate_step()
        self.current_page_frame = new_page_frame

    def load_achievements(self):
        """Loads achievements from a JSON file, creating it if it doesn't exist."""
        # Define the default achievements structure here.
        # This ensures the application can always function and can create the file if missing.
        DEFAULT_ACHIEVEMENTS = {
            "achievement_7": {"name": "Le Débutant", "desc": "Lancer votre tout premier jeu.", "unlocked_key": "achievement_7_unlocked", "icon_unlocked": "🚀", "icon_locked": "🔒", "difficulty": 1},
            "achievement_3": {"name": "Le Touche-à-tout", "desc": "Changer le thème de l'application.", "unlocked_key": "achievement_3_unlocked", "icon_unlocked": "🎨", "icon_locked": "🔒", "difficulty": 2},
            "achievement_chercheur": {"name": "Le Chercheur", "desc": "Utiliser la recherche.", "unlocked_key": "achievement_chercheur_unlocked", "icon_unlocked": "🔎", "icon_locked": "🔒", "difficulty": 3},
            "achievement_favori": {"name": "Le Favori", "desc": "Avoir marqué un jeu comme favori.", "unlocked_key": "achievement_favori_unlocked", "icon_unlocked": "⭐", "icon_locked": "🔒", "difficulty": 4},
            "achievement_12": {"name": "L'Explorateur", "desc": "Scanner le dossier des jeux pour en trouver de nouveaux.", "unlocked_key": "achievement_12_unlocked", "icon_unlocked": "🧭", "icon_locked": "🔒", "difficulty": 5},
            "achievement_identity_change": {"name": "Changement d'Identité", "desc": "Changer votre nom d'utilisateur.", "unlocked_key": "achievement_identity_change_unlocked", "icon_unlocked": "🎭", "icon_locked": "🔒", "difficulty": 5},
            "achievement_5": {"name": "Le Collectionneur", "desc": "Ajouter un nouveau jeu manuellement.", "unlocked_key": "achievement_5_unlocked", "icon_unlocked": "🎁", "icon_locked": "🔒", "difficulty": 6},
            "achievement_mode_liste": {"name": "Mode Liste", "desc": "Utiliser l'affichage Liste.", "unlocked_key": "achievement_mode_liste_unlocked", "icon_unlocked": "📋", "icon_locked": "🔒", "difficulty": 7},
            "achievement_8": {"name": "Le Bricoleur", "desc": "Modifier les détails d'un jeu.", "unlocked_key": "achievement_8_unlocked", "icon_unlocked": "✍️", "icon_locked": "🔒", "difficulty": 8},
            "achievement_11": {"name": "Le Nettoyeur", "desc": "Réinitialiser le fond d'écran par défaut.", "unlocked_key": "achievement_11_unlocked", "icon_unlocked": "🧹", "icon_locked": "🔒", "difficulty": 9},
            "achievement_spotlight": {"name": "Sous les Projecteurs", "desc": "Lancer un jeu depuis la section 'Suggestion'.", "unlocked_key": "achievement_spotlight_unlocked", "icon_unlocked": "💡", "icon_locked": "🔒", "difficulty": 10},
            "achievement_14": {"name": "Le Grand Voyageur", "desc": "Visiter toutes les pages de l'application.", "unlocked_key": "achievement_14_unlocked", "icon_unlocked": "🗺️", "icon_locked": "🔒", "difficulty": 11},
            "achievement_curieux": {"name": "Le Curieux", "desc": "Lire un conseil du jour.", "unlocked_key": "achievement_curieux_unlocked", "icon_unlocked": "💡", "icon_locked": "🔒", "difficulty": 1},
            "achievement_depanneur": {"name": "Le Dépanneur", "desc": "Ouvrir le fichier de log de crash.", "unlocked_key": "achievement_depanneur_unlocked", "icon_unlocked": "🛠️", "icon_locked": "🔒", "difficulty": 2},
            "achievement_architecte": {"name": "L'Architecte", "desc": "Ouvrir le dossier des paramètres.", "unlocked_key": "achievement_architecte_unlocked", "icon_unlocked": "🏗️", "icon_locked": "🔒", "difficulty": 2},
            "achievement_maitre_style": {"name": "Maître du Style", "desc": "Changer la taille de la police.", "unlocked_key": "achievement_maitre_style_unlocked", "icon_unlocked": "✒️", "icon_locked": "🔒", "difficulty": 16},
            "achievement_arrondir_angles": {"name": "Arrondir les Angles", "desc": "Changer le rayon des bordures.", "unlocked_key": "achievement_arrondir_angles_unlocked", "icon_unlocked": "✨", "icon_locked": "🔒", "difficulty": 17},
            "achievement_personnalisateur": {"name": "Le Personnalisateur", "desc": "Modifier un paramètre d'apparence.", "unlocked_key": "achievement_personnalisateur_unlocked", "icon_unlocked": "🖌️", "icon_locked": "🔒", "difficulty": 4},
            "achievement_tri_za": {"name": "Le Contrarieur", "desc": "Trier les jeux de Z à A.", "unlocked_key": "achievement_tri_za_unlocked", "icon_unlocked": "🔄", "icon_locked": "🔒", "difficulty": 3},
            "achievement_duplicateur": {"name": "Le Cloneur", "desc": "Dupliquer un jeu.", "unlocked_key": "achievement_duplicateur_unlocked", "icon_unlocked": "👯", "icon_locked": "🔒", "difficulty": 15},
            "achievement_detective": {"name": "Le Détective", "desc": "Ouvrir les logs et les paramètres dans la même session.", "unlocked_key": "achievement_detective_unlocked", "icon_unlocked": "🕵️", "icon_locked": "🔒", "difficulty": 16},
            "achievement_grand_tour": {"name": "Le Grand Tour", "desc": "Visiter les pages Profil, Stats et Suggestions.", "unlocked_key": "achievement_grand_tour_unlocked", "icon_unlocked": "🌍", "icon_locked": "🔒", "difficulty": 12},
            "achievement_minimaliste": {"name": "Le Minimaliste", "desc": "Supprimer 5 jeux de la bibliothèque.", "unlocked_key": "achievement_minimaliste_unlocked", "icon_unlocked": "🗑️", "icon_locked": "🔒", "difficulty": 15},
            "achievement_fidele": {"name": "Le Fidèle", "desc": "Lancer l'application 7 jours différents.", "unlocked_key": "achievement_fidele_unlocked", "icon_unlocked": "📅", "icon_locked": "🔒", "difficulty": 20},
            "achievement_zappeur": {"name": "Le Zappeur", "desc": "Lancer 3 jeux différents dans la même session.", "unlocked_key": "achievement_zappeur_unlocked", "icon_unlocked": "⚡", "icon_locked": "🔒", "difficulty": 12},
            "achievement_2": {"name": "Le Joueur", "desc": "Lancer 10 jeux différents.", "unlocked_key": "achievement_2_unlocked", "icon_unlocked": "🎮", "icon_locked": "🔒", "difficulty": 13},
            "achievement_15": {"name": "L'Organisateur", "desc": "Avoir au moins 10 jeux dans la liste.", "unlocked_key": "achievement_15_unlocked", "icon_unlocked": "📚", "icon_locked": "🔒", "difficulty": 14},
            "achievement_5_favoris": {"name": "Collection de Favoris", "desc": "Avoir 5 jeux en favoris.", "unlocked_key": "achievement_5_favoris_unlocked", "icon_unlocked": "🌟", "icon_locked": "🔒", "difficulty": 15},
            "achievement_16": {"name": "La Plume Créative", "desc": "Ajouter une description personnalisée pour un jeu.", "unlocked_key": "achievement_16_unlocked", "icon_unlocked": "✒️", "icon_locked": "🔒", "difficulty": 16},
            "achievement_critique": {"name": "Le Critique", "desc": "Ajouter une description à 5 jeux différents.", "unlocked_key": "achievement_critique_unlocked", "icon_unlocked": "🖋️", "icon_locked": "🔒", "difficulty": 17},
            "achievement_17": {"name": "L'Icône Personnalisée", "desc": "Attribuer une icône personnalisée à un jeu.", "unlocked_key": "achievement_17_unlocked", "icon_unlocked": "🖌️", "icon_locked": "🔒", "difficulty": 18},
            "achievement_archiviste": {"name": "L'Archiviste", "desc": "Avoir classifié un jeu avec au moins une catégorie.", "unlocked_key": "achievement_archiviste_unlocked", "icon_unlocked": "🗂️", "icon_locked": "🔒", "difficulty": 19},
            "achievement_grand_nettoyage": {"name": "Le Grand Nettoyage", "desc": "Utiliser 3 outils de maintenance différents.", "unlocked_key": "achievement_grand_nettoyage_unlocked", "icon_unlocked": "🧼", "icon_locked": "🔒", "difficulty": 20},
            "achievement_curateur": {"name": "Le Curateur", "desc": "Avoir 5 jeux avec au moins une catégorie.", "unlocked_key": "achievement_curateur_unlocked", "icon_unlocked": "🗃️", "icon_locked": "🔒", "difficulty": 21},
            "achievement_bibliothecaire": {"name": "Le Bibliothécaire", "desc": "Avoir au moins 5 catégories différentes.", "unlocked_key": "achievement_bibliothecaire_unlocked", "icon_unlocked": "🗃️", "icon_locked": "🔒", "difficulty": 22},
            "achievement_connoisseur": {"name": "Le Connaisseur", "desc": "Lancer 5 fois le même jeu.", "unlocked_key": "achievement_connoisseur_unlocked", "icon_unlocked": "🧐", "icon_locked": "🔒", "difficulty": 23},
            "achievement_night_owl": {"name": "Le Noctambule", "desc": "Lancer un jeu entre 22h et 4h.", "unlocked_key": "achievement_night_owl_unlocked", "icon_unlocked": "🦉", "icon_locked": "🔒", "difficulty": 24},
            "achievement_taxonomiste": {"name": "Le Taxonomiste", "desc": "Utiliser le gestionnaire de catégories.", "unlocked_key": "achievement_taxonomiste_unlocked", "icon_unlocked": "🏷️", "icon_locked": "🔒", "difficulty": 15},
            "achievement_polyglotte": {"name": "Le Polyglotte", "desc": "Changer de thème 5 fois.", "unlocked_key": "achievement_polyglotte_unlocked", "icon_unlocked": "✨", "icon_locked": "🔒", "difficulty": 25},
            "achievement_bibliophile": {"name": "Le Bibliophile", "desc": "Posséder 25 jeux dans sa bibliothèque.", "unlocked_key": "achievement_bibliophile_unlocked", "icon_unlocked": "🏛️", "icon_locked": "🔒", "difficulty": 26},
            "achievement_13": {"name": "L'Addict", "desc": "Lancer un total de 50 jeux.", "unlocked_key": "achievement_13_unlocked", "icon_unlocked": "🕹️", "icon_locked": "🔒", "difficulty": 27},
            "achievement_10_favoris": {"name": "Galaxie de Favoris", "desc": "Avoir 10 jeux en favoris.", "unlocked_key": "achievement_10_favoris_unlocked", "icon_unlocked": "🌠", "icon_locked": "🔒", "difficulty": 28},
            "achievement_marathonien": {"name": "Le Marathonien", "desc": "Atteindre 1h de jeu au total.", "unlocked_key": "achievement_marathonien_unlocked", "icon_unlocked": "⏱️", "icon_locked": "🔒", "difficulty": 29},
            "achievement_session_xl": {"name": "Session XL", "desc": "Jouer 30 minutes d'affilée sur un jeu.", "unlocked_key": "achievement_session_xl_unlocked", "icon_unlocked": "⌛", "icon_locked": "🔒", "difficulty": 30},
            "achievement_oiseau_de_nuit": {"name": "L'Oiseau de Nuit", "desc": "Lancer un jeu entre 2h et 4h du matin.", "unlocked_key": "achievement_oiseau_de_nuit_unlocked", "icon_unlocked": "🦇", "icon_locked": "🔒", "difficulty": 31},
            "achievement_pro_themes": {"name": "Le Pro des Thèmes", "desc": "Changer de thème 10 fois.", "unlocked_key": "achievement_pro_themes_unlocked", "icon_unlocked": "🌈", "icon_locked": "🔒", "difficulty": 32},
            "achievement_maitre_icones": {"name": "Le Maître des Icônes", "desc": "Attribuer une icône personnalisée à 10 jeux.", "unlocked_key": "achievement_maitre_icones_unlocked", "icon_unlocked": "🖼️", "icon_locked": "🔒", "difficulty": 33},
            "achievement_grand_archiviste": {"name": "Le Grand Archiviste", "desc": "Classifier 15 jeux avec au moins une catégorie.", "unlocked_key": "achievement_grand_archiviste_unlocked", "icon_unlocked": "🗄️", "icon_locked": "🔒", "difficulty": 34},
            "achievement_perfection": {"name": "Le Perfectionniste", "desc": "Avoir 15 jeux avec icône et description personnalisées.", "unlocked_key": "achievement_perfection_unlocked", "icon_unlocked": "🏆", "icon_locked": "🔒", "difficulty": 35},
            "achievement_ultime_joueur": {"name": "L'Ultime Joueur", "desc": "Lancer un total de 100 jeux.", "unlocked_key": "achievement_ultime_joueur_unlocked", "icon_unlocked": "🏅", "icon_locked": "🔒", "difficulty": 36},
            "achievement_gardien_temps": {"name": "Le Gardien du Temps", "desc": "Atteindre 5 heures de jeu au total.", "unlocked_key": "achievement_gardien_temps_unlocked", "icon_unlocked": "⏳", "icon_locked": "🔒", "difficulty": 37},
            "achievement_legende": {"name": "La Légende", "desc": "Posséder 50 jeux dans sa bibliothèque.", "unlocked_key": "achievement_legende_unlocked", "icon_unlocked": "📜", "icon_locked": "🔒", "difficulty": 38},
            "achievement_devotion": {"name": "Dévotion", "desc": "Lancer 10 fois le même jeu.", "unlocked_key": "achievement_devotion_unlocked", "icon_unlocked": "🛐", "icon_locked": "🔒", "difficulty": 39},
            "achievement_maitre_du_temps": {"name": "Le Maître du Temps", "desc": "Atteindre 10 heures de jeu au total.", "unlocked_key": "achievement_maitre_du_temps_unlocked", "icon_unlocked": "🕰️", "icon_locked": "🔒", "difficulty": 40},
            "achievement_insomniaque": {"name": "L'Insomniaque", "desc": "Lancer un jeu après minuit 5 jours différents.", "unlocked_key": "achievement_insomniaque_unlocked", "icon_unlocked": "☕", "icon_locked": "🔒", "difficulty": 41},
            "achievement_collectionneur_ultime": {"name": "Le Collectionneur Ultime", "desc": "Avoir 25 jeux en favoris.", "unlocked_key": "achievement_collectionneur_ultime_unlocked", "icon_unlocked": "🌌", "icon_locked": "🔒", "difficulty": 42},
            "achievement_1": {"name": "Le Fouineur", "desc": "Trouvé l'Easter Egg secret.", "unlocked_key": "achievement_1_unlocked", "icon_unlocked": "🤫", "icon_locked": "🔒", "difficulty": 98},
            "achievement_profile_view": {"name": "Curieux du Profil", "desc": "Visiter la page Profil.", "unlocked_key": "achievement_profile_view_unlocked", "icon_unlocked": "👤", "icon_locked": "🔒", "difficulty": 2},
            "achievement_stats_view": {"name": "Analyste", "desc": "Consulter la page Statistiques.", "unlocked_key": "achievement_stats_view_unlocked", "icon_unlocked": "📊", "icon_locked": "🔒", "difficulty": 3},
            "achievement_suggestion": {"name": "Redécouverte", "desc": "Lancer un jeu depuis Suggestions.", "unlocked_key": "achievement_suggestion_unlocked", "icon_unlocked": "🔁", "icon_locked": "🔒", "difficulty": 4},
            "achievement_exporteur": {"name": "Archiviste", "desc": "Exporter la base de données.", "unlocked_key": "achievement_exporteur_unlocked", "icon_unlocked": "📤", "icon_locked": "🔒", "difficulty": 5},
            "achievement_importateur": {"name": "Restaurateur", "desc": "Importer une base de données.", "unlocked_key": "achievement_importateur_unlocked", "icon_unlocked": "📥", "icon_locked": "🔒", "difficulty": 6},
            "achievement_backup": {"name": "Sauvegarde", "desc": "Créer une sauvegarde de la base.", "unlocked_key": "achievement_backup_unlocked", "icon_unlocked": "💾", "icon_locked": "🔒", "difficulty": 4},
            "achievement_repair_data": {"name": "Réparateur", "desc": "Réparer/normaliser la base de données.", "unlocked_key": "achievement_repair_data_unlocked", "icon_unlocked": "🛠️", "icon_locked": "🔒", "difficulty": 6},
            "achievement_mark_missing": {"name": "Traqueur", "desc": "Marquer les jeux introuvables.", "unlocked_key": "achievement_mark_missing_unlocked", "icon_unlocked": "📍", "icon_locked": "🔒", "difficulty": 4},
            "achievement_deduplicate": {"name": "Zéro Doublons", "desc": "Dédoublonner la bibliothèque.", "unlocked_key": "achievement_deduplicate_unlocked", "icon_unlocked": "🧹", "icon_locked": "🔒", "difficulty": 5},
            "achievement_fix_icons": {"name": "Styliste", "desc": "Réparer les icônes manquantes.", "unlocked_key": "achievement_fix_icons_unlocked", "icon_unlocked": "🖼️", "icon_locked": "🔒", "difficulty": 4},
            "achievement_ui_polish": {"name": "La Finition", "desc": "Appliquer une option d'apparence (polish UI).", "unlocked_key": "achievement_ui_polish_unlocked", "icon_unlocked": "✨", "icon_locked": "🔒", "difficulty": 2},
            "achievement_collectionneur_complet": {"name": "Le Collectionneur Complet", "desc": "Débloquer tous les autres succès.", "unlocked_key": "achievement_collectionneur_complet_unlocked", "icon_unlocked": "👑", "icon_locked": "🔒", "difficulty": 99},
            "achievement_maniaque": {"name": "Le Maniaque", "desc": "Avoir une bibliothèque sans aucun jeu introuvable.", "unlocked_key": "achievement_maniaque_unlocked", "icon_unlocked": "✨", "icon_locked": "🔒", "difficulty": 25},
            "achievement_explorateur_ultime": {"name": "L'Explorateur Ultime", "desc": "Posséder plus de 20 jeux dans la bibliothèque.", "unlocked_key": "achievement_explorateur_ultime_unlocked", "icon_unlocked": "🗺️", "icon_locked": "🔒", "difficulty": 22},
            "achievement_maitre_du_hasard": {"name": "Maître du Hasard", "desc": "Lancer un jeu aléatoire 10 fois.", "unlocked_key": "achievement_maitre_du_hasard_unlocked", "icon_unlocked": "🎲", "icon_locked": "🔒", "difficulty": 18}
        }
        
        DEFAULT_ACHIEVEMENTS["achievement_critic"] = {"name": "Le Critique", "desc": "Noter un jeu pour la première fois.", "unlocked_key": "achievement_critic_unlocked", "icon_unlocked": "🌟", "icon_locked": "🔒", "difficulty": 5}
        DEFAULT_ACHIEVEMENTS["achievement_portable"] = {"name": "Le Nomade", "desc": "Lancer l'application en mode portable.", "unlocked_key": "achievement_portable_unlocked", "icon_unlocked": "🎒", "icon_locked": "🔒", "difficulty": 10}
        DEFAULT_ACHIEVEMENTS["achievement_updater"] = {"name": "Le Visionnaire", "desc": "Vérifier s'il y a une nouvelle mise à jour.", "unlocked_key": "achievement_updater_unlocked", "icon_unlocked": "🚀", "icon_locked": "🔒", "difficulty": 6}

        if not os.path.exists(ACHIEVEMENTS_FILE):
            try:
                with open(ACHIEVEMENTS_FILE, "w", encoding="utf-8") as f:
                    json.dump(DEFAULT_ACHIEVEMENTS, f, indent=4, ensure_ascii=False)
                return DEFAULT_ACHIEVEMENTS
            except Exception as e:
                log_crash("Failed to create default achievements.json", e)
                return DEFAULT_ACHIEVEMENTS # Return default on creation failure
        
        # File exists, try to load it
        try:
            with open(ACHIEVEMENTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Basic validation: check if it's a dictionary
            if not isinstance(data, dict):
                log_crash("achievements.json is corrupted (not a dictionary), using defaults.", None)
                return DEFAULT_ACHIEVEMENTS
            return data
        except (json.JSONDecodeError, IOError) as e:
            log_crash(f"Failed to load or parse achievements.json, using defaults.", e)
            return DEFAULT_ACHIEVEMENTS

    def _create_gradient_photo(self, color1, color2, width, height):
        cache_key = (color1, color2, width, height)
        if cache_key in self.gradient_cache:
            return self.gradient_cache[cache_key]

        img = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(img)
        r1, g1, b1 = self.winfo_rgb(color1)
        r2, g2, b2 = self.winfo_rgb(color2)
        for i in range(height):
            r = int(r1/256 + (r2/256 - r1/256) * i / height)
            g = int(g1/256 + (g2/256 - g1/256) * i / height)
            b = int(b1/256 + (b2/256 - b1/256) * i / height)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        photo = ImageTk.PhotoImage(img)
        self.gradient_cache[cache_key] = photo
        return photo

    def _apply_appearance_settings(self):
        """Applies font size and corner radius settings by re-initializing styles."""
        try:
            self._init_styles()
            # Mark all pages as dirty to force a full redraw with new styles
            for page in self.page_map.keys():
                self._mark_dirty([page])
            
            # Trigger an update on the current page
            current_page_name = self.get_page_name(self.current_page_frame)
            self.show_page(current_page_name)
        except Exception as e:
            log_crash("Failed to apply new appearance settings", e)

    def _adjust_color(self, color_hex, factor):
        """Lightens or darkens a color. factor > 1 lightens, < 1 darkens."""
        if not color_hex.startswith('#'):
            # Handle named colors by converting them to hex first
            try:
                rgb = self.winfo_rgb(color_hex) # returns 16-bit values
                r, g, b = (c >> 8 for c in rgb) # convert to 8-bit
            except tk.TclError:
                r, g, b = 128, 128, 128 # fallback grey
        else:
            r, g, b = int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16)
        
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    # --- Setup & Initialization ---
    def _load_theme(self):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("theme", "darkly")
        except Exception:
            return "darkly"

    def _init_styles(self):
        try: # Get colors from theme to ensure consistency
            bg_color = self.app_style.lookup("TFrame", "background")
            fg_color = self.app_style.lookup("TLabel", "foreground")
            
            theme_name = self.settings.get("theme")
            custom_colors = self.settings.get("custom_theme_colors", {})
            
            if theme_name == "custom" and custom_colors:
                primary_color = custom_colors.get('primary', self.app_style.colors.primary)
                secondary_color = custom_colors.get('secondary', self.app_style.colors.secondary)
                light_color = custom_colors.get('light', self.app_style.colors.light)
                dark_color = custom_colors.get('dark', self.app_style.colors.dark)
            else:
                primary_color = self.app_style.colors.primary
                secondary_color = self.app_style.colors.secondary
                light_color = self.app_style.colors.light
                dark_color = self.app_style.colors.dark

        except Exception: # Fallback colors in case of error.
            bg_color, fg_color, primary_color, secondary_color, light_color, dark_color = "#2a2a2a", "#ffffff", "#0d6efd", "#6c757d", "#f8f9fa", "#343a40"

        font_size_map = {"Petit": 9, "Moyen": 11, "Grand": 13}
        base_font_size = font_size_map.get(self.font_size_var.get(), 11)
        
        # Apply global font size
        self.app_style.configure('.', font=('Segoe UI', base_font_size))

        # Apply corner radius to buttons
        self.app_style.configure("TButton", font=("Segoe UI", base_font_size, "bold"), padding=(15, 10), relief="flat", borderwidth=0, focuscolor="none", borderradius=self.corner_radius_var.get())
        self.app_style.configure("Content.TFrame", background=bg_color)
        self.app_style.configure("Card.TFrame", background=dark_color, borderwidth=0, relief="flat")

        hover_color = self._adjust_color(dark_color, 1.2) # Lighten by 20% for hover
        self.app_style.configure("GameCard.TFrame", background=dark_color, borderwidth=1, relief="solid", bordercolor="#444")
        self.app_style.map("GameCard.TFrame",
            background=[('hover', hover_color)],
            bordercolor=[('hover', primary_color), ('!hover', '#444')],
            relief=[('hover', 'raised'), ('!hover', 'solid')]
        )

        label_styles = {
            "TLabel": {"font": ('Segoe UI', base_font_size), "foreground": fg_color, "background": bg_color},
            "Header.TLabel": {"font": ('Segoe UI', base_font_size + 15, "bold"), "foreground": light_color, "background": bg_color},
            "Section.TLabel": {"font": ('Segoe UI', base_font_size + 5, "bold"), "foreground": light_color, "background": bg_color},
            "CardTitle.TLabel": {"font": ('Segoe UI', base_font_size + 4, "bold"), "foreground": light_color, "background": dark_color},
            "Card.TLabel": {"font": ('Segoe UI', base_font_size + 1), "foreground": fg_color, "background": dark_color},
            "GameCard.TLabel": {"font": ('Segoe UI', base_font_size + 1), "foreground": light_color, "background": dark_color},
            "GameCard.Desc.TLabel": {"font": ('Segoe UI', base_font_size - 1), "foreground": secondary_color, "background": dark_color},
            "Category.TLabel": {"font": ('Segoe UI', base_font_size - 3, "italic"), "foreground": secondary_color, "background": dark_color},
            "Invalid.TLabel": {"font": ("Segoe UI", 8, "italic"), "foreground": self.app_style.colors.danger, "background": dark_color},
            "Disabled.TLabel": {"font": ('Segoe UI', base_font_size - 1), "foreground": secondary_color, "background": dark_color},
            "Spotlight.TLabel": {"font": ('Segoe UI', base_font_size, "italic"), "foreground": fg_color, "background": dark_color},
            "Tip.TLabel": {"font": ('Segoe UI', base_font_size - 1, "italic"), "foreground": fg_color, "background": bg_color},
            "SidebarLogo.TLabel": {"font": ('Segoe UI', base_font_size + 11, "bold"), "foreground": "#ffffff", "background": "#1c1c1c"},
            "SidebarInfo.TLabel": {"font": ('Segoe UI', base_font_size - 1), "foreground": secondary_color, "background": "#1c1c1c"},
        }

        for style_name, config in label_styles.items():
            self.app_style.configure(style_name, font=config["font"], foreground=config["foreground"], background=config["background"]) # Applying styles to labels.
            self.app_style.map(style_name,
                foreground=[('!active', config["foreground"]), ('active', config["foreground"]), ('focus', config["foreground"]), ('hover', config["foreground"]), ('disabled', secondary_color)],
                background=[('!active', config["background"]), ('active', config["background"]), ('focus', config["background"]), ('hover', config["background"]), ('disabled', config["background"])]
            )

        sidebar_bg = "#1c1c1c"
        sidebar_fg = "#e0e0e0"
        sidebar_active_bg = "#333333"
        self.app_style.configure("Sidebar.TFrame", background=sidebar_bg, borderradius=0)
        self.app_style.configure("Sidebar.TButton", font=('Segoe UI', base_font_size + 2), foreground=sidebar_fg, background=sidebar_bg, borderwidth=0, focusthickness=0, anchor="w", relief="flat", padding=(15, 10))
        self.app_style.map("Sidebar.TButton",
            background=[("active", sidebar_active_bg), ("hover", sidebar_active_bg), ("!active", sidebar_bg)],
            foreground=[("active", "#ffffff"), ("!active", sidebar_fg)]
        )
        self.app_style.configure("Sidebar.Active.TButton", font=('Segoe UI', base_font_size + 2, "bold"), foreground="#ffffff", background=primary_color, borderwidth=0, focusthickness=0, anchor="w", relief="flat", padding=(15, 10))
        self.app_style.map("Sidebar.Active.TButton",
            background=[("!active", primary_color), ("hover", primary_color)]
        )

        self.app_style.configure("Favorite.TButton", font=("Segoe UI", 14), padding=0, relief="flat", borderwidth=0, focuscolor="none", background=dark_color)
        self.app_style.map("Favorite.TButton", foreground=[('active', primary_color), ('pressed', primary_color), ('hover', primary_color)]) # Style for Favorite Button
        self.app_style.configure("Gold.TButton", foreground=self.app_style.colors.warning, background=dark_color, borderradius=self.corner_radius_var.get())
        self.app_style.configure("Custom.TLabelframe", padding=20, relief="solid", borderwidth=1, bordercolor=dark_color, borderradius=self.corner_radius_var.get())
        self.app_style.configure("Custom.TLabelframe.Label", font=('Segoe UI', base_font_size + 1, "bold"), foreground=fg_color, background=bg_color)
        self.app_style.configure("Spotlight.TFrame", padding=20, relief="flat", borderwidth=0)
        
        self.app_style.configure("FavFilter.TCheckbutton", font=('Segoe UI', base_font_size - 1), indicatorrelief="flat", indicatormargin=0, padding=0)
        self.app_style.map("FavFilter.TCheckbutton",
            indicatorcolor=[("selected", primary_color), ("!selected", dark_color)], # Style for Favourite Filter Button
            foreground=[("hover", primary_color)]
        )

        # Styles for unlocked achievements
        success_color = self.app_style.colors.success
        # Assuming a light text color is best on the success background
        self.app_style.configure("success.TFrame", background=success_color)
        self.app_style.configure("success.TLabel", foreground=self.app_style.colors.light, background=success_color)

    def ensure_directories(self):
        for folder in [GAMES_FOLDER, IMAGES_FOLDER, SETTINGS_FOLDER]: # Ensure SETTINGS_FOLDER is created
            if not os.path.exists(folder):
                os.makedirs(folder)

    # --- Game Filtering and Actions ---
    def filter_games(self, event=None, animate=True):
        search_term = self.search_entry.get().lower()
        show_favs = self.show_favorites_only.get()
        category = self.category_filter.get()
        collection = self.collection_filter.get()

        if search_term: # Unlock achievement when user searches
            self.check_and_unlock_achievement("achievement_chercheur")

        self.filtered_games = []
        with self.games_lock:
            games_copy = list(self.games)

        for game in games_copy:
            if game.get("deleted"):
                continue

            name_match = search_term in game.get("name", "").lower()
            desc_match = search_term in game.get("description", "").lower() # Filter games

            if not (name_match or desc_match):
                continue

            if show_favs and not game.get("favorite"):
                continue

            if category != "Toutes" and category not in game.get("categories", []):
                continue

            if collection != "Toutes" and (collection not in self.collections or game['path'] not in self.collections[collection]):
                continue
            
            self.filtered_games.append(game)

        sort_map = {
            "Nom (A-Z)": ("name", False),
            "Nom (Z-A)": ("name", True),
            "Plus joué": ("launch_count", True),
            "Moins joué": ("launch_count", False),
            "Plus récent": ("last_launched", True),
            "Plus ancien": ("last_launched", False),
            "Mieux noté": ("rating", True),
            "Moins bien noté": ("rating", False),
        }
        sort_key, reverse = sort_map.get(self.sort_order.get(), ("name", False))
        
        if sort_key == "last_launched":
            # Handle None values for last_launched
            self.filtered_games.sort(key=lambda g: g.get(sort_key) or "0", reverse=reverse)
        else:
            self.filtered_games.sort(key=lambda g: g.get(sort_key, 0), reverse=reverse)

        if self.sort_order.get() == "Nom (Z-A)":
            self.check_and_unlock_achievement("achievement_tri_za")

        self.update_game_cards(animate=animate)

    def debounced_filter_games(self, event=None):
        if self.search_timer:
            self.after_cancel(self.search_timer)
            self.search_timer = None

        # Si la touche Entrée est pressée, lancer la recherche immédiatement.
        if event and event.keysym == 'Return':
            self.filter_games()
        # Sinon, utiliser le délai habituel.
        else:
            self.search_timer = self.after(300, self.filter_games)

    def clear_filters(self):
        self.search_entry.delete(0, tk.END)
        self.show_favorites_only.set(False)
        self.category_filter.set("Toutes")
        self.filter_games()

    # --- UI Creation ---
    def create_sidebar(self):
        sidebar_logo = ttk.Label(self.sidebar_frame, text=APP_NAME, style="SidebarLogo.TLabel")
        sidebar_logo.pack(pady=(20, 10), padx=10)

        main_nav = [("Accueil", "main"), ("Jeux", "games"), ("Succès", "achievements"), ("Paramètres", "settings")] # Added bootstyle="round"
        for text, page in main_nav:
            btn = ttk.Button(self.sidebar_frame, text=text, style="Sidebar.TButton", command=lambda p=page: self.show_page(p))
            btn.pack(fill="x", pady=6, padx=12)
            self.sidebar_buttons[page] = btn

        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill="x", padx=12, pady=12)

        btn = ttk.Button(self.sidebar_frame, text="Aperçu", style="Sidebar.TButton", command=lambda: self.show_page("pro"))
        btn.pack(fill="x", pady=4, padx=12)
        self.sidebar_buttons["pro"] = btn

        self.sidebar_user_label = ttk.Label(self.sidebar_frame, text=self.get_username(), style="SidebarInfo.TLabel")
        self.sidebar_user_label.pack(pady=(6, 2), padx=12)
        ttk.Button(self.sidebar_frame, text="Quitter", bootstyle="danger-outline", command=self.destroy).pack(fill="x", pady=(6, 20), padx=12)

    def create_main_page(self):
        self.main_page_frame.grid_columnconfigure(0, weight=1)
        self.main_page_frame.grid_rowconfigure(1, weight=1)

        header_frame = ttk.Frame(self.main_page_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=30, pady=(30, 20))
        self.welcome_label = ttk.Label(header_frame, text=self.get_welcome_message(), font=("Segoe UI", 26, "bold"))
        self.welcome_label.pack(side="left") # Added bootstyle="round" to the random game button
        ttk.Button(header_frame, text="Lancer un jeu au hasard", command=self.lancer_jeu_aleatoire, bootstyle="success-outline").pack(side="right")

        content_grid = ttk.Frame(self.main_page_frame)
        content_grid.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        content_grid.grid_columnconfigure(0, weight=3, uniform="main")
        content_grid.grid_columnconfigure(1, weight=2, uniform="main")
        content_grid.grid_rowconfigure(0, weight=1)

        # --- Left Column ---
        left_col = ttk.Frame(content_grid)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        left_col.grid_rowconfigure(0, weight=1)
        left_col.grid_rowconfigure(1, weight=1)
        left_col.grid_columnconfigure(0, weight=1)

        # Dashboard
        dashboard_frame = ttk.Labelframe(left_col, text="Tableau de bord", style="Custom.TLabelframe")
        dashboard_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        dashboard_frame.grid_columnconfigure([0, 1], weight=1)
        dashboard_frame.grid_rowconfigure([0, 1], weight=1)
        
        self.total_games_label, card_games = self.create_dashboard_card(dashboard_frame, "Jeux", "0", 0, 0)
        card_games.bind("<Button-1>", lambda e: self.show_page("games"))
        self.playtime_label, card_playtime = self.create_dashboard_card(dashboard_frame, "Temps de jeu", "0h 0m", 0, 1)
        card_playtime.bind("<Button-1>", lambda e: self.go_to_pro_tab(1))
        self.achievements_label, card_achievements = self.create_dashboard_card(dashboard_frame, "Succès", "0/0", 1, 0)
        card_achievements.bind("<Button-1>", lambda e: self.show_page("achievements"))
        self.most_played_label, card_most_played = self.create_dashboard_card(dashboard_frame, "Le plus joué", "N/A", 1, 1)
        card_most_played.bind("<Button-1>", lambda e: self.show_page("games"))


        # Spotlight
        self.spotlight_frame = ttk.Labelframe(left_col, text="À la une", style="Custom.TLabelframe")
        self.spotlight_frame.grid(row=1, column=0, sticky="nsew")
        self.spotlight_frame.grid_columnconfigure(0, weight=1)
        self.spotlight_frame.grid_rowconfigure(0, weight=1)

        # --- Right Column ---
        right_col = ttk.Frame(content_grid)
        right_col.grid(row=0, column=1, sticky="nsew")
        right_col.grid_rowconfigure(0, weight=1)
        right_col.grid_columnconfigure(0, weight=1)

        # Tip of the day
        tip_frame = ttk.Labelframe(right_col, text="💡 Conseil du jour", style="Custom.TLabelframe")
        tip_frame.grid(row=0, column=0, sticky="nsew")
        tip_frame.grid_columnconfigure(0, weight=1)
        tip_frame.grid_rowconfigure(0, weight=1)

        tip_text = random.choice(TIPS)
        tip_label = ttk.Label(tip_frame, text=tip_text, wraplength=300, justify="center", style="Tip.TLabel")
        tip_label.place(relx=0.5, rely=0.5, anchor="center", bordermode="inside")

        def update_tip_wraplength(event, lbl=tip_label):
            wraplength = event.width - 40
            if wraplength > 1:
                lbl.config(wraplength=wraplength)
        tip_frame.bind("<Configure>", update_tip_wraplength)

    def create_dashboard_card(self, parent, title, value, r, c):
        card = ttk.Frame(parent, style="Dashboard.TFrame")
        card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False) # Prevent widgets inside from resizing the card

        bg_label = ttk.Label(card)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        title_label = ttk.Label(card, text=title, font=("Segoe UI", 11, "italic"))
        title_label.pack(pady=(5,0))
        
        value_label = ttk.Label(card, text=value, font=("Segoe UI", 22, "bold"))
        value_label.pack(pady=(0,5), expand=True)

        def on_card_resize(event, bg=bg_label, card_widget=card):
            if event.width <= 1 or event.height <= 1: return
            
            color1 = self.app_style.colors.get(card_widget.bootstyle_color, self.app_style.colors.primary)
            color2 = self._adjust_color(color1, 0.6)
            
            gradient_img = self._create_gradient_photo(color1, color2, event.width, event.height)
            bg.config(image=gradient_img)
            bg.image = gradient_img

        # Set initial style and bind resize
        if title == "Jeux": card.bootstyle_color = "info"
        elif title == "Temps de jeu": card.bootstyle_color = "success"
        elif title == "Succès": card.bootstyle_color = "warning"
        else: card.bootstyle_color = "primary"

        # Make labels transparent by setting their background to the card's style
        for child in [title_label, value_label]:
            child.configure(style=f"inverse-{card.bootstyle_color}.TLabel")

        card.bind("<Configure>", on_card_resize)
        return value_label, card

    def create_games_page(self):
        self.games_page_frame.grid_rowconfigure(0, weight=1)
        self.games_page_frame.grid_columnconfigure(0, weight=1)
        self.games_scrolled_frame = SafeScrolledFrame(self.games_page_frame, autohide=self.autohide_scrollbars_var.get())
        self.games_scrolled_frame.grid(row=0, column=0, sticky="nsew")
        container = self.games_scrolled_frame.container
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1) # Ensure container expands vertically

        top_toolbar = ttk.Frame(container, padding=(20, 10))
        top_toolbar.grid(row=0, column=0, sticky="ew")
        top_toolbar.grid_columnconfigure(1, weight=1)

        ttk.Label(top_toolbar, text="Rechercher:", font=("Segoe UI", 11)).grid(row=0, column=0, padx=(0, 10))
        self.search_entry = ttk.Entry(top_toolbar, bootstyle="info")
        self.search_entry.grid(row=0, column=1, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.debounced_filter_games)

        clear_btn = ttk.Button(top_toolbar, text="X", command=self.clear_filters, bootstyle="danger-link", width=2)
        clear_btn.grid(row=0, column=2, padx=(5, 0))
        ToolTip(clear_btn, "Effacer tous les filtres")

        controls_frame = ttk.Frame(top_toolbar)
        controls_frame.grid(row=0, column=3, padx=(10, 0))
        
        self.fav_button = ttk.Checkbutton(controls_frame, text="⭐ Favoris", variable=self.show_favorites_only, command=self.filter_games, style="FavFilter.TCheckbutton", takefocus=False)
        self.fav_button.pack(side="left", padx=5)
        
        self.sort_menu = ttk.OptionMenu(controls_frame, self.sort_order, "Nom (A-Z)", "Nom (A-Z)", "Nom (Z-A)", "Plus joué", "Moins joué", "Plus récent", "Plus ancien", "Mieux noté", "Moins bien noté", command=self.filter_games)
        self.sort_menu.pack(side="left", padx=5)
        
        self.collection_filter = tk.StringVar(value="Toutes")
        self.collection_menu = ttk.OptionMenu(controls_frame, self.collection_filter, "Toutes", command=self.filter_games)
        self.collection_menu.pack(side="left", padx=5)
        self.category_menu = ttk.OptionMenu(controls_frame, self.category_filter, "Toutes", command=self.filter_games)
        self.category_menu.pack(side="left", padx=5)

        self.view_mode_btn = ttk.Checkbutton(controls_frame, variable=self.view_mode, onvalue="Liste", offvalue="Grille", text="Vue Liste", command=self.toggle_view_mode, bootstyle="outline-toolbutton")
        self.view_mode_btn.pack(side="left", padx=5)

        # This button is referenced by the scan_for_games function
        self.scan_button = ttk.Button(controls_frame, text="Scanner", command=self.start_manual_scan, bootstyle="info-outline")
        self.scan_button.pack(side="left", padx=5)
        ToolTip(self.scan_button, "Scanner le dossier pour de nouveaux jeux (F5)")

        self.games_grid_frame = ttk.Frame(container)
        self.games_grid_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.games_grid_frame.grid_columnconfigure([0,1,2,3], weight=1)

    def create_settings_page(self):
        self.settings_page_frame.grid_rowconfigure(0, weight=1)
        self.settings_page_frame.grid_columnconfigure(0, weight=1)
        self.settings_scrolled_frame = SafeScrolledFrame(self.settings_page_frame, autohide=self.autohide_scrollbars_var.get())
        self.settings_scrolled_frame.grid(row=0, column=0, sticky="nsew")
        container = self.settings_scrolled_frame.container
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1) # Ensure container expands vertically

        header = ttk.Frame(container, padding=(20, 20))
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="Paramètres", font=("Segoe UI", 24, "bold")).pack(anchor="w")

        settings_notebook = ttk.Notebook(container, bootstyle="primary")
        settings_notebook.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # --- Onglet Apparence ---
        appearance_tab = ttk.Frame(settings_notebook, padding=20)
        settings_notebook.add(appearance_tab, text="Apparence")
        appearance_tab.grid_columnconfigure(1, weight=1)

        ttk.Label(appearance_tab, text="Thème:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        theme_menu = ttk.OptionMenu(appearance_tab, tk.StringVar(value=self.app_style.theme.name), None, *THEMES, command=self.change_theme)
        theme_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(appearance_tab, text="Fond d'écran:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        bg_frame = ttk.Frame(appearance_tab)
        bg_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
        ttk.Button(bg_frame, text="Choisir une image", command=self.select_background).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ttk.Button(bg_frame, text="Réinitialiser", command=lambda: self.set_background(GRADIENT_DEFAULT_PATH), bootstyle="secondary").pack(side="left", expand=True, fill="x")

        ttk.Checkbutton(appearance_tab, text="Plein écran au démarrage", variable=self.fullscreen_var, command=self.toggle_fullscreen).grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        ttk.Checkbutton(appearance_tab, text="Masquer les barres de défilement", variable=self.autohide_scrollbars_var, command=self.toggle_autohide).grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        ttk.Label(appearance_tab, text="Taille de la police:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        font_menu = ttk.OptionMenu(appearance_tab, self.font_size_var, "Moyen", "Petit", "Moyen", "Grand", command=self.save_and_apply_appearance)
        font_menu.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(appearance_tab, text="Arrondi des angles:").grid(row=5, column=0, padx=10, pady=10, sticky="w")
        corner_frame = ttk.Frame(appearance_tab)
        corner_frame.grid(row=5, column=1, padx=10, pady=10, sticky="ew")
        corner_scale = ttk.Scale(corner_frame, from_=0, to=20, variable=self.corner_radius_var, command=lambda e: self.save_and_apply_appearance())
        corner_scale.pack(side="left", fill="x", expand=True)
        corner_label = ttk.Label(corner_frame, textvariable=self.corner_radius_var, width=3)
        corner_label.pack(side="left", padx=(10, 0))

        # Row 6: Page Transition
        ttk.Label(appearance_tab, text="Transition de page:").grid(row=6, column=0, padx=10, pady=10, sticky="w")
        self.animation_type_menu = ttk.OptionMenu(
            appearance_tab, self.animation_type_var, "Glissement", "Glissement", "Fondu", command=self.save_animation_type
        )
        self.animation_type_menu.grid(row=6, column=1, padx=10, pady=10, sticky="ew")

        # Row 7: Custom Theme Editor
        ttk.Label(appearance_tab, text="Thème personnalisé:").grid(row=7, column=0, padx=10, pady=10, sticky="w")
        ttk.Button(appearance_tab, text="Éditeur de thème", command=self.open_theme_editor).grid(
            row=7, column=1, padx=10, pady=10, sticky="ew"
        )

        # --- Onglet Maintenance ---
        maintenance_tab = ttk.Frame(settings_notebook, padding=20)
        settings_notebook.add(maintenance_tab, text="Dossiers & Maintenance")
        maintenance_tab.grid_columnconfigure(0, weight=1)

        folders_frame = ttk.Labelframe(maintenance_tab, text="Dossiers", style="Custom.TLabelframe")
        folders_frame.grid(row=0, column=0, sticky="ew", pady=10)
        folders_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Button(folders_frame, text="Ouvrir le dossier des jeux", command=lambda: os.startfile(self.get_games_folder())).pack(fill="x", padx=20, pady=10)
        ttk.Button(folders_frame, text="Changer le dossier des jeux", command=self.change_games_folder).pack(fill="x", padx=20, pady=10)
        ttk.Button(folders_frame, text="Ouvrir le dossier des paramètres", command=lambda: os.startfile(SETTINGS_FOLDER)).pack(fill="x", padx=20, pady=10)
        ttk.Button(folders_frame, text="Ouvrir le journal des erreurs", command=self.open_crash_log).pack(fill="x", padx=20, pady=10)

        maintenance_frame = ttk.Labelframe(maintenance_tab, text="Maintenance de la bibliothèque", style="Custom.TLabelframe")
        maintenance_frame.grid(row=1, column=0, sticky="ew", pady=10)
        maintenance_frame.grid_columnconfigure([0, 1], weight=1)

        maintenance_buttons = [
            ("📤 Exporter les données", self.export_data), ("📥 Importer les données", self.import_data),
            ("💾 Créer une sauvegarde", self.backup_data), ("📍 Marquer les jeux manquants", self.mark_missing_games_ui),
            ("🗑️ Supprimer les jeux manquants", self.remove_missing_games_ui), ("✨ Supprimer les doublons", self.deduplicate_games_ui),
        ]
        for i, (text, cmd) in enumerate(maintenance_buttons):
            row, col = divmod(i, 2)
            ttk.Button(maintenance_frame, text=text, command=cmd, bootstyle="secondary-outline").grid(row=row, column=col, sticky="ew", padx=10, pady=5)

        # Bouton de réinitialisation des succès
        reset_ach_btn = ttk.Button(maintenance_frame, text="Réinitialiser tous les succès", command=self.reset_achievements_ui, bootstyle="danger-outline")
        reset_ach_btn.grid(row=len(maintenance_buttons) // 2, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

        # Bouton de réinitialisation totale
        reset_all_btn = ttk.Button(maintenance_frame, text="Réinitialiser TOUTE l'application", command=self.reset_all_data_ui, bootstyle="danger")
        reset_all_btn.grid(row=len(maintenance_buttons) // 2 + 1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        # --- Onglet Catégories ---
        categories_tab = ttk.Frame(settings_notebook, padding=20)
        settings_notebook.add(categories_tab, text="Gestion des Catégories")
        self.create_categories_tab(categories_tab)

        # --- Onglet Collections ---
        collections_tab = ttk.Frame(settings_notebook, padding=20)
        settings_notebook.add(collections_tab, text="Collections")
        self.create_collections_tab(collections_tab)

    def create_categories_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        cat_frame = ttk.Labelframe(parent, text="Toutes les catégories", style="Custom.TLabelframe")
        cat_frame.grid(row=0, column=0, sticky="nsew", pady=10)
        cat_frame.grid_columnconfigure(0, weight=1)
        cat_frame.grid_rowconfigure(0, weight=1)

        cols = ('category_name',)
        self.categories_tree = ttk.Treeview(cat_frame, columns=cols, show='headings', height=10)
        self.categories_tree.heading('category_name', text='Nom de la catégorie')
        self.categories_tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.populate_categories_treeview()

        button_frame = ttk.Frame(cat_frame)
        button_frame.grid(row=1, column=0, pady=10)

        ttk.Button(button_frame, text="Renommer", command=self.rename_category, bootstyle="info").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.delete_category, bootstyle="danger").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Actualiser", command=self.populate_categories_treeview, bootstyle="secondary").pack(side="left", padx=5)

    def create_collections_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        coll_frame = ttk.Labelframe(parent, text="Toutes les collections", style="Custom.TLabelframe")
        coll_frame.grid(row=0, column=0, sticky="nsew", pady=10)
        coll_frame.grid_columnconfigure(0, weight=1)
        coll_frame.grid_rowconfigure(0, weight=1)

        cols = ('collection_name', 'game_count')
        self.collections_tree = ttk.Treeview(coll_frame, columns=cols, show='headings', height=10)
        self.collections_tree.heading('collection_name', text='Nom de la collection')
        self.collections_tree.heading('game_count', text='Nombre de jeux')
        self.collections_tree.column('game_count', anchor='center', width=120)
        self.collections_tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.populate_collections_treeview()

        button_frame = ttk.Frame(coll_frame)
        button_frame.grid(row=1, column=0, pady=10)

        ttk.Button(button_frame, text="Créer", command=self.create_collection_ui).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Renommer", command=self.rename_collection_ui).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.delete_collection_ui, bootstyle="danger").pack(side="left", padx=5)

    def populate_categories_treeview(self):
        for i in self.categories_tree.get_children():
            self.categories_tree.delete(i)
        with self.games_lock:
            # Create a copy to iterate over
            all_categories = sorted(list(set(cat for g in self.games for cat in g.get("categories", []))))

        for cat in all_categories:
            self.categories_tree.insert("", "end", values=(cat,))

    def populate_collections_treeview(self):
        for i in self.collections_tree.get_children():
            self.collections_tree.delete(i)
        for name, game_paths in sorted(self.collections.items()):
            self.collections_tree.insert("", "end", values=(name, len(game_paths)))

    def update_collection_filter_menu(self):
        menu = self.collection_menu["menu"]
        menu.delete(0, "end")
        menu.add_command(label="Toutes", command=lambda: self.collection_filter.set("Toutes") or self.filter_games())
        for name in sorted(self.collections.keys()):
            menu.add_command(label=name, command=lambda n=name: self.collection_filter.set(n) or self.filter_games())

    def create_achievements_page(self):
        self.achievements_page_frame.grid_rowconfigure(0, weight=1)
        self.achievements_page_frame.grid_columnconfigure(0, weight=1)
        self.achievements_scrolled_frame = SafeScrolledFrame(self.achievements_page_frame, autohide=self.autohide_scrollbars_var.get())
        self.achievements_scrolled_frame.grid(row=0, column=0, sticky="nsew")
        container = self.achievements_scrolled_frame.container
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1) # Ensure container expands vertically

        ttk.Label(container, text="Succès", font=("Segoe UI", 24, "bold")).grid(row=0, column=0, pady=(30, 20), padx=30, sticky="w")
        self.achievements_container = ttk.Frame(container)
        self.achievements_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    def create_pro_page(self):
        self.pro_page_frame.grid_columnconfigure(0, weight=1)
        self.pro_page_frame.grid_rowconfigure(1, weight=1)

        header = ttk.Frame(self.pro_page_frame, padding=(30, 30, 30, 20))
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="Aperçu", font=("Segoe UI", 24, "bold")).pack(anchor="w")

        self.pro_page_notebook = ttk.Notebook(self.pro_page_frame, bootstyle="primary")
        self.pro_page_notebook.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.pro_page_notebook.bind("<<NotebookTabChanged>>", self._on_pro_tab_changed)

        # --- Onglet Profil ---
        profile_tab_container = ttk.Frame(self.pro_page_notebook)
        self.pro_page_notebook.add(profile_tab_container, text="Profil")
        profile_scrolled_frame = SafeScrolledFrame(profile_tab_container, autohide=self.autohide_scrollbars_var.get())
        profile_scrolled_frame.pack(fill="both", expand=True)
        profile_tab = profile_scrolled_frame.container
        profile_tab.configure(padding=20)
        profile_tab.grid_columnconfigure(0, weight=1)

        profile_card = ttk.Labelframe(profile_tab, text="Informations Utilisateur", style="Custom.TLabelframe")
        profile_card.grid(row=1, column=0, sticky="ew", pady=10)
        profile_card.grid_columnconfigure(1, weight=1)
        
        # Username row
        ttk.Label(profile_card, text="Nom d'utilisateur :", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=20, pady=5)
        user_frame = ttk.Frame(profile_card)
        user_frame.grid(row=0, column=1, sticky="w", padx=20, pady=5)
        self.pro_username_label = ttk.Label(user_frame, text=self.get_username(), font=("Segoe UI", 11))
        self.pro_username_label.pack(side="left")
        edit_user_btn = ttk.Button(user_frame, text="✏️", command=self.change_username, bootstyle="link", width=2)
        edit_user_btn.pack(side="left", padx=(5,0))
        ToolTip(edit_user_btn, "Changer le nom d'utilisateur")

        stats_labels = {
            "Temps de jeu total": "pro_profile_playtime_label",
            "Jeux lancés": "pro_profile_launched_label",
            "Jeux en favoris": "pro_profile_fav_label",
            "Date d'inscription": "pro_profile_reg_label"
        }
        for i, (text, attr_name) in enumerate(stats_labels.items(), start=1):
            ttk.Label(profile_card, text=f"{text} :", font=("Segoe UI", 11, "bold")).grid(row=i, column=0, sticky="w", padx=20, pady=5)
            value_label = ttk.Label(profile_card, text="-", font=("Segoe UI", 11))
            value_label.grid(row=i, column=1, sticky="w", padx=20, pady=5)
            setattr(self, attr_name, value_label)

        # --- Onglet Statistiques ---
        stats_tab_container = ttk.Frame(self.pro_page_notebook)
        self.pro_page_notebook.add(stats_tab_container, text="Statistiques")
        stats_scrolled_frame = SafeScrolledFrame(stats_tab_container, autohide=self.autohide_scrollbars_var.get())
        stats_scrolled_frame.pack(fill="both", expand=True)
        stats_tab = stats_scrolled_frame.container
        stats_tab.configure(padding=20)
        stats_tab.grid_columnconfigure(0, weight=1)

        ach_frame = ttk.Labelframe(stats_tab, text="Progression des Succès", style="Custom.TLabelframe")
        ach_frame.grid(row=1, column=0, sticky="ew", pady=10)
        ach_frame.grid_rowconfigure(0, weight=1)
        ach_frame.grid_columnconfigure(0, weight=1)
        self.pro_stats_ach_meter = Meter(
            master=ach_frame,
            metersize=180,
            padding=5,
            amountused=0,
            amounttotal=len(self.achievements_data),
            subtext="débloqués",
            bootstyle="success",
            interactive=False,
        )
        self.pro_stats_ach_meter.grid(row=0, column=0, pady=10)

        # Library stats
        lib_frame = ttk.Labelframe(stats_tab, text="Statistiques de la Bibliothèque", style="Custom.TLabelframe")
        lib_frame.grid(row=2, column=0, sticky="ew", pady=10)
        lib_frame.grid_columnconfigure(1, weight=1)

        lib_stats_labels = {
            "Nombre total de jeux": "pro_stats_lib_total_label",
            "Jeux avec description personnalisée": "pro_stats_lib_desc_label",
            "Jeux avec icône personnalisée": "pro_stats_lib_icon_label",
            "Jeux introuvables": "pro_stats_lib_missing_label"
        }
        for i, (text, attr_name) in enumerate(lib_stats_labels.items()):
            ttk.Label(lib_frame, text=f"{text} :", font=("Segoe UI", 11, "bold")).grid(row=i, column=0, sticky="w", padx=20, pady=5)
            value_label = ttk.Label(lib_frame, text="-", font=("Segoe UI", 11))
            value_label.grid(row=i, column=1, sticky="w", padx=20, pady=5)
            setattr(self, attr_name, value_label)

        # Top 5 games
        top_games_frame = ttk.Labelframe(stats_tab, text="Top 5 des jeux les plus joués", style="Custom.TLabelframe")
        top_games_frame.grid(row=3, column=0, sticky="ew", pady=10)
        top_games_frame.grid_columnconfigure(0, weight=1)

        cols = ('game_name', 'play_time')
        self.pro_stats_top_games_tree = ttk.Treeview(top_games_frame, columns=cols, show='headings', height=5, selectmode="none")
        self.pro_stats_top_games_tree.heading('game_name', text='Jeu')
        self.pro_stats_top_games_tree.heading('play_time', text='Temps de jeu')
        self.pro_stats_top_games_tree.column('play_time', anchor='center', width=120)
        self.pro_stats_top_games_tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # --- Onglet Suggestions ---
        suggestion_tab = ttk.Frame(self.pro_page_notebook, padding=20)
        self.pro_page_notebook.add(suggestion_tab, text="Suggestions")
        suggestion_tab.grid_columnconfigure(0, weight=1)
        suggestion_tab.grid_rowconfigure(1, weight=1)

        sugg_header = ttk.Frame(suggestion_tab)
        sugg_header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        ttk.Label(sugg_header, text="Essayez quelque chose de nouveau", font=("Segoe UI", 16, "bold")).pack(side="left")
        ttk.Button(sugg_header, text="Nouvelle suggestion", command=self.update_pro_page, bootstyle="info-outline").pack(side="right")

        self.pro_suggestion_frame = ttk.Frame(suggestion_tab, style="Card.TFrame")
        self.pro_suggestion_frame.grid(row=1, column=0, sticky="nsew")

        # --- Onglet À propos ---
        about_tab = ttk.Frame(self.pro_page_notebook, padding=20)
        self.pro_page_notebook.add(about_tab, text="À propos")
        about_tab.grid_columnconfigure(0, weight=1)
        about_tab.grid_rowconfigure(0, weight=1)
        
        about_container = ttk.Frame(about_tab)
        about_container.place(relx=0.5, rely=0.5, anchor="center")
        try:
            # Utilisation de la nouvelle méthode pour charger l'icône
            self.about_logo = self._get_image_icon(DEFAULT_GAME_ICON, (128, 128))
            ttk.Label(about_container, image=self.about_logo).pack(pady=10)
        except Exception:
            pass
        ttk.Label(about_container, text=APP_NAME, font=("Segoe UI", 32, "bold")).pack(pady=(5, 0))
        ttk.Label(about_container, text=VERSION, font=("Segoe UI", 14)).pack()
        ttk.Label(about_container, text=COPYRIGHT, font=("Segoe UI", 12, "italic"), bootstyle="secondary").pack(pady=(20, 0))
        ttk.Label(about_container, text="Lanceur de jeux moderne et personnalisable.", bootstyle="secondary").pack()
        
        link = ttk.Label(about_container, text="Développé avec Python et Tkinter. Voir sur GitHub.", foreground=self.app_style.colors.primary, cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/dodosi/dodoxi"))

        update_btn = ttk.Button(about_container, text="Vérifier les mises à jour", command=lambda: self.start_update_check(manual=True))
        update_btn.pack(pady=(10,0))

    def _on_pro_tab_changed(self, event):
        notebook = event.widget
        tab_name = notebook.tab(notebook.select(), "text")
        
        if tab_name == "Profil":
            self.check_and_unlock_achievement("achievement_profile_view")
            self.session_pro_pages_visited.add("profile")
        elif tab_name == "Statistiques":
            self.check_and_unlock_achievement("achievement_stats_view")
            self.session_pro_pages_visited.add("stats")
        elif tab_name == "Suggestions":
            self.check_and_unlock_achievement("achievement_suggestion")
            self.session_pro_pages_visited.add("suggestion")
        elif tab_name == "À propos":
            self.check_and_unlock_achievement("achievement_ui_polish")

        self.check_and_unlock_pro_pages_achievement()

    def save_animation_type(self, *args):
        self.save_settings("page_transition_animation", self.animation_type_var.get())

    def save_and_apply_appearance(self, *args):
        self.save_settings("font_size", self.font_size_var.get())
        self.save_settings("corner_radius", self.corner_radius_var.get())
        self._apply_appearance_settings()
        if self.font_size_var.get() != "Moyen":
            self.check_and_unlock_achievement("achievement_maitre_style")
        if self.corner_radius_var.get() != 8:
            self.check_and_unlock_achievement("achievement_arrondir_angles")

    def _update_sidebar_active(self, active_page_name):
        for page, button in self.sidebar_buttons.items():
            style = "Sidebar.Active.TButton" if page == active_page_name else "Sidebar.TButton"
            button.configure(style=style)

    # --- Page Content Updaters ---
    def update_welcome_message(self):
        self.welcome_label.config(text=self.get_welcome_message())

    def update_main_page_stats(self):
        with self.games_lock:
            total_games = len([g for g in self.games if not g.get("deleted")])
            most_played = max([g for g in self.games if not g.get("deleted")], key=lambda g: g.get("launch_count", 0), default=None)

        unlocked_ach = sum(1 for ach in self.achievements_data.values() if self.settings.get(ach["unlocked_key"]))
        total_ach = len(self.achievements_data)
        total_playtime_s = self.settings.get("total_playtime_seconds", 0)
        h, m = divmod(total_playtime_s / 60, 60)
        
        self.total_games_label.config(text=str(total_games))
        self.achievements_label.config(text=f"{unlocked_ach}/{total_ach}")
        self.playtime_label.config(text=f"{int(h)}h {int(m)}m")

        self.most_played_label.config(text=most_played['name'] if most_played and most_played['launch_count'] > 0 else "N/A")

        self.update_spotlight_game()

    def _create_spotlight_content(self, parent_frame, from_suggestion_page=False):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        with self.games_lock:
            available_games = [g for g in self.games if not g.get("deleted")]

        if not available_games:
            ttk.Label(parent_frame, text="Ajoutez des jeux pour en voir un ici !", style="Card.TLabel").pack(expand=True)
            return

        # Suggestion : un jeu peu joué ou jamais joué
        spotlight_game = min(available_games, key=lambda g: (g.get("launch_count", 0), g.get("last_launched") or "0"))
        
        card = ttk.Frame(parent_frame, style="Card.TFrame")
        card.pack(fill="both", expand=True, padx=5 if not from_suggestion_page else 0, pady=5 if not from_suggestion_page else 0)
        card.grid_columnconfigure(1, weight=1)
        
        icon = self._get_image_icon(spotlight_game.get("icon", DEFAULT_GAME_ICON), (96, 96))
        icon_label = ttk.Label(card, image=icon, style="Card.TLabel")
        icon_label.image = icon
        icon_label.grid(row=0, column=0, rowspan=3, padx=15, pady=15)

        ttk.Label(card, text=spotlight_game.get("name"), style="CardTitle.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(card, text="Essayez-le !", style="Spotlight.TLabel").grid(row=1, column=1, sticky="w")
        
        ttk.Button(card, text="Lancer", command=lambda g=spotlight_game: self.lancer_jeu(g, from_spotlight=True), bootstyle="success").grid(row=2, column=1, sticky="w", pady=5)

    def update_spotlight_game(self):
        self._create_spotlight_content(self.spotlight_frame)

    def update_game_cards(self, animate=True):
        columns = self._get_game_grid_columns()
        for i in range(4):
            self.games_grid_frame.grid_columnconfigure(i, weight=0 if i >= columns else 1)

        if not self.filtered_games:
            for widget in self.games_grid_frame.winfo_children():
                widget.destroy()
            empty_frame = ttk.Frame(self.games_grid_frame)
            empty_frame.grid(row=0, column=0, columnspan=columns or 1, pady=50)
            
            msg = "Aucun jeu trouvé."
            if not any(g for g in self.games if not g.get("deleted")):
                msg = "Votre bibliothèque est vide."
            
            ttk.Label(empty_frame, text=msg, font=("Segoe UI", 16, "bold"), bootstyle="secondary").pack(pady=10)
            ttk.Button(empty_frame, text="Ajouter un jeu", command=self.add_game).pack(pady=5)
            return

        def _create_card_callback(game_data, idx):
            row, col = divmod(idx, columns)
            card = self.create_game_card_widget(self.games_grid_frame)
            self.update_game_card_content(card, game_data)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.game_card_widgets[game_data['path']] = card
            return card

        self.staggered_load(self.games_grid_frame, self.filtered_games, _create_card_callback, delay=35, animate=animate) # Delay adjusted for better feel

    def reflow_game_cards(self):
        """Re-grids existing game cards without destroying them for smooth resizing."""
        if self.is_updating_view:
            return
        columns = self._get_game_grid_columns()
        for i in range(4):
            self.games_grid_frame.grid_columnconfigure(i, weight=1 if i < columns else 0)

        # Re-grid existing widgets
        for idx, game_data in enumerate(self.filtered_games):
            widget = self.game_card_widgets.get(game_data['path'])
            if widget and widget.winfo_exists():
                row, col = divmod(idx, columns)
                widget.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def _get_image_icon(self, path, size=(64, 64)):
        """Charge, redimensionne et renvoie un objet PhotoImage de manière sécurisée."""
        cache_key = (path, size)
        if cache_key in self.icon_cache:
            # Check if the image object is still valid (Tkinter might garbage collect if not referenced)
            # A simple check like `if self.icon_cache[cache_key].__dict__:` is not reliable.
            # Better to just return it and let Tkinter handle it, or use a strong reference.
            # For now, assume it's valid if in cache.
            return self.icon_cache[cache_key]

        try:
            img = Image.open(path)
        except Exception:
            # Si le chemin spécifié échoue, utiliser l'icône par défaut
            path = DEFAULT_GAME_ICON
            # Always try to load default icon if original path fails
            try:
                img = Image.open(DEFAULT_GAME_ICON)
            except Exception as e_default:
                log_crash(f"Impossible de charger même l'icône par défaut: {DEFAULT_GAME_ICON}", e_default)
                # Create a blank image to prevent further errors if default also fails
                blank_img = Image.new("RGB", size, "grey")
                photo_image = ImageTk.PhotoImage(blank_img)
                self.icon_cache[cache_key] = photo_image
                return photo_image
        
        img = img.resize(size, Image.Resampling.LANCZOS)
        photo_image = ImageTk.PhotoImage(img)
        self.icon_cache[cache_key] = photo_image
        return photo_image

    def _create_achievement_card(self, parent, ach_data):
        """Crée et renvoie un widget de carte de succès unique."""
        key, ach = ach_data
        unlocked = self.settings.get(ach["unlocked_key"], False)
        
        card_style = "success.TFrame" if unlocked else "Card.TFrame"
        card = ttk.Frame(parent, style=card_style, padding=15)
        card.grid_columnconfigure(1, weight=1)

        icon = ach["icon_unlocked"] if unlocked else ach["icon_locked"]
        icon_style = "success.TLabel" if unlocked else "Card.TLabel"
        ttk.Label(card, text=icon, font=("Segoe UI", 24), style=icon_style).grid(row=0, column=0, rowspan=2, padx=(0, 15))
        
        name_style = "success.TLabel" if unlocked else "CardTitle.TLabel"
        ttk.Label(card, text=ach["name"], font=("Segoe UI", 12, "bold"), style=name_style).grid(row=0, column=1, sticky="w")
        
        desc_style = "success.TLabel" if unlocked else "Disabled.TLabel"
        desc_label = ttk.Label(card, text=ach["desc"], justify="left", style=desc_style)
        desc_label.grid(row=1, column=1, sticky="w")

        card.ach_key = key # Store the achievement key on the widget
        return card

    def update_achievements_page(self, animate=True): # Modified to use reflow or staggered_load
        cols = 2 if self.winfo_width() >= 1100 else 1
        self.achievements_container.grid_columnconfigure(list(range(cols)), weight=1)

        sorted_achievements = sorted(self.achievements_data.items(), key=lambda item: item[1]['difficulty'])
        
        difficulties = {
            "Facile": (1, 10),
            "Normal": (11, 25),
            "Difficile": (26, 40),
            "Expert": (41, 97),
            "Légendaire": (98, 100)
        }

        render_list = []
        for difficulty_name, (min_diff, max_diff) in difficulties.items():
            ach_in_difficulty = [ach for ach in sorted_achievements if min_diff <= ach[1]['difficulty'] <= max_diff]
            if ach_in_difficulty:
                render_list.append(('header', difficulty_name))
                for ach_tuple in ach_in_difficulty:
                    render_list.append(('achievement', ach_tuple))

        if animate:
            # Clear existing widgets and the map if animating (rebuilding)
            for widget in self.achievements_container.winfo_children():
                widget.destroy()
            self.achievement_headers.clear()
            self.achievement_separators.clear()
            self.achievement_card_widgets.clear() # Clear the map

            row, col = 0, 0
            def _create_item_callback(item_tuple, idx): # This callback is for staggered_load
                nonlocal row, col
                item_type, item_data = item_tuple
                widget = None

                if item_type == 'header':
                    if row > 0:
                        sep = ttk.Separator(self.achievements_container)
                        sep.grid(row=row, column=0, columnspan=cols, sticky="ew", pady=20)
                        self.achievement_separators[item_data] = sep
                        row += 1
                    widget = ttk.Label(self.achievements_container, text=item_data, font=("Segoe UI", 16, "bold"), style="Section.TLabel")
                    widget.grid(row=row, column=0, columnspan=cols, sticky="w", pady=(0, 10))
                    self.achievement_headers[item_data] = widget
                    row += 1
                    col = 0
                
                elif item_type == 'achievement':
                    widget = self._create_achievement_card(self.achievements_container, item_data)
                    widget.grid(row=row, column=col, sticky="ew", padx=10, pady=10)
                    self.achievement_card_widgets[item_data[0]] = widget # Store by key
                    col += 1
                    if col >= cols:
                        col = 0
                        row += 1
                return widget
            
            self.staggered_load(self.achievements_container, render_list, _create_item_callback, delay=30, animate=animate)
        else:
            # Fast reflow without animation (for resize)
            self.reflow_achievement_cards(render_list, cols)

    def reflow_achievement_cards(self, render_list, cols):
        # Hide all widgets before re-gridding them to prevent flickering
        for widget in self.achievements_container.winfo_children():
            widget.grid_forget()

        row, col = 0, 0
        for item_tuple in render_list:
            item_type, item_data = item_tuple
            
            if item_type == 'header':
                if row > 0:
                    # Get or create separator
                    sep = self.achievement_separators.get(item_data)
                    if not (sep and sep.winfo_exists()):
                        sep = ttk.Separator(self.achievements_container)
                        self.achievement_separators[item_data] = sep
                    sep.grid(row=row, column=0, columnspan=cols, sticky="ew", pady=20)
                    row += 1
                
                # Get or create header
                header = self.achievement_headers.get(item_data)
                if not (header and header.winfo_exists()):
                    header = ttk.Label(self.achievements_container, text=item_data, font=("Segoe UI", 16, "bold"), style="Section.TLabel")
                    self.achievement_headers[item_data] = header
                header.grid(row=row, column=0, columnspan=cols, sticky="w", pady=(0, 10))
                row += 1
                col = 0
            
            elif item_type == 'achievement':
                ach_key = item_data[0]
                widget = self.achievement_card_widgets.get(ach_key)
                if not (widget and widget.winfo_exists()):
                    widget = self._create_achievement_card(self.achievements_container, item_data)
                    self.achievement_card_widgets[ach_key] = widget
                
                widget.grid(row=row, column=col, sticky="ew", padx=10, pady=10)
                col += 1
                if col >= cols:
                    col = 0
                    row += 1

    def update_pro_page(self):
        # --- Update Profile Tab ---
        with self.games_lock:
            total_playtime_s = self.settings.get("total_playtime_seconds", 0)
            h, m = divmod(total_playtime_s / 60, 60)
            fav_games = len([g for g in self.games if g.get("favorite")])
            
            if self.pro_profile_playtime_label: self.pro_profile_playtime_label.config(text=f"{int(h)}h {int(m)}m")
            if self.pro_profile_launched_label: self.pro_profile_launched_label.config(text=str(self.settings.get('games_launched_count', 0)))
            if self.pro_profile_fav_label: self.pro_profile_fav_label.config(text=str(fav_games))
            if self.pro_profile_reg_label: self.pro_profile_reg_label.config(text=self.settings.get("login_dates", ["N/A"])[0])

        # --- Update Stats Tab ---
        unlocked_ach = sum(1 for ach in self.achievements_data.values() if self.settings.get(ach["unlocked_key"]))
        total_ach = len(self.achievements_data)

        if self.pro_stats_ach_meter: self.pro_stats_ach_meter.configure(amountused=unlocked_ach)

        with self.games_lock:
            total_games = len([g for g in self.games if not g.get("deleted")])
            missing_games = sum(1 for g in self.games if g.get("missing"))
            games_with_desc = sum(1 for g in self.games if not g.get("deleted") and g.get("description") not in [None, "Aucune description."])
            games_with_icon = sum(1 for g in self.games if not g.get("deleted") and g.get("icon") not in [None, DEFAULT_GAME_ICON])
            top_games = sorted([g for g in self.games if not g.get("deleted")], key=lambda g: g.get("playtime_seconds", 0), reverse=True)[:5]

        if self.pro_stats_lib_total_label: self.pro_stats_lib_total_label.config(text=str(total_games))
        if self.pro_stats_lib_desc_label: self.pro_stats_lib_desc_label.config(text=f"{games_with_desc} / {total_games}")
        if self.pro_stats_lib_icon_label: self.pro_stats_lib_icon_label.config(text=f"{games_with_icon} / {total_games}")
        if self.pro_stats_lib_missing_label: self.pro_stats_lib_missing_label.config(text=str(missing_games))

        if self.pro_stats_top_games_tree:
            for i in self.pro_stats_top_games_tree.get_children():
                self.pro_stats_top_games_tree.delete(i)
            
            for game in top_games:
                playtime_s = game.get("playtime_seconds", 0)
                if playtime_s > 0:
                    h, rem = divmod(playtime_s, 3600)
                    m, s = divmod(rem, 60)
                    playtime_str = f"{int(h)}h {int(m)}m"
                    self.pro_stats_top_games_tree.insert("", "end", values=(game['name'], playtime_str))

        # --- Update Suggestion Tab ---
        if self.pro_suggestion_frame:
            self._create_spotlight_content(self.pro_suggestion_frame, from_suggestion_page=True)

    def get_page_name(self, frame):
        return self.frame_map.get(frame)

    def get_page_index(self, name):
        try:
            return self.page_order.index(name)
        except (ValueError, TypeError):
            return -1

    # --- Page Navigation & Display ---
    def show_page(self, page_name: str):
        target_frame = self.page_map.get(page_name)
        if not target_frame or self.current_page_frame == target_frame or self.is_transitioning:
            return

        self._update_sidebar_active(page_name)
        self.visited_pages.add(page_name)
        if len(self.visited_pages) >= 4: self.check_and_unlock_achievement("achievement_14")

        # Determine animation direction based on sidebar order
        current_idx = self.get_page_index(self.get_page_name(self.current_page_frame))
        target_idx = self.get_page_index(page_name)
        direction = "left" if target_idx > current_idx else "right"

        def on_transition_complete():
            # Now that the new page is in place, update its content if needed.
            if self.pages_dirty.get(page_name):
                if page_name == "achievements": self.update_achievements_page()
                elif page_name == "main": self.update_welcome_message(); self.update_main_page_stats()
                elif page_name == "games": self.filter_games()
                elif page_name == "pro": self.update_pro_page()
                self.pages_dirty[page_name] = False

        self.animate_page_transition(target_frame, direction=direction, on_complete=on_transition_complete)

    def go_to_pro_tab(self, tab_index: int):
        """Navigates to the 'pro' page and selects a specific tab."""
        self.show_page("pro")
        if self.pro_page_notebook:
            try:
                self.pro_page_notebook.select(tab_index)
            except tk.TclError:
                # Tab might not exist, or notebook is not fully created.
                pass

    def check_missing_games(self):
        """Checks all games in the library and updates their 'missing' status."""
        updated = False
        count = 0
        with self.games_lock:
            for game in self.games:
                path = game.get("path", "")
                is_missing = not path or not os.path.exists(path)
                if game.get("missing") != is_missing:
                    game["missing"] = is_missing
                    updated = True
            
            count = sum(1 for g in self.games if g.get("missing"))

        if updated:
            self.save_games()
        
        return count
        
    def load_data(self, file_path: str, data_type: str, default_value: dict | list) -> dict | list:
        """
        Charge un fichier de données JSON de manière sécurisée.
        Tente de restaurer à partir d'une sauvegarde en cas de corruption.
        Crée le fichier avec les valeurs par défaut s'il n'existe pas.
        """
        backup_path = file_path + ".bak"
        
        def _read_file(path):
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                return None
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None

        # 1. Essayer de charger le fichier principal
        data = _read_file(file_path)
        if data is not None:
            return data

        # 2. Le fichier principal est corrompu ou absent, essayer la sauvegarde
        log_crash(f"Fichier de données principal '{os.path.basename(file_path)}' corrompu ou absent. Tentative de restauration...")
        backup_data = _read_file(backup_path)
        
        if backup_data is not None:
            try:
                # Restaurer le fichier principal à partir de la sauvegarde
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(backup_data, f, indent=4)
                messagebox.showinfo(
                    "Restauration des données",
                    f"Le fichier de {data_type} semblait corrompu et a été restauré\n"
                    f"à partir d'une sauvegarde récente."
                )
                return backup_data
            except IOError as e:
                log_crash(f"Échec de la restauration de la sauvegarde pour {file_path}", e)
                # Continuer pour utiliser la sauvegarde en mémoire même si la restauration a échoué
                return backup_data

        # 3. Le fichier principal ET la sauvegarde sont inutilisables. Créer un nouveau fichier.
        log_crash(f"Création d'un nouveau fichier de données pour '{os.path.basename(file_path)}'.")
        try:
            # Renommer le fichier potentiellement corrompu avant d'en créer un nouveau
            if os.path.exists(file_path):
                os.rename(file_path, file_path + f".corrupt-{int(time.time())}")
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_value, f, indent=4)
            
            return default_value
        except Exception as e:
            log_crash(f"Échec critique de la création du fichier de données {file_path}", e)
            messagebox.showerror(
                "Erreur critique",
                f"Impossible de créer le fichier de données pour {data_type}.\n"
                f"L'application ne peut pas continuer."
            )
            sys.exit(1)

    def save_data(self, file_path: str, data: dict | list):
        """
        Sauvegarde les données de manière sécurisée en créant d'abord une sauvegarde.
        """
        backup_path = file_path + ".bak"
        try:
            # 1. Créer une sauvegarde de la version actuelle (si elle existe)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f_src, open(backup_path, 'w', encoding='utf-8') as f_dst:
                    f_dst.write(f_src.read())

            # 2. Écrire les nouvelles données dans le fichier principal
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except (IOError, TypeError) as e:
            log_crash(f"Échec de la sauvegarde des données pour {os.path.basename(file_path)}", e)
            messagebox.showerror("Erreur de sauvegarde", f"Impossible de sauvegarder les données : {e}")

    # --- Data Handling ---
    def load_settings(self) -> dict:
        default_settings = {
            "username": None,
            "theme": "darkly",
            "background": "",
            "fullscreen": False,
            "autohide_scrollbars": True,
            "font_size": "Moyen",
            "corner_radius": 8,
            "view_mode": "Grille",
            "games_folder": GAMES_FOLDER,
            "games_launched_count": 0,
            "theme_change_count": 0,
            "total_playtime_seconds": 0,
            "random_launch_count": 0,
            "last_seen_version": "",
            "deleted_games_count": 0,
            "login_dates": [],
            "page_transition_animation": "Glissement",
            "custom_theme_colors": {}
        }
        for ach in self.achievements_data.values():
            default_settings[ach["unlocked_key"]] = False
            
        settings = self.load_data(SETTINGS_FILE, "paramètres", default_settings)
        # Ensure username is set, even if loading from an old settings file
        if not settings.get("username") or not settings["username"].strip():
            try:
                settings["username"] = os.getlogin()
            except Exception:
                settings["username"] = "Utilisateur"

        return settings

    def save_settings(self, key: str, value):
        self.settings[key] = value
        self.save_data(SETTINGS_FILE, self.settings)
        if key.endswith("_unlocked") or "count" in key or "playtime" in key:
            self._mark_dirty(["main", "achievements"])
        if key == "theme":
            self._apply_appearance_settings()

    def load_collections(self) -> dict:
        return self.load_data(COLLECTIONS_FILE, "collections", {})
    def save_collections(self):
        self.save_data(COLLECTIONS_FILE, self.collections)

    def load_games(self) -> list:
        return self.load_data(GAMES_FILE, "jeux", []) # Ensure games are loaded from the correct folder

    def save_games(self):
        with self.games_lock:
            # Create a copy to avoid holding the lock during file I/O
            games_to_save = [g.copy() for g in self.games]
            # Perform checks that need the lock
            games_not_deleted = [g for g in games_to_save if not g.get("deleted")]
            if len(games_not_deleted) >= 10: self.check_and_unlock_achievement("achievement_15")
            if len(games_not_deleted) > 20: self.check_and_unlock_achievement("achievement_explorateur_ultime")
        self.save_data(GAMES_FILE, games_to_save)
        self._mark_dirty(["games", "main"])

    # --- Other methods ---
    def get_welcome_message(self) -> str:
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12: return "Bonjour !"
        if 12 <= hour < 18: return "Bon après-midi !"
        return "Bonne soirée !"

    def lancer_jeu_aleatoire(self):
        with self.games_lock:
            available = [g for g in self.games if not g.get("deleted")]
        if not available:
            messagebox.showinfo("Info", "Aucun jeu disponible.")
            return
        game = random.choice(available)
        self.lancer_jeu(game)
        
        count = self.settings.get("random_launch_count", 0) + 1
        self.save_settings("random_launch_count", count)
        if count >= 10:
            self.check_and_unlock_achievement("achievement_maitre_du_hasard")

    def lancer_jeu(self, game_data: dict, from_spotlight: bool = False):
        full_path = game_data.get("path", "")
        if not full_path or not os.path.exists(full_path):
            messagebox.showerror("Erreur", f"Fichier de jeu introuvable: {full_path}")
            return

        dependencies = game_data.get("requires", [])
        if dependencies and dependencies[0]: # Check if not empty list or list with empty string
            for module in dependencies:
                if not check_and_install_module(module):
                    messagebox.showwarning("Lancement annulé", f"Le module '{module}' est requis.")
                    return
        
        try:
            proc = subprocess.Popen([sys.executable, full_path], cwd=os.path.dirname(full_path))
            start_time = time.time()
            self.running_processes[proc.pid] = {"start_time": start_time, "game_path": full_path, "proc": proc}

            with self.games_lock:
                game_data["launch_count"] = game_data.get("launch_count", 0) + 1
                game_data["last_launched"] = datetime.datetime.now().isoformat()

            self.settings["games_launched_count"] = self.settings.get("games_launched_count", 0) + 1
            self.session_launched_games.add(game_data['path'])
            
            self.save_games()
            self.save_settings("games_launched_count", self.settings["games_launched_count"])
            
            self.check_and_unlock_achievement("achievement_7")
            if len(self.session_launched_games) >= 3: self.check_and_unlock_achievement("achievement_zappeur")
            if from_spotlight: self.check_and_unlock_achievement("achievement_spotlight")

        except Exception as e:
            log_crash(f"Échec du lancement de {full_path}", e)
            messagebox.showerror("Erreur de lancement", f"Impossible de lancer le jeu: {e}")

    def poll_processes(self):
        finished_pids = []
        games_data_updated = False
        for pid, data in list(self.running_processes.items()): # Use list to allow modification during iteration
            try:
                proc = data.get("proc")
                if proc and proc.poll() is not None:
                    playtime = time.time() - data["start_time"]
                    
                    with self.games_lock:
                        # Find game and update its playtime
                        for game in self.games:
                            if game.get("path") == data.get("game_path"):
                                game["playtime_seconds"] = game.get("playtime_seconds", 0) + playtime
                                games_data_updated = True
                                break
                    
                    # Update total playtime
                    total_playtime = self.settings.get("total_playtime_seconds", 0) + playtime
                    self.save_settings("total_playtime_seconds", total_playtime)
                    
                    finished_pids.append(pid)
            except ProcessLookupError:
                # The process might have already been reaped by the OS
                finished_pids.append(pid)
            except Exception as e:
                log_crash(f"Error polling process {pid}", e)
                finished_pids.append(pid) # Remove problematic process
        
        for pid in finished_pids:
            if pid in self.running_processes:
                del self.running_processes[pid]

        if games_data_updated:
            self.save_games()
            
        self.after(5000, self.poll_processes)

    def check_loyalty_achievement(self):
        today = datetime.date.today().isoformat()
        login_dates = self.settings.get("login_dates", [])
        if today not in login_dates:
            login_dates.append(today)
            self.save_settings("login_dates", login_dates[-30:])
        
        if len(set(login_dates)) >= 7:
            self.check_and_unlock_achievement("achievement_fidele")

    def start_manual_scan(self):
        if self.scan_in_progress.is_set():
            self.show_toast("Scan en cours", "Un scan de la bibliothèque est déjà en cours.", "warning")
            return
        self.scan_in_progress.set()
        self.scan_button.config(text="Scan en cours...", state="disabled")
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _scan_worker(self):
        self.scan_for_games()

    def initial_scan_for_games(self):
        """
        Scans for games on startup without updating UI elements that may not exist yet.
        This is a synchronous, non-threaded scan.
        """
        with self.games_lock:
            existing_paths = {g["path"] for g in self.games if g.get("path")}
            new_games_count = 0
            
            folder = self.get_games_folder()
            if not os.path.exists(folder):
                return

            for root, _, files in os.walk(folder):
                for file in files:
                    if file.endswith(".py"):
                        full_path = os.path.abspath(os.path.join(root, file))
                        if full_path in existing_paths:
                            continue

                        name = file.replace('.py', '').replace('_', ' ').title()
                        if file in ["main.py", "app.py"]:
                            name = os.path.basename(root).replace('_', ' ').title()
                        
                        new_game_data = {
                            "name": name, "path": full_path, "description": "Aucune description.",
                            "icon": DEFAULT_GAME_ICON, "requires": [], "deleted": False,
                            "favorite": False, "launch_count": 0, "last_launched": None,
                            "categories": [], "playtime_seconds": 0
                        }
                        self.games.append(new_game_data)
                        new_games_count += 1
        
        if new_games_count > 0:
            self.check_and_unlock_achievement("achievement_12")

    def scan_for_games(self):
        existing_paths = {g["path"]: g for g in self.games}
        new_games_count = 0

        folder = self.get_games_folder()
        if not os.path.exists(folder):
            self.scan_in_progress.clear()
            self.after(0, self.scan_button.config, {"text": "Scanner", "state": "normal"})
            return

        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".py"):
                    # Permet à d'autres opérations de s'exécuter pour ne pas bloquer
                    # complètement le thread (même si c'est un worker)
                    time.sleep(0.001) 
                    if not self.scan_in_progress.is_set(): # Check if scan was cancelled
                        return -1 # Indicate cancellation

                    full_path = os.path.abspath(os.path.join(root, file))
                    if full_path in existing_paths:
                        continue

                    name = file.replace('.py', '').replace('_', ' ').title()
                    if file in ["main.py", "app.py"]:
                        name = os.path.basename(root).replace('_', ' ').title()
                    
                    new_game_data = {
                        "name": name, "path": full_path, "description": "Aucune description.",
                        "icon": DEFAULT_GAME_ICON, "requires": [], "deleted": False,
                        "favorite": False, "launch_count": 0, "last_launched": None,
                        "categories": [], "playtime_seconds": 0
                    }
                    with self.games_lock:
                        self.games.append(new_game_data)
                    new_games_count += 1
        
        def _scan_complete():
            if new_games_count > 0:
                self.save_games()
                self.check_and_unlock_achievement("achievement_12")
            
            self.scan_in_progress.clear()
            self.scan_button.config(text="Scanner", state="normal")
            self.show_toast("Scan terminé", f"{new_games_count} nouveau(x) jeu(x) ajouté(s)." if new_games_count > 0 else "Aucun nouveau jeu trouvé.", "success")
            self.filter_games()

        # Planifier l'exécution du code UI sur le thread principal
        if self.scan_in_progress.is_set(): # Ensure we don't schedule if cancelled
            self.after(0, _scan_complete)

    def add_game(self):
        path = filedialog.askopenfilename( # noqa: E1120
            title="Sélectionner le script Python du jeu",
            filetypes=[("Scripts Python", "*.py")]
        )
        if not path:
            return

        # Check if game already exists
        with self.games_lock:
            exists = any(g['path'] == path for g in self.games)
        if exists:
            messagebox.showwarning("Jeu existant", "Ce jeu est déjà dans votre bibliothèque.")
            return

        name = os.path.basename(path).replace('.py', '').replace('_', ' ').title()
        
        new_game = {
            "name": name, "path": path, "description": "Aucune description.",
            "icon": DEFAULT_GAME_ICON, "requires": [], "deleted": False,
            "favorite": False, "launch_count": 0, "last_launched": None,
            "categories": [], "playtime_seconds": 0, "rating": 0
        }

        with self.games_lock:
            self.games.append(new_game)
        self.save_games()
        self.filter_games()
        self.show_toast("Jeu ajouté", f"'{name}' a été ajouté à votre bibliothèque.", "success")
        self.check_and_unlock_achievement("achievement_5") # Le Collectionneur

    def update_game_card_by_path(self, game_path: str):
        """Finds and updates a single game card in the UI using a direct map."""
        card = self.game_card_widgets.get(game_path)
        with self.games_lock:
            game_data = next((g for g in self.games if g.get("path") == game_path), None)
        if card and game_data and card.winfo_exists():
            self.update_game_card_content(card, game_data)

    def show_toast(self, title, message, bootstyle="info"):
        toast = ttk.Frame(self.toast_container, padding=10, bootstyle=bootstyle)
        toast.pack(fill="x", pady=5, padx=10)
        
        ttk.Label(toast, text=title, font=("Segoe UI", 10, "bold"), bootstyle=f"inverse-{bootstyle}").pack(anchor="w")
        ttk.Label(toast, text=message, bootstyle=f"inverse-{bootstyle}").pack(anchor="w")

        self.after(4000, toast.destroy)

    def get_games_folder(self):
        return self.settings.get("games_folder", GAMES_FOLDER)

    def change_games_folder(self):
        if self.scan_in_progress.is_set():
            self.show_toast("Action impossible", "Un scan est déjà en cours.", "warning")
            return

        new_folder = filedialog.askdirectory(title="Sélectionner le dossier des jeux")
        if new_folder:
            self.save_settings("games_folder", new_folder)
            self.games = [] # Clear list to rescan
            self.save_games()
            self.filter_games() # Update UI to show empty list
            self.show_toast("Dossier changé", "Lancement du scan de la nouvelle bibliothèque...", "info")
            self.start_manual_scan() # Start the background scan

    def open_crash_log(self):
        if os.path.exists(CRASH_LOG_FILE):
            os.startfile(CRASH_LOG_FILE)
        else:
            messagebox.showinfo("Info", "Aucun journal d'erreurs trouvé.")

    def change_theme(self, theme_name: str):
        self.app_style.theme_use(theme_name)
        self.save_settings("theme", theme_name)
        self.check_and_unlock_achievement("achievement_esthete")
        self.check_and_unlock_achievement("achievement_3")
        self.show_toast("Thème changé", "Le nouveau thème sera pleinement appliqué au redémarrage.", "info")

    def select_background(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if path:
            self.set_background(path)
    
    def _update_background_display(self):
        if not self.original_background_pil or not self.background_label:
            return
        try:
            width, height = self.winfo_width(), self.winfo_height()
            if width <= 1 or height <= 1: return

            image_pil_resized = self.original_background_pil.resize((width, height), Image.Resampling.LANCZOS)
            self.background_image = ImageTk.PhotoImage(image_pil_resized)
            self.background_label.config(image=self.background_image)
        except Exception as e:
            log_crash("Échec de la mise à jour du fond d'écran", e)

    def set_background(self, image_path: str | None):
        if not image_path or not os.path.exists(image_path):
            image_path = GRADIENT_DEFAULT_PATH
        try:
            self.original_background_pil = Image.open(image_path)
            if not self.background_label:
                self.background_label = ttk.Label(self)
                self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.background_label.lower()
            self._update_background_display()
            self.current_background_path = image_path
            self.save_settings("background", image_path)
        except Exception as e:
            log_crash("Échec du réglage du fond d'écran", e)
            self.save_settings("background", "")
            self.original_background_pil = None

    def delayed_resize(self, event):
        if self.resize_timer: self.after_cancel(self.resize_timer)
        self.resize_timer = self.after(100, lambda: self.on_resize(event))

    def on_resize(self, event):
        if self.winfo_width() > 1 and self.winfo_height() > 1 and not self.is_transitioning:
            self._update_background_display()
            
            current_ach_cols = 2 if self.winfo_width() >= 1100 else 1
            if self._last_ach_cols != current_ach_cols:
                if self.current_page_frame == self.achievements_page_frame:
                    self.update_achievements_page(animate=False)
                self._last_ach_cols = current_ach_cols

            current_games_cols = self._get_game_grid_columns()
            if self._last_games_cols != current_games_cols:
                if self.current_page_frame == self.games_page_frame:
                    self.reflow_game_cards()
                self._last_games_cols = current_games_cols

    def _get_game_grid_columns(self) -> int:
        width = self.winfo_width()
        if self.view_mode.get() == "Liste": return 2 if width >= 1200 else 1
        if width < 900: return 1
        if width < 1300: return 2
        if width < 1700: return 3
        return 4

    def toggle_view_mode(self):
        self.save_settings("view_mode", self.view_mode.get())
        self.update_game_cards()

    def create_game_card_widget(self, parent: ttk.Frame) -> ttk.Frame:
        card = ttk.Frame(parent, style="GameCard.TFrame", padding=15)
        card.grid_columnconfigure(1, weight=1)
        return card

    def _create_game_card_widgets_if_needed(self, card: ttk.Frame):
        """Creates and places the permanent widgets inside a game card if they don't exist."""
        if hasattr(card, 'is_initialized'):
            return

        # Layout
        card.grid_columnconfigure(1, weight=1)
        card.grid_rowconfigure(2, weight=1)

        card.bind("<Button-3>", lambda e, c=card: self.show_game_context_menu(e, c.game_data))

        # Widgets
        card.icon_label = ttk.Label(card, style="GameCard.TLabel")
        card.icon_label.grid(row=0, column=0, rowspan=4, padx=10, pady=5, sticky="n")

        card.title_frame = ttk.Frame(card, style="GameCard.TFrame")
        card.title_frame.grid(row=0, column=1, sticky="ew")
        
        card.title_label = ttk.Label(card.title_frame, style="GameCard.TLabel", font=("Segoe UI", 14, "bold"))
        card.title_label.pack(side="left", anchor="w")
        
        card.fav_button = ttk.Button(card.title_frame, padding=0, bootstyle="link")
        card.fav_button.pack(side="right", anchor="e", padx=5)
        ToolTip(card.fav_button, "Ajouter/Retirer des favoris")

        card.desc_label = ttk.Label(card, style="GameCard.Desc.TLabel")
        card.desc_label.grid(row=1, column=1, sticky="ew", pady=(2, 5), padx=5)
        
        ttk.Frame(card, style="GameCard.TFrame").grid(row=2, column=1, sticky="nsew") # Spacer

        card.rating_frame = ttk.Frame(card, style="GameCard.TFrame")
        card.rating_frame.grid(row=2, column=0, sticky="s", padx=10, pady=5)


        card.bottom_frame = ttk.Frame(card, style="GameCard.TFrame")
        card.bottom_frame.grid(row=3, column=1, sticky="ew", pady=5)
        card.bottom_frame.grid_columnconfigure(0, weight=1)

        card.cat_label = ttk.Label(card.bottom_frame, style="Category.TLabel")
        card.cat_label.grid(row=0, column=0, sticky="w", padx=5)

        card.button_group = ttk.Frame(card.bottom_frame, style="GameCard.TFrame")
        card.button_group.grid(row=0, column=1, sticky="e")

        card.edit_btn = ttk.Button(card.button_group, text="✏️", bootstyle="secondary-outline", width=2)
        card.edit_btn.pack(side="left", padx=(0, 5))
        ToolTip(card.edit_btn, "Modifier")

        card.delete_btn = ttk.Button(card.button_group, text=TRASH_ICON, bootstyle="danger-outline", width=2)
        card.delete_btn.pack(side="left", padx=(0, 5))
        ToolTip(card.delete_btn, "Supprimer")

        card.launch_btn = ttk.Button(card.button_group, text="Lancer")
        card.launch_btn.pack(side="left")

        card.is_initialized = True

    def update_game_card_content(self, card: ttk.Frame, game_data: dict):
        self._create_game_card_widgets_if_needed(card)
        card.game_data = game_data

        icon = self._get_image_icon(game_data.get("icon", DEFAULT_GAME_ICON), (64, 64))
        card.icon_label.config(image=icon)
        card.icon_label.image = icon

        card.title_label.config(text=game_data.get("name", "Jeu inconnu"))

        fav_char = "⭐" if game_data.get("favorite") else "☆"
        fav_bootstyle = "warning" if game_data.get("favorite") else "secondary"
        card.fav_button.config(text=fav_char, bootstyle=(fav_bootstyle, "link"), command=lambda g=game_data: self.toggle_favorite(g))

        card.desc_label.config(text=game_data.get("description", "Aucune description."))
        
        self._update_rating_widget(card.rating_frame, game_data)
        
        def wrap_description(event, label=card.desc_label):
            wraplength = event.width - 100 # card width - icon width - paddings
            if wraplength > 1:
                label.config(wraplength=wraplength)
        card.bind('<Configure>', wrap_description)

        cat_text = "Catégories : " + ", ".join(game_data.get("categories", [])) if game_data.get("categories") else ""
        if game_data.get("missing"):
            card.cat_label.config(text="Fichier introuvable !", style="Invalid.TLabel")
            launch_button_state = "disabled"
        else:
            card.cat_label.config(text=cat_text, style="Category.TLabel")
            launch_button_state = "normal"

        card.edit_btn.config(command=lambda g=game_data: self.edit_game(g))
        card.delete_btn.config(command=lambda g=game_data: self.delete_game(g))
        card.launch_btn.config(command=lambda g=game_data: self.lancer_jeu(g), state=launch_button_state)

    def edit_game(self, game_data: dict):
        """Opens a dialog to edit the details of a game."""
        edit_window = tk.Toplevel(self)
        edit_window.title(f"Modifier: {game_data.get('name')}")
        edit_window.geometry("600x450")
        edit_window.transient(self)
        edit_window.grab_set()

        # --- Variables ---
        name_var = tk.StringVar(value=game_data.get("name"))
        path_var = tk.StringVar(value=game_data.get("path"))
        requires_var = tk.StringVar(value=", ".join(game_data.get("requires", [])))
        rating_var = tk.IntVar(value=game_data.get("rating", 0))
        desc_var = tk.StringVar(value=game_data.get("description"))
        icon_var = tk.StringVar(value=game_data.get("icon"))
        categories_var = tk.StringVar(value=", ".join(game_data.get("categories", [])))

        # --- Layout ---
        form_frame = ttk.Frame(edit_window, padding=20)
        form_frame.pack(fill="both", expand=True)
        form_frame.grid_columnconfigure(1, weight=1)

        # --- Widgets ---
        # Name
        ttk.Label(form_frame, text="Nom:").grid(row=0, column=0, sticky="w", pady=5)
        name_entry = ttk.Entry(form_frame, textvariable=name_var)
        name_entry.grid(row=0, column=1, sticky="ew", pady=5)

        # Path
        ttk.Label(form_frame, text="Chemin:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=path_var, state="readonly").grid(row=1, column=1, sticky="ew", pady=5)

        # Dependencies
        ttk.Label(form_frame, text="Dépendances (pip):").grid(row=2, column=0, sticky="w", pady=5)
        requires_entry = ttk.Entry(form_frame, textvariable=requires_var)
        requires_entry.grid(row=2, column=1, sticky="ew", pady=5)

        # Rating
        ttk.Label(form_frame, text="Note:").grid(row=3, column=0, sticky="w", pady=5)
        rating_frame = ttk.Frame(form_frame)
        rating_frame.grid(row=3, column=1, sticky="ew", pady=5)
        ttk.Scale(rating_frame, from_=0, to=5, variable=rating_var, style="info.Horizontal.TScale").pack(side="left", fill="x", expand=True)
        ttk.Label(rating_frame, textvariable=rating_var, width=2).pack(side="left", padx=(10, 0))

        # Description
        ttk.Label(form_frame, text="Description:").grid(row=4, column=0, sticky="w", pady=5)
        desc_entry = ttk.Entry(form_frame, textvariable=desc_var)
        desc_entry.grid(row=4, column=1, sticky="ew", pady=5)

        # Categories
        ttk.Label(form_frame, text="Catégories (virgules):").grid(row=5, column=0, sticky="w", pady=5)
        cat_entry = ttk.Entry(form_frame, textvariable=categories_var)
        cat_entry.grid(row=5, column=1, sticky="ew", pady=5)

        # Icon
        ttk.Label(form_frame, text="Icône:").grid(row=6, column=0, sticky="w", pady=5)
        icon_frame = ttk.Frame(form_frame)
        icon_frame.grid(row=6, column=1, sticky="ew", pady=5)
        icon_entry = ttk.Entry(icon_frame, textvariable=icon_var)
        icon_entry.pack(side="left", fill="x", expand=True)
        
        def _select_icon():
            path = filedialog.askopenfilename(
                title="Sélectionner une icône",
                filetypes=[("Images", "*.png *.ico *.jpg"), ("Tous les fichiers", "*.*")]
            )
            if path:
                icon_var.set(path)

        ttk.Button(icon_frame, text="...", command=_select_icon, width=3).pack(side="left", padx=(5,0))

        # --- Save/Cancel Buttons ---
        button_frame = ttk.Frame(edit_window, padding=(20, 10))
        button_frame.pack(fill="x")

        def _save_changes():
            # Update game_data dictionary
            game_data["name"] = name_var.get()
            game_data["description"] = desc_var.get()
            game_data["requires"] = [r.strip() for r in requires_var.get().split(",") if r.strip()]
            game_data["rating"] = rating_var.get()
            game_data["icon"] = icon_var.get()
            game_data["categories"] = [c.strip() for c in categories_var.get().split(",") if c.strip()]
            
            self.save_games()
            self.update_game_card_by_path(game_data["path"])
            self.check_and_unlock_achievement("achievement_8")
            if game_data["description"] != "Aucune description.":
                self.check_and_unlock_achievement("achievement_16") # La Plume Créative
            if game_data["icon"] != DEFAULT_GAME_ICON:
                self.check_and_unlock_achievement("achievement_17") # L'Icône Personnalisée
            if game_data["requires"]:
                self.check_and_unlock_achievement("achievement_dependency") # Le Technicien
            if game_data["rating"] > 0:
                self.check_and_unlock_achievement("achievement_critic")

            edit_window.destroy()

        ttk.Button(button_frame, text="Enregistrer", command=_save_changes, bootstyle="success").pack(side="right", padx=5)
        ttk.Button(button_frame, text="Annuler", command=edit_window.destroy, bootstyle="secondary").pack(side="right")

    def toggle_favorite(self, game_data: dict):
        is_now_favorite = not game_data.get("favorite", False)
        with self.games_lock:
            game_data["favorite"] = is_now_favorite
        self.save_games()
        
        # Unlock achievements
        if is_now_favorite:
            self.check_and_unlock_achievement("achievement_favori")
            with self.games_lock:
                fav_count = sum(1 for g in self.games if g.get("favorite"))
            if fav_count >= 5:
                self.check_and_unlock_achievement("achievement_5_favoris")
            if fav_count >= 10:
                self.check_and_unlock_achievement("achievement_10_favoris")

        # Instantly update the card's visual state for maximum fluidity
        self.update_game_card_by_path(game_data["path"])
        # If the favorite filter is on and the game is no longer a favorite, hide its card
        if self.show_favorites_only.get() and not is_now_favorite:
            card = self.game_card_widgets.get(game_data["path"])
            if card and card.winfo_exists():
                card.grid_forget()

    def delete_game(self, game_data: dict):
        if messagebox.askyesno("Confirmation de suppression",
                               f"Êtes-vous sûr de vouloir supprimer '{game_data['name']}' de votre bibliothèque ?\n\n"
                               "Cette action ne supprime pas les fichiers du jeu et peut être annulée en modifiant manuellement le fichier games.json.",
                               parent=self, icon='warning'):
            with self.games_lock:
                game_data["deleted"] = True
            self.save_games()
            self.filter_games() # Refresh the view
            self.show_toast("Jeu supprimé", f"'{game_data['name']}' a été déplacé dans la corbeille.", "warning")

            # Achievement check
            deleted_count = self.settings.get("deleted_games_count", 0) + 1
            self.save_settings("deleted_games_count", deleted_count)
            if deleted_count >= 5:
                self.check_and_unlock_achievement("achievement_minimaliste")

    def _mark_dirty(self, pages: list[str]):
        for page in pages:
            if page in self.pages_dirty:
                self.pages_dirty[page] = True

    def focus_search(self, event=None):
        self.show_page("games")
        self.search_entry.focus_set()

    def unlock_achievement_1(self, event=None):
        self.check_and_unlock_achievement("achievement_1")

    def verify_dependencies_on_startup(self):
        pass # Placeholder

    def start_update_check(self, manual=False):
        """Starts the update check in a background thread to not freeze the UI."""
        threading.Thread(target=self._check_for_updates_worker, args=(manual,), daemon=True).start()

    def _check_for_updates_worker(self, manual=False):
        """Fetches version info from a URL and compares with local version."""
        # This URL should point to a raw JSON file on your GitHub repo or another server.
        UPDATE_URL = "https://raw.githubusercontent.com/dodosi/dodoxi/main/version.json"
        try:
            with urllib.request.urlopen(UPDATE_URL, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            latest_version = data.get("latest_version")
            release_url = data.get("release_url")

            # Simple version comparison (e.g., "v0.17.0" > "v0.16.0")
            if latest_version and release_url and latest_version > VERSION:
                self.after(0, self.show_update_notification, latest_version, release_url)
            elif manual:
                self.after(0, messagebox.showinfo, "Mise à jour", "Vous utilisez déjà la dernière version.")

        except Exception as e:
            log_crash("Failed to check for updates", e)
            if manual:
                self.after(0, messagebox.showerror, "Erreur", "Impossible de vérifier les mises à jour.\n"
                                                              "Veuillez vérifier votre connexion internet ou le journal d'erreurs.")

    def show_whats_new_window(self):
        win = tk.Toplevel(self)
        win.title("Nouveautés")
        win.geometry("500x450")
        win.transient(self)
        win.grab_set()

        header_frame = ttk.Frame(win, padding=20)
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text=f"Nouveautés de la v{VERSION}", font=("Segoe UI", 16, "bold")).pack()

        text_frame = ScrolledFrame(win, autohide=True)
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)

        news_text = """
Bienvenue sur la nouvelle version du lanceur !

Voici les principales améliorations :

▪️ Système de Notation par Étoiles
Vous pouvez maintenant noter chaque jeu de 1 à 5 étoiles directement depuis sa carte. Triez votre bibliothèque par note pour retrouver rapidement vos préférés !

▪️ Mode Portable
Créez un fichier vide nommé "portable.txt" à côté du lanceur pour qu'il stocke toutes ses données dans un dossier "data". Idéal pour une utilisation sur clé USB.

▪️ Stabilité et Fluidité Accrues
De nombreux bugs causant des crashs et des ralentissements ont été corrigés. L'application est maintenant plus stable et réactive, notamment lors du redimensionnement de la fenêtre.

▪️ Améliorations Visuelles
Les actions de maintenance dans les paramètres ont maintenant des icônes pour une meilleure lisibilité.
"""
        ttk.Label(text_frame, text=news_text, wraplength=450, justify="left").pack(pady=10)

        ok_button = ttk.Button(win, text="Compris !", command=win.destroy, bootstyle="success")
        ok_button.pack(pady=20)

        self.save_settings("last_seen_version", VERSION)

    def show_update_notification(self, new_version, url):
        if messagebox.askyesno(
            "Mise à jour disponible",
            f"Une nouvelle version ({new_version}) est disponible !\n"
            "Voulez-vous ouvrir la page de téléchargement ?"
        ):
            webbrowser.open(url)
            self.check_and_unlock_achievement("achievement_updater")
        self.save_settings("last_seen_version", VERSION)

    def create_default_gradient(self):
        if os.path.exists(GRADIENT_DEFAULT_PATH): return
        try:
            width, height = 200, 200
            start_color = (40, 40, 60)
            end_color = (20, 20, 30)
            image = Image.new("RGB", (width, height))
            draw = ImageDraw.Draw(image)
            for y in range(height):
                r = int(start_color[0] + (end_color[0] - start_color[0]) * y / height)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * y / height)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * y / height)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            image.save(GRADIENT_DEFAULT_PATH)
        except Exception as e:
            log_crash("Failed to create default gradient", e)

    def create_default_icon(self):
        if os.path.exists(DEFAULT_GAME_ICON): return
        try:
            width, height = 128, 128
            image = Image.new("RGB", (width, height), color = (80, 80, 80))
            draw = ImageDraw.Draw(image)
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            draw.text((width/4, height/2.5), "No Icon", font=font, fill=(200, 200, 200))
            image.save(DEFAULT_GAME_ICON)
        except Exception as e:
            log_crash("Failed to create default icon", e)

    def check_and_unlock_achievement(self, key: str):
        k = self.achievements_data[key]["unlocked_key"]
        if not self.settings.get(k):
            self.save_settings(k, True)
            self.show_toast(f"Succès débloqué !", self.achievements_data[key]["name"], "success")

    def check_and_unlock_pro_pages_achievement(self):
        if len(self.session_pro_pages_visited) >= 3:
            self.check_and_unlock_achievement("achievement_grand_tour")

    def toggle_fullscreen(self):
        self.attributes("-fullscreen", self.fullscreen_var.get())
        self.save_settings("fullscreen", self.fullscreen_var.get())

    def toggle_autohide(self):
        self.save_settings("autohide_scrollbars", self.autohide_scrollbars_var.get())
        self.show_toast("Paramètre sauvegardé", "Le changement sera appliqué au redémarrage.", "info")

    def perform_first_run_setup(self): # New function for first run
        messagebox.showinfo(f"Bienvenue dans {APP_NAME} !",
                            "Pour commencer, veuillez sélectionner le dossier principal où se trouvent vos jeux Python.")
        self.change_games_folder()
        self.save_settings("first_run", False)

    def get_username(self):
        return self.settings.get("username", "Utilisateur")

    def update_username_in_ui(self):
        new_name = self.get_username()
        if self.sidebar_user_label:
            self.sidebar_user_label.config(text=new_name)
        if self.pro_username_label:
            self.pro_username_label.config(text=new_name)

    def change_username(self):
        current_name = self.get_username()
        new_name = simpledialog.askstring("Changer de nom", "Entrez votre nouveau nom d'utilisateur :", initialvalue=current_name, parent=self)
        if new_name and new_name.strip() and new_name != current_name:
            self.save_settings("username", new_name.strip())
            self.update_username_in_ui()
            self.show_toast("Nom d'utilisateur mis à jour", f"Votre nom est maintenant '{new_name.strip()}'.", "success")
            self.check_and_unlock_achievement("achievement_identity_change")

    # --- Maintenance Functions ---
    def export_data(self):
        path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Archive ZIP", "*.zip")], title="Exporter les données")
        if not path: return
        
        import zipfile
        try:
            with zipfile.ZipFile(path, 'w') as zf:
                if os.path.exists(GAMES_FILE): zf.write(GAMES_FILE, os.path.basename(GAMES_FILE))
                if os.path.exists(SETTINGS_FILE): zf.write(SETTINGS_FILE, os.path.basename(SETTINGS_FILE))
            self.show_toast("Exportation réussie", "Données exportées avec succès.", "success")
        except Exception as e:
            self.show_toast("Erreur d'exportation", str(e), "danger")

    def import_data(self):
        if not messagebox.askyesno("Importer les données", "Ceci écrasera vos données actuelles. Voulez-vous continuer ?"):
            return
        path = filedialog.askopenfilename(filetypes=[("Archive ZIP", "*.zip")], title="Importer les données")
        if not path: return

        import zipfile
        try:
            with zipfile.ZipFile(path, 'r') as zf:
                zf.extractall(SETTINGS_FOLDER)
            self.show_toast("Importation réussie", "Veuillez redémarrer l'application.", "success")
            self.after(1000, self.destroy)
        except Exception as e:
            self.show_toast("Erreur d'importation", str(e), "danger")

    def backup_data(self):
        import shutil
        backup_dir = os.path.join(SETTINGS_FOLDER, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            shutil.copy(GAMES_FILE, os.path.join(backup_dir, f"games_{timestamp}.json"))
            shutil.copy(SETTINGS_FILE, os.path.join(backup_dir, f"settings_{timestamp}.json"))
            self.show_toast("Sauvegarde créée", f"Sauvegarde créée dans le dossier 'backups'.", "success")
        except Exception as e:
            self.show_toast("Erreur de sauvegarde", str(e), "danger")

    def mark_missing_games_ui(self):
        count = self.check_missing_games()
        self.show_toast("Scan terminé", f"{count} jeu(x) marqué(s) comme manquant(s).", "info")
        self.filter_games()

    def remove_missing_games_ui(self):
        with self.games_lock:
            missing_count = sum(1 for g in self.games if g.get("missing"))
        if missing_count == 0:
            self.show_toast("Info", "Aucun jeu manquant à supprimer.", "info")
            return
        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer {missing_count} jeu(x) manquant(s) de votre bibliothèque ?"):
            with self.games_lock:
                self.games = [g for g in self.games if not g.get("missing")]
            self.save_games()
            self.filter_games()
            self.show_toast("Nettoyage terminé", f"{missing_count} jeu(x) supprimé(s).", "success")

    def deduplicate_games_ui(self):
        # Simple deduplication based on path
        seen_paths = set()
        unique_games = []
        with self.games_lock:
            games_to_check = list(self.games)

        for g in games_to_check:
            path = g.get("path")
            if path and path not in seen_paths:
                unique_games.append(g)
                seen_paths.add(path)
        removed_count = len(games_to_check) - len(unique_games)
        if removed_count > 0:
            with self.games_lock:
                self.games = unique_games
            self.save_games()
            self.filter_games()
        self.show_toast("Dédoublonnage terminé", f"{removed_count} doublon(s) supprimé(s).", "success" if removed_count > 0 else "info")

    def reset_all_data_ui(self):
        """Deletes all user data files and closes the application."""
        warning_message = (
            "ATTENTION : ACTION IRRÉVERSIBLE\n\n"
            "Vous êtes sur le point de supprimer TOUTES les données de l'application, y compris :\n"
            " - Votre bibliothèque de jeux\n"
            " - Tous vos paramètres\n"
            " - Toute votre progression de succès\n\n"
            "L'application se fermera et vous devrez la redémarrer.\n"
            "Êtes-vous absolument certain de vouloir continuer ?"
        )
        if not messagebox.askyesno(
            "Confirmation de réinitialisation totale",
            warning_message,
            parent=self,
            icon='error'
        ):
            return
        
        # Extra confirmation step
        confirmation_text = simpledialog.askstring(
            "Confirmation Finale",
            'Cette action est définitive. Pour confirmer, veuillez taper "RESET" dans le champ ci-dessous.',
            parent=self
        )

        if confirmation_text != "RESET":
            self.show_toast("Réinitialisation annulée", "Le texte de confirmation est incorrect.", "warning")
            return

        files_to_delete = [
            GAMES_FILE, GAMES_FILE + ".bak",
            SETTINGS_FILE, SETTINGS_FILE + ".bak",
            ACHIEVEMENTS_FILE, ACHIEVEMENTS_FILE + ".bak",
            CRASH_LOG_FILE
        ]

        failed_files = []
        for file_path in files_to_delete:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except OSError as e:
                failed_files.append(os.path.basename(file_path))
                log_crash(f"Failed to delete file during reset: {file_path}", e)

        if failed_files:
            messagebox.showerror("Erreur de réinitialisation", f"Certains fichiers n'ont pas pu être supprimés : {', '.join(failed_files)}\nVeuillez les supprimer manuellement.")
        else:
            messagebox.showinfo("Réinitialisation terminée", "Toutes les données ont été supprimées.\nL'application va maintenant se fermer. Veuillez la relancer.")
        
        self.destroy()

    def reset_achievements_ui(self):
        """Resets all achievements to their locked state."""
        if not messagebox.askyesno(
            "Confirmation",
            "Êtes-vous sûr de vouloir réinitialiser TOUS vos succès ?\n"
            "Cette action est irréversible.",
            parent=self,
            icon='warning'
        ):
            return

        # Iterate through all defined achievements and set their unlocked status to False
        for ach_data in self.achievements_data.values():
            unlocked_key = ach_data.get("unlocked_key")
            if unlocked_key and unlocked_key in self.settings:
                self.settings[unlocked_key] = False
        
        # Save all changes at once
        self.save_data(SETTINGS_FILE, self.settings)
        
        # Mark relevant pages as dirty to force a refresh
        self._mark_dirty(["main", "achievements", "pro"])

        # If we are on a relevant page, refresh it now for immediate feedback
        if self.current_page_frame == self.achievements_page_frame: self.update_achievements_page()
        elif self.current_page_frame == self.main_page_frame: self.update_main_page_stats()
        elif self.current_page_frame == self.pro_page_frame: self.update_pro_page()
            
        self.show_toast("Succès réinitialisés", "Tous les succès ont été verrouillés.", "success")

    def rename_category(self):
        selected_item = self.categories_tree.focus()
        if not selected_item:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une catégorie à renommer.")
            return

        old_name = self.categories_tree.item(selected_item)['values'][0]
        new_name = simpledialog.askstring("Renommer la catégorie", f"Nouveau nom pour '{old_name}':", parent=self)

        if new_name and new_name.strip() and new_name != old_name:
            new_name = new_name.strip()
            with self.games_lock:
                for game in self.games:
                    if old_name in game.get("categories", []):
                        game["categories"].remove(old_name)
                        if new_name not in game["categories"]:
                            game["categories"].append(new_name)
            
            self.save_games()
            self.populate_categories_treeview()
            self.show_toast("Catégorie renommée", f"'{old_name}' est devenu '{new_name}'.", "success")
            self.check_and_unlock_achievement("achievement_taxonomiste")

    def delete_category(self):
        selected_item = self.categories_tree.focus()
        if not selected_item:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une catégorie à supprimer.")
            return

        cat_name = self.categories_tree.item(selected_item)['values'][0]
        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer la catégorie '{cat_name}' de tous les jeux ?"):
            with self.games_lock:
                for game in self.games:
                    if cat_name in game.get("categories", []):
                        game["categories"].remove(cat_name)
            
            self.save_games()
            self.populate_categories_treeview()
            self.show_toast("Catégorie supprimée", f"La catégorie '{cat_name}' a été supprimée.", "success")
            self.check_and_unlock_achievement("achievement_taxonomiste")

    def create_collection_ui(self):
        name = simpledialog.askstring("Nouvelle collection", "Nom de la nouvelle collection :", parent=self)
        if name and name.strip():
            name = name.strip()
            if name in self.collections:
                messagebox.showwarning("Collection existante", f"La collection '{name}' existe déjà.")
                return
            self.collections[name] = []
            self.save_collections()
            self.populate_collections_treeview()
            self.update_collection_filter_menu()
            self.check_and_unlock_achievement("achievement_conservateur")

    def rename_collection_ui(self):
        selected_item = self.collections_tree.focus()
        if not selected_item:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une collection à renommer.")
            return

        old_name = self.collections_tree.item(selected_item)['values'][0]
        new_name = simpledialog.askstring("Renommer la collection", f"Nouveau nom pour '{old_name}':", parent=self)

        if new_name and new_name.strip() and new_name != old_name:
            new_name = new_name.strip()
            if new_name in self.collections:
                messagebox.showwarning("Collection existante", f"La collection '{new_name}' existe déjà.")
                return
            
            self.collections[new_name] = self.collections.pop(old_name)
            self.save_collections()
            self.populate_collections_treeview()
            self.update_collection_filter_menu()

    def delete_collection_ui(self):
        selected_item = self.collections_tree.focus()
        if not selected_item:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une collection à supprimer.")
            return

        name = self.collections_tree.item(selected_item)['values'][0]
        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer la collection '{name}' ?\n(Les jeux ne seront pas supprimés de la bibliothèque)"):
            del self.collections[name]
            self.save_collections()
            self.populate_collections_treeview()
            self.update_collection_filter_menu()

    def show_game_context_menu(self, event, game_data):
        context_menu = tk.Menu(self, tearoff=0)
        
        collections_menu = tk.Menu(context_menu, tearoff=0)
        context_menu.add_cascade(label="Ajouter à la collection", menu=collections_menu)
        
        if not self.collections:
            collections_menu.add_command(label="(Aucune collection)", state="disabled")
        else:
            for name in sorted(self.collections.keys()):
                var = tk.BooleanVar(value=(game_data['path'] in self.collections[name]))
                collections_menu.add_checkbutton(label=name, variable=var, 
                                                command=lambda g=game_data, c=name: self.toggle_game_in_collection(g, c))

        collections_menu.add_separator()
        collections_menu.add_command(label="Nouvelle collection...", command=self.create_collection_ui)
        
        context_menu.post(event.x_root, event.y_root)

    def toggle_game_in_collection(self, game_data, collection_name):
        game_path = game_data['path']
        if game_path in self.collections[collection_name]:
            self.collections[collection_name].remove(game_path)
        else:
            self.collections[collection_name].append(game_path)
        self.save_collections()
        self.populate_collections_treeview() # Update game count

    def open_theme_editor(self):
        editor = tk.Toplevel(self)
        editor.title("Éditeur de Thème")
        editor.transient(self)
        editor.grab_set()

        colors = self.settings.get("custom_theme_colors", {}).copy()
        color_vars = {}

        main_frame = ttk.Frame(editor, padding=20)
        main_frame.pack(fill="both", expand=True)

        def _pick_color(key, var, preview):
            from ttkbootstrap.dialogs.colorchooser import ColorChooserDialog
            dialog = ColorChooserDialog(initialcolor=var.get(), parent=editor)
            dialog.show()
            if dialog.result:
                var.set(dialog.result.hex)
                preview.configure(background=dialog.result.hex)

        color_keys = ["primary", "secondary", "success", "info", "warning", "danger", "light", "dark"]
        for i, key in enumerate(color_keys):
            ttk.Label(main_frame, text=f"{key.capitalize()}:").grid(row=i, column=0, sticky="w", padx=5, pady=5)
            color_vars[key] = tk.StringVar(value=colors.get(key, self.app_style.colors.get(key, "#ffffff")))
            preview = tk.Frame(main_frame, width=100, height=25, background=color_vars[key].get(), relief="solid", borderwidth=1)
            preview.grid(row=i, column=1, padx=5, pady=5)
            ttk.Button(main_frame, text="Choisir...", command=lambda k=key, v=color_vars[key], p=preview: _pick_color(k, v, p)).grid(row=i, column=2, padx=5, pady=5)

        def _save_theme():
            for key, var in color_vars.items():
                colors[key] = var.get()
            self.settings["custom_theme_colors"] = colors
            self.save_settings("theme", "custom")
            self.check_and_unlock_achievement("achievement_maestro_themes")
            editor.destroy()

        ttk.Button(main_frame, text="Sauvegarder et Appliquer", command=_save_theme, bootstyle="success").grid(row=len(color_keys), column=0, columnspan=3, pady=20)

    def _update_rating_widget(self, parent, game_data):
        for w in parent.winfo_children():
            w.destroy()
        
        current_rating = game_data.get("rating", 0)
        
        for i in range(1, 6):
            star_char = "★" if i <= current_rating else "☆"
            star_color = "warning" if i <= current_rating else "secondary"
            star_btn = ttk.Button(
                parent,
                text=star_char,
                bootstyle=(star_color, "link"),
                command=lambda g=game_data, r=i: self.set_rating(g, r)
            )
            star_btn.pack(side="left")

    def set_rating(self, game_data, rating):
        with self.games_lock:
            game_data["rating"] = 0 if game_data.get("rating", 0) == rating else rating
        self.save_games()
        self.update_game_card_by_path(game_data["path"])
        self.check_and_unlock_achievement("achievement_critic")

if __name__ == "__main__":
    try:
        app = GameLauncher()
        app.mainloop()
    except Exception as e:
        # Enregistre le crash avant de quitter
        log_crash("L'application a rencontré une erreur fatale et va se fermer.", e)
        # Affiche aussi un message à l'utilisateur
        messagebox.showerror("Erreur Fatale", f"Une erreur inattendue est survenue: {e}\nConsultez crash_log.txt pour plus de détails.")
