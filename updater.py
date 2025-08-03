import sys
import os
import time
import shutil
import subprocess
import logging

# Güncelleyici için temel loglama yapılandırması
# Bu loglar, ana botun loglarından ayrı olarak 'updater_log.log' dosyasına yazılacaktır.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - UPDATER - %(levelname)s - %(message)s', filename='updater_log.log', filemode='a')

def run_updater():
    logging.info("Updater başlatıldı.")

    # Argümanları kontrol et: <ana_uygulama_dizini> <yeni_dosyalar_dizini>
    if len(sys.argv) < 3:
        logging.error("Kullanım hatası: updater.exe <ana_uygulama_dizini> <yeni_dosyalar_dizini>")
        logging.error(f"Alınan argümanlar: {sys.argv}")
        time.sleep(5) # Hata mesajının kullanıcı tarafından görülmesi için kısa bir bekleme
        sys.exit(1)

    app_dir = sys.argv[1] # Ana uygulamanın çalıştığı dizin
    new_files_dir = sys.argv[2] # Yeni indirilen ve çıkarılan dosyaların geçici dizini
    main_exe_name = "King Bot Pro.exe" # Ana uygulamanın adı
    main_exe_path = os.path.join(app_dir, main_exe_name) # Ana uygulamanın tam yolu

    logging.info(f"Ana uygulama dizini: {app_dir}")
    logging.info(f"Yeni dosyalar dizini: {new_files_dir}")
    logging.info(f"Ana uygulamanın adı: {main_exe_name}")

    # Ana uygulamanın tamamen kapanmasını bekle
    # Bu, dosya kilitlenmelerini önlemek için kritik öneme sahiptir.
    max_wait_time = 30 # saniye
    wait_interval = 1 # saniye
    logging.info(f"'{main_exe_name}' uygulamasının kapanması bekleniyor (maksimum {max_wait_time} saniye)...")
    for i in range(max_wait_time // wait_interval):
        if not is_process_running(main_exe_name):
            logging.info(f"'{main_exe_name}' kapandı.")
            break
        logging.info(f"'{main_exe_name}' hala çalışıyor... ({i+1}/{max_wait_time // wait_interval})")
        time.sleep(wait_interval)
    else:
        logging.error(f"'{main_exe_name}' belirlenen süre içinde kapanmadı. Güncelleme iptal ediliyor.")
        # Hata durumunda geçici dizinleri temizlemeden çıkış yap, manuel müdahale gerekebilir.
        sys.exit(1)

    # Mevcut uygulama dosyalarını sil
    # Ana .exe'yi silmek, üzerine yazma sorunlarını azaltır.
    logging.info(f"Eski '{main_exe_name}' siliniyor: {main_exe_path}")
    try:
        if os.path.exists(main_exe_path):
            os.remove(main_exe_path)
            logging.info(f"Eski '{main_exe_name}' başarıyla silindi.")
    except OSError as e:
        logging.error(f"Eski '{main_exe_name}' silinirken hata oluştu: {e}. Lütfen uygulamayı manuel olarak kapatın ve yeniden deneyin.")
        time.sleep(5) # Hata mesajının görünmesi için bekle
        sys.exit(1)

    # Yeni dosyaları ana uygulama dizinine kopyala
    logging.info(f"Yeni dosyalar kopyalanıyor: '{new_files_dir}' konumundan '{app_dir}' konumuna.")
    try:
        # shutil.copytree, hedef dizin zaten varsa hata verir.
        # Bu yüzden, yeni_files_dir içindeki her şeyi app_dir'e kopyalamak daha güvenlidir.
        for item in os.listdir(new_files_dir):
            s = os.path.join(new_files_dir, item)
            d = os.path.join(app_dir, item)
            if os.path.isdir(s):
                # Eğer hedef dizin varsa önce sil, sonra kopyala
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                # Dosya ise doğrudan kopyala (üzerine yazacaktır)
                shutil.copy2(s, d) # copy2, dosya meta verilerini de kopyalar (örn. oluşturulma tarihi)
        logging.info("Tüm yeni dosyalar başarıyla kopyalandı.")

    except Exception as e:
        logging.error(f"Yeni dosyalar kopyalanırken hata oluştu: {e}")
        time.sleep(5) # Hata mesajının görünmesi için bekle
        sys.exit(1)

    # Geçici dizinleri temizle
    logging.info(f"Geçici dizin temizleniyor: {new_files_dir}")
    try:
        shutil.rmtree(new_files_dir)
        logging.info("Geçici dizin başarıyla silindi.")
    except Exception as e:
        logging.warning(f"Geçici dizin silinirken hata oluştu: {e}")

    # Güncellenmiş uygulamayı başlat
    logging.info(f"Güncellenmiş '{main_exe_name}' başlatılıyor: {main_exe_path}")
    try:
        # subprocess.Popen ile yeni uygulamayı başlat ve bu updater'ın işini bitir.
        # Windows'ta DETACHED_PROCESS ve CREATE_NEW_PROCESS_GROUP bayrakları,
        # yeni sürecin bu updater'dan bağımsız çalışmasını sağlar.
        subprocess.Popen([main_exe_path], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
        logging.info("Güncellenmiş uygulama başarıyla başlatıldı.")
    except Exception as e:
        logging.error(f"Güncellenmiş uygulama başlatılırken hata: {e}")
        time.sleep(5) # Hata mesajının görünmesi için bekle
        sys.exit(1)

    logging.info("Updater görevi tamamlandı. Çıkış yapılıyor.")
    sys.exit(0) # Başarılı çıkış

def is_process_running(process_name):
    """Belirtilen isimde bir işlemin çalışıp çalışmadığını kontrol eder (Windows için)."""
    try:
        # tasklist komutunu kullanarak işlemi kontrol et
        # /FI "IMAGENAME eq <process_name>" ile sadece belirli bir isimdeki işlemi filtrele
        # findstr /I <process_name> ile büyük/küçük harf duyarsız arama yap
        # Eğer işlem bulunursa ERRORLEVEL 0 döner, aksi takdirde 1
        # CREATE_NO_WINDOW: Komut istemi penceresinin açılmasını engeller.
        output = subprocess.check_output(['tasklist', '/FI', f'IMAGENAME eq {process_name}'], creationflags=subprocess.CREATE_NO_WINDOW)
        return process_name.lower() in output.decode().lower()
    except subprocess.CalledProcessError:
        # tasklist işlemi bulamazsa bu hatayı fırlatır, yani işlem çalışmıyor demektir.
        return False
    except Exception as e:
        logging.error(f"İşlem kontrolü sırasında hata: {e}")
        return False

if __name__ == "__main__":
    run_updater()
