import pyautogui
import time
import json
import os
import requests
import zipfile
import datetime
import logging
import sys
import webbrowser
import subprocess
import shutil
import winreg
import psutil
from typing import Dict, List, Tuple, Optional, Any
import cv2
import numpy as np
from PIL import Image

# --- Loglama Yapılandırması ---
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='bot_logs.log',
        filemode='a'
    )

# --- Sabitler ---
USER_DATA_FILE = "user_data.json" 
LICENSE_API_URL = "https://polychaser.com/bot_api/license_api.php" 
BOT_API_KEY = os.getenv("BOT_API_KEY", "ewrwe4324315sadfASDasdas")
BOT_EXE_NAME = "King Bot Pro.exe"
UPDATER_EXE_NAME = "King Bot Pro Updater.exe"

# Sosyal Medya Linkleri
DISCORD_URL = "https://discord.gg/pJ8Sf464"
TELEGRAM_URL = "https://t.me/+wHPg9nJt1qljMDFk"

# Modern Renkler
MODERN_COLORS = {
    'primary': '#3498db',
    'secondary': '#2ecc71', 
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
    'background': '#ffffff',
    'sidebar': '#2c3e50'
}

# --- PyAutoGUI Ayarları ---
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

class ImageRecognition:
    """Gelişmiş görüntü tanıma sınıfı"""
    
    def __init__(self):
        self.template_cache = {}
        self.last_screenshot = None
        self.screenshot_time = 0
        
    def load_template(self, image_path: str) -> Optional[np.ndarray]:
        """Template görselini yükle ve cache'le"""
        if image_path in self.template_cache:
            return self.template_cache[image_path]
            
        if not os.path.exists(image_path):
            logging.warning(f"Template bulunamadı: {image_path}")
            return None
            
        try:
            template = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if template is not None:
                self.template_cache[image_path] = template
                return template
        except Exception as e:
            logging.error(f"Template yüklenemedi {image_path}: {e}")
            
        return None
    
    def get_fresh_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """Güncel ekran görüntüsü al"""
        try:
            current_time = time.time()
            
            # Çok yakın zamanda alınmış screenshot varsa onu kullan
            if (self.last_screenshot is not None and 
                current_time - self.screenshot_time < 0.5):
                return self.last_screenshot
                
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
                
            # PIL'den OpenCV formatına çevir
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            self.last_screenshot = screenshot_cv
            self.screenshot_time = current_time
            
            return screenshot_cv
            
        except Exception as e:
            logging.error(f"Screenshot alınamadı: {e}")
            return None
    
    def find_template_matches(self, template_path: str, region: Optional[Tuple[int, int, int, int]] = None, 
                            confidence: float = 0.8, max_matches: int = 1) -> List[Tuple[int, int, float]]:
        """Template matching ile çoklu eşleşme bul"""
        template = self.load_template(template_path)
        if template is None:
            return []
            
        screenshot = self.get_fresh_screenshot(region)
        if screenshot is None:
            return []
            
        try:
            # Template matching
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            
            matches = []
            h, w = template.shape[:2]
            
            # Çoklu eşleşme için
            for _ in range(max_matches):
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val >= confidence:
                    x, y = max_loc
                    
                    # Region offset'i ekle
                    if region:
                        x += region[0]
                        y += region[1]
                        
                    matches.append((x + w//2, y + h//2, max_val))
                    
                    # Bu alanı maskele ki tekrar bulunmasın
                    cv2.rectangle(result, (max_loc[0] - w//2, max_loc[1] - h//2), 
                                (max_loc[0] + w//2, max_loc[1] + h//2), 0, -1)
                else:
                    break
                    
            return matches
            
        except Exception as e:
            logging.error(f"Template matching hatası: {e}")
            return []

# Global image recognition instance
image_recognition = ImageRecognition()

# --- Kaynak Yolu Yönetimi ---
def get_resource_path(relative_path: str) -> str:
    """PyInstaller uyumlu kaynak yolu döndür"""
    try:
        base_path = sys._MEIPASS
        logging.debug(f"PyInstaller _MEIPASS yolu kullanılıyor: {base_path}")
    except AttributeError:
        base_path = os.path.abspath(".")
        logging.debug(f"Normal Python yolu kullanılıyor: {base_path}")
    
    full_path = os.path.join(base_path, relative_path)
    logging.debug(f"Kaynak yolu çözüldü: {relative_path} -> {full_path}")
    return full_path

# --- Mouse ve Tıklama İşlemleri ---
def get_mouse_position() -> Tuple[int, int]:
    """Mevcut mouse pozisyonunu al"""
    return pyautogui.position()

def safe_click(x: int, y: int, duration: float = 0.1, double_click: bool = False) -> bool:
    """Güvenli tıklama işlemi"""
    try:
        # Ekran sınırları kontrolü
        screen_width, screen_height = pyautogui.size()
        if not (0 <= x <= screen_width and 0 <= y <= screen_height):
            logging.warning(f"Tıklama koordinatları ekran dışında: ({x}, {y})")
            return False
            
        pyautogui.moveTo(x, y, duration=duration)
        time.sleep(0.1)
        
        if double_click:
            pyautogui.doubleClick()
        else:
            pyautogui.click()
            
        logging.debug(f"Tıklama başarılı: ({x}, {y})")
        return True
        
    except Exception as e:
        logging.error(f"Tıklama hatası ({x}, {y}): {e}")
        return False

def try_click(image_path: str, game_area_region: Tuple[int, int, int, int], 
              max_attempts: int = 3, confidence: float = 0.8, 
              click_offset: Tuple[int, int] = (0, 0), double_click: bool = False) -> bool:
    """Gelişmiş görsel bulma ve tıklama"""
    if not os.path.exists(image_path):
        logging.warning(f"Görsel dosyası bulunamadı: {image_path}")
        return False
        
    for attempt in range(max_attempts):
        try:
            matches = image_recognition.find_template_matches(
                image_path, game_area_region, confidence, max_matches=1
            )
            
            if matches:
                x, y, match_confidence = matches[0]
                
                # Offset uygula
                click_x = x + click_offset[0]
                click_y = y + click_offset[1]
                
                if safe_click(click_x, click_y, double_click=double_click):
                    logging.info(f"Görsel bulundu ve tıklandı: {os.path.basename(image_path)} "
                               f"({click_x}, {click_y}) - Güven: {match_confidence:.3f}")
                    return True
                    
            if attempt < max_attempts - 1:
                time.sleep(0.5)  # Yeniden deneme arası bekleme
                
        except Exception as e:
            logging.error(f"try_click hatası (Deneme {attempt + 1}): {e}")
            
    logging.debug(f"Görsel bulunamadı: {os.path.basename(image_path)} (Güven: {confidence})")
    return False

def find_image_location(image_path: str, game_area_region: Tuple[int, int, int, int], 
                       confidence: float = 0.8) -> Optional[Tuple[int, int]]:
    """Görsel lokasyonunu bul (tıklamadan)"""
    matches = image_recognition.find_template_matches(
        image_path, game_area_region, confidence, max_matches=1
    )
    
    if matches:
        x, y, _ = matches[0]
        return (x, y)
        
    return None

def click_sequence(image_names: List[str], image_paths: Dict[str, str], 
                  game_area_region: Tuple[int, int, int, int], confidence: float = 0.8, 
                  delay: float = 0.5, log_prefix: str = "") -> bool:
    """Görsel sequence'i sırayla tıkla"""
    successful_clicks = 0
    
    for image_name in image_names:
        if image_name in image_paths:
            if try_click(image_paths[image_name], game_area_region, 
                        max_attempts=1, confidence=confidence):
                successful_clicks += 1
                logging.debug(f"[{log_prefix}] {image_name} tıklandı")
                time.sleep(delay)
            else:
                logging.debug(f"[{log_prefix}] {image_name} bulunamadı")
        else:
            logging.warning(f"[{log_prefix}] {image_name} image_paths'te bulunamadı")
            
    return successful_clicks > 0

def find_multiple_images(image_paths: List[str], game_area_region: Tuple[int, int, int, int], 
                        confidence: float = 0.8) -> List[Tuple[str, int, int, float]]:
    """Birden fazla görseli aynı anda ara"""
    found_images = []
    
    for image_path in image_paths:
        if os.path.exists(image_path):
            matches = image_recognition.find_template_matches(
                image_path, game_area_region, confidence, max_matches=1
            )
            
            if matches:
                x, y, match_confidence = matches[0]
                found_images.append((image_path, x, y, match_confidence))
                
    # Güven skoruna göre sırala
    found_images.sort(key=lambda x: x[3], reverse=True)
    return found_images

# --- Yapılandırma Yönetimi ---
def load_config(config_file: str = "config.json") -> Dict[str, Any]:
    """Yapılandırma dosyasını yükle"""
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logging.debug(f"Yapılandırma yüklendi: {config_file}")
                return config
    except Exception as e:
        logging.error(f"Yapılandırma yüklenemedi: {e}")
        
    # Varsayılan yapılandırma
    default_config = {
        "game_area_region": [0, 0, 1920, 1080],
        "confidence_threshold": 0.8,
        "click_delay": 0.5,
        "max_attempts": 3,
        "auto_screenshot": True,
        "emulator_optimization": True
    }
    
    save_config(default_config, config_file)
    return default_config

def save_config(config: Dict[str, Any], config_file: str = "config.json") -> bool:
    """Yapılandırmayı kaydet"""
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        logging.debug(f"Yapılandırma kaydedildi: {config_file}")
        return True
    except Exception as e:
        logging.error(f"Yapılandırma kaydedilemedi: {e}")
        return False

# --- Kullanıcı Verisi Yönetimi ---
def load_user_data() -> Dict[str, Any]:
    """Kullanıcı verilerini yükle"""
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Kullanıcı verisi yüklenemedi: {e}")
        
    return {"license_key": "", "last_update_check": 0, "user_preferences": {}}

def save_user_data(data: Dict[str, Any]) -> bool:
    """Kullanıcı verilerini kaydet"""
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Kullanıcı verisi kaydedilemedi: {e}")
        return False

# --- Lisans Yönetimi ---
def check_license_status(license_key: str) -> Dict[str, Any]:
    """Online lisans kontrolü"""
    try:
        response = requests.post(LICENSE_API_URL, 
                               data={"license_key": license_key, "action": "check"},
                               timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Lisans API hatası: {response.status_code}")
            
    except requests.RequestException as e:
        logging.error(f"Lisans kontrolü ağ hatası: {e}")
    except Exception as e:
        logging.error(f"Lisans kontrolü hatası: {e}")
        
    return {"status": "error", "message": "Lisans kontrolü başarısız"}

def activate_license_code(license_key: str) -> Dict[str, Any]:
    """Lisans kodunu aktive et"""
    try:
        response = requests.post(LICENSE_API_URL,
                               data={"license_key": license_key, "action": "activate"},
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                # Başarılı aktivasyon sonrası kullanıcı verisini güncelle
                user_data = load_user_data()
                user_data["license_key"] = license_key
                user_data["activation_date"] = datetime.datetime.now().isoformat()
                save_user_data(user_data)
                
            return result
            
    except Exception as e:
        logging.error(f"Lisans aktivasyon hatası: {e}")
        
    return {"status": "error", "message": "Aktivasyon başarısız"}

def is_license_active_locally() -> bool:
    """Yerel lisans kontrolü"""
    try:
        user_data = load_user_data()
        license_key = user_data.get("license_key", "")
        
        if not license_key:
            return False
            
        # Basit yerel kontrol (gerçek uygulamada daha karmaşık olabilir)
        activation_date = user_data.get("activation_date")
        if activation_date:
            activation_dt = datetime.datetime.fromisoformat(activation_date)
            days_since_activation = (datetime.datetime.now() - activation_dt).days
            
            # 30 gün geçerlilik (örnek)
            return days_since_activation < 30
            
    except Exception as e:
        logging.error(f"Yerel lisans kontrolü hatası: {e}")
        
    return False

# --- Güncelleme Yönetimi ---
def check_for_updates() -> Dict[str, Any]:
    """Güncelleme kontrolü"""
    try:
        from version import __version__
        
        response = requests.get("https://polychaser.com/bot_api/version_check.php", 
                              params={"current_version": __version__},
                              timeout=10)
        
        if response.status_code == 200:
            update_info = response.json()
            
            # Son kontrol zamanını kaydet
            user_data = load_user_data()
            user_data["last_update_check"] = time.time()
            save_user_data(user_data)
            
            return update_info
            
    except Exception as e:
        logging.error(f"Güncelleme kontrolü hatası: {e}")
        
    return {"status": "error", "message": "Güncelleme kontrolü başarısız"}

def download_update(download_url: str, filename: str) -> bool:
    """Güncellemeyi indir"""
    try:
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        logging.info(f"Güncelleme indirildi: {filename}")
        return True
        
    except Exception as e:
        logging.error(f"Güncelleme indirme hatası: {e}")
        return False

def prepare_update_and_launch_updater() -> bool:
    """Güncellemeyi hazırla ve updater'ı başlat"""
    try:
        updater_path = get_resource_path(UPDATER_EXE_NAME)
        
        if os.path.exists(updater_path):
            subprocess.Popen([updater_path], shell=True)
            logging.info("Updater başlatıldı")
            return True
        else:
            logging.error(f"Updater bulunamadı: {updater_path}")
            
    except Exception as e:
        logging.error(f"Updater başlatma hatası: {e}")
        
    return False

# --- Sistem Optimizasyonu ---
def optimize_system_for_bot() -> bool:
    """Bot için sistem optimizasyonu"""
    try:
        # Yüksek DPI farkındalığı
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
            
        # PyAutoGUI optimizasyonları
        pyautogui.PAUSE = 0.05  # Daha hızlı işlem
        pyautogui.FAILSAFE = True  # Güvenlik
        
        # OpenCV optimizasyonları
        cv2.setUseOptimized(True)
        cv2.setNumThreads(4)
        
        logging.info("Sistem optimizasyonu tamamlandı")
        return True
        
    except Exception as e:
        logging.error(f"Sistem optimizasyon hatası: {e}")
        return False

def get_system_info() -> Dict[str, Any]:
    """Sistem bilgilerini al"""
    try:
        info = {
            "os": os.name,
            "python_version": sys.version,
            "screen_size": pyautogui.size(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent
        }
        
        # Windows özel bilgiler
        if os.name == 'nt':
            try:
                import platform
                info["windows_version"] = platform.version()
                info["windows_architecture"] = platform.architecture()[0]
            except:
                pass
                
        return info
        
    except Exception as e:
        logging.error(f"Sistem bilgisi alma hatası: {e}")
        return {}

# --- Hata Yönetimi ---
def handle_error_and_notify(error_message: str, log_level: int = logging.ERROR, 
                          show_popup: bool = False) -> None:
    """Hata yönetimi ve bildirim"""
    logging.log(log_level, error_message)
    
    if show_popup:
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Hata", error_message)
        except:
            pass

def save_error_log(error_info: Dict[str, Any], filename: str = "error_log.json") -> bool:
    """Hata logunu kaydet"""
    try:
        error_info["timestamp"] = datetime.datetime.now().isoformat()
        error_info["system_info"] = get_system_info()
        
        # Mevcut logları yükle
        logs = []
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                logs = json.load(f)
                
        # Yeni log'u ekle
        logs.append(error_info)
        
        # Son 100 log'u sakla
        logs = logs[-100:]
        
        # Kaydet
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)
            
        return True
        
    except Exception as e:
        logging.error(f"Hata logu kaydedilemedi: {e}")
        return False

# --- URL ve Sosyal Medya ---
def open_url(url: str) -> bool:
    """URL'yi varsayılan tarayıcıda aç"""
    try:
        webbrowser.open(url)
        logging.info(f"URL açıldı: {url}")
        return True
    except Exception as e:
        logging.error(f"URL açma hatası: {e}")
        return False

def open_discord():
    """Discord sunucusunu aç"""
    return open_url(DISCORD_URL)

def open_telegram():
    """Telegram kanalını aç"""
    return open_url(TELEGRAM_URL)

# --- Gelişmiş Görüntü İşleme ---
def enhance_image_for_recognition(image_path: str) -> Optional[str]:
    """Görüntü tanıma için görüntüyü iyileştir"""
    try:
        # Özgün görüntüyü yükle
        image = cv2.imread(image_path)
        if image is None:
            return None
            
        # Görüntü iyileştirme teknikleri
        # 1. Gürültü azaltma
        denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        
        # 2. Keskinlik artırma
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        # 3. Kontrast iyileştirme
        lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        enhanced = cv2.merge((cl,a,b))
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        # İyileştirilmiş görüntüyü kaydet
        enhanced_path = image_path.replace('.png', '_enhanced.png').replace('.jpg', '_enhanced.jpg')
        cv2.imwrite(enhanced_path, enhanced)
        
        return enhanced_path
        
    except Exception as e:
        logging.error(f"Görüntü iyileştirme hatası: {e}")
        return None

def create_image_variants(image_path: str) -> List[str]:
    """Görüntünün farklı varyantlarını oluştur (farklı boyutlar, renkler)"""
    variants = []
    
    try:
        image = cv2.imread(image_path)
        if image is None:
            return variants
            
        base_name = os.path.splitext(image_path)[0]
        
        # Boyut varyantları
        for scale in [0.8, 0.9, 1.1, 1.2]:
            height, width = image.shape[:2]
            new_width = int(width * scale)
            new_height = int(height * scale)
            resized = cv2.resize(image, (new_width, new_height))
            
            variant_path = f"{base_name}_scale_{scale}.png"
            cv2.imwrite(variant_path, resized)
            variants.append(variant_path)
            
        # Renk varyantları
        # Parlaklık ayarı
        for brightness in [-20, -10, 10, 20]:
            bright_image = cv2.convertScaleAbs(image, alpha=1, beta=brightness)
            variant_path = f"{base_name}_bright_{brightness}.png"
            cv2.imwrite(variant_path, bright_image)
            variants.append(variant_path)
            
    except Exception as e:
        logging.error(f"Görüntü varyant oluşturma hatası: {e}")
        
    return variants

# --- Güncelleme Notları ---
def save_last_shown_update_note_version(version: str) -> bool:
    """Son gösterilen güncelleme notu sürümünü kaydet"""
    try:
        user_data = load_user_data()
        user_data["last_shown_update_note_version"] = version
        return save_user_data(user_data)
    except Exception as e:
        logging.error(f"Güncelleme notu sürümü kaydedilemedi: {e}")
        return False

def load_last_shown_update_note_version() -> str:
    """Son gösterilen güncelleme notu sürümünü yükle"""
    try:
        user_data = load_user_data()
        return user_data.get("last_shown_update_note_version", "0.0.0")
    except Exception as e:
        logging.error(f"Güncelleme notu sürümü yüklenemedi: {e}")
        return "0.0.0"

# --- Performans Monitoring ---
class PerformanceMonitor:
    """Performans izleme sınıfı"""
    
    def __init__(self):
        self.start_times = {}
        self.performance_data = {}
        
    def start_timer(self, operation_name: str):
        """Operasyon timer'ını başlat"""
        self.start_times[operation_name] = time.time()
        
    def end_timer(self, operation_name: str) -> float:
        """Operasyon timer'ını bitir ve süreyi döndür"""
        if operation_name in self.start_times:
            duration = time.time() - self.start_times[operation_name]
            
            if operation_name not in self.performance_data:
                self.performance_data[operation_name] = []
                
            self.performance_data[operation_name].append(duration)
            
            # Son 100 kaydı sakla
            self.performance_data[operation_name] = self.performance_data[operation_name][-100:]
            
            del self.start_times[operation_name]
            return duration
            
        return 0.0
        
    def get_average_time(self, operation_name: str) -> float:
        """Operasyon ortalama süresini al"""
        if operation_name in self.performance_data and self.performance_data[operation_name]:
            return sum(self.performance_data[operation_name]) / len(self.performance_data[operation_name])
        return 0.0
        
    def get_performance_report(self) -> Dict[str, Dict[str, float]]:
        """Performans raporu al"""
        report = {}
        
        for operation_name, times in self.performance_data.items():
            if times:
                report[operation_name] = {
                    'average': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'count': len(times)
                }
                
        return report

# Global performance monitor
performance_monitor = PerformanceMonitor()

# Uygulama başlangıcında sistem optimizasyonu yap
optimize_system_for_bot()
