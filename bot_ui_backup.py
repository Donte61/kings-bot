import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from tips_ui import TipsUI
import threading
import time
import queue
import pyautogui
import os
import logging
import json
import datetime
import random
from log import TkinterLogHandler, log_queue
from utils import get_mouse_position, save_config, load_config, try_click, find_image_location, check_for_updates, prepare_update_and_launch_updater, activate_license_code, check_license_status, load_user_data, save_user_data, is_license_active_locally, BOT_API_KEY, get_resource_path, open_url, handle_error_and_notify, save_last_shown_update_note_version, load_last_shown_update_note_version, BOT_EXE_NAME, UPDATER_EXE_NAME
from sequences import (
    perform_healing_sequence, perform_daily_tasks, perform_kutu_sequence,
    perform_anahtar_sequence, perform_asker_hasat_sequence,
    perform_recovery_sequence, perform_mesaj_sequence, perform_savas_sequence,
    perform_ittifak_sequence, perform_suadasi_sequence, perform_bekcikulesi_sequence, perform_askerbas_sequence, perform_dunya_heal_sequence,
    perform_fetih_sequence, perform_isyanci_sequence
)
from version import __version__
from update_notes_ui import UpdateNotesUI
from task_manager import TaskManager, TaskStatus

stats_queue = queue.Queue()
update_progress_queue = queue.Queue()

class ScrolledFrame(tk.Frame):
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)
        v_scrollbar = ttk.Scrollbar(self, orient="vertical")
        v_scrollbar.pack(fill="y", side="right", expand=False)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=v_scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.config(command=canvas.yview)
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        self.interior = interior = tk.Frame(canvas, bg=kw.get('bg'))
        interior_id = canvas.create_window(0, 0, window=interior, anchor="nw")
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        def _configure_interior(event):
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.config(width=interior.winfo_width())
        interior.bind('<Configure>', _configure_interior)
        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)
        canvas.bind_all('<MouseWheel>', _on_mousewheel)

class ResolutionSelector:
    def __init__(self, master):
        self.master = master
        self.master.title("Ekran Çözünürlüğü Seçimi")
        self.master.geometry("350x200")
        self.master.resizable(False, False)
        self.master.configure(bg="#2c3e50")
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.selected_resolution = None
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Helvetica", 11), padding=8, background="#1abc9c", foreground="#ffffff", borderwidth=0)
        style.map("TButton", background=[('active', '#16a085')])
        style.configure("TLabel", font=("Helvetica", 12), background="#2c3e50", foreground="#ecf0f1")
        tk.Label(self.master, text="Lütfen cihazınız için bir çözünürlük seçin:", font=("Helvetica", 14, "bold"), bg="#2c3e50", fg="#ecf0f1", wraplength=300).pack(pady=20)
        btn_frame = tk.Frame(self.master, bg="#2c3e50")
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Laptop (1280x720)", command=lambda: self.select_resolution("laptop")).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Masaüstü (1920x1080)", command=lambda: self.select_resolution("desktop")).pack(side="right", padx=10)
        self.master.update_idletasks()
        x = self.master.winfo_screenwidth() // 2 - self.master.winfo_width() // 2
        y = self.master.winfo_screenheight() // 2 - self.master.winfo_height() // 2
        self.master.geometry(f"+{x}+{y}")
        self.master.attributes("-topmost", True)
    def select_resolution(self, resolution_type):
        self.selected_resolution = resolution_type
        self.master.destroy()
    def on_closing(self):
        self.selected_resolution = None
        self.master.destroy()

class BotUI:
    def __init__(self, root, resolution_type):
        self.root = root
        self.resolution_type = resolution_type
        self.set_geometry_and_styles()
        self.root.title(f"{BOT_EXE_NAME.replace('.exe', '')} v{__version__}")
        self.root.configure(bg=self.colors['background'])
        try:
            self.root.iconbitmap(get_resource_path("app_icon.ico"))
        except tk.TclError:
            handle_error_and_notify("app_icon.ico bulunamadı veya yüklenemedi.", log_level=logging.WARNING)
        self.is_bot_running = False
        self.bot_thread = None
        self.start_event = threading.Event()
        self.game_area = None
        self.bot_start_time = None
        self.latest_update_info = None
        self.anaekran_image_path = get_resource_path(os.path.join("anaekran", "anaekran.png"))
        self.anaekran2_image_path = get_resource_path(os.path.join("anaekran", "anaekran2.png"))
        self.last_resort_x = tk.StringVar(value="")
        self.last_resort_y = tk.StringVar(value="")
        self.fetih_x = tk.StringVar(value="")  # Yeni eklenen fetih X koordinatı
        self.fetih_y = tk.StringVar(value="")  # Yeni eklenen fetih Y koordinatı
        self.task_manager = TaskManager(on_stats_update=self.handle_stats_update)
        self.image_paths = self.load_image_paths()
        self.selections = self.create_selection_vars()
        self.success_counts = self.create_stat_vars("success")
        self.failure_counts = self.create_stat_vars("failure")
        self.countdown_info = self.create_countdown_vars()
        self.license_active = True  # Always active - license removed
        self.expiration_timestamp = 0
        self.current_license_code = tk.StringVar(value="")
        self.tips_button_added = False
        self.emulator_button_added = False
        self.tips_ui = None
        self.last_shown_update_note_version = load_last_shown_update_note_version()
        self.setup_logging()
        self.setup_tasks()
        self.setup_ui()
        self.load_initial_config()
        # Otomatik güncelleme kontrolü devre dışı bırakıldı

    def perform_system_check(self):
        logging.info("Sistem kontrolü başlatılıyor...")

        if not self.is_valid_game_area():
            issues.append("- Geçersiz oyun alanı. Yeniden seçin.")
    
        # Oyun alanı kontrolü
        if not self.game_area or len(self.game_area) != 4:
            handle_error_and_notify("Oyun alanı tanımlı değil. Kurulum sekmesinden alan seçin.", notify_user=True)
            return False

        # Resim yolu kontrolü
        missing_images = []
        for task_name, task in self.task_manager.tasks.items():
            for key in task.kwargs.get('image_paths', {}).keys():
                if not os.path.exists(task.kwargs['image_paths'][key]):
                    missing_images.append(key)
        if missing_images:
            logging.error(f"Eksik görseller: {missing_images}")
            handle_error_and_notify(f"Şu görseller eksik: {', '.join(missing_images)}", notify_user=True)
            return False

        # Görev interval kontrolü (timed görevler)
        for name, task in self.task_manager.tasks.items():
            if task.is_timed:
                interval_var = self.selections.get(f"{name}_interval")
                if not interval_var or interval_var.get() < 1:
                    logging.warning(f"{name} için geçersiz zaman aralığı, varsayılan 10dk atanıyor.")
                    if interval_var:
                        interval_var.set(10)
                    task.interval = 10 * 60

        # Lisans kontrolü kaldırıldı - bot artık serbest

        logging.info("Sistem kontrolü başarıyla tamamlandı.")
        return True

    def handle_stats_update(self, stat_type, key, value):
        if stat_type == "success":
            current_value = self.success_counts[key].get()
            stats_queue.put(("success", key, current_value + 1))
        elif stat_type == "countdown":
            stats_queue.put(("countdown", key, value))
        elif stat_type == "failure":
            current_value = self.failure_counts[key].get()
            stats_queue.put(("failure", key, current_value + 1))

    def setup_tasks(self):
        task_config = [
            {"name": "dunyaheal", "func": perform_dunya_heal_sequence, "is_timed": False},
            {"name": "healing", "func": perform_healing_sequence, "is_timed": False},
            {"name": "daily", "func": perform_daily_tasks, "is_timed": False},
            {"name": "kutu", "func": perform_kutu_sequence, "is_timed": False},
            {"name": "anahtar", "func": perform_anahtar_sequence, "is_timed": False},
            {"name": "asker", "func": perform_asker_hasat_sequence, "is_timed": True},
            {"name": "bekcikulesi", "func": perform_bekcikulesi_sequence, "is_timed": True},
            {"name": "mesaj", "func": perform_mesaj_sequence, "is_timed": True},
            {"name": "savas", "func": perform_savas_sequence, "is_timed": True},
            {
                "name": "ittifak", "func": perform_ittifak_sequence, "is_timed": True,
                "extra_kwargs": {"rapid_click_image": "ittifak4", "rapid_click_count": 5}
            },
            {
                "name": "suadasi", "func": perform_suadasi_sequence, "is_timed": True,
                "extra_kwargs": {
                    "su3_offset_x": 10 if self.resolution_type == "laptop" else 20,
                    "su3_offset_y": 10 if self.resolution_type == "laptop" else 20
                }
            },
            {"name": "askerbas", "func": perform_askerbas_sequence, "is_timed": True},
            {"name": "fetih", "func": perform_fetih_sequence, "is_timed": True},
            {"name": "isyanci", "func": perform_isyanci_sequence, "is_timed": True},
        ]

        for config in task_config:
            name = config["name"]
            interval = self.selections[f"{name}_interval"].get() if config["is_timed"] else 0
            
            kwargs = {
                'game_area_region': self.game_area,
                'image_paths': self.image_paths,
                'confidence': self.selections[f"{name}_confidence"].get()
            }
            
            if "extra_kwargs" in config:
                kwargs.update(config["extra_kwargs"])

            self.task_manager.add_task(
                name=name,
                func=config["func"],
                kwargs=kwargs,
                is_timed=config["is_timed"],
                interval=interval
            )
        logging.info("Tüm görevler TaskManager'a eklendi ve yapılandırıldı.")

    def set_geometry_and_styles(self):
        self.colors = {
            'background': '#282c34',
            'frame': '#3c4049',
            'text': '#abb2bf',
            'accent': '#61afef',
            'accent_active': '#528bce',
            'danger': '#e06c75',
            'danger_active': '#be5046',
            'warning': '#d19a66',
            'success': '#98c379',
            'widget_bg': '#21252b'
        }
        
        self.font_family = "Segoe UI" if os.name == 'nt' else "Helvetica"

        if self.resolution_type == "laptop":
            self.root.geometry("900x700")
            self.base_font_size = 10
            self.header_font_size = 18
        else:
            self.root.geometry("1100x850")
            self.base_font_size = 12
            self.header_font_size = 22
        self.root.minsize(850, 650)
        
        style = ttk.Style()
        style.theme_use('clam')

        style.configure("TFrame", background=self.colors['background'])
        style.configure("TLabel", font=(self.font_family, self.base_font_size), background=self.colors['background'], foreground=self.colors['text'])
        style.configure("Card.TFrame", background=self.colors['frame'], relief='raised', borderwidth=1)
        style.configure("Header.TLabel", font=(self.font_family, self.header_font_size, "bold"), background=self.colors['background'], foreground=self.colors['accent'])
        style.configure("Status.TLabel", font=(self.font_family, self.base_font_size - 1), background=self.colors['background'], foreground=self.colors['text'])
        
        style.configure("TButton", font=(self.font_family, self.base_font_size, "bold"), padding=10, background=self.colors['accent'], foreground="#ffffff", borderwidth=0, relief=tk.RAISED)
        style.map("TButton", background=[('active', self.colors['accent_active'])])
        
        style.configure("Danger.TButton", background=self.colors['danger'])
        style.map("Danger.TButton", background=[('active', self.colors['danger_active'])])

        style.configure("TCheckbutton", font=(self.font_family, self.base_font_size), background=self.colors['frame'], foreground=self.colors['text'], indicatorrelief=tk.FLAT, padding=5)
        style.map('TCheckbutton', indicatorbackground=[('selected', self.colors['accent'])], background=[('active', self.colors['frame'])])

        style.configure("TSpinbox", font=(self.font_family, self.base_font_size), background=self.colors['widget_bg'], foreground=self.colors['text'], fieldbackground=self.colors['widget_bg'], borderwidth=1, relief=tk.FLAT)
        style.configure("TEntry", font=(self.font_family, self.base_font_size), background=self.colors['widget_bg'], foreground=self.colors['text'], fieldbackground=self.colors['widget_bg'], borderwidth=1, relief=tk.FLAT)

        style.configure("TNotebook", background=self.colors['background'], borderwidth=0)
        style.configure("TNotebook.Tab", font=(self.font_family, self.base_font_size, "bold"), padding=[12, 6], background=self.colors['frame'], foreground=self.colors['text'], borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", self.colors['accent'])], foreground=[("selected", "#ffffff")])

    def setup_logging(self):
        logging.basicConfig(filename='bot.log', level=logging.INFO,
                           format='%(asctime)s - %(levelname)s - %(message)s')
        handler = TkinterLogHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

    def setup_ui(self):
        header = tk.Frame(self.root, bg=self.colors['background'])
        header.pack(fill="x", pady=10, padx=10)
        ttk.Label(header, text=BOT_EXE_NAME.replace('.exe', ''), style="Header.TLabel").pack(side="left", padx=10)
        self.btn_toggle = ttk.Button(header, text="Botu Başlat", command=self.toggle_bot, state=tk.DISABLED)
        self.btn_toggle.pack(side="left", padx=10)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=5, padx=10, fill="both", expand=True)
        self.create_setup_tab()
        self.create_tasks_tab()
        self.create_game_time_tab()  # Yeni: Oyun içi zaman tabı
        self.create_log_tab()
        status_bar = tk.Frame(self.root, bg=self.colors['background'])
        status_bar.pack(fill="x", pady=5, padx=10)
        self.runtime_label = ttk.Label(status_bar, text="Süre: 00:00:00", style="Status.TLabel")
        self.runtime_label.pack(side="right", padx=10)

        # Initialize license status label
        self.license_status_label = ttk.Label(status_bar, text="Durum: Kontrol Ediliyor...", style="Status.TLabel")
        self.license_status_label.pack(side="left", padx=10)
        self.game_time_label = ttk.Label(status_bar, text="Oyun Saati: --:--", style="Status.TLabel")
        self.game_time_label.pack(side="right", padx=10)

    def create_setup_tab(self):
        setup_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(setup_frame, text="Kurulum")

        # Card for Game Area
        area_card = ttk.Frame(setup_frame, style="Card.TFrame", padding=15)
        area_card.pack(fill="x", expand=True, pady=(0, 10))
        
        ttk.Label(area_card, text="Oyun Alanı", font=(self.font_family, self.base_font_size + 4, "bold"), style="TLabel").pack(anchor="w", pady=(0, 10))
        
        self.area_label = ttk.Label(area_card, text="Oyun alanı seçilmedi.", wraplength=int(self.root.winfo_width() * 0.8), style="TLabel")
        self.area_label.pack(pady=5, fill="x")
        
        canvas_width = 400 if self.resolution_type == "desktop" else 320
        canvas_height = 200 if self.resolution_type == "desktop" else 160
        self.canvas = tk.Canvas(area_card, width=canvas_width, height=canvas_height, bg=self.colors['widget_bg'], bd=0, relief="flat")
        self.canvas.pack(pady=10)
        
        btn_frame = ttk.Frame(area_card, style="Card.TFrame")
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Oyun Alanını Seç", command=self.select_area_window).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Gündüz Resmi Seç", command=lambda: self.select_anaekran_image("day")).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Gece Resmi Seç", command=lambda: self.select_anaekran_image("night")).pack(side="left", padx=5)

        # Card for Last Resort Coordinates
        coord_card = ttk.Frame(setup_frame, style="Card.TFrame", padding=15)
        coord_card.pack(fill="x", expand=True, pady=10)

        ttk.Label(coord_card, text="Son Çare Koordinatları", font=(self.font_family, self.base_font_size + 2, "bold"), style="TLabel").pack(anchor="w", pady=(0, 10))
        ttk.Label(coord_card, text="Botun ana ekrana dönemediği durumlarda tıklanacak acil durum koordinatı.", style="TLabel").pack(anchor="w", pady=(0, 10))

        coord_entry_frame = ttk.Frame(coord_card, style="Card.TFrame")
        coord_entry_frame.pack(pady=5, anchor="w")
        
        ttk.Label(coord_entry_frame, text="X:", style="TLabel").pack(side="left", padx=(0, 5))
        ttk.Entry(coord_entry_frame, textvariable=self.last_resort_x, width=8).pack(side="left", padx=5)
        ttk.Label(coord_entry_frame, text="Y:", style="TLabel").pack(side="left", padx=(10, 5))
        ttk.Entry(coord_entry_frame, textvariable=self.last_resort_y, width=8).pack(side="left", padx=5)
        ttk.Button(coord_entry_frame, text="Koordinat Seç ('k' tuşu)", command=self.select_last_resort_coords).pack(side="left", padx=10)

        # Card for Fetih Coordinates
        fetih_card = ttk.Frame(setup_frame, style="Card.TFrame", padding=15)
        fetih_card.pack(fill="x", expand=True, pady=10)

        ttk.Label(fetih_card, text="Fetih Koordinatları", font=(self.font_family, self.base_font_size + 2, "bold"), style="TLabel").pack(anchor="w", pady=(0, 10))
        ttk.Label(fetih_card, text="Fetih görevleri için kullanılacak koordinat.", style="TLabel").pack(anchor="w", pady=(0, 10))

        fetih_entry_frame = ttk.Frame(fetih_card, style="Card.TFrame")
        fetih_entry_frame.pack(pady=5, anchor="w")
        
        ttk.Label(fetih_entry_frame, text="X:", style="TLabel").pack(side="left", padx=(0, 5))
        ttk.Entry(fetih_entry_frame, textvariable=self.fetih_x, width=8).pack(side="left", padx=5)
        ttk.Label(fetih_entry_frame, text="Y:", style="TLabel").pack(side="left", padx=(10, 5))
        ttk.Entry(fetih_entry_frame, textvariable=self.fetih_y, width=8).pack(side="left", padx=5)
        ttk.Button(fetih_entry_frame, text="Koordinat Seç ('f' tuşu)", command=self.select_fetih_coords).pack(side="left", padx=10)

    def create_tasks_tab(self):
        tasks_outer_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tasks_outer_frame, text="Görevler")

        tasks_scrolled_frame = ScrolledFrame(tasks_outer_frame, bg=self.colors['background'])
        tasks_scrolled_frame.pack(fill="both", expand=True)
        tasks_grid = tasks_scrolled_frame.interior
        tasks_grid.configure(bg=self.colors['background'])

        tasks = [
            ("dunyaheal", "Dünya Heal", "Tek Çalışır, Sadece iyileştirme ekranında kullanılması önerilir."),
            ("healing", "Yaralı İyileştirme", "Yaralı askerleri iyileştirir."),
            ("daily", "Günlük Görevler", "Günlük görevleri ve ödülleri toplar."),
            ("kutu", "Kutu Açma", "Etkinlik ve diğer kutuları açar."),
            ("anahtar", "Anahtar Sandıkları", "Anahtar sandıklarını açar."),
            ("asker", "Asker Hasadı", "Eğitilmiş askerleri toplar."),
            ("bekcikulesi", "Bekçi Kulesi", "Bekçi kulesi ödüllerini toplar."),
            ("mesaj", "Mesaj Kontrolü", "Gelen mesajları ve raporları kontrol eder."),
            ("savas", "Savaş Görevleri", "Otomatik savaş görevlerini yürütür."),
            ("ittifak", "İttifak Görevleri", "İttifak yardım ve görevlerini tamamlar."),
            ("suadasi", "Su Adası", "Su adası etkinliğini tamamlar."),
            ("askerbas", "Asker Basma", "Belirlenen türde asker basar."),
            ("fetih", "Fetih Görevleri", "Fetih ile ilgili görevleri yapar."),
            ("isyanci", "İsyancı Görevleri", "İsyancılara saldırır ve ödülleri toplar."),
        ]

        for key, label, desc in tasks:
            card = ttk.Frame(tasks_grid, style="Card.TFrame", padding=15)
            card.pack(fill="x", pady=5, padx=10)
            
            header_frame = ttk.Frame(card, style="Card.TFrame")
            header_frame.pack(fill="x")
            
            ttk.Checkbutton(header_frame, text=label, variable=self.selections[key], style="TCheckbutton", command=self.on_selection_change).pack(side="left")

            
            sub_frame = ttk.Frame(header_frame, style="Card.TFrame")
            sub_frame.pack(side="right")

            ttk.Label(sub_frame, text="Başarı:", style="TLabel", background=self.colors['frame']).pack(side="left", padx=(10, 2))
            ttk.Label(sub_frame, textvariable=self.success_counts[key], foreground=self.colors['success'], background=self.colors['frame']).pack(side="left")
            
            ttk.Label(sub_frame, text="Hata:", style="TLabel", background=self.colors['frame']).pack(side="left", padx=(10, 2))
            ttk.Label(sub_frame, textvariable=self.failure_counts[key], foreground=self.colors['danger'], background=self.colors['frame']).pack(side="left")

            ttk.Label(card, text=desc, wraplength=self.root.winfo_width() - 100, justify=tk.LEFT, style="TLabel", background=self.colors['frame']).pack(anchor="w", pady=(5, 10))

            config_frame = ttk.Frame(card, style="Card.TFrame")
            config_frame.pack(fill="x", pady=5)

            ttk.Label(config_frame, text="Eşleşme:", style="TLabel", background=self.colors['frame']).pack(side="left", padx=(0, 5))
            ttk.Spinbox(config_frame, from_=0.1, to=1.0, increment=0.05, textvariable=self.selections[f"{key}_confidence"], width=6).pack(side="left", padx=5)

            if key in self.countdown_info:
                interval_var = self.selections[f"{key}_interval"]
                countdown_var = self.countdown_info[key]
                ttk.Label(config_frame, text="Aralık(dk):", style="TLabel", background=self.colors['frame']).pack(side="left", padx=(15, 5))
                ttk.Spinbox(config_frame, from_=1, to=120, textvariable=interval_var, width=6).pack(side="left", padx=5)
                ttk.Label(config_frame, textvariable=countdown_var, foreground=self.colors['warning'], background=self.colors['frame']).pack(side="left", padx=10)

        bottom_card = ttk.Frame(tasks_outer_frame, style="TFrame", padding="10")
        bottom_card.pack(fill="x", pady=10)
        
        ttk.Checkbutton(bottom_card, text="Bot Başladığında Pencereyi Gizle", variable=self.selections["hide_window"], style="TCheckbutton").pack(side="left", anchor="w")
        
        btn_frame = ttk.Frame(bottom_card, style="TFrame")
        btn_frame.pack(side="right")
        ttk.Button(btn_frame, text="Ayarları Kaydet", command=self.save_settings).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Ayarları Yükle", command=self.load_settings).pack(side="left", padx=5)

    def create_license_tab(self):
        license_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(license_frame, text="Lisans")

        license_card = ttk.Frame(license_frame, style="Card.TFrame", padding=15)
        license_card.pack(fill="x", expand=True, pady=(0, 10))
        
        ttk.Label(license_card, text="Lisans Yönetimi", font=(self.font_family, self.base_font_size + 4, "bold"), style="TLabel", background=self.colors['frame']).pack(anchor="w", pady=(0, 10))
        ttk.Label(license_card, text="Lisans kodunuzu girerek botu aktive edin.", style="TLabel", background=self.colors['frame']).pack(anchor="w", pady=(0, 10))
        
        entry_frame = ttk.Frame(license_card, style="Card.TFrame")
        entry_frame.pack(pady=10, fill="x")
        ttk.Entry(entry_frame, textvariable=self.current_license_code, width=40).pack(side="left", fill="x", expand=True)
        self.activate_license_btn = ttk.Button(entry_frame, text="Aktive Et", command=self.activate_license_code)
        self.activate_license_btn.pack(side="left", padx=10)
        
        self.license_status_label = ttk.Label(license_card, text="Durum: Kontrol Ediliyor...", font=(self.font_family, self.base_font_size, "italic"), style="TLabel", background=self.colors['frame'])
        self.license_status_label.pack(pady=10, anchor="w")

        social_card = ttk.Frame(license_frame, style="Card.TFrame", padding=15)
        social_card.pack(fill="x", expand=True, pady=10)
        
        ttk.Label(social_card, text="Topluluk", font=(self.font_family, self.base_font_size + 2, "bold"), style="TLabel", background=self.colors['frame']).pack(anchor="w", pady=(0, 10))
        
        social_media_frame = ttk.Frame(social_card, style="Card.TFrame")
        social_media_frame.pack(pady=10)

        try:
            discord_img_path = get_resource_path(os.path.join("SosyalMedya", "discord.png"))
            discord_img = Image.open(discord_img_path).resize((40, 40), Image.Resampling.LANCZOS)
            self.discord_photo = ImageTk.PhotoImage(discord_img)
            discord_label = tk.Label(social_media_frame, image=self.discord_photo, cursor="hand2", bg=self.colors['frame'])
            discord_label.pack(side="left", padx=15)
            discord_label.bind("<Button-1>", lambda e: open_url("https://discord.gg/pJ8Sf464"))
        except Exception as e:
            handle_error_and_notify(f"Discord ikonu yüklenemedi: {e}", log_level=logging.ERROR, notify_user=False)

        try:
            telegram_img_path = get_resource_path(os.path.join("SosyalMedya", "telegram.png"))
            telegram_img = Image.open(telegram_img_path).resize((40, 40), Image.Resampling.LANCZOS)
            self.telegram_photo = ImageTk.PhotoImage(telegram_img)
            telegram_label = tk.Label(social_media_frame, image=self.telegram_photo, cursor="hand2", bg=self.colors['frame'])
            telegram_label.pack(side="left", padx=15)
            telegram_label.bind("<Button-1>", lambda e: open_url("https://t.me/+wHPg9nJt1qljMDFk"))
        except Exception as e:
            handle_error_and_notify(f"Telegram ikonu yüklenemedi: {e}", log_level=logging.ERROR, notify_user=False)

    def show_startup_checklist(self):
        issues = []

        if not self.is_valid_game_area():
            issues.append("- Geçersiz oyun alanı. Yeniden seçin.")
        # Oyun alanı kontrolü
        if not self.game_area or len(self.game_area) != 4:
            issues.append("- Oyun alanı seçilmemiş.")

        # Lisans kontrolü kaldırıldı - bot artık serbest

        # Ana ekran görselleri kontrolü
        if not (os.path.exists(self.anaekran_image_path) or os.path.exists(self.anaekran2_image_path)):
            issues.append("- Ana ekran görselleri eksik.")

        # Dünya Heal kontrolü
        if self.selections["dunyaheal"].get():
            for key, var in self.selections.items():
                if key != "dunyaheal" and isinstance(var, tk.BooleanVar) and var.get():
                    issues.append("- 'Dünya Heal' seçiliyken başka görev seçilemez.")

        if issues:
            checklist = "\n".join(issues)
            messagebox.showwarning("Başlangıç Kontrol Listesi", f"Başlamadan önce aşağıdaki sorunları düzeltin:\n\n{checklist}")
            return False

        messagebox.showinfo("Başlangıç Kontrolü", "Tüm sistem kontrolleri başarılı. Bot başlatılabilir.")
        return True

    def create_update_tab(self):
        update_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(update_frame, text="Güncelleme")

        update_card = ttk.Frame(update_frame, style="Card.TFrame", padding=15)
        update_card.pack(fill="x", expand=True, pady=(0, 10))
        
        ttk.Label(update_card, text="Yazılım Güncelleme", font=(self.font_family, self.base_font_size + 4, "bold"), style="TLabel", background=self.colors['frame']).pack(anchor="w", pady=(0, 10))
        self.update_status_label = ttk.Label(update_card, text="Durum: Başlangıç kontrolü yapılıyor...", style="TLabel", background=self.colors['frame'])
        self.update_status_label.pack(pady=5, anchor="w")
        
        self.update_progress_bar = ttk.Progressbar(update_card, length=300, mode="determinate")
        self.update_progress_bar.pack(pady=10, fill="x")
        self.update_progress_label = ttk.Label(update_card, text="", style="TLabel", background=self.colors['frame'])
        self.update_progress_label.pack(pady=5, anchor="w")
        
        btn_frame = ttk.Frame(update_card, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=10)
        self.btn_check_update = ttk.Button(btn_frame, text="Güncellemeleri Kontrol Et", command=self.check_for_updates_manual)
        self.btn_check_update.pack(side="left", padx=5)
        self.btn_install_update = ttk.Button(btn_frame, text="Güncellemeyi Yükle", command=self.install_update, state=tk.DISABLED)
        self.btn_install_update.pack(side="left", padx=5)

        notes_card = ttk.Frame(update_frame, style="Card.TFrame", padding=15)
        notes_card.pack(fill="both", expand=True, pady=10)
        
        ttk.Label(notes_card, text="Sürüm Notları", font=(self.font_family, self.base_font_size + 2, "bold"), style="TLabel", background=self.colors['frame']).pack(anchor="w", pady=(0, 10))
        self.update_info_text = ScrolledText(notes_card, height=5, state="disabled", bg=self.colors['widget_bg'], fg=self.colors['text'], font=("Consolas", self.base_font_size - 1), relief="flat", bd=1)
        self.update_info_text.pack(pady=5, fill="both", expand=True)

    def create_game_time_tab(self):
        game_time_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(game_time_frame, text="Oyun Saati")
        
        time_card = ttk.Frame(game_time_frame, style="Card.TFrame", padding=15)
        time_card.pack(fill="x", expand=True)
        
        ttk.Label(time_card, text="Oyun İçi Zaman Takibi", font=(self.font_family, self.base_font_size + 4, "bold"), style="TLabel", background=self.colors['frame']).pack(anchor="w", pady=(0, 10))
        
        # Ana zaman gösterimi
        self.current_time_label = ttk.Label(time_card, text="Mevcut Oyun Saati: --:--", font=(self.font_family, self.base_font_size + 6, "bold"), style="TLabel", background=self.colors['frame'], foreground=self.colors['accent'])
        self.current_time_label.pack(pady=15)
        
        # Zaman ayarlama bölümü
        time_setting_frame = ttk.Frame(time_card, style="Card.TFrame")
        time_setting_frame.pack(fill="x", pady=10)
        
        ttk.Label(time_setting_frame, text="Manuel Zaman Ayarı:", style="TLabel", background=self.colors['frame']).pack(anchor="w", pady=(0, 5))
        
        manual_time_frame = ttk.Frame(time_setting_frame, style="Card.TFrame")
        manual_time_frame.pack(anchor="w", pady=5)
        
        self.hour_var = tk.StringVar(value="12")
        self.minute_var = tk.StringVar(value="00")
        
        ttk.Label(manual_time_frame, text="Saat:", style="TLabel", background=self.colors['frame']).pack(side="left", padx=(0, 5))
        ttk.Spinbox(manual_time_frame, from_=0, to=23, textvariable=self.hour_var, width=4, format="%02.0f").pack(side="left", padx=5)
        ttk.Label(manual_time_frame, text="Dakika:", style="TLabel", background=self.colors['frame']).pack(side="left", padx=(10, 5))
        ttk.Spinbox(manual_time_frame, from_=0, to=59, textvariable=self.minute_var, width=4, format="%02.0f").pack(side="left", padx=5)
        ttk.Button(manual_time_frame, text="Zamanı Ayarla", command=self.set_game_time).pack(side="left", padx=10)
        
        # Otomatik zaman algılama
        auto_detect_frame = ttk.Frame(time_card, style="Card.TFrame")
        auto_detect_frame.pack(fill="x", pady=15)
        
        ttk.Label(auto_detect_frame, text="Otomatik Zaman Algılama:", style="TLabel", background=self.colors['frame']).pack(anchor="w", pady=(0, 5))
        ttk.Label(auto_detect_frame, text="Bot çalışırken oyun ekranından zamanı otomatik olarak okuyacaktır.", style="TLabel", background=self.colors['frame'], foreground=self.colors['warning']).pack(anchor="w", pady=(0, 10))
        
        detect_btn_frame = ttk.Frame(auto_detect_frame, style="Card.TFrame")
        detect_btn_frame.pack(anchor="w")
        
        ttk.Button(detect_btn_frame, text="Şimdi Zamanı Oku", command=self.detect_game_time).pack(side="left", padx=5)
        ttk.Button(detect_btn_frame, text="Otomatik Okumayı Başlat", command=self.start_time_detection).pack(side="left", padx=5)
        ttk.Button(detect_btn_frame, text="Otomatik Okumayı Durdur", command=self.stop_time_detection).pack(side="left", padx=5)
        
        # Zaman bilgileri
        info_card = ttk.Frame(game_time_frame, style="Card.TFrame", padding=15)
        info_card.pack(fill="both", expand=True, pady=10)
        
        ttk.Label(info_card, text="Zaman Bilgileri", font=(self.font_family, self.base_font_size + 2, "bold"), style="TLabel", background=self.colors['frame']).pack(anchor="w", pady=(0, 10))
        
        self.time_info_text = tk.Text(info_card, height=8, bg=self.colors['widget_bg'], fg=self.colors['text'], font=(self.font_family, self.base_font_size - 1), relief="flat", bd=1, state="disabled")
        self.time_info_text.pack(fill="both", expand=True)
        
        # Zaman değişkenleri
        self.game_time_hours = 12
        self.game_time_minutes = 0
        self.time_detection_active = False
        self.time_detection_thread = None
        
        # Zamanı güncelle
        self.root.after(1000, self.update_game_time_display)
    
    def create_log_tab(self):
        log_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(log_frame, text="Loglar")
        
        log_card = ttk.Frame(log_frame, style="Card.TFrame", padding=15)
        log_card.pack(fill="both", expand=True)
        
        ttk.Label(log_card, text="Bot Çalışma Logları", font=(self.font_family, self.base_font_size + 4, "bold"), style="TLabel", background=self.colors['frame']).pack(anchor="w", pady=(0, 10))
        self.log_text = ScrolledText(log_card, height=20, state="disabled", bg=self.colors['widget_bg'], fg=self.colors['text'], font=("Consolas", self.base_font_size - 1), relief="flat", bd=1)
        self.log_text.pack(pady=5, fill="both", expand=True)
        
        self.log_text.tag_config("ERROR", foreground=self.colors['danger'])
        self.log_text.tag_config("WARNING", foreground=self.colors['warning'])
        self.log_text.tag_config("INFO", foreground=self.colors['text'])

    def create_selection_vars(self):
        return {
            "dunyaheal": tk.BooleanVar(value=True),
            "dunyaheal_confidence": tk.DoubleVar(value=0.7),
            "healing": tk.BooleanVar(value=True), "daily": tk.BooleanVar(value=True),
            "kutu": tk.BooleanVar(value=True), "anahtar": tk.BooleanVar(value=True),
            "asker": tk.BooleanVar(value=True), "bekcikulesi": tk.BooleanVar(value=True),
            "mesaj": tk.BooleanVar(value=True), "savas": tk.BooleanVar(value=False),
            "ittifak": tk.BooleanVar(value=False), "suadasi": tk.BooleanVar(value=False),
            "askerbas": tk.BooleanVar(value=True), "hide_window": tk.BooleanVar(value=False),
            "fetih": tk.BooleanVar(value=False),
            "healing_confidence": tk.DoubleVar(value=0.7), "daily_confidence": tk.DoubleVar(value=0.8),
            "kutu_confidence": tk.DoubleVar(value=0.8), "anahtar_confidence": tk.DoubleVar(value=0.8),
            "asker_confidence": tk.DoubleVar(value=0.8), "bekcikulesi_confidence": tk.DoubleVar(value=0.8),
            "mesaj_confidence": tk.DoubleVar(value=0.7), "savas_confidence": tk.DoubleVar(value=0.6),
            "ittifak_confidence": tk.DoubleVar(value=0.8), "suadasi_confidence": tk.DoubleVar(value=0.55),
            "askerbas_confidence": tk.DoubleVar(value=0.8),
            "fetih_confidence": tk.DoubleVar(value=0.8),
            "savas_interval": tk.IntVar(value=10), "ittifak_interval": tk.IntVar(value=10),
            "mesaj_interval": tk.IntVar(value=5), "suadasi_interval": tk.IntVar(value=30),
            "askerbas_interval": tk.IntVar(value=10), "asker_interval": tk.IntVar(value=10),
            "bekcikulesi_interval": tk.IntVar(value=10),
            "fetih_interval": tk.IntVar(value=60),
            "isyanci": tk.BooleanVar(value=False),
            "isyanci_confidence": tk.DoubleVar(value=0.7),
            "isyanci_interval": tk.IntVar(value=60),
        }

    def create_stat_vars(self, stat_type):
        return {key: tk.IntVar(value=0) for key in ["healing", "daily", "kutu", "anahtar", "asker", "bekcikulesi", "mesaj", "savas", "ittifak", "suadasi", "askerbas", "dunyaheal", "fetih", "isyanci"]}

    def create_countdown_vars(self):
        return {key: tk.StringVar(value="Hazır") for key in ["savas", "ittifak", "mesaj", "suadasi", "askerbas", "asker", "bekcikulesi", "fetih", "isyanci"]}

    def load_initial_config(self):
        config = load_config()
        if config:
            if 'game_area_region' in config and len(config['game_area_region']) == 4:
                self.game_area = tuple(config['game_area_region'])
                self.area_label.config(text=f"Mevcut Oyun Alanı: {self.game_area}")
                logging.info("Oyun alanı yüklendi.")
            if 'anaekran_image_path' in config:
                self.anaekran_image_path = config['anaekran_image_path']
                self.image_paths['anaekran'] = self.anaekran_image_path
                logging.info(f"Ana ekran (gündüz) resmi: {self.anaekran_image_path}")
            if 'anaekran2_image_path' in config:
                self.anaekran2_image_path = config['anaekran2_image_path']
                self.image_paths['anaekran2'] = self.anaekran2_image_path
                logging.info(f"Ana ekran (gece) resmi: {self.anaekran2_image_path}")
            if 'last_resort_x' in config and 'last_resort_y' in config:
                self.last_resort_x.set(str(config['last_resort_x']) if config['last_resort_x'] else "")
                self.last_resort_y.set(str(config['last_resort_y']) if config['last_resort_y'] else "")
            if 'fetih_x' in config and 'fetih_y' in config:  # Yeni eklenen fetih koordinatları
                self.fetih_x.set(str(config['fetih_x']) if config['fetih_x'] else "")
                self.fetih_y.set(str(config['fetih_y']) if config['fetih_y'] else "")
            if 'last_execution_times' in config:
                pass
        user_data = load_user_data()
        if 'license_code' in user_data:
            self.current_license_code.set(user_data['license_code'])
        self.last_shown_update_note_version = load_last_shown_update_note_version()
        self.load_settings()
        if self.game_area:
            self.update_area_preview()
        self.root.after(200, self.update_log_view)
        self.root.after(200, self.update_stats_view)
        self.root.after(200, self.update_download_progress)
        self.root.after(1000, self.update_license_status)
        self.root.after(900000, self.periodic_license_check)
        self.root.after(1000, self.update_runtime_status)

    def load_image_paths(self):
        image_paths = {}
        image_folders = [
            "anaekran", "dunyaheal", "heal", "kutu", "anahtar", "asker",
            "bekcikulesi", "geri", "mesaj", "savas", "ittifak", "suadasi",
            "askerbas", "fetih", "isyanci"
        ]
        for folder in image_folders:
            folder_path = get_resource_path(folder)
            if not os.path.isdir(folder_path):
                logging.warning(f"Resim klasörü bulunamadı: {folder_path}")
                continue
            for filename in os.listdir(folder_path):
                if filename.endswith(".png"):
                    key = os.path.splitext(filename)[0]
                    if key in image_paths:
                        logging.warning(f"Tekrarlanan resim anahtarı '{key}'. '{folder}' klasöründeki resim, öncekini geçersiz kılacak.")
                    image_paths[key] = get_resource_path(os.path.join(folder, filename))
        
        logging.info(f"{len(image_paths)} adet resim yolu yüklendi.")
        return image_paths

    def update_log_view(self):
        while not log_queue.empty():
            level, message = log_queue.get()
            self.log_text.config(state="normal")
            if level in ("ERROR", "WARNING", "INFO"):
                self.log_text.insert(tk.END, f"{message}\n", level)
            else:
                self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.config(state="disabled")
            self.log_text.see(tk.END)
        self.root.after(200, self.update_log_view)

    def update_stats_view(self):
        while not stats_queue.empty():
            stat_type, key, value = stats_queue.get()
            if stat_type == "success":
                if key in self.success_counts:
                    self.success_counts[key].set(value)
            elif stat_type == "failure":
                if key in self.failure_counts:
                    self.failure_counts[key].set(value)
            elif stat_type == "countdown":
                if key in self.countdown_info:
                    self.countdown_info[key].set(value)
        self.root.after(200, self.update_stats_view)

    def update_download_progress(self):
        while not update_progress_queue.empty():
            bytes_downloaded, total_size = update_progress_queue.get()
            if total_size > 0:
                progress = (bytes_downloaded / total_size) * 100
                self.update_progress_bar["value"] = progress
                self.update_progress_label.config(text=f"{bytes_downloaded/1024/1024:.2f} MB / {total_size/1024/1024:.2f} MB")
            else:
                self.update_progress_bar["value"] = 0
                self.update_progress_label.config(text="İndirme bekleniyor...")
        self.root.after(100, self.update_download_progress)

    def update_license_status(self):
        # Bot artık lisanssız çalışıyor - her zaman aktif göster
        self.license_active = True
        
        # UI bileşenlerini yalnızca bir kez ekle
        if not self.tips_button_added:
            try:
                self.tips_ui = TipsUI(self.root, self.license_active, self.base_font_size, self.colors)
                header = self.root.winfo_children()[0]
                ttk.Button(header, text="İpuçları", command=self.tips_ui.show, style="TButton").pack(side="left", padx=10)
                self.tips_button_added = True
                logging.info("İpuçları butonu başlık çubuğuna eklendi.")
            except Exception as e:
                logging.warning(f"İpuçları butonu eklenirken hata: {e}")

        if not self.emulator_button_added:
            try:
                header = self.root.winfo_children()[0]
                ttk.Button(header, text="Emülatör Başlat", command=self.start_emulator_ui, style="TButton").pack(side="left", padx=10)
                self.emulator_button_added = True
                logging.info("Emülatör Başlat butonu başlık çubuğuna eklendi.")
            except Exception as e:
                logging.warning(f"Emülatör butonu eklenirken hata: {e}")
        
        # Her zaman aktif durumu göster
        self.license_status_label.config(text="Durum: Aktif (Lisanssız Sürüm)", foreground=self.colors['accent'])
        
        # Bot başlatma butonu her zaman aktif (lisanstan bağımsız)
        if self.game_area:
            self.btn_toggle.config(state=tk.NORMAL)
        else:
            self.btn_toggle.config(state=tk.DISABLED)

        # Durumu güncellemek için tekrar çağır (daha az sıklıkta)
        self.root.after(300000, self.update_license_status)  # 5 dakikada bir

    def start_emulator_ui(self):
        try:
            from win_optimizer_advanced import WinOptimizerApp
            emulator_root = tk.Toplevel(self.root)
            emulator_root.title("Emülatör Optimizasyonu")
            app = WinOptimizerApp(emulator_root)
            logging.info("Emülatör optimizasyon arayüzü başlatıldı.")
        except Exception as e:
            handle_error_and_notify(f"Emülatör arayüzü başlatılamadı: {str(e)}", notify_user=True, log_level=logging.ERROR) 

    def periodic_license_check(self):
        user_data = load_user_data()
        license_code = user_data.get('license_code')
        if license_code:
            logging.info("Periyodik lisans sunucu kontrolü yapılıyor...")
            threading.Thread(target=self._check_license_online, args=(license_code,), daemon=True).start()
        self.root.after(900000, self.periodic_license_check)

    def _check_license_online(self, license_code):
        response = check_license_status(license_code, BOT_API_KEY)
        if response and response.get('status') == 'success' and 'expiration_date' in response:
            user_data = load_user_data()
            user_data['expiration_date'] = response['expiration_date']
            save_user_data(user_data)
            logging.info(f"Lisans durumu API'den güncellendi.")
        else:
            handle_error_and_notify(
                f"Lisans durumu API'den alınamadı: {response.get('message', 'Bilinmeyen Hata')}",
                log_level=logging.WARNING,
                notify_user=False
            )
        self.root.after(0, self.update_license_status)

    def update_runtime_status(self):
        if self.is_bot_running and self.bot_start_time:
            elapsed_time = time.time() - self.bot_start_time
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.runtime_label.config(text=f"Süre: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
        else:
            self.runtime_label.config(text="Süre: 00:00:00")
        self.root.after(1000, self.update_runtime_status)

    def toggle_bot(self):
        if self.is_bot_running:
            self.stop_bot()
        else:
            self.start_bot()

    def start_bot(self):
        if not self.show_startup_checklist():
            return
        if not self.perform_system_check():
            return
        if not self.game_area:
            handle_error_and_notify("Lütfen önce 'Kurulum' sekmesinden oyun alanını seçin.", notify_user=True)
            return
        self.is_bot_running = True
        self.btn_toggle.config(text="Botu Durdur", style="Danger.TButton")
        self.license_status_label.config(text="Çalışıyor", foreground=self.colors['accent'])
        self.bot_start_time = time.time()
        
        self.update_task_manager_tasks()
        self.task_manager.update_task_selection(self.get_current_selections())

        self.start_event.set()
        self.bot_thread = threading.Thread(target=self._bot_loop, daemon=True)
        self.bot_thread.start()
        logging.info("Bot başlatıldı.")
        if self.selections["hide_window"].get():
            self.root.withdraw()

    def get_current_selections(self):
        return {key: var.get() for key, var in self.selections.items()}

    def update_task_manager_tasks(self):
        for name, task in self.task_manager.tasks.items():
            task.kwargs['confidence'] = self.selections[f"{name}_confidence"].get()
            task.kwargs['game_area_region'] = self.game_area
            if task.is_timed:
                task.interval = self.selections[f"{name}_interval"].get() * 60

    def stop_bot(self):
        if self.is_bot_running:
            self.is_bot_running = False
            self.start_event.clear()
            self.btn_toggle.config(text="Botu Başlat", style="TButton")
            self.license_status_label.config(text="Durduruldu", foreground=self.colors['danger'])
            self.bot_start_time = None
            if self.bot_thread and self.bot_thread.is_alive():
                logging.info("Bot durdurma işlemi bekleniyor...")
            
            self.save_last_execution_times()

            if not self.root.state() == 'normal':
                self.root.deiconify()
            logging.info("Bot durduruldu.")

    def _bot_loop(self):
        idle_sleep_time = random.uniform(3.0, 7.0)
        anaekran_paths = [
            get_resource_path(os.path.join("anaekran", "anaekran.png")),
            get_resource_path(os.path.join("anaekran", "anaekran2.png"))
        ]

        while self.is_bot_running:
            try:
                last_x = int(self.last_resort_x.get()) if self.last_resort_x.get() else None
                last_y = int(self.last_resort_y.get()) if self.last_resort_y.get() else None
                fetih_x = int(self.fetih_x.get()) if self.fetih_x.get() else None
                fetih_y = int(self.fetih_y.get()) if self.fetih_y.get() else None
            except (ValueError, tk.TclError):
                last_x, last_y = None, None
                fetih_x, fetih_y = None, None
                handle_error_and_notify("Koordinatlar geçersiz. Lütfen kontrol edin.", log_level=logging.WARNING, notify_user=False)

            # Ana ekrana dönme kontrolü
            recovery_success = perform_recovery_sequence(
                game_area_region=self.game_area,
                image_paths=self.image_paths,
                anaekran_image_paths=anaekran_paths,
                last_resort_x=last_x,
                last_resort_y=last_y
            )
            if recovery_success is False:
                handle_error_and_notify(
                    "Bot ana ekrana dönemedi ve takıldı. Lütfen oyunu kontrol edin.",
                    log_level=logging.CRITICAL, notify_user=True, contact_discord=True, contact_telegram=True
                )
                self.root.after(0, self.stop_bot)
                return

            # Sıradaki görevi al
            current_selections = self.get_current_selections()
            self.task_manager.update_task_selection(current_selections)
            next_task = self.task_manager.get_next_task(current_selections)

            if next_task:
                # Fetih görevi için koordinatları ekle
                if next_task.name == "fetih":
                    next_task.kwargs['fetih_x'] = fetih_x
                    next_task.kwargs['fetih_y'] = fetih_y
                result = next_task.run()
                self.task_manager.process_task_result(next_task, result, current_selections)
                if result == TaskStatus.FAILURE:
                    time.sleep(random.uniform(1.0, 2.0))
            else:
                logging.info(f"Çalıştırılacak görev yok. {idle_sleep_time:.1f} saniye bekleniyor...")
                time.sleep(idle_sleep_time)

            time.sleep(random.uniform(0.5, 1.5))
    def on_selection_change(self, changed_key=None):
        if self.selections["dunyaheal"].get():
            # Diğer tüm görevleri devre dışı bırak
            for key in self.selections:
                if key not in ["dunyaheal", "dunyaheal_confidence", "hide_window"]:
                    if isinstance(self.selections[key], tk.BooleanVar):
                        self.selections[key].set(False)
            messagebox.showinfo("Uyarı", "'Dünya Heal' seçili olduğu için diğer görevler devre dışı bırakıldı.")

    def save_last_execution_times(self):
        config = load_config()
        last_times = {task.name: task.last_execution_time for task in self.task_manager.timed_tasks}
        config['last_execution_times'] = last_times
        save_config(config)
        logging.info("Görevlerin son çalışma zamanları kaydedildi.")

    def load_last_execution_times(self):
        config = load_config()
        last_times = config.get('last_execution_times', {})
        for name, timestamp in last_times.items():
            if name in self.task_manager.tasks:
                self.task_manager.tasks[name].last_execution_time = timestamp
        logging.info("Görevlerin son çalışma zamanları yüklendi.")

    def select_area_window(self):
        selection_root = tk.Toplevel(self.root)
        selection_root.attributes("-fullscreen", True)
        selection_root.attributes("-alpha", 0.3)
        selection_root.wait_visibility(selection_root)
        selection_root.attributes("-topmost", True)
        canvas = tk.Canvas(selection_root, cursor="cross", bg="gray", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_text(selection_root.winfo_screenwidth()/2, 50,
                        text="Oyun alanını seçmek için sürükleyip bırakın. (Bitirmek için ESC)",
                        font=("Helvetica", 20, "bold"), fill="white")
        start_x, start_y = None, None
        rect_id = None
        def on_mouse_down(event):
            nonlocal start_x, start_y
            start_x, start_y = event.x, event.y
        def on_mouse_drag(event):
            nonlocal rect_id
            if start_x is not None:
                if rect_id:
                    canvas.delete(rect_id)
                rect_id = canvas.create_rectangle(start_x, start_y, event.x, event.y, outline="red", width=3)
        def on_mouse_up(event):
            if start_x is not None:
                x1 = min(start_x, event.x)
                y1 = min(start_y, event.y)
                x2 = max(start_x, event.x)
                y2 = max(start_y, event.y)
                if x2 <= x1 or y2 <= y1:
                    handle_error_and_notify("Geçersiz oyun alanı seçildi. Genişlik ve yükseklik pozitif olmalı.", notify_user=True)
                    selection_root.destroy()
                    return
                self.game_area = (x1, y1, x2, y2)
                self.area_label.config(text=f"Oyun Alanı Seçildi: {self.game_area}")
                config = load_config()
                config['game_area_region'] = self.game_area
                save_config(config)
                logging.info(f"Oyun alanı kaydedildi: {self.game_area}")
                self.update_area_preview()
                self.btn_toggle.config(state=tk.NORMAL)
                selection_root.destroy()
        def on_escape(event):
            selection_root.destroy()
            logging.info("Oyun alanı seçimi iptal edildi.")
        canvas.bind("<ButtonPress-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)
        selection_root.bind("<Escape>", on_escape)

    def is_valid_game_area(self):
        if not self.game_area or len(self.game_area) != 4:
            return False
        x1, y1, x2, y2 = self.game_area
        return (x2 - x1) > 10 and (y2 - y1) > 10

    def update_area_preview(self):
        logging.info(f"update_area_preview çağrıldı, game_area: {self.game_area}")
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if self.game_area and len(self.game_area) == 4:
            try:
                x1, y1, x2, y2 = self.game_area
                logging.info(f"game_area koordinatları: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
                if x2 <= x1 or y2 <= y1:
                    raise ValueError("Geçersiz oyun alanı: genişlik ve yükseklik pozitif olmalı.")
                screen_width, screen_height = pyautogui.size()
                scale_x = canvas_width / screen_width
                scale_y = canvas_height / screen_height
                screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
                img = screenshot
                img = img.resize((int((x2-x1)*scale_x), int((y2-y1)*scale_y)), Image.Resampling.LANCZOS)
                self.preview_image = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, image=self.preview_image, anchor="nw")
                self.canvas.create_rectangle(x1 * scale_x, y1 * scale_y, x2 * scale_x, y2 * scale_y, outline="#1abc9c", width=2)
                self.canvas.create_text(canvas_width/2, canvas_height/2, text=f"Seçili Alan: {x2-x1}x{y2-y1}", fill="#2c3e50", font=("Helvetica", self.base_font_size -1))
            except Exception as e:
                handle_error_and_notify(f"Önizleme ekran görüntüsü alınamadı: {e}", log_level=logging.ERROR, notify_user=False)
                self.canvas.create_text(canvas_width/2, canvas_height/2, text=f"Önizleme alınamadı: {e}", fill="#888", font=("Helvetica", self.base_font_size))
        else:
            logging.info("Oyun alanı seçilmedi veya geçersiz.")
            self.canvas.create_text(canvas_width/2, canvas_height/2, text="Oyun Alanı Önizlemesi (Alan Seçilmedi)", fill="#888", font=("Helvetica", self.base_font_size))

    def select_anaekran_image(self, time_of_day):
        file_path = filedialog.askopenfilename(title=f"Ana Ekran Resmini Seçin ({time_of_day.capitalize()})", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            config = load_config()
            if time_of_day == "day":
                self.anaekran_image_path = file_path
                self.image_paths['anaekran'] = file_path
                config['anaekran_image_path'] = file_path
                logging.info(f"Ana ekran (gündüz) resmi güncellendi: {file_path}")
                messagebox.showinfo("Bilgi", f"Ana ekran (gündüz) resmi güncellendi: {os.path.basename(file_path)}")
            elif time_of_day == "night":
                self.anaekran2_image_path = file_path
                self.image_paths['anaekran2'] = file_path
                config['anaekran2_image_path'] = file_path
                logging.info(f"Ana ekran (gece) resmi güncellendi: {file_path}")
                messagebox.showinfo("Bilgi", f"Ana ekran (gece) resmi güncellendi: {os.path.basename(file_path)}")
            save_config(config)

    def select_fetih_coords(self):
        messagebox.showinfo("Bilgi", "Fetih koordinatını seçmek için imleci istediğiniz yere getirin ve klavyeden 'f' tuşuna basın.")
        self.root.bind("<KeyRelease-f>", self._capture_fetih_position)     

    def _capture_fetih_position(self, event):
        pos = get_mouse_position()
        self.fetih_x.set(pos.x)
        self.fetih_y.set(pos.y)
        config = load_config()
        config['fetih_x'] = pos.x
        config['fetih_y'] = pos.y
        save_config(config)
        logging.info(f"Fetih koordinatları kaydedildi: ({pos.x}, {pos.y})")
        messagebox.showinfo("Bilgi", f"Fetih koordinatları kaydedildi: X={pos.x}, Y={pos.y}")
        self.root.unbind("<KeyRelease-f>")       

    def select_last_resort_coords(self):
        messagebox.showinfo("Bilgi", "Son çare koordinatını seçmek için imleci istediğiniz yere getirin ve klavyeden 'k' tuşuna basın.")
        self.root.bind("<KeyRelease-k>", self._capture_mouse_position)

    def _capture_mouse_position(self, event):
        pos = get_mouse_position()
        self.last_resort_x.set(pos.x)
        self.last_resort_y.set(pos.y)
        config = load_config()
        config['last_resort_x'] = pos.x
        config['last_resort_y'] = pos.y
        save_config(config)
        logging.info(f"Son çare koordinatları kaydedildi: ({pos.x}, {pos.y})")
        messagebox.showinfo("Bilgi", f"Son çare koordinatları kaydedildi: X={pos.x}, Y={pos.y}")
        self.root.unbind("<KeyRelease-k>")

    def save_settings(self):
        config = load_config()
        for key, var in self.selections.items():
            config[key] = var.get()
        save_config(config)
        logging.info("Ayarlar kaydedildi.")
        messagebox.showinfo("Bilgi", "Ayarlar başarıyla kaydedildi!")

    def load_settings(self):
        config = load_config()
        if config:
            for key, var in self.selections.items():
                if key in config:
                    try:
                        var.set(config[key])
                    except tk.TclError:
                        handle_error_and_notify(f"Ayar yüklenemedi: {key} - {config[key]}", log_level=logging.WARNING, notify_user=False)
            logging.info("Ayarlar yüklendi.")
        else:
            handle_error_and_notify("Yüklenecek ayar bulunamadı.", log_level=logging.INFO, notify_user=False)

    def check_for_updates_on_startup(self):
        self.update_status_label.config(text="Durum: Güncelleme kontrol ediliyor...")
        threading.Thread(target=self._check_for_updates_thread, args=(False,), daemon=True).start()

    def check_for_updates_manual(self):
        self.update_status_label.config(text="Durum: Güncelleme kontrol ediliyor...")
        self.btn_check_update.config(state=tk.DISABLED)
        self.btn_install_update.config(state=tk.DISABLED)
        threading.Thread(target=self._check_for_updates_thread, args=(True,), daemon=True).start()

    def _check_for_updates_thread(self, is_manual):
        response = check_for_updates(__version__)
        if response and response.get('latest_version'):
            latest_version = response.get('latest_version')
            download_url = response.get('download_url')
            release_notes = response.get('release_notes', 'Sürüm notları mevcut değil.')
            self.latest_update_info = {'latest_version': latest_version, 'download_url': download_url}
            self.update_status_label.config(text=f"Yeni sürüm mevcut: v{latest_version}", foreground=self.colors['accent'])
            self.update_info_text.config(state="normal")
            self.update_info_text.delete(1.0, tk.END)
            self.update_info_text.insert(tk.END, f"Sürüm Notları (v{latest_version}):\n\n{release_notes}")
            self.update_info_text.config(state="disabled")
            self.btn_install_update.config(state=tk.NORMAL)
            if is_manual:
                messagebox.showinfo("Güncelleme", f"Yeni sürüm v{latest_version} mevcut.")
            if self._is_version_newer(latest_version, self.last_shown_update_note_version):
                logging.info(f"Yeni sürüm notları gösteriliyor: v{latest_version}")
                UpdateNotesUI(self.root, release_notes, latest_version, self.colors, save_last_shown_update_note_version)
        else:
            self.update_status_label.config(text="Bot güncel.", foreground=self.colors['text'])
            self.update_info_text.config(state="normal")
            self.update_info_text.delete(1.0, tk.END)
            self.update_info_text.insert(tk.END, "Yenilikler:\n- Fetih eklendi. \n- Mesaj kontrolü iyileştirildi.\n- Su Adası görevi eklendi.\nHata Düzeltmeleri:\n- Küçük performans iyileştirmeleri.\n- Tasarım Değişikliği.")
            self.update_info_text.config(state="disabled")
            if is_manual:
                messagebox.showinfo("Güncelleme", "Botunuz güncel.")
        self.btn_check_update.config(state=tk.NORMAL)

    def _is_version_newer(self, new_version, old_version):
        new_parts = list(map(int, new_version.split('.')))
        old_parts = list(map(int, old_version.split('.')))
        return new_parts > old_parts

    def install_update(self):
        if self.latest_update_info:
            if messagebox.askyesno("Güncelleme", f"v{self.latest_update_info['latest_version']} yüklenecek. Bot yeniden başlatılacak. Devam edilsin mi?"):
                self.btn_install_update.config(state=tk.DISABLED)
                self.btn_check_update.config(state=tk.DISABLED)
                self.update_status_label.config(text="Güncelleme indiriliyor...")
                threading.Thread(target=self._perform_update_and_restart, args=(self.latest_update_info['download_url'], self._update_progress_callback), daemon=True).start()

    def _update_progress_callback(self, bytes_downloaded, total_size):
        update_progress_queue.put((bytes_downloaded, total_size))

    def _perform_update_and_restart(self, download_url, progress_callback):
        try:
            if prepare_update_and_launch_updater(download_url, progress_callback):
                logging.info("Güncelleme hazırlandı ve güncelleyici başlatıldı. Uygulama kapatılıyor...")
                self.root.quit()
            else:
                handle_error_and_notify("Güncelleme hazırlığı sırasında bir hata oluştu.", notify_user=True)
                self.btn_install_update.config(state=tk.NORMAL)
                self.btn_check_update.config(state=tk.NORMAL)
        except Exception as e:
            handle_error_and_notify(f"Güncelleme başlatılırken beklenmeyen hata: {e}", notify_user=True)

    def activate_license_code(self):
        license_code = self.current_license_code.get().strip()
        if not license_code:
            handle_error_and_notify("Lütfen bir lisans kodu girin.", notify_user=True)
            return
        self.activate_license_btn.config(state=tk.DISABLED, text="...")
        threading.Thread(target=self._activate_license_thread, args=(license_code,), daemon=True).start()

    def _activate_license_thread(self, license_code):
        response = activate_license_code(license_code, BOT_API_KEY)
        self.root.after(0, self._process_activation_response, response, license_code)

    # Oyun içi zaman fonksiyonları
    def set_game_time(self):
        try:
            hours = int(self.hour_var.get())
            minutes = int(self.minute_var.get())
            if 0 <= hours <= 23 and 0 <= minutes <= 59:
                self.game_time_hours = hours
                self.game_time_minutes = minutes
                self.update_time_info(f"Oyun saati manuel olarak {hours:02d}:{minutes:02d} olarak ayarlandı.")
                logging.info(f"Oyun saati manuel olarak {hours:02d}:{minutes:02d} olarak ayarlandı.")
            else:
                messagebox.showerror("Hata", "Geçersiz saat veya dakika değeri!")
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
    
    def detect_game_time(self):
        if not self.game_area:
            messagebox.showerror("Hata", "Lütfen önce oyun alanını seçin!")
            return
        
        # OCR kütüphanesi kullanarak ekrandan saat okuma denemeleri
        try:
            import pytesseract
            from PIL import Image
            
            # Oyun alanından screenshot al
            x1, y1, x2, y2 = self.game_area
            screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
            
            # Saatin olabileceği bölgeleri dene (genelde üst kısımda)
            width, height = screenshot.size
            time_regions = [
                (int(width*0.8), 0, width, int(height*0.1)),  # Sağ üst
                (int(width*0.4), 0, int(width*0.6), int(height*0.1)),  # Orta üst
                (0, 0, int(width*0.2), int(height*0.1)),  # Sol üst
            ]
            
            for region in time_regions:
                time_crop = screenshot.crop(region)
                # Kontrastı artır
                time_crop = time_crop.convert('L')  # Gri tonlama
                
                # OCR ile metni oku
                text = pytesseract.image_to_string(time_crop, config='--psm 8 -c tessedit_char_whitelist=0123456789:')
                
                # Saat formatını ara (HH:MM)
                import re
                time_match = re.search(r'(\d{1,2}):(\d{2})', text)
                if time_match:
                    hours = int(time_match.group(1))
                    minutes = int(time_match.group(2))
                    if 0 <= hours <= 23 and 0 <= minutes <= 59:
                        self.game_time_hours = hours
                        self.game_time_minutes = minutes
                        self.update_time_info(f"Oyun saati otomatik olarak {hours:02d}:{minutes:02d} olarak algılandı.")
                        logging.info(f"Oyun saati otomatik olarak {hours:02d}:{minutes:02d} olarak algılandı.")
                        return
            
            self.update_time_info("Oyun saati otomatik olarak algılanamadı. Manuel olarak ayarlayın.")
            messagebox.showwarning("Uyarı", "Oyun saati otomatik olarak algılanamadı. Manuel olarak ayarlayın.")
            
        except ImportError:
            messagebox.showerror("Hata", "OCR kütüphanesi bulunamadı. Manuel olarak saat ayarlayın.")
            self.update_time_info("OCR kütüphanesi bulunamadı. Zaman okuma özelliği çalışmıyor.")
        except Exception as e:
            logging.error(f"Zaman algılama hatası: {e}")
            self.update_time_info(f"Zaman algılama hatası: {e}")
    
    def start_time_detection(self):
        if self.time_detection_active:
            messagebox.showinfo("Bilgi", "Otomatik zaman algılama zaten aktif!")
            return
        
        self.time_detection_active = True
        self.time_detection_thread = threading.Thread(target=self._time_detection_loop, daemon=True)
        self.time_detection_thread.start()
        self.update_time_info("Otomatik zaman algılama başlatıldı. Her 5 dakikada bir oyun saati okunacak.")
        logging.info("Otomatik zaman algılama başlatıldı.")
    
    def stop_time_detection(self):
        self.time_detection_active = False
        self.update_time_info("Otomatik zaman algılama durduruldu.")
        logging.info("Otomatik zaman algılama durduruldu.")
    
    def _time_detection_loop(self):
        while self.time_detection_active:
            self.detect_game_time()
            # 5 dakika bekle
            for _ in range(300):  # 300 saniye = 5 dakika
                if not self.time_detection_active:
                    break
                time.sleep(1)
    
    def update_time_info(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.time_info_text.config(state="normal")
        self.time_info_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.time_info_text.config(state="disabled")
        self.time_info_text.see(tk.END)
    
    def update_game_time_display(self):
        # Oyun saatini göster
        game_time_str = f"{self.game_time_hours:02d}:{self.game_time_minutes:02d}"
        self.current_time_label.config(text=f"Mevcut Oyun Saati: {game_time_str}")
        self.game_time_label.config(text=f"Oyun Saati: {game_time_str}")
        
        # Her dakika oyun saatini bir dakika ilerlet (gerçek zamanda 1 saniye = oyun zamanında 1 dakika değil, bu örnek)
        # Gerçek oyun zaman akışına göre ayarlanabilir
        
        self.root.after(60000, self.update_game_time_display)  # Her dakika güncelle
    
    def _process_activation_response(self, response, license_code):
        if response and response.get('status') == 'success' and 'expiration_date' in response:
            try:
                exp_dt = datetime.datetime.strptime(response['expiration_date'], '%Y-%m-%d %H:%M:%S')
                self.expiration_timestamp = exp_dt.timestamp()
                self.license_active = self.expiration_timestamp > time.time()
                
                user_data = load_user_data()
                user_data['license_code'] = license_code
                user_data['expiration_date'] = response['expiration_date']
                save_user_data(user_data)
                
                messagebox.showinfo("Lisans Başarılı", f"Lisans başarıyla aktive edildi. Bitiş: {response['expiration_date']}")
                self.update_license_status()

            except ValueError:
                handle_error_and_notify("Sunucudan geçersiz tarih formatı alındı.", notify_user=True, contact_discord=True, contact_telegram=True)
                self.license_active = False
            except Exception as e:
                handle_error_and_notify(f"Beklenmeyen bir hata oluştu: {e}", notify_user=True, contact_discord=True, contact_telegram=True)
                self.license_active = False
        else:
            error_message = response.get('message', 'Bilinmeyen bir hata oluştu. Lütfen tekrar deneyin.')
            handle_error_and_notify(error_message, notify_user=True, contact_discord=True, contact_telegram=True)
            self.license_active = False
        
        self.activate_license_btn.config(state=tk.NORMAL, text="Aktive Et")
        self.update_license_status()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    selector_dialog = ResolutionSelector(tk.Toplevel(root))
    root.wait_window(selector_dialog.master)
    selected_res = selector_dialog.selected_resolution
    if selected_res:
        root.deiconify()
        app = BotUI(root, selected_res)
        root.mainloop()
    else:
        root.destroy()
        print("Çözünürlük seçilmedi, uygulama kapatılıyor.")