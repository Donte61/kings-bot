import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import winreg
import os
import subprocess
import psutil
import wmi
import time
import ctypes
import sys
import logging
import shutil
import datetime
import json

from utils import get_resource_path

# Configure logging
logging.basicConfig(filename="optimizer.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

class WinOptimizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KingBot Optimizer - Windows & Emülatör")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")
        self.debug_mode = True
        self.operations = []
        self.root.iconbitmap(get_resource_path("app_icon.ico"))

        # Initialize emulator paths
        self.emulator_paths = {
            "BlueStacks": "",
            "LDPlayer": "",
            "Nox": "",
            "MEmu": ""
        }
        self.load_emulator_paths()
        self.disabled_services = []
        self.removed_startup_items = []
        self.original_visual_effects = None
        self.registry_backup_path = None
        self.removed_registry_items = []

        # Style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Arial", 10, "bold"), padding=10, background="#3b3b4b", foreground="#ffffff")
        self.style.configure("TLabel", font=("Arial", 12), background="#1e1e2e", foreground="#ffffff")
        self.style.configure("TNotebook", background="#1e1e2e")
        self.style.configure("TProgressbar", thickness=20, troughcolor="#2e2e3e", background="#00ff88")

        # Main Frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(main_frame, text="KingBot Optimizer: Windows & Emülatör", font=("Arial", 16, "bold")).pack(pady=10)

        # Tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(pady=10, fill="both", expand=True)

        # Windows Optimization Tab
        win_frame = ttk.Frame(notebook)
        notebook.add(win_frame, text="Windows Optimizasyonu")

        # Emulator Optimization Tab
        emu_frame = ttk.Frame(notebook)
        notebook.add(emu_frame, text="Emülatör Optimizasyonu")

        # Emulator Start Tab
        start_frame = ttk.Frame(notebook)
        notebook.add(start_frame, text="Emülatör Başlat")

        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, maximum=100, style="TProgressbar")
        self.progress.pack(pady=10, fill="x")
        self.progress_label = ttk.Label(main_frame, text="Durum: Hazır")
        self.progress_label.pack()

        # Windows Optimization Buttons
        ttk.Button(win_frame, text="Gereksiz Hizmetleri Kapat", command=lambda: self.run_with_progress(self.disable_services, "Bu işlem bazı hizmetleri (ör. Yazıcı, Arama) devre dışı bırakır. Sistem işlevselliği etkilenebilir. Devam etmek istiyor musunuz?")).pack(pady=5, fill="x")
        ttk.Button(win_frame, text="Başlangıç Programlarını Kapat", command=lambda: self.run_with_progress(self.disable_startup, "Bu işlem başlangıç programlarını kaldırabilir. Önemli uygulamalar başlamayabilir. Devam etmek istiyor musunuz?")).pack(pady=5, fill="x")
        ttk.Button(win_frame, text="Görsel Efektleri Kapat", command=lambda: self.run_with_progress(self.disable_visual_effects, "Bu işlem görsel efektleri devre dışı bırakır, arayüz sadeleşir. Devam etmek istiyor musunuz?")).pack(pady=5, fill="x")
        ttk.Button(win_frame, text="Disk Temizleme Yap", command=lambda: self.run_with_progress(self.clean_temp_files, "Bu işlem geçici dosyaları siler. Önemli veriler etkilenmez, ancak dikkatli olun. Devam etmek istiyor musunuz?")).pack(pady=5, fill="x")
        ttk.Button(win_frame, text="Güç Planını Performansa Ayarla", command=lambda: self.run_with_progress(self.set_power_plan, "Bu işlem güç tüketimini artırabilir. Devam etmek istiyor musunuz?")).pack(pady=5, fill="x")
        ttk.Button(win_frame, text="Tarayıcı Çerezlerini Temizle", command=lambda: self.run_with_progress(self.clear_browser_cache, "Bu işlem tarayıcı çerezlerini ve önbelleği siler. Oturumlar kapanabilir. Devam etmek istiyor musunuz?")).pack(pady=5, fill="x")
        ttk.Button(win_frame, text="Kayıt Defteri Optimizasyonu", command=lambda: self.run_with_progress(self.optimize_registry, "Bu işlem kayıt defterini optimize eder. Hatalı değişiklikler sistemi bozabilir. Devam etmek istiyor musunuz?")).pack(pady=5, fill="x")
        ttk.Button(win_frame, text="Tüm Değişiklikleri Geri Al", command=lambda: self.run_with_progress(self.undo_changes, "Bu işlem yapılan tüm optimizasyonları geri alır. Devam etmek istiyor musunuz?")).pack(pady=5, fill="x")

        # Emulator Optimization Buttons
        ttk.Label(emu_frame, text="Emülatör Performans Ayarları", font=("Arial", 12, "bold")).pack(pady=5)
        ttk.Button(emu_frame, text="Emülatör için CPU Önceliğini Artır", command=lambda: self.run_with_progress(self.boost_emulator_cpu, "Bu işlem emülatörün CPU önceliğini artırır. Diğer uygulamalar yavaşlayabilir. Devam etmek istiyor musunuz?")).pack(pady=5, fill="x")
        ttk.Button(emu_frame, text="Arka Plan Uygulamalarını Kapat", command=lambda: self.run_with_progress(self.close_background_apps, "Bu işlem arka plan uygulamalarını kapatır. Önemli işlemler kesintiye uğrayabilir. Devam etmek istiyor musunuz?")).pack(pady=5, fill="x")
        ttk.Button(emu_frame, text="Emülatör için Bellek Temizleme", command=lambda: self.run_with_progress(self.clear_memory, "Bu işlem sistem belleğini temizler. Devam etmek istiyor musunuz?")).pack(pady=5, fill="x")
        ttk.Button(emu_frame, text="Windows Oyun Modunu Aç", command=lambda: self.run_with_progress(self.enable_game_mode, "Bu işlem oyun modunu etkinleştirir. Sistem davranışı değişebilir. Devam etmek istiyor musunuz?")).pack(pady=5, fill="x")

        # Emulator Start Tab
        ttk.Label(start_frame, text="Emülatör Başlatma", font=("Arial", 12, "bold")).pack(pady=5)
        self.emulator_var = tk.StringVar()
        self.emulator_combo = ttk.Combobox(start_frame, textvariable=self.emulator_var, values=["BlueStacks", "LDPlayer", "Nox", "MEmu"], state="readonly")
        self.emulator_combo.set("BlueStacks")
        self.emulator_combo.pack(pady=5)
        ttk.Button(start_frame, text="Emülatörü Otomatik Başlat", command=lambda: self.run_with_progress(self.start_emulator, "Bu işlem emülatörü başlatmadan önce tüm optimizasyonları yapar. Sistem kaynakları yoğun kullanılabilir. Devam etmek istiyor musunuz?")).pack(pady=5, fill="x")
        ttk.Button(start_frame, text="Emülatör Yolu Seç", command=self.select_emulator_path).pack(pady=5, fill="x")

        # Exit Button
        ttk.Button(main_frame, text="Çıkış", command=root.quit, style="TButton").pack(pady=15)

        # Status Bar
        self.status = ttk.Label(main_frame, text="Hazır", relief="sunken", anchor="w")
        self.status.pack(side="bottom", fill="x")

        # Check for admin privileges
        if not self.is_admin():
            self.limited_mode = True
            self.status.config(text="Yönetici izni yok, sınırlı modda çalışıyor!")
            messagebox.showwarning("Sınırlı Mod", "Program yönetici izni olmadan başlatıldı. Hizmet kapatma, kayıt defteri düzenleme ve güç planı değişiklikleri devre dışı. Tam işlevsellik için lütfen yönetici olarak yeniden başlatın.")
            logging.info("Program sınırlı modda başlatıldı.")
        else:
            self.run_as_admin()  # Only call if not already admin

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def run_as_admin(self):
        if not self.is_admin():
            try:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                logging.info("Program yönetici olarak yeniden başlatılmaya çalışılıyor.")
                self.root.quit()  # Close the current instance gracefully
            except Exception as e:
                logging.error(f"Yönetici olarak başlatma başarısız: {str(e)}")
                self.limited_mode = True
                self.status.config(text="Yönetici izni yok, sınırlı modda çalışıyor!")
                messagebox.showwarning("Sınırlı Mod", "Yönetici izni verilmedi. Hizmet kapatma, kayıt defteri düzenleme ve güç planı değişiklikleri devre dışı. Tam işlevsellik için lütfen yönetici olarak yeniden başlatın.")
                logging.info("Program sınırlı modda başlatıldı.")

    def load_emulator_paths(self):
        try:
            config_file = "emulator_paths.json"
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    saved_paths = json.load(f)
                    for emulator, path in saved_paths.items():
                        if emulator in self.emulator_paths and os.path.exists(path):
                            self.emulator_paths[emulator] = path
                print("Emülatör yolları yüklendi:", self.emulator_paths)
                logging.info(f"Emülatör yolları yüklendi: {self.emulator_paths}")
            else:
                logging.debug("Emülatör yolları dosyası bulunamadı, varsayılan yollar kullanılacak.")
        except Exception as e:
            print(f"Emülatör yolları yüklenemedi: {str(e)}")
            logging.error(f"Emülatör yolları yüklenemedi: {str(e)}")

    def save_emulator_paths(self):
        try:
            config_file = "emulator_paths.json"
            with open(config_file, "w") as f:
                json.dump(self.emulator_paths, f, indent=4)
            print("Emülatör yolları kaydedildi:", self.emulator_paths)
            logging.info(f"Emülatör yolları kaydedildi: {self.emulator_paths}")
        except Exception as e:
            print(f"Emülatör yolları kaydedilemedi: {str(e)}")
            logging.error(f"Emülatör yolları kaydedilemedi: {str(e)}")

    def run_with_progress(self, func, warning_message):
        if self.limited_mode and func.__name__ in ["disable_services", "disable_startup", "disable_visual_effects", "set_power_plan", "optimize_registry", "undo_changes"]:
            self.status.config(text="Sınırlı mod: İşlem devre dışı!")
            messagebox.showwarning("Sınırlı Mod", f"{func.__name__} için yönetici izni gerekli!")
            logging.info(f"Sınırlı mod: {func.__name__} atlandı.")
            return
        if not messagebox.askyesno("Uyarı", warning_message):
            self.status.config(text="İşlem iptal edildi.")
            print("İşlem iptal edildi.")
            logging.info("İşlem iptal edildi.")
            return
        self.progress["value"] = 0
        self.progress_label.config(text="İşlem başlatılıyor...")
        self.root.update()
        try:
            if self.debug_mode:
                logging.debug(f"Başlatılan işlem: {func.__name__}")
                self.operations.append(func.__name__)
            for i in range(10, 100, 10):
                self.progress["value"] = i
                self.progress_label.config(text=f"İşlem: %{i}")
                self.root.update()
                time.sleep(0.5)
            func()
            self.progress["value"] = 100
            self.progress_label.config(text="İşlem Tamamlandı!")
        except Exception as e:
            logging.error(f"Hata oluştu: {str(e)}")
            print(f"Hata oluştu: {str(e)}")
            self.progress["value"] = 0
            self.progress_label.config(text="Hata!")
            messagebox.showerror("Hata", f"İşlem başarısız: {str(e)}")
            if self.debug_mode and func.__name__ in ["start_emulator", "disable_services", "close_background_apps", "clear_memory", "optimize_registry"]:
                logging.debug("Hata nedeniyle geri alma başlatılıyor...")
                self.undo_changes()
                messagebox.showinfo("Geri Alma", "Hata nedeniyle işlemler geri alındı.")
            raise

    def find_emulator_paths(self):
        default_paths = {
            "BlueStacks": r"C:\Program Files\BlueStacks_nxt\HD-Player.exe",
            "LDPlayer": r"C:\LDPlayer\dnplayer.exe",
            "Nox": r"C:\Program Files (x86)\Nox\bin\Nox.exe",
            "MEmu": r"C:\Program Files\Microvirt\MEmu\MEmu.exe"
        }
        for emulator, path in default_paths.items():
            if not self.emulator_paths[emulator] and os.path.exists(path):
                self.emulator_paths[emulator] = path
        self.save_emulator_paths()
        self.status.config(text="Emülatör yolları kontrol edildi.")
        print("Emülatör yolları kontrol edildi:", self.emulator_paths)
        logging.info(f"Emülatör yolları kontrol edildi: {self.emulator_paths}")

    def select_emulator_path(self):
        emulator = self.emulator_var.get()
        path = filedialog.askopenfilename(title=f"{emulator} Yolu Seç", filetypes=[("Executable files", "*.exe")])
        if path:
            self.emulator_paths[emulator] = path
            self.save_emulator_paths()
            self.status.config(text=f"{emulator} yolu güncellendi!")
            messagebox.showinfo("Başarılı", f"{emulator} için yol seçildi: {path}")
            print(f"{emulator} için yol seçildi: {path}")
            logging.info(f"{emulator} için yol seçildi: {path}")

    def start_emulator(self):
        emulator = self.emulator_var.get()
        if not self.emulator_paths[emulator]:
            messagebox.showerror("Hata", f"{emulator} için geçerli bir yol belirtilmedi!")
            print(f"Hata: {emulator} için yol belirtilmedi.")
            logging.error(f"Hata: {emulator} için yol belirtilmedi.")
            return

        print(f"{emulator} başlatılıyor...")
        logging.info(f"{emulator} başlatılıyor...")
        try:
            # Start emulator
            process = subprocess.Popen([self.emulator_paths[emulator]], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.debug(f"{emulator} başlatma komutu gönderildi: {self.emulator_paths[emulator]}")
            time.sleep(5)  # Wait for emulator to initialize

            # Check if emulator process is running
            try:
                psutil.Process(process.pid)
                logging.debug(f"{emulator} işlemi başlatıldı, PID: {process.pid}")
            except psutil.NoSuchProcess:
                raise Exception(f"{emulator} işlemi başlatılamadı.")

            # Perform optimizations
            self.disable_services()
            self.progress["value"] = 25
            self.progress_label.config(text="Hizmetler kapatıldı: %25")
            self.root.update()
            time.sleep(0.5)

            self.disable_startup()
            self.progress["value"] = 50
            self.progress_label.config(text="Başlangıç programları kapatıldı: %50")
            self.root.update()
            time.sleep(0.5)

            self.disable_visual_effects()
            self.progress["value"] = 75
            self.progress_label.config(text="Görsel efektler kapatıldı: %75")
            self.root.update()
            time.sleep(0.5)

            self.set_power_plan()
            self.enable_game_mode()
            self.boost_emulator_cpu()

            self.progress["value"] = 100
            self.progress_label.config(text=f"{emulator} başlatıldı: %100")
            self.status.config(text=f"{emulator} başlatıldı!")
            messagebox.showinfo("Başarılı", f"{emulator} başarıyla başlatıldı!")
            print(f"{emulator} başarıyla başlatıldı.")
            logging.info(f"{emulator} başarıyla başlatıldı.")
        except Exception as e:
            logging.error(f"start_emulator başarısız: {str(e)}")
            self.undo_changes()
            raise

    def disable_startup(self):
        if self.limited_mode:
            self.status.config(text="Sınırlı mod: Başlangıç temizleme devre dışı!")
            messagebox.showwarning("Sınırlı Mod", "Başlangıç programlarını temizleme için yönetici izni gerekli!")
            logging.info("Sınırlı mod: Başlangıç temizleme atlandı.")
            return
        try:
            c = wmi.WMI()
            services = ["Spooler", "WSearch", "SysMain"]
            self.disabled_services = []
            for service_name in services:
                service_list = c.Win32_Service(Name=service_name)
                if not service_list:
                    print(f"Hata: {service_name} hizmeti bulunamadı.")
                    logging.error(f"Hata: {service_name} hizmeti bulunamadı.")
                    self.status.config(text=f"Hata: {service_name} hizmeti bulunamadı!")
                    continue
                for service in service_list:
                    print(f"İşlem yapılıyor: {service_name}, Durum: {service.State}")
                    logging.debug(f"İşlem yapılıyor: {service_name}, Durum: {service.State}")
                    if service.State == "Running":
                        result = service.StopService()
                        if result == 0:
                            print(f"{service_name} hizmeti durduruldu.")
                            logging.debug(f"{service_name} hizmeti durduruldu.")
                        else:
                            print(f"Hata: {service_name} hizmeti durdurulamadı, hata kodu: {result}")
                            logging.error(f"Hata: {service_name} hizmeti durdurulamadı, hata kodu: {result}")
                    if service.StartMode != "Disabled":
                        result = service.ChangeStartMode("Disabled")
                        if result == 0:
                            self.disabled_services.append(service_name)
                            print(f"{service_name} hizmeti devre dışı bırakıldı.")
                            logging.debug(f"{service_name} hizmeti devre dışı bırakıldı.")
                        else:
                            print(f"Hata: {service_name} hizmeti devre dışı bırakılamadı, hata kodu: {result}")
                            logging.error(f"Hata: {service_name} hizmeti devre dışı bırakılamadı, hata kodu: {result}")
            self.status.config(text="Hizmetler kapatıldı!")
            print("Hizmetler kapatıldı.")
            logging.info("Hizmetler kapatıldı.")
            messagebox.showinfo("Başarılı", "Gereksiz hizmetler kapatıldı!")
        except Exception as e:
            self.status.config(text="Hata: Hizmet kapatma başarısız!")
            print(f"Hata: Hizmet kapatma başarısız: {str(e)}")
            logging.error(f"Hata: Hizmet kapatma başarısız: {str(e)}")
            messagebox.showerror("Hata", f"Hizmet kapatma başarısız: {str(e)}")
            raise

    def disable_startup(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
            self.removed_startup_items = []
            for value_name in ["ExampleProgram", "OneDrive"]:
                try:
                    value, _ = winreg.QueryValueEx(key, value_name)
                    winreg.DeleteValue(key, value_name)
                    self.removed_startup_items.append((value_name, value))
                    print(f"Başlangıç programı kaldırıldı: {value_name}")
                    logging.debug(f"Başlangıç programı kaldırıldı: {value_name}")
                except:
                    print(f"Başlangıç programı bulunamadı: {value_name}")
                    logging.debug(f"Başlangıç programı bulunamadı: {value_name}")
            winreg.CloseKey(key)
            self.status.config(text="Başlangıç programları temizlendi!")
            print("Başlangıç programları temizlendi.")
            logging.info("Başlangıç programları temizlendi.")
            messagebox.showinfo("Başarılı", "Başlangıç programları temizlendi!")
        except Exception as e:
            self.status.config(text="Hata: Başlangıç temizleme başarısız!")
            print(f"Hata: Başlangıç temizleme başarısız: {str(e)}")
            logging.error(f"Hata: Başlangıç temizleme başarısız: {str(e)}")
            messagebox.showerror("Hata", f"Başlangıç temizleme başarısız: {str(e)}")
            raise

    def disable_visual_effects(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", 0, winreg.KEY_ALL_ACCESS)
            try:
                self.original_visual_effects = winreg.QueryValueEx(key, "VisualFXSetting")[0]
            except:
                self.original_visual_effects = None
            winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
            winreg.CloseKey(key)
            self.status.config(text="Görsel efektler kapatıldı!")
            print("Görsel efektler kapatıldı.")
            logging.info("Görsel efektler kapatıldı.")
            messagebox.showinfo("Başarılı", "Görsel efektler kapatıldı!")
        except Exception as e:
            self.status.config(text="Hata: Görsel efekt kapatma başarısız!")
            print(f"Hata: Görsel efekt kapatma başarısız: {str(e)}")
            logging.error(f"Hata: Görsel efekt kapatma başarısız: {str(e)}")
            messagebox.showerror("Hata", f"Görsel efekt kapatma başarısız: {str(e)}")
            raise

    def clean_temp_files(self):
        try:
            os.system("del /q /s %temp%\\*.*")
            subprocess.run("cleanmgr /sagerun:1", shell=True, check=False)
            self.status.config(text="Disk temizleme tamamlandı!")
            print("Disk temizleme tamamlandı.")
            logging.info("Disk temizleme tamamlandı.")
            messagebox.showinfo("Başarılı", "Disk temizleme tamamlandı!")
        except Exception as e:
            self.status.config(text="Hata: Disk temizleme başarısız!")
            print(f"Hata: Disk temizleme başarısız: {str(e)}")
            logging.error(f"Hata: Disk temizleme başarısız: {str(e)}")
            messagebox.showerror("Hata", f"Disk temizleme başarısız: {str(e)}")
            raise

    def set_power_plan(self):
        try:
            subprocess.run("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", shell=True, check=True)
            self.status.config(text="Yüksek performans planı aktif!")
            print("Yüksek performans planı aktif.")
            logging.info("Yüksek performans planı aktif.")
            messagebox.showinfo("Başarılı", "Güç planı yüksek performansa ayarlandı!")
        except Exception as e:
            self.status.config(text="Hata: Güç planı ayarı başarısız!")
            print(f"Hata: Güç planı ayarı başarısız: {str(e)}")
            logging.error(f"Hata: Güç planı ayarı başarısız: {str(e)}")
            messagebox.showerror("Hata", f"Güç planı ayarı başarısız: {str(e)}")
            raise

    def boost_emulator_cpu(self):
        try:
            emulator = self.emulator_var.get()
            if not self.emulator_paths[emulator]:
                raise Exception(f"{emulator} için yol belirtilmedi.")
            emulator_processes = {
                "BlueStacks": ["HD-Player.exe", "Bluestacks.exe"],
                "LDPlayer": ["dnplayer.exe", "LDPlayer.exe"],
                "Nox": ["Nox.exe", "NoxVMHandle.exe"],
                "MEmu": ["MEmu.exe", "MEmuHeadless.exe"]
            }
            found = False
            for _ in range(3):
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] in emulator_processes[emulator]:
                        proc.nice(psutil.REALTIME_PRIORITY_CLASS)
                        found = True
                        print(f"{emulator} için CPU önceliği artırıldı: {proc.info['name']}")
                        logging.debug(f"{emulator} için CPU önceliği artırıldı: {proc.info['name']}")
                        break
                if found:
                    break
                logging.debug(f"{emulator} işlemi bulunamadı, tekrar deneniyor...")
                time.sleep(2)
            if not found:
                print(f"Hata: {emulator} işlemi bulunamadı.")
                logging.error(f"Hata: {emulator} işlemi bulunamadı.")
                raise Exception(f"{emulator} işlemi bulunamadı.")
            self.status.config(text=f"{emulator} CPU önceliği artırıldı!")
            print(f"{emulator} CPU önceliği artırıldı.")
            logging.info(f"{emulator} CPU önceliği artırıldı.")
            messagebox.showinfo("Başarılı", f"{emulator} için CPU önceliği artırıldı!")
        except Exception as e:
            self.status.config(text="Hata: CPU önceliği artırma başarısız!")
            print(f"Hata: CPU önceliği artırma başarısız: {str(e)}")
            logging.error(f"Hata: CPU önceliği artırma başarısız: {str(e)}")
            messagebox.showerror("Hata", f"CPU önceliği artırma başarısız: {str(e)}")
            raise

    def close_background_apps(self):
        try:
            exclude = [
                "svchost.exe", "explorer.exe", "cmd.exe", "python.exe",
                "dwm.exe", "winlogon.exe", "csrss.exe", "smss.exe",
                "System", "Idle", "conhost.exe", "taskhostw.exe",
                "lsass.exe", "spoolsv.exe", "fontdrvhost.exe"
            ]
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] not in exclude and "emulator" not in proc.info['name'].lower():
                    try:
                        proc.terminate()
                        print(f"Arka plan uygulaması kapatıldı: {proc.info['name']}")
                        logging.debug(f"Arka plan uygulaması kapatıldı: {proc.info['name']}")
                    except:
                        print(f"Arka plan uygulaması kapatılamadı: {proc.info['name']}")
                        logging.debug(f"Arka plan uygulaması kapatılamadı: {proc.info['name']}")
            self.status.config(text="Arka plan uygulamaları kapatıldı!")
            print("Arka plan uygulamaları kapatıldı.")
            logging.info("Arka plan uygulamaları kapatıldı.")
            messagebox.showinfo("Başarılı", "Arka plan uygulamaları kapatıldı!")
        except Exception as e:
            self.status.config(text="Hata: Arka plan kapatma başarısız!")
            print(f"Hata: Arka plan kapatma başarısız: {str(e)}")
            logging.error(f"Hata: Arka plan kapatma başarısız: {str(e)}")
            messagebox.showerror("Hata", f"Arka plan kapatma başarısız: {str(e)}")
            raise

    def clear_memory(self):
        try:
            ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
            self.status.config(text="Bellek temizlendi!")
            print("Bellek temizlendi.")
            logging.info("Bellek temizlendi.")
            messagebox.showinfo("Başarılı", "Bellek temizlendi!")
        except Exception as e:
            self.status.config(text="Hata: Bellek temizleme başarısız!")
            print(f"Hata: Bellek temizleme başarısız: {str(e)}")
            logging.error(f"Hata: Bellek temizleme başarısız: {str(e)}")
            messagebox.showerror("Hata", f"Bellek temizleme başarısız: {str(e)}")
            raise

    def enable_game_mode(self):
        if self.limited_mode:
            self.status.config(text="Sınırlı mod: Oyun modu devre dışı!")
            messagebox.showwarning("Sınırlı Mod", "Oyun modu etkinleştirme için yönetici izni gerekli!")
            logging.info("Sınırlı mod: Oyun modu atlandı.")
            return
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "AllowAutoGameMode", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            self.status.config(text="Oyun modu aktif!")
            print("Oyun modu aktif.")
            logging.info("Oyun modu aktif.")
            messagebox.showinfo("Başarılı", "Oyun modu aktifleştirildi!")
        except Exception as e:
            self.status.config(text="Hata: Oyun modu ayarı başarısız!")
            print(f"Hata: Oyun modu ayarı başarısız: {str(e)}")
            logging.error(f"Hata: Oyun modu ayarı başarısız: {str(e)}")
            messagebox.showerror("Hata", f"Oyun modu ayarı başarısız: {str(e)}")
            raise

    def clear_browser_cache(self):
        try:
            browser_paths = {
                "Chrome": os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\Cache"),
                "Firefox": os.path.expanduser(r"~\AppData\Local\Mozilla\Firefox\Profiles"),
                "Edge": os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\User Data\Default\Cache")
            }
            for browser, cache_path in browser_paths.items():
                if os.path.exists(cache_path):
                    try:
                        shutil.rmtree(cache_path, ignore_errors=True)
                        print(f"{browser} önbelleği temizlendi.")
                        logging.debug(f"{browser} önbelleği temizlendi.")
                    except Exception as e:
                        print(f"Hata: {browser} önbelleği temizlenemedi: {str(e)}")
                        logging.error(f"Hata: {browser} önbelleği temizlenemedi: {str(e)}")
                else:
                    print(f"Hata: {browser} önbellek dizini bulunamadı.")
                    logging.debug(f"Hata: {browser} önbellek dizini bulunamadı.")
            self.status.config(text="Tarayıcı çerezleri ve önbellek temizlendi!")
            print("Tarayıcı çerezleri ve önbellek temizlendi.")
            logging.info("Tarayıcı çerezleri ve önbellek temizlendi.")
            messagebox.showinfo("Başarılı", "Tarayıcı çerezleri ve önbellek temizlendi!")
        except Exception as e:
            self.status.config(text="Hata: Tarayıcı önbellek temizleme başarısız!")
            print(f"Hata: Tarayıcı önbellek temizleme başarısız: {str(e)}")
            logging.error(f"Hata: Tarayıcı önbellek temizleme başarısız: {str(e)}")
            messagebox.showerror("Hata", f"Tarayıcı önbellek temizleme başarısız: {str(e)}")
            raise

    def optimize_registry(self):
        try:
            backup_dir = os.path.expanduser(r"~\Desktop\RegistryBackup")
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.registry_backup_path = os.path.join(backup_dir, f"registry_backup_{timestamp}.reg")
            result = subprocess.run(f'reg export HKCU "{self.registry_backup_path}"', shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Kayıt defteri yedekleme başarısız: {result.stderr}")
            print(f"Kayıt defteri yedeklendi: {self.registry_backup_path}")
            logging.debug(f"Kayıt defteri yedeklendi: {self.registry_backup_path}")

            context_menu_key = r"Software\Classes\*\shell"
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, context_menu_key, 0, winreg.KEY_ALL_ACCESS)
            except FileNotFoundError:
                print(f"Hata: Kayıt defteri anahtarı bulunamadı: {context_menu_key}")
                logging.error(f"Hata: Kayıt defteri anahtarı bulunamadı: {context_menu_key}")
                self.status.config(text="Kayıt defteri anahtarı bulunamadı, optimizasyon atlandı.")
                messagebox.showinfo("Bilgi", "Kayıt defteri anahtarı bulunamadı, optimizasyon atlandı.")
                return

            self.removed_registry_items = []
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    if "ExampleContextMenu" in subkey_name:
                        subkey_path = f"{context_menu_key}\\{subkey_name}"
                        winreg.DeleteKey(key, subkey_name)
                        self.removed_registry_items.append(subkey_path)
                        print(f"Kayıt defteri girdisi kaldırıldı: {subkey_name}")
                        logging.debug(f"Kayıt defteri girdisi kaldırıldı: {subkey_name}")
                    else:
                        i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
            self.status.config(text="Kayıt defteri optimize edildi!")
            print("Kayıt defteri optimize edildi.")
            logging.info("Kayıt defteri optimize edildi.")
            messagebox.showinfo("Başarılı", "Kayıt defteri optimize edildi!")
        except Exception as e:
            self.status.config(text="Hata: Kayıt defteri optimizasyonu başarısız!")
            print(f"Hata: Kayıt defteri optimizasyonu başarısız: {str(e)}")
            logging.error(f"Hata: Kayıt defteri optimizasyonu başarısız: {str(e)}")
            messagebox.showerror("Hata", f"Kayıt defteri optimizasyonu başarısız: {str(e)}")
            raise

    def undo_changes(self):
        try:
            c = wmi.WMI()
            for service_name in self.disabled_services:
                service_list = c.Win32_Service(Name=service_name)
                if service_list:
                    for service in service_list:
                        result = service.ChangeStartMode("Automatic")
                        if result == 0:
                            service.StartService()
                            print(f"{service_name} hizmeti geri yüklendi.")
                            logging.debug(f"{service_name} hizmeti geri yüklendi.")
                        else:
                            print(f"Hata: {service_name} hizmeti geri yüklenemedi, hata kodu: {result}")
                            logging.error(f"Hata: {service_name} hizmeti geri yüklenemedi, hata kodu: {result}")
            self.disabled_services = []

            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            for value_name, value in self.removed_startup_items:
                try:
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value)
                    print(f"Başlangıç programı geri yüklendi: {value_name}")
                    logging.debug(f"Başlangıç programı geri yüklendi: {value_name}")
                except:
                    print(f"Başlangıç programı geri yüklenemedi: {value_name}")
                    logging.error(f"Başlangıç programı geri yüklenemedi: {value_name}")
            winreg.CloseKey(key)
            self.removed_startup_items = []

            if self.original_visual_effects is not None:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, self.original_visual_effects)
                winreg.CloseKey(key)
                print("Görsel efektler geri yüklendi.")
                logging.debug("Görsel efektler geri yüklendi.")
                self.original_visual_effects = None

            subprocess.run("powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e", shell=True, check=True)
            print("Dengeli güç planı geri yüklendi.")
            logging.debug("Dengeli güç planı geri yüklendi.")

            if self.registry_backup_path and os.path.exists(self.registry_backup_path):
                result = subprocess.run(f'reg import "{self.registry_backup_path}"', shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(f"Kayıt defteri geri yükleme başarısız: {result.stderr}")
                print("Kayıt defteri geri yüklendi.")
                logging.debug("Kayıt defteri geri yüklendi.")
                self.registry_backup_path = None

            self.status.config(text="Tüm değişiklikler geri alındı!")
            print("Tüm değişiklikler geri alındı.")
            logging.info("Tüm değişiklikler geri alındı.")
            messagebox.showinfo("Başarılı", "Tüm değişiklikler geri alındı!")
        except Exception as e:
            self.status.config(text="Hata: Geri alma başarısız!")
            print(f"Hata: Geri alma başarısız: {str(e)}")
            logging.error(f"Hata: Geri alma başarısız: {str(e)}")
            messagebox.showerror("Hata", f"Geri alma başarısız: {str(e)}")
            raise

if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    else:
        root = tk.Tk()
        app = WinOptimizerApp(root)
        root.mainloop()