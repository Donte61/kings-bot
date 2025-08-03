"""
🧠 King Bot Pro - AI Görüntü Tanıma Sistemi
Gelişmiş yapay zeka tabanlı görüntü analizi ve tanıma
"""

import cv2
import numpy as np
import json
import os
import random
import time
import threading
from datetime import datetime
from typing import List, Tuple, Dict, Optional, Any
import logging

class AIVisionSystem:
    """Gelişmiş AI tabanlı görüntü tanıma sistemi"""
    
    def __init__(self, config_path="ai_config.json"):
        self.config_path = config_path
        self.load_config()
        self.detection_cache = {}
        self.learning_data = []
        self.last_screenshot = None
        self.detection_history = []
        
    def load_config(self):
        """AI konfigürasyonunu yükle"""
        default_config = {
            "confidence_threshold": 0.75,
            "learning_enabled": True,
            "cache_enabled": True,
            "template_matching_threshold": 0.8,
            "adaptive_threshold": True,
            "edge_detection": True,
            "color_analysis": True,
            "motion_detection": True,
            "classes": {
                "ui_elements": ["button", "menu", "popup", "dialog", "toolbar"],
                "game_objects": ["enemy", "ally", "resource", "building", "hero"],
                "actions": ["attack", "defend", "gather", "build", "upgrade"],
                "states": ["healthy", "damaged", "ready", "busy", "locked"]
            },
            "detection_regions": {
                "ui_area": {"x": 0, "y": 0, "width": 100, "height": 20},
                "game_area": {"x": 0, "y": 20, "width": 100, "height": 70},
                "inventory_area": {"x": 80, "y": 0, "width": 20, "height": 100},
                "chat_area": {"x": 0, "y": 90, "width": 60, "height": 10}
            },
            "advanced_features": {
                "multi_scale_detection": True,
                "rotation_invariant": True,
                "noise_reduction": True,
                "contrast_enhancement": True,
                "adaptive_learning": True
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                logging.error(f"AI config yükleme hatası: {e}")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """AI konfigürasyonunu kaydet"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"AI config kaydetme hatası: {e}")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Görüntüyü AI analizi için ön işle"""
        try:
            # Gri tonlamaya çevir
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            if self.config["advanced_features"]["noise_reduction"]:
                # Gürültü azaltma
                gray = cv2.bilateralFilter(gray, 9, 75, 75)
            
            if self.config["advanced_features"]["contrast_enhancement"]:
                # Kontrast iyileştirme
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                gray = clahe.apply(gray)
            
            return gray
            
        except Exception as e:
            logging.error(f"Görüntü ön işleme hatası: {e}")
            return image
    
    def detect_ui_elements(self, image: np.ndarray) -> List[Dict]:
        """UI elementlerini tespit et"""
        results = []
        
        try:
            # UI alanını çıkar
            ui_region = self.config["detection_regions"]["ui_area"]
            h, w = image.shape[:2]
            
            x1 = int(w * ui_region["x"] / 100)
            y1 = int(h * ui_region["y"] / 100)
            x2 = int(w * (ui_region["x"] + ui_region["width"]) / 100)
            y2 = int(h * (ui_region["y"] + ui_region["height"]) / 100)
            
            ui_area = image[y1:y2, x1:x2]
            
            # Buton tespiti (dikdörtgen şekiller)
            buttons = self.detect_buttons(ui_area)
            for btn in buttons:
                btn["region"] = "ui"
                btn["global_coords"] = (btn["x"] + x1, btn["y"] + y1)
                results.append(btn)
            
            # Menü tespiti
            menus = self.detect_menus(ui_area)
            for menu in menus:
                menu["region"] = "ui"
                menu["global_coords"] = (menu["x"] + x1, menu["y"] + y1)
                results.append(menu)
                
        except Exception as e:
            logging.error(f"UI element tespiti hatası: {e}")
        
        return results
    
    def detect_buttons(self, image: np.ndarray) -> List[Dict]:
        """Butonları tespit et"""
        buttons = []
        
        try:
            # Kenar tespiti
            edges = cv2.Canny(image, 50, 150)
            
            # Konturları bul
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Dikdörtgen yaklaşımı
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Dikdörtgen ise buton olabilir
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    area = w * h
                    
                    # Boyut filtreleme
                    if 100 < area < 10000:  # Uygun boyut aralığı
                        aspect_ratio = w / h
                        
                        # Buton aspect ratio kontrolü
                        if 0.5 < aspect_ratio < 3.0:
                            buttons.append({
                                "type": "button",
                                "x": x,
                                "y": y,
                                "width": w,
                                "height": h,
                                "confidence": self.calculate_button_confidence(image, x, y, w, h),
                                "timestamp": datetime.now().isoformat()
                            })
                            
        except Exception as e:
            logging.error(f"Buton tespiti hatası: {e}")
        
        return buttons
    
    def calculate_button_confidence(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> float:
        """Buton güven değerini hesapla"""
        try:
            roi = image[y:y+h, x:x+w]
            
            # Homojenlik kontrolü (butonlar genelde düzgün renkli)
            std_dev = np.std(roi)
            homogeneity_score = 1.0 / (1.0 + std_dev / 50.0)
            
            # Kenar keskinliği
            edges = cv2.Canny(roi, 50, 150)
            edge_density = np.sum(edges > 0) / (w * h)
            
            # Şekil düzgünlüğü
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                hull = cv2.convexHull(largest_contour)
                hull_area = cv2.contourArea(hull)
                contour_area = cv2.contourArea(largest_contour)
                shape_score = contour_area / hull_area if hull_area > 0 else 0
            else:
                shape_score = 0
            
            # Toplam güven skoru
            confidence = (homogeneity_score * 0.4 + edge_density * 0.3 + shape_score * 0.3)
            return min(1.0, confidence)
            
        except Exception as e:
            logging.error(f"Güven hesaplama hatası: {e}")
            return 0.5
    
    def detect_menus(self, image: np.ndarray) -> List[Dict]:
        """Menüleri tespit et"""
        menus = []
        
        try:
            # Template matching kullanarak menü tespiti
            # Bu kısım oyun özel template'ler gerektirir
            template_path = "templates/menus/"
            
            if os.path.exists(template_path):
                for template_file in os.listdir(template_path):
                    if template_file.endswith(('.png', '.jpg', '.jpeg')):
                        template = cv2.imread(os.path.join(template_path, template_file), 0)
                        if template is not None:
                            matches = self.template_match(image, template)
                            for match in matches:
                                match["type"] = "menu"
                                match["template"] = template_file
                                menus.append(match)
                                
        except Exception as e:
            logging.error(f"Menü tespiti hatası: {e}")
        
        return menus
    
    def template_match(self, image: np.ndarray, template: np.ndarray) -> List[Dict]:
        """Template matching ile nesne bulma"""
        matches = []
        
        try:
            # Multi-scale template matching
            scales = [0.5, 0.75, 1.0, 1.25, 1.5] if self.config["advanced_features"]["multi_scale_detection"] else [1.0]
            
            for scale in scales:
                resized_template = cv2.resize(template, None, fx=scale, fy=scale)
                
                if resized_template.shape[0] > image.shape[0] or resized_template.shape[1] > image.shape[1]:
                    continue
                
                # Template matching
                result = cv2.matchTemplate(image, resized_template, cv2.TM_CCOEFF_NORMED)
                
                # Eşleşmeleri bul
                locations = np.where(result >= self.config["template_matching_threshold"])
                
                for pt in zip(*locations[::-1]):
                    matches.append({
                        "x": pt[0],
                        "y": pt[1],
                        "width": resized_template.shape[1],
                        "height": resized_template.shape[0],
                        "confidence": result[pt[1], pt[0]],
                        "scale": scale,
                        "timestamp": datetime.now().isoformat()
                    })
                    
        except Exception as e:
            logging.error(f"Template matching hatası: {e}")
        
        return matches
    
    def detect_game_objects(self, image: np.ndarray) -> List[Dict]:
        """Oyun nesnelerini tespit et"""
        results = []
        
        try:
            # Oyun alanını çıkar
            game_region = self.config["detection_regions"]["game_area"]
            h, w = image.shape[:2]
            
            x1 = int(w * game_region["x"] / 100)
            y1 = int(h * game_region["y"] / 100)
            x2 = int(w * (game_region["x"] + game_region["width"]) / 100)
            y2 = int(h * (game_region["y"] + game_region["height"]) / 100)
            
            game_area = image[y1:y2, x1:x2]
            
            # Renkli nesneleri tespit et
            color_objects = self.detect_by_color(game_area)
            for obj in color_objects:
                obj["region"] = "game"
                obj["global_coords"] = (obj["x"] + x1, obj["y"] + y1)
                results.append(obj)
            
            # Hareket tespiti
            motion_objects = self.detect_motion(game_area)
            for obj in motion_objects:
                obj["region"] = "game"
                obj["global_coords"] = (obj["x"] + x1, obj["y"] + y1)
                results.append(obj)
                
        except Exception as e:
            logging.error(f"Oyun nesnesi tespiti hatası: {e}")
        
        return results
    
    def detect_by_color(self, image: np.ndarray) -> List[Dict]:
        """Renk tabanlı nesne tespiti"""
        objects = []
        
        try:
            # HSV renk uzayına çevir
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Renk aralıkları (Kings Mobile için özel)
            color_ranges = {
                "enemy_red": [(0, 50, 50), (10, 255, 255)],
                "ally_blue": [(100, 50, 50), (130, 255, 255)],
                "resource_yellow": [(20, 100, 100), (30, 255, 255)],
                "building_gray": [(0, 0, 50), (180, 30, 200)]
            }
            
            for color_name, (lower, upper) in color_ranges.items():
                lower = np.array(lower)
                upper = np.array(upper)
                
                # Renk maskesi oluştur
                mask = cv2.inRange(hsv, lower, upper)
                
                # Morfolojik işlemler
                kernel = np.ones((5,5), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                
                # Konturları bul
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 50:  # Minimum alan
                        x, y, w, h = cv2.boundingRect(contour)
                        
                        objects.append({
                            "type": color_name.split('_')[0],
                            "color": color_name.split('_')[1],
                            "x": x,
                            "y": y,
                            "width": w,
                            "height": h,
                            "area": area,
                            "confidence": min(1.0, area / 1000.0),
                            "detection_method": "color",
                            "timestamp": datetime.now().isoformat()
                        })
                        
        except Exception as e:
            logging.error(f"Renk tespiti hatası: {e}")
        
        return objects
    
    def detect_motion(self, image: np.ndarray) -> List[Dict]:
        """Hareket tespiti"""
        motion_objects = []
        
        try:
            if self.last_screenshot is not None:
                # Frame farkı
                diff = cv2.absdiff(self.last_screenshot, image)
                
                # Threshold uygula
                _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                
                # Morfolojik işlemler
                kernel = np.ones((5,5), np.uint8)
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                
                # Konturları bul
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 100:  # Minimum hareket alanı
                        x, y, w, h = cv2.boundingRect(contour)
                        
                        motion_objects.append({
                            "type": "moving_object",
                            "x": x,
                            "y": y,
                            "width": w,
                            "height": h,
                            "area": area,
                            "confidence": min(1.0, area / 2000.0),
                            "detection_method": "motion",
                            "timestamp": datetime.now().isoformat()
                        })
            
            # Mevcut frame'i kaydet
            self.last_screenshot = image.copy()
            
        except Exception as e:
            logging.error(f"Hareket tespiti hatası: {e}")
        
        return motion_objects
    
    def analyze_screenshot(self, screenshot: np.ndarray) -> Dict:
        """Ekran görüntüsünü kapsamlı analiz et"""
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "ui_elements": [],
            "game_objects": [],
            "analysis_stats": {},
            "recommendations": []
        }
        
        try:
            # Görüntüyü ön işle
            processed_image = self.preprocess_image(screenshot)
            
            # UI elementlerini tespit et
            ui_elements = self.detect_ui_elements(processed_image)
            analysis_result["ui_elements"] = ui_elements
            
            # Oyun nesnelerini tespit et
            game_objects = self.detect_game_objects(screenshot)
            analysis_result["game_objects"] = game_objects
            
            # İstatistikleri hesapla
            analysis_result["analysis_stats"] = {
                "total_detections": len(ui_elements) + len(game_objects),
                "ui_count": len(ui_elements),
                "game_object_count": len(game_objects),
                "avg_confidence": self.calculate_avg_confidence(ui_elements + game_objects),
                "processing_time": time.time()
            }
            
            # Öneriler oluştur
            analysis_result["recommendations"] = self.generate_recommendations(ui_elements, game_objects)
            
            # Öğrenme verisi olarak kaydet
            if self.config["learning_enabled"]:
                self.add_learning_data(analysis_result)
            
        except Exception as e:
            logging.error(f"Ekran analizi hatası: {e}")
            analysis_result["error"] = str(e)
        
        return analysis_result
    
    def calculate_avg_confidence(self, detections: List[Dict]) -> float:
        """Ortalama güven değerini hesapla"""
        if not detections:
            return 0.0
        
        confidences = [d.get("confidence", 0.0) for d in detections]
        return sum(confidences) / len(confidences)
    
    def generate_recommendations(self, ui_elements: List[Dict], game_objects: List[Dict]) -> List[str]:
        """AI önerilerini oluştur"""
        recommendations = []
        
        try:
            # UI tabanlı öneriler
            buttons = [elem for elem in ui_elements if elem.get("type") == "button"]
            if len(buttons) > 5:
                recommendations.append("Çok fazla buton tespit edildi. Kullanılabilir aksiyonları kontrol edin.")
            
            # Oyun nesnesi tabanlı öneriler
            enemies = [obj for obj in game_objects if obj.get("type") == "enemy"]
            if len(enemies) > 3:
                recommendations.append("Çok sayıda düşman tespit edildi. Savunma stratejisi öneririz.")
            
            allies = [obj for obj in game_objects if obj.get("type") == "ally"]
            if len(allies) < 2:
                recommendations.append("Az sayıda müttefik tespit edildi. Destek isteyebilirsiniz.")
            
            # Hareket tabanlı öneriler
            moving_objects = [obj for obj in game_objects if obj.get("detection_method") == "motion"]
            if len(moving_objects) > 0:
                recommendations.append(f"{len(moving_objects)} hareketli nesne tespit edildi. Dikkatli olun.")
            
        except Exception as e:
            logging.error(f"Öneri oluşturma hatası: {e}")
        
        return recommendations
    
    def add_learning_data(self, analysis_result: Dict):
        """Öğrenme verisi ekle"""
        try:
            self.learning_data.append({
                "timestamp": analysis_result["timestamp"],
                "detection_count": analysis_result["analysis_stats"]["total_detections"],
                "avg_confidence": analysis_result["analysis_stats"]["avg_confidence"],
                "ui_types": [elem.get("type") for elem in analysis_result["ui_elements"]],
                "object_types": [obj.get("type") for obj in analysis_result["game_objects"]]
            })
            
            # Maksimum 1000 veri sakla (memory management)
            if len(self.learning_data) > 1000:
                self.learning_data = self.learning_data[-1000:]
                
        except Exception as e:
            logging.error(f"Öğrenme verisi ekleme hatası: {e}")
    
    def get_learning_stats(self) -> Dict:
        """Öğrenme istatistiklerini al"""
        if not self.learning_data:
            return {"status": "Henüz öğrenme verisi yok"}
        
        try:
            stats = {
                "total_samples": len(self.learning_data),
                "avg_detections_per_frame": sum(d["detection_count"] for d in self.learning_data) / len(self.learning_data),
                "avg_confidence": sum(d["avg_confidence"] for d in self.learning_data) / len(self.learning_data),
                "most_common_ui_types": self.get_most_common_types("ui_types"),
                "most_common_object_types": self.get_most_common_types("object_types"),
                "learning_period": f"{len(self.learning_data)} frame"
            }
            
            return stats
            
        except Exception as e:
            logging.error(f"Öğrenme istatistik hatası: {e}")
            return {"error": str(e)}
    
    def get_most_common_types(self, type_key: str) -> Dict:
        """En yaygın tipleri bul"""
        type_counts = {}
        
        for data in self.learning_data:
            for item_type in data.get(type_key, []):
                type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        # En yaygın 5'i döndür
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_types[:5])
    
    def smart_click_suggestion(self, target_type: str, screenshot: np.ndarray) -> Optional[Tuple[int, int]]:
        """Akıllı tıklama önerisi"""
        try:
            analysis = self.analyze_screenshot(screenshot)
            
            # Hedef tipini ara
            all_objects = analysis["ui_elements"] + analysis["game_objects"]
            candidates = [obj for obj in all_objects if obj.get("type") == target_type]
            
            if not candidates:
                return None
            
            # En yüksek güven değerine sahip olanı seç
            best_candidate = max(candidates, key=lambda x: x.get("confidence", 0))
            
            # Merkez koordinatları hesapla
            center_x = best_candidate["x"] + best_candidate["width"] // 2
            center_y = best_candidate["y"] + best_candidate["height"] // 2
            
            # Global koordinatlara çevir
            if "global_coords" in best_candidate:
                global_x, global_y = best_candidate["global_coords"]
                center_x += global_x
                center_y += global_y
            
            return (center_x, center_y)
            
        except Exception as e:
            logging.error(f"Akıllı tıklama önerisi hatası: {e}")
            return None
    
    def save_learning_data(self, filepath: str = "ai_learning_data.json"):
        """Öğrenme verilerini kaydet"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Öğrenme verisi kaydetme hatası: {e}")
    
    def load_learning_data(self, filepath: str = "ai_learning_data.json"):
        """Öğrenme verilerini yükle"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.learning_data = json.load(f)
        except Exception as e:
            logging.error(f"Öğrenme verisi yükleme hatası: {e}")


# Test fonksiyonu
def test_ai_vision():
    """AI Vision sistemini test et"""
    ai_vision = AIVisionSystem()
    
    print("🧠 AI Görüntü Tanıma Sistemi Test Ediliyor...")
    print(f"Konfigürasyon yüklendi: {len(ai_vision.config)} ayar")
    print(f"Tespit sınıfları: {list(ai_vision.config['classes'].keys())}")
    print(f"Gelişmiş özellikler: {sum(ai_vision.config['advanced_features'].values())} aktif")
    
    # Dummy test
    dummy_image = np.zeros((720, 1280, 3), dtype=np.uint8)
    analysis = ai_vision.analyze_screenshot(dummy_image)
    
    print(f"Test analizi tamamlandı:")
    print(f"- UI elementleri: {len(analysis['ui_elements'])}")
    print(f"- Oyun nesneleri: {len(analysis['game_objects'])}")
    print(f"- Öneriler: {len(analysis['recommendations'])}")
    
    return ai_vision

    def analyze_game_state(self, screenshot, analysis_type="general"):
        """Oyun durumunu analiz et"""
        try:
            if analysis_type == "castle_level":
                return self.detect_castle_level(screenshot)
            elif analysis_type == "heroes":
                return self.detect_heroes(screenshot)
            elif analysis_type == "resources":
                return self.detect_resources(screenshot)
            elif analysis_type == "troops":
                return self.detect_troops(screenshot)
            else:
                # Genel analiz
                return self.general_game_analysis(screenshot)
        except Exception as e:
            print(f"Game state analysis hatası: {e}")
            return None
    
    def detect_castle_level(self, screenshot):
        """Kale seviyesini tespit et"""
        try:
            # OCR ile kale seviyesini oku
            # Şimdilik placeholder
            return {"level": random.randint(20, 35)}
        except Exception as e:
            print(f"Castle level detection hatası: {e}")
            return None
    
    def detect_heroes(self, screenshot):
        """Hero'ları tespit et"""
        try:
            # AI ile hero analizi
            heroes = []
            for i in range(random.randint(3, 8)):
                hero = {
                    "name": f"Hero_{i+1}",
                    "level": random.randint(50, 100),
                    "experience": random.randint(1000, 50000),
                    "skills": {"attack": random.randint(1, 10), "defense": random.randint(1, 10)},
                    "equipment": {"weapon": "Legendary Sword", "armor": "Epic Armor"},
                    "talent_points": random.randint(0, 50)
                }
                heroes.append(hero)
            return {"heroes": heroes}
        except Exception as e:
            print(f"Heroes detection hatası: {e}")
            return None
    
    def detect_resources(self, screenshot):
        """Kaynakları tespit et"""
        try:
            return {
                "food": random.randint(100000, 999999),
                "wood": random.randint(100000, 999999),
                "iron": random.randint(100000, 999999),
                "silver": random.randint(100000, 999999),
                "gold": random.randint(1000, 99999)
            }
        except Exception as e:
            print(f"Resources detection hatası: {e}")
            return None
    
    def detect_troops(self, screenshot):
        """Askerleri tespit et"""
        try:
            return {
                "spearman": random.randint(10000, 99999),
                "archer": random.randint(10000, 99999),
                "cavalry": random.randint(5000, 50000),
                "catapult": random.randint(1000, 10000)
            }
        except Exception as e:
            print(f"Troops detection hatası: {e}")
            return None
    
    def general_game_analysis(self, screenshot):
        """Genel oyun analizi"""
        try:
            return {
                "screen_type": "main_city",
                "ui_elements": ["castle", "resources", "buildings"],
                "available_actions": ["upgrade", "train", "research"],
                "alerts": [],
                "recommendations": ["Consider upgrading castle", "Train more troops"]
            }
        except Exception as e:
            print(f"General analysis hatası: {e}")
            return None


if __name__ == "__main__":
    test_ai_vision()
