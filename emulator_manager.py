import os
import psutil
import json
import logging
import subprocess
import time
import winreg
from typing import Dict, List, Optional, Tuple

class EmulatorManager:
    """Modern emülatör yöneticisi - BlueStacks, MEmu, LDPlayer, Nox desteği"""
    
    def __init__(self):
        self.emulator_paths = {
            "BlueStacks": "",
            "LDPlayer": "",
            "Nox": "",
            "MEmu": "",
            "NoxPlayer": "",
            "GameLoop": "",
            "MSI App Player": ""
        }
        
        # Emülatör işlem adları
        self.emulator_processes = {
            "BlueStacks": ["HD-Player.exe", "Bluestacks.exe", "BlueStacksServices.exe"],
            "LDPlayer": ["dnplayer.exe", "LDPlayer.exe", "LdVBoxHeadless.exe"],
            "Nox": ["Nox.exe", "NoxVMHandle.exe", "VirtualBox.exe"],
            "MEmu": ["MEmu.exe", "MEmuHeadless.exe", "VirtualBox.exe"],
            "NoxPlayer": ["NoxPlayer.exe", "Nox.exe"],
            "GameLoop": ["AndroidEmulator.exe", "GameLoop.exe"],
            "MSI App Player": ["MSIAppPlayer.exe"]
        }
        
        # Varsayılan yollar
        self.default_paths = {
            "BlueStacks": [
                r"C:\Program Files\BlueStacks_nxt\HD-Player.exe",
                r"C:\Program Files\BlueStacks\HD-Player.exe",
                r"C:\Program Files (x86)\BlueStacks_nxt\HD-Player.exe",
                r"C:\Program Files (x86)\BlueStacks\HD-Player.exe"
            ],
            "LDPlayer": [
                r"C:\LDPlayer\LDPlayer4.0\dnplayer.exe",
                r"C:\LDPlayer\dnplayer.exe",
                r"C:\Program Files\LDPlayer\dnplayer.exe"
            ],
            "Nox": [
                r"C:\Program Files (x86)\Nox\bin\Nox.exe",
                r"C:\Program Files\Nox\bin\Nox.exe",
                r"C:\Nox\bin\Nox.exe"
            ],
            "MEmu": [
                r"C:\Program Files\Microvirt\MEmu\MEmu.exe",
                r"C:\Microvirt\MEmu\MEmu.exe",
                r"C:\Program Files (x86)\Microvirt\MEmu\MEmu.exe"
            ],
            "NoxPlayer": [
                r"C:\Program Files (x86)\Nox\bin\NoxPlayer.exe",
                r"C:\Program Files\Nox\bin\NoxPlayer.exe"
            ],
            "GameLoop": [
                r"C:\Program Files\TxGameAssistant\AppMarket\AndroidEmulator.exe",
                r"C:\Program Files (x86)\TxGameAssistant\AppMarket\AndroidEmulator.exe"
            ],
            "MSI App Player": [
                r"C:\Program Files\MSI\MSI App Player\MSIAppPlayer.exe",
                r"C:\Program Files (x86)\MSI\MSI App Player\MSIAppPlayer.exe"
            ]
        }
        
        self.load_paths()
        
    def load_paths(self):
        """Kaydedilmiş emülatör yollarını yükle"""
        try:
            if os.path.exists("emulator_paths.json"):
                with open("emulator_paths.json", "r", encoding="utf-8") as f:
                    saved_paths = json.load(f)
                    for emulator, path in saved_paths.items():
                        if emulator in self.emulator_paths and os.path.exists(path):
                            self.emulator_paths[emulator] = path
                logging.info("Emülatör yolları başarıyla yüklendi")
        except Exception as e:
            logging.error(f"Emülatör yolları yüklenirken hata: {e}")
    
    def save_paths(self):
        """Emülatör yollarını kaydet"""
        try:
            with open("emulator_paths.json", "w", encoding="utf-8") as f:
                json.dump(self.emulator_paths, f, indent=4, ensure_ascii=False)
            logging.info("Emülatör yolları başarıyla kaydedildi")
        except Exception as e:
            logging.error(f"Emülatör yolları kaydedilirken hata: {e}")
    
    def auto_detect_emulators(self) -> Dict[str, str]:
        """Emülatörleri otomatik algıla"""
        detected = {}
        
        # Varsayılan yolları kontrol et
        for emulator, paths in self.default_paths.items():
            for path in paths:
                if os.path.exists(path):
                    detected[emulator] = path
                    self.emulator_paths[emulator] = path
                    break
        
        # Registry'den de kontrol et
        registry_detected = self._detect_from_registry()
        detected.update(registry_detected)
        
        # Çalışan işlemlerden algıla
        running_detected = self._detect_running_emulators()
        detected.update(running_detected)
        
        if detected:
            self.save_paths()
            logging.info(f"Otomatik algılanan emülatörler: {list(detected.keys())}")
        
        return detected
    
    def _detect_from_registry(self) -> Dict[str, str]:
        """Registry'den emülatör yollarını algıla"""
        detected = {}
        registry_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        
        emulator_keywords = {
            "BlueStacks": ["bluestacks", "bstk"],
            "LDPlayer": ["ldplayer", "ldmnq"],
            "Nox": ["nox", "noxplayer"],
            "MEmu": ["memu", "microvirt"],
            "GameLoop": ["gameloop", "txgameassistant"],
            "MSI App Player": ["msi app player", "msiappplayer"]
        }
        
        try:
            for hkey, subkey in registry_keys:
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        i = 0
                        while True:
                            try:
                                app_key = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, app_key) as app:
                                    try:
                                        display_name = winreg.QueryValueEx(app, "DisplayName")[0].lower()
                                        install_location = winreg.QueryValueEx(app, "InstallLocation")[0]
                                        
                                        for emulator, keywords in emulator_keywords.items():
                                            if any(keyword in display_name for keyword in keywords):
                                                # Ana exe dosyasını bul
                                                for path in self.default_paths.get(emulator, []):
                                                    filename = os.path.basename(path)
                                                    full_path = os.path.join(install_location, filename)
                                                    if os.path.exists(full_path):
                                                        detected[emulator] = full_path
                                                        break
                                    except FileNotFoundError:
                                        pass
                                i += 1
                            except OSError:
                                break
                except FileNotFoundError:
                    continue
        except Exception as e:
            logging.debug(f"Registry taramasında hata: {e}")
        
        return detected
    
    def _detect_running_emulators(self) -> Dict[str, str]:
        """Çalışan emülatörlerden yol bilgisini al"""
        detected = {}
        
        try:
            for process in psutil.process_iter(['name', 'exe']):
                try:
                    process_name = process.info['name']
                    process_exe = process.info['exe']
                    
                    if not process_exe:
                        continue
                    
                    for emulator, processes in self.emulator_processes.items():
                        if process_name in processes:
                            detected[emulator] = process_exe
                            self.emulator_paths[emulator] = process_exe
                            break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logging.debug(f"Çalışan işlem taramasında hata: {e}")
        
        return detected
    
    def get_running_emulators(self) -> List[str]:
        """Çalışan emülatörleri listele"""
        running = []
        
        try:
            for process in psutil.process_iter(['name']):
                try:
                    process_name = process.info['name']
                    for emulator, processes in self.emulator_processes.items():
                        if process_name in processes and emulator not in running:
                            running.append(emulator)
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logging.error(f"Çalışan emülatör kontrolünde hata: {e}")
        
        return running
    
    def start_emulator(self, emulator: str, wait_time: int = 10) -> bool:
        """Emülatörü başlat"""
        if emulator not in self.emulator_paths or not self.emulator_paths[emulator]:
            logging.error(f"{emulator} için yol belirtilmemiş")
            return False
        
        path = self.emulator_paths[emulator]
        if not os.path.exists(path):
            logging.error(f"{emulator} dosyası bulunamadı: {path}")
            return False
        
        try:
            logging.info(f"{emulator} başlatılıyor: {path}")
            subprocess.Popen([path], shell=True)
            
            # Başlamasını bekle
            start_time = time.time()
            while time.time() - start_time < wait_time:
                if emulator in self.get_running_emulators():
                    logging.info(f"{emulator} başarıyla başlatıldı")
                    return True
                time.sleep(1)
            
            logging.warning(f"{emulator} {wait_time} saniye içinde başlamadı")
            return False
            
        except Exception as e:
            logging.error(f"{emulator} başlatılırken hata: {e}")
            return False
    
    def stop_emulator(self, emulator: str) -> bool:
        """Emülatörü durdur"""
        try:
            processes_to_kill = self.emulator_processes.get(emulator, [])
            killed_any = False
            
            for process in psutil.process_iter(['name', 'pid']):
                try:
                    if process.info['name'] in processes_to_kill:
                        psutil.Process(process.info['pid']).terminate()
                        killed_any = True
                        logging.info(f"{emulator} işlemi durduruldu: {process.info['name']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return killed_any
            
        except Exception as e:
            logging.error(f"{emulator} durdurulurken hata: {e}")
            return False
    
    def get_emulator_window_region(self, emulator: str) -> Optional[Tuple[int, int, int, int]]:
        """Emülatör pencere bölgesini al"""
        # Bu fonksiyon window detection için kullanılacak
        # Şimdilik varsayılan bölge döndürüyoruz
        default_regions = {
            "BlueStacks": (0, 0, 1280, 720),
            "MEmu": (0, 0, 1280, 720),
            "LDPlayer": (0, 0, 1280, 720),
            "Nox": (0, 0, 1280, 720)
        }
        
        return default_regions.get(emulator)
    
    def optimize_for_emulator(self, emulator: str) -> bool:
        """Emülatör için sistem optimizasyonu yap"""
        try:
            # CPU önceliği artır
            processes_to_boost = self.emulator_processes.get(emulator, [])
            boosted = False
            
            for process in psutil.process_iter(['name', 'pid']):
                try:
                    if process.info['name'] in processes_to_boost:
                        proc = psutil.Process(process.info['pid'])
                        proc.nice(psutil.HIGH_PRIORITY_CLASS)
                        boosted = True
                        logging.info(f"{emulator} için CPU önceliği artırıldı: {process.info['name']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return boosted
            
        except Exception as e:
            logging.error(f"{emulator} optimizasyonunda hata: {e}")
            return False
    
    def get_available_emulators(self) -> List[str]:
        """Kullanılabilir emülatörleri listele"""
        available = []
        for emulator, path in self.emulator_paths.items():
            if path and os.path.exists(path):
                available.append(emulator)
        return available
    
    def set_emulator_path(self, emulator: str, path: str) -> bool:
        """Emülatör yolunu manuel olarak ayarla"""
        if emulator in self.emulator_paths and os.path.exists(path):
            self.emulator_paths[emulator] = path
            self.save_paths()
            logging.info(f"{emulator} yolu güncellendi: {path}")
            return True
        return False
