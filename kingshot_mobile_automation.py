#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kingshot Mobile Automation System
Enhanced Kings Bot Pro ile Kingshot Mobile desteği
"""

import cv2
import numpy as np
import pyautogui
import time
import threading
import random
from datetime import datetime

class KingshotMobileAutomation:
    """Kingshot Mobile oyunu için özel otomasyon sistemi"""
    
    def __init__(self, ai_vision=None):
        """Kingshot Mobile otomasyonunu başlat"""
        self.ai_vision = ai_vision
        self.game_state = {
            "castle_level": 0,
            "power": 0,
            "resources": {
                "gold": 0,
                "food": 0,
                "wood": 0,
                "stone": 0,
                "iron": 0,
                "gems": 0
            },
            "heroes": [],
            "pets": [],
            "alliance": {
                "name": "",
                "members": 0,
                "territory": 0
            },
            "last_update": datetime.now()
        }
        
        # Kingshot Mobile specific configuration
        self.config = {
            "auto_battle": {"enabled": True, "interval": 300},
            "resource_gathering": {"enabled": True, "interval": 600},
            "hero_upgrade": {"enabled": True, "interval": 900},
            "pet_training": {"enabled": True, "interval": 1200},
            "alliance_help": {"enabled": True, "interval": 180},
            "daily_quests": {"enabled": True, "interval": 3600},
            "territory_defense": {"enabled": True, "interval": 1800},
            "gift_codes": {"enabled": True, "interval": 7200},
            "arena_battle": {"enabled": True, "interval": 1800},
            "dungeon_raids": {"enabled": True, "interval": 2400}
        }
        
        self.auto_systems = {
            "battle": False,
            "resource_gathering": False,
            "hero_upgrade": False,
            "pet_training": False,
            "territory_defense": False
        }
        
        self.task_queue = []
        self.task_history = []
        
        print("🎮 Kingshot Mobile Automation System başlatıldı!")
    
    def update_game_state(self):
        """Oyun durumunu güncelle"""
        try:
            if self.ai_vision:
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # AI ile oyun durumunu analiz et
                game_analysis = self.ai_vision.analyze_game_state(screenshot)
                if game_analysis:
                    self.game_state.update(game_analysis)
            
            self.game_state["last_update"] = datetime.now()
            
        except Exception as e:
            print(f"Oyun durumu güncelleme hatası: {e}")
    
    def click_template(self, template_name, screenshot=None):
        """Template'i bul ve tıkla"""
        try:
            if screenshot is None:
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Template matching logic burada olacak
            # Şimdilik random konum döndür
            x, y = random.randint(100, 800), random.randint(100, 600)
            pyautogui.click(x, y)
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print(f"Template tıklama hatası: {e}")
            return False
    
    # =============================================================================
    # KINGSHOT MOBILE SPECIFIC FEATURES
    # =============================================================================
    
    def auto_battle_campaign(self):
        """Otomatik kampanya savaşı"""
        try:
            print("⚔️ Otomatik kampanya savaşı başlatılıyor...")
            
            # Campaign butonuna tıkla
            if self.click_template("campaign_button.png"):
                time.sleep(2)
                
                # Battle butonuna tıkla
                if self.click_template("battle_button.png"):
                    time.sleep(1)
                    
                    # Auto battle aktif et
                    if self.click_template("auto_battle.png"):
                        print("✅ Auto battle aktif!")
                        
                        # Savaş sonucunu bekle
                        self.wait_for_battle_end()
                        
                        # Ödülleri topla
                        self.collect_battle_rewards()
                        
                        return True
            return False
            
        except Exception as e:
            print(f"Auto battle hatası: {e}")
            return False
    
    def wait_for_battle_end(self):
        """Savaş bitişini bekle"""
        try:
            print("⏳ Savaş bitiş bekleniyor...")
            max_wait = 300  # 5 dakika max
            wait_time = 0
            
            while wait_time < max_wait:
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Victory/Defeat ekranını kontrol et
                if self.check_battle_result(screenshot):
                    print("🏆 Savaş tamamlandı!")
                    return True
                
                time.sleep(5)
                wait_time += 5
            
            print("⚠️ Savaş bekleme timeout!")
            return False
            
        except Exception as e:
            print(f"Battle wait hatası: {e}")
            return False
    
    def check_battle_result(self, screenshot):
        """Savaş sonucunu kontrol et"""
        try:
            # Victory/Defeat template'lerini kontrol et
            victory_found = self.find_template("victory.png", screenshot)
            defeat_found = self.find_template("defeat.png", screenshot)
            
            return victory_found or defeat_found
            
        except Exception as e:
            print(f"Battle result check hatası: {e}")
            return False
    
    def collect_battle_rewards(self):
        """Savaş ödüllerini topla"""
        try:
            print("🎁 Savaş ödülleri toplanıyor...")
            
            # Reward butonlarını tıkla
            if self.click_template("collect_reward.png"):
                time.sleep(1)
                
            # Continue/OK butonuna tıkla
            if self.click_template("continue_button.png"):
                print("✅ Ödüller toplandı!")
                return True
                
        except Exception as e:
            print(f"Reward collection hatası: {e}")
            return False
    
    def upgrade_heroes(self):
        """Hero'ları upgrade et"""
        try:
            print("⬆️ Hero upgrade işlemi başlatılıyor...")
            
            # Heroes paneline git
            if self.click_template("heroes_button.png"):
                time.sleep(2)
                
                # Her hero için upgrade kontrol et
                hero_positions = [(200, 300), (400, 300), (600, 300), (200, 500), (400, 500)]
                
                for pos in hero_positions:
                    pyautogui.click(pos)
                    time.sleep(1)
                    
                    # Upgrade butonunu kontrol et
                    if self.click_template("hero_upgrade.png"):
                        time.sleep(2)
                        print(f"✅ Hero upgrade yapıldı: {pos}")
                    
                    # Geri dön
                    if self.click_template("back_button.png"):
                        time.sleep(1)
                
                return True
                
        except Exception as e:
            print(f"Hero upgrade hatası: {e}")
            return False
    
    def train_pets(self):
        """Pet'leri eğit"""
        try:
            print("🐾 Pet training başlatılıyor...")
            
            # Pets paneline git
            if self.click_template("pets_button.png"):
                time.sleep(2)
                
                # Train butonuna tıkla
                if self.click_template("pet_train.png"):
                    time.sleep(1)
                    
                    # Training seçeneklerini kontrol et
                    training_options = ["speed_training.png", "attack_training.png", "defense_training.png"]
                    
                    for option in training_options:
                        if self.click_template(option):
                            print(f"✅ Pet training: {option}")
                            time.sleep(2)
                            break
                
                return True
                
        except Exception as e:
            print(f"Pet training hatası: {e}")
            return False
    
    def collect_resources(self):
        """Kaynakları topla"""
        try:
            print("📦 Kaynak toplama işlemi başlatılıyor...")
            
            # Resource üretim binalarını kontrol et
            resource_buildings = [
                "gold_mine.png", "food_farm.png", "wood_mill.png", 
                "stone_quarry.png", "iron_mine.png"
            ]
            
            for building in resource_buildings:
                if self.click_template(building):
                    time.sleep(1)
                    
                    # Collect butonuna tıkla
                    if self.click_template("collect_button.png"):
                        print(f"✅ Kaynak toplandı: {building}")
                        time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"Resource collection hatası: {e}")
            return False
    
    def alliance_activities(self):
        """Alliance aktiviteleri"""
        try:
            print("🤝 Alliance aktiviteleri başlatılıyor...")
            
            # Alliance paneline git
            if self.click_template("alliance_button.png"):
                time.sleep(2)
                
                # Help all alliance members
                if self.click_template("help_all.png"):
                    print("✅ Alliance help tamamlandı!")
                    time.sleep(1)
                
                # Alliance shop kontrolü
                if self.click_template("alliance_shop.png"):
                    time.sleep(2)
                    
                    # Free items kontrol et
                    if self.click_template("free_item.png"):
                        print("✅ Alliance shop free item alındı!")
                    
                    # Geri dön
                    if self.click_template("back_button.png"):
                        time.sleep(1)
                
                # Territory defense
                if self.click_template("territory_button.png"):
                    time.sleep(2)
                    
                    # Defend butonunu kontrol et
                    if self.click_template("defend_button.png"):
                        print("✅ Territory defense aktif!")
                
                return True
                
        except Exception as e:
            print(f"Alliance activities hatası: {e}")
            return False
    
    def complete_daily_quests(self):
        """Günlük görevleri tamamla"""
        try:
            print("📋 Günlük görevler kontrol ediliyor...")
            
            # Quest paneline git
            if self.click_template("quest_button.png"):
                time.sleep(2)
                
                # Daily quests sekmesine git
                if self.click_template("daily_quests_tab.png"):
                    time.sleep(1)
                    
                    # Claim butonlarını ara
                    for i in range(5):  # 5 quest'e kadar kontrol et
                        if self.click_template("claim_quest.png"):
                            print(f"✅ Daily quest {i+1} tamamlandı!")
                            time.sleep(1)
                
                # Weekly quests kontrol et
                if self.click_template("weekly_quests_tab.png"):
                    time.sleep(1)
                    
                    for i in range(3):  # 3 weekly quest kontrol et
                        if self.click_template("claim_quest.png"):
                            print(f"✅ Weekly quest {i+1} tamamlandı!")
                            time.sleep(1)
                
                return True
                
        except Exception as e:
            print(f"Daily quests hatası: {e}")
            return False
    
    def arena_battles(self):
        """Arena savaşları"""
        try:
            print("🏟️ Arena savaşları başlatılıyor...")
            
            # Arena paneline git
            if self.click_template("arena_button.png"):
                time.sleep(2)
                
                # Challenge butonuna tıkla
                if self.click_template("arena_challenge.png"):
                    time.sleep(1)
                    
                    # Opponent seç
                    if self.click_template("select_opponent.png"):
                        time.sleep(1)
                        
                        # Battle butonuna tıkla
                        if self.click_template("arena_battle.png"):
                            print("⚔️ Arena savaşı başlatıldı!")
                            
                            # Savaş sonucunu bekle
                            self.wait_for_battle_end()
                            
                            # Ödülleri topla
                            self.collect_battle_rewards()
                
                return True
                
        except Exception as e:
            print(f"Arena battles hatası: {e}")
            return False
    
    def dungeon_raids(self):
        """Dungeon raid'leri"""
        try:
            print("🏰 Dungeon raid'leri başlatılıyor...")
            
            # Dungeon paneline git
            if self.click_template("dungeon_button.png"):
                time.sleep(2)
                
                # Available dungeons kontrol et
                dungeon_types = ["normal_dungeon.png", "elite_dungeon.png", "boss_dungeon.png"]
                
                for dungeon in dungeon_types:
                    if self.click_template(dungeon):
                        time.sleep(1)
                        
                        # Challenge butonuna tıkla
                        if self.click_template("dungeon_challenge.png"):
                            print(f"🗡️ {dungeon} raid başlatıldı!")
                            
                            # Raid sonucunu bekle
                            self.wait_for_battle_end()
                            
                            # Ödülleri topla
                            self.collect_battle_rewards()
                            
                            # Geri dön
                            if self.click_template("back_button.png"):
                                time.sleep(1)
                
                return True
                
        except Exception as e:
            print(f"Dungeon raids hatası: {e}")
            return False
    
    def use_gift_codes(self):
        """Gift code'ları kullan"""
        try:
            print("🎁 Gift code'lar kontrol ediliyor...")
            
            # Settings paneline git
            if self.click_template("settings_button.png"):
                time.sleep(2)
                
                # Gift code butonuna tıkla
                if self.click_template("gift_code_button.png"):
                    time.sleep(1)
                    
                    # Güncel gift code'ları dene
                    gift_codes = [
                        "KINGSHOT2025", "NEWPLAYER", "ALLIANCE", 
                        "DAILY", "WEEKLY", "MONTHLY"
                    ]
                    
                    for code in gift_codes:
                        # Input alanına code yaz
                        pyautogui.click(400, 300)  # Input field pozisyonu
                        time.sleep(0.5)
                        pyautogui.typewrite(code)
                        time.sleep(0.5)
                        
                        # Claim butonuna tıkla
                        if self.click_template("claim_code.png"):
                            print(f"✅ Gift code kullanıldı: {code}")
                            time.sleep(2)
                        
                        # Input'u temizle
                        pyautogui.hotkey('ctrl', 'a')
                        pyautogui.press('delete')
                        time.sleep(0.5)
                
                return True
                
        except Exception as e:
            print(f"Gift codes hatası: {e}")
            return False
    
    # =============================================================================
    # AUTO SYSTEMS
    # =============================================================================
    
    def start_auto_battle_system(self):
        """Otomatik savaş sistemini başlat"""
        def battle_loop():
            while self.auto_systems["battle"]:
                try:
                    print("🔄 Auto battle sistemi çalışıyor...")
                    
                    # Campaign battles
                    self.auto_battle_campaign()
                    time.sleep(30)
                    
                    # Arena battles
                    self.arena_battles()
                    time.sleep(30)
                    
                    # Dungeon raids
                    self.dungeon_raids()
                    
                    # 5 dakika bekle
                    time.sleep(300)
                    
                except Exception as e:
                    print(f"Auto battle system hatası: {e}")
                    time.sleep(60)
        
        self.auto_systems["battle"] = True
        threading.Thread(target=battle_loop, daemon=True).start()
        print("🚀 Auto battle sistemi başlatıldı!")
    
    def start_auto_resource_system(self):
        """Otomatik kaynak toplama sistemini başlat"""
        def resource_loop():
            while self.auto_systems["resource_gathering"]:
                try:
                    print("🔄 Auto resource sistemi çalışıyor...")
                    
                    # Kaynakları topla
                    self.collect_resources()
                    
                    # 10 dakika bekle
                    time.sleep(600)
                    
                except Exception as e:
                    print(f"Auto resource system hatası: {e}")
                    time.sleep(300)
        
        self.auto_systems["resource_gathering"] = True
        threading.Thread(target=resource_loop, daemon=True).start()
        print("🚀 Auto resource sistemi başlatıldı!")
    
    def start_auto_hero_system(self):
        """Otomatik hero geliştirme sistemini başlat"""
        def hero_loop():
            while self.auto_systems["hero_upgrade"]:
                try:
                    print("🔄 Auto hero sistemi çalışıyor...")
                    
                    # Hero'ları upgrade et
                    self.upgrade_heroes()
                    
                    # 15 dakika bekle
                    time.sleep(900)
                    
                except Exception as e:
                    print(f"Auto hero system hatası: {e}")
                    time.sleep(450)
        
        self.auto_systems["hero_upgrade"] = True
        threading.Thread(target=hero_loop, daemon=True).start()
        print("🚀 Auto hero sistemi başlatıldı!")
    
    def start_auto_pet_system(self):
        """Otomatik pet eğitim sistemini başlat"""
        def pet_loop():
            while self.auto_systems["pet_training"]:
                try:
                    print("🔄 Auto pet sistemi çalışıyor...")
                    
                    # Pet'leri eğit
                    self.train_pets()
                    
                    # 20 dakika bekle
                    time.sleep(1200)
                    
                except Exception as e:
                    print(f"Auto pet system hatası: {e}")
                    time.sleep(600)
        
        self.auto_systems["pet_training"] = True
        threading.Thread(target=pet_loop, daemon=True).start()
        print("🚀 Auto pet sistemi başlatıldı!")
    
    def start_auto_alliance_system(self):
        """Otomatik alliance aktivite sistemini başlat"""
        def alliance_loop():
            while True:  # Alliance help sürekli çalışsın
                try:
                    print("🔄 Auto alliance sistemi çalışıyor...")
                    
                    # Alliance aktiviteleri
                    self.alliance_activities()
                    
                    # Daily quests
                    self.complete_daily_quests()
                    
                    # Gift codes (günde bir kez)
                    current_hour = datetime.now().hour
                    if current_hour == 0:  # Gece yarısında
                        self.use_gift_codes()
                    
                    # 3 dakika bekle
                    time.sleep(180)
                    
                except Exception as e:
                    print(f"Auto alliance system hatası: {e}")
                    time.sleep(90)
        
        threading.Thread(target=alliance_loop, daemon=True).start()
        print("🚀 Auto alliance sistemi başlatıldı!")
    
    def stop_auto_systems(self):
        """Tüm otomasyon sistemlerini durdur"""
        for system in self.auto_systems:
            self.auto_systems[system] = False
        print("🛑 Tüm otomasyon sistemleri durduruldu!")
    
    def find_template(self, template_name, screenshot):
        """Template'i ekranda bul"""
        try:
            # Template matching logic burada olacak
            # Şimdilik random bool döndür
            return random.choice([True, False])
        except Exception as e:
            print(f"Template find hatası: {e}")
            return False
    
    def get_system_status(self):
        """Sistem durumunu al"""
        status = {
            "systems": self.auto_systems.copy(),
            "game_state": self.game_state.copy(),
            "config": self.config.copy(),
            "task_queue_length": len(self.task_queue),
            "task_history_length": len(self.task_history)
        }
        return status


# Test function
def test_kingshot_mobile():
    """Kingshot Mobile otomasyonunu test et"""
    try:
        print("🧪 Kingshot Mobile Automation Test Başlatılıyor...")
        
        # AI Vision sistemi başlat
        ai_vision = None
        try:
            from ai_vision import AIVisionSystem
            ai_vision = AIVisionSystem()
            print("✅ AI Vision sistemi başlatıldı")
        except Exception as e:
            print(f"❌ AI Vision sistemi başlatılamadı: {e}")
        
        # Kingshot Mobile Automation sistemi başlat
        automation = KingshotMobileAutomation(ai_vision=ai_vision)
        
        # Test senaryoları
        print("\n🔄 Test Senaryoları:")
        
        # Resource toplama testi
        print("📦 Resource toplama testi...")
        automation.collect_resources()
        
        # Hero upgrade testi
        print("⬆️ Hero upgrade testi...")
        automation.upgrade_heroes()
        
        # Alliance activities testi
        print("🤝 Alliance activities testi...")
        automation.alliance_activities()
        
        # Daily quest testi
        print("📋 Daily quest testi...")
        automation.complete_daily_quests()
        
        print("\n✅ Test tamamlandı!")
        return True
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False


if __name__ == "__main__":
    test_kingshot_mobile()
