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
import subprocess # Harici komutları çalıştırmak için eklendi
import shutil # Dosya işlemleri için eklendi

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
# Yeni bot adı ve güncelleyici adı sabitleri
BOT_EXE_NAME = "King Bot Pro.exe"
UPDATER_EXE_NAME = "King Bot Pro Updater.exe"

# Sosyal Medya Linkleri
DISCORD_URL = "https://discord.gg/pJ8Sf464"
TELEGRAM_URL = "https://t.me/+wHPg9nJt1qljMDFk"

# --- Kaynak Yolu Yönetimi ---
def get_resource_path(relative_path):
    """
    PyInstaller tarafından paketlenmiş uygulamalar için kaynak dosyalarının
    mutlak yolunu döndürür.
    """
    try:
        base_path = sys._MEIPASS
        logging.debug(f"PyInstaller _MEIPASS yolu kullanılıyor: {base_path}")
    except AttributeError:
        base_path = os.path.abspath(".")
        logging.debug(f"Normal Python yolu kullanılıyor: {base_path}")
    
    full_path = os.path.join(base_path, relative_path)
    logging.debug(f"Kaynak yolu çözüldü: {relative_path} -> {full_path}")
    return full_path

# --- PyAutoGUI Yardımcı Fonksiyonlar ---
def try_click(image_path_relative, region, max_attempts=3, confidence=0.9):
    """
    Belirtilen görseli ekranda bulmaya ve tıklamaya çalışır.
    Verilen confidence değerinden başlayarak azalan güven seviyeleriyle dener.
    """
    image_path = get_resource_path(image_path_relative)
    
    for attempt in range(max_attempts):
        current_confidence = confidence - (attempt * 0.05)
        if current_confidence < 0.5: # Makul bir alt sınır belirle
            break
            
        try:
            location = pyautogui.locateCenterOnScreen(image_path, region=region, confidence=current_confidence)
            if location:
                logging.info(f"'{image_path_relative}' görseli bulundu ve tıklandı (Güven: {current_confidence:.2f}). Konum: {location}")
                pyautogui.click(location)
                time.sleep(1.5)
                return True
        except pyautogui.ImageNotFoundException:
            logging.debug(f"'{image_path_relative}' görseli bulunamadı (Deneme {attempt+1}/{max_attempts}, Güven: {current_confidence:.2f}).")
            time.sleep(0.5)
            continue
        except Exception as e:
            logging.error(f"'{image_path_relative}' görseline tıklanırken beklenmeyen hata: {e}")
            return False
    
    logging.warning(f"'{image_path_relative}' görseli {max_attempts} denemede bulunamadı.")
    return False

def get_mouse_position():
    """Mevcut fare imleci konumunu döndürür."""
    pos = pyautogui.position()
    logging.info(f"Fare konumu alındı: X={pos.x}, Y={pos.y}")
    return pos

def find_image_location(image_path_relative, region, confidence=0.8):
    """
    Belirtilen görselin ekran üzerindeki merkez koordinatlarını bulur.
    Görsel yolu için get_resource_path kullanılır.
    """
    image_path = get_resource_path(image_path_relative)
    try:
        location = pyautogui.locateCenterOnScreen(image_path, region=region, confidence=confidence)
        if location:
            logging.info(f"'{image_path_relative}' görselinin merkezi bulundu: {location}")
            return location
        else:
            logging.debug(f"'{image_path_relative}' görseli belirtilen bölgede bulunamadı.")
            return None
    except pyautogui.ImageNotFoundException:
        logging.debug(f"'{image_path_relative}' görseli ekranda bulunamadı.")
        return None
    except Exception as e:
        logging.error(f"'{image_path_relative}' görseli aranırken beklenmeyen hata: {e}")
        return None

def click_sequence(image_keys, image_paths, region, base_confidence=0.8, sleep_after_click=1.5, log_prefix=""):
    """
    Bir dizi görseli sırayla bulup tıklamaya çalışır.
    Her bir görsel için try_click fonksiyonunu kullanır.
    """
    action_performed = False
    for key in image_keys:
        logging.info(f"[{log_prefix}] '{key}.png' aranıyor...")
        
        image_full_path = image_paths.get(key)
        if not image_full_path or not os.path.exists(image_full_path):
            logging.warning(f"[{log_prefix}] Resim yolu bulunamadı veya geçersiz: {key}")
            continue

        if try_click(image_full_path, region, max_attempts=4, confidence=base_confidence):
            action_performed = True
            time.sleep(sleep_after_click)
        else:
            logging.warning(f"[{log_prefix}] '{key}.png' bulunamadı ve tıklanamadı.")
            # Eğer bir adım başarısız olursa tüm sekansı durdurmak istiyorsanız:
            # return False
            
    if not action_performed:
        logging.warning(f"[{log_prefix}] Dizideki hiçbir görsel bulunamadı.")
        
    return action_performed

# --- Yapılandırma ve Kullanıcı Verileri Yönetimi ---
def save_config(config):
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        logging.info("Ayarlar 'config.json' dosyasına başarıyla kaydedildi.")
    except IOError as e:
        logging.error(f"Ayarlar 'config.json' dosyasına kaydedilirken I/O hatası: {e}")
    except Exception as e:
        logging.error(f"Ayarlar 'config.json' dosyasına kaydedilirken beklenmeyen hata: {e}")

def load_config():
    if os.path.exists('config.json'):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            logging.info("Ayarlar 'config.json' dosyasından başarıyla yüklendi.")
            return config
        except json.JSONDecodeError:
            logging.error("Ayarlar dosyası 'config.json' geçersiz JSON içeriyor. Boş ayarlar döndürülüyor.")
            return {}
        except IOError as e:
            logging.error(f"Ayarlar 'config.json' dosyasından yüklenirken I/O hatası: {e}")
            return {}
        except Exception as e:
            logging.error(f"Ayarlar 'config.json' dosyasından yüklenirken beklenmeyen hata: {e}")
            return {}
    logging.info("'config.json' dosyası bulunamadı. Boş ayarlar döndürülüyor.")
    return {}

def save_user_data(user_data):
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(user_data, f, indent=4)
        logging.info(f"Kullanıcı verileri '{USER_DATA_FILE}' dosyasına başarıyla kaydedildi.")
    except IOError as e:
        logging.error(f"Kullanıcı verileri '{USER_DATA_FILE}' dosyasına kaydedilirken I/O hatası: {e}")
    except Exception as e:
        logging.error(f"Kullanıcı verileri '{USER_DATA_FILE}' dosyasına kaydedilirken beklenmeyen hata: {e}")

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                data = json.load(f)
            logging.info(f"Kullanıcı verileri '{USER_DATA_FILE}' dosyasından başarıyla yüklendi.")
            return data
        except json.JSONDecodeError:
            logging.error(f"Kullanıcı veri dosyası '{USER_DATA_FILE}' geçersiz JSON içeriyor. Boş veri döndürülüyor.")
            return {}
        except IOError as e:
            logging.error(f"Kullanıcı verileri '{USER_DATA_FILE}' dosyasından yüklenirken I/O hatası: {e}")
            return {}
        except Exception as e:
            logging.error(f"Kullanıcı verileri '{USER_DATA_FILE}' dosyasından yüklenirken beklenmeyen hata: {e}")
            return {}
    logging.info(f"'{USER_DATA_FILE}' dosyası bulunamadı. Boş veri döndürülüyor.")
    return {}

def save_last_shown_update_note_version(version):
    """
    Kullanıcının güncelleme notlarını 'tekrar gösterme' olarak işaretlediği son sürümü kaydeder.
    """
    user_data = load_user_data()
    user_data['last_shown_update_note_version'] = version
    save_user_data(user_data)
    logging.info(f"Son gösterilen güncelleme notu sürümü kaydedildi: {version}")

def load_last_shown_update_note_version():
    """
    Kullanıcının 'tekrar gösterme' olarak işaretlediği son güncelleme notu sürümünü yükler.
    """
    user_data = load_user_data()
    version = user_data.get('last_shown_update_note_version', '0.0.0')
    logging.info(f"Yüklenen son gösterilen güncelleme notu sürümü: {version}")
    return version

# --- Uygulama Güncelleme Fonksiyonları ---

def check_for_updates(current_version):
    try:
        response = requests.get("https://polychaser.com/version.json", timeout=5) 
        response.raise_for_status() 
        latest_release_info = response.json()
        
        latest_version = latest_release_info.get("latest_version")
        download_url = latest_release_info.get("download_url")
        release_notes = latest_release_info.get("release_notes", "Sürüm notu yok.")

        if not latest_version or not download_url:
            logging.warning("Güncelleme bilgisi JSON'u eksik veya hatalı (latest_version veya download_url bulunamadı).")
            return None

        current_major, current_minor, current_patch = map(int, current_version.split('.'))
        latest_major, latest_minor, latest_patch = map(int, latest_version.split('.'))

        if (latest_major > current_major or
            (latest_major == current_major and latest_minor > current_minor) or
            (latest_major == current_major and latest_minor == current_minor and latest_patch > current_patch)):
            
            logging.info(f"Yeni sürüm bulundu: {latest_version} (Mevcut: {current_version})")
            return {
                "latest_version": latest_version,
                "download_url": download_url,
                "release_notes": release_notes
            }
        logging.info(f"Uygulama zaten güncel (Mevcut: {current_version}, En Son: {latest_version}).")
    except requests.exceptions.Timeout:
        logging.error("Güncelleme kontrolü zaman aşımına uğradı. İnternet bağlantınızı kontrol edin.")
    except requests.exceptions.ConnectionError:
        logging.error("Güncelleme sunucusuna bağlanılamadı. İnternet bağlantınızı kontrol edin.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Güncelleme kontrolü sırasında ağ hatası oluştu: {e}") 
    except json.JSONDecodeError:
        logging.error("Güncelleme bilgisi okunurken hata: Geçersiz JSON yanıtı alındı.") 
    except ValueError:
        logging.error(f"Versiyon formatı hatası. Mevcut: '{current_version}', En son: '{latest_version}'")
    except Exception as e:
        logging.error(f"Güncelleme kontrolünde beklenmeyen bir hata oluştu: {e}") 
    return None

def prepare_update_and_launch_updater(download_url, progress_callback=None):
    """
    Güncelleme zip dosyasını indirir, geçici bir dizine çıkarır ve ardından
    updater.exe'yi başlatarak ana uygulamayı kapatır.
    """
    current_app_dir = os.getcwd() # Ana uygulamanın çalıştığı dizin
    
    # Geçici dizinler oluştur
    # TEMP veya TMP ortam değişkenlerini kullan, yoksa '/tmp' (Linux/macOS) veya 'temp' (Windows) kullan
    temp_base_dir = os.environ.get('TEMP') or os.environ.get('TMP') or (os.path.join(os.getcwd(), 'temp_update_files') if os.name == 'nt' else '/tmp')
    temp_download_dir = os.path.join(temp_base_dir, 'kingbot_temp_download')
    temp_extract_dir = os.path.join(temp_base_dir, 'kingbot_temp_extract')

    # Önceki çalıştırmalardan kalmış olabilecek geçici dizinleri güvenli bir şekilde temizle
    for temp_dir in [temp_download_dir, temp_extract_dir]:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logging.info(f"Geçici dizin temizlendi: {temp_dir}")
            except OSError as e:
                logging.warning(f"Geçici dizin temizlenirken hata (muhtemelen kullanımda): {temp_dir} - {e}")
            except Exception as e:
                logging.error(f"Geçici dizin temizlenirken beklenmeyen hata: {temp_dir} - {e}")

    # Yeni geçici dizinleri oluştur
    os.makedirs(temp_download_dir, exist_ok=True)
    os.makedirs(temp_extract_dir, exist_ok=True)

    zip_file_name = "update.zip"
    download_path = os.path.join(temp_download_dir, zip_file_name) 
    
    try:
        logging.info(f"Güncelleme zip dosyası indiriliyor: {download_url} -> {download_path}")
        response = requests.get(download_url, stream=True, timeout=30) 
        response.raise_for_status() # HTTP hataları için istisna fırlat

        total_size = int(response.headers.get('content-length', 0))
        bytes_downloaded = 0

        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if not chunk:
                    break
                f.write(chunk)
                bytes_downloaded += len(chunk)
                if progress_callback:
                    # İndirme ilerlemesini UI'a gönder
                    progress_callback(bytes_downloaded, total_size)
        
        logging.info(f"'{zip_file_name}' dosyası başarıyla indirildi. Şimdi '{temp_extract_dir}' konumuna çıkarılıyor...")
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)
        logging.info(f"'{zip_file_name}' başarıyla '{temp_extract_dir}' konumuna çıkarıldı.")

        # İndirilen zip dosyasını sil (artık çıkarıldığı için gerek yok)
        os.remove(download_path)
        logging.info(f"İndirilen zip dosyası silindi: {download_path}")

        # Updater.exe'nin çıkarılan dizinde olup olmadığını kontrol et
        updater_path_in_temp = os.path.join(temp_extract_dir, UPDATER_EXE_NAME)
        if not os.path.exists(updater_path_in_temp):
            logging.error(f"Updater.exe ({UPDATER_EXE_NAME}) çıkarılan dizinde bulunamadı: {temp_extract_dir}. Güncelleme başarısız.")
            handle_error_and_notify(f"Güncelleyici dosyası ({UPDATER_EXE_NAME}) güncelleme paketinde bulunamadı. Lütfen geliştiriciyle iletişime geçin.", notify_user=True)
            return False

        # Updater.exe'yi başlat ve ana uygulama dizinini ve yeni dosyaların dizinini argüman olarak geçir
        logging.info(f"Updater başlatılıyor: '{updater_path_in_temp}' ile argümanlar: '{current_app_dir}' ve '{temp_extract_dir}'")
        
        # subprocess.Popen ile yeni uygulamayı başlat ve bu updater'ın işini bitir.
        # Windows'ta DETACHED_PROCESS ve CREATE_NEW_PROCESS_GROUP bayrakları,
        # yeni sürecin bu updater'dan bağımsız çalışmasını sağlar.
        # Bu, ana uygulamanın kapanmasına izin verirken updater'ın arka planda çalışmasını sağlar.
        # UAC (User Account Control) yükseltmesi gerekebilir, bu durumda kullanıcıya sorulacaktır.
        subprocess.Popen([updater_path_in_temp, current_app_dir, temp_extract_dir], 
                         creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
        
        logging.info("Updater başarıyla başlatıldı. Ana uygulama kapatılıyor...")
        return True # Ana uygulamanın kapanması gerektiğini bildir
    
    except requests.exceptions.Timeout:
        logging.error("Güncelleme indirilirken zaman aşımı oluştu.")
        handle_error_and_notify("Güncelleme indirilirken zaman aşımı oluştu. İnternet bağlantınızı kontrol edin.", notify_user=True)
    except requests.exceptions.ConnectionError:
        logging.error("Güncelleme sunucusuna bağlanılamadı. İnternet bağlantınızı kontrol edin.")
        handle_error_and_notify("Güncelleme sunucusuna bağlanılamadı. İnternet bağlantınızı kontrol edin.", notify_user=True)
    except requests.exceptions.RequestException as e:
        logging.error(f"Güncelleme indirilirken ağ hatası oluştu: {e}") 
        handle_error_and_notify(f"Güncelleme indirilirken ağ hatası oluştu: {e}", notify_user=True)
    except zipfile.BadZipFile:
        logging.error("İndirilen dosya geçerli bir zip dosyası değil. Dosya bozuk olabilir.") 
        handle_error_and_notify("İndirilen güncelleme dosyası bozuk veya geçersiz.", notify_user=True)
        if os.path.exists(download_path): # Bozuk zip dosyasını sil
            os.remove(download_path) 
    except Exception as e:
        logging.error(f"Güncelleme hazırlanırken beklenmeyen bir hata oluştu: {e}") 
        handle_error_and_notify(f"Güncelleme hazırlanırken beklenmeyen bir hata oluştu: {e}", notify_user=True)
    
    finally:
        # Hata olsa bile geçici indirme dizinini temizlemeye çalış
        if os.path.exists(temp_download_dir):
            try:
                shutil.rmtree(temp_download_dir)
                logging.info(f"İndirme geçici dizini temizlendi (finally): {temp_download_dir}")
            except Exception as e:
                logging.warning(f"İndirme geçici dizini temizlenirken hata (finally): {e}")
        # Çıkarma dizinini updater.exe silmeli, burada silmiyoruz.
    return False

# --- LİSANS YÖNETİMİ FONKSİYONLARI (Değişiklik Yok) ---
def _make_license_api_request(action, license_code, api_key):
    if not api_key:
        logging.error("BOT_API_KEY tanımlanmamış. Lisans API isteği gönderilemiyor.")
        return {'status': 'error', 'message': 'Uygulama API Anahtarı eksik. Geliştirici ile iletişime geçin.'}

    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': api_key
    }
    payload = {'action': action, 'code': license_code}
    
    try:
        logging.info(f"Lisans API isteği gönderiliyor ({action}). URL: {LICENSE_API_URL}") 
        response = requests.post(LICENSE_API_URL, headers=headers, json=payload, timeout=10)
        
        logging.info(f"Lisans API yanıtı ({action}) - Durum Kodu: {response.status_code}, Yanıt Metni: {response.text}") 
        response.raise_for_status()

        result = response.json()
        return result
    except requests.exceptions.Timeout:
        logging.error(f"Lisans API isteği zaman aşımına uğradı ({action}).") 
        return {'status': 'error', 'message': 'API isteği zaman aşımına uğradı. İnternet bağlantınızı kontrol edin.'}
    except requests.exceptions.ConnectionError:
        logging.error(f"Lisans API'sine bağlanılamadı ({action}).")
        return {'status': 'error', 'message': 'API sunucusuna bağlanılamadı. İnternet bağlantınızı kontrol edin.'}
    except requests.exceptions.HTTPError as e:
        logging.error(f"Lisans API'den HTTP hatası alındı ({action}): {e.response.status_code} - {e.response.text}")
        try:
            error_json = e.response.json()
            return {'status': 'error', 'message': error_json.get('message', 'API sunucusundan bir hata alındı.')}
        except json.JSONDecodeError:
            return {'status': 'error', 'message': f'API sunucusundan hata alındı, ancak yanıt çözümlenemedi. Durum: {e.response.status_code}'}
    except json.JSONDecodeError:
        logging.error(f"Lisans API'den geçersiz JSON yanıtı alındı ({action}). Yanıt: {response.text}") 
        return {'status': 'error', 'message': "API'den geçersiz cevap alındı (JSON hatası)."}
    except Exception as e:
        logging.error(f"Lisans API isteğinde beklenmeyen hata ({action}): {e}") 
        return {'status': 'error', 'message': f"Beklenmeyen bir hata oluştu: {e}"}

def activate_license_code(license_code, api_key):
    # Lisans sistemi kaldırıldı - her zaman başarılı
    future_date = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
    return {
        'status': 'success',
        'message': 'Lisans başarıyla aktive edildi (Lisanssız sürüm)',
        'expiration_date': future_date
    }

def check_license_status(license_code, api_key):
    # Lisans sistemi kaldırıldı - her zaman başarılı
    future_date = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
    return {
        'status': 'success',
        'message': 'Lisans aktif (Lisanssız sürüm)',
        'expiration_date': future_date
    }

def is_license_active_locally(license_data):
    # Lisans sistemi kaldırıldı - her zaman aktif
    logging.info("Lisans sistemi kaldırıldı - bot lisanssız çalışıyor.")
    return True, "Aktif (Lisanssız Sürüm)"

def open_url(url):
    """Belirtilen URL'yi varsayılan web tarayıcısında açar."""
    try:
        webbrowser.open_new_tab(url)
        logging.info(f"URL açıldı: {url}")
    except Exception as e:
        logging.error(f"URL açılırken hata oluştu: {url} - {e}")

def handle_error_and_notify(error_message, log_level=logging.ERROR, notify_user=False, contact_discord=False, contact_telegram=False):
    """
    Hataları loglar ve isteğe bağlı olarak kullanıcıya bildirim gösterir veya
    sosyal medya linklerini açar.
    """
    logging.log(log_level, error_message)
    if notify_user:
        import tkinter as tk
        from tkinter import messagebox
        if tk._default_root is not None:
            tk._default_root.after(0, lambda: messagebox.showerror("Hata!", error_message))
        else:
            messagebox.showerror("Hata!", error_message)

    if contact_discord:
        open_url(DISCORD_URL)
    if contact_telegram:
        open_url(TELEGRAM_URL)
