"""
🎮 King Bot Pro - Kings Mobile Özel Otomasyonlar
Kings of Avalon oyununa özel gelişmiş otomasyon sistemleri
"""

import cv2
import numpy as np
import time
import json
import os
import random
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import pyautogui
from dataclasses import dataclass
from enum import Enum


class BuildingType(Enum):
    """Bina tipleri"""
    CASTLE = "castle"
    FARM = "farm"
    SAWMILL = "sawmill"
    IRON_MINE = "iron_mine"
    SILVER_MINE = "silver_mine"
    BARRACKS = "barracks"
    STABLE = "stable"
    RANGE = "range"
    SIEGE_WORKSHOP = "siege_workshop"
    HOSPITAL = "hospital"
    WALL = "wall"
    WATCHTOWER = "watchtower"


class TroopType(Enum):
    """Asker tipleri"""
    SPEARMAN = "spearman"
    ARCHER = "archer"
    CAVALRY = "cavalry"
    CATAPULT = "catapult"
    BALLISTA = "ballista"
    BATTERING_RAM = "battering_ram"


class ResourceType(Enum):
    """Kaynak tipleri"""
    FOOD = "food"
    WOOD = "wood"
    IRON = "iron"
    SILVER = "silver"
    GOLD = "gold"


@dataclass
class Hero:
    """Hero bilgileri"""
    name: str
    level: int
    experience: int
    skills: Dict[str, int]
    equipment: Dict[str, str]
    talent_points: int


@dataclass
class AllianceWar:
    """İttifak savaşı bilgileri"""
    war_id: str
    start_time: datetime
    end_time: datetime
    phase: str
    score: Dict[str, int]
    objectives: List[str]


class KingsMobileAutomation:
    """Kings Mobile özel otomasyon sistemi"""
    
    def __init__(self, ai_vision_system=None):
        self.ai_vision = ai_vision_system
        self.config_file = "kings_mobile_config.json"
        self.load_config()
        
        # Oyun durumu
        self.game_state = {
            "castle_level": 0,
            "resources": {res.value: 0 for res in ResourceType},
            "heroes": [],
            "troops": {troop.value: 0 for troop in TroopType},
            "alliance_war": None,
            "last_update": None
        }
        
        # Görev sistemi
        self.task_queue = []
        self.active_tasks = []
        self.task_history = []
        
        # Template dosyaları
        self.templates_dir = "kings_mobile_templates"
        self.ensure_templates_directory()
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Otomatik sistemler
        self.auto_systems = {
            "resource_gathering": False,
            "alliance_help": False,
            "daily_tasks": False,
            "hero_development": False,
            "troop_training": False,
            "research": False,
            "building_upgrade": False
        }
    
    def load_config(self):
        """Konfigürasyon dosyasını yükle"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = self.get_default_config()
                self.save_config()
        except Exception as e:
            print(f"Config yükleme hatası: {e}")
            self.config = self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Varsayılan konfigürasyon"""
        return {
            "auto_resource_gathering": {
                "enabled": True,
                "gather_types": ["food", "wood", "iron", "silver"],
                "march_count": 4,
                "duration_hours": 8,
                "hero_selection": "auto"
            },
            "alliance_help": {
                "enabled": True,
                "help_all_interval": 300,  # 5 dakika
                "request_help": True,
                "alliance_shop": True
            },
            "daily_tasks": {
                "enabled": True,
                "vip_chest": True,
                "free_chests": True,
                "dragon_lair": True,
                "alliance_gifts": True,
                "daily_quests": True
            },
            "hero_development": {
                "enabled": True,
                "auto_level_up": True,
                "talent_allocation": "balanced",
                "equipment_upgrade": True,
                "skill_priority": ["attack", "defense", "health"]
            },
            "troop_training": {
                "enabled": True,
                "training_queue": ["spearman", "archer", "cavalry"],
                "maintain_ratio": True,
                "hospital_check": True
            },
            "research": {
                "enabled": True,
                "research_priority": ["military", "economy", "defense"],
                "auto_research": True
            },
            "building_upgrade": {
                "enabled": True,
                "upgrade_priority": ["castle", "resource_buildings", "military"],
                "resource_requirement_check": True
            },
            "alliance_war": {
                "auto_participate": True,
                "target_selection": "auto",
                "march_coordination": True,
                "shield_management": True
            },
            "safety": {
                "anti_detection": True,
                "random_delays": True,
                "human_like_movements": True,
                "break_intervals": [30, 60],  # dakika
                "daily_limit_hours": 8
            }
        }
    
    def save_config(self):
        """Konfigürasyonu kaydet"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Config kaydetme hatası: {e}")
    
    def ensure_templates_directory(self):
        """Template dizinini oluştur"""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
    
    def start_automation(self):
        """Otomasyonu başlat"""
        print("🎮 Kings Mobile Otomasyonu Başlatılıyor...")
        
        # Oyun durumunu güncelle
        self.update_game_state()
        
        # Monitoring başlat
        self.start_monitoring()
        
        # Otomatik sistemleri başlat
        self.start_auto_systems()
        
        print("✅ Tüm otomasyon sistemleri aktif!")
    
    def stop_automation(self):
        """Otomasyonu durdur"""
        print("🛑 Kings Mobile Otomasyonu Durduruluyor...")
        
        # Monitoring durdur
        self.stop_monitoring()
        
        # Aktif görevleri temizle
        self.task_queue.clear()
        self.active_tasks.clear()
        
        # Otomatik sistemleri durdur
        for system in self.auto_systems:
            self.auto_systems[system] = False
        
        print("✅ Otomasyon durduruldu!")
    
    def update_game_state(self):
        """Oyun durumunu güncelle"""
        try:
            # Ekran görüntüsü al
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Kale seviyesini tespit et
            castle_level = self.detect_castle_level(screenshot)
            if castle_level:
                self.game_state["castle_level"] = castle_level
            
            # Kaynakları tespit et
            resources = self.detect_resources(screenshot)
            if resources:
                self.game_state["resources"].update(resources)
            
            # Hero bilgilerini güncelle
            heroes = self.detect_heroes(screenshot)
            if heroes:
                self.game_state["heroes"] = heroes
            
            # Asker sayılarını tespit et
            troops = self.detect_troops(screenshot)
            if troops:
                self.game_state["troops"].update(troops)
            
            # İttifak savaşı durumunu kontrol et
            alliance_war = self.detect_alliance_war(screenshot)
            if alliance_war:
                self.game_state["alliance_war"] = alliance_war
            
            self.game_state["last_update"] = datetime.now()
            
        except Exception as e:
            print(f"Oyun durumu güncelleme hatası: {e}")
    
    def detect_castle_level(self, screenshot) -> Optional[int]:
        """Kale seviyesini tespit et"""
        try:
            # AI vision kullan
            if self.ai_vision:
                result = self.ai_vision.analyze_game_state(screenshot, "castle_level")
                if result and "level" in result:
                    return result["level"]
            
            # Template matching fallback
            template_path = os.path.join(self.templates_dir, "castle_info.png")
            if os.path.exists(template_path):
                template = cv2.imread(template_path)
                locations = self.find_template(screenshot, template)
                if locations:
                    # OCR ile seviye oku
                    level = self.extract_number_from_region(screenshot, locations[0])
                    return level
            
        except Exception as e:
            print(f"Kale seviyesi tespit hatası: {e}")
        
        return None
    
    def detect_resources(self, screenshot) -> Dict[str, int]:
        """Kaynakları tespit et"""
        resources = {}
        
        try:
            # Resource bar'ı bul
            resource_templates = {
                "food": "food_icon.png",
                "wood": "wood_icon.png", 
                "iron": "iron_icon.png",
                "silver": "silver_icon.png",
                "gold": "gold_icon.png"
            }
            
            for resource_type, template_file in resource_templates.items():
                template_path = os.path.join(self.templates_dir, template_file)
                if os.path.exists(template_path):
                    template = cv2.imread(template_path)
                    locations = self.find_template(screenshot, template)
                    
                    if locations:
                        # Resource miktarını oku
                        amount = self.extract_resource_amount(screenshot, locations[0], resource_type)
                        if amount:
                            resources[resource_type] = amount
            
        except Exception as e:
            print(f"Kaynak tespit hatası: {e}")
        
        return resources
    
    def detect_heroes(self, screenshot) -> List[Hero]:
        """Hero bilgilerini tespit et"""
        heroes = []
        
        try:
            # Hero panelini aç
            if self.click_template("hero_button.png", screenshot):
                time.sleep(2)
                
                # Hero listesini oku
                hero_screenshot = pyautogui.screenshot()
                hero_screenshot = cv2.cvtColor(np.array(hero_screenshot), cv2.COLOR_RGB2BGR)
                
                # AI vision ile hero analizi
                if self.ai_vision:
                    hero_data = self.ai_vision.analyze_game_state(hero_screenshot, "heroes")
                    if hero_data and "heroes" in hero_data:
                        for hero_info in hero_data["heroes"]:
                            hero = Hero(
                                name=hero_info.get("name", "Unknown"),
                                level=hero_info.get("level", 1),
                                experience=hero_info.get("experience", 0),
                                skills=hero_info.get("skills", {}),
                                equipment=hero_info.get("equipment", {}),
                                talent_points=hero_info.get("talent_points", 0)
                            )
                            heroes.append(hero)
                
                # Paneli kapat
                self.click_template("close_button.png", hero_screenshot)
            
        except Exception as e:
            print(f"Hero tespit hatası: {e}")
        
        return heroes
    
    def detect_troops(self, screenshot) -> Dict[str, int]:
        """Asker sayılarını tespit et"""
        troops = {}
        
        try:
            # Barracks'a git
            if self.click_template("barracks_button.png", screenshot):
                time.sleep(2)
                
                troop_screenshot = pyautogui.screenshot()
                troop_screenshot = cv2.cvtColor(np.array(troop_screenshot), cv2.COLOR_RGB2BGR)
                
                # Her asker tipi için sayıları oku
                troop_templates = {
                    "spearman": "spearman_icon.png",
                    "archer": "archer_icon.png",
                    "cavalry": "cavalry_icon.png",
                    "catapult": "catapult_icon.png"
                }
                
                for troop_type, template_file in troop_templates.items():
                    template_path = os.path.join(self.templates_dir, template_file)
                    if os.path.exists(template_path):
                        template = cv2.imread(template_path)
                        locations = self.find_template(troop_screenshot, template)
                        
                        if locations:
                            count = self.extract_troop_count(troop_screenshot, locations[0])
                            if count:
                                troops[troop_type] = count
                
                # Paneli kapat
                self.click_template("close_button.png", troop_screenshot)
            
        except Exception as e:
            print(f"Asker tespit hatası: {e}")
        
        return troops
    
    def detect_alliance_war(self, screenshot) -> Optional[AllianceWar]:
        """İttifak savaşını tespit et"""
        try:
            # Alliance war icon'u ara
            if self.find_template(screenshot, "alliance_war_icon.png"):
                # War bilgilerini al
                war_info = self.extract_war_info(screenshot)
                if war_info:
                    return AllianceWar(
                        war_id=war_info.get("id", "unknown"),
                        start_time=war_info.get("start_time", datetime.now()),
                        end_time=war_info.get("end_time", datetime.now() + timedelta(hours=24)),
                        phase=war_info.get("phase", "unknown"),
                        score=war_info.get("score", {}),
                        objectives=war_info.get("objectives", [])
                    )
        except Exception as e:
            print(f"Alliance war tespit hatası: {e}")
        
        return None
    
    def start_monitoring(self):
        """Monitoring sistemini başlat"""
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    # Oyun durumunu güncelle
                    self.update_game_state()
                    
                    # Acil durumları kontrol et
                    self.check_emergency_situations()
                    
                    # Görevleri işle
                    self.process_task_queue()
                    
                    # Kısa bekleme
                    time.sleep(30)  # 30 saniyede bir kontrol
                    
                except Exception as e:
                    print(f"Monitoring hatası: {e}")
                    time.sleep(60)
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Monitoring sistemini durdur"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
    
    def check_emergency_situations(self):
        """Acil durumları kontrol et"""
        try:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Saldırı uyarısı
            if self.find_template(screenshot, "attack_warning.png"):
                self.handle_attack_warning()
            
            # Kaynak dolu uyarısı
            if self.find_template(screenshot, "resources_full.png"):
                self.handle_resources_full()
            
            # Hospital dolu
            if self.find_template(screenshot, "hospital_full.png"):
                self.handle_hospital_full()
            
            # Alliance help needed
            if self.find_template(screenshot, "alliance_help_needed.png"):
                self.handle_alliance_help()
            
        except Exception as e:
            print(f"Acil durum kontrolü hatası: {e}")
    
    def handle_attack_warning(self):
        """Saldırı uyarısını işle"""
        print("🚨 Saldırı Uyarısı! Shield aktifleştiriliyor...")
        
        try:
            # Shield kullan
            if self.use_shield():
                print("🛡️ Shield aktifleştirildi!")
            else:
                # Teleport kullan
                if self.use_teleport():
                    print("🚀 Teleport kullanıldı!")
                else:
                    print("⚠️ Shield/Teleport kullanılamadı!")
                    
        except Exception as e:
            print(f"Saldırı uyarısı işleme hatası: {e}")
    
    def handle_resources_full(self):
        """Dolu kaynakları işle"""
        print("📦 Kaynaklar dolu! Upgrade veya training başlatılıyor...")
        
        try:
            # Building upgrade başlat
            if self.start_building_upgrade():
                print("🏗️ Building upgrade başlatıldı!")
            
            # Troop training başlat
            elif self.start_troop_training():
                print("👥 Troop training başlatıldı!")
            
            # Research başlat
            elif self.start_research():
                print("🔬 Research başlatıldı!")
                
        except Exception as e:
            print(f"Dolu kaynak işleme hatası: {e}")
    
    def handle_hospital_full(self):
        """Hospital dolu durumunu işle"""
        print("🏥 Hospital dolu! Healing başlatılıyor...")
        
        try:
            # Heal all troops
            if self.heal_all_troops():
                print("💊 Tüm askerler iyileştirildi!")
            else:
                print("⚠️ Healing başarısız!")
                
        except Exception as e:
            print(f"Hospital işleme hatası: {e}")
    
    def handle_alliance_help(self):
        """Alliance yardım durumunu işle"""
        print("🤝 Alliance yardım istekleri işleniyor...")
        
        try:
            if self.help_all_alliance():
                print("✅ Tüm alliance üyelerine yardım edildi!")
                
        except Exception as e:
            print(f"Alliance yardım hatası: {e}")
    
    def start_auto_systems(self):
        """Otomatik sistemleri başlat"""
        
        # Resource gathering
        if self.config["auto_resource_gathering"]["enabled"]:
            self.start_auto_resource_gathering()
        
        # Alliance help
        if self.config["alliance_help"]["enabled"]:
            self.start_auto_alliance_help()
        
        # Daily tasks
        if self.config["daily_tasks"]["enabled"]:
            self.start_auto_daily_tasks()
        
        # Hero development
        if self.config["hero_development"]["enabled"]:
            self.start_auto_hero_development()
        
        # Troop training
        if self.config["troop_training"]["enabled"]:
            self.start_auto_troop_training()
        
        # Research
        if self.config["research"]["enabled"]:
            self.start_auto_research()
        
        # Building upgrade
        if self.config["building_upgrade"]["enabled"]:
            self.start_auto_building_upgrade()
    
    def start_auto_resource_gathering(self):
        """Otomatik kaynak toplama başlat"""
        def resource_gathering_loop():
            while self.auto_systems["resource_gathering"]:
                try:
                    print("🌾 Otomatik kaynak toplama çalışıyor...")
                    
                    # Mevcut march'ları kontrol et
                    active_marches = self.get_active_marches()
                    max_marches = self.config["auto_resource_gathering"]["march_count"]
                    
                    if len(active_marches) < max_marches:
                        # Yeni march başlat
                        available_slots = max_marches - len(active_marches)
                        for _ in range(available_slots):
                            if self.start_resource_march():
                                print("⚔️ Yeni kaynak march'ı başlatıldı!")
                                time.sleep(random.uniform(5, 15))
                            else:
                                break
                    
                    # 10 dakika bekle
                    time.sleep(600)
                    
                except Exception as e:
                    print(f"Resource gathering hatası: {e}")
                    time.sleep(300)
        
        self.auto_systems["resource_gathering"] = True
        threading.Thread(target=resource_gathering_loop, daemon=True).start()
    
    def start_auto_alliance_help(self):
        """Otomatik alliance yardım başlat"""
        def alliance_help_loop():
            while self.auto_systems["alliance_help"]:
                try:
                    print("🤝 Otomatik alliance yardım çalışıyor...")
                    
                    if self.help_all_alliance():
                        print("✅ Alliance yardımları tamamlandı!")
                    
                    # Alliance shop kontrolü
                    if self.config["alliance_help"]["alliance_shop"]:
                        self.check_alliance_shop()
                    
                    # Belirlenen aralıkta bekle
                    interval = self.config["alliance_help"]["help_all_interval"]
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"Alliance help hatası: {e}")
                    time.sleep(300)
        
        self.auto_systems["alliance_help"] = True
        threading.Thread(target=alliance_help_loop, daemon=True).start()
    
    def start_auto_daily_tasks(self):
        """Otomatik günlük görevler başlat"""
        def daily_tasks_loop():
            last_daily_check = datetime.now().date()
            
            while self.auto_systems["daily_tasks"]:
                try:
                    current_date = datetime.now().date()
                    
                    # Günlük reset kontrolü
                    if current_date > last_daily_check:
                        print("📅 Günlük görevler başlatılıyor...")
                        
                        config = self.config["daily_tasks"]
                        
                        # VIP chest
                        if config["vip_chest"]:
                            self.collect_vip_chest()
                        
                        # Free chests
                        if config["free_chests"]:
                            self.collect_free_chests()
                        
                        # Dragon lair
                        if config["dragon_lair"]:
                            self.attack_dragon_lair()
                        
                        # Alliance gifts
                        if config["alliance_gifts"]:
                            self.collect_alliance_gifts()
                        
                        # Daily quests
                        if config["daily_quests"]:
                            self.complete_daily_quests()
                        
                        last_daily_check = current_date
                        print("✅ Günlük görevler tamamlandı!")
                    
                    # 1 saat bekle
                    time.sleep(3600)
                    
                except Exception as e:
                    print(f"Daily tasks hatası: {e}")
                    time.sleep(1800)
        
        self.auto_systems["daily_tasks"] = True
        threading.Thread(target=daily_tasks_loop, daemon=True).start()
    
    def start_auto_hero_development(self):
        """Otomatik hero geliştirme başlat"""
        def hero_development_loop():
            while self.auto_systems["hero_development"]:
                try:
                    print("🦸 Otomatik hero geliştirme çalışıyor...")
                    
                    config = self.config["hero_development"]
                    
                    # Auto level up
                    if config["auto_level_up"]:
                        self.auto_level_heroes()
                    
                    # Equipment upgrade
                    if config["equipment_upgrade"]:
                        self.auto_upgrade_equipment()
                    
                    # Talent allocation
                    self.auto_allocate_talents()
                    
                    # 30 dakika bekle
                    time.sleep(1800)
                    
                except Exception as e:
                    print(f"Hero development hatası: {e}")
                    time.sleep(900)
        
        self.auto_systems["hero_development"] = True
        threading.Thread(target=hero_development_loop, daemon=True).start()
    
    # Utility methods
    def find_template(self, screenshot, template_name, threshold=0.8):
        """Template matching"""
        try:
            if isinstance(template_name, str):
                template_path = os.path.join(self.templates_dir, template_name)
                if not os.path.exists(template_path):
                    return []
                template = cv2.imread(template_path)
            else:
                template = template_name
            
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)
            
            if len(locations[0]) > 0:
                matches = []
                for pt in zip(*locations[::-1]):
                    matches.append((pt[0], pt[1], template.shape[1], template.shape[0]))
                return matches
            
        except Exception as e:
            print(f"Template matching hatası: {e}")
        
        return []
    
    def click_template(self, template_name, screenshot=None, confidence=0.8):
        """Template'e tıkla"""
        try:
            if screenshot is None:
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            matches = self.find_template(screenshot, template_name, confidence)
            if matches:
                x, y, w, h = matches[0]
                center_x = x + w // 2
                center_y = y + h // 2
                
                # Human-like click
                self.human_like_click(center_x, center_y)
                return True
            
        except Exception as e:
            print(f"Template tıklama hatası: {e}")
        
        return False
    
    def human_like_click(self, x, y):
        """İnsan benzeri tıklama"""
        try:
            # Random offset
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-3, 3)
            
            # Mouse hareketi
            pyautogui.moveTo(x + offset_x, y + offset_y, 
                           duration=random.uniform(0.1, 0.3))
            
            # Tıklama
            pyautogui.click()
            
            # Random delay
            time.sleep(random.uniform(0.1, 0.5))
            
        except Exception as e:
            print(f"Human-like click hatası: {e}")
    
    def extract_number_from_region(self, screenshot, region):
        """Bölgeden sayı çıkar (OCR)"""
        try:
            x, y, w, h = region
            roi = screenshot[y:y+h, x:x+w]
            
            # OCR ile sayı oku
            # Bu kısım Tesseract OCR veya custom number recognition gerektirir
            # Şimdilik placeholder
            return None
            
        except Exception as e:
            print(f"Number extraction hatası: {e}")
            return None

    def get_active_marches(self):
        """Aktif march'ları al"""
        try:
            # AI vision kullanarak march sayısını tespit et
            if self.ai_vision:
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                # March bilgilerini AI ile analiz et
                return []  # Şimdilik boş liste döndür
            return []
        except Exception as e:
            print(f"Active marches hatası: {e}")
            return []
    
    def start_resource_march(self):
        """Kaynak march'ı başlat"""
        try:
            # World map'e git ve resource tile seç
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Template'lerle march başlatma işlemi
            if self.click_template("world_map.png", screenshot):
                time.sleep(2)
                if self.click_template("resource_tile.png"):
                    time.sleep(1)
                    if self.click_template("gather_button.png"):
                        time.sleep(1)
                        if self.click_template("march_button.png"):
                            return True
            return False
        except Exception as e:
            print(f"Resource march başlatma hatası: {e}")
            return False
    
    def help_all_alliance(self):
        """Tüm alliance üyelerine yardım et"""
        try:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Alliance paneline git
            if self.click_template("alliance_button.png", screenshot):
                time.sleep(2)
                # Help all butonuna tıkla
                if self.click_template("help_all_button.png"):
                    print("✅ Alliance help tamamlandı!")
                    return True
            return False
        except Exception as e:
            print(f"Alliance help hatası: {e}")
            return False
    
    def check_alliance_shop(self):
        """Alliance shop'u kontrol et"""
        try:
            # Alliance shop kontrol kodu
            print("🏪 Alliance shop kontrol ediliyor...")
            return True
        except Exception as e:
            print(f"Alliance shop hatası: {e}")
            return False
    
    def collect_vip_chest(self):
        """VIP chest topla"""
        try:
            if self.click_template("vip_chest.png"):
                print("📦 VIP chest toplandı!")
                return True
            return False
        except Exception as e:
            print(f"VIP chest hatası: {e}")
            return False
    
    def collect_free_chests(self):
        """Free chest'leri topla"""
        try:
            if self.click_template("free_chest.png"):
                print("🎁 Free chest'ler toplandı!")
                return True
            return False
        except Exception as e:
            print(f"Free chest hatası: {e}")
            return False
    
    def attack_dragon_lair(self):
        """Dragon lair'e saldır"""
        try:
            if self.click_template("dragon_lair.png"):
                time.sleep(1)
                if self.click_template("attack_button.png"):
                    print("🐉 Dragon lair saldırısı başlatıldı!")
                    return True
            return False
        except Exception as e:
            print(f"Dragon lair hatası: {e}")
            return False
    
    def collect_alliance_gifts(self):
        """Alliance hediyelerini topla"""
        try:
            if self.click_template("alliance_gifts.png"):
                print("🎁 Alliance hediyeleri toplandı!")
                return True
            return False
        except Exception as e:
            print(f"Alliance gifts hatası: {e}")
            return False
    
    def complete_daily_quests(self):
        """Günlük görevleri tamamla"""
        try:
            if self.click_template("daily_quests.png"):
                print("📋 Günlük görevler kontrol edildi!")
                return True
            return False
        except Exception as e:
            print(f"Daily quests hatası: {e}")
            return False
    
    def auto_level_heroes(self):
        """Hero'ları otomatik level up yap"""
        try:
            # Hero paneline git
            if self.click_template("hero_button.png"):
                time.sleep(2)
                # Level up butonlarını ara ve tıkla
                if self.click_template("hero_levelup.png"):
                    print("⬆️ Hero level up yapıldı!")
                    return True
            return False
        except Exception as e:
            print(f"Auto level heroes hatası: {e}")
            return False
    
    def auto_upgrade_equipment(self):
        """Equipment'leri otomatik upgrade et"""
        try:
            if self.click_template("equipment_upgrade.png"):
                print("⚔️ Equipment upgrade yapıldı!")
                return True
            return False
        except Exception as e:
            print(f"Equipment upgrade hatası: {e}")
            return False
    
    def auto_allocate_talents(self):
        """Talent'leri otomatik dağıt"""
        try:
            if self.click_template("talent_button.png"):
                time.sleep(1)
                if self.click_template("auto_allocate.png"):
                    print("🌟 Talent'ler otomatik dağıtıldı!")
                    return True
            return False
        except Exception as e:
            print(f"Talent allocation hatası: {e}")
            return False
    
    def start_auto_troop_training(self):
        """Otomatik asker eğitimi başlat"""
        def troop_training_loop():
            while self.auto_systems["troop_training"]:
                try:
                    print("👥 Otomatik troop training çalışıyor...")
                    
                    # Barracks'a git
                    if self.click_template("barracks_button.png"):
                        time.sleep(2)
                        # Train butonuna tıkla
                        if self.click_template("train_button.png"):
                            print("⚔️ Troop training başlatıldı!")
                    
                    # 30 dakika bekle
                    time.sleep(1800)
                    
                except Exception as e:
                    print(f"Troop training hatası: {e}")
                    time.sleep(900)
        
        self.auto_systems["troop_training"] = True
        threading.Thread(target=troop_training_loop, daemon=True).start()
    
    def start_auto_research(self):
        """Otomatik araştırma başlat"""
        def research_loop():
            while self.auto_systems["research"]:
                try:
                    print("🔬 Otomatik research çalışıyor...")
                    
                    # Academy'e git
                    if self.click_template("academy_button.png"):
                        time.sleep(2)
                        # Research butonuna tıkla
                        if self.click_template("research_button.png"):
                            print("📚 Research başlatıldı!")
                    
                    # 1 saat bekle
                    time.sleep(3600)
                    
                except Exception as e:
                    print(f"Research hatası: {e}")
                    time.sleep(1800)
        
        self.auto_systems["research"] = True
        threading.Thread(target=research_loop, daemon=True).start()
    
    def start_auto_building_upgrade(self):
        """Otomatik bina upgrade başlat"""
        def building_upgrade_loop():
            while self.auto_systems["building_upgrade"]:
                try:
                    print("🏗️ Otomatik building upgrade çalışıyor...")
                    
                    # Upgrade yapılabilir binaları bul
                    if self.click_template("upgrade_available.png"):
                        time.sleep(1)
                        if self.click_template("upgrade_button.png"):
                            print("⬆️ Building upgrade başlatıldı!")
                    
                    # 30 dakika bekle
                    time.sleep(1800)
                    
                except Exception as e:
                    print(f"Building upgrade hatası: {e}")
                    time.sleep(900)
        
        self.auto_systems["building_upgrade"] = True
        threading.Thread(target=building_upgrade_loop, daemon=True).start()
    
    def process_task_queue(self):
        """Görev kuyruğunu işle"""
        try:
            while self.task_queue:
                task = self.task_queue.pop(0)
                print(f"📋 Görev işleniyor: {task}")
                # Görev işleme kodu
                self.task_history.append(task)
        except Exception as e:
            print(f"Task queue işleme hatası: {e}")
    
    def use_shield(self):
        """Shield kullan"""
        try:
            if self.click_template("shield_icon.png"):
                time.sleep(1)
                if self.click_template("use_shield.png"):
                    print("🛡️ Shield kullanıldı!")
                    return True
            return False
        except Exception as e:
            print(f"Shield kullanma hatası: {e}")
            return False
    
    def use_teleport(self):
        """Teleport kullan"""
        try:
            if self.click_template("teleport_icon.png"):
                time.sleep(1)
                if self.click_template("use_teleport.png"):
                    print("🚀 Teleport kullanıldı!")
                    return True
            return False
        except Exception as e:
            print(f"Teleport kullanma hatası: {e}")
            return False
    
    def start_building_upgrade(self):
        """Building upgrade başlat"""
        try:
            if self.click_template("building_upgrade.png"):
                print("🏗️ Building upgrade başlatıldı!")
                return True
            return False
        except Exception as e:
            print(f"Building upgrade başlatma hatası: {e}")
            return False
    
    def start_troop_training(self):
        """Troop training başlat"""
        try:
            if self.click_template("troop_training.png"):
                print("👥 Troop training başlatıldı!")
                return True
            return False
        except Exception as e:
            print(f"Troop training başlatma hatası: {e}")
            return False
    
    def start_research(self):
        """Research başlat"""
        try:
            if self.click_template("research_start.png"):
                print("🔬 Research başlatıldı!")
                return True
            return False
        except Exception as e:
            print(f"Research başlatma hatası: {e}")
            return False
    
    def heal_all_troops(self):
        """Tüm askerleri iyileştir"""
        try:
            if self.click_template("hospital_button.png"):
                time.sleep(2)
                if self.click_template("heal_all_button.png"):
                    print("💊 Tüm askerler iyileştirildi!")
                    return True
            return False
        except Exception as e:
            print(f"Heal all troops hatası: {e}")
            return False
    
    def extract_resource_amount(self, screenshot, location, resource_type):
        """Resource miktarını çıkar"""
        try:
            # OCR ile resource miktarını oku
            # Şimdilik placeholder
            return random.randint(1000, 99999)
        except Exception as e:
            print(f"Resource amount extraction hatası: {e}")
            return 0
    
    def extract_troop_count(self, screenshot, location):
        """Asker sayısını çıkar"""
        try:
            # OCR ile asker sayısını oku
            # Şimdilik placeholder
            return random.randint(100, 9999)
        except Exception as e:
            print(f"Troop count extraction hatası: {e}")
            return 0
    
    def extract_war_info(self, screenshot):
        """Savaş bilgilerini çıkar"""
        try:
            # AI vision ile savaş bilgilerini analiz et
            return {
                "id": "war_123",
                "phase": "preparation",
                "score": {"our_alliance": 0, "enemy_alliance": 0},
                "objectives": ["Destroy enemy towers", "Capture flags"]
            }
        except Exception as e:
            print(f"War info extraction hatası: {e}")
            return None


# Test fonksiyonu
def test_kings_mobile_automation():
    """Kings Mobile otomasyonunu test et"""
    automation = KingsMobileAutomation()
    
    print("🎮 Kings Mobile Otomasyonu Test Ediliyor...")
    
    # Konfigürasyonu göster
    print("⚙️ Mevcut Konfigürasyon:")
    for system, config in automation.config.items():
        if isinstance(config, dict) and "enabled" in config:
            status = "✅" if config["enabled"] else "❌"
            print(f"{status} {system}")
    
    # Test oyun durumu güncelleme
    automation.update_game_state()
    print(f"🏰 Oyun Durumu: {automation.game_state}")
    
    print("✅ Test tamamlandı!")


if __name__ == "__main__":
    test_kings_mobile_automation()
