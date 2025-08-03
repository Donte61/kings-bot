import os
import time
import random
import pyautogui
import logging
from utils import try_click, find_image_location, click_sequence

def perform_healing_sequence(game_area_region, image_paths, confidence=0.7):
    log_prefix = "İyileştirme"
    logging.info(f"[{log_prefix}] Dizisi başlatıldı")
    
    # Öncelikli olarak hprec1'i dene, başarılı olursa hemen çık
    if try_click(image_paths['hprec1'], game_area_region, max_attempts=1, confidence=confidence):
        logging.info(f"[{log_prefix}] Öncelikli iyileştirme ('hprec1') başarılı.")
        return True

    # Ana iyileştirme akışı
    if try_click(image_paths['heal1'], game_area_region, max_attempts=1, confidence=confidence):
        time.sleep(0.2)
        click_sequence(['iyilestir', 'hphelp', 'helpme'], image_paths, game_area_region, confidence, 0.2, log_prefix)
        return True

    logging.warning(f"[{log_prefix}] Hiçbir iyileştirme görseli bulunamadı.")
    return False

def perform_daily_tasks(game_area_region, image_paths, confidence=0.8):
    log_prefix = "Günlük Görevler"
    logging.info(f"[{log_prefix}] Dizisi başlatıldı")
    
    if try_click(image_paths['et_ambar'], game_area_region, max_attempts=1, confidence=confidence):
        time.sleep(2)
        if try_click(image_paths['et_topla'], game_area_region, max_attempts=1, confidence=confidence):
            logging.info(f"[{log_prefix}] Et toplama başarılı.")
            return True
    
    logging.warning(f"[{log_prefix}] Hiçbir günlük görev görseli bulunamadı.")
    return False

def perform_kutu_sequence(game_area_region, image_paths, confidence=0.8):
    log_prefix = "Kutu"
    logging.info(f"[{log_prefix}] Dizisi başlatıldı")
    
    if try_click(image_paths['kutu'], game_area_region, max_attempts=1, confidence=confidence):
        logging.info(f"[{log_prefix}] Kutu açıldı.")
        return True
        
    logging.warning(f"[{log_prefix}] Kutu görseli bulunamadı.")
    return False

def perform_anahtar_sequence(game_area_region, image_paths, confidence=0.8):
    log_prefix = "Anahtar"
    logging.info(f"[{log_prefix}] Dizisi başlatıldı")
    
    if try_click(image_paths['anahtar1'], game_area_region, max_attempts=1, confidence=confidence):
        time.sleep(2)
        click_sequence(['anahtar2', 'anahtarback', 'anahtarback2'], image_paths, game_area_region, confidence, 1.5, log_prefix)
        return True

    logging.warning(f"[{log_prefix}] Hiçbir anahtar görseli bulunamadı.")
    return False

def perform_asker_hasat_sequence(game_area_region, image_paths, confidence=0.8):
    log_prefix = "Asker Hasat"
    logging.info(f"[{log_prefix}] Dizisi başlatıldı")
    action_performed = False
    
    for img_key in ['asker1', 'asker2', 'asker3']:
        if try_click(image_paths[img_key], game_area_region, max_attempts=2, confidence=confidence):
            action_performed = True
            time.sleep(1) # Bir sonraki hasat için kısa bekleme
            
    return action_performed

def perform_bekcikulesi_sequence(game_area_region, image_paths, confidence=0.8):
    log_prefix = "Bekçi Kulesi"
    logging.info(f"[{log_prefix}] Dizisi başlatıldı")
    images_to_click = [f'bekci{i}' for i in range(1, 10)]
    return click_sequence(images_to_click, image_paths, game_area_region, confidence, 2.0, log_prefix)

def perform_last_resort_click(game_area_region, last_resort_x=None, last_resort_y=None):
    logging.info("Son çare tıklaması gerçekleştiriliyor...")
    try:
        if last_resort_x is None or last_resort_y is None:
            left, top, width, height = game_area_region
            last_resort_x = left + width // 2
            last_resort_y = top + height // 2
        pyautogui.click(last_resort_x, last_resort_y)
        logging.info(f"Son çare tıklaması yapıldı ({last_resort_x}, {last_resort_y}).")
        time.sleep(1.5)
        return True
    except Exception as e:
        logging.error(f"Son çare tıklaması başarısız: {str(e)}")
        return False

def perform_recovery_sequence(game_area_region, image_paths, anaekran_image_paths, confidence=0.8, last_resort_x=None, last_resort_y=None):
    logging.info("Kurtarma dizisi başlatıldı...")

    # Önce ana ekranda mıyız kontrol et
    anaekran_bulundu = False
    for path in anaekran_image_paths:
        if path and os.path.exists(path):
            location = find_image_location(path, game_area_region, confidence=0.7)
            if location:
                logging.info(f"Zaten ana ekranda ({os.path.basename(path)}).")
                return True
            else:
                logging.warning(f"Ana ekran ({os.path.basename(path)}) görünmüyor.")
        else:
            logging.warning(f"Ana ekran dosyası eksik veya erişilemiyor: {path}")

    # Geri butonlarını sırayla dene
    back_buttons = [f'b{i}' for i in range(7, 0, -1)]
    for button in back_buttons:
        logging.info(f"[Kurtarma] '{button}.png' aranıyor...")
        if try_click(image_paths[button], game_area_region, max_attempts=2, confidence=confidence):
            time.sleep(1)
            for path in anaekran_image_paths:
                if path and os.path.exists(path):
                    location = find_image_location(path, game_area_region, confidence=0.7)
                    if location:
                        logging.info("Geri butonu ile ana ekrana dönüldü.")
                        return True
    
    # Son çare tıklaması
    logging.warning("Geri butonları başarısız, son çare tıklaması deneniyor...")
    if perform_last_resort_click(game_area_region, last_resort_x, last_resort_y):
        time.sleep(1)
        for path in anaekran_image_paths:
            if path and os.path.exists(path):
                location = find_image_location(path, game_area_region, confidence=0.7)
                if location:
                    logging.info("Son çare sonrası ana ekrana dönüldü.")
                    return True
    
    logging.error("Tüm kurtarma denemeleri başarısız oldu.")
    return False

def perform_askerbas_sequence(game_area_region, image_paths, confidence=0.8):
    log_prefix = "Asker Basma"
    logging.info(f"[{log_prefix}] Dizisi başlatıldı...")
    images_to_click = [f'askerbas{i}' for i in range(1, 5)]
    return click_sequence(images_to_click, image_paths, game_area_region, confidence, 1.5, log_prefix)

def perform_mesaj_sequence(game_area_region, image_paths, confidence=0.7):
    log_prefix = "Mesaj"
    logging.info(f"[{log_prefix}] Dizisi başlatıldı...")
    if try_click(image_paths['mesaj1'], game_area_region, max_attempts=1, confidence=confidence):
        time.sleep(1.5)
        click_sequence(['mesaj2', 'mesaj3', 'mesaj4', 'mesaj5'], image_paths, game_area_region, confidence, 1.5, log_prefix)
        # mesaj3'e tıkladıktan sonra hala ekrandaysa, bu genellikle bir pop-up veya bildirim olduğu anlamına gelir.
        # Onu kapatmak için tekrar tıklamak mantıklı olabilir.
        if find_image_location(image_paths['mesaj3'], game_area_region, confidence):
             try_click(image_paths['mesaj3'], game_area_region, max_attempts=1, confidence=confidence)
             logging.info(f"[{log_prefix}] Kapatma denemesi yapıldı.")
        return True
    
    logging.warning(f"[{log_prefix}] Hiçbir mesaj bulunamadı.")
    return False

def perform_savas_sequence(game_area_region, image_paths, confidence=0.6):
    log_prefix = "Savaş"
    logging.info(f"[{log_prefix}] Dizisi başlatıldı...")
    if try_click(image_paths['savas1'], game_area_region, max_attempts=1, confidence=confidence):
        time.sleep(1.5)
        images_to_click = [f'savas{i}' for i in range(2, 9)]
        return click_sequence(images_to_click, image_paths, game_area_region, confidence, 1.5, log_prefix)

    logging.warning(f"[{log_prefix}] Savaş menüsü bulunamadı.")
    return False

def perform_dunya_heal_sequence(game_area_region, image_paths, confidence=0.7):
    log_prefix = "Dünya Heal"
    logging.info(f"[{log_prefix}] Dizisi başlatıldı")
    return click_sequence(['h1', 'h2', 'h3'], image_paths, game_area_region, confidence, 0.2, log_prefix)

def perform_ittifak_sequence(game_area_region, image_paths, confidence=0.8, rapid_click_image=None, rapid_click_count=5):
    log_prefix = "İttifak"
    logging.info(f"[{log_prefix}] Dizisi başlatıldı...")
    images_to_click = [f'ittifak{i}' for i in range(1, 9)]
    
    action_performed = False
    for img_key in images_to_click:
        location = find_image_location(image_paths[img_key], game_area_region, confidence=confidence)
        if location:
            pyautogui.click(location)
            logging.info(f"[{log_prefix}] '{img_key}.png' tıklandı.")
            action_performed = True
            time.sleep(1.5)
            if rapid_click_image and img_key == rapid_click_image:
                logging.info(f"[{log_prefix}] {rapid_click_count} hızlı tıklama yapılıyor...")
                for _ in range(rapid_click_count - 1):
                    pyautogui.click(location)
                    time.sleep(0.1)
    return action_performed

def perform_isyanci_sequence(game_area_region, image_paths, confidence=0.7):
    log_prefix = "İsyancı"
    logging.info(f"[{log_prefix}] Dizisi başlatıldı")
    
    for conf in [0.7, 0.6, 0.5]:
        logging.info(f"[{log_prefix}] s1.png aranıyor, confidence={conf}...")
        if try_click(image_paths['s1'], game_area_region, max_attempts=1, confidence=conf):
            time.sleep(1.5)
            if try_click(image_paths['s2'], game_area_region, max_attempts=1, confidence=confidence):
                logging.info(f"[{log_prefix}] İsyancıya saldırıldı. Raporun gelmesi bekleniyor...")
                time.sleep(5)
                if try_click(image_paths['s3'], game_area_region, max_attempts=1, confidence=confidence):
                    logging.info(f"[{log_prefix}] Rapor kapatıldı.")
                    return True
                else:
                    logging.warning(f"[{log_prefix}] Saldırı sonrası rapor bulunamadı veya kapatılamadı.")
                    return True
            break
    else:
        logging.warning(f"[{log_prefix}] s1.png 3 denemede bulunamadı.")
    
    logging.warning(f"[{log_prefix}] Dizi tamamlanamadı.")
    return False

def perform_suadasi_sequence(game_area_region, image_paths, confidence=0.55, su3_offset_x=0, su3_offset_y=0):
    log_prefix = "Su Adası"
    logging.info(f"[{log_prefix}] Dizisi başlatıldı...")
    
    su1_location = find_image_location(image_paths['su1'], game_area_region, confidence=confidence)
    if su1_location:
        pyautogui.click(su1_location)
        time.sleep(2)
        
        # Ekranı yukarı kaydır
        drag_up_amount = game_area_region[3] // 2
        pyautogui.dragTo(su1_location.x, su1_location.y - drag_up_amount, duration=1.0, button='left')
        time.sleep(2)
        
        if try_click(image_paths['su2'], game_area_region, max_attempts=1, confidence=confidence):
            time.sleep(2)
            # su3.png için üç kez azalan confidence ile dene
            for conf in [0.55, 0.45, 0.35]:
                logging.info(f"[{log_prefix}] su3.png aranıyor, confidence={conf}...")
                su3_location = find_image_location(image_paths['su3'], game_area_region, confidence=conf)
                if su3_location:
                    pyautogui.click(su3_location.x + su3_offset_x, su3_location.y + su3_offset_y)
                    time.sleep(2)
                    if try_click(image_paths['su4'], game_area_region, max_attempts=1, confidence=confidence):
                        logging.info(f"[{log_prefix}] Dizi başarıyla tamamlandı.")
                        return True
                    break
            else:
                logging.warning(f"[{log_prefix}] su3.png 3 denemede bulunamadı.")
    
    logging.warning(f"[{log_prefix}] Dizi tamamlanamadı.")
    return False

def perform_fetih_sequence(game_area_region, image_paths, confidence=0.8, fetih_x=None, fetih_y=None):
    log_prefix = "Fetih"
    logging.info(f"[{log_prefix}] Dizisi başlatıldı")
    
    if fetih_x is not None and fetih_y is not None:
        pyautogui.click(fetih_x, fetih_y)
        logging.info(f"[{log_prefix}] Fetih koordinatlarına tıklandı: ({fetih_x}, {fetih_y})")
        time.sleep(0.5)
    
    if try_click(image_paths['fetih1'], game_area_region, confidence=confidence):
        time.sleep(0.5)
        if try_click(image_paths['fetih2'], game_area_region, confidence=confidence):
            time.sleep(0.5)
            if try_click(image_paths['fetih3'], game_area_region, confidence=confidence):
                time.sleep(1)
                if try_click(image_paths['fetih4'], game_area_region, confidence=confidence):
                    logging.info(f"[{log_prefix}] Dizi başarıyla tamamlandı.")
                    return True

    logging.warning(f"[{log_prefix}] Dizi tamamlanamadı.")
    return False