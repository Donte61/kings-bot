#!/usr/bin/env python3
"""
King Bot Pro v2.0.0 - Modern Edition
Başlangıç scripti - Emülatör desteği ve modern GUI ile
"""

import sys
import os
import logging
import traceback
import tkinter as tk
from tkinter import messagebox
import threading
import time

# Kendi modüllerimizi import et
try:
    from version import __version__
    from emulator_manager import EmulatorManager
    from modern_bot_ui import ModernBotUI
    from enhanced_utils import optimize_system_for_bot, get_system_info, handle_error_and_notify
    from license_ui import LicenseUI
    from win_optimizer_advanced import WinOptimizerApp
except ImportError as e:
    print(f"Modül import hatası: {e}")
    sys.exit(1)

class BotApplication:
    """Ana bot uygulaması"""
    
    def __init__(self):
        self.root = None
        self.app = None
        self.emulator_manager = None
        
    def setup_logging(self):
        """Logging sistemini kur"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler('king_bot_pro.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Startup log
        logging.info(f"King Bot Pro v{__version__} başlatılıyor...")
        logging.info(f"Python {sys.version}")
        logging.info(f"Platform: {sys.platform}")
        
    def check_requirements(self):
        """Gerekli kütüphaneleri kontrol et"""
        required_modules = [
            'tkinter', 'PIL', 'pyautogui', 'opencv-python', 
            'numpy', 'psutil', 'requests'
        ]
        
        missing_modules = []
        
        for module in required_modules:
            try:
                if module == 'opencv-python':
                    import cv2
                elif module == 'PIL':
                    from PIL import Image
                else:
                    __import__(module)
            except ImportError:
                missing_modules.append(module)
                
        if missing_modules:
            error_msg = f"Eksik kütüphaneler: {', '.join(missing_modules)}\n"
            error_msg += "Lütfen şu komutu çalıştırın: pip install " + " ".join(missing_modules)
            logging.error(error_msg)
            messagebox.showerror("Eksik Kütüphaneler", error_msg)
            return False
            
        return True
        
    def show_splash_screen(self):
        """Splash screen göster"""
        splash = tk.Toplevel()
        splash.title("King Bot Pro")
        splash.geometry("400x300")
        splash.resizable(False, False)
        splash.configure(bg="#2c3e50")
        
        # Center the splash screen
        splash.update_idletasks()
        x = (splash.winfo_screenwidth() // 2) - (400 // 2)
        y = (splash.winfo_screenheight() // 2) - (300 // 2)
        splash.geometry(f"400x300+{x}+{y}")
        
        # Logo placeholder
        logo_frame = tk.Frame(splash, bg="#2c3e50")
        logo_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Title
        title_label = tk.Label(logo_frame, 
                              text="King Bot Pro", 
                              font=("Segoe UI", 24, "bold"),
                              fg="#3498db",
                              bg="#2c3e50")
        title_label.pack(pady=20)
        
        # Version
        version_label = tk.Label(logo_frame,
                                text=f"v{__version__} - Modern Edition",
                                font=("Segoe UI", 12),
                                fg="#ecf0f1",
                                bg="#2c3e50")
        version_label.pack()
        
        # Loading text
        loading_label = tk.Label(logo_frame,
                                text="Yükleniyor...",
                                font=("Segoe UI", 10),
                                fg="#bdc3c7",
                                bg="#2c3e50")
        loading_label.pack(pady=20)
        
        # Progress bar simulation
        progress_frame = tk.Frame(logo_frame, bg="#2c3e50")
        progress_frame.pack(fill="x", pady=10)
        
        progress_canvas = tk.Canvas(progress_frame, height=4, bg="#34495e", highlightthickness=0)
        progress_canvas.pack(fill="x")
        
        # Animate progress
        def animate_progress():
            for i in range(101):
                try:
                    width = progress_canvas.winfo_width()
                    fill_width = (width * i) / 100
                    progress_canvas.delete("all")
                    progress_canvas.create_rectangle(0, 0, fill_width, 4, fill="#3498db", outline="")
                    splash.update()
                    time.sleep(0.02)
                except:
                    break
                    
        # Start animation in main thread using after method
        def update_progress(i=0):
            if i <= 100:
                try:
                    width = progress_canvas.winfo_width()
                    fill_width = (width * i) / 100
                    progress_canvas.delete("all")
                    progress_canvas.create_rectangle(0, 0, fill_width, 4, fill="#3498db", outline="")
                    splash.after(20, lambda: update_progress(i + 1))
                except:
                    pass
                    
        splash.after(100, update_progress)
        
        return splash
        
    def initialize_components(self):
        """Bileşenleri başlat"""
        try:
            # Sistem optimizasyonu
            logging.info("Sistem optimizasyonu yapılıyor...")
            optimize_system_for_bot()
            
            # Sistem bilgilerini logla
            system_info = get_system_info()
            logging.info(f"Sistem Bilgileri: {system_info}")
            
            # Emülatör yöneticisini başlat
            logging.info("Emülatör yöneticisi başlatılıyor...")
            self.emulator_manager = EmulatorManager()
            
            # Emülatörleri otomatik algıla
            detected = self.emulator_manager.auto_detect_emulators()
            if detected:
                logging.info(f"Algılanan emülatörler: {list(detected.keys())}")
            else:
                logging.info("Hiç emülatör algılanamadı")
                
            return True
            
        except Exception as e:
            logging.error(f"Bileşen başlatma hatası: {e}")
            handle_error_and_notify(f"Başlatma hatası: {e}", show_popup=True)
            return False
            
    def show_resolution_selector(self):
        """Çözünürlük seçici göster"""
        class ResolutionSelector:
            def __init__(self, master):
                self.master = master
                self.master.title("Ekran Çözünürlüğü Seçimi")
                self.master.geometry("400x250")
                self.master.resizable(False, False)
                self.master.configure(bg="#2c3e50")
                self.master.transient()
                self.master.grab_set()
                
                self.selected_resolution = None
                
                # Center window
                self.master.update_idletasks()
                x = (self.master.winfo_screenwidth() // 2) - (400 // 2)
                y = (self.master.winfo_screenheight() // 2) - (250 // 2)
                self.master.geometry(f"400x250+{x}+{y}")
                
                self.create_widgets()
                
            def create_widgets(self):
                # Title
                title = tk.Label(self.master, 
                               text="Lütfen bir çözünürlük seçin",
                               font=("Segoe UI", 16, "bold"),
                               fg="#ecf0f1",
                               bg="#2c3e50")
                title.pack(pady=20)
                
                # Info
                info = tk.Label(self.master,
                              text="Bu ayar emülatör uyumluluğu için gereklidir",
                              font=("Segoe UI", 10),
                              fg="#bdc3c7",
                              bg="#2c3e50")
                info.pack(pady=10)
                
                # Buttons frame
                btn_frame = tk.Frame(self.master, bg="#2c3e50")
                btn_frame.pack(pady=20)
                
                # Resolution buttons
                resolutions = [
                    ("📱 Mobil (720x1280)", "mobile"),
                    ("💻 Laptop (1366x768)", "laptop"),
                    ("🖥️ Masaüstü (1920x1080)", "desktop"),
                    ("📺 4K (2560x1440)", "4k")
                ]
                
                for text, res_type in resolutions:
                    btn = tk.Button(btn_frame,
                                  text=text,
                                  font=("Segoe UI", 11),
                                  bg="#3498db",
                                  fg="white",
                                  bd=0,
                                  padx=20,
                                  pady=10,
                                  command=lambda r=res_type: self.select_resolution(r))
                    btn.pack(pady=5, fill="x")
                    
                    # Hover effects
                    def on_enter(e, button=btn):
                        button.config(bg="#2980b9")
                    def on_leave(e, button=btn):
                        button.config(bg="#3498db")
                        
                    btn.bind("<Enter>", on_enter)
                    btn.bind("<Leave>", on_leave)
                    
            def select_resolution(self, resolution_type):
                self.selected_resolution = resolution_type
                self.master.destroy()
                
        selector_window = tk.Toplevel(self.root)
        selector = ResolutionSelector(selector_window)
        
        # Wait for selection
        self.root.wait_window(selector_window)
        
        return getattr(selector, 'selected_resolution', 'desktop')
        
    def run(self):
        """Uygulamayı çalıştır"""
        try:
            # Logging setup
            self.setup_logging()
            
            # Requirements check
            if not self.check_requirements():
                return False
                
            # Create root window (hidden initially)
            self.root = tk.Tk()
            self.root.withdraw()  # Hide main window initially
            
            # Show splash screen
            splash = self.show_splash_screen()
            
            # Initialize components
            if not self.initialize_components():
                splash.destroy()
                return False
                
            # Wait a bit for splash effect
            time.sleep(2)
            
            # Destroy splash
            splash.destroy()
            
            # Show resolution selector
            resolution_type = self.show_resolution_selector()
            logging.info(f"Seçilen çözünürlük: {resolution_type}")
            
            # Show main window
            self.root.deiconify()
            
            # Create main application
            logging.info("Ana uygulama penceresi oluşturuluyor...")
            self.app = ModernBotUI(self.root)
            
            # Set window properties based on resolution
            self.configure_window_for_resolution(resolution_type)
            
            logging.info("King Bot Pro başarıyla başlatıldı!")
            
            # Start main loop
            self.root.mainloop()
            
            return True
            
        except KeyboardInterrupt:
            logging.info("Uygulama kullanıcı tarafından sonlandırıldı")
            return True
            
        except Exception as e:
            error_msg = f"Kritik uygulama hatası: {e}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            
            if self.root:
                messagebox.showerror("Kritik Hata", error_msg)
            else:
                print(error_msg)
                
            return False
            
        finally:
            self.cleanup()
            
    def configure_window_for_resolution(self, resolution_type):
        """Çözünürlüğe göre pencere ayarları"""
        configs = {
            'mobile': {'geometry': '800x1000', 'resizable': (True, True)},
            'laptop': {'geometry': '1200x800', 'resizable': (True, True)},
            'desktop': {'geometry': '1400x900', 'resizable': (True, True)},
            '4k': {'geometry': '1600x1000', 'resizable': (True, True)}
        }
        
        config = configs.get(resolution_type, configs['desktop'])
        
        self.root.geometry(config['geometry'])
        self.root.resizable(*config['resizable'])
        
        # Center window
        self.root.update_idletasks()
        width, height = map(int, config['geometry'].split('x'))
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{config['geometry']}+{x}+{y}")
        
    def cleanup(self):
        """Temizlik işlemleri"""
        try:
            logging.info("Uygulama kapatılıyor...")
            
            if self.app:
                # Bot'u durdur
                if hasattr(self.app, 'is_bot_running') and self.app.is_bot_running:
                    self.app.stop_bot()
                    
                # Task manager'ı durdur
                if hasattr(self.app, 'task_manager'):
                    self.app.task_manager.stop()
                    
            logging.info("Temizlik tamamlandı")
            
        except Exception as e:
            logging.error(f"Temizlik hatası: {e}")

def show_optimizer_option():
    """Optimizer seçeneklerini göster"""
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle
    
    result = messagebox.askyesnocancel(
        "King Bot Pro Başlatma",
        "King Bot Pro'yu nasıl başlatmak istiyorsunuz?\n\n"
        "• EVET: Önce Windows Optimizer'ı aç\n"
        "• HAYIR: Doğrudan botu başlat\n"
        "• İPTAL: Çıkış yap",
        icon="question"
    )
    
    root.destroy()
    return result

def main():
    """Ana fonksiyon"""
    try:
        # Optimizer seçeneği
        choice = show_optimizer_option()
        
        if choice is None:  # Cancel
            return 0
        elif choice:  # Yes - Open optimizer first
            try:
                optimizer_root = tk.Tk()
                optimizer_app = WinOptimizerApp(optimizer_root)
                
                # Optimizer tamamlandığında bot'u başlat
                def on_optimizer_close():
                    optimizer_root.destroy()
                    
                    # Bot'u başlat
                    bot_app = BotApplication()
                    bot_app.run()
                    
                optimizer_root.protocol("WM_DELETE_WINDOW", on_optimizer_close)
                optimizer_root.mainloop()
                
            except Exception as e:
                logging.error(f"Optimizer hatası: {e}")
                # Optimizer başarısızsa direkt bot'u başlat
                bot_app = BotApplication()
                return 0 if bot_app.run() else 1
                
        else:  # No - Direct bot start
            bot_app = BotApplication()
            return 0 if bot_app.run() else 1
            
    except Exception as e:
        print(f"Başlatma hatası: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
