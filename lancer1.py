# -*- coding: utf-8 -*-
# Mon Lanceur de Jeux Propulsé par IA - Version Réparée et Stabilisée (v0.17)
import os
import sys
import json
import datetime
import random
import subprocess
import traceback
import time
import shutil
import tkinter as tk
import threading
from tkinter import messagebox, filedialog, simpledialog
import webbrowser
import csv
import requests

# Optional GUI/third-party libs will be imported below and handled if missing.
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from ttkbootstrap.scrolled import ScrolledFrame
    from ttkbootstrap.tooltip import ToolTip
    from ttkbootstrap.widgets import Meter
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import platformdirs
except ImportError as e:
    # If imports fail, present a minimal dialog offering to install deps.
    def log_crash_early(message: str, exception: Exception | None = None):
        try:
            log_dir = os.path.join(os.path.expanduser("~"), "Dodoxi_logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "early_crash.log")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"EARLY CRASH - {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n")
                f.write(f"Message: {message}\n")
                if exception:
                    f.write(f"Error: {exception}\n")
                    f.write(traceback.format_exc())
                f.write("-" * 40 + "\n")
        except Exception:
            pass

    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Dépendances manquantes",
        f"Une dépendance requise est manquante: {e.name}.\n"
        f"Veuillez installer les dépendances en utilisant la commande suivante:\n"
        f"pip install -r requirements.txt"
    )
    sys.exit(1)

# --- Constants and Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Portable Mode Check and SETTINGS_FOLDER definition
if os.path.exists(os.path.join(SCRIPT_DIR, "portable.txt")):
    SETTINGS_FOLDER = os.path.join(SCRIPT_DIR, "data")
    # If portable, games folder is relative to script
    GAMES_FOLDER_DEFAULT = os.path.join(SCRIPT_DIR, "jeux")
else:
    # If not portable, use platformdirs for settings and games folders
    # If not portable, use platformdirs for settings and games folders
    try:
        SETTINGS_FOLDER = os.path.join(platformdirs.user_data_dir(appname="Dodoxi", appauthor="dodosi"), "settings")
        GAMES_FOLDER_DEFAULT = os.path.join(platformdirs.user_documents_dir(), "Dodoxi Games")
    except Exception:
        # If platformdirs isn't available or fails, fall back to local data folder
        SETTINGS_FOLDER = os.path.join(SCRIPT_DIR, "data")
        GAMES_FOLDER_DEFAULT = os.path.join(SCRIPT_DIR, "jeux")
JAVA_GAMES_FOLDER = os.path.join(SCRIPT_DIR, "java")

# Ensure SETTINGS_FOLDER exists before defining files within it
if not os.path.exists(SETTINGS_FOLDER):
    os.makedirs(SETTINGS_FOLDER)

GAMES_FOLDER = GAMES_FOLDER_DEFAULT # This will be the initial default, but can be changed by user
IMAGES_FOLDER = os.path.join(SCRIPT_DIR, "images")
SOUNDS_FOLDER = os.path.join(SCRIPT_DIR, "sounds")
SETTINGS_FILE = os.path.join(SETTINGS_FOLDER, "settings.json")
GAMES_FILE = os.path.join(SETTINGS_FOLDER, "games.json")
ACHIEVEMENTS_FILE = os.path.join(SETTINGS_FOLDER, "achievements.json")
COLLECTIONS_FILE = os.path.join(SETTINGS_FOLDER, "collections.json")
CRASH_LOG_FILE = os.path.join(SETTINGS_FOLDER, "crash_log.txt")
GRADIENT_DEFAULT_PATH = os.path.join(IMAGES_FOLDER, "gradient_default.png")
DEFAULT_GAME_ICON = os.path.join(IMAGES_FOLDER, "default_icon.png")
ACHIEVEMENT_SOUND = os.path.join(SOUNDS_FOLDER, "achievement.wav")
TOAST_SOUND = os.path.join(SOUNDS_FOLDER, "toast.wav")

# --- App Info ---
VERSION = "v0.17"
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
        try:
            print(f"Échec du log crash: {e}")
        except Exception:
            pass

def show_fatal_error_dialog(error_message: str, exception_object: Exception):
    """Logs a crash and displays a custom fatal error dialog with a copy button."""
    # Log the crash first to ensure the report is saved.
    log_crash(error_message, exception_object)

    # Prepare the full report for display and copying.
    full_report = (
        f"Rapport d'erreur - {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n"
        f"Version: {VERSION}\n"
        f"Message: {error_message}\n"
        f"Erreur: {exception_object}\n"
        "Traceback:\n"
        f"{traceback.format_exc()}"
    )

    try:
        # Create a temporary root window to host the dialog
        root = tk.Tk()
        root.withdraw()

        # Use ttkbootstrap if available for a better look
        try:
            import ttkbootstrap as ttk
            style = ttk.Style(theme='darkly') # A safe default theme
            dialog = ttk.Toplevel(root)
        except ImportError:
            from tkinter import ttk
            dialog = tk.Toplevel(root)

        dialog.title("Erreur Fatale")
        dialog.geometry("700x450")
        dialog.minsize(500, 300)
        
        dialog.transient(root)
        dialog.grab_set()

        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        ttk.Label(main_frame, text="L'application a rencontré une erreur fatale.", font=("Segoe UI", 14, "bold"), foreground="red").grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='w')

        text_area = tk.Text(main_frame, wrap="word", height=10, width=70, font=("Courier New", 9), relief="flat", borderwidth=1)
        text_area.insert("1.0", full_report)
        text_area.config(state="disabled")
        text_area.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=text_area.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        text_area.config(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0), sticky='e')

        # --- Countdown and Close Logic ---
        timer_id = None
        def close_dialog():
            nonlocal timer_id
            if timer_id:
                try:
                    dialog.after_cancel(timer_id)
                except tk.TclError:
                    pass # Dialog might already be gone
            timer_id = None
            root.destroy()
            sys.exit(1)

        def countdown(seconds_left=10):
            nonlocal timer_id
            if seconds_left > 0:
                countdown_label.config(text=f"Fermeture auto dans {seconds_left}s")
                timer_id = dialog.after(1000, countdown, seconds_left - 1)
            else:
                close_dialog()

        countdown_label = ttk.Label(button_frame, text="")
        countdown_label.pack(side="left", padx=(0, 20))

        copy_button = ttk.Button(button_frame, text="Copier le rapport")
        def copy_report():
            dialog.clipboard_clear()
            dialog.clipboard_append(full_report)
            dialog.update() # Make sure clipboard content is available
            original_text = copy_button.cget("text")
            copy_button.config(text="Copié !", state="disabled")
            dialog.after(1500, lambda: copy_button.config(text=original_text, state="normal"))
        copy_button.config(command=copy_report)

        ttk.Button(button_frame, text="Fermer", command=close_dialog).pack(side="right", padx=(5, 0))
        copy_button.pack(side="right")
        
        dialog.protocol("WM_DELETE_WINDOW", close_dialog)
        countdown() # Start the auto-close timer
        dialog.wait_window()

    except (tk.TclError, ImportError, RuntimeError) as final_e:
        log_crash("Failed to display custom fatal error dialog", final_e)
        messagebox.showerror("Erreur Fatale", f"Une erreur inattendue est survenue: {exception_object}\nConsultez crash_log.txt pour plus de détails.")
        sys.exit(1)

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

def play_sound(sound_path: str, enabled: bool):
    """Plays a sound in a separate thread to avoid blocking the UI."""
    if not enabled or not os.path.exists(sound_path):
        return

    def _play():
        try:
            # Import locally to avoid dependency error if user chooses not to install
            from playsound import playsound
            playsound(sound_path)
        except Exception as e:
            # Log this silently, as it's not a critical error
            log_crash(f"Failed to play sound: {sound_path}", e)

    threading.Thread(target=_play, daemon=True).start()



class ManualScrolledFrame(ttk.Frame): # noqa: E722
    """A simplified and reliable scrolled frame using a Canvas and an inner Frame.
    This version focuses on performance and standard behavior, removing custom animations."""
    def __init__(self, master=None, autohide=True, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.v_scroll = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)
        
        # Match canvas background to parent for seamless look
        try:
            style = ttk.Style()
            bg = style.lookup(self.winfo_class(), 'background')
            self.canvas.configure(bg=bg)
        except tk.TclError:
            pass # Style not found, use default

        self.v_scroll.grid(row=0, column=1, sticky='ns')
        self.canvas.grid(row=0, column=0, sticky='nsew')

        self.container = ttk.Frame(self.canvas)
        self._window_id = self.canvas.create_window((0, 0), window=self.container, anchor='nw')

        # --- Bindings for layout and scrolling ---
        self.container.bind('<Configure>', self._on_container_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # This is the key for smooth scrolling: bind when mouse enters, unbind when it leaves.
        self.bind('<Enter>', self._bind_mouse_wheel)
        self.bind('<Leave>', self._unbind_mouse_wheel)

        # Autohide scrollbar
        self._autohide = autohide
        self._scrollbar_hide_after = None
        if self._autohide:
            self.v_scroll.grid_remove()
            self.bind('<Enter>', self._show_sb, add='+')
            self.bind('<Leave>', self._hide_sb, add='+')

    def _on_container_configure(self, event):
        """Called when the container frame's size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Called when the canvas's size changes."""
        self.canvas.itemconfigure(self._window_id, width=event.width)

    def _on_mousewheel(self, event):
        """Handles mouse wheel scrolling in a cross-platform way."""
        # The delta is different on each platform
        if sys.platform.startswith('linux'): # Linux
            if event.num == 5:
                delta = 1
            elif event.num == 4:
                delta = -1
            else:
                delta = 0
        elif sys.platform == 'darwin': # macOS
            delta = event.delta
        else: # Windows
            delta = -1 * int(event.delta / 120)
        
        self.canvas.yview_scroll(delta, "units")

    def _bind_mouse_wheel(self, event):
        """Bind mouse wheel scrolling for the entire application."""
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        if sys.platform.startswith('linux'):
            self.bind_all("<Button-4>", self._on_mousewheel)
            self.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mouse_wheel(self, event):
        """Unbind mouse wheel scrolling."""
        self.unbind_all("<MouseWheel>")
        if sys.platform.startswith('linux'):
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")

    def _show_sb(self, e=None):
        """Show the scrollbar."""
        if self._autohide:
            if self._scrollbar_hide_after:
                self.after_cancel(self._scrollbar_hide_after)
                self._scrollbar_hide_after = None
            self.v_scroll.grid()

    def _hide_sb(self, e=None):
        """Schedule the scrollbar to hide."""
        if self._autohide:
            self._scrollbar_hide_after = self.after(500, self.v_scroll.grid_remove)

    def update_scrollregion(self):
        """A public method to manually update the scroll region."""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    # --- Classe Principale de l'Application ---
class GameLauncher(ttk.Window): # Main application class
    def __init__(self):
        themename = self._load_theme()
        super().__init__(themename=themename, title=APP_NAME)
        self.withdraw() # Cacher la fenêtre principale pendant le chargement
        self.app_style = ttk.Style()
        self.show_loading_screen_and_initialize()

    def show_loading_screen_and_initialize(self):
        """Affiche une fenêtre de chargement et lance l'initialisation en arrière-plan."""
        self.loading_window = tk.Toplevel(self)
        self.loading_window.overrideredirect(True)
        w, h = 450, 150
        x = self.winfo_screenwidth() // 2 - w // 2
        y = self.winfo_screenheight() // 2 - h // 2
        self.loading_window.geometry(f"{w}x{h}+{x}+{y}")
        self.loading_window.transient(self)
        self.loading_window.lift()

        loading_frame = ttk.Frame(self.loading_window, padding=20, bootstyle="primary")
        loading_frame.pack(fill="both", expand=True)

        ttk.Label(loading_frame, text=f"{APP_NAME} - Chargement...", font=("Segoe UI", 12, "bold"), bootstyle="inverse-primary").pack(pady=(0, 10))
        self.loading_label = ttk.Label(loading_frame, text="Démarrage...", bootstyle="inverse-primary")
        self.loading_label.pack(pady=5)
        self.loading_progress = ttk.Progressbar(self.loading_window, mode='determinate', length=300, bootstyle="success")
        self.loading_progress.pack(pady=10)

        threading.Thread(target=self._perform_startup_tasks, daemon=True).start()

    def _update_loading_status(self, text, value):
        """Met à jour l'interface de la fenêtre de chargement depuis le thread de travail."""
        if hasattr(self, 'loading_window') and self.loading_window.winfo_exists():
            self.loading_label.config(text=text)
            self.loading_progress['value'] = value
            self.loading_window.update_idletasks()

    def _perform_startup_tasks(self):
        """Exécute les tâches de chargement de données et de traitement initial."""
        self.after(0, lambda: self._update_loading_status("Initialisation...", 0))

        # --- Initialisation des variables d'instance ---
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
        self.menubar_frame = None # For the custom menubar
        self.scan_in_progress = threading.Event()
        self.games_lock = threading.Lock()
        self.is_updating_view = False # Flag to prevent scrolling during view updates
        self.game_card_widgets = {}
        self.icon_cache = {}
        self.page_map = {}
        self.sidebar_buttons = {}
        self.gradient_cache = {}

        self.collection_filter = None
        self.collections = {} # Will be loaded from file
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
        self.pro_top_games_chart_frame = None
        self.pro_cat_chart_frame = None
        self.pro_suggestion_frame = None

        self.pages_dirty = {"main": True, "games": True, "achievements": True}

        self.after(0, lambda: self._update_loading_status("Vérification des dossiers...", 10))
        self.ensure_directories()

        # --- Chargement des données et initialisation des variables dépendantes ---
        self.after(0, lambda: self._update_loading_status("Chargement des succès...", 20))
        self.achievements_data = self.load_achievements()
        self.after(0, lambda: self._update_loading_status("Chargement des collections...", 30))
        self.collections = self.load_collections()
        self.after(0, lambda: self._update_loading_status("Chargement des paramètres...", 40))
        self.settings = self.load_settings()
        self.after(0, lambda: self._update_loading_status("Chargement de la bibliothèque...", 50))
        self.games = self.load_games()

        # --- Traitement initial des données ---
        self.after(0, lambda: self._update_loading_status("Synchronisation de la bibliothèque...", 70))
        library_was_modified = self._sync_library_on_startup()
        
        if library_was_modified:
            self.after(0, lambda: self._update_loading_status("Sauvegarde de la bibliothèque...", 80))
            self.save_games()
        self.after(0, lambda: self._update_loading_status("Vérification de la fidélité...", 90))
        self.check_loyalty_achievement()

        self.after(0, self._finish_ui_setup)

    # --- Small UX helpers added for v0.17 enhancements ---
    def _fade_transition(self, from_frame, to_frame, duration=200):
        """Simple fade transition using an overlay canvas; non-blocking."""
        try:
            if from_frame is to_frame or getattr(self, 'is_transitioning', False):
                return
            self.is_transitioning = True
            overlay = tk.Canvas(self, highlightthickness=0, bg='')
            overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            steps = max(3, int(duration // 30))
            alpha_values = [i/steps for i in range(0, steps+1)]

            def step_in(i=0):
                try:
                    if i > steps:
                        # switch frames then fade out
                        if hasattr(from_frame, 'place_forget'):
                            from_frame.place_forget()
                        try:
                            to_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
                        except Exception:
                            pass
                        self.after(10, lambda: step_out(steps))
                        return
                    color = f"#{int(0):02x}{int(0):02x}{int(0):02x}"
                    overlay.configure(bg=color)
                    overlay.lift()
                    self.after(30, lambda: step_in(i+1))
                except Exception:
                    self.is_transitioning = False

            def step_out(i):
                try:
                    if i < 0:
                        overlay.destroy()
                        self.is_transitioning = False
                        return
                    overlay.configure(bg='')
                    self.after(30, lambda: step_out(i-1))
                except Exception:
                    overlay.destroy()
                    self.is_transitioning = False

            step_in(0)
        except Exception:
            self.is_transitioning = False

    def _highlight_matching_game_cards(self, text):
        """Highlight game cards whose title contains text (case-insensitive)."""
        try:
            q = (text or '').strip().lower()
            for gid, widgets in self.game_card_widgets.items():
                try:
                    title = widgets.get('title_text', '')
                    frame = widgets.get('frame')
                    if not frame:
                        continue
                    if q and q in title.lower():
                        try:
                            frame.configure(style='Highlight.TFrame')
                        except Exception:
                            frame.configure(background='#fff4b1')
                    else:
                        try:
                            frame.configure(style='Dashboard.TFrame')
                        except Exception:
                            frame.configure(background='')
                except Exception:
                    continue
        except Exception:
            pass

    def _finish_ui_setup(self):
        """Crée l'interface utilisateur principale une fois les données chargées."""

        # Variables dépendantes des 'settings'
        self.current_background_path = self.settings.get("background", "")
        self.theme_change_count = self.settings.get("theme_change_count", 0)
        self.fullscreen_var = tk.BooleanVar(value=self.settings.get("fullscreen", False))
        self.autohide_scrollbars_var = tk.BooleanVar(value=self.settings.get("autohide_scrollbars", True))
        self.font_size_var = tk.StringVar(value=self.settings.get("font_size", "Moyen"))
        self.corner_radius_var = tk.IntVar(value=self.settings.get("corner_radius", 8))
        self.animation_type_var = tk.StringVar(value=self.settings.get("page_transition_animation", "Glissement"))
        self.view_mode = tk.StringVar(value=self.settings.get("view_mode", "Grille"))
        self.enable_sounds_var = tk.BooleanVar(value=self.settings.get("enable_sounds", True))

        # Apply saved window geometry
        saved_width = self.settings.get("window_width", 2000)
        saved_height = self.settings.get("window_height", 1700)
        saved_pos_x = self.settings.get("window_pos_x")
        saved_pos_y = self.settings.get("window_pos_y")

        if saved_pos_x is not None and saved_pos_y is not None:
            self.geometry(f"{saved_width}x{saved_height}+{saved_pos_x}+{saved_pos_y}")
        else:
            # If no saved position, center the window
            self.update_idletasks() # Ensure window dimensions are calculated
            x = (self.winfo_screenwidth() // 2) - (saved_width // 2)
            y = (self.winfo_screenheight() // 2) - (saved_height // 2)
            self.geometry(f"{saved_width}x{saved_height}+{x}+{y}")

        # Apply fullscreen setting right after geometry, before showing the window
        if self.fullscreen_var.get():
            self.attributes("-fullscreen", True)

        # Création du conteneur pour les notifications "toast"
        self.toast_container = ttk.Frame(self)
        self.toast_container.place(relx=0.99, rely=0.98, anchor="se")
        self.toast_container.lift()
        # Empêche les toasts d'intercepter les clics de la fenêtre principale
        self.toast_container.bind("<Button-1>", lambda e: "break")

        self.minsize(900, 700)

        self._init_styles()

        # Variables pour les filtres et le tri
        self.sort_order = tk.StringVar(value="Nom (A-Z)")
        self.show_favorites_only = tk.BooleanVar(value=False)
        self.category_filter = tk.StringVar(value="Toutes")

        self.create_default_gradient()
        self.apply_background_setting()
        self.create_default_icon()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Frame for the custom menubar
        self.menubar_frame = ttk.Frame(self, style="Nav.TFrame")
        self.menubar_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.sidebar_frame = ttk.Frame(self, style="Sidebar.TFrame")
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew")

        self.content_frame = ttk.Frame(self) # Frame for main content
        self.content_frame.grid(row=1, column=1, sticky="nsew")
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
        # Création de la sidebar et de la menubar après les pages pour que les commandes fonctionnent
        self.create_sidebar()
        self.create_menubar()
        self.resize_timer = None
        self.bind("<Configure>", self.delayed_resize)
        self.bind("<Control-o>", self.unlock_achievement_1)
        self.bind("<Control-f>", self.focus_search)
    # F5 scan binding removed per user request to prevent accidental scans
        self.bind_all("<F11>", self._toggle_fullscreen_event)
        self.bind("<Control-r>", lambda e: self.lancer_jeu_aleatoire()) # Keybind to launch a random game
        # Keyboard navigation: Ctrl+1..5 to jump pages; Left/Right to navigate
        try:
            self.bind_all('<Control-1>', lambda e: self.show_page('main'))
            self.bind_all('<Control-2>', lambda e: self.show_page('games'))
            self.bind_all('<Control-3>', lambda e: self.show_page('achievements'))
            self.bind_all('<Control-4>', lambda e: self.show_page('settings'))
            self.bind_all('<Control-5>', lambda e: self.show_page('pro'))
            self.bind_all('<Left>', lambda e: self._navigate_page(-1))
            self.bind_all('<Right>', lambda e: self._navigate_page(1))
        except Exception:
            pass
        self.running_processes = {}
        self.protocol("WM_DELETE_WINDOW", self._on_closing) # Handle window close button
        self.after(500, self.verify_dependencies_on_startup)

        if self.settings.get("first_run", True):
            self.after(500, self.perform_first_run_setup) # Guide the user on first launch

        # Show 'what's new' after an update, but not on the very first run.
        if not self.settings.get("first_run", True) and self.settings.get("last_seen_version") != VERSION: # Show 'what's new' after update.
            self.after(1000, self.show_whats_new_window)

        # Check for portable mode achievement
        if os.path.exists(os.path.join(SCRIPT_DIR, "portable.txt")):
            self.check_and_unlock_achievement("achievement_portable")
        
        self.after(5000, self.start_update_check) # Check for updates a few seconds after launch

        # Finalisation
        if hasattr(self, 'loading_window'): self.loading_window.destroy()
        self.deiconify()
        # Prevent most widgets from keeping a persistent focus highlight
        try:
            self.bind_all('<Button-1>', self._suppress_widget_highlight, add=True)
        except Exception:
            pass
        
    def _on_closing(self):
        # Save current geometry before closing
        self.save_settings("window_width", self.winfo_width())
        self.save_settings("window_height", self.winfo_height())
        self.save_settings("window_pos_x", self.winfo_x())
        self.save_settings("window_pos_y", self.winfo_y())
        super().destroy() # Call the original destroy method

    def _navigate_page(self, delta:int):
        try:
            order = self.page_order
            try:
                idx = order.index(self.frame_map.get(self.current_page_frame))
            except Exception:
                # find by value mapping
                cur = self.current_page_frame
                idx = 0
                for i,k in enumerate(order):
                    if self.page_map.get(k) == cur:
                        idx = i
                        break
            new_idx = (idx + delta) % len(order)
            self.show_page(order[new_idx])
        except Exception:
            pass

    def _suppress_widget_highlight(self, event):
        """Prevent most widgets from keeping focus (removes persistent highlighting).

        Allows Entry/Text widgets to receive focus normally. For other widgets,
        clicking will return focus to the main window which prevents focus
        highlight from showing.
        """
        try:
            w = event.widget
            # Allow text-entry widgets to receive focus
            cls = w.winfo_class().lower()
            if cls in ('entry', 'text'):
                return

            # Some ttk widgets report class 'TEntry' or similar; check name
            if hasattr(w, 'configure') and 'insertbackground' in w.configure():
                return

            # Otherwise, move focus back to the root window to avoid highlight
            try:
                self.focus_set()
            except Exception:
                pass
        except Exception:
            pass

    # --- Splash & Animations ---
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
                try:
                    # After all items are loaded, give the UI a moment to settle, then
                    # explicitly update the scrollregion of the parent scrolled frame.
                    def _finalize_scroll():
                        parent = container
                        while parent and not isinstance(parent, ManualScrolledFrame):
                            parent = parent.master
                        if parent and isinstance(parent, ManualScrolledFrame):
                            parent.update_scrollregion()
                    self.after(100, _finalize_scroll)
                except Exception:
                    pass

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

    def show_confetti_animation(self, duration=3500):
        """Displays a full-screen confetti animation for rare achievements."""
        if self.is_transitioning: return

        confetti_window = tk.Toplevel(self)
        confetti_window.overrideredirect(True)
        confetti_window.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{self.winfo_x()}+{self.winfo_y()}")
        confetti_window.attributes("-alpha", 0.9)
        confetti_window.attributes("-topmost", True)
        confetti_window.lift()
        confetti_window.transient(self)

        canvas = tk.Canvas(confetti_window, bg='black', highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        confetti_window.wm_attributes("-transparentcolor", "black")

        colors = [self.app_style.colors.primary, self.app_style.colors.success, self.app_style.colors.info, self.app_style.colors.warning, self.app_style.colors.danger, "#FFD700", "#C0C0C0"]
        confetti_particles = []

        for _ in range(250):
            x = random.randint(0, self.winfo_width())
            y = random.randint(-self.winfo_height(), 0)
            size = random.randint(6, 16)
            color = random.choice(colors)
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(2, 6)
            particle = canvas.create_rectangle(x, y, x + size, y + size, fill=color, outline="")
            confetti_particles.append({'id': particle, 'vx': vx, 'vy': vy})

        def _animate():
            if not confetti_window.winfo_exists(): return
            for p in confetti_particles:
                canvas.move(p['id'], p['vx'], p['vy'])
            self.after(16, _animate) # ~60 FPS

        _animate()
        confetti_window.after(duration, confetti_window.destroy)

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
        
        # --- Nouveaux succès ajoutés ---
        DEFAULT_ACHIEVEMENTS["achievement_matinal"] = {"name": "Le Matinal", "desc": "Lancer un jeu avant 8h du matin.", "unlocked_key": "achievement_matinal_unlocked", "icon_unlocked": "🌅", "icon_locked": "🔒", "difficulty": 10}
        DEFAULT_ACHIEVEMENTS["achievement_sprinteur"] = {"name": "Le Sprinteur", "desc": "Lancer 5 jeux différents en moins de 5 minutes.", "unlocked_key": "achievement_sprinteur_unlocked", "icon_unlocked": "💨", "icon_locked": "🔒", "difficulty": 15}
        DEFAULT_ACHIEVEMENTS["achievement_fidele_2"] = {"name": "Le Grand Fidèle", "desc": "Lancer l'application 30 jours différents.", "unlocked_key": "achievement_fidele_2_unlocked", "icon_unlocked": "🗓️", "icon_locked": "🔒", "difficulty": 30}
        DEFAULT_ACHIEVEMENTS["achievement_collectionneur_themes"] = {"name": "Le Collectionneur de Thèmes", "desc": "Essayer tous les thèmes disponibles.", "unlocked_key": "achievement_collectionneur_themes_unlocked", "icon_unlocked": "🌈", "icon_locked": "🔒", "difficulty": 20}
        DEFAULT_ACHIEVEMENTS["achievement_critique_art"] = {"name": "Le Critique d'Art", "desc": "Noter 10 jeux différents.", "unlocked_key": "achievement_critique_art_unlocked", "icon_unlocked": "🌟", "icon_locked": "🔒", "difficulty": 20}
        DEFAULT_ACHIEVEMENTS["achievement_bibliothecaire_chef"] = {"name": "Le Bibliothécaire en Chef", "desc": "Créer 10 catégories différentes.", "unlocked_key": "achievement_bibliothecaire_chef_unlocked", "icon_unlocked": "🗂️", "icon_locked": "🔒", "difficulty": 30}
        DEFAULT_ACHIEVEMENTS["achievement_conservateur_chef"] = {"name": "Le Conservateur en Chef", "desc": "Créer 5 collections différentes.", "unlocked_key": "achievement_conservateur_chef_unlocked", "icon_unlocked": "🗃️", "icon_locked": "🔒", "difficulty": 25}
        DEFAULT_ACHIEVEMENTS["achievement_duplicateur_serie"] = {"name": "Le Duplicateur en Série", "desc": "Dupliquer 5 jeux.", "unlocked_key": "achievement_duplicateur_serie_unlocked", "icon_unlocked": "🧬", "icon_locked": "🔒", "difficulty": 20}
        DEFAULT_ACHIEVEMENTS["achievement_grand_nettoyage_2"] = {"name": "Le Grand Nettoyage Nv.2", "desc": "Utiliser 5 outils de maintenance différents.", "unlocked_key": "achievement_grand_nettoyage_2_unlocked", "icon_unlocked": "🧼", "icon_locked": "🔒", "difficulty": 25}
        DEFAULT_ACHIEVEMENTS["achievement_marathonien_2"] = {"name": "Le Marathonien Confirmé", "desc": "Atteindre 2 heures de jeu au total.", "unlocked_key": "achievement_marathonien_2_unlocked", "icon_unlocked": "🏃", "icon_locked": "🔒", "difficulty": 35}
        DEFAULT_ACHIEVEMENTS["achievement_maitre_temps_2"] = {"name": "Le Maître du Temps Confirmé", "desc": "Atteindre 25 heures de jeu au total.", "unlocked_key": "achievement_maitre_temps_2_unlocked", "icon_unlocked": "🕰️", "icon_locked": "🔒", "difficulty": 45}
        DEFAULT_ACHIEVEMENTS["achievement_gardien_temps_2"] = {"name": "Le Gardien du Temps Ultime", "desc": "Atteindre 100 heures de jeu au total.", "unlocked_key": "achievement_gardien_temps_2_unlocked", "icon_unlocked": "⏳", "icon_locked": "🔒", "difficulty": 50}
        DEFAULT_ACHIEVEMENTS["achievement_ultime_joueur_2"] = {"name": "L'Ultime Joueur Nv.2", "desc": "Lancer un total de 250 jeux.", "unlocked_key": "achievement_ultime_joueur_2_unlocked", "icon_unlocked": "🏅", "icon_locked": "🔒", "difficulty": 40}
        DEFAULT_ACHIEVEMENTS["achievement_addict_2"] = {"name": "L'Addict Nv.2", "desc": "Lancer un total de 500 jeux.", "unlocked_key": "achievement_addict_2_unlocked", "icon_unlocked": "🕹️", "icon_locked": "🔒", "difficulty": 50}
        DEFAULT_ACHIEVEMENTS["achievement_devotion_2"] = {"name": "Dévotion Ultime", "desc": "Lancer 25 fois le même jeu.", "unlocked_key": "achievement_devotion_2_unlocked", "icon_unlocked": "🛐", "icon_locked": "🔒", "difficulty": 45}
        DEFAULT_ACHIEVEMENTS["achievement_perfectionniste_2"] = {"name": "Le Perfectionniste Nv.2", "desc": "Avoir 25 jeux avec icône et description personnalisées.", "unlocked_key": "achievement_perfectionniste_2_unlocked", "icon_unlocked": "🏆", "icon_locked": "🔒", "difficulty": 40}
        DEFAULT_ACHIEVEMENTS["achievement_grand_archiviste_2"] = {"name": "Le Grand Archiviste Nv.2", "desc": "Classifier 25 jeux avec au moins une catégorie.", "unlocked_key": "achievement_grand_archiviste_2_unlocked", "icon_unlocked": "🗄️", "icon_locked": "🔒", "difficulty": 38}
        DEFAULT_ACHIEVEMENTS["achievement_java_lover"] = {"name": "Java Lover", "desc": "Lancer un jeu Java.", "unlocked_key": "achievement_java_lover_unlocked", "icon_unlocked": "☕", "icon_locked": "🔒", "difficulty": 8}
        DEFAULT_ACHIEVEMENTS["achievement_python_lover"] = {"name": "Pythonista", "desc": "Lancer un jeu Python.", "unlocked_key": "achievement_python_lover_unlocked", "icon_unlocked": "🐍", "icon_locked": "🔒", "difficulty": 8}
        DEFAULT_ACHIEVEMENTS["achievement_collection_addict"] = {"name": "Collection Addict", "desc": "Ajouter un jeu à 3 collections différentes.", "unlocked_key": "achievement_collection_addict_unlocked", "icon_unlocked": "📚", "icon_locked": "🔒", "difficulty": 22}
        DEFAULT_ACHIEVEMENTS["achievement_full_backup"] = {"name": "Le Prévoyant", "desc": "Exporter et importer des données dans la même session.", "unlocked_key": "achievement_full_backup_unlocked", "icon_unlocked": "🔄", "icon_locked": "🔒", "difficulty": 18}
        DEFAULT_ACHIEVEMENTS["achievement_speed_demon"] = {"name": "Démon de la Vitesse", "desc": "Lancer 3 jeux en moins de 30 secondes.", "unlocked_key": "achievement_speed_demon_unlocked", "icon_unlocked": "🏎️", "icon_locked": "🔒", "difficulty": 25}
        DEFAULT_ACHIEVEMENTS["achievement_social"] = {"name": "Le Social", "desc": "Ouvrir le lien GitHub.", "unlocked_key": "achievement_social_unlocked", "icon_unlocked": "🌐", "icon_locked": "🔒", "difficulty": 4}
        DEFAULT_ACHIEVEMENTS["achievement_historien"] = {"name": "L'Historien", "desc": "Consulter les nouveautés d'une version.", "unlocked_key": "achievement_historien_unlocked", "icon_unlocked": "📜", "icon_locked": "🔒", "difficulty": 5}
        DEFAULT_ACHIEVEMENTS["achievement_minimaliste_2"] = {"name": "Le Grand Minimaliste", "desc": "Supprimer 10 jeux de la bibliothèque.", "unlocked_key": "achievement_minimaliste_2_unlocked", "icon_unlocked": "🗑️", "icon_locked": "🔒", "difficulty": 20}
        DEFAULT_ACHIEVEMENTS["achievement_maitre_icones_2"] = {"name": "Le Grand Maître des Icônes", "desc": "Attribuer une icône personnalisée à 20 jeux.", "unlocked_key": "achievement_maitre_icones_2_unlocked", "icon_unlocked": "🎨", "icon_locked": "🔒", "difficulty": 38}
        DEFAULT_ACHIEVEMENTS["achievement_critique_pro"] = {"name": "Le Critique Professionnel", "desc": "Ajouter une description à 10 jeux.", "unlocked_key": "achievement_critique_pro_unlocked", "icon_unlocked": "🖋️", "icon_locked": "🔒", "difficulty": 24}
        DEFAULT_ACHIEVEMENTS["achievement_collectionneur_legendaire"] = {"name": "Le Collectionneur Légendaire", "desc": "Avoir 50 jeux en favoris.", "unlocked_key": "achievement_collectionneur_legendaire_unlocked", "icon_unlocked": "🌌", "icon_locked": "🔒", "difficulty": 50}

        DEFAULT_ACHIEVEMENTS["achievement_critic"] = {"name": "Première Étoile", "desc": "Noter un jeu pour la première fois.", "unlocked_key": "achievement_critic_unlocked", "icon_unlocked": "🌟", "icon_locked": "🔒", "difficulty": 5}
        DEFAULT_ACHIEVEMENTS["achievement_portable"] = {"name": "Le Nomade", "desc": "Lancer l'application en mode portable.", "unlocked_key": "achievement_portable_unlocked", "icon_unlocked": "🎒", "icon_locked": "🔒", "difficulty": 10}
        DEFAULT_ACHIEVEMENTS["achievement_updater"] = {"name": "Le Visionnaire", "desc": "Vérifier s'il y a une nouvelle mise à jour.", "unlocked_key": "achievement_updater_unlocked", "icon_unlocked": "🚀", "icon_locked": "🔒", "difficulty": 6}
        DEFAULT_ACHIEVEMENTS["achievement_dependency"] = {"name": "Le Technicien", "desc": "Spécifier une dépendance pour un jeu.", "unlocked_key": "achievement_dependency_unlocked", "icon_unlocked": "⚙️", "icon_locked": "🔒", "difficulty": 12}
        DEFAULT_ACHIEVEMENTS["achievement_conservateur"] = {"name": "Le Conservateur", "desc": "Créer une collection de jeux.", "unlocked_key": "achievement_conservateur_unlocked", "icon_unlocked": "🗄️", "icon_locked": "🔒", "difficulty": 14}
        DEFAULT_ACHIEVEMENTS["achievement_maestro_themes"] = {"name": "Maestro des Thèmes", "desc": "Créer et sauvegarder un thème personnalisé.", "unlocked_key": "achievement_maestro_themes_unlocked", "icon_unlocked": "👑", "icon_locked": "🔒", "difficulty": 25}

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
            # Optional: Add new default achievements to an existing file
            updated = False
            for key, value in DEFAULT_ACHIEVEMENTS.items():
                if key not in data:
                    data[key] = value
                    updated = True
            if updated:
                try:
                    with open(ACHIEVEMENTS_FILE, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                except Exception as e:
                    log_crash("Failed to add new achievements to existing file.", e)
            return data
        except (json.JSONDecodeError, IOError) as e:
            log_crash(f"Failed to load or parse achievements.json, using defaults.", e)
            # Attempt to restore from backup if it exists
            backup_file = ACHIEVEMENTS_FILE + ".bak"
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, "r", encoding="utf-8") as f:
                        self.show_toast("Récupération", "Le fichier des succès a été restauré depuis une sauvegarde.", "info")
                        return json.load(f)
                except Exception as backup_e:
                    log_crash("Failed to restore achievements.json from backup.", backup_e)
            return DEFAULT_ACHIEVEMENTS

    def save_achievements(self):
        """Saves the current achievements data to its JSON file."""
        self.save_data(self.achievements_data, ACHIEVEMENTS_FILE)

    def load_collections(self):
        """Loads collections from a JSON file, creating it if it doesn't exist."""
        return self.load_data(COLLECTIONS_FILE, default_factory=dict)

    def save_collections(self):
        """Saves the current collections data to its JSON file."""
        self.save_data(self.collections, COLLECTIONS_FILE)

    def load_data(self, *args, **kwargs):
        """Robust JSON loader used throughout the app.

        Supports two call signatures for backward compatibility:
        - load_data(file_path, default_factory=list)
        - load_data(file_path, data_type_str, default_value)

        Returns the parsed JSON or a default value on errors. Attempts to
        restore from a .bak file if available.
        """
        # Normalize arguments
        if len(args) == 0:
            raise TypeError("load_data requires at least the file_path argument")
        file_path = args[0]

        # Default factory mode
        if len(args) == 1:
            default_factory = kwargs.get('default_factory', list)
            default_value = default_factory()
            data_type = os.path.basename(file_path)
        elif len(args) == 2:
            # Could be (file_path, default_factory) or (file_path, data_type_str)
            if callable(args[1]):
                default_factory = args[1]
                default_value = default_factory()
                data_type = os.path.basename(file_path)
            else:
                data_type = args[1]
                default_value = kwargs.get('default_value', None)
        elif len(args) >= 3:
            data_type = args[1]
            default_value = args[2]
        else:
            data_type = os.path.basename(file_path)
            default_value = kwargs.get('default_value', None)

        backup_path = file_path + ".bak"

        def _read_json(path):
            try:
                if not os.path.exists(path) or os.path.getsize(path) == 0:
                    return None
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None

        # Try primary file
        data = _read_json(file_path)
        if data is not None:
            return data

        log_crash(f"Données corrompues ou manquantes pour {os.path.basename(file_path)}. Tentative de restauration...")

        # Try backup
        backup_data = _read_json(backup_path)
        if backup_data is not None:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=4, ensure_ascii=False)
                try:
                    self.show_toast("Récupération", f"Le fichier de {data_type} a été restauré à partir d'une sauvegarde.", "info")
                except Exception:
                    pass
                return backup_data
            except Exception as e:
                log_crash(f"Échec de la restauration pour {file_path}", e)
                return backup_data

        # Create fresh default
        try:
            if os.path.exists(file_path):
                try:
                    os.rename(file_path, file_path + f".corrupt-{int(time.time())}")
                except Exception:
                    pass
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_value, f, indent=4, ensure_ascii=False)
            return default_value
        except Exception as e:
            log_crash(f"Impossible de créer le fichier de données {file_path}", e)
            try:
                messagebox.showerror("Erreur critique", f"Impossible de créer le fichier de données pour {data_type}.")
            except Exception:
                pass
            sys.exit(1)

    def save_data(self, *args):
        """Save JSON data to disk.

        Supports both call styles used in the codebase:
        - save_data(file_path, data)
        - save_data(data, file_path)

        Will create a .bak before overwriting and logs errors.
        """
        if len(args) != 2:
            raise TypeError("save_data requires exactly two positional arguments (file_path,data) or (data,file_path)")

        # Allow either order: detect if first arg is a path
        if isinstance(args[0], str):
            file_path, data = args[0], args[1]
        else:
            data, file_path = args[0], args[1]

        backup_path = file_path + ".bak"
        try:
            # Create a textual backup if the file exists
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f_src, open(backup_path, 'w', encoding='utf-8') as f_dst:
                        f_dst.write(f_src.read())
                except Exception:
                    # Best-effort backup; continue even if backup fails
                    pass

            # Write the new data
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            log_crash(f"Failed to save data to {os.path.basename(file_path)}", e)
            try:
                self.show_toast("Erreur de Sauvegarde", f"Impossible d'écrire dans {os.path.basename(file_path)}.", "error")
            except Exception:
                pass

    def load_settings(self):
        """Loads settings using the generic load_data function."""
        default_settings = {
            "username": "Dodoxi User",
            "theme": "darkly",
            "games_folder": GAMES_FOLDER_DEFAULT,
            "fullscreen": False,
            "autohide_scrollbars": True,
            "font_size": "Moyen",
            "corner_radius": 8,
            "page_transition_animation": "Glissement",
            "view_mode": "Grille",
            "enable_sounds": True,
            "first_run": True,
            "last_seen_version": VERSION,
            "last_run_date": datetime.date.today().isoformat(),
            "run_days_streak": 1,
            "theme_change_count": 0,
            "total_playtime": 0,
            "custom_theme_colors": {},
        }
        
        settings_data = self.load_data(SETTINGS_FILE, default_factory=lambda: default_settings)
        
        # Ensure all default keys exist in the loaded settings
        updated = False
        for key, value in default_settings.items():
            if key not in settings_data:
                settings_data[key] = value
                updated = True
        
        if updated:
            self.save_data(settings_data, SETTINGS_FILE)
            
        return settings_data

    def save_settings(self, key=None, value=None):
        """Saves a specific setting or the entire settings dictionary."""
        if key:
            self.settings[key] = value
        self.save_data(self.settings, SETTINGS_FILE)

    def load_games(self):
        """Loads games using the generic load_data function."""
        return self.load_data(GAMES_FILE, default_factory=list)

    
    def _create_gradient_photo(self, color1, color2, width, height):
        cache_key = (color1, color2, width, height)
        if cache_key in self.gradient_cache:
            return self.gradient_cache[cache_key]

        try:
            img = Image.new("RGB", (width, height))
            draw = ImageDraw.Draw(img)
            r1, g1, b1 = self.winfo_rgb(color1)
            r2, g2, b2 = self.winfo_rgb(color2)
            r1, g1, b1 = r1 >> 8, g1 >> 8, b1 >> 8
            r2, g2, b2 = r2 >> 8, g2 >> 8, b2 >> 8

            for i in range(height):
                t = i / height
                r = int(r1 * (1 - t) + r2 * t)
                g = int(g1 * (1 - t) + g2 * t)
                b = int(b1 * (1 - t) + b2 * t)
                draw.line([(0, i), (width, i)], fill=(r, g, b))
            
            photo = ImageTk.PhotoImage(img)
            self.gradient_cache[cache_key] = photo
            return photo
        except Exception as e:
            log_crash("Failed to create gradient photo", e)
            return self.default_gradient_photo # Return a default if creation fails

    def _apply_appearance_settings(self):
        """Applies font size and corner radius settings by re-initializing styles."""
        try:
            self._init_styles()
            # Mark all pages as dirty to force a full redraw with new styles
            for page in self.page_map.keys():
                self._mark_dirty([page])
            
            # Trigger an update on the current page
            current_page_name = self.get_page_name(self.current_page_frame)
            if current_page_name:
                self.show_page(current_page_name)
        except Exception as e:
            log_crash("Failed to apply new appearance settings", e)

    def _adjust_color(self, color_hex, factor):
        """Lightens or darkens a color. factor > 1 lightens, < 1 darkens."""
        if not color_hex.startswith('#'):
            try:
                rgb = self.winfo_rgb(color_hex)
                r, g, b = (c >> 8 for c in rgb)
            except tk.TclError:
                r, g, b = 128, 128, 128 # fallback grey
        else:
            color_hex = color_hex.lstrip('#')
            if len(color_hex) == 3:
                color_hex = "".join([c*2 for c in color_hex])
            if len(color_hex) != 6:
                return "#808080" # fallback grey
            r, g, b = int(color_hex[0:2], 16), int(color_hex[2:4], 16), int(color_hex[4:6], 16)
        
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    # --- Setup & Initialization ---
    def _load_theme(self):
        """Loads the theme from the settings file."""
        # This function now only needs to read from a pre-loaded settings dict,
        # but we'll keep it separate for now. It's called before settings are loaded.
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f).get("theme", "darkly")
        except (IOError, json.JSONDecodeError):
            return "darkly" # Default theme on error
        return "darkly"

    def _init_styles(self):
        """Initializes all custom ttk styles for the application."""
        try:
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

        except Exception as e:
            log_crash("Failed to get theme colors, using fallbacks.", e)
            bg_color, fg_color, primary_color, secondary_color, light_color, dark_color = "#2a2a2a", "#ffffff", "#0d6efd", "#6c757d", "#f8f9fa", "#343a40"

        font_size_map = {"Petit": 9, "Moyen": 11, "Grand": 13}
        base_font_size = font_size_map.get(self.font_size_var.get(), 11)
        
        # --- Global Font & Style Configurations ---
        base_font = ('Segoe UI', base_font_size)
        bold_font = (base_font[0], base_font[1], 'bold')
        
        self.app_style.configure('.', font=base_font) # Set default font for all widgets
        self.app_style.configure('TLabel', font=base_font)
        self.app_style.configure('TButton', font=bold_font, padding=(15, 10), relief="flat", borderwidth=0, focuscolor="none", borderradius=self.corner_radius_var.get())
        self.app_style.configure('Treeview.Heading', font=bold_font)
        
        # --- Frame Styles ---
        self.app_style.configure("Content.TFrame", background=bg_color)
        self.app_style.configure("Card.TFrame", background=dark_color, borderwidth=0, relief="flat")
        
        hover_color = self._adjust_color(dark_color, 1.2)
        self.app_style.configure("GameCard.TFrame", background=dark_color, borderwidth=1, relief="solid", bordercolor="#444")
        self.app_style.map("GameCard.TFrame",
            background=[('hover', hover_color)],
            bordercolor=[('hover', primary_color), ('!hover', '#444')],
            relief=[('hover', 'raised'), ('!hover', 'solid')]
        )

        # --- Label Styles ---
        label_styles = {
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
            self.app_style.configure(style_name, **config)
            # Ensure hover/disabled states don't change appearance unless specified
            self.app_style.map(style_name,
                foreground=[('disabled', secondary_color)],
            )

        sidebar_bg = "#1c1c1c"
        sidebar_fg = "#e0e0e0"
        sidebar_active_bg = "#333333"
        self.app_style.configure("Sidebar.TFrame", background=sidebar_bg, borderradius=0)
        self.app_style.configure("Sidebar.TButton", font=('Segoe UI', base_font_size + 2), foreground=sidebar_fg, background=sidebar_bg, borderwidth=0, focusthickness=0, anchor="w", relief="flat", padding=(15, 10))
        self.app_style.map("Sidebar.TButton",
            background=[("active", sidebar_active_bg), ("hover", sidebar_active_bg), ("!active", sidebar_bg)],
            foreground=[("active", "#ffffff"), ("hover", primary_color), ("!active", sidebar_fg)] # Shine effect on hover
        )
        self.app_style.configure("Sidebar.Active.TButton", font=('Segoe UI', base_font_size + 2, "bold"), foreground="#ffffff", background=primary_color, borderwidth=0, focusthickness=0, anchor="w", relief="flat", padding=(15, 10))
        self.app_style.map("Sidebar.Active.TButton",
            background=[("!active", primary_color), ("hover", self._adjust_color(primary_color, 1.1))] # Slight shine for active button
        )

        self.app_style.configure("Nav.TFrame", background="#212529")

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

        # Styles for other common widgets to remove unwanted highlights
        self.app_style.configure("TEntry",
                                 fieldbackground=dark_color,
                                 foreground=fg_color,
                                 borderwidth=1,
                                 relief='flat',
                                 insertcolor=fg_color,
                                 bordercolor=secondary_color)
        self.app_style.map("TEntry",
                           bordercolor=[('focus', primary_color), ('!focus', secondary_color)])

        self.app_style.configure("Treeview",
                                 background=dark_color,
                                 fieldbackground=dark_color,
                                 foreground=fg_color,
                                 borderwidth=0,
                                 relief='flat')
        self.app_style.map("Treeview",
                           background=[('selected', primary_color)],
                           foreground=[('selected', light_color)])
        self.app_style.configure("Treeview.Heading",
                                 background=self._adjust_color(dark_color, 1.1),
                                 foreground=light_color,
                                 relief='flat',
                                 font=('Segoe UI', base_font_size, 'bold'))

        # Styles for unlocked achievements
        success_color = self.app_style.colors.success
        # Assuming a light text color is best on the success background
        self.app_style.configure("success.TFrame", background=success_color)
        self.app_style.configure("success.TLabel", foreground=self.app_style.colors.light, background=success_color)

    def ensure_directories(self):
        for folder in [GAMES_FOLDER, IMAGES_FOLDER, SETTINGS_FOLDER, SOUNDS_FOLDER]: # Ensure SETTINGS_FOLDER is created
            if not os.path.exists(folder):
                os.makedirs(folder)

    # --- Game Filtering and Actions ---
    def filter_games(self, event=None, animate=True):
        search_term = "" # Search entry removed, so term is always empty
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
        # Since search entry is removed, this can just call filter_games directly.
        self.filter_games()

    def clear_filters(self):
        self.show_favorites_only.set(False)
        self.category_filter.set("Toutes")
        self.filter_games()

    # --- UI Creation ---
    def create_sidebar(self):
        sidebar_logo = ttk.Label(self.sidebar_frame, text=APP_NAME, style="SidebarLogo.TLabel")
        sidebar_logo.pack(pady=(20, 10), padx=10)
        # Simplified navigation: remove the large "Accueil" / top items per user request
        # Keep essential pages and expose quick actions below.
        main_nav = [
            ("🏠 Accueil", "main"),
            ("🎮 Jeux", "games"),
            ("🏆 Succès", "achievements"), 
            ("⚙️ Paramètres", "settings")
        ]
        for text, page in main_nav:
            btn = ttk.Button(self.sidebar_frame, text=text, style="Sidebar.TButton", command=lambda p=page: self.show_page(p))
            btn.pack(fill="x", pady=6, padx=12)
            self.sidebar_buttons[page] = btn

        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill="x", padx=12, pady=12)

        # Quick actions area (compact, at top of separator)
        quick_frame = ttk.Frame(self.sidebar_frame)
        quick_frame.pack(fill="x", padx=12, pady=(4, 8))
        ttk.Label(quick_frame, text="Actions rapides", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        # Scanner button removed from sidebar per user request (functionality retained via keyboard binding if needed)
        ttk.Button(quick_frame, text="🎲 Lancer aléatoire", style="Sidebar.TButton", command=self.lancer_jeu_aleatoire).pack(fill="x", pady=4) # Java game button removed per user request
        ttk.Button(quick_frame, text="⌨️ Raccourcis", style="Sidebar.TButton", command=self.show_shortcuts).pack(fill="x", pady=4)

        # User section and exit button (désactivé)
        # Profil masqué à la demande: aucune création de label utilisateur ici.
        # self.sidebar_user_label.pack(pady=(6, 2), padx=12)
        ttk.Button(self.sidebar_frame, text="Quitter", bootstyle="danger-outline", command=self._on_closing).pack(side="bottom", fill="x", pady=(6, 20), padx=12)

    def launch_java_game(self):
        """Run the bundled PowerShell build-and-run script in a background thread."""
        import threading, subprocess, os, tkinter.messagebox as _mb

        def _run():
            try:
                base = os.path.dirname(os.path.abspath(__file__))
                script = os.path.join(base, 'download-game', 'build-and-run.ps1')
                if not os.path.exists(script):
                    _mb.showerror("Erreur", f"Script introuvable: {script}")
                    return
                subprocess.Popen(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', script], cwd=base)
            except Exception as e:
                log_crash("Failed to launch Java game", e)
                try:
                    _mb.showerror("Erreur", "Échec du lancement du jeu Java. Voir le log d'erreurs.")
                except Exception:
                    pass

        threading.Thread(target=_run, daemon=True).start()

    def create_menubar(self):  # noqa: C901
        """Creates a custom, stylable menubar using ttk.Menubuttons."""
        # This method replaces the native menubar to allow for full styling.
        # The menubar_frame is created in __init__

        # Get theme colors for styling
        try:
            # Use a very dark color for dropdowns, and primary for selection
            bg = self.app_style.colors.dark
            fg = self.app_style.colors.light
            active_bg = self.app_style.colors.primary
            active_fg = self.app_style.colors.light
            menubar_bg = self.app_style.lookup("Nav.TFrame", "background")
        except (AttributeError, tk.TclError):
            # Fallback colors
            bg = "#2a2a2a"
            fg = "#ffffff"
            active_bg = "#0d6efd"
            active_fg = "#ffffff"
            menubar_bg = "#212529"

        # Style for the dropdown menus (the popups)
        menu_style = {
            "tearoff": 0,
            "bg": bg,
            "fg": fg,
            "activebackground": active_bg,
            "activeforeground": active_fg,
            "selectcolor": fg,
            "relief": "flat",
            "borderwidth": 0,
            "activeborderwidth": 0
        }

        # Style for the Menubuttons themselves (the "Fichier", "Éditer" buttons)
        self.app_style.configure("Custom.TMenubutton",
                                 background=menubar_bg,
                                 foreground=fg,
                                 font=('Segoe UI', 10),
                                 borderwidth=0,
                                 relief="flat",
                                 padding=(8, 4),
                                 anchor="w")
        self.app_style.map("Custom.TMenubutton",
                           background=[('active', self._adjust_color(menubar_bg, 1.2)),
                                       ('hover', self._adjust_color(menubar_bg, 1.2))])

        # --- Fichier Menu ---
        file_menubutton = ttk.Menubutton(self.menubar_frame, text="Fichier", style="Custom.TMenubutton")
        file_menubutton.pack(side="left")
        file_menu = tk.Menu(file_menubutton, **menu_style)
        file_menubutton["menu"] = file_menu

    # Removed visible 'Scanner les jeux' menu entry per user request. The keyboard binding (F5) remains if configured.
        file_menu.add_command(label="Ajouter un jeu...", command=self.add_game)
        file_menu.add_separator()
        file_menu.add_command(label="Exporter les données...", command=self.export_data)
        file_menu.add_command(label="Importer les données...", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self._on_closing)

        # --- Éditer Menu ---
        edit_menubutton = ttk.Menubutton(self.menubar_frame, text="Éditer", style="Custom.TMenubutton")
        edit_menubutton.pack(side="left")
        edit_menu = tk.Menu(edit_menubutton, **menu_style)
        edit_menubutton["menu"] = edit_menu

        edit_menu.add_command(label="Rechercher...", command=self.focus_search, accelerator="Ctrl+F")
        edit_menu.add_separator()
        edit_menu.add_command(label="Changer le nom d'utilisateur...", command=self.change_username)
        edit_menu.add_command(label="Changer le dossier des jeux...", command=self.change_games_folder)
        edit_menu.add_separator()
        edit_menu.add_command(label="Préférences...", command=lambda: self.show_page('settings'))

        # --- Aide Menu ---
        help_menubutton = ttk.Menubutton(self.menubar_frame, text="Aide", style="Custom.TMenubutton")
        help_menubutton.pack(side="left")
        help_menu = tk.Menu(help_menubutton, **menu_style)
        help_menubutton["menu"] = help_menu

        help_menu.add_command(label="Voir sur GitHub", command=lambda: webbrowser.open("https://github.com/Dodo13500/dodoxy"))
        help_menu.add_command(label="Vérifier les mises à jour...", command=lambda: self.start_update_check(manual=True))
        help_menu.add_command(label="Afficher les nouveautés", command=self.show_whats_new_window)
        help_menu.add_separator()
        help_menu.add_command(label="À propos de Dodoxi", command=lambda: self.go_to_pro_tab(3))

    def show_shortcuts(self):
        """Display a small shortcuts/help dialog with useful quick toggles."""
        try:
            dlg = tk.Toplevel(self)
            dlg.title("Raccourcis")
            dlg.transient(self)
            dlg.resizable(False, False)
            dlg.grab_set()
            frm = ttk.Frame(dlg, padding=12)
            frm.pack(fill="both", expand=True)
            shortcuts = [
                ("Ctrl+F", "Focus recherche"),
                ("Ctrl+1..5", "Changer d'onglet rapide"),
                ("Left/Right", "Naviguer entre pages"),
                # ("F5", "Scanner les jeux")  # Removed visible shortcut entry per user request
            ]
            for k, desc in shortcuts:
                ttk.Label(frm, text=f"{k}: {desc}", anchor="w").pack(fill="x", pady=2)

            ttk.Separator(frm, orient="horizontal").pack(fill="x", pady=8)
            ttk.Button(frm, text="Basculer autohide scrollbar", command=self._toggle_autohide_scrollbars).pack(fill="x", pady=4)
            ttk.Button(frm, text="Ouvrir les paramètres", command=lambda: self.show_page('settings')).pack(fill="x", pady=4)
            ttk.Button(frm, text="Fermer", command=dlg.destroy).pack(fill="x", pady=(8,0))
        except Exception as e:
            log_crash("Failed to show shortcuts dialog", e)

    def _toggle_autohide_scrollbars(self):
        current = self.autohide_scrollbars_var.get()
        self.autohide_scrollbars_var.set(not current)
        # Propagate to existing scrolled frames if any
        for attr in ('games_scrolled_frame', 'achievements_scrolled_frame'):
            sf = getattr(self, attr, None)
            if sf and hasattr(sf, 'set_autohide'):
                try:
                    sf.set_autohide(not current)
                except Exception:
                    pass

    def create_main_page(self):
        self.main_page_frame.grid_columnconfigure(0, weight=1)
        self.main_page_frame.grid_rowconfigure(1, weight=1)

        header_frame = ttk.Frame(self.main_page_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=30, pady=(30, 20))
        self.welcome_label = ttk.Label(header_frame, text=self.get_welcome_message(), font=("Segoe UI", 26, "bold"))
    # Welcome header hidden per user request (do not pack)
    # self.welcome_label.pack(side="left")
    # Random launch button hidden
    # ttk.Button(header_frame, text="Lancer un jeu au hasard", command=self.lancer_jeu_aleatoire, bootstyle="success-outline").pack(side="right")

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
            
            try:
                color1 = self.app_style.colors.get(card_widget.bootstyle_color)
            except Exception:
                try:
                    color1 = getattr(self.app_style.colors, 'primary', '#0d6efd')
                except Exception:
                    color1 = '#0d6efd'
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

        self.games_scrolled_frame = ManualScrolledFrame(self.games_page_frame, autohide=self.autohide_scrollbars_var.get()) # noqa: E722
        self.games_scrolled_frame.grid(row=0, column=0, sticky="nsew")
        try:
            self.games_scrolled_frame.bind('<Configure>', lambda e: self.games_scrolled_frame.update_scrollregion())
        except Exception:
            pass

        container = getattr(self.games_scrolled_frame, 'container', None) or self.games_scrolled_frame
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)  # Give content row vertical weight so layout doesn't create extra scrollable space

        # Top toolbar for filters
        top_toolbar = ttk.Frame(container, padding=(20, 15, 20, 5))
        top_toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_toolbar.grid_columnconfigure(3, weight=1) # Push controls to the right

        # Search entry is fully removed per user request.
        self.search_entry = tk.StringVar() # Use a StringVar to hold search term if needed elsewhere, but no visible entry.

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
        # Create the attribute but do not pack it so it's hidden from the toolbar UI
        self.scan_button = ttk.Button(controls_frame, text="Scanner", command=self.start_manual_scan, bootstyle="info-outline", state="disabled")
        # Intentionally not packed to remove visible button
        ToolTip(self.scan_button, "(Hidden) Scanner le dossier pour de nouveaux jeux (F5)")
        
        self.games_grid_frame = ttk.Frame(container)
        self.games_grid_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        # Configure exactly 3 columns with uniform weight.
        for i in range(3):
            self.games_grid_frame.grid_columnconfigure(i, weight=1, uniform="game_card_col")

        self.scan_loading_frame = ttk.Frame(container)
        ttk.Label(self.scan_loading_frame, text="Recherche de jeux en cours...", font=("Segoe UI", 14, "italic"), bootstyle="secondary").pack(pady=20)
        self.scan_progressbar = ttk.Progressbar(self.scan_loading_frame, mode='indeterminate', length=300)
        self.scan_progressbar.pack(pady=20, padx=20)
        
    def create_settings_page(self):
        self.settings_page_frame.grid_rowconfigure(0, weight=1)
        self.settings_page_frame.grid_columnconfigure(0, weight=1)
        self.settings_scrolled_frame = ManualScrolledFrame(self.settings_page_frame, autohide=self.autohide_scrollbars_var.get())
        self.settings_scrolled_frame.grid(row=0, column=0, sticky="nsew")
        container = getattr(self.settings_scrolled_frame, 'container', None) or self.settings_scrolled_frame
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
        bg_frame.grid_columnconfigure([0, 1, 2], weight=1)
        ttk.Button(bg_frame, text="Choisir une image", command=self.select_image_background).grid(row=0, column=0, sticky="ew", padx=(0, 2))
        ttk.Button(bg_frame, text="Choisir un dégradé", command=self.open_gradient_editor).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(bg_frame, text="Réinitialiser", command=lambda: self.set_image_background(GRADIENT_DEFAULT_PATH), bootstyle="secondary").grid(row=0, column=2, sticky="ew", padx=(2, 0))

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

        # Row 8: Enable Sounds
        ttk.Checkbutton(appearance_tab, text="Activer les sons de notification", variable=self.enable_sounds_var, command=self.toggle_sounds).grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Row 9: Reset Window Geometry
        ttk.Button(appearance_tab, text="Réinitialiser la position/taille de la fenêtre", command=self.reset_window_geometry, bootstyle="secondary-outline").grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="w")

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
        
        # Update collection filter menu when settings page is created
        # This ensures the menu is populated even if no collections exist yet.
        self.update_collection_filter_menu()

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

    def populate_collections_treeview(self, treeview=None):
        target_tree = treeview if treeview is not None else self.collections_tree
        if not target_tree or not target_tree.winfo_exists(): return
        for i in target_tree.get_children():
            target_tree.delete(i)
        for name, game_paths in sorted(self.collections.items()):
            target_tree.insert("", "end", values=(name, len(game_paths)))

    def populate_categories_treeview(self):
        if not self.categories_tree or not self.categories_tree.winfo_exists(): return
        for i in self.categories_tree.get_children():
            self.categories_tree.delete(i)
        with self.games_lock:
            all_categories = sorted(list(set(cat for g in self.games for cat in g.get("categories", []))))
        for cat in all_categories:
            self.categories_tree.insert("", "end", values=(cat,))

    def update_collection_filter_menu(self):
        menu = self.collection_menu["menu"]
        menu.delete(0, "end")
        menu.add_command(label="Toutes", command=lambda: self.collection_filter.set("Toutes") or self.filter_games())
        for name in sorted(self.collections.keys()):
            menu.add_command(label=name, command=lambda n=name: self.collection_filter.set(n) or self.filter_games())

    def create_achievements_page(self):
        self.achievements_page_frame.grid_rowconfigure(0, weight=1)
        self.achievements_page_frame.grid_columnconfigure(0, weight=1)
        self.achievements_scrolled_frame = ManualScrolledFrame(self.achievements_page_frame, autohide=self.autohide_scrollbars_var.get())
        self.achievements_scrolled_frame.grid(row=0, column=0, sticky="nsew")

        # Determine the inner container immediately so it's always defined
        container = getattr(self.achievements_scrolled_frame, 'container', None) or self.achievements_scrolled_frame
        if container is None:
            container = self.achievements_scrolled_frame
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)  # Give content row vertical weight so layout doesn't create extra scrollable space

        try:
            sf = self.achievements_scrolled_frame
            if hasattr(sf, 'update_scrollregion'):
                sf.bind('<Configure>', lambda e: sf.update_scrollregion())
        except Exception:
            pass

        ttk.Label(container, text="Succès", font=("Segoe UI", 24, "bold")).grid(row=0, column=0, pady=(30, 20), padx=30, sticky="w")
        # Parent achievement cards directly into the scrolled-frame's container.
        self.achievements_container = container
        # Make sure the container cell used for content expands.
        # We use row=1 to match the page layout used elsewhere.
        # (child widgets will be gridded into self.achievements_container)
        # Schedule an update of the scrollregion after a short delay to ensure
        # content added asynchronously is included.
        try:
            self.after(100, lambda: getattr(self, 'achievements_scrolled_frame', None) and self.achievements_scrolled_frame.update_scrollregion())
        except Exception:
            pass

        
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
        profile_scrolled_frame = ManualScrolledFrame(profile_tab_container, autohide=self.autohide_scrollbars_var.get())
        profile_scrolled_frame.pack(fill="both", expand=True)
        profile_tab = getattr(profile_scrolled_frame, 'container', None) or profile_scrolled_frame
        profile_tab.configure(padding=20)
        profile_tab.grid_columnconfigure(0, weight=1)

        profile_card = ttk.Labelframe(profile_tab, text="Informations Utilisateur", style="Custom.TLabelframe") # noqa: E722
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

        # Recently Played Games
        recent_games_frame = ttk.Labelframe(profile_tab, text="Jeux Récemment Lancés", style="Custom.TLabelframe")
        recent_games_frame.grid(row=len(stats_labels) + 2, column=0, sticky="ew", pady=10)
        recent_games_frame.grid_columnconfigure(0, weight=1)

        cols = ('game_name', 'last_launched')
        self.pro_recent_games_tree = ttk.Treeview(recent_games_frame, columns=cols, show='headings', height=5, selectmode="none", takefocus=False)
        self.pro_recent_games_tree.heading('game_name', text='Jeu')
        self.pro_recent_games_tree.heading('last_launched', text='Dernier lancement')
        self.pro_recent_games_tree.column('last_launched', anchor='center', width=150)
        self.pro_recent_games_tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # --- Onglet Statistiques --- # noqa: E722
        stats_tab_container = ttk.Frame(self.pro_page_notebook)
        self.pro_page_notebook.add(stats_tab_container, text="Statistiques")
        stats_scrolled_frame = ManualScrolledFrame(stats_tab_container, autohide=self.autohide_scrollbars_var.get())
        stats_scrolled_frame.pack(fill="both", expand=True)
        stats_tab = getattr(stats_scrolled_frame, 'container', None) or stats_scrolled_frame
        stats_tab.configure(padding=20)
        stats_tab.grid_columnconfigure(0, weight=1)

        # Export Stats Button
        ttk.Button(stats_tab, text="Exporter les statistiques (CSV)", command=self.export_stats_to_csv, bootstyle="info-outline").grid(row=0, column=0, sticky="ew", pady=(0, 20))

        # Achievements Progress
        ach_frame = ttk.Labelframe(stats_tab, text="Progression des Succès", style="Custom.TLabelframe") # noqa: E722
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
        lib_frame = ttk.Labelframe(stats_tab, text="Statistiques de la Bibliothèque", style="Custom.TLabelframe") # noqa: E722
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
        top_games_frame = ttk.Labelframe(stats_tab, text="Top 5 des jeux les plus joués", style="Custom.TLabelframe") # noqa: E722
        top_games_frame.grid(row=3, column=0, sticky="ew", pady=10)
        top_games_frame.grid_columnconfigure(0, weight=1)
        top_games_frame.grid_rowconfigure(0, minsize=200)
        self.pro_top_games_chart_frame = ttk.Frame(top_games_frame)
        self.pro_top_games_chart_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Games by Category
        cat_stats_frame = ttk.Labelframe(stats_tab, text="Jeux par Catégorie", style="Custom.TLabelframe")
        cat_stats_frame.grid(row=4, column=0, sticky="ew", pady=10)
        cat_stats_frame.grid_columnconfigure(0, weight=1)
        cat_stats_frame.grid_rowconfigure(0, minsize=200)
        self.pro_cat_chart_frame = ttk.Frame(cat_stats_frame)
        self.pro_cat_chart_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # --- Onglet Collections Overview ---
        collections_overview_tab = ttk.Frame(self.pro_page_notebook, padding=20)
        self.pro_page_notebook.add(collections_overview_tab, text="Collections")
        collections_overview_tab.grid_columnconfigure(0, weight=1)
        collections_overview_tab.grid_rowconfigure(0, weight=1)

        cols = ('collection_name', 'game_count')
        self.pro_collections_tree = ttk.Treeview(collections_overview_tab, columns=cols, show='headings', height=10, selectmode="none", takefocus=False)
        self.pro_collections_tree.heading('collection_name', text='Nom de la collection')
        self.pro_collections_tree.heading('game_count', text='Nombre de jeux')
        self.pro_collections_tree.column('game_count', anchor='center', width=120)
        self.pro_collections_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Onglet Suggestions --- # noqa: E722
        suggestion_tab = ttk.Frame(self.pro_page_notebook, padding=20)
        self.pro_page_notebook.add(suggestion_tab, text="Suggestions")
        # Utiliser pack() de manière cohérente dans cet onglet pour éviter les conflits

        sugg_header = ttk.Frame(suggestion_tab) # noqa: E722
        sugg_header.pack(fill="x", pady=(0, 20))
        ttk.Label(sugg_header, text="Essayez quelque chose de nouveau", font=("Segoe UI", 16, "bold")).pack(side="left")
        ttk.Button(sugg_header, text="Nouvelle suggestion", command=self.update_pro_page, bootstyle="info-outline").pack(side="right")

        self.pro_suggestion_frame = ttk.Frame(suggestion_tab, style="Card.TFrame")
        self.pro_suggestion_frame.pack(fill="both", expand=True)

        # --- Onglet À propos ---
        about_tab = ttk.Frame(self.pro_page_notebook, padding=20) # noqa: E722
        self.pro_page_notebook.add(about_tab, text="À propos")
        about_tab.grid_columnconfigure(0, weight=1)
        about_tab.grid_rowconfigure(0, weight=1)
        
        about_container = ttk.Frame(about_tab)
        about_container.place(relx=0.5, rely=0.5, anchor="center")
        try:
            # Utilisation de la nouvelle méthode pour charger l'icône
            self.about_logo = self._get_image_icon(DEFAULT_GAME_ICON, (128, 128)) # noqa: E722
            ttk.Label(about_container, image=self.about_logo).pack(pady=10)
        except Exception:
            pass
        ttk.Label(about_container, text=APP_NAME, font=("Segoe UI", 32, "bold")).pack(pady=(5, 0))
        ttk.Label(about_container, text=VERSION, font=("Segoe UI", 14)).pack()
        ttk.Label(about_container, text=COPYRIGHT, font=("Segoe UI", 12, "italic"), bootstyle="secondary").pack(pady=(20, 0))
        ttk.Label(about_container, text="Lanceur de jeux moderne et personnalisable.", bootstyle="secondary").pack()
        
        link = ttk.Label(about_container, text="Développé avec Python et Tkinter. Voir sur GitHub.", foreground=self.app_style.colors.primary, cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Dodo13500/dodoxy"))

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

    def _get_general_stats(self) -> dict:
        """Gathers general statistics about the library and user profile."""
        with self.games_lock:
            total_playtime_s = self.settings.get("total_playtime_seconds", 0)
            h, m = divmod(total_playtime_s / 60, 60)
            fav_games = len([g for g in self.games if g.get("favorite")])
            total_games = len([g for g in self.games if not g.get("deleted")])
            missing_games = sum(1 for g in self.games if g.get("missing"))
            games_with_desc = sum(1 for g in self.games if not g.get("deleted") and g.get("description") and g.get("description") != "Aucune description.")
            games_with_icon = sum(1 for g in self.games if not g.get("deleted") and g.get("icon") and g.get("icon") != DEFAULT_GAME_ICON)

        unlocked_ach = sum(1 for ach in self.achievements_data.values() if self.settings.get(ach["unlocked_key"]))
        total_ach = len(self.achievements_data)

        return {
            "Temps de jeu total": f"{int(h)}h {int(m)}m",
            "Jeux lancés": self.settings.get('games_launched_count', 0),
            "Jeux en favoris": fav_games,
            "Succès débloqués": f"{unlocked_ach}/{total_ach}",
            "Total de jeux dans la bibliothèque": total_games,
            "Jeux avec description personnalisée": games_with_desc,
            "Jeux avec icône personnalisée": games_with_icon,
            "Jeux introuvables": missing_games
        }

    def _get_top_games_data_for_export(self) -> list[dict]:
        """Gathers data for the top 5 most played games."""
        with self.games_lock:
            top_games = sorted([g for g in self.games if not g.get("deleted")], key=lambda g: g.get("playtime_seconds", 0), reverse=True)[:5]
        data = []
        for game in top_games:
            playtime_s = game.get("playtime_seconds", 0)
            if playtime_s > 0:
                playtime_hours = playtime_s / 3600
                data.append({"name": game['name'], "playtime_hours": playtime_hours})
        return data

    def _get_category_counts_for_export(self) -> dict:
        """Gathers data for game counts by category."""
        category_counts = {}
        with self.games_lock:
            for game in self.games:
                if not game.get("deleted"):
                    for cat in game.get("categories", []):
                        category_counts[cat] = category_counts.get(cat, 0) + 1
        return category_counts

    def export_stats_to_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            title="Exporter les statistiques"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # General Statistics
                writer.writerow(["Statistiques Générales"])
                general_stats = self._get_general_stats()
                for key, value in general_stats.items():
                    writer.writerow([key, value])
                writer.writerow([]) # Empty row for separation

                # Top 5 Games
                writer.writerow(["Top 5 des Jeux les Plus Joués"])
                writer.writerow(["Nom du Jeu", "Temps de Jeu (heures)"])
                top_games_data = self._get_top_games_data_for_export()
                for game in top_games_data:
                    writer.writerow([game["name"], f"{game['playtime_hours']:.2f}"])
                writer.writerow([]) # Empty row for separation

                # Games by Category
                writer.writerow(["Jeux par Catégorie"])
                writer.writerow(["Catégorie", "Nombre de Jeux"])
                category_counts = self._get_category_counts_for_export()
                for category, count in sorted(category_counts.items()):
                    writer.writerow([category, count])
                writer.writerow([]) # Empty row for separation

            self.show_toast("Exportation réussie", "Les statistiques ont été exportées en CSV.", "success")
            self.check_and_unlock_achievement("achievement_exporteur")
        except Exception as e:
            log_crash("Failed to export statistics to CSV", e)
            self.show_toast("Erreur d'exportation", f"Impossible d'exporter les statistiques: {e}", "danger")

    def _create_bar_chart(self, parent_frame, data_dict, title, horizontal=True, x_label=""):
        """Creates and embeds a matplotlib bar chart."""
        # Clear previous chart
        for widget in parent_frame.winfo_children():
            widget.destroy()

        if not data_dict:
            ttk.Label(parent_frame, text="Pas de données à afficher.", style="Card.TLabel").pack(pady=20)
            return

        try:
            # Use theme colors for the chart
            bg_color = self.app_style.lookup("Card.TFrame", "background")
            fg_color = self.app_style.lookup("Card.TLabel", "foreground")
            primary_color = self.app_style.colors.primary

            fig = Figure(figsize=(5, 4), dpi=90, facecolor=bg_color)
            ax = fig.add_subplot(111)
            # Adjust layout to prevent labels from being cut off
            fig.subplots_adjust(left=0.35 if horizontal else 0.1, right=0.95, top=0.9, bottom=0.15)

            labels = list(data_dict.keys())
            values = list(data_dict.values())

            if horizontal:
                bars = ax.barh(labels, values, color=primary_color, height=0.6)
                ax.invert_yaxis()  # Display top item at the top
                ax.set_xlabel(x_label, color=fg_color)
            else:
                bars = ax.bar(labels, values, color=primary_color, width=0.6)

            # Style the chart
            ax.set_title(title, color=fg_color, pad=15)
            ax.set_facecolor(bg_color)
            ax.tick_params(axis='x', colors=fg_color)
            ax.tick_params(axis='y', colors=fg_color)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color(fg_color)
            ax.spines['left'].set_color(fg_color)

            canvas = FigureCanvasTkAgg(fig, master=parent_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            log_crash("Failed to create matplotlib chart", e)
            ttk.Label(parent_frame, text="Erreur lors de la création du graphique.", style="Card.TLabel").pack(pady=20)

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

    def _show_card_loading_animation(self):
        """Affiche une animation de chargement dans la grille des jeux."""
        # Clear the grid first
        for widget in self.games_grid_frame.winfo_children():
            widget.destroy()
        
        # Create and show the loading frame, centered
        loading_frame = ttk.Frame(self.games_grid_frame)
        # Place it in the center of the grid area
        loading_frame.grid(row=0, column=0, columnspan=self._get_game_grid_columns() or 1, pady=50, sticky="ew")
        loading_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(loading_frame, text="Chargement des jeux...", font=("Segoe UI", 14, "italic"), bootstyle="secondary").pack(pady=10)
        progress = ttk.Progressbar(loading_frame, mode='indeterminate', length=300)
        progress.pack(pady=20)
        progress.start()
        
        # This is important to make the animation appear before the next step
        self.update_idletasks()

    def update_game_cards(self, animate=True):
        columns = self._get_game_grid_columns()
        # Column configuration is now static and set in create_games_page
        if not self.filtered_games:
            # If no games, clear and show "No games found" message
            self._show_card_loading_animation() # Clear existing content
            self.after(50, self._display_no_games_message, columns) # Schedule message display
            return

        self._show_card_loading_animation()

        def _create_card_callback(game_data, idx):
            row, col = divmod(idx, columns)
            card = self.create_game_card_widget(self.games_grid_frame)
            self.update_game_card_content(card, game_data)
            card.grid(row=row, column=col, padx=2, pady=10, sticky="nsew")
            self.game_card_widgets[game_data['path']] = card
            return card

        # Schedule the actual loading to allow the UI to update and show the animation
        self.after(50, lambda: self.staggered_load(self.games_grid_frame, self.filtered_games, _create_card_callback, delay=35, animate=animate))

    def _display_no_games_message(self, columns):
        """Displays a message when no games are found after filtering/scanning."""
        for widget in self.games_grid_frame.winfo_children():
            widget.destroy()
        empty_frame = ttk.Frame(self.games_grid_frame)
        empty_frame.grid(row=0, column=0, columnspan=columns or 1, pady=50)
        
        msg = "Aucun jeu trouvé."
        if not any(g for g in self.games if not g.get("deleted")):
            msg = "Votre bibliothèque est vide."
        
        ttk.Label(empty_frame, text=msg, font=("Segoe UI", 16, "bold"), bootstyle="secondary").pack(pady=10)
        ttk.Button(empty_frame, text="Ajouter un jeu", command=self.add_game).pack(pady=5)

    def reflow_game_cards(self):
        """Re-grids existing game cards without destroying them for smooth resizing."""
        if self.is_updating_view:
            return
        columns = self._get_game_grid_columns()
        # Column configuration is now static and set in create_games_page
        # Re-grid existing widgets
        for idx, game_data in enumerate(self.filtered_games):
            widget = self.game_card_widgets.get(game_data['path'])
            if widget and widget.winfo_exists():
                row, col = divmod(idx, columns)
                widget.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

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

            login_dates = self.settings.get("login_dates", [])
            reg_date = login_dates[0] if login_dates else "N/A"
            if self.pro_profile_playtime_label: self.pro_profile_playtime_label.config(text=f"{int(h)}h {int(m)}m")
            if self.pro_profile_launched_label: self.pro_profile_launched_label.config(text=str(self.settings.get('games_launched_count', 0)))
            if self.pro_profile_fav_label: self.pro_profile_fav_label.config(text=str(fav_games))
            if self.pro_profile_reg_label: self.pro_profile_reg_label.config(text=reg_date)

        # --- Update Stats Tab ---
        unlocked_ach = sum(1 for ach in self.achievements_data.values() if self.settings.get(ach["unlocked_key"]))
        total_ach = len(self.achievements_data)

        if self.pro_stats_ach_meter: self.pro_stats_ach_meter.configure(amountused=unlocked_ach)

        with self.games_lock:
            general_stats = self._get_general_stats()
            top_games_data_chart = self._get_top_games_data_for_export() # Use this for chart
            category_counts_chart = self._get_category_counts_for_export() # Use this for chart

        if self.pro_stats_lib_total_label: self.pro_stats_lib_total_label.config(text=str(general_stats["Total de jeux dans la bibliothèque"]))
        if self.pro_stats_lib_desc_label: self.pro_stats_lib_desc_label.config(text=f"{general_stats['Jeux avec description personnalisée']} / {general_stats['Total de jeux dans la bibliothèque']}")
        if self.pro_stats_lib_icon_label: self.pro_stats_lib_icon_label.config(text=f"{general_stats['Jeux avec icône personnalisée']} / {general_stats['Total de jeux dans la bibliothèque']}")
        if self.pro_stats_lib_missing_label: self.pro_stats_lib_missing_label.config(text=str(general_stats["Jeux introuvables"]))

        # Update Top 5 Games Chart
        if self.pro_top_games_chart_frame:
            top_games_data = {}
            for game in top_games_data_chart:
                playtime_s = game.get("playtime_seconds", 0)
                if playtime_s > 0:
                    playtime_hours = playtime_s / 3600
                    top_games_data[game['name']] = playtime_hours
            self._create_bar_chart(self.pro_top_games_chart_frame, top_games_data, "Top 5 des jeux", x_label="Heures de jeu")

        # Update Games by Category Chart
        if self.pro_cat_chart_frame:
            # Fix: Call _create_bar_chart directly as _schedule_chart_update is not defined
            self._create_bar_chart(self.pro_cat_chart_frame, category_counts_chart, "Jeux par catégorie", horizontal=False, x_label="Nombre de jeux")

        # Update Recently Played Games
        if self.pro_recent_games_tree:
            for i in self.pro_recent_games_tree.get_children():
                self.pro_recent_games_tree.delete(i)
            
            recent_games = sorted([g for g in self.games if g.get("last_launched") and not g.get("deleted")],
                                  key=lambda g: g.get("last_launched"), reverse=True)[:5]
            
            for game in recent_games:
                last_launched_dt = datetime.datetime.fromisoformat(game["last_launched"])
                self.pro_recent_games_tree.insert("", "end", values=(game['name'], last_launched_dt.strftime("%Y-%m-%d %H:%M")))

        # Update Collections Overview
        if self.pro_collections_tree:
            for i in self.pro_collections_tree.get_children():
                self.pro_collections_tree.delete(i)
            self.populate_collections_treeview(treeview=self.pro_collections_tree)

        # --- Update Suggestion Tab ---
        if self.pro_suggestion_frame: # noqa: E722
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

        def _on_complete_and_resync():
            try:
                on_transition_complete()
            except Exception:
                pass
            try:
                # Give the layout a brief moment then ensure scroll regions are correct
                self.after(50, lambda: self._ensure_scrolled_frame_layout(target_frame))
            except Exception:
                pass

        self.animate_page_transition(target_frame, direction=direction, on_complete=_on_complete_and_resync)

    def go_to_pro_tab(self, tab_index: int):
        """Navigates to the 'pro' page and selects a specific tab."""
        self.show_page("pro")
        if self.pro_page_notebook:
            try:
                self.pro_page_notebook.select(tab_index)
            except tk.TclError:
                # Tab might not exist, or notebook is not fully created.
                pass

    # (Unified load_data implementation exists earlier in the file.)

    # --- Data Handling ---

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
            # Filter out deleted games before choosing a random one
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
        game_type = game_data.get("type", "python") # Default to python for old entries
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
            command = []
            if game_type == "java":
                command = ["java", "-jar", full_path]
            elif game_type == "java_source":
                # New logic to compile and run .java file
                dir_path = os.path.dirname(full_path)
                file_name = os.path.basename(full_path)
                class_name = file_name.replace('.java', '')
                
                # Compile command
                compile_command = ["javac", full_path]
                compile_proc = subprocess.run(compile_command, cwd=dir_path, capture_output=True, text=True, check=False)
                
                if compile_proc.returncode != 0:
                    error_message = f"Échec de la compilation de {file_name}:\n{compile_proc.stderr}"
                    messagebox.showerror("Erreur de compilation", error_message)
                    return

                # Run command
                command = ["java", class_name]
            else: # python
                command = [sys.executable, full_path]
            proc = subprocess.Popen(command, cwd=os.path.dirname(full_path))
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
        total_playtime_update = 0
        for pid, data in list(self.running_processes.items()):  # Use list to allow modification during iteration
            try:
                proc = data.get("proc")
                if proc and proc.poll() is not None:
                    playtime = time.time() - data["start_time"]
                    total_playtime_update += playtime

                    with self.games_lock:
                        # Find game and update its playtime
                        for game in self.games:
                            if game.get("path") == data.get("game_path"):
                                game["playtime_seconds"] = game.get("playtime_seconds", 0) + playtime
                                games_data_updated = True
                                break

                    finished_pids.append(pid)
            except ProcessLookupError:
                # The process might have already been reaped by the OS
                finished_pids.append(pid)
            except Exception as e:
                log_crash(f"Error polling process {pid}", e)
                finished_pids.append(pid)  # Remove problematic process

        for pid in finished_pids:
            if pid in self.running_processes:
                del self.running_processes[pid]

        if games_data_updated:
            self.save_games()

        if total_playtime_update > 0:
            total_playtime = self.settings.get("total_playtime_seconds", 0) + total_playtime_update
            self.save_settings("total_playtime_seconds", total_playtime)

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
        self.scan_button.config(text="Annuler", command=self.cancel_scan, bootstyle="danger-outline")
        self._show_scan_loading_animation()
        threading.Thread(target=self._scan_worker, daemon=True).start()
    
    def cancel_scan(self):
        """Cancels the ongoing game scan."""
        if self.scan_in_progress.is_set():
            self.scan_in_progress.clear()  # Signal the worker thread to stop
            self._hide_scan_loading_animation()
            self.scan_button.config(text="Scanner", command=self.start_manual_scan, bootstyle="info-outline")
            self.show_toast("Scan annulé", "La recherche de jeux a été interrompue.", "warning")

    def _scan_worker(self):
        """Worker thread for scanning games. Calls _scan_complete on the main thread when done."""
        self.check_and_unlock_achievement("achievement_12")
        new_games_count = self.scan_for_games()

        # Only update UI if the scan was not cancelled.
        # The scan_for_games function returns -1 on cancellation.
        if new_games_count != -1:
            self.after(0, self._scan_complete, new_games_count)

    def _sync_library_on_startup(self):
        """
        Scans for new games and checks for missing games in a single, efficient pass.
        This is intended for synchronous startup use and avoids multiple file I/O passes.
        Returns True if the library was modified, False otherwise.
        """
        library_was_modified = False
        try:
            with self.games_lock:
                existing_paths_in_db = {g["path"] for g in self.games if g.get("path")}
                found_on_disk_paths = set()
                
                # --- Scan for Python games ---
                python_games_folder = self.get_games_folder()
                if os.path.exists(python_games_folder):
                    for root, _, files in os.walk(python_games_folder):
                        for file in files:
                            if file.endswith(".py"):
                                full_path = os.path.abspath(os.path.join(root, file))
                                found_on_disk_paths.add(full_path)
                                if full_path not in existing_paths_in_db:
                                    name = file.replace('.py', '').replace('_', ' ').title()
                                    if file.lower() in ["main.py", "app.py", "__main__.py"]:
                                        name = os.path.basename(root).replace('_', ' ').title()
                                    
                                    new_game_data = {
                                        "name": name, "path": full_path, "description": "Aucune description.",
                                        "icon": DEFAULT_GAME_ICON, "requires": [], "deleted": False,
                                        "favorite": False, "launch_count": 0, "last_launched": None,
                                        "categories": [], "playtime_seconds": 0, "rating": 0,
                                        "type": "python"
                                    }
                                    self.games.append(new_game_data)
                                    library_was_modified = True

                # --- Scan for Java games ---
                if os.path.exists(JAVA_GAMES_FOLDER):
                    for game_dir_name in os.listdir(JAVA_GAMES_FOLDER):
                        game_dir_path = os.path.join(JAVA_GAMES_FOLDER, game_dir_name)
                        if not os.path.isdir(game_dir_path):
                            continue

                        executable_path, executable_type = self._find_java_executable(game_dir_path)

                        if executable_path:
                            found_on_disk_paths.add(executable_path)
                            if executable_path not in existing_paths_in_db:
                                game_to_add = {
                                    "name": game_dir_name.replace('_', ' ').title(),
                                    "path": executable_path,
                                    "description": "Jeu Java." if executable_type == "java" else "Jeu Java (source).",
                                    "icon": DEFAULT_GAME_ICON, "requires": [], "deleted": False,
                                    "favorite": False, "launch_count": 0, "last_launched": None,
                                    "categories": ["Java"], "playtime_seconds": 0, "rating": 0,
                                    "type": executable_type
                                }
                                self.games.append(game_to_add)
                                library_was_modified = True
                
                # --- Check for missing games using the set of found paths ---
                for game in self.games:
                    path = game.get("path")
                    is_missing = path not in found_on_disk_paths if path else True
                    if game.get("missing") != is_missing:
                        game["missing"] = is_missing
                        library_was_modified = True
        except Exception as e:
            log_crash("Error during startup library sync", e)

        return library_was_modified

    def scan_for_games(self) -> int: # Added return type hint
        """Scans for games and returns the number of new games found, or -1 if cancelled."""
        with self.games_lock:
            existing_paths = {g["path"] for g in self.games if g.get("path")}
        new_games_count = 0

        # --- Scan for Python games ---
        python_games_folder = self.get_games_folder()
        if os.path.exists(python_games_folder):
            for root, _, files in os.walk(python_games_folder):
                if not self.scan_in_progress.is_set(): return -1
                for file in files:
                    # Allows other operations to run without completely blocking the worker thread
                    time.sleep(0.001) 
                    if not self.scan_in_progress.is_set():  # Check if scan was cancelled
                        return -1 # Indicate cancellation

                    full_path = os.path.abspath(os.path.join(root, file))
                    if full_path in existing_paths:
                        continue

                    if file.endswith(".py"):
                        name = file.replace('.py', '').replace('_', ' ').title()
                        if file.lower() in ["main.py", "app.py", "__main__.py"]:
                            name = os.path.basename(root).replace('_', ' ').title()
                        
                        new_game_data = {
                            "name": name, "path": full_path, "description": "Aucune description.",
                            "icon": DEFAULT_GAME_ICON, "requires": [], "deleted": False,
                            "favorite": False, "launch_count": 0, "last_launched": None,
                            "categories": [], "playtime_seconds": 0, "rating": 0,
                            "type": "python" # Add game type
                        }
                        with self.games_lock:
                            self.games.append(new_game_data)
                        existing_paths.add(full_path)
                        new_games_count += 1

        # --- Scan for Java games ---
        if os.path.exists(JAVA_GAMES_FOLDER):
            for game_dir_name in os.listdir(JAVA_GAMES_FOLDER):
                if not self.scan_in_progress.is_set(): return -1
                game_dir_path = os.path.join(JAVA_GAMES_FOLDER, game_dir_name)
                if os.path.isdir(game_dir_path):
                    # Check if a game from this directory is already in the library
                    with self.games_lock:
                        if any(g.get("path", "").startswith(game_dir_path) for g in self.games):
                            continue

                    executable_path, executable_type = self._find_java_executable(game_dir_path)

                    if not executable_path:
                        continue

                    # Since we already checked if the game exists, we can just add it.
                    new_game_data = {
                        "name": game_dir_name.replace('_', ' ').title(),
                        "path": executable_path,
                        "description": "Jeu Java." if executable_type == "java" else "Jeu Java (source).",
                        "icon": DEFAULT_GAME_ICON, "requires": [], "deleted": False,
                        "favorite": False, "launch_count": 0, "last_launched": None,
                        "categories": ["Java"], "playtime_seconds": 0, "rating": 0,
                        "type": executable_type
                    }
                    with self.games_lock:
                        self.games.append(new_game_data)
                    existing_paths.add(executable_path)
                    new_games_count += 1

        return new_games_count # Return the count if not cancelled

    def _scan_complete(self, new_games_count: int): # New method for scan completion UI updates
        self._hide_scan_loading_animation()
        if new_games_count > 0:
            self.save_games()
            # Achievement for scanning is now handled in start_manual_scan or _scan_worker
        
        self.scan_in_progress.clear()
        self.scan_button.config(text="Scanner", command=self.start_manual_scan, bootstyle="info-outline", state="normal")
        self.show_toast("Scan terminé", f"{new_games_count} nouveau(x) jeu(x) ajouté(s)." if new_games_count > 0 else "Aucun nouveau jeu trouvé.", "success")
        self.filter_games()

    def _find_java_executable(self, directory_path: str) -> tuple[str | None, str | None]:
        """
        Recursively searches a directory for a .jar or .java file.
        Prioritizes .jar files.
        Returns a tuple of (path, type) or (None, None).
        """
        executable_path = None
        executable_type = None
        first_java_found = None

        for root, _, files in os.walk(directory_path):
            # Prioritize finding a .jar file
            for file in files:
                if file.endswith(".jar"):
                    executable_path = os.path.abspath(os.path.join(root, file))
                    executable_type = "java"
                    return executable_path, executable_type # Return immediately once a JAR is found
            
            # If no .jar yet, look for the first .java file
            if not first_java_found:
                for file in files:
                    if file.endswith(".java"):
                        first_java_found = os.path.abspath(os.path.join(root, file))
                        break # Found a java file, stop searching this directory's files
        return (first_java_found, "java_source") if first_java_found else (None, None)

    def _show_scan_loading_animation(self): # noqa: E722
        """Hides the game grid and shows the scanning progress animation."""
        self.games_grid_frame.grid_remove()
        self.scan_loading_frame.grid(row=1, column=0, sticky="", pady=50) # Centered
        self.scan_progressbar.start()

    def _hide_scan_loading_animation(self):
        """Hides the scanning animation and shows the game grid."""
        if self.scan_loading_frame.winfo_ismapped():
            self.scan_progressbar.stop()
            self.scan_loading_frame.grid_remove()
        self.games_grid_frame.grid()

    def add_game(self):
        path = filedialog.askopenfilename( # noqa: E722
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

    def show_toast(self, title, message, bootstyle="info", sound_path=None):
        if sound_path:
            play_sound(sound_path, self.enable_sounds_var.get())
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
        self.check_and_unlock_achievement("achievement_3")
        self.show_toast("Thème changé", "Le nouveau thème sera pleinement appliqué au redémarrage.", "info")

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

    def apply_background_setting(self):
        """Applique le fond d'écran (image ou dégradé) en fonction des paramètres."""
        bg_type = self.settings.get("background_type", "image")
        if bg_type == "gradient":
            colors = self.settings.get("background_gradient_colors", ["#2a2a2a", "#1a1a1a"])
            self.set_gradient_background(colors[0], colors[1])
        else: # "image"
            image_path = self.settings.get("background", GRADIENT_DEFAULT_PATH)
            self.set_image_background(image_path)

    def set_gradient_background(self, color1: str, color2: str):
        """Crée un dégradé en mémoire et l'applique comme fond d'écran."""
        try:
            # Crée une image PIL de base. _update_background_display s'occupera du redimensionnement.
            width, height = 200, 200
            
            img = Image.new("RGB", (width, height))
            draw = ImageDraw.Draw(img)
            
            r1, g1, b1 = self.winfo_rgb(color1)
            r2, g2, b2 = self.winfo_rgb(color2)
            
            for i in range(height):
                r = int(r1/256 + (r2/256 - r1/256) * i / height)
                g = int(g1/256 + (g2/256 - g1/256) * i / height)
                b = int(b1/256 + (b2/256 - b1/256) * i / height)
                draw.line([(0, i), (width, i)], fill=(r, g, b))

            self.original_background_pil = img

            if not self.background_label:
                self.background_label = ttk.Label(self)
                self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.background_label.lower()
            self._update_background_display()
            
            # Sauvegarder les paramètres
            self.save_settings("background_type", "gradient")
            self.save_settings("background_gradient_colors", [color1, color2])
        except Exception as e:
            log_crash("Échec de la définition du fond d'écran en dégradé", e)
            self.set_image_background(GRADIENT_DEFAULT_PATH)

    def set_image_background(self, image_path: str | None):
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
            self.save_settings("background_type", "image")
            self.save_settings("background", image_path)
        except Exception as e:
            log_crash("Échec du réglage du fond d'écran", e)
            self.save_settings("background", "")
            self.original_background_pil = None

    def select_image_background(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if path:
            self.set_image_background(path)

    def open_gradient_editor(self):
        """Ouvre une fenêtre pour choisir les couleurs du dégradé."""
        editor = tk.Toplevel(self)
        editor.title("Éditeur de Dégradé")
        editor.transient(self)
        editor.grab_set()
        editor.geometry("400x250")

        current_colors = self.settings.get("background_gradient_colors", ["#2a2a2a", "#1a1a1a"])
        
        color1_var = tk.StringVar(value=current_colors[0])
        color2_var = tk.StringVar(value=current_colors[1])

        main_frame = ttk.Frame(editor, padding=20)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(1, weight=1)

        def _pick_color(var, preview_label):
            from ttkbootstrap.dialogs.colorchooser import ColorChooserDialog
            dialog = ColorChooserDialog(initialcolor=var.get(), parent=editor)
            dialog.show()
            if dialog.result:
                var.set(dialog.result.hex)
                preview_label.configure(background=dialog.result.hex)

        # Color 1
        ttk.Label(main_frame, text="Couleur du haut:").grid(row=0, column=0, sticky="w", padx=5, pady=10)
        preview1 = tk.Frame(main_frame, width=100, height=25, background=color1_var.get(), relief="solid", borderwidth=1)
        preview1.grid(row=0, column=1, padx=5, pady=10)
        ttk.Button(main_frame, text="Choisir...", command=lambda: _pick_color(color1_var, preview1)).grid(row=0, column=2, padx=5, pady=10)

        # Color 2
        ttk.Label(main_frame, text="Couleur du bas:").grid(row=1, column=0, sticky="w", padx=5, pady=10)
        preview2 = tk.Frame(main_frame, width=100, height=25, background=color2_var.get(), relief="solid", borderwidth=1)
        preview2.grid(row=1, column=1, padx=5, pady=10)
        ttk.Button(main_frame, text="Choisir...", command=lambda: _pick_color(color2_var, preview2)).grid(row=1, column=2, padx=5, pady=10)

        def _apply_and_save():
            color1 = color1_var.get()
            color2 = color2_var.get()
            self.set_gradient_background(color1, color2)
            editor.destroy()

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        ttk.Button(button_frame, text="Appliquer", command=_apply_and_save, bootstyle="success").pack(side="right", padx=5)
        ttk.Button(button_frame, text="Annuler", command=editor.destroy, bootstyle="secondary").pack(side="right")

    def delayed_resize(self, event):
        if self.resize_timer: self.after_cancel(self.resize_timer)
        self.resize_timer = self.after(100, lambda: self.on_resize(event))

    def on_resize(self, event):
        if self.winfo_width() > 1 and self.winfo_height() > 1 and not self.is_transitioning:
            self._update_background_display()
            
            current_ach_cols = max(1, self.winfo_width() // 600)
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
        if self.view_mode.get() == "Liste":
            return 1 # List view should always be a single column for consistency
        else: # Grid view
           # Rétablit une grille fixe de 3 colonnes comme demandé.
           return 3
    def toggle_view_mode(self):
        self.save_settings("view_mode", self.view_mode.get())
        self.update_game_cards()

    def create_game_card_widget(self, parent: ttk.Frame) -> ttk.Frame:
        """Creates a new game card widget and initializes its permanent sub-widgets."""
        card = ttk.Frame(parent, style="GameCard.TFrame", padding=15)
        card.is_initialized = True # Mark as initialized
        
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
        card.fav_button.config(style="Favorite.TButton") # Apply specific style
        card.fav_button.pack(side="right", anchor="e", padx=5)
        ToolTip(card.fav_button, "Ajouter/Retirer des favoris")

        card.desc_label = ttk.Label(card, style="GameCard.Desc.TLabel")
        card.desc_label.grid(row=1, column=1, sticky="ew", pady=(2, 5), padx=5)
        
        ttk.Frame(card, style="GameCard.TFrame").grid(row=2, column=1, sticky="nsew") # Spacer
        
        card.rating_frame = ttk.Frame(card, style="GameCard.TFrame") # Rating frame
        card.rating_frame.grid(row=2, column=0, sticky="s", padx=10, pady=5)


        card.bottom_frame = ttk.Frame(card, style="GameCard.TFrame")
        card.bottom_frame.grid(row=3, column=1, sticky="ew", pady=5)
        card.bottom_frame.grid_columnconfigure(0, weight=1)

        # Frame for categories and type
        info_line_frame = ttk.Frame(card.bottom_frame, style="GameCard.TFrame")
        info_line_frame.grid(row=0, column=0, sticky="w")

        card.cat_label = ttk.Label(card.bottom_frame, style="Category.TLabel")
        card.cat_label.pack(in_=info_line_frame, side="left", padx=5)
        card.type_label = ttk.Label(card.bottom_frame, style="Category.TLabel")
        card.type_label.pack(in_=info_line_frame, side="left", padx=5)

        card.button_group = ttk.Frame(card.bottom_frame, style="GameCard.TFrame")
        card.button_group.grid(row=0, column=2, sticky="e")

        card.edit_btn = ttk.Button(card.button_group, text="✏️", bootstyle="secondary-outline", width=2)
        card.edit_btn.pack(side="left", padx=(0, 5))
        ToolTip(card.edit_btn, "Modifier")

        card.delete_btn = ttk.Button(card.button_group, text=TRASH_ICON, bootstyle="danger-outline", width=2)
        card.delete_btn.pack(side="left", padx=(0, 5))
        ToolTip(card.delete_btn, "Supprimer")

        card.launch_btn = ttk.Button(card.button_group, text="Lancer")
        card.launch_btn.pack(side="left")
        return card

    def update_game_card_content(self, card: ttk.Frame, game_data: dict):
        card.game_data = game_data

        icon = self._get_image_icon(game_data.get("icon", DEFAULT_GAME_ICON), (64, 64))
        card.icon_label.config(image=icon)
        card.icon_label.image = icon

        card.title_label.config(text=game_data.get("name", "Jeu inconnu"))

        fav_char = "⭐" if game_data.get("favorite") else "☆"
        fav_bootstyle = "warning" if game_data.get("favorite") else "secondary"
        card.fav_button.config(text=fav_char, bootstyle=(fav_bootstyle, "link"), command=lambda g=game_data: self.toggle_favorite(g))

        card.desc_label.config(text=game_data.get("description", "Aucune description."))
        
        self._update_rating_widget(card.rating_frame, game_data) # Update rating stars

        # Update game type label
        game_type = game_data.get("type", "python")
        if "java" in game_type:
            type_icon = "☕"
            type_bootstyle = "danger" # Red
        else: # python
            type_icon = "🐍"
            type_bootstyle = "info" # Blue
        card.type_label.config(text=f"{type_icon} {game_type.replace('_', ' ').capitalize()}", bootstyle=type_bootstyle)

        def wrap_description(event, label=card.desc_label, title_label=card.title_label):
            # card width - icon width (64) - icon padding (10) - fav button width (approx 30) - padding
            wraplength = event.width - 120 
            if wraplength > 1:
                label.config(wraplength=wraplength)
                title_label.config(wraplength=wraplength)
        card.bind('<Configure>', wrap_description, add='+')

        cat_text = "Catégories : " + ", ".join(game_data.get("categories", [])) if game_data.get("categories") else ""
        if game_data.get("missing"):
            card.cat_label.config(text="Fichier introuvable !", style="Invalid.TLabel")
            launch_button_state = "disabled"
        else: # noqa: E722
            card.cat_label.config(text=cat_text, style="Category.TLabel")
            launch_button_state = "normal"

        card.edit_btn.config(command=lambda g=game_data: self.edit_game(g))
        card.delete_btn.config(command=lambda g=game_data: self.delete_game(g))
        card.launch_btn.config(command=lambda g=game_data: self.lancer_jeu(g), state=launch_button_state)

    def edit_game(self, game_data: dict):
        """Opens a dialog to edit the details of a game."""
        edit_window = tk.Toplevel(self)
        edit_window.title(f"Modifier: {game_data.get('name')}")
        edit_window.geometry("650x500")
        edit_window.minsize(500, 450)
        edit_window.transient(self)
        edit_window.grab_set()

        # --- Variables ---
        name_var = tk.StringVar(value=game_data.get("name"))
        path_var = tk.StringVar(value=game_data.get("path"))
        requires_var = tk.StringVar(value=", ".join(game_data.get("requires", [])))
        rating_var = tk.IntVar(value=game_data.get("rating", 0))
        icon_var = tk.StringVar(value=game_data.get("icon"))
        categories_var = tk.StringVar(value=", ".join(game_data.get("categories", [])))

        # --- Layout ---
        form_frame = ttk.Frame(edit_window, padding=20)
        form_frame.pack(fill="both", expand=True)
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_rowconfigure(4, weight=1) # Make description row expandable

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
        ttk.Label(form_frame, text="Description:").grid(row=4, column=0, sticky="nw", pady=5)
        desc_frame = ttk.Frame(form_frame, relief="solid", borderwidth=1)
        desc_frame.grid(row=4, column=1, sticky="nsew", pady=5)
        desc_frame.grid_rowconfigure(0, weight=1)
        desc_frame.grid_columnconfigure(0, weight=1)
        desc_text = tk.Text(desc_frame, wrap="word", height=4, font=("Segoe UI", 9))
        desc_text.insert("1.0", game_data.get("description", ""))
        desc_text.grid(row=0, column=0, sticky="nsew")
        desc_scroll = ttk.Scrollbar(desc_frame, orient="vertical", command=desc_text.yview)
        desc_scroll.grid(row=0, column=1, sticky="ns")
        desc_text.config(yscrollcommand=desc_scroll.set)

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
            game_data["description"] = desc_text.get("1.0", "end-1c").strip()
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

            # Vérifier le succès "Le Critique" (5 descriptions)
            with self.games_lock:
                games_with_desc_count = sum(1 for g in self.games if not g.get("deleted") and g.get("description") and g.get("description") not in ["", "Aucune description."])
            if games_with_desc_count >= 5:
                self.check_and_unlock_achievement("achievement_critique")

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
            if card and card.winfo_exists(): # noqa: E1120
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

    def verify_dependencies_on_startup(self): # This function is empty and not used elsewhere.
        pass # Placeholder

    def start_update_check(self, manual=False):
        """Starts the update check in a background thread to not freeze the UI."""
        threading.Thread(target=self._check_for_updates_worker, args=(manual,), daemon=True).start()

    def _check_for_updates_worker(self, manual=False):
        """Fetches version info from a URL and compares with local version."""
        # This URL should point to a raw JSON file on your GitHub repo or another server.
        UPDATE_URL = "https://raw.githubusercontent.com/Dodo13500/dodoxy/main/version.json"
        try:
            response = requests.get(UPDATE_URL, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            
            latest_version = data.get("latest_version")
            release_url = data.get("release_url")

            # Simple version comparison (e.g., "v0.17.0" > "v0.16.0")
            if latest_version and release_url and latest_version > VERSION:
                self.after(0, self.show_update_notification, latest_version, release_url)
            elif manual:
                self.after(0, messagebox.showinfo, "Mise à jour", "Vous utilisez déjà la dernière version.")

        except requests.exceptions.RequestException as e:
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

        text_frame = ScrolledFrame(win, autohide=True)  # This is the ScrolledFrame widget
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        container = getattr(text_frame, 'container', None) or text_frame  # Widgets must be placed in its .container

        # Loading label
        loading_label = ttk.Label(container, text="Chargement des nouveautés...", bootstyle="secondary")
        loading_label.pack(pady=20)

        # The actual content label (created but not packed yet)
        content_label = ttk.Label(container, text="", wraplength=450, justify="left")

        def _fetch_whats_new_worker():
            WHATS_NEW_URL = "https://raw.githubusercontent.com/Dodo13500/dodoxy/main/whatsnew.txt"
            try:
                response = requests.get(WHATS_NEW_URL, timeout=10)
                response.raise_for_status()
                news_text = response.text
            except requests.exceptions.RequestException as e:
                log_crash("Failed to fetch what's new content", e)
                news_text = (
                    "Impossible de charger les nouveautés.\n\n"
                    "Veuillez vérifier votre connexion internet.\n"
                    "Les détails de l'erreur ont été enregistrés dans le journal."
                )

            def _update_ui():
                if not win.winfo_exists():
                    return  # Window might be closed
                loading_label.destroy()
                content_label.config(text=news_text)
                content_label.pack(pady=10, anchor='w')

            # Schedule the UI update on the main thread
            self.after(0, _update_ui)

        # Start the fetch in a background thread
        threading.Thread(target=_fetch_whats_new_worker, daemon=True).start()

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
        except Exception as e: # noqa: E722
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
            image.save(DEFAULT_GAME_ICON) # noqa: E722
        except Exception as e:
            log_crash("Failed to create default icon", e)

    def check_and_unlock_achievement(self, key: str):
        k = self.achievements_data[key]["unlocked_key"]
        if not self.settings.get(k):
            self.save_settings(k, True)

            ach_data = self.achievements_data[key]
            difficulty = ach_data.get("difficulty", 0)
            RARE_ACHIEVEMENT_THRESHOLD = 25 # Succès avec une difficulté >= 25 sont rares

            if difficulty >= RARE_ACHIEVEMENT_THRESHOLD:
                self.show_confetti_animation()

            # La notification toast jouera le son du succès # noqa: E722
            self.show_toast(f"Succès débloqué !", ach_data["name"], "success", sound_path=ACHIEVEMENT_SOUND)

    def check_and_unlock_pro_pages_achievement(self):
        if len(self.session_pro_pages_visited) >= 3:
            self.check_and_unlock_achievement("achievement_grand_tour")

    def toggle_fullscreen(self):
        self.attributes("-fullscreen", self.fullscreen_var.get())
        self.save_settings("fullscreen", self.fullscreen_var.get())

    def _toggle_fullscreen_event(self, event=None):
        """Toggles fullscreen mode from a key press and updates the Checkbutton variable."""
        current_state = self.fullscreen_var.get()
        self.fullscreen_var.set(not current_state)
        self.toggle_fullscreen()

    def toggle_autohide(self):
        self.save_settings("autohide_scrollbars", self.autohide_scrollbars_var.get())
        self.show_toast("Paramètre sauvegardé", "Le changement sera appliqué au redémarrage.", "info")

    def toggle_sounds(self):
        self.save_settings("enable_sounds", self.enable_sounds_var.get())

    def reset_window_geometry(self):
        """Resets the window size and position to default and saves it."""
        default_width = 1400
        default_height = 1000
        
        # Update settings dictionary
        self.save_settings("window_width", default_width)
        self.save_settings("window_height", default_height)
        self.save_settings("window_pos_x", None)
        self.save_settings("window_pos_y", None)
        
        # Center the window
        self.update_idletasks() # Ensure screen dimensions are up to date
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (default_width // 2)
        y = (screen_height // 2) - (default_height // 2)
        
        self.geometry(f"{default_width}x{default_height}+{x}+{y}")
        self.show_toast("Géométrie réinitialisée", "La taille et la position de la fenêtre ont été réinitialisées.", "success")

    def perform_first_run_setup(self): # New function for first run
        messagebox.showinfo(f"Bienvenue dans {APP_NAME} !", # noqa: E722
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
        new_name = simpledialog.askstring("Changer de nom", "Entrez votre nouveau nom d'utilisateur :", initialvalue=current_name, parent=self) # noqa: E722
        if new_name and new_name.strip() and new_name != current_name:
            self.save_settings("username", new_name.strip())
            self.update_username_in_ui()
            self.show_toast("Nom d'utilisateur mis à jour", f"Votre nom est maintenant '{new_name.strip()}'.", "success")
            self.check_and_unlock_achievement("achievement_identity_change")

    # --- Maintenance Functions ---
    def export_data(self):
        path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Archive ZIP", "*.zip")], title="Exporter les données")
        if not path: return # noqa: E722
        
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
            return # noqa: E722
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
        try: # noqa: E722
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
            self.show_toast("Nettoyage terminé", f"{missing_count} jeu(x) supprimé(s).", "success") # noqa: E722

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
        if not messagebox.askyesno( # noqa: E722
            "Confirmation de réinitialisation totale",
            warning_message,
            parent=self,
            icon='error'
        ):
            return
        
        # Extra confirmation step
        confirmation_text = simpledialog.askstring( # noqa: E722
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
            "Confirmation", # noqa: E722
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
        new_name = simpledialog.askstring("Renommer la catégorie", f"Nouveau nom pour '{old_name}':", parent=self) # noqa: E722

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
        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer la catégorie '{cat_name}' de tous les jeux ?"): # noqa: E722
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
        if name and name.strip(): # noqa: E722
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
        new_name = simpledialog.askstring("Renommer la collection", f"Nouveau nom pour '{old_name}':", parent=self) # noqa: E722

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
        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer la collection '{name}' ?\n(Les jeux ne seront pas supprimés de la bibliothèque)"): # noqa: E722
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

        collections_menu.add_separator() # noqa: E722
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

    def open_theme_editor(self): # noqa: C901
        editor = tk.Toplevel(self)
        editor.title("Éditeur de Thème")
        editor.transient(self)
        editor.grab_set()

        colors = self.settings.get("custom_theme_colors", {}).copy()
        color_vars = {}

        main_frame = ttk.Frame(editor, padding=20)
        main_frame.pack(fill="both", expand=True)

        def _pick_color(key, var, preview):
            from ttkbootstrap.dialogs.colorchooser import ColorChooserDialog # noqa: E722
            dialog = ColorChooserDialog(initialcolor=var.get(), parent=editor)
            dialog.show()
            if dialog.result:
                var.set(dialog.result.hex)
                preview.configure(background=dialog.result.hex)

        color_keys = ["primary", "secondary", "success", "info", "warning", "danger", "light", "dark"]
        for i, key in enumerate(color_keys):
            ttk.Label(main_frame, text=f"{key.capitalize()}:").grid(row=i, column=0, sticky="w", padx=5, pady=5)
            try:
                fallback = self.app_style.colors.get(key)
            except Exception:
                fallback = "#ffffff"
            color_vars[key] = tk.StringVar(value=colors.get(key, fallback))
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
        for w in parent.winfo_children(): # noqa: E722
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
            game_data["rating"] = 0 if game_data.get("rating", 0) == rating else rating # noqa: E722
        self.save_games()
        self.update_game_card_by_path(game_data["path"])
        self.check_and_unlock_achievement("achievement_critic")

if __name__ == "__main__":
    try:
        app = GameLauncher()
        app.mainloop()
    except Exception as e:
        # Affiche une fenêtre d'erreur personnalisée qui gère aussi le logging
        show_fatal_error_dialog("L'application a rencontré une erreur fatale et va se fermer.", e)
