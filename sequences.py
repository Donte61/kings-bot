import os
import time
import random
import pyautogui
import logging
import json
from typing import Dict, List, Tuple, Optional
from utils import try_click, find_image_location, click_sequence, get_resource_path

class AdvancedSequenceManager:
    """Gelişmiş bot sequence yöneticisi"""
    
    def __init__(self):
        self.sequence_stats = {}
        self.failed_attempts = {}
        self.last_execution_times = {}
        self.setup_logging()
        
    def setup_logging(self):
        """Sequence logging kurulumu"""
        self.logger = logging.getLogger("SequenceManager")
        
    def reset_stats(self):
        """İstatistikleri sıfırla"""
        self.sequence_stats.clear()
        self.failed_attempts.clear()
        self.last_execution_times.clear()
        
    def get_sequence_stats(self, sequence_name: str) -> Dict:
        """Sequence istatistiklerini al"""
        return self.sequence_stats.get(sequence_name, {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'last_run': None,
            'average_duration': 0
        })
        
    def update_sequence_stats(self, sequence_name: str, success: bool, duration: float):
        """Sequence istatistiklerini güncelle"""
        if sequence_name not in self.sequence_stats:
            self.sequence_stats[sequence_name] = {
                'total_runs': 0,
                'successful_runs': 0,
                'failed_runs': 0,
                'last_run': None,
                'average_duration': 0,
                'total_duration': 0
            }
            
        stats = self.sequence_stats[sequence_name]
        stats['total_runs'] += 1
        stats['last_run'] = time.time()
        stats['total_duration'] += duration
        stats['average_duration'] = stats['total_duration'] / stats['total_runs']
        
        if success:
            stats['successful_runs'] += 1
            # Başarılı olursa failed attempts'i sıfırla
            self.failed_attempts[sequence_name] = 0
        else:
            stats['failed_runs'] += 1
            # Başarısız attempts'i artır
            self.failed_attempts[sequence_name] = self.failed_attempts.get(sequence_name, 0) + 1
            
    def should_skip_sequence(self, sequence_name: str, cooldown_minutes: int = 5) -> bool:
        """Sequence'in skip edilip edilmeyeceğini kontrol et"""
        # Çok fazla başarısız deneme varsa skip et
        if self.failed_attempts.get(sequence_name, 0) >= 3:
            self.logger.warning(f"{sequence_name} çok fazla başarısız deneme nedeniyle skip ediliyor")
            return True
            
        # Cooldown kontrolü
        last_run = self.last_execution_times.get(sequence_name, 0)
        if time.time() - last_run < cooldown_minutes * 60:
            return True
            
        return False
        
    def execute_sequence_with_stats(self, sequence_name: str, sequence_func, *args, **kwargs):
        """Sequence'i istatistiklerle birlikte çalıştır"""
        if self.should_skip_sequence(sequence_name):
            return False
            
        start_time = time.time()
        self.last_execution_times[sequence_name] = start_time
        
        try:
            self.logger.info(f"[{sequence_name}] Sequence başlatıldı")
            result = sequence_func(*args, **kwargs)
            duration = time.time() - start_time
            
            self.update_sequence_stats(sequence_name, result, duration)
            
            if result:
                self.logger.info(f"[{sequence_name}] Başarılı - Süre: {duration:.2f}s")
            else:
                self.logger.warning(f"[{sequence_name}] Başarısız - Süre: {duration:.2f}s")
                
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"[{sequence_name}] Hata: {e} - Süre: {duration:.2f}s")
            self.update_sequence_stats(sequence_name, False, duration)
            return False

# Global sequence manager instance
sequence_manager = AdvancedSequenceManager()

def perform_healing_sequence(game_area_region, image_paths, confidence=0.7):
    """Geliştirilmiş iyileştirme sequence'i"""
    def healing_worker():
        log_prefix = "İyileştirme"
        
        # Öncelikli iyileştirme kontrolü
        priority_images = ['hprec1', 'heal1']
        for img in priority_images:
            if img in image_paths and try_click(image_paths[img], game_area_region, max_attempts=1, confidence=confidence):
                logging.info(f"[{log_prefix}] Öncelikli iyileştirme bulundu: {img}")
                time.sleep(0.3)
                
                # İyileştirme butonları sequence'i
                healing_buttons = ['iyilestir', 'hphelp', 'helpme']
                return click_sequence(healing_buttons, image_paths, game_area_region, confidence, 0.2, log_prefix)
                
        # Alternatif iyileştirme yöntemleri
        alternative_images = ['back', 'geri']
        for img in alternative_images:
            if img in image_paths and try_click(image_paths[img], game_area_region, max_attempts=1, confidence=confidence):
                logging.info(f"[{log_prefix}] Alternatif iyileştirme: {img}")
                return True
                
        logging.warning(f"[{log_prefix}] Hiçbir iyileştirme görseli bulunamadı")
        return False
        
    return sequence_manager.execute_sequence_with_stats("healing", healing_worker)

def perform_daily_tasks(game_area_region, image_paths, confidence=0.8):
    """Geliştirilmiş günlük görevler sequence'i"""
    def daily_worker():
        log_prefix = "Günlük Görevler"
        success_count = 0
        
        # Et toplama görevi
        if 'et_ambar' in image_paths and try_click(image_paths['et_ambar'], game_area_region, max_attempts=2, confidence=confidence):
            time.sleep(2)
            if 'et_topla' in image_paths and try_click(image_paths['et_topla'], game_area_region, max_attempts=2, confidence=confidence):
                logging.info(f"[{log_prefix}] Et toplama başarılı")
                success_count += 1
                time.sleep(1)
                
        # Ek günlük görevler varsa buraya eklenebilir
        daily_tasks = ['daily_task1', 'daily_task2', 'daily_task3']  # Örnek
        for task in daily_tasks:
            if task in image_paths and try_click(image_paths[task], game_area_region, max_attempts=1, confidence=confidence):
                logging.info(f"[{log_prefix}] {task} tamamlandı")
                success_count += 1
                time.sleep(0.5)
                
        return success_count > 0
        
    return sequence_manager.execute_sequence_with_stats("daily_tasks", daily_worker)

def perform_kutu_sequence(game_area_region, image_paths, confidence=0.8):
    """Geliştirilmiş kutu açma sequence'i"""
    def kutu_worker():
        log_prefix = "Kutu"
        opened_boxes = 0
        
        # Birden fazla kutu türü deneme
        box_types = ['kutu', 'box', 'chest']  # Farklı kutu görsel adları
        
        for box_type in box_types:
            if box_type in image_paths:
                # Her kutu türü için birden fazla deneme
                for attempt in range(3):
                    if try_click(image_paths[box_type], game_area_region, max_attempts=1, confidence=confidence):
                        logging.info(f"[{log_prefix}] {box_type} açıldı (Deneme {attempt + 1})")
                        opened_boxes += 1
                        time.sleep(1)
                        
                        # Kutu açıldıktan sonra ek butonlar varsa
                        confirm_buttons = ['confirm', 'ok', 'collect']
                        for btn in confirm_buttons:
                            if btn in image_paths and try_click(image_paths[btn], game_area_region, max_attempts=1, confidence=confidence):
                                time.sleep(0.5)
                                break
                    else:
                        break  # Bu kutu türü için daha fazla deneme yapma
                        
        return opened_boxes > 0
        
    return sequence_manager.execute_sequence_with_stats("kutu", kutu_worker)

def perform_anahtar_sequence(game_area_region, image_paths, confidence=0.8):
    """Geliştirilmiş anahtar kullanma sequence'i"""
    def anahtar_worker():
        log_prefix = "Anahtar"
        used_keys = 0
        
        # Farklı anahtar türleri
        key_images = ['anahtar1', 'anahtar2', 'anahtarback', 'anahtarback2']
        
        for key_img in key_images:
            if key_img in image_paths and try_click(image_paths[key_img], game_area_region, max_attempts=2, confidence=confidence):
                logging.info(f"[{log_prefix}] {key_img} kullanıldı")
                used_keys += 1
                time.sleep(1)
                
                # Anahtar kullanımı sonrası onay butonları
                confirm_sequence = ['use', 'confirm', 'ok']
                click_sequence(confirm_sequence, image_paths, game_area_region, confidence, 0.3, log_prefix)
                
        return used_keys > 0
        
    return sequence_manager.execute_sequence_with_stats("anahtar", anahtar_worker)

def perform_asker_hasat_sequence(game_area_region, image_paths, confidence=0.8):
    """Geliştirilmiş asker hasadı sequence'i"""
    def asker_worker():
        log_prefix = "Asker Hasadı"
        harvested = 0
        
        # Asker hasat görselleri
        soldier_images = ['asker1', 'asker2', 'asker3']
        
        for soldier_img in soldier_images:
            if soldier_img in image_paths:
                # Her asker türü için çoklu hasat denemesi
                for round_num in range(2):  # 2 tur hasat
                    if try_click(image_paths[soldier_img], game_area_region, max_attempts=1, confidence=confidence):
                        logging.info(f"[{log_prefix}] {soldier_img} hasadı - Tur {round_num + 1}")
                        harvested += 1
                        time.sleep(1.5)
                        
                        # Hasat sonrası butonlar
                        harvest_buttons = ['collect', 'harvest', 'gather']
                        click_sequence(harvest_buttons, image_paths, game_area_region, confidence, 0.5, log_prefix)
                        
        return harvested > 0
        
    return sequence_manager.execute_sequence_with_stats("asker_hasat", asker_worker)

def perform_recovery_sequence(game_area_region, image_paths, confidence=0.7):
    """Geliştirilmiş recovery sequence'i"""
    def recovery_worker():
        log_prefix = "Recovery"
        
        # Geri dönüş butonları öncelik sırasına göre
        back_buttons = ['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'back']
        
        for btn in back_buttons:
            if btn in image_paths and try_click(image_paths[btn], game_area_region, max_attempts=1, confidence=confidence):
                logging.info(f"[{log_prefix}] {btn} ile geri dönüş başarılı")
                time.sleep(0.5)
                return True
                
        return False
        
    return sequence_manager.execute_sequence_with_stats("recovery", recovery_worker)

def perform_mesaj_sequence(game_area_region, image_paths, confidence=0.8):
    """Geliştirilmiş mesaj gönderme sequence'i"""
    def mesaj_worker():
        log_prefix = "Mesaj"
        sent_messages = 0
        
        # Mesaj görselleri sıralı olarak
        message_images = ['mesaj1', 'mesaj2', 'mesaj3', 'mesaj4', 'mesaj5']
        
        for msg_img in message_images:
            if msg_img in image_paths and try_click(image_paths[msg_img], game_area_region, max_attempts=1, confidence=confidence):
                logging.info(f"[{log_prefix}] {msg_img} gönderildi")
                sent_messages += 1
                time.sleep(1)
                
                # Mesaj gönderme onayı
                send_buttons = ['send', 'gonder', 'ok']
                click_sequence(send_buttons, image_paths, game_area_region, confidence, 0.3, log_prefix)
                
        return sent_messages > 0
        
    return sequence_manager.execute_sequence_with_stats("mesaj", mesaj_worker)

def perform_savas_sequence(game_area_region, image_paths, confidence=0.8):
    """Geliştirilmiş savaş sequence'i"""
    def savas_worker():
        log_prefix = "Savaş"
        battles_fought = 0
        
        # Savaş görselleri
        battle_images = ['savas1', 'savas2', 'savas3', 'savas4', 'savas5', 'savas6', 'savas7', 'savas8']
        
        for battle_img in battle_images:
            if battle_img in image_paths and try_click(image_paths[battle_img], game_area_region, max_attempts=1, confidence=confidence):
                logging.info(f"[{log_prefix}] {battle_img} savaşı başlatıldı")
                battles_fought += 1
                time.sleep(2)  # Savaş için daha uzun bekleme
                
                # Savaş sonrası butonlar
                battle_buttons = ['attack', 'fight', 'battle', 'ok']
                click_sequence(battle_buttons, image_paths, game_area_region, confidence, 0.5, log_prefix)
                
        return battles_fought > 0
        
    return sequence_manager.execute_sequence_with_stats("savas", savas_worker)

def perform_ittifak_sequence(game_area_region, image_paths, confidence=0.8):
    """Geliştirilmiş ittifak sequence'i"""
    def ittifak_worker():
        log_prefix = "İttifak"
        alliance_actions = 0
        
        # İttifak görselleri
        alliance_images = ['ittifak1', 'ittifak2', 'ittifak3', 'ittifak4', 'ittifak5', 'ittifak6', 'ittifak7', 'ittifak8']
        
        for alliance_img in alliance_images:
            if alliance_img in image_paths and try_click(image_paths[alliance_img], game_area_region, max_attempts=1, confidence=confidence):
                logging.info(f"[{log_prefix}] {alliance_img} etkileşimi")
                alliance_actions += 1
                time.sleep(1)
                
                # İttifak etkileşim butonları
                interaction_buttons = ['help', 'assist', 'join', 'ok']
                click_sequence(interaction_buttons, image_paths, game_area_region, confidence, 0.3, log_prefix)
                
        return alliance_actions > 0
        
    return sequence_manager.execute_sequence_with_stats("ittifak", ittifak_worker)

def perform_suadasi_sequence(game_area_region, image_paths, confidence=0.8):
    """Geliştirilmiş su adası sequence'i"""
    def suadasi_worker():
        log_prefix = "Su Adası"
        island_actions = 0
        
        # Su adası görselleri
        island_images = ['su1', 'su2', 'su3', 'su4', 'su5']
        
        for island_img in island_images:
            if island_img in image_paths and try_click(image_paths[island_img], game_area_region, max_attempts=1, confidence=confidence):
                logging.info(f"[{log_prefix}] {island_img} etkileşimi")
                island_actions += 1
                time.sleep(1.5)
                
                # Su adası etkileşim butonları
                action_buttons = ['collect', 'gather', 'explore', 'ok']
                click_sequence(action_buttons, image_paths, game_area_region, confidence, 0.5, log_prefix)
                
        return island_actions > 0
        
    return sequence_manager.execute_sequence_with_stats("suadasi", suadasi_worker)

def perform_bekcikulesi_sequence(game_area_region, image_paths, confidence=0.8):
    """Geliştirilmiş bekçi kulesi sequence'i"""
    def bekcikulesi_worker():
        log_prefix = "Bekçi Kulesi"
        tower_actions = 0
        
        # Bekçi kulesi görselleri
        tower_images = ['bekci1', 'bekci2', 'bekci3', 'bekci4', 'bekci5', 'bekci6', 'bekci7', 'bekci8', 'bekci9']
        
        for tower_img in tower_images:
            if tower_img in image_paths and try_click(image_paths[tower_img], game_area_region, max_attempts=1, confidence=confidence):
                logging.info(f"[{log_prefix}] {tower_img} etkileşimi")
                tower_actions += 1
                time.sleep(1)
                
                # Kule etkileşim butonları
                tower_buttons = ['upgrade', 'collect', 'build', 'ok']
                click_sequence(tower_buttons, image_paths, game_area_region, confidence, 0.3, log_prefix)
                
        return tower_actions > 0
        
    return sequence_manager.execute_sequence_with_stats("bekcikulesi", bekcikulesi_worker)

def perform_askerbas_sequence(game_area_region, image_paths, confidence=0.8):
    """Geliştirilmiş asker basma sequence'i"""
    def askerbas_worker():
        log_prefix = "Asker Basma"
        trained_soldiers = 0
        
        # Asker basma görselleri
        training_images = ['askerbas1', 'askerbas2', 'askerbas3', 'askerbas4']
        
        for training_img in training_images:
            if training_img in image_paths:
                # Her asker türü için çoklu basma
                for batch in range(2):  # 2 batch asker basma
                    if try_click(image_paths[training_img], game_area_region, max_attempts=1, confidence=confidence):
                        logging.info(f"[{log_prefix}] {training_img} - Batch {batch + 1}")
                        trained_soldiers += 1
                        time.sleep(2)  # Asker basma için uzun bekleme
                        
                        # Eğitim onay butonları
                        training_buttons = ['train', 'recruit', 'ok', 'confirm']
                        click_sequence(training_buttons, image_paths, game_area_region, confidence, 0.5, log_prefix)
                        
        return trained_soldiers > 0
        
    return sequence_manager.execute_sequence_with_stats("askerbas", askerbas_worker)

def perform_dunya_heal_sequence(game_area_region, image_paths, confidence=0.7):
    """Geliştirilmiş dünya iyileştirme sequence'i"""
    def dunya_heal_worker():
        log_prefix = "Dünya İyileştirme"
        healed = 0
        
        # Dünya iyileştirme görselleri
        world_heal_images = ['h1', 'h2', 'h3', 'h4']
        
        for heal_img in world_heal_images:
            if heal_img in image_paths and try_click(image_paths[heal_img], game_area_region, max_attempts=1, confidence=confidence):
                logging.info(f"[{log_prefix}] {heal_img} dünya iyileştirmesi")
                healed += 1
                time.sleep(2)
                
                # İyileştirme onay butonları
                heal_buttons = ['heal', 'cure', 'restore', 'ok']
                click_sequence(heal_buttons, image_paths, game_area_region, confidence, 0.5, log_prefix)
                
        return healed > 0
        
    return sequence_manager.execute_sequence_with_stats("dunya_heal", dunya_heal_worker)

def perform_fetih_sequence(game_area_region, image_paths, confidence=0.8):
    """Geliştirilmiş fetih sequence'i"""
    def fetih_worker():
        log_prefix = "Fetih"
        conquests = 0
        
        # Fetih görselleri
        conquest_images = ['fetih1', 'fetih2', 'fetih3', 'fetih4']
        
        for conquest_img in conquest_images:
            if conquest_img in image_paths and try_click(image_paths[conquest_img], game_area_region, max_attempts=1, confidence=confidence):
                logging.info(f"[{log_prefix}] {conquest_img} fetihi başlatıldı")
                conquests += 1
                time.sleep(3)  # Fetih için uzun bekleme
                
                # Fetih butonları
                conquest_buttons = ['conquer', 'attack', 'invade', 'ok']
                click_sequence(conquest_buttons, image_paths, game_area_region, confidence, 0.5, log_prefix)
                
        return conquests > 0
        
    return sequence_manager.execute_sequence_with_stats("fetih", fetih_worker)

def perform_isyanci_sequence(game_area_region, image_paths, confidence=0.8):
    """Geliştirilmiş isyancı sequence'i"""
    def isyanci_worker():
        log_prefix = "İsyancı"
        rebellions = 0
        
        # İsyancı görselleri
        rebel_images = ['s1', 's2', 's3']
        
        for rebel_img in rebel_images:
            if rebel_img in image_paths and try_click(image_paths[rebel_img], game_area_region, max_attempts=1, confidence=confidence):
                logging.info(f"[{log_prefix}] {rebel_img} isyancı etkileşimi")
                rebellions += 1
                time.sleep(1.5)
                
                # İsyancı butonları
                rebel_buttons = ['fight', 'battle', 'defeat', 'ok']
                click_sequence(rebel_buttons, image_paths, game_area_region, confidence, 0.4, log_prefix)
                
        return rebellions > 0
        
    return sequence_manager.execute_sequence_with_stats("isyanci", isyanci_worker)

def get_all_sequence_stats():
    """Tüm sequence istatistiklerini al"""
    return sequence_manager.sequence_stats

def reset_all_sequence_stats():
    """Tüm sequence istatistiklerini sıfırla"""
    sequence_manager.reset_stats()
    logging.info("Tüm sequence istatistikleri sıfırlandı")

def get_sequence_success_rate(sequence_name: str) -> float:
    """Sequence başarı oranını al"""
    stats = sequence_manager.get_sequence_stats(sequence_name)
    if stats['total_runs'] == 0:
        return 0.0
    return (stats['successful_runs'] / stats['total_runs']) * 100

def save_sequence_stats_to_file(filename: str = "sequence_stats.json"):
    """Sequence istatistiklerini dosyaya kaydet"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(sequence_manager.sequence_stats, f, indent=4, ensure_ascii=False, default=str)
        logging.info(f"Sequence istatistikleri {filename} dosyasına kaydedildi")
    except Exception as e:
        logging.error(f"Sequence istatistikleri kaydedilemedi: {e}")

def load_sequence_stats_from_file(filename: str = "sequence_stats.json"):
    """Sequence istatistiklerini dosyadan yükle"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                sequence_manager.sequence_stats = json.load(f)
            logging.info(f"Sequence istatistikleri {filename} dosyasından yüklendi")
    except Exception as e:
        logging.error(f"Sequence istatistikleri yüklenemedi: {e}")

# Uygulama başlarken istatistikleri yükle
load_sequence_stats_from_file()
