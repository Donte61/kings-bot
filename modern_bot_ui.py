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
    
    def on_enter(self, event):
        self.configure(bg=self.hover_color)
        self.label.configure(bg=self.hover_color)
    
    def on_leave(self, event):
        self.configure(bg=self.bg_color)
        self.label.configure(bg=self.bg_color)
    
    def on_click(self, event):
        if self.command:
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
            'warning': '#f39c12',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'background': '#ffffff',
            'sidebar': '#2c3e50',
            'text': '#2c3e50',
            'text_light': '#6c757d'
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
        self.log_handler = TkinterLogHandler(log_queue)
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
        TipsUI(self.root)
        
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
                messagebox.showinfo("Başarılı", "Loglar kaydedildi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Log kaydetme hatası: {e}")

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
