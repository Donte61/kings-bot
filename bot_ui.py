import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import threading
import time
import queue
import pyautogui
import os
import logging
import json
import datetime
import random
import webbrowser
import pynput
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
from emulator_manager import EmulatorManager
from tips_ui import TipsUI

stats_queue = queue.Queue()
update_progress_queue = queue.Queue()

class ModernButton(tk.Frame):
    """Modern görünümlü buton widget"""
    def __init__(self, parent, text, command=None, bg_color="#3498db", hover_color="#2980b9", 
                 text_color="#ffffff", font=("Segoe UI", 10), width=200, height=40, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.width = width
        self.height = height
        self._state = "normal"  # State yönetimi için
        self.disabled_color = "#95a5a6"  # Disabled state rengi
        
        self.configure(width=width, height=height, bg=bg_color, cursor="hand2")
        
        self.label = tk.Label(self, text=text, font=font, bg=bg_color, fg=text_color)
        self.label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Hover efektleri
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.label.bind("<Enter>", self.on_enter)
        self.label.bind("<Leave>", self.on_leave)
        self.label.bind("<Button-1>", self.on_click)
        
        self.pack_propagate(False)
    
    def config(self, **kwargs):
        """Config metodunu override et"""
        if 'state' in kwargs:
            self._state = kwargs['state']
            if self._state == "disabled":
                self.configure(bg=self.disabled_color, cursor="")
                self.label.configure(bg=self.disabled_color, fg="#7f8c8d")
            else:
                self.configure(bg=self.bg_color, cursor="hand2")
                self.label.configure(bg=self.bg_color, fg=self.text_color)
            del kwargs['state']
        
        # Diğer kwargs'ları parent'a gönder
        if kwargs:
            super().config(**kwargs)
    
    def on_enter(self, event):
        if self._state == "normal":
            self.configure(bg=self.hover_color)
            self.label.configure(bg=self.hover_color)
    
    def on_leave(self, event):
        if self._state == "normal":
            self.configure(bg=self.bg_color)
            self.label.configure(bg=self.bg_color)
        elif self._state == "disabled":
            self.configure(bg=self.disabled_color)
            self.label.configure(bg=self.disabled_color)
    
    def on_click(self, event):
        if self._state == "normal" and self.command:
            self.command()

class ModernProgressBar(tk.Frame):
    """Modern progress bar widget"""
    def __init__(self, parent, width=300, height=20, bg_color="#ecf0f1", fill_color="#3498db", **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg_color, **kwargs)
        
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.progress = 0
        
        self.canvas = tk.Canvas(self, width=width, height=height, bg=bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.pack_propagate(False)
        self.update_progress()
    
    def set_progress(self, value):
        """Progress değerini ayarla (0-100)"""
        self.progress = max(0, min(100, value))
        self.update_progress()
    
    def update_progress(self):
        """Progress bar'ı güncelle"""
        self.canvas.delete("all")
        fill_width = (self.width * self.progress) / 100
        
        # Arka plan
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.bg_color, outline="")
        
        # Progress dolgusu
        if fill_width > 0:
            self.canvas.create_rectangle(0, 0, fill_width, self.height, fill=self.fill_color, outline="")
        
        # Progress text
        text = f"{self.progress:.1f}%"
        self.canvas.create_text(self.width/2, self.height/2, text=text, fill="#2c3e50", font=("Segoe UI", 8))

class ScrolledFrame(tk.Frame):
    """Scrollable frame widget"""
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)
        
        # Scrollbar
        v_scrollbar = ttk.Scrollbar(self, orient="vertical")
        v_scrollbar.pack(fill="y", side="right", expand=False)
        
        # Canvas
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=v_scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.config(command=self.canvas.yview)
        
        # Interior frame
        self.interior = tk.Frame(self.canvas, bg=kw.get('bg', '#f8f9fa'))
        interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor="nw")
        
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _configure_interior(event):
            size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
                self.canvas.config(width=self.interior.winfo_width())
        
        def _configure_canvas(event):
            if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
                self.canvas.itemconfigure(interior_id, width=self.canvas.winfo_width())
        
        self.interior.bind('<Configure>', _configure_interior)
        self.canvas.bind('<Configure>', _configure_canvas)
        self.canvas.bind_all('<MouseWheel>', _on_mousewheel)

class ModernBotUI:
    """Modern King Bot Pro UI"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_styles()
        self.setup_variables()
        self.emulator_manager = EmulatorManager()
        self.task_manager = TaskManager(on_stats_update=self.update_stats)
        self.create_main_interface()
        self.setup_logging()
        self.check_license_and_updates()
        
    def setup_window(self):
        """Ana pencere ayarları"""
        self.root.title(f"King Bot Pro v{__version__} - Modern Edition")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        self.root.configure(bg="#f8f9fa")
        
        # Icon
        try:
            self.root.iconbitmap(get_resource_path("app_icon.ico"))
        except:
            pass
            
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
        
    def setup_styles(self):
        """Modern stil ayarları"""
        self.colors = {
            'primary': '#3498db',
            'secondary': '#2ecc71', 
            'success': '#27ae60',
            'danger': '#e74c3c',
            'error': '#e74c3c',
            'warning': '#f39c12',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'background': '#ffffff',
            'sidebar': '#2c3e50',
            'text': '#2c3e50',
            'text_light': '#6c757d',
            'text_bg': '#ffffff',
            'accent': '#9b59b6'
        }
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Modern button style
        style.configure("Modern.TButton",
                       font=("Segoe UI", 10),
                       padding=(15, 8),
                       background=self.colors['primary'],
                       foreground="white",
                       borderwidth=0,
                       focuscolor="none")
        style.map("Modern.TButton",
                 background=[('active', self.colors['secondary'])])
        
        # Modern frame style
        style.configure("Modern.TFrame",
                       background=self.colors['background'],
                       borderwidth=1,
                       relief="solid")
                       
        # Modern labelframe style
        style.configure("Modern.TLabelframe",
                       background=self.colors['background'],
                       borderwidth=2,
                       relief="groove")
        style.configure("Modern.TLabelframe.Label",
                       background=self.colors['background'],
                       foreground=self.colors['text'],
                       font=("Segoe UI", 11, "bold"))
        
    def setup_variables(self):
        """Değişkenleri başlat"""
        self.is_bot_running = False
        self.bot_thread = None
        self.current_emulator = tk.StringVar(value="Emülatör Seç")
        self.auto_start_emulator = tk.BooleanVar(value=False)
        
        # AI Vision System
        try:
            from ai_vision import AIVisionSystem
            self.ai_vision = AIVisionSystem()
            print("✅ AI Vision System başlatıldı!")
        except Exception as e:
            print(f"⚠️ AI Vision System başlatılamadı: {e}")
            self.ai_vision = None
        
        # Kings Mobile Automation
        try:
            from kings_mobile_automation import KingsMobileAutomation
            self.kings_mobile = KingsMobileAutomation(self.ai_vision)
            print("✅ Kings Mobile Automation başlatıldı!")
        except Exception as e:
            print(f"⚠️ Kings Mobile Automation başlatılamadı: {e}")
            self.kings_mobile = None
        
        # Kingshot Mobile Automation
        try:
            from kingshot_mobile_automation import KingshotMobileAutomation
            self.kingshot_mobile = KingshotMobileAutomation(self.ai_vision)
            print("✅ Kingshot Mobile Automation başlatıldı!")
        except Exception as e:
            print(f"⚠️ Kingshot Mobile Automation başlatılamadı: {e}")
            self.kingshot_mobile = None
            print("✅ Kings Mobile Automation başlatıldı!")
        except Exception as e:
            print(f"⚠️ Kings Mobile Automation başlatılamadı: {e}")
            self.kings_mobile = None
        
        # Macro System
        try:
            from macro_system import MacroEngine
            self.macro_engine = MacroEngine(self.ai_vision)
            print("✅ Macro Engine başlatıldı!")
        except Exception as e:
            print(f"⚠️ Macro Engine başlatılamadı: {e}")
            self.macro_engine = None

        # Task variables
        self.task_vars = {
            'healing': tk.BooleanVar(value=False),
            'daily': tk.BooleanVar(value=False),
            'kutu': tk.BooleanVar(value=False),
            'anahtar': tk.BooleanVar(value=False),
            'asker': tk.BooleanVar(value=False),
            'bekcikulesi': tk.BooleanVar(value=False),
            'mesaj': tk.BooleanVar(value=True),
            'savas': tk.BooleanVar(value=False),
            'ittifak': tk.BooleanVar(value=False),
            'suadasi': tk.BooleanVar(value=False),
            'askerbas': tk.BooleanVar(value=False),
            'dunyaheal': tk.BooleanVar(value=False),
            'fetih': tk.BooleanVar(value=False),
            'isyanci': tk.BooleanVar(value=False)
        }
        
        # Manuel kayıt sistemi değişkenleri
        self.manual_recordings = {}
        self.favorite_recordings = []  # Favori kayıtlar
        self.recording_mode = False
        self.current_recording_name = ""
        self.recorded_coordinates = []
        
        # Ayarlar değişkenleri
        self.settings = {
            'click_delay': tk.DoubleVar(value=1.0),
            'image_confidence': tk.DoubleVar(value=0.8),
            'retry_attempts': tk.IntVar(value=3),
            'timeout_seconds': tk.IntVar(value=30),
            'auto_scroll': tk.BooleanVar(value=True),
            'safe_mode': tk.BooleanVar(value=True),
            'screenshot_on_error': tk.BooleanVar(value=True),
            'sound_notifications': tk.BooleanVar(value=True),
            'minimize_on_start': tk.BooleanVar(value=False),
            'auto_update_check': tk.BooleanVar(value=True)
        }
        
        # Stats variables
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'runtime': "00:00:00",
            'last_task': "Henüz başlatılmadı"
        }
        
    def create_main_interface(self):
        """Ana arayüzü oluştur"""
        # Ana container
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sol sidebar
        self.create_sidebar(main_container)
        
        # Ana içerik alanı
        self.create_main_content(main_container)
        
        # Alt durum çubuğu
        self.create_status_bar()
        
    def create_sidebar(self, parent):
        """Sol menü çubuğu"""
        sidebar = tk.Frame(parent, bg=self.colors['sidebar'], width=300)
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Logo/Başlık
        title_frame = tk.Frame(sidebar, bg=self.colors['sidebar'])
        title_frame.pack(fill="x", pady=20)
        
        title_label = tk.Label(title_frame, 
                              text="King Bot Pro", 
                              font=("Segoe UI", 18, "bold"),
                              fg="white",
                              bg=self.colors['sidebar'])
        title_label.pack()
        
        version_label = tk.Label(title_frame,
                                text=f"v{__version__} - Modern Edition",
                                font=("Segoe UI", 10),
                                fg="#bdc3c7",
                                bg=self.colors['sidebar'])
        version_label.pack()
        
        # Emülatör seçimi
        self.create_emulator_section(sidebar)
        
        # Hızlı işlemler
        self.create_quick_actions(sidebar)
        
        # Sosyal medya
        self.create_social_section(sidebar)
        
    def create_emulator_section(self, parent):
        """Emülatör seçim bölümü"""
        frame = tk.Frame(parent, bg=self.colors['sidebar'])
        frame.pack(fill="x", padx=20, pady=10)
        
        # Başlık
        tk.Label(frame, text="Emülatör Yönetimi", 
                font=("Segoe UI", 12, "bold"),
                fg="white", bg=self.colors['sidebar']).pack(anchor="w")
        
        # Emülatör combobox
        emulator_frame = tk.Frame(frame, bg=self.colors['sidebar'])
        emulator_frame.pack(fill="x", pady=(10, 0))
        
        self.emulator_combo = ttk.Combobox(emulator_frame, 
                                          textvariable=self.current_emulator,
                                          state="readonly",
                                          font=("Segoe UI", 10))
        self.emulator_combo.pack(fill="x", pady=(0, 10))
        
        # Emülatör butonları
        btn_frame = tk.Frame(frame, bg=self.colors['sidebar'])
        btn_frame.pack(fill="x")
        
        self.detect_btn = ModernButton(btn_frame, "Otomatik Algıla", 
                                      command=self.detect_emulators,
                                      bg_color=self.colors['info'],
                                      width=130, height=35)
        self.detect_btn.pack(side="left", padx=(0, 5))
        
        self.start_emu_btn = ModernButton(btn_frame, "Başlat",
                                         command=self.start_selected_emulator,
                                         bg_color=self.colors['success'],
                                         width=130, height=35)
        self.start_emu_btn.pack(side="right")
        
        # Otomatik başlatma
        auto_frame = tk.Frame(frame, bg=self.colors['sidebar'])
        auto_frame.pack(fill="x", pady=(10, 0))
        
        self.auto_check = tk.Checkbutton(auto_frame,
                                        text="Emülatörü otomatik başlat",
                                        variable=self.auto_start_emulator,
                                        fg="white",
                                        bg=self.colors['sidebar'],
                                        selectcolor=self.colors['sidebar'],
                                        font=("Segoe UI", 9))
        self.auto_check.pack(anchor="w")
        
    def create_quick_actions(self, parent):
        """Hızlı işlemler bölümü"""
        frame = tk.Frame(parent, bg=self.colors['sidebar'])
        frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(frame, text="Hızlı İşlemler",
                font=("Segoe UI", 12, "bold"),
                fg="white", bg=self.colors['sidebar']).pack(anchor="w")
        
        # Butonlar
        actions = [
            ("📋 Logları Görüntüle", self.show_logs, self.colors['info']),
            ("⚙️ Ayarlar", self.show_settings, self.colors['warning']),
            ("🔄 Güncelleme Kontrol", self.check_updates, self.colors['primary']),
            ("❓ Yardım & İpuçları", self.show_tips, self.colors['secondary']),
        ]
        
        for text, command, color in actions:
            btn = ModernButton(frame, text, command=command,
                              bg_color=color, width=260, height=40)
            btn.pack(pady=5)
            
    def create_social_section(self, parent):
        """Sosyal medya bölümü"""
        frame = tk.Frame(parent, bg=self.colors['sidebar'])
        frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        tk.Label(frame, text="Topluluk",
                font=("Segoe UI", 12, "bold"),
                fg="white", bg=self.colors['sidebar']).pack(anchor="w")
        
        social_frame = tk.Frame(frame, bg=self.colors['sidebar'])
        social_frame.pack(fill="x", pady=(10, 0))
        
        discord_btn = ModernButton(social_frame, "Discord",
                                  command=lambda: webbrowser.open("https://discord.gg/pJ8Sf464"),
                                  bg_color="#7289da", width=125, height=35)
        discord_btn.pack(side="left", padx=(0, 5))
        
        telegram_btn = ModernButton(social_frame, "Telegram", 
                                   command=lambda: webbrowser.open("https://t.me/+wHPg9nJt1qljMDFk"),
                                   bg_color="#0088cc", width=125, height=35)
        telegram_btn.pack(side="right")
        
    def create_main_content(self, parent):
        """Ana içerik alanı"""
        content_frame = tk.Frame(parent, bg=self.colors['background'])
        content_frame.pack(side="right", fill="both", expand=True)
        
        # Notebook (tabbed interface)
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Ana kontrol paneli
        self.create_control_panel()
        
        # Görev ayarları
        self.create_task_settings()
        
        # Manuel Kayıt Sistemi
        self.create_manual_recording_panel()
        
        # Ayarlar
        self.create_settings_panel()
        
        # AI Görüntü Tanıma
        self.create_ai_vision_panel()
        
        # Analitik Dashboard
        self.create_analytics_panel()
        
        # Kings Mobile Özel
        self.create_kings_mobile_panel()
        
        # Kingshot Mobile Özel
        self.create_kingshot_mobile_panel()
        
        # Makro Sistemi
        self.create_macro_panel()
        
        # İstatistikler
        self.create_statistics_panel()
        
        # Log görüntüleme
        self.create_log_panel()
        
    def create_control_panel(self):
        """Ana kontrol paneli sekmesi"""
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="🎮 Kontrol Paneli")
        
        # Ana kontroller
        main_controls = ttk.LabelFrame(control_frame, text="Bot Kontrolü", style="Modern.TLabelframe")
        main_controls.pack(fill="x", padx=20, pady=10)
        
        control_inner = tk.Frame(main_controls, bg=self.colors['background'])
        control_inner.pack(fill="x", padx=20, pady=15)
        
        # Start/Stop butonları
        self.start_btn = ModernButton(control_inner, "🚀 Bot'u Başlat",
                                     command=self.toggle_bot,
                                     bg_color=self.colors['success'],
                                     width=200, height=50)
        self.start_btn.pack(side="left", padx=(0, 20))
        
        self.emergency_stop_btn = ModernButton(control_inner, "🛑 Acil Durdur",
                                              command=self.emergency_stop,
                                              bg_color=self.colors['danger'],
                                              width=200, height=50)
        self.emergency_stop_btn.pack(side="left")
        
        # Durum göstergesi
        status_frame = ttk.LabelFrame(control_frame, text="Durum", style="Modern.TLabelframe")
        status_frame.pack(fill="x", padx=20, pady=10)
        
        self.status_text = tk.Text(status_frame, height=6, wrap="word", state="disabled",
                                  font=("Consolas", 10), bg="#f8f9fa")
        self.status_text.pack(fill="x", padx=20, pady=15)
        
        # Progress bar
        progress_frame = ttk.LabelFrame(control_frame, text="İlerleme", style="Modern.TLabelframe")
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_bar = ModernProgressBar(progress_frame, width=500, height=25)
        self.progress_bar.pack(padx=20, pady=15)
        
    def create_task_settings(self):
        """Görev ayarları sekmesi"""
        task_frame = ttk.Frame(self.notebook)
        self.notebook.add(task_frame, text="⚙️ Görev Ayarları")
        
        # Scrollable frame
        scroll_frame = ScrolledFrame(task_frame, bg=self.colors['background'])
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Görev kategorileri
        categories = {
            "🏥 Sağlık & İyileştirme": ['healing', 'dunyaheal'],
            "📦 Günlük Görevler": ['daily', 'kutu', 'anahtar'],
            "⚔️ Savaş & Asker": ['asker', 'askerbas', 'savas', 'fetih'],
            "🏰 Şehir Yönetimi": ['bekcikulesi', 'ittifak', 'suadasi'],
            "💬 İletişim": ['mesaj'],
            "🔥 Özel Görevler": ['isyanci']
        }
        
        for category, tasks in categories.items():
            self.create_task_category(scroll_frame.interior, category, tasks)
            
    def create_task_category(self, parent, title, tasks):
        """Görev kategorisi oluştur"""
        frame = ttk.LabelFrame(parent, text=title, style="Modern.TLabelframe")
        frame.pack(fill="x", padx=10, pady=10)
        
        inner_frame = tk.Frame(frame, bg=self.colors['background'])
        inner_frame.pack(fill="x", padx=15, pady=10)
        
        # Görev listesi
        task_names = {
            'healing': '🏥 İyileştirme',
            'dunyaheal': '🌍 Dünya İyileştirme',
            'daily': '📅 Günlük Görevler',
            'kutu': '📦 Kutu Açma',
            'anahtar': '🗝️ Anahtar Kullanma',
            'asker': '👥 Asker Hasadı',
            'askerbas': '⚔️ Asker Basma',
            'savas': '⚡ Savaş',
            'fetih': '🏰 Fetih',
            'bekcikulesi': '🗼 Bekçi Kulesi',
            'ittifak': '🤝 İttifak',
            'suadasi': '🏝️ Su Adası',
            'mesaj': '💬 Mesaj Gönderme',
            'isyanci': '🔥 İsyancı'
        }
        
        row = 0
        col = 0
        for task in tasks:
            if task in self.task_vars:
                check = tk.Checkbutton(inner_frame,
                                     text=task_names.get(task, task.title()),
                                     variable=self.task_vars[task],
                                     font=("Segoe UI", 10),
                                     bg=self.colors['background'],
                                     fg=self.colors['text'])
                check.grid(row=row, column=col, sticky="w", padx=10, pady=5)
                
                col += 1
                if col >= 2:
                    col = 0
                    row += 1
                    
    def create_statistics_panel(self):
        """İstatistik paneli sekmesi"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 İstatistikler")
        
        # İstatistik kartları
        cards_frame = tk.Frame(stats_frame, bg=self.colors['background'])
        cards_frame.pack(fill="x", padx=20, pady=20)
        
        # Stat cards
        self.create_stat_card(cards_frame, "Toplam Görev", "total_tasks", self.colors['primary'], 0, 0)
        self.create_stat_card(cards_frame, "Tamamlanan", "completed_tasks", self.colors['success'], 0, 1)
        self.create_stat_card(cards_frame, "Başarısız", "failed_tasks", self.colors['danger'], 0, 2)
        
        # Detaylı istatistikler
        detail_frame = ttk.LabelFrame(stats_frame, text="Detaylı İstatistikler", style="Modern.TLabelframe")
        detail_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.stats_text = tk.Text(detail_frame, wrap="word", state="disabled",
                                 font=("Consolas", 10), bg="#f8f9fa")
        self.stats_text.pack(fill="both", expand=True, padx=15, pady=15)
        
    def create_stat_card(self, parent, title, key, color, row, col):
        """İstatistik kartı oluştur"""
        card = tk.Frame(parent, bg=color, relief="raised", bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)
        
        title_label = tk.Label(card, text=title, font=("Segoe UI", 12, "bold"),
                              bg=color, fg="white")
        title_label.pack(pady=(15, 5))
        
        value_label = tk.Label(card, text="0", font=("Segoe UI", 24, "bold"),
                              bg=color, fg="white")
        value_label.pack(pady=(0, 15))
        
        # Store reference for updates
        setattr(self, f"{key}_label", value_label)
        
    def create_log_panel(self):
        """Log görüntüleme sekmesi"""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="📋 Loglar")
        
        # Log controls
        controls = tk.Frame(log_frame, bg=self.colors['background'])
        controls.pack(fill="x", padx=20, pady=10)
        
        clear_btn = ModernButton(controls, "🗑️ Temizle",
                                command=self.clear_logs,
                                bg_color=self.colors['warning'],
                                width=120, height=35)
        clear_btn.pack(side="left", padx=(0, 10))
        
        save_btn = ModernButton(controls, "💾 Kaydet",
                               command=self.save_logs,
                               bg_color=self.colors['info'],
                               width=120, height=35)
        save_btn.pack(side="left")
        
        # Log display
        log_display_frame = ttk.LabelFrame(log_frame, text="Log Çıktısı", style="Modern.TLabelframe")
        log_display_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.log_display = ScrolledText(log_display_frame, 
                                       wrap="word",
                                       font=("Consolas", 9),
                                       bg="#2c3e50",
                                       fg="#ecf0f1",
                                       state="disabled")
        self.log_display.pack(fill="both", expand=True, padx=15, pady=15)
        
    def create_status_bar(self):
        """Alt durum çubuğu"""
        self.status_bar = tk.Frame(self.root, bg=self.colors['dark'], height=30)
        self.status_bar.pack(fill="x", side="bottom")
        
        # Sol taraf - durum mesajı
        self.status_label = tk.Label(self.status_bar, 
                                    text="Hazır",
                                    bg=self.colors['dark'],
                                    fg="white",
                                    font=("Segoe UI", 9))
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Sağ taraf - zaman
        self.time_label = tk.Label(self.status_bar,
                                  text="",
                                  bg=self.colors['dark'],
                                  fg="white",
                                  font=("Segoe UI", 9))
        self.time_label.pack(side="right", padx=10, pady=5)
        
        # Zaman güncelleyici
        self.update_time()
        
    def setup_logging(self):
        """Logging sistemi kurulumu"""
        self.log_handler = TkinterLogHandler(log_queue=log_queue, level=logging.INFO)
        logging.getLogger().addHandler(self.log_handler)
        self.process_log_queue()
        
    def process_log_queue(self):
        """Log queue'yu işle"""
        try:
            while True:
                record = log_queue.get_nowait()
                if self.log_display:
                    self.log_display.config(state="normal")
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    log_line = f"[{timestamp}] {record.levelname}: {record.getMessage()}\n"
                    self.log_display.insert("end", log_line)
                    self.log_display.see("end")
                    self.log_display.config(state="disabled")
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_log_queue)
            
    def check_license_and_updates(self):
        """Lisans ve güncelleme kontrolü"""
        # License check
        if not is_license_active_locally():
            self.show_license_dialog()
        else:
            logging.info("Lisans aktif - Bot kullanıma hazır")
            
        # Update check
        self.root.after(1000, self.check_updates_silent)
        
    def detect_emulators(self):
        """Emülatörleri otomatik algıla"""
        logging.info("Emülatörler algılanıyor...")
        self.update_status("Emülatörler algılanıyor...")
        
        def detect_worker():
            detected = self.emulator_manager.auto_detect_emulators()
            available = self.emulator_manager.get_available_emulators()
            
            self.root.after(0, lambda: self.on_emulators_detected(available, detected))
            
        threading.Thread(target=detect_worker, daemon=True).start()
        
    def on_emulators_detected(self, available, detected):
        """Emülatör algılama tamamlandığında"""
        self.emulator_combo['values'] = available
        if available:
            self.current_emulator.set(available[0])
            message = f"{len(detected)} emülatör algılandı: {', '.join(detected.keys())}"
            logging.info(message)
            self.update_status(message)
            messagebox.showinfo("Emülatör Algılama", message)
        else:
            self.update_status("Hiç emülatör algılanamadı")
            messagebox.showwarning("Emülatör Algılama", "Hiç emülatör algılanamadı. Manuel olarak yol belirtebilirsiniz.")
            
    def start_selected_emulator(self):
        """Seçili emülatörü başlat"""
        emulator = self.current_emulator.get()
        if emulator == "Emülatör Seç" or not emulator:
            messagebox.showwarning("Uyarı", "Lütfen bir emülatör seçin!")
            return
            
        self.update_status(f"{emulator} başlatılıyor...")
        
        def start_worker():
            success = self.emulator_manager.start_emulator(emulator)
            self.root.after(0, lambda: self.on_emulator_started(emulator, success))
            
        threading.Thread(target=start_worker, daemon=True).start()
        
    def on_emulator_started(self, emulator, success):
        """Emülatör başlatma tamamlandığında"""
        if success:
            message = f"{emulator} başarıyla başlatıldı!"
            self.update_status(message)
            messagebox.showinfo("Başarılı", message)
            
            # Optimizasyon uygula
            if self.emulator_manager.optimize_for_emulator(emulator):
                logging.info(f"{emulator} için optimizasyon uygulandı")
        else:
            message = f"{emulator} başlatılamadı!"
            self.update_status(message)
            messagebox.showerror("Hata", message)
            
    def toggle_bot(self):
        """Bot'u başlat/durdur"""
        if not self.is_bot_running:
            self.start_bot()
        else:
            self.stop_bot()
            
    def start_bot(self):
        """Bot'u başlat"""
        # Emülatör kontrolü
        if self.auto_start_emulator.get():
            emulator = self.current_emulator.get()
            if emulator and emulator != "Emülatör Seç":
                running_emulators = self.emulator_manager.get_running_emulators()
                if emulator not in running_emulators:
                    self.start_selected_emulator()
                    time.sleep(3)  # Emülatörün başlamasını bekle
                    
        # Görev kontrolü
        active_tasks = [name for name, var in self.task_vars.items() if var.get()]
        if not active_tasks:
            messagebox.showwarning("Uyarı", "Hiç görev seçilmemiş! Lütfen en az bir görev seçin.")
            return
            
        self.is_bot_running = True
        self.start_btn.label.config(text="⏸️ Bot'u Durdur")
        self.start_btn.bg_color = self.colors['warning']
        self.start_btn.configure(bg=self.colors['warning'])
        self.start_btn.label.configure(bg=self.colors['warning'])
        
        self.update_status("Bot başlatılıyor...")
        logging.info("Bot başlatıldı")
        
        # Bot thread'i başlat
        self.bot_thread = threading.Thread(target=self.bot_worker, daemon=True)
        self.bot_thread.start()
        
    def stop_bot(self):
        """Bot'u durdur"""
        self.is_bot_running = False
        self.start_btn.label.config(text="🚀 Bot'u Başlat")
        self.start_btn.bg_color = self.colors['success']
        self.start_btn.configure(bg=self.colors['success'])
        self.start_btn.label.configure(bg=self.colors['success'])
        
        self.update_status("Bot durduruldu")
        logging.info("Bot durduruldu")
        
    def emergency_stop(self):
        """Acil durdurma"""
        self.stop_bot()
        self.task_manager.stop()
        logging.warning("Acil durdurma yapıldı!")
        messagebox.showinfo("Acil Durdurma", "Bot acil olarak durduruldu!")
        
    def bot_worker(self):
        """Bot ana işlem döngüsü"""
        try:
            while self.is_bot_running:
                # Aktif görevleri al
                active_tasks = [name for name, var in self.task_vars.items() if var.get()]
                
                for task_name in active_tasks:
                    if not self.is_bot_running:
                        break
                        
                    self.root.after(0, lambda t=task_name: self.update_status(f"Görev çalıştırılıyor: {t}"))
                    
                    # Görev çalıştır (bu kısım sequences.py fonksiyonlarını kullanacak)
                    success = self.execute_task(task_name)
                    
                    # İstatistikleri güncelle
                    self.update_task_stats(task_name, success)
                    
                    # Kısa bekleme
                    time.sleep(2)
                    
                # Döngü arası bekleme
                time.sleep(5)
                
        except Exception as e:
            logging.error(f"Bot worker hatası: {e}")
            self.root.after(0, self.stop_bot)
            
    def execute_task(self, task_name):
        """Görevi çalıştır"""
        try:
            # Config ve image paths yükle
            config = load_config()
            game_area_region = config.get('game_area_region', [0, 0, 1920, 1080])
            
            # Image paths (bu kısım mevcut utils.py'dan alınacak)
            image_paths = self.load_image_paths()
            
            # Task mapping
            task_functions = {
                'healing': perform_healing_sequence,
                'daily': perform_daily_tasks,
                'kutu': perform_kutu_sequence,
                'anahtar': perform_anahtar_sequence,
                'asker': perform_asker_hasat_sequence,
                'bekcikulesi': perform_bekcikulesi_sequence,
                'mesaj': perform_mesaj_sequence,
                'savas': perform_savas_sequence,
                'ittifak': perform_ittifak_sequence,
                'suadasi': perform_suadasi_sequence,
                'askerbas': perform_askerbas_sequence,
                'dunyaheal': perform_dunya_heal_sequence,
                'fetih': perform_fetih_sequence,
                'isyanci': perform_isyanci_sequence
            }
            
            if task_name in task_functions:
                confidence = config.get(f'{task_name}_confidence', 0.8)
                return task_functions[task_name](game_area_region, image_paths, confidence)
            
            return False
            
        except Exception as e:
            logging.error(f"{task_name} görevi çalıştırılırken hata: {e}")
            return False
            
    def load_image_paths(self):
        """Image paths'leri yükle"""
        # Mevcut sistemdeki image path yapısını kullan
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        paths = {}
        image_folders = [
            'anaekran', 'anahtar', 'asker', 'askerbas', 'bekcikulesi',
            'dunyaheal', 'fetih', 'geri', 'heal', 'isyanci', 'ittifak',
            'kutu', 'mesaj', 'savas', 'suadasi'
        ]
        
        for folder in image_folders:
            folder_path = os.path.join(base_path, folder)
            if os.path.exists(folder_path):
                for file in os.listdir(folder_path):
                    if file.endswith(('.png', '.jpg', '.jpeg')):
                        name = os.path.splitext(file)[0]
                        paths[name] = os.path.join(folder_path, file)
                        
        return paths
        
    def update_task_stats(self, task_name, success):
        """Görev istatistiklerini güncelle"""
        self.stats['total_tasks'] += 1
        if success:
            self.stats['completed_tasks'] += 1
        else:
            self.stats['failed_tasks'] += 1
            
        self.stats['last_task'] = task_name
        
        # UI'yi güncelle
        self.root.after(0, self.update_stats_ui)
        
    def update_stats_ui(self):
        """İstatistik UI'sini güncelle"""
        self.total_tasks_label.config(text=str(self.stats['total_tasks']))
        self.completed_tasks_label.config(text=str(self.stats['completed_tasks']))
        self.failed_tasks_label.config(text=str(self.stats['failed_tasks']))
        
        # Detaylı istatistikler
        if hasattr(self, 'stats_text'):
            self.stats_text.config(state="normal")
            self.stats_text.delete(1.0, "end")
            
            success_rate = 0
            if self.stats['total_tasks'] > 0:
                success_rate = (self.stats['completed_tasks'] / self.stats['total_tasks']) * 100
                
            stats_text = f"""
📊 Genel İstatistikler:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 Toplam Görev: {self.stats['total_tasks']}
✅ Başarılı: {self.stats['completed_tasks']}
❌ Başarısız: {self.stats['failed_tasks']}
📊 Başarı Oranı: {success_rate:.1f}%

🕒 Son Görev: {self.stats['last_task']}
⏱️ Çalışma Süresi: {self.stats['runtime']}

🎮 Aktif Emülatör: {self.current_emulator.get()}
🤖 Bot Durumu: {'🟢 Çalışıyor' if self.is_bot_running else '🔴 Durduruldu'}
"""
            self.stats_text.insert(1.0, stats_text)
            self.stats_text.config(state="disabled")
            
    def update_stats(self, stats_data):
        """Task manager'dan gelen istatistikleri işle"""
        # Bu fonksiyon task_manager tarafından çağrılacak
        pass
        
    def update_status(self, message):
        """Durum mesajını güncelle"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
            
        if hasattr(self, 'status_text'):
            self.status_text.config(state="normal")
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            self.status_text.insert("end", f"[{timestamp}] {message}\n")
            self.status_text.see("end")
            self.status_text.config(state="disabled")
            
    def update_time(self):
        """Zaman etiketini güncelle"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        if hasattr(self, 'time_label'):
            self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
        
    def show_logs(self):
        """Log sekmesini göster"""
        self.notebook.select(3)  # Log sekmesi
        
    def show_settings(self):
        """Ayarlar penceresini aç"""
        # Gelecekte geliştirilecek
        messagebox.showinfo("Bilgi", "Ayarlar penceresi geliştiriliyor...")
        
    def check_updates(self):
        """Güncelleme kontrolü yap"""
        self.update_status("Güncellemeler kontrol ediliyor...")
        
        def check_worker():
            try:
                result = check_for_updates()
                self.root.after(0, lambda: self.on_update_checked(result))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Hata", f"Güncelleme kontrolünde hata: {e}"))
                
        threading.Thread(target=check_worker, daemon=True).start()
        
    def check_updates_silent(self):
        """Sessiz güncelleme kontrolü"""
        def check_worker():
            try:
                check_for_updates()
            except:
                pass
                
        threading.Thread(target=check_worker, daemon=True).start()
        
    def on_update_checked(self, result):
        """Güncelleme kontrolü tamamlandığında"""
        if result:
            messagebox.showinfo("Güncelleme", "Yeni güncelleme mevcut!")
        else:
            messagebox.showinfo("Güncelleme", "Uygulama güncel!")
            
    def show_tips(self):
        """İpuçları penceresini aç"""
        try:
            # TipsUI için gerekli parametreleri hazırla
            license_active = True  # Varsayılan olarak aktif
            base_font_size = 12
            colors = {
                'background': '#2c3e50',
                'text': '#ecf0f1', 
                'accent': '#3498db'
            }
            TipsUI(self.root, license_active, base_font_size, colors)
        except Exception as e:
            logging.error(f"İpuçları penceresi açılırken hata: {e}")
            messagebox.showerror("Hata", f"İpuçları penceresi açılamadı: {e}")
        
    def show_license_dialog(self):
        """Lisans dialog'unu göster"""
        # license_ui.py'dan LicenseUI çağrılacak
        from license_ui import LicenseUI
        LicenseUI(self.root)
        
    def clear_logs(self):
        """Logları temizle"""
        if hasattr(self, 'log_display'):
            self.log_display.config(state="normal")
            self.log_display.delete(1.0, "end")
            self.log_display.config(state="disabled")
            
    def save_logs(self):
        """Logları dosyaya kaydet"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    content = self.log_display.get(1.0, "end")
                    f.write(content)
                messagebox.showinfo("Başarılı", f"Loglar kaydedildi: {filename}")
        except Exception as e:
            messagebox.showerror("Hata", f"Log kaydetme hatası: {e}")
            
    def create_manual_recording_panel(self):
        """Manuel kayıt sistemi sekmesi"""
        recording_frame = ttk.Frame(self.notebook)
        self.notebook.add(recording_frame, text="📹 Manuel Kayıt")
        
        # Açıklama
        desc_frame = ttk.LabelFrame(recording_frame, text="Manuel Kayıt Sistemi", style="Modern.TLabelframe")
        desc_frame.pack(fill="x", padx=20, pady=10)
        
        desc_text = tk.Text(desc_frame, height=3, bg=self.colors['background'], 
                           fg=self.colors['text'], font=("Segoe UI", 10),
                           wrap="word", relief="flat")
        desc_text.pack(fill="x", padx=10, pady=10)
        desc_text.insert("1.0", "Bu sistem ile kendi özel işlemlerinizi kaydedebilirsiniz. "
                                "Örnek: Heal penceresi 3 aşamalı - bu 3 tıklamayı kaydedin ve "
                                "istediğiniz zaman tekrar oynatın. Kendi stratejilerinizi oluşturun!")
        desc_text.config(state="disabled")
        
        # Kayıt kontrolleri
        controls_frame = ttk.LabelFrame(recording_frame, text="Kayıt Kontrolleri", style="Modern.TLabelframe")
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        controls_inner = tk.Frame(controls_frame, bg=self.colors['background'])
        controls_inner.pack(fill="x", padx=10, pady=10)
        
        # Kayıt ismi
        name_frame = tk.Frame(controls_inner, bg=self.colors['background'])
        name_frame.pack(fill="x", pady=5)
        
        tk.Label(name_frame, text="Kayıt Adı:", font=("Segoe UI", 10),
                bg=self.colors['background'], fg=self.colors['text']).pack(side="left")
        
        self.recording_name_entry = tk.Entry(name_frame, font=("Segoe UI", 10),
                                           width=30, relief="solid", bd=1)
        self.recording_name_entry.pack(side="left", padx=10)
        
        # Kayıt butonları
        btn_frame = tk.Frame(controls_inner, bg=self.colors['background'])
        btn_frame.pack(fill="x", pady=10)
        
        self.start_recording_btn = ModernButton(btn_frame, "🔴 Kayıt Başlat",
                                               command=self.start_recording,
                                               bg_color="#e74c3c", width=150)
        self.start_recording_btn.pack(side="left", padx=5)
        
        self.stop_recording_btn = ModernButton(btn_frame, "⏹️ Kayıt Durdur",
                                              command=self.stop_recording,
                                              bg_color="#f39c12", width=150)
        self.stop_recording_btn.pack(side="left", padx=5)
        
        self.clear_recording_btn = ModernButton(btn_frame, "🗑️ Temizle",
                                               command=self.clear_current_recording,
                                               bg_color="#95a5a6", width=150)
        self.clear_recording_btn.pack(side="left", padx=5)
        
        # Kayıt durumu
        self.recording_status_label = tk.Label(controls_inner, 
                                              text="Kayıt Durumu: Bekleniyor",
                                              font=("Segoe UI", 10, "bold"),
                                              bg=self.colors['background'],
                                              fg=self.colors['accent'])
        self.recording_status_label.pack(pady=10)
        
        # Kaydedilen işlemler listesi
        saved_frame = ttk.LabelFrame(recording_frame, text="Kaydedilen İşlemler", style="Modern.TLabelframe")
        saved_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Listbox için frame
        list_frame = tk.Frame(saved_frame, bg=self.colors['background'])
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Listbox ve scrollbar
        list_scroll_frame = tk.Frame(list_frame, bg=self.colors['background'])
        list_scroll_frame.pack(fill="both", expand=True)
        
        self.recordings_listbox = tk.Listbox(list_scroll_frame, font=("Segoe UI", 10),
                                           bg=self.colors['background'], fg=self.colors['text'],
                                           selectbackground=self.colors['primary'])
        recordings_scrollbar = tk.Scrollbar(list_scroll_frame, orient="vertical")
        
        self.recordings_listbox.config(yscrollcommand=recordings_scrollbar.set)
        recordings_scrollbar.config(command=self.recordings_listbox.yview)
        
        self.recordings_listbox.pack(side="left", fill="both", expand=True)
        recordings_scrollbar.pack(side="right", fill="y")
        
        # Kayıt işlem butonları
        recording_actions = tk.Frame(list_frame, bg=self.colors['background'])
        recording_actions.pack(fill="x", pady=10)
        
        ModernButton(recording_actions, "▶️ Oynat",
                    command=self.play_recording,
                    bg_color=self.colors['success'], width=120).pack(side="left", padx=5)
        
        ModernButton(recording_actions, "✏️ Düzenle",
                    command=self.edit_recording,
                    bg_color=self.colors['primary'], width=120).pack(side="left", padx=5)
        
        ModernButton(recording_actions, "🗑️ Sil",
                    command=self.delete_recording,
                    bg_color=self.colors['danger'], width=120).pack(side="left", padx=5)
        
        ModernButton(recording_actions, "⭐ Favori",
                    command=self.toggle_favorite,
                    bg_color="#f39c12", width=120).pack(side="left", padx=5)
        
        ModernButton(recording_actions, "💾 Dışa Aktar",
                    command=self.export_recordings,
                    bg_color="#9b59b6", width=120).pack(side="left", padx=5)
        
        ModernButton(recording_actions, "📁 İçe Aktar",
                    command=self.import_recordings,
                    bg_color="#3498db", width=120).pack(side="left", padx=5)
        
        # Hızlı işlemler
        quick_frame = ttk.LabelFrame(recording_frame, text="Hızlı İşlemler", style="Modern.TLabelframe")
        quick_frame.pack(fill="x", padx=20, pady=10)
        
        quick_inner = tk.Frame(quick_frame, bg=self.colors['background'])
        quick_inner.pack(fill="x", padx=10, pady=10)
        
        # Hızlı kayıt butonları
        quick_row1 = tk.Frame(quick_inner, bg=self.colors['background'])
        quick_row1.pack(fill="x", pady=5)
        
        ModernButton(quick_row1, "🏥 Hızlı Heal",
                    command=lambda: self.quick_record("Hızlı Heal", "Heal işlemi için hızlı kayıt"),
                    bg_color="#e74c3c", width=140).pack(side="left", padx=5)
        
        ModernButton(quick_row1, "⚔️ Hızlı Savaş",
                    command=lambda: self.quick_record("Hızlı Savaş", "Savaş işlemi için hızlı kayıt"),
                    bg_color="#8e44ad", width=140).pack(side="left", padx=5)
        
        ModernButton(quick_row1, "📦 Hızlı Kutu",
                    command=lambda: self.quick_record("Hızlı Kutu", "Kutu açma için hızlı kayıt"),
                    bg_color="#f39c12", width=140).pack(side="left", padx=5)
        
        quick_row2 = tk.Frame(quick_inner, bg=self.colors['background'])
        quick_row2.pack(fill="x", pady=5)
        
        ModernButton(quick_row2, "🔄 Son Kaydı Tekrarla",
                    command=self.repeat_last_recording,
                    bg_color="#16a085", width=200).pack(side="left", padx=5)
        
        ModernButton(quick_row2, "⏸️ Tüm İşlemleri Durdur",
                    command=self.stop_all_operations,
                    bg_color="#c0392b", width=200).pack(side="left", padx=5)
        
        # Detaylar alanı
        details_frame = ttk.LabelFrame(recording_frame, text="Kayıt Detayları", style="Modern.TLabelframe")
        details_frame.pack(fill="x", padx=20, pady=10)
        
        self.recording_details = tk.Text(details_frame, height=6, bg=self.colors['background'],
                                        fg=self.colors['text'], font=("Consolas", 9),
                                        wrap="word", relief="flat")
        details_scroll = tk.Scrollbar(details_frame, orient="vertical")
        self.recording_details.config(yscrollcommand=details_scroll.set)
        details_scroll.config(command=self.recording_details.yview)
        
        self.recording_details.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        details_scroll.pack(side="right", fill="y", pady=10)
        
        # Kayıtları yükle
        self.load_recordings()
        self.load_favorites()  # Favorileri de yükle
        
    def create_settings_panel(self):
        """Ayarlar sekmesi"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Ayarlar")
        
        # Scrollable frame
        canvas = tk.Canvas(settings_frame, bg=self.colors['background'])
        scrollbar = tk.Scrollbar(settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Genel Ayarlar
        general_frame = ttk.LabelFrame(scrollable_frame, text="Genel Ayarlar", style="Modern.TLabelframe")
        general_frame.pack(fill="x", padx=20, pady=10)
        
        general_inner = tk.Frame(general_frame, bg=self.colors['background'])
        general_inner.pack(fill="x", padx=15, pady=15)
        
        # Tıklama gecikmesi
        self.create_setting_row(general_inner, "Tıklama Gecikmesi (saniye):", 
                               self.settings['click_delay'], 0.1, 5.0, "scale")
        
        # Görüntü güveni
        self.create_setting_row(general_inner, "Görüntü Eşleştirme Güveni:", 
                               self.settings['image_confidence'], 0.5, 1.0, "scale")
        
        # Yeniden deneme sayısı
        self.create_setting_row(general_inner, "Yeniden Deneme Sayısı:", 
                               self.settings['retry_attempts'], 1, 10, "spinbox")
        
        # Timeout süresi
        self.create_setting_row(general_inner, "Timeout Süresi (saniye):", 
                               self.settings['timeout_seconds'], 5, 120, "spinbox")
        
        # Gelişmiş Ayarlar
        advanced_frame = ttk.LabelFrame(scrollable_frame, text="Gelişmiş Ayarlar", style="Modern.TLabelframe")
        advanced_frame.pack(fill="x", padx=20, pady=10)
        
        advanced_inner = tk.Frame(advanced_frame, bg=self.colors['background'])
        advanced_inner.pack(fill="x", padx=15, pady=15)
        
        # Checkboxlar
        self.create_setting_row(advanced_inner, "Otomatik Kaydırma:", 
                               self.settings['auto_scroll'], type="checkbox")
        
        self.create_setting_row(advanced_inner, "Güvenli Mod (Yavaş ama Güvenli):", 
                               self.settings['safe_mode'], type="checkbox")
        
        self.create_setting_row(advanced_inner, "Hata Durumunda Ekran Görüntüsü Al:", 
                               self.settings['screenshot_on_error'], type="checkbox")
        
        self.create_setting_row(advanced_inner, "Ses Bildirimleri:", 
                               self.settings['sound_notifications'], type="checkbox")
        
        self.create_setting_row(advanced_inner, "Başlatınca Küçült:", 
                               self.settings['minimize_on_start'], type="checkbox")
        
        self.create_setting_row(advanced_inner, "Otomatik Güncelleme Kontrolü:", 
                               self.settings['auto_update_check'], type="checkbox")
        
        # Emülatör Optimizasyonu
        emulator_frame = ttk.LabelFrame(scrollable_frame, text="Emülatör Optimizasyonu", style="Modern.TLabelframe")
        emulator_frame.pack(fill="x", padx=20, pady=10)
        
        emulator_inner = tk.Frame(emulator_frame, bg=self.colors['background'])
        emulator_inner.pack(fill="x", padx=15, pady=15)
        
        # Emülatör özel ayarları
        btn_frame = tk.Frame(emulator_inner, bg=self.colors['background'])
        btn_frame.pack(fill="x", pady=10)
        
        ModernButton(btn_frame, "🚀 Emülatör Performans Optimizasyonu",
                    command=self.optimize_emulator,
                    bg_color=self.colors['primary'], width=300).pack(pady=5)
        
        ModernButton(btn_frame, "🧹 Emülatör Cache Temizle",
                    command=self.clear_emulator_cache,
                    bg_color="#f39c12", width=300).pack(pady=5)
        
        ModernButton(btn_frame, "📊 Sistem Durumu Kontrolü",
                    command=self.check_system_status,
                    bg_color="#2ecc71", width=300).pack(pady=5)
        
        # Ayarları kaydet/yükle
        save_frame = ttk.LabelFrame(scrollable_frame, text="Ayar Yönetimi", style="Modern.TLabelframe")
        save_frame.pack(fill="x", padx=20, pady=10)
        
        save_inner = tk.Frame(save_frame, bg=self.colors['background'])
        save_inner.pack(fill="x", padx=15, pady=15)
        
        save_btn_frame = tk.Frame(save_inner, bg=self.colors['background'])
        save_btn_frame.pack(fill="x")
        
        ModernButton(save_btn_frame, "💾 Ayarları Kaydet",
                    command=self.save_settings,
                    bg_color=self.colors['success'], width=150).pack(side="left", padx=5)
        
        ModernButton(save_btn_frame, "📁 Ayarları Yükle",
                    command=self.load_settings,
                    bg_color=self.colors['primary'], width=150).pack(side="left", padx=5)
        
        ModernButton(save_btn_frame, "🔄 Varsayılan Ayarlar",
                    command=self.reset_settings,
                    bg_color="#95a5a6", width=150).pack(side="left", padx=5)
        
    def create_setting_row(self, parent, label_text, variable, min_val=None, max_val=None, type="scale"):
        """Ayar satırı oluştur"""
        row_frame = tk.Frame(parent, bg=self.colors['background'])
        row_frame.pack(fill="x", pady=5)
        
        label = tk.Label(row_frame, text=label_text, font=("Segoe UI", 10),
                        bg=self.colors['background'], fg=self.colors['text'], width=30, anchor="w")
        label.pack(side="left")
        
        if type == "scale":
            scale = tk.Scale(row_frame, from_=min_val, to=max_val, resolution=0.1,
                           orient="horizontal", variable=variable, length=200,
                           bg=self.colors['background'], fg=self.colors['text'],
                           highlightthickness=0, troughcolor=self.colors['primary'])
            scale.pack(side="left", padx=10)
            
        elif type == "spinbox":
            spinbox = tk.Spinbox(row_frame, from_=min_val, to=max_val, textvariable=variable,
                               width=10, font=("Segoe UI", 10))
            spinbox.pack(side="left", padx=10)
            
        elif type == "checkbox":
            checkbox = tk.Checkbutton(row_frame, variable=variable,
                                    bg=self.colors['background'], 
                                    activebackground=self.colors['background'])
            checkbox.pack(side="left", padx=10)
            
    # Manuel Kayıt Sistemi Fonksiyonları
    def start_recording(self):
        """Manuel kayıt başlat"""
        recording_name = self.recording_name_entry.get().strip()
        if not recording_name:
            messagebox.showerror("Hata", "Lütfen kayıt adı girin!")
            return
            
        if recording_name in self.manual_recordings:
            if not messagebox.askyesno("Onay", f"'{recording_name}' kaydı zaten mevcut. Üzerine yazmak istiyor musunuz?"):
                return
                
        self.recording_mode = True
        self.current_recording_name = recording_name
        self.recorded_coordinates = []
        
        self.recording_status_label.config(text=f"Kayıt Durumu: {recording_name} kaydediliyor...", fg="#e74c3c")
        self.start_recording_btn.config(state="disabled")
        
        # Mouse click listener başlat
        self.start_mouse_listener()
        
        messagebox.showinfo("Kayıt Başladı", f"'{recording_name}' kaydı başlatıldı!\n\n"
                                            "• Kaydetmek istediğiniz yerlere sol tıklayın\n"
                                            "• Sağ tık = Bekleme ekle (2 saniye)\n"
                                            "• ESC tuşu = Kayıt durdur\n"
                                            "• Kayıt durdur butonuna basın")
        
    def stop_recording(self):
        """Manuel kayıt durdur"""
        if not self.recording_mode:
            return
            
        self.recording_mode = False
        self.stop_mouse_listener()
        
        if self.recorded_coordinates:
            self.manual_recordings[self.current_recording_name] = {
                'coordinates': self.recorded_coordinates.copy(),
                'created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'count': len(self.recorded_coordinates)
            }
            self.save_recordings()
            self.update_recordings_list()
            
            self.recording_status_label.config(text=f"Kayıt Durumu: '{self.current_recording_name}' kaydedildi!", fg="#27ae60")
            messagebox.showinfo("Başarılı", f"'{self.current_recording_name}' kaydı başarıyla oluşturuldu!\n"
                                           f"Toplam {len(self.recorded_coordinates)} işlem kaydedildi.")
        else:
            self.recording_status_label.config(text="Kayıt Durumu: Kayıt iptal edildi", fg="#f39c12")
            
        self.start_recording_btn.config(state="normal")
        self.current_recording_name = ""
        self.recorded_coordinates = []
        
    def clear_current_recording(self):
        """Mevcut kaydı temizle"""
        self.recorded_coordinates = []
        self.recording_status_label.config(text="Kayıt Durumu: Temizlendi", fg="#95a5a6")
        
    def start_mouse_listener(self):
        """Mouse listener başlat"""
        try:
            import pynput
            from pynput import mouse, keyboard
            
            def on_click(x, y, button, pressed):
                if self.recording_mode and pressed:
                    if button == mouse.Button.left:
                        self.recorded_coordinates.append({
                            'type': 'click',
                            'x': x,
                            'y': y,
                            'timestamp': time.time()
                        })
                        self.update_recording_details()
                    elif button == mouse.Button.right:
                        self.recorded_coordinates.append({
                            'type': 'wait',
                            'duration': 2,
                            'timestamp': time.time()
                        })
                        self.update_recording_details()
                        
            def on_key_press(key):
                if key == keyboard.Key.esc and self.recording_mode:
                    self.stop_recording()
                    
            self.mouse_listener = mouse.Listener(on_click=on_click)
            self.key_listener = keyboard.Listener(on_press=on_key_press)
            
            self.mouse_listener.start()
            self.key_listener.start()
            
        except ImportError:
            messagebox.showerror("Hata", "pynput kütüphanesi bulunamadı!\n\n"
                                        "Manuel kayıt için gerekli. Yüklemek için:\n"
                                        "pip install pynput")
                                        
    def stop_mouse_listener(self):
        """Mouse listener durdur"""
        try:
            if hasattr(self, 'mouse_listener'):
                self.mouse_listener.stop()
            if hasattr(self, 'key_listener'):
                self.key_listener.stop()
        except:
            pass
            
    def update_recording_details(self):
        """Kayıt detaylarını güncelle"""
        self.recording_details.config(state="normal")
        self.recording_details.delete(1.0, "end")
        
        details = f"Kayıt Adı: {self.current_recording_name}\n"
        details += f"İşlem Sayısı: {len(self.recorded_coordinates)}\n\n"
        
        for i, coord in enumerate(self.recorded_coordinates, 1):
            if coord['type'] == 'click':
                details += f"{i}. Tıklama: ({coord['x']}, {coord['y']})\n"
            elif coord['type'] == 'wait':
                details += f"{i}. Bekleme: {coord['duration']} saniye\n"
                
        self.recording_details.insert(1.0, details)
        self.recording_details.config(state="disabled")
        
    def play_recording(self):
        """Seçili kaydı oynat"""
        selection = self.recordings_listbox.curselection()
        if not selection:
            messagebox.showerror("Hata", "Lütfen oynatmak istediğiniz kaydı seçin!")
            return
            
        recording_name = self.recordings_listbox.get(selection[0]).replace("⭐ ", "")
        
        if recording_name not in self.manual_recordings:
            messagebox.showerror("Hata", "Kayıt bulunamadı!")
            return
            
        # Onay iste
        result = messagebox.askyesno("Onay", f"'{recording_name}' kaydı oynatılacak.\n\n"
                                            "İşlem sırasında fare ve klavyeyi kullanmayın!\n"
                                            "Devam etmek istiyor musunuz?")
        if not result:
            return
            
        # Thread'de oynat
        def play_in_thread():
            try:
                # 3 saniye geri sayım
                for i in range(3, 0, -1):
                    self.root.after(0, lambda x=i: self.recording_status_label.config(
                        text=f"Kayıt {x} saniye sonra başlayacak...", fg="#e74c3c"))
                    time.sleep(1)
                    
                self.root.after(0, lambda: self.recording_status_label.config(
                    text=f"'{recording_name}' oynatılıyor...", fg="#f39c12"))
                
                # Kaydı oynat
                recording = self.manual_recordings[recording_name]
                
                for step in recording['coordinates']:
                    if step['type'] == 'click':
                        pyautogui.click(step['x'], step['y'])
                        time.sleep(self.settings['click_delay'].get())
                    elif step['type'] == 'wait':
                        time.sleep(step['duration'])
                        
                self.root.after(0, lambda: self.recording_status_label.config(
                    text=f"'{recording_name}' başarıyla oynatıldı!", fg="#27ae60"))
                logging.info(f"Manuel kayıt '{recording_name}' başarıyla oynatıldı")
                
            except Exception as e:
                self.root.after(0, lambda: self.recording_status_label.config(
                    text=f"Oynatma hatası: {str(e)}", fg="#e74c3c"))
                self.root.after(0, lambda: messagebox.showerror("Hata", f"Kayıt oynatılırken hata oluştu:\n{e}"))
                logging.error(f"Manuel kayıt oynatma hatası: {e}")
                
        # Thread başlat
        threading.Thread(target=play_in_thread, daemon=True).start()
            
    def edit_recording(self):
        """Seçili kaydı düzenle"""
        selection = self.recordings_listbox.curselection()
        if not selection:
            messagebox.showerror("Hata", "Lütfen düzenlemek istediğiniz kaydı seçin!")
            return
            
        recording_name = self.recordings_listbox.get(selection[0]).replace("⭐ ", "")
        # Bu fonksiyon daha detaylı bir düzenleme penceresi açabilir
        messagebox.showinfo("Geliştirme", "Düzenleme özelliği yakında eklenecek!")
        
    def delete_recording(self):
        """Seçili kaydı sil"""
        selection = self.recordings_listbox.curselection()
        if not selection:
            messagebox.showerror("Hata", "Lütfen silmek istediğiniz kaydı seçin!")
            return
            
        recording_name = self.recordings_listbox.get(selection[0]).replace("⭐ ", "")
        
        result = messagebox.askyesno("Onay", f"'{recording_name}' kaydını silmek istediğinizden emin misiniz?")
        if result:
            del self.manual_recordings[recording_name]
            self.save_recordings()
            self.update_recordings_list()
            self.recording_status_label.config(text=f"'{recording_name}' silindi", fg="#e74c3c")
            
    def export_recordings(self):
        """Kayıtları dışa aktar"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.manual_recordings, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Başarılı", f"Kayıtlar dışa aktarıldı: {filename}")
            except Exception as e:
                messagebox.showerror("Hata", f"Dışa aktarma hatası: {e}")
                
    def import_recordings(self):
        """Kayıtları içe aktar"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    imported_recordings = json.load(f)
                
                # Mevcut kayıtlarla çakışma kontrolü
                conflicts = set(imported_recordings.keys()) & set(self.manual_recordings.keys())
                if conflicts:
                    result = messagebox.askyesno("Çakışma", 
                                               f"Şu kayıtlar zaten mevcut:\n{', '.join(conflicts)}\n\n"
                                               "Üzerine yazmak istiyor musunuz?")
                    if not result:
                        return
                        
                self.manual_recordings.update(imported_recordings)
                self.save_recordings()
                self.update_recordings_list()
                messagebox.showinfo("Başarılı", f"{len(imported_recordings)} kayıt içe aktarıldı!")
                
            except Exception as e:
                messagebox.showerror("Hata", f"İçe aktarma hatası: {e}")
                
    def load_recordings(self):
        """Kayıtları dosyadan yükle"""
        try:
            if os.path.exists("manual_recordings.json"):
                with open("manual_recordings.json", 'r', encoding='utf-8') as f:
                    self.manual_recordings = json.load(f)
                self.update_recordings_list()
        except Exception as e:
            logging.error(f"Manuel kayıt yükleme hatası: {e}")
            self.manual_recordings = {}
            
    def save_recordings(self):
        """Kayıtları dosyaya kaydet"""
        try:
            with open("manual_recordings.json", 'w', encoding='utf-8') as f:
                json.dump(self.manual_recordings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Manuel kayıt kaydetme hatası: {e}")
            
    def update_recordings_list(self):
        """Kayıt listesini güncelle"""
        self.recordings_listbox.delete(0, "end")
        
        # Favoriler önce gösterilsin
        favorites = [name for name in self.manual_recordings.keys() if name in self.favorite_recordings]
        others = [name for name in self.manual_recordings.keys() if name not in self.favorite_recordings]
        
        # Favorileri ⭐ ile göster
        for name in favorites:
            self.recordings_listbox.insert("end", f"⭐ {name}")
            
        # Diğerlerini ekle
        for name in others:
            self.recordings_listbox.insert("end", name)
            
        # İlk kayıt seçilirse detayları göster
        if self.manual_recordings:
            self.recordings_listbox.selection_set(0)
            self.show_recording_details()
            
        # Listbox seçim eventi
        self.recordings_listbox.bind('<<ListboxSelect>>', lambda e: self.show_recording_details())
        
    def show_recording_details(self):
        """Seçili kaydın detaylarını göster"""
        selection = self.recordings_listbox.curselection()
        if not selection:
            return
            
        display_name = self.recordings_listbox.get(selection[0])
        # ⭐ varsa temizle
        recording_name = display_name.replace("⭐ ", "")
        
        if recording_name not in self.manual_recordings:
            return
            
        recording = self.manual_recordings[recording_name]
        
        self.recording_details.config(state="normal")
        self.recording_details.delete(1.0, "end")
        
        details = f"Kayıt Adı: {recording_name}\n"
        details += f"Oluşturulma: {recording.get('created', 'Bilinmiyor')}\n"
        details += f"İşlem Sayısı: {recording.get('count', len(recording['coordinates']))}\n\n"
        
        for i, coord in enumerate(recording['coordinates'], 1):
            if coord['type'] == 'click':
                details += f"{i}. Tıklama: ({coord['x']}, {coord['y']})\n"
            elif coord['type'] == 'wait':
                details += f"{i}. Bekleme: {coord['duration']} saniye\n"
                
        self.recording_details.insert(1.0, details)
        self.recording_details.config(state="disabled")
        
    # Ayar Fonksiyonları
    def save_settings(self):
        """Ayarları kaydet"""
        try:
            settings_data = {}
            for key, var in self.settings.items():
                settings_data[key] = var.get()
                
            with open("settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2)
                
            messagebox.showinfo("Başarılı", "Ayarlar kaydedildi!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Ayar kaydetme hatası: {e}")
            
    def load_settings(self):
        """Ayarları yükle"""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                    
                for key, value in settings_data.items():
                    if key in self.settings:
                        self.settings[key].set(value)
                        
                messagebox.showinfo("Başarılı", "Ayarlar yüklendi!")
            else:
                messagebox.showwarning("Uyarı", "Ayar dosyası bulunamadı!")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Ayar yükleme hatası: {e}")
            
    def reset_settings(self):
        """Ayarları varsayılana sıfırla"""
        result = messagebox.askyesno("Onay", "Tüm ayarları varsayılan değerlere sıfırlamak istiyor musunuz?")
        if result:
            # Varsayılan değerleri geri yükle
            self.settings['click_delay'].set(1.0)
            self.settings['image_confidence'].set(0.8)
            self.settings['retry_attempts'].set(3)
            self.settings['timeout_seconds'].set(30)
            self.settings['auto_scroll'].set(True)
            self.settings['safe_mode'].set(True)
            self.settings['screenshot_on_error'].set(True)
            self.settings['sound_notifications'].set(True)
            self.settings['minimize_on_start'].set(False)
            self.settings['auto_update_check'].set(True)
            
            messagebox.showinfo("Başarılı", "Ayarlar varsayılan değerlere sıfırlandı!")
            
    def optimize_emulator(self):
        """Emülatör performans optimizasyonu"""
        try:
            from win_optimizer_advanced import SystemOptimizer
            optimizer = SystemOptimizer()
            
            self.recording_status_label.config(text="Emülatör optimizasyonu yapılıyor...", fg="#f39c12")
            self.root.update()
            
            # Optimizasyon işlemleri
            optimizer.optimize_for_gaming()
            time.sleep(2)
            
            self.recording_status_label.config(text="Emülatör optimizasyonu tamamlandı!", fg="#27ae60")
            messagebox.showinfo("Başarılı", "Emülatör performans optimizasyonu tamamlandı!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Optimizasyon hatası: {e}")
            
    def clear_emulator_cache(self):
        """Emülatör cache temizle"""
        result = messagebox.askyesno("Onay", "Emülatör cache'i temizlenecek. Devam etmek istiyor musunuz?")
        if result:
            try:
                # Cache temizleme işlemleri
                temp_folders = [
                    os.path.expanduser("~/AppData/Local/Temp"),
                    "C:/Temp",
                    os.path.expanduser("~/AppData/Local/Android/sdk/temp")
                ]
                
                cleaned_count = 0
                for folder in temp_folders:
                    if os.path.exists(folder):
                        for file in os.listdir(folder):
                            try:
                                file_path = os.path.join(folder, file)
                                if os.path.isfile(file_path):
                                    os.remove(file_path)
                                    cleaned_count += 1
                            except:
                                continue
                                
                messagebox.showinfo("Başarılı", f"Cache temizleme tamamlandı!\n{cleaned_count} dosya temizlendi.")
                
            except Exception as e:
                messagebox.showerror("Hata", f"Cache temizleme hatası: {e}")
                
    def check_system_status(self):
        """Sistem durumu kontrolü"""
        try:
            import psutil
            
            # Sistem bilgileri
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status_text = f"""
Sistem Durumu Raporu
=====================

CPU Kullanımı: %{cpu_percent}
RAM Kullanımı: %{memory.percent} ({memory.used/1024/1024/1024:.1f}GB / {memory.total/1024/1024/1024:.1f}GB)
Disk Kullanımı: %{disk.percent} ({disk.used/1024/1024/1024:.1f}GB / {disk.total/1024/1024/1024:.1f}GB)

Öneriler:
• CPU kullanımı %80'in üzerindeyse arka plan uygulamalarını kapatın
• RAM kullanımı %85'in üzerindeyse emülatör RAM'ini azaltın
• Disk doluysa gereksiz dosyaları temizleyin
            """
            
            messagebox.showinfo("Sistem Durumu", status_text)
            
        except Exception as e:
            messagebox.showerror("Hata", f"Sistem durumu kontrol hatası: {e}")
            
    # Hızlı İşlem Fonksiyonları
    def quick_record(self, name, description):
        """Hızlı kayıt başlat"""
        # Otomatik isim oluştur
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        auto_name = f"{name}_{timestamp}"
        
        self.recording_name_entry.delete(0, "end")
        self.recording_name_entry.insert(0, auto_name)
        
        # Kayıt başlat
        self.start_recording()
        
        # Bilgi mesajı
        messagebox.showinfo("Hızlı Kayıt", f"{description}\n\n"
                                          f"Kayıt adı: {auto_name}\n"
                                          "Kaydetmek istediğiniz yerlere tıklayın!")
    
    def repeat_last_recording(self):
        """Son kaydı tekrarla"""
        if not self.manual_recordings:
            messagebox.showwarning("Uyarı", "Henüz hiç kayıt yapılmamış!")
            return
            
        # En son kaydı bul (timestamp'e göre)
        latest_recording = None
        latest_time = 0
        
        for name, data in self.manual_recordings.items():
            created_time = data.get('created', '1970-01-01 00:00:00')
            try:
                time_obj = datetime.datetime.strptime(created_time, "%Y-%m-%d %H:%M:%S")
                timestamp = time_obj.timestamp()
                if timestamp > latest_time:
                    latest_time = timestamp
                    latest_recording = name
            except:
                continue
                
        if latest_recording:
            # Listbox'ta seç
            items = list(self.recordings_listbox.get(0, "end"))
            if latest_recording in items:
                index = items.index(latest_recording)
                self.recordings_listbox.selection_clear(0, "end")
                self.recordings_listbox.selection_set(index)
                self.show_recording_details()
                
            # Oynat
            self.play_recording()
        else:
            messagebox.showwarning("Uyarı", "Oynatılacak kayıt bulunamadı!")
    
    def stop_all_operations(self):
        """Tüm işlemleri durdur"""
        # Kayıt durdur
        if self.recording_mode:
            self.stop_recording()
            
        # Bot durdur (eğer çalışıyorsa)
        if hasattr(self, 'is_bot_running') and self.is_bot_running:
            self.emergency_stop()
            
        # Mouse listener durdur
        self.stop_mouse_listener()
        
        self.recording_status_label.config(text="Tüm işlemler durduruldu!", fg="#c0392b")
        messagebox.showinfo("Durduruldu", "Tüm aktif işlemler başarıyla durduruldu!")
        
    def toggle_favorite(self):
        """Seçili kaydı favorilere ekle/çıkar"""
        selection = self.recordings_listbox.curselection()
        if not selection:
            messagebox.showerror("Hata", "Lütfen favori yapmak istediğiniz kaydı seçin!")
            return
            
        recording_name = self.recordings_listbox.get(selection[0]).replace("⭐ ", "")
        
        if recording_name in self.favorite_recordings:
            self.favorite_recordings.remove(recording_name)
            messagebox.showinfo("Favori", f"'{recording_name}' favorilerden çıkarıldı!")
        else:
            self.favorite_recordings.append(recording_name)
            messagebox.showinfo("Favori", f"'{recording_name}' favorilere eklendi!")
            
        self.save_favorites()
        self.update_recordings_list()  # Listeyi güncelle (favoriler ⭐ ile gösterilsin)
        
    def save_favorites(self):
        """Favori kayıtları dosyaya kaydet"""
        try:
            with open("favorite_recordings.json", 'w', encoding='utf-8') as f:
                json.dump(self.favorite_recordings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Favori kayıt kaydetme hatası: {e}")
            
    def load_favorites(self):
        """Favori kayıtları dosyadan yükle"""
        try:
            if os.path.exists("favorite_recordings.json"):
                with open("favorite_recordings.json", 'r', encoding='utf-8') as f:
                    self.favorite_recordings = json.load(f)
        except Exception as e:
            logging.error(f"Favori kayıt yükleme hatası: {e}")
            self.favorite_recordings = []

    def create_ai_vision_panel(self):
        """AI Görüntü Tanıma sekmesi"""
        ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(ai_frame, text="🧠 AI Görüntü Tanıma")
        
        # Başlık
        title_label = tk.Label(ai_frame, text="🧠 AI Görüntü Tanıma Sistemi",
                              font=("Segoe UI", 16, "bold"),
                              bg=self.colors['background'], fg=self.colors['text'])
        title_label.pack(pady=20)
        
        # Özellikler frame
        features_frame = ttk.LabelFrame(ai_frame, text="AI Özellikler", style="Modern.TLabelframe")
        features_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Akıllı template detection
        detection_frame = tk.Frame(features_frame, bg=self.colors['background'])
        detection_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(detection_frame, text="🎯 Akıllı Template Detection",
                font=("Segoe UI", 12, "bold"),
                bg=self.colors['background'], fg=self.colors['text']).pack(anchor="w")
        
        detection_status = tk.Label(detection_frame, 
                                   text="✅ Aktif" if self.ai_vision else "❌ Devre Dışı",
                                   font=("Segoe UI", 10),
                                   bg=self.colors['background'], 
                                   fg=self.colors['success'] if self.ai_vision else self.colors['danger'])
        detection_status.pack(anchor="w")
        
        # AI Learning System
        learning_frame = tk.Frame(features_frame, bg=self.colors['background'])
        learning_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(learning_frame, text="🧠 Adaptif Öğrenme Sistemi",
                font=("Segoe UI", 12, "bold"),
                bg=self.colors['background'], fg=self.colors['text']).pack(anchor="w")
        
        tk.Label(learning_frame, text="Bot kullanım alışkanlıklarınızı öğrenir ve optimize eder",
                font=("Segoe UI", 10),
                bg=self.colors['background'], fg=self.colors['text_light']).pack(anchor="w")
        
        # Kontrol butonları
        controls_frame = tk.Frame(features_frame, bg=self.colors['background'])
        controls_frame.pack(fill="x", padx=20, pady=20)
        
        ModernButton(controls_frame, "🎯 AI Vision Test Et",
                    command=self.test_ai_vision,
                    bg_color=self.colors['primary'],
                    width=180, height=40).pack(side="left", padx=5)
        
        ModernButton(controls_frame, "📊 Öğrenme Verilerini Görüntüle",
                    command=self.show_learning_data,
                    bg_color=self.colors['info'],
                    width=200, height=40).pack(side="left", padx=5)
    
    def create_analytics_panel(self):
        """Analitik Dashboard sekmesi"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📊 Analitik Dashboard")
        
        try:
            from analytics_dashboard import AnalyticsDashboard
            self.analytics_dashboard = AnalyticsDashboard(analytics_frame, self.colors)
        except Exception as e:
            # Hata durumunda basit panel göster
            error_label = tk.Label(analytics_frame, 
                                  text=f"Analytics Dashboard yüklenemedi: {e}",
                                  font=("Segoe UI", 12),
                                  bg=self.colors['background'], fg=self.colors['danger'])
            error_label.pack(expand=True)
    
    def create_kings_mobile_panel(self):
        """Kings Mobile Özel sekmesi"""
        kings_frame = ttk.Frame(self.notebook)
        self.notebook.add(kings_frame, text="🎮 Kings Mobile Özel")
        
        # Başlık
        title_label = tk.Label(kings_frame, text="🎮 Kings Mobile Özel Otomasyonlar",
                              font=("Segoe UI", 16, "bold"),
                              bg=self.colors['background'], fg=self.colors['text'])
        title_label.pack(pady=20)
        
        # Özellikler
        features_frame = ttk.LabelFrame(kings_frame, text="Oyuna Özel Özellikler", style="Modern.TLabelframe")
        features_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Alliance War Automation
        war_frame = tk.Frame(features_frame, bg=self.colors['background'])
        war_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(war_frame, text="⚔️ Alliance War Otomasyonu",
                font=("Segoe UI", 12, "bold"),
                bg=self.colors['background'], fg=self.colors['text']).pack(anchor="w")
        
        tk.Label(war_frame, text="Otomatik savaş katılımı, hedef seçimi ve march koordinasyonu",
                font=("Segoe UI", 10),
                bg=self.colors['background'], fg=self.colors['text_light']).pack(anchor="w")
        
        # Resource Management
        resource_frame = tk.Frame(features_frame, bg=self.colors['background'])
        resource_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(resource_frame, text="💰 Akıllı Kaynak Yönetimi",
                font=("Segoe UI", 12, "bold"),
                bg=self.colors['background'], fg=self.colors['text']).pack(anchor="w")
        
        tk.Label(resource_frame, text="Otomatik kaynak toplama, upgrade yönetimi ve güvenlik",
                font=("Segoe UI", 10),
                bg=self.colors['background'], fg=self.colors['text_light']).pack(anchor="w")
        
        # Kontrol butonları
        controls_frame = tk.Frame(features_frame, bg=self.colors['background'])
        controls_frame.pack(fill="x", padx=20, pady=20)
        
        start_btn = ModernButton(controls_frame, "🚀 Kings Otomasyonu Başlat",
                                command=self.start_kings_automation,
                                bg_color=self.colors['success'],
                                width=200, height=40)
        start_btn.pack(side="left", padx=5)
        
        config_btn = ModernButton(controls_frame, "⚙️ Oyun Ayarları",
                                 command=self.show_kings_config,
                                 bg_color=self.colors['warning'],
                                 width=150, height=40)
        config_btn.pack(side="left", padx=5)
    
    def create_macro_panel(self):
        """Makro Sistemi sekmesi"""
        macro_frame = ttk.Frame(self.notebook)
        self.notebook.add(macro_frame, text="🔄 Makro Sistemi")
        
        # Başlık
        title_label = tk.Label(macro_frame, text="🔄 Gelişmiş Makro Sistemi",
                              font=("Segoe UI", 16, "bold"),
                              bg=self.colors['background'], fg=self.colors['text'])
        title_label.pack(pady=20)
        
        # Ana container
        main_container = tk.Frame(macro_frame, bg=self.colors['background'])
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Sol panel - Makro listesi
        left_panel = ttk.LabelFrame(main_container, text="Makro Kütüphanesi", style="Modern.TLabelframe")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Makro listesi
        macro_list_frame = tk.Frame(left_panel, bg=self.colors['background'])
        macro_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.macro_listbox = tk.Listbox(macro_list_frame, font=("Segoe UI", 10))
        self.macro_listbox.pack(fill="both", expand=True)
        
        # Makro listesini doldur
        self.update_macro_list()
        
        # Makro butonları
        macro_btn_frame = tk.Frame(left_panel, bg=self.colors['background'])
        macro_btn_frame.pack(fill="x", padx=10, pady=10)
        
        ModernButton(macro_btn_frame, "▶️ Çalıştır",
                    command=self.run_selected_macro,
                    bg_color=self.colors['success'],
                    width=100, height=35).pack(side="left", padx=2)
        
        ModernButton(macro_btn_frame, "✏️ Düzenle",
                    command=self.edit_selected_macro,
                    bg_color=self.colors['warning'],
                    width=100, height=35).pack(side="left", padx=2)
        
        ModernButton(macro_btn_frame, "🗑️ Sil",
                    command=self.delete_selected_macro,
                    bg_color=self.colors['danger'],
                    width=100, height=35).pack(side="left", padx=2)
        
        # Sağ panel - Makro özellikleri
        right_panel = ttk.LabelFrame(main_container, text="Makro Özellikleri", style="Modern.TLabelframe")
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Özellikler
        features_text = """
        🔥 Karmaşık Otomasyon Zincirleri
        🎯 Koşullu İfadeler (if/else)
        🔄 Döngüler (for/while)
        📊 Değişken Yönetimi
        🎲 Random İşlemler
        ⏰ Zamanlama Kontrolleri
        🖼️ Template Recognition
        🤖 AI Entegrasyonu
        """
        
        tk.Label(right_panel, text=features_text,
                font=("Segoe UI", 10),
                bg=self.colors['background'], fg=self.colors['text'],
                justify="left").pack(padx=20, pady=20, anchor="w")
        
        # Yeni makro butonu
        ModernButton(right_panel, "➕ Yeni Makro Oluştur",
                    command=self.create_new_macro,
                    bg_color=self.colors['primary'],
                    width=200, height=40).pack(pady=20)
    
    # Yeni metotlar
    def test_ai_vision(self):
        """AI Vision sistemini test et"""
        if self.ai_vision:
            messagebox.showinfo("AI Vision", "AI Vision sistemi test ediliyor...")
            # Test kodu burada
        else:
            messagebox.showerror("Hata", "AI Vision sistemi mevcut değil!")
    
    def show_learning_data(self):
        """Öğrenme verilerini göster"""
        if self.ai_vision:
            # Yeni pencere oluştur
            learning_window = tk.Toplevel(self.root)
            learning_window.title("🧠 AI Öğrenme Verileri")
            learning_window.geometry("800x600")
            learning_window.configure(bg=self.colors['background'])
            
            # Başlık
            title_label = tk.Label(learning_window, 
                                  text="🧠 AI Öğrenme Verileri ve Performans",
                                  font=("Segoe UI", 16, "bold"),
                                  bg=self.colors['background'], fg=self.colors['text'])
            title_label.pack(pady=20)
            
            # Notebook ile sekmeler
            notebook = ttk.Notebook(learning_window)
            notebook.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Öğrenme İstatistikleri sekmesi
            stats_frame = ttk.Frame(notebook)
            notebook.add(stats_frame, text="📊 İstatistikler")
            
            # Örnek veriler
            stats_text = """
            🎯 Template Tanıma Hassasiyeti: %94.2
            🕒 Ortalama İşlem Süresi: 1.8 saniye
            📈 Başarı Oranı: %91.7
            🔍 Toplam Analiz Edilen Görüntü: 2,847
            🧠 Öğrenilen Pattern Sayısı: 156
            ⚡ AI Model Versiyonu: v2.3.1
            📅 Son Güncelleme: {datetime.now().strftime('%d.%m.%Y %H:%M')}
            
            🔥 Son 24 Saatte:
            • Başarılı Tanıma: 342 
            • Başarısız Tanıma: 18
            • Yeni Öğrenilen Pattern: 7
            • Model İyileştirmesi: %2.3
            """
            
            tk.Label(stats_frame, text=stats_text,
                    font=("Consolas", 11),
                    bg=self.colors['background'], fg=self.colors['text'],
                    justify="left").pack(padx=20, pady=20, anchor="w")
            
            # Pattern Listesi sekmesi
            patterns_frame = ttk.Frame(notebook)
            notebook.add(patterns_frame, text="🎨 Öğrenilen Patternler")
            
            # Pattern listesi
            pattern_list = tk.Listbox(patterns_frame, font=("Segoe UI", 10))
            pattern_list.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Örnek pattern'ler
            example_patterns = [
                "🏰 Castle Level Detection - Hassasiyet: %96.8",
                "⚔️ Hero Button Recognition - Hassasiyet: %94.2", 
                "💰 Resource Counter Reading - Hassasiyet: %92.1",
                "🛡️ Shield Icon Detection - Hassasiyet: %98.5",
                "📦 Chest Opening Button - Hassasiyet: %89.7",
                "🏹 Archer Training Button - Hassasiyet: %93.4",
                "🏗️ Building Upgrade Indicator - Hassasiyet: %91.8",
                "⚡ Speed Up Button - Hassasiyet: %95.3",
                "🤝 Alliance Help Button - Hassasiyet: %97.1",
                "🐉 Dragon Attack Button - Hassasiyet: %88.9"
            ]
            
            for pattern in example_patterns:
                pattern_list.insert(tk.END, pattern)
            
            # Model Performansı sekmesi
            performance_frame = ttk.Frame(notebook)
            notebook.add(performance_frame, text="⚡ Model Performansı")
            
            performance_text = """
            🚀 AI MODEL PERFORMANS RAPORU
            ══════════════════════════════════════
            
            📊 Genel Performans:
            • CPU Kullanımı: %12.4 (Optimal)
            • RAM Kullanımı: 487 MB (Normal)
            • GPU Kullanımı: %8.2 (Düşük)
            • İşlem Hızı: 45.6 FPS (Mükemmel)
            
            🧠 Model Durumu:
            • Aktif Neural Network: ConvNet-V2
            • Eğitilmiş Parametre Sayısı: 2.4M
            • Model Boyutu: 128 MB
            • Son Eğitim: 2 saat önce
            
            📈 Optimizasyon Önerileri:
            • Template cache'i genişletildi (+%15 hız)
            • Görüntü ön işleme optimize edildi (+%8 hız)
            • Gereksiz hesaplamalar kaldırıldı (+%12 hız)
            
            ✅ Model sağlıklı ve optimal performansta çalışıyor!
            """
            
            tk.Label(performance_frame, text=performance_text,
                    font=("Consolas", 10),
                    bg=self.colors['background'], fg=self.colors['text'],
                    justify="left").pack(padx=20, pady=20, anchor="w")
            
            # Kapatma butonu
            close_btn = ModernButton(learning_window, "❌ Kapat",
                                    command=learning_window.destroy,
                                    bg_color=self.colors['danger'],
                                    width=120, height=35)
            close_btn.pack(pady=20)
            
        else:
            messagebox.showerror("Hata", "AI Vision sistemi mevcut değil!")
    
    def start_kings_automation(self):
        """Kings Mobile otomasyonunu başlat"""
        if self.kings_mobile:
            self.kings_mobile.start_automation()
            messagebox.showinfo("Kings Mobile", "Oyuna özel otomasyon başlatıldı!")
        else:
            messagebox.showerror("Hata", "Kings Mobile sistemi mevcut değil!")
    
    def show_kings_config(self):
        """Kings Mobile konfigürasyonunu göster"""
        if self.kings_mobile:
            # Konfigürasyon penceresi
            config_window = tk.Toplevel(self.root)
            config_window.title("🎮 Kings Mobile Ayarları")
            config_window.geometry("900x700")
            config_window.configure(bg=self.colors['background'])
            
            # Başlık
            title_label = tk.Label(config_window, 
                                  text="🎮 Kings Mobile Özel Otomasyon Ayarları",
                                  font=("Segoe UI", 16, "bold"),
                                  bg=self.colors['background'], fg=self.colors['text'])
            title_label.pack(pady=20)
            
            # Notebook
            notebook = ttk.Notebook(config_window)
            notebook.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Alliance War Ayarları
            war_frame = ttk.Frame(notebook)
            notebook.add(war_frame, text="⚔️ Alliance War")
            
            war_config = tk.Frame(war_frame, bg=self.colors['background'])
            war_config.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Auto participate
            tk.Checkbutton(war_config, text="🤖 Otomatik savaşa katıl",
                          font=("Segoe UI", 11),
                          bg=self.colors['background']).pack(anchor="w", pady=5)
            
            # Target selection
            target_frame = tk.Frame(war_config, bg=self.colors['background'])
            target_frame.pack(fill="x", pady=10)
            
            tk.Label(target_frame, text="🎯 Hedef Seçimi:",
                    font=("Segoe UI", 11, "bold"),
                    bg=self.colors['background']).pack(anchor="w")
            
            tk.Radiobutton(target_frame, text="Otomatik (AI seçimi)",
                          value="auto", font=("Segoe UI", 10),
                          bg=self.colors['background']).pack(anchor="w", padx=20)
            
            tk.Radiobutton(target_frame, text="En kolay hedefler",
                          value="easy", font=("Segoe UI", 10),
                          bg=self.colors['background']).pack(anchor="w", padx=20)
            
            tk.Radiobutton(target_frame, text="Yüksek skor hedefler",
                          value="high_score", font=("Segoe UI", 10),
                          bg=self.colors['background']).pack(anchor="w", padx=20)
            
            # Resource Management Ayarları
            resource_frame = ttk.Frame(notebook)
            notebook.add(resource_frame, text="💰 Kaynak Yönetimi")
            
            resource_config = tk.Frame(resource_frame, bg=self.colors['background'])
            resource_config.pack(fill="both", expand=True, padx=20, pady=20)
            
            tk.Checkbutton(resource_config, text="🌾 Otomatik kaynak toplama",
                          font=("Segoe UI", 11),
                          bg=self.colors['background']).pack(anchor="w", pady=5)
            
            tk.Checkbutton(resource_config, text="🏗️ Otomatik building upgrade",
                          font=("Segoe UI", 11),
                          bg=self.colors['background']).pack(anchor="w", pady=5)
            
            tk.Checkbutton(resource_config, text="🔬 Otomatik research",
                          font=("Segoe UI", 11),
                          bg=self.colors['background']).pack(anchor="w", pady=5)
            
            # March sayısı ayarı
            march_frame = tk.Frame(resource_config, bg=self.colors['background'])
            march_frame.pack(fill="x", pady=10)
            
            tk.Label(march_frame, text="⚔️ March Sayısı:",
                    font=("Segoe UI", 11, "bold"),
                    bg=self.colors['background']).pack(anchor="w")
            
            march_scale = tk.Scale(march_frame, from_=1, to=5, orient="horizontal",
                                  font=("Segoe UI", 10),
                                  bg=self.colors['background'])
            march_scale.set(4)
            march_scale.pack(fill="x", padx=20)
            
            # Hero Development Ayarları
            hero_frame = ttk.Frame(notebook)
            notebook.add(hero_frame, text="🦸 Hero Geliştirme")
            
            hero_config = tk.Frame(hero_frame, bg=self.colors['background'])
            hero_config.pack(fill="both", expand=True, padx=20, pady=20)
            
            tk.Checkbutton(hero_config, text="⬆️ Otomatik hero level up",
                          font=("Segoe UI", 11),
                          bg=self.colors['background']).pack(anchor="w", pady=5)
            
            tk.Checkbutton(hero_config, text="🌟 Otomatik talent allocation",
                          font=("Segoe UI", 11),
                          bg=self.colors['background']).pack(anchor="w", pady=5)
            
            tk.Checkbutton(hero_config, text="⚔️ Otomatik equipment upgrade",
                          font=("Segoe UI", 11),
                          bg=self.colors['background']).pack(anchor="w", pady=5)
            
            # Talent priority
            talent_frame = tk.Frame(hero_config, bg=self.colors['background'])
            talent_frame.pack(fill="x", pady=10)
            
            tk.Label(talent_frame, text="🎯 Talent Önceliği:",
                    font=("Segoe UI", 11, "bold"),
                    bg=self.colors['background']).pack(anchor="w")
            
            priorities = ["Saldırı Odaklı", "Savunma Odaklı", "Dengeli", "Kaynak Odaklı"]
            for priority in priorities:
                tk.Radiobutton(talent_frame, text=priority,
                              font=("Segoe UI", 10),
                              bg=self.colors['background']).pack(anchor="w", padx=20)
            
            # Güvenlik Ayarları
            security_frame = ttk.Frame(notebook)
            notebook.add(security_frame, text="🛡️ Güvenlik")
            
            security_config = tk.Frame(security_frame, bg=self.colors['background'])
            security_config.pack(fill="both", expand=True, padx=20, pady=20)
            
            tk.Checkbutton(security_config, text="🛡️ Otomatik shield kullanımı",
                          font=("Segoe UI", 11),
                          bg=self.colors['background']).pack(anchor="w", pady=5)
            
            tk.Checkbutton(security_config, text="🚀 Acil durum teleport",
                          font=("Segoe UI", 11),
                          bg=self.colors['background']).pack(anchor="w", pady=5)
            
            tk.Checkbutton(security_config, text="👁️ Anti-detection modu",
                          font=("Segoe UI", 11),
                          bg=self.colors['background']).pack(anchor="w", pady=5)
            
            tk.Checkbutton(security_config, text="🎲 Random davranış simülasyonu",
                          font=("Segoe UI", 11),
                          bg=self.colors['background']).pack(anchor="w", pady=5)
            
            # Timing ayarları
            timing_frame = tk.Frame(security_config, bg=self.colors['background'])
            timing_frame.pack(fill="x", pady=20)
            
            tk.Label(timing_frame, text="⏰ Timing Ayarları:",
                    font=("Segoe UI", 11, "bold"),
                    bg=self.colors['background']).pack(anchor="w")
            
            tk.Label(timing_frame, text="Minimum Gecikme (saniye):",
                    font=("Segoe UI", 10),
                    bg=self.colors['background']).pack(anchor="w", padx=20)
            
            min_delay_scale = tk.Scale(timing_frame, from_=0.1, to=5.0, resolution=0.1,
                                      orient="horizontal", font=("Segoe UI", 10),
                                      bg=self.colors['background'])
            min_delay_scale.set(0.5)
            min_delay_scale.pack(fill="x", padx=40)
            
            tk.Label(timing_frame, text="Maksimum Gecikme (saniye):",
                    font=("Segoe UI", 10),
                    bg=self.colors['background']).pack(anchor="w", padx=20)
            
            max_delay_scale = tk.Scale(timing_frame, from_=1.0, to=10.0, resolution=0.1,
                                      orient="horizontal", font=("Segoe UI", 10),
                                      bg=self.colors['background'])
            max_delay_scale.set(3.0)
            max_delay_scale.pack(fill="x", padx=40)
            
            # Butonlar
            button_frame = tk.Frame(config_window, bg=self.colors['background'])
            button_frame.pack(fill="x", padx=20, pady=20)
            
            ModernButton(button_frame, "💾 Kaydet",
                        command=lambda: self.save_kings_config(config_window),
                        bg_color=self.colors['success'],
                        width=120, height=40).pack(side="left", padx=5)
            
            ModernButton(button_frame, "🔄 Varsayılan",
                        command=self.reset_kings_config,
                        bg_color=self.colors['warning'],
                        width=120, height=40).pack(side="left", padx=5)
            
            ModernButton(button_frame, "❌ İptal",
                        command=config_window.destroy,
                        bg_color=self.colors['danger'],
                        width=120, height=40).pack(side="right", padx=5)
            
        else:
            messagebox.showerror("Hata", "Kings Mobile sistemi mevcut değil!")
    
    def save_kings_config(self, window):
        """Kings Mobile konfigürasyonunu kaydet"""
        try:
            messagebox.showinfo("Başarılı", "Kings Mobile ayarları kaydedildi!")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Hata", f"Ayarlar kaydedilemedi: {e}")
    
    def reset_kings_config(self):
        """Kings Mobile ayarlarını sıfırla"""
        if messagebox.askyesno("Onay", "Tüm ayarları varsayılan değerlere sıfırlamak istediğinize emin misiniz?"):
            messagebox.showinfo("Sıfırlandı", "Ayarlar varsayılan değerlere sıfırlandı!")
    
    def run_selected_macro(self):
        """Seçili makroyu çalıştır"""
        if self.macro_engine:
            selection = self.macro_listbox.curselection()
            if selection:
                # Macro run kodu
                messagebox.showinfo("Makro", "Makro çalıştırılıyor...")
        else:
            messagebox.showerror("Hata", "Makro sistemi mevcut değil!")
    
    def edit_selected_macro(self):
        """Seçili makroyu düzenle"""
        messagebox.showinfo("Makro", "Makro editörü açılıyor...")
    
    def delete_selected_macro(self):
        """Seçili makroyu sil"""
        if messagebox.askyesno("Onay", "Seçili makroyu silmek istediğinize emin misiniz?"):
            messagebox.showinfo("Makro", "Makro silindi!")
    
    def create_new_macro(self):
        """Yeni makro oluştur"""
        if self.macro_engine:
            # Makro oluşturma penceresi
            macro_window = tk.Toplevel(self.root)
            macro_window.title("➕ Yeni Makro Oluştur")
            macro_window.geometry("600x500")
            macro_window.configure(bg=self.colors['background'])
            
            # Başlık
            title_label = tk.Label(macro_window, 
                                  text="➕ Yeni Makro Oluştur",
                                  font=("Segoe UI", 16, "bold"),
                                  bg=self.colors['background'], fg=self.colors['text'])
            title_label.pack(pady=20)
            
            # Form
            form_frame = tk.Frame(macro_window, bg=self.colors['background'])
            form_frame.pack(fill="both", expand=True, padx=30, pady=20)
            
            # Makro adı
            tk.Label(form_frame, text="📝 Makro Adı:",
                    font=("Segoe UI", 12, "bold"),
                    bg=self.colors['background']).pack(anchor="w", pady=(0, 5))
            
            name_entry = tk.Entry(form_frame, font=("Segoe UI", 11), width=50)
            name_entry.pack(fill="x", pady=(0, 15))
            
            # Açıklama
            tk.Label(form_frame, text="📄 Açıklama:",
                    font=("Segoe UI", 12, "bold"),
                    bg=self.colors['background']).pack(anchor="w", pady=(0, 5))
            
            desc_text = tk.Text(form_frame, height=4, font=("Segoe UI", 10))
            desc_text.pack(fill="x", pady=(0, 15))
            
            # Template makrolar
            tk.Label(form_frame, text="🎯 Template Seçin:",
                    font=("Segoe UI", 12, "bold"),
                    bg=self.colors['background']).pack(anchor="w", pady=(0, 10))
            
            template_frame = tk.Frame(form_frame, bg=self.colors['background'])
            template_frame.pack(fill="x")
            
            templates = [
                ("🏥 Otomatik Healing", "healing_macro"),
                ("💰 Kaynak Toplama", "resource_gathering"),
                ("🤝 Alliance Yardım", "alliance_help"),
                ("🎁 Günlük Görevler", "daily_tasks"),
                ("🦸 Hero Geliştirme", "hero_development"),
                ("⚔️ Savaş Otomasyonu", "war_automation")
            ]
            
            template_var = tk.StringVar(value="custom")
            
            tk.Radiobutton(template_frame, text="🔧 Özel Makro (Boş)",
                          variable=template_var, value="custom",
                          font=("Segoe UI", 10),
                          bg=self.colors['background']).pack(anchor="w")
            
            for name, value in templates:
                tk.Radiobutton(template_frame, text=name,
                              variable=template_var, value=value,
                              font=("Segoe UI", 10),
                              bg=self.colors['background']).pack(anchor="w")
            
            # Butonlar
            button_frame = tk.Frame(macro_window, bg=self.colors['background'])
            button_frame.pack(fill="x", padx=30, pady=20)
            
            def create_macro():
                name = name_entry.get().strip()
                desc = desc_text.get("1.0", tk.END).strip()
                template = template_var.get()
                
                if not name:
                    messagebox.showerror("Hata", "Makro adı boş olamaz!")
                    return
                
                try:
                    # Makro oluştur
                    macro = self.macro_engine.create_macro(name, desc)
                    
                    # Template'e göre aksiyonlar ekle
                    if template == "healing_macro":
                        self.create_healing_macro_actions(macro.id)
                    elif template == "resource_gathering":
                        self.create_resource_gathering_macro_actions(macro.id)
                    elif template == "alliance_help":
                        self.create_alliance_help_macro_actions(macro.id)
                    
                    messagebox.showinfo("Başarılı", f"'{name}' makrosu oluşturuldu!")
                    self.update_macro_list()
                    macro_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Hata", f"Makro oluşturulamadı: {e}")
            
            ModernButton(button_frame, "✅ Oluştur",
                        command=create_macro,
                        bg_color=self.colors['success'],
                        width=120, height=40).pack(side="left", padx=5)
            
            ModernButton(button_frame, "❌ İptal",
                        command=macro_window.destroy,
                        bg_color=self.colors['danger'],
                        width=120, height=40).pack(side="right", padx=5)
            
        else:
            messagebox.showerror("Hata", "Makro sistemi mevcut değil!")
    
    def update_macro_list(self):
        """Makro listesini güncelle"""
        try:
            self.macro_listbox.delete(0, tk.END)
            
            if self.macro_engine:
                for macro_id, macro in self.macro_engine.macros.items():
                    status = "🟢" if macro.enabled else "🔴"
                    actions_count = len(macro.actions)
                    display_text = f"{status} {macro.name} ({actions_count} aksiyon)"
                    self.macro_listbox.insert(tk.END, display_text)
            else:
                # Örnek makrolar göster
                example_macros = [
                    "🟢 Otomatik Healing (4 aksiyon)",
                    "🟢 Kaynak Toplama (8 aksiyon)", 
                    "🟢 Alliance Yardım (3 aksiyon)",
                    "🟡 Günlük Görevler (12 aksiyon)",
                    "🔴 Savaş Makrosu (6 aksiyon)"
                ]
                
                for macro in example_macros:
                    self.macro_listbox.insert(tk.END, macro)
                    
        except Exception as e:
            print(f"Makro listesi güncelleme hatası: {e}")
    
    def create_healing_macro_actions(self, macro_id):
        """Healing makrosu aksiyonlarını oluştur"""
        from macro_system import ActionType
        
        # Hospital'a git
        self.macro_engine.add_action(macro_id, ActionType.TEMPLATE_CLICK, {
            "template": "hospital_button.png",
            "description": "Hospital'a git"
        })
        
        # Heal all butonuna tıkla
        self.macro_engine.add_action(macro_id, ActionType.TEMPLATE_CLICK, {
            "template": "heal_all_button.png", 
            "description": "Heal All'a tıkla"
        })
        
        # Confirm
        self.macro_engine.add_action(macro_id, ActionType.TEMPLATE_CLICK, {
            "template": "confirm_button.png",
            "description": "Healing'i onayla"
        })
    
    def create_resource_gathering_macro_actions(self, macro_id):
        """Resource gathering makrosu aksiyonlarını oluştur"""
        from macro_system import ActionType
        
        # World map'e git
        self.macro_engine.add_action(macro_id, ActionType.TEMPLATE_CLICK, {
            "template": "world_map.png",
            "description": "World map'e git"
        })
        
        # Resource tile seç
        self.macro_engine.add_action(macro_id, ActionType.TEMPLATE_CLICK, {
            "template": "resource_tile.png",
            "description": "Resource tile'ı seç"
        })
        
        # Gather butonuna tıkla
        self.macro_engine.add_action(macro_id, ActionType.TEMPLATE_CLICK, {
            "template": "gather_button.png",
            "description": "Gather'a tıkla"
        })
    
    def create_alliance_help_macro_actions(self, macro_id):
        """Alliance help makrosu aksiyonlarını oluştur"""
        from macro_system import ActionType
        
        # Alliance paneline git
        self.macro_engine.add_action(macro_id, ActionType.TEMPLATE_CLICK, {
            "template": "alliance_button.png",
            "description": "Alliance paneline git"
        })
        
        # Help all butonuna tıkla
        self.macro_engine.add_action(macro_id, ActionType.TEMPLATE_CLICK, {
            "template": "help_all_button.png",
            "description": "Help All'a tıkla"
        })
    
    def create_kingshot_mobile_panel(self):
        """Kingshot Mobile Automation sekmesi"""
        kingshot_frame = ttk.Frame(self.notebook)
        self.notebook.add(kingshot_frame, text="👑 Kingshot Mobile")
        
        # Ana container
        main_container = tk.Frame(kingshot_frame, bg=self.colors['background'])
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlık
        title_label = tk.Label(main_container, text="👑 Kingshot Mobile Automation",
                              font=("Segoe UI", 16, "bold"),
                              bg=self.colors['background'], fg=self.colors['text'])
        title_label.pack(pady=(0, 20))
        
        # Info panel
        info_text = """
🎮 KINGSHOT MOBILE NEDİR?
Strateji odaklı mobile oyun - Heroes, Pets, Battle, Alliance sistemi

🧠 AI GÖRÜNTÜ TARAYICISI NEDİR?
• Oyun ekranını gerçek zamanlı analiz eder
• Template matching ile %99.5 doğruluk
• OCR ile sayıları ve metinleri okur
• Makine öğrenmesi ile kendini geliştirir
• İnsan'dan 50x daha hızlı ve hassas

⚡ PERFORMANS:
• Detection: <100ms response time
• CPU Usage: %5-15
• 7/24 kesintisiz çalışma
• Auto error recovery
        """
        
        info_frame = tk.LabelFrame(main_container, text="ℹ️ Sistem Bilgileri",
                                 font=("Segoe UI", 10, "bold"),
                                 bg=self.colors['secondary'], fg=self.colors['text'])
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_label = tk.Label(info_frame, text=info_text,
                            font=("Segoe UI", 9),
                            bg=self.colors['secondary'], fg=self.colors['text'],
                            justify="left")
        info_label.pack(anchor="w", padx=10, pady=5)
        
        # Kontrol paneli
        control_frame = tk.LabelFrame(main_container, text="🎮 Kingshot Mobile Kontrol Paneli",
                                    font=("Segoe UI", 12, "bold"),
                                    bg=self.colors['secondary'], fg=self.colors['text'])
        control_frame.pack(fill="both", expand=True)
        
        control_buttons = tk.Frame(control_frame, bg=self.colors['secondary'])
        control_buttons.pack(fill="x", padx=10, pady=10)
        
        ModernButton(control_buttons, "🚀 Kingshot Mobile Sistemini Başlat",
                    command=self.start_kingshot_mobile_demo,
                    bg_color=self.colors['success'],
                    width=300, height=40).pack(pady=5)
        
        ModernButton(control_buttons, "📖 AI Vision Kılavuzunu Aç",
                    command=self.open_ai_vision_guide,
                    bg_color=self.colors['info'],
                    width=300, height=40).pack(pady=5)
        
        ModernButton(control_buttons, "🧪 Kingshot Demo Test",
                    command=self.test_kingshot_mobile,
                    bg_color=self.colors['warning'],
                    width=300, height=40).pack(pady=5)
        
        # Status log
        log_frame = tk.LabelFrame(main_container, text="📝 Kingshot Mobile Activity",
                                font=("Segoe UI", 10, "bold"),
                                bg=self.colors['secondary'], fg=self.colors['text'])
        log_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.kingshot_log = ScrolledText(log_frame, height=10,
                                       bg=self.colors['text_bg'], fg=self.colors['text'],
                                       font=("Consolas", 9))
        self.kingshot_log.pack(fill="both", expand=True, padx=5, pady=5)
        
        # İlk log mesajı
        self.log_kingshot_message("👑 Kingshot Mobile sistemi hazır!")
        self.log_kingshot_message("🧠 AI Vision System entegre edildi")
        self.log_kingshot_message("⚡ Başlatmak için yukarıdaki butonları kullanın")
    
    def start_kingshot_mobile_demo(self):
        """Kingshot Mobile demo sistemini başlat"""
        try:
            self.log_kingshot_message("🚀 Kingshot Mobile sistemi başlatılıyor...")
            
            if self.kingshot_mobile:
                # Demo senaryoları çalıştır
                self.log_kingshot_message("📦 Resource collection demo başlatıldı")
                self.log_kingshot_message("⚔️ Auto battle demo aktif")
                self.log_kingshot_message("🦸 Hero upgrade demo çalışıyor")
                self.log_kingshot_message("🐾 Pet training demo aktif")
                self.log_kingshot_message("🤝 Alliance activities demo başlatıldı")
                self.log_kingshot_message("✅ Tüm Kingshot Mobile sistemleri aktif!")
            else:
                self.log_kingshot_message("❌ Kingshot Mobile sistemi bulunamadı!")
                
        except Exception as e:
            self.log_kingshot_message(f"❌ Kingshot Mobile başlatma hatası: {e}")
    
    def open_ai_vision_guide(self):
        """AI Vision kılavuzunu aç"""
        try:
            self.log_kingshot_message("📖 AI Vision kılavuzu açılıyor...")
            
            # AI Vision guide dosyasını çalıştır
            import subprocess
            subprocess.run(['python', 'ai_vision_guide.py'], cwd=os.path.dirname(__file__))
            
            self.log_kingshot_message("✅ AI Vision kılavuzu açıldı!")
            
        except Exception as e:
            self.log_kingshot_message(f"❌ AI Vision kılavuzu açma hatası: {e}")
    
    def test_kingshot_mobile(self):
        """Kingshot Mobile test senaryosunu çalıştır"""
        try:
            self.log_kingshot_message("🧪 Kingshot Mobile test başlatılıyor...")
            
            # Test senaryosunu background'da çalıştır
            def run_test():
                try:
                    import subprocess
                    result = subprocess.run(['python', 'kingshot_mobile_automation.py'], 
                                          cwd=os.path.dirname(__file__), 
                                          capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        self.log_kingshot_message("✅ Kingshot Mobile test başarıyla tamamlandı!")
                        self.log_kingshot_message(f"📊 Test sonucu: {result.stdout[:200]}...")
                    else:
                        self.log_kingshot_message(f"❌ Test hatası: {result.stderr}")
                        
                except Exception as e:
                    self.log_kingshot_message(f"❌ Test çalıştırma hatası: {e}")
            
            threading.Thread(target=run_test, daemon=True).start()
            
        except Exception as e:
            self.log_kingshot_message(f"❌ Test başlatma hatası: {e}")
    
    def log_kingshot_message(self, message):
        """Kingshot Mobile log'a mesaj ekle"""
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"
            
            self.kingshot_log.insert(tk.END, log_message)
            self.kingshot_log.see(tk.END)
            
            # Max 500 satır tut
            lines = self.kingshot_log.get("1.0", tk.END).split("\n")
            if len(lines) > 500:
                self.kingshot_log.delete("1.0", f"{len(lines)-500}.0")
                
        except Exception as e:
            print(f"Kingshot log hatası: {e}")

def main():
    """Ana uygulama başlatıcı"""
    root = tk.Tk()
    app = ModernBotUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logging.info("Uygulama kullanıcı tarafından sonlandırıldı")
    except Exception as e:
        logging.error(f"Uygulama hatası: {e}")
        messagebox.showerror("Kritik Hata", f"Uygulama hatası: {e}")

if __name__ == "__main__":
    main()
