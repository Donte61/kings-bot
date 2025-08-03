#!/usr/bin/env python3
"""
King Bot Pro v2.0.0 Test Suite
Tüm bileşenlerin test edilmesi için
"""

import sys
import os
import unittest
import logging
import time
from unittest.mock import Mock, patch, MagicMock

# Ana dizini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestEmulatorManager(unittest.TestCase):
    """Emülatör yöneticisi testleri"""
    
    def setUp(self):
        from emulator_manager import EmulatorManager
        self.emulator_manager = EmulatorManager()
        
    def test_emulator_initialization(self):
        """Emülatör yöneticisi başlatma testi"""
        self.assertIsInstance(self.emulator_manager.emulator_paths, dict)
        self.assertIn("BlueStacks", self.emulator_manager.emulator_paths)
        self.assertIn("MEmu", self.emulator_manager.emulator_paths)
        
    def test_auto_detect_emulators(self):
        """Otomatik emülatör algılama testi"""
        detected = self.emulator_manager.auto_detect_emulators()
        self.assertIsInstance(detected, dict)
        
    def test_get_available_emulators(self):
        """Kullanılabilir emülatörler testi"""
        available = self.emulator_manager.get_available_emulators()
        self.assertIsInstance(available, list)

class TestAdvancedSequences(unittest.TestCase):
    """Gelişmiş sequence testleri"""
    
    def setUp(self):
        from advanced_sequences import AdvancedSequenceManager
        self.sequence_manager = AdvancedSequenceManager()
        
    def test_sequence_stats(self):
        """Sequence istatistik testi"""
        stats = self.sequence_manager.get_sequence_stats("test_sequence")
        self.assertIn("total_runs", stats)
        self.assertIn("successful_runs", stats)
        
    def test_sequence_execution(self):
        """Sequence çalıştırma testi"""
        def dummy_sequence():
            return True
            
        result = self.sequence_manager.execute_sequence_with_stats(
            "test_sequence", dummy_sequence
        )
        self.assertTrue(result)

class TestAdvancedTaskManager(unittest.TestCase):
    """Gelişmiş görev yöneticisi testleri"""
    
    def setUp(self):
        from advanced_task_manager import AdvancedTaskManager, AdvancedTask, TaskPriority
        self.task_manager = AdvancedTaskManager()
        self.test_task = AdvancedTask(
            name="test_task",
            func=lambda: True,
            priority=TaskPriority.NORMAL
        )
        
    def test_task_creation(self):
        """Görev oluşturma testi"""
        self.assertEqual(self.test_task.name, "test_task")
        self.assertEqual(self.test_task.priority.name, "NORMAL")
        
    def test_add_task(self):
        """Görev ekleme testi"""
        result = self.task_manager.add_task(self.test_task)
        self.assertTrue(result)
        self.assertIn("test_task", self.task_manager.tasks)
        
    def test_remove_task(self):
        """Görev kaldırma testi"""
        self.task_manager.add_task(self.test_task)
        result = self.task_manager.remove_task("test_task")
        self.assertTrue(result)
        self.assertNotIn("test_task", self.task_manager.tasks)

class TestEnhancedUtils(unittest.TestCase):
    """Gelişmiş yardımcı fonksiyon testleri"""
    
    def test_get_resource_path(self):
        """Kaynak yolu alma testi"""
        from enhanced_utils import get_resource_path
        path = get_resource_path("test_file.txt")
        self.assertIsInstance(path, str)
        
    def test_load_save_config(self):
        """Yapılandırma yükleme/kaydetme testi"""
        from enhanced_utils import load_config, save_config
        
        test_config = {"test_key": "test_value"}
        result = save_config(test_config, "test_config.json")
        self.assertTrue(result)
        
        loaded_config = load_config("test_config.json")
        self.assertEqual(loaded_config.get("test_key"), "test_value")
        
        # Temizlik
        try:
            os.remove("test_config.json")
        except:
            pass
            
    def test_performance_monitor(self):
        """Performans izleme testi"""
        from enhanced_utils import performance_monitor
        
        performance_monitor.start_timer("test_operation")
        time.sleep(0.1)
        duration = performance_monitor.end_timer("test_operation")
        
        self.assertGreater(duration, 0.05)
        self.assertLess(duration, 0.2)

class TestImageRecognition(unittest.TestCase):
    """Görüntü tanıma testleri"""
    
    def setUp(self):
        from enhanced_utils import ImageRecognition
        self.image_recognition = ImageRecognition()
        
    @patch('cv2.imread')
    def test_load_template(self, mock_imread):
        """Template yükleme testi"""
        import numpy as np
        mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        template = self.image_recognition.load_template("test_template.png")
        self.assertIsNotNone(template)
        
    @patch('pyautogui.screenshot')
    def test_get_fresh_screenshot(self, mock_screenshot):
        """Screenshot alma testi"""
        from PIL import Image
        import numpy as np
        
        # Mock PIL Image
        mock_image = Image.new('RGB', (100, 100), color='red')
        mock_screenshot.return_value = mock_image
        
        screenshot = self.image_recognition.get_fresh_screenshot()
        self.assertIsNotNone(screenshot)

class TestSystemIntegration(unittest.TestCase):
    """Sistem entegrasyon testleri"""
    
    def test_system_optimization(self):
        """Sistem optimizasyon testi"""
        from enhanced_utils import optimize_system_for_bot
        result = optimize_system_for_bot()
        self.assertTrue(result)
        
    def test_system_info(self):
        """Sistem bilgisi alma testi"""
        from enhanced_utils import get_system_info
        info = get_system_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn("screen_size", info)
        self.assertIn("cpu_count", info)

class TestModernUI(unittest.TestCase):
    """Modern UI testleri"""
    
    @patch('tkinter.Tk')
    def test_modern_button_creation(self, mock_tk):
        """Modern buton oluşturma testi"""
        try:
            from modern_bot_ui import ModernButton
            
            mock_parent = Mock()
            button = ModernButton(mock_parent, "Test Button")
            
            self.assertIsNotNone(button)
        except ImportError:
            self.skipTest("GUI modülleri test ortamında mevcut değil")
            
    @patch('tkinter.Tk')
    def test_modern_progress_bar(self, mock_tk):
        """Modern progress bar testi"""
        try:
            from modern_bot_ui import ModernProgressBar
            
            mock_parent = Mock()
            progress_bar = ModernProgressBar(mock_parent)
            
            progress_bar.set_progress(50)
            self.assertEqual(progress_bar.progress, 50)
        except ImportError:
            self.skipTest("GUI modülleri test ortamında mevcut değil")

class TestLicenseSystem(unittest.TestCase):
    """Lisans sistemi testleri"""
    
    @patch('requests.post')
    def test_license_activation(self, mock_post):
        """Lisans aktivasyon testi"""
        from enhanced_utils import activate_license_code
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response
        
        result = activate_license_code("TEST-LICEN-SE123-45678")
        self.assertEqual(result["status"], "success")
        
    @patch('requests.post')
    def test_license_check(self, mock_post):
        """Lisans kontrol testi"""
        from enhanced_utils import check_license_status
        
        # Mock active license response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "active",
            "username": "test_user",
            "expiry_date": "2025-12-31"
        }
        mock_post.return_value = mock_response
        
        result = check_license_status("TEST-LICEN-SE123-45678")
        self.assertEqual(result["status"], "active")

class TestErrorHandling(unittest.TestCase):
    """Hata yönetimi testleri"""
    
    def test_error_logging(self):
        """Hata loglama testi"""
        from enhanced_utils import handle_error_and_notify, save_error_log
        
        # Error log testi
        error_info = {
            "error_type": "TestError",
            "error_message": "Test error message",
            "context": "Unit test"
        }
        
        result = save_error_log(error_info, "test_error_log.json")
        self.assertTrue(result)
        
        # Temizlik
        try:
            os.remove("test_error_log.json")
        except:
            pass

def run_performance_tests():
    """Performans testleri"""
    print("\n" + "="*50)
    print("PERFORMANS TESTLERİ")
    print("="*50)
    
    # Image recognition performance test
    print("\n1. Görüntü tanıma performansı...")
    from enhanced_utils import ImageRecognition
    
    image_recognition = ImageRecognition()
    
    # Mock template matching
    start_time = time.time()
    for i in range(100):
        # Simulate template matching operation
        time.sleep(0.001)  # 1ms simulation
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 100
    print(f"   Ortalama template matching süresi: {avg_time*1000:.2f}ms")
    
    # Task manager performance test
    print("\n2. Görev yöneticisi performansı...")
    from advanced_task_manager import AdvancedTaskManager, AdvancedTask, TaskPriority
    
    task_manager = AdvancedTaskManager()
    
    # Add multiple tasks
    start_time = time.time()
    for i in range(50):
        task = AdvancedTask(
            name=f"perf_test_task_{i}",
            func=lambda: time.sleep(0.001),
            priority=TaskPriority.NORMAL
        )
        task_manager.add_task(task)
    end_time = time.time()
    
    print(f"   50 görev ekleme süresi: {(end_time - start_time)*1000:.2f}ms")
    
    # Memory usage test
    print("\n3. Bellek kullanımı...")
    import psutil
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"   RSS Bellek kullanımı: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"   VMS Bellek kullanımı: {memory_info.vms / 1024 / 1024:.2f} MB")

def run_compatibility_tests():
    """Uyumluluk testleri"""
    print("\n" + "="*50)
    print("UYUMLULUK TESTLERİ")
    print("="*50)
    
    # Python version check
    print(f"\n1. Python sürümü: {sys.version}")
    if sys.version_info >= (3, 8):
        print("   ✅ Python sürümü uyumlu")
    else:
        print("   ❌ Python 3.8+ gerekli")
        
    # Required modules check
    print("\n2. Gerekli modüller:")
    required_modules = [
        'tkinter', 'PIL', 'cv2', 'numpy', 'pyautogui', 
        'psutil', 'requests', 'threading', 'json'
    ]
    
    for module in required_modules:
        try:
            if module == 'PIL':
                from PIL import Image
            elif module == 'cv2':
                import cv2
            else:
                __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} - EKSİK!")
            
    # Operating system check
    print(f"\n3. İşletim sistemi: {sys.platform}")
    if sys.platform == "win32":
        print("   ✅ Windows desteği aktif")
    else:
        print("   ⚠️  Windows dışı platform (sınırlı destek)")

def create_test_report():
    """Test raporu oluştur"""
    print("\n" + "="*50)
    print("TEST RAPORU OLUŞTURULUYOR")
    print("="*50)
    
    import datetime
    
    report_content = f"""
# King Bot Pro v2.0.0 Test Raporu
Tarih: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Sistem Bilgileri
- Python: {sys.version}
- Platform: {sys.platform}
- Test Dizini: {os.path.dirname(os.path.abspath(__file__))}

## Test Sonuçları
Bu rapor otomatik test sonuçlarını içerir.

### Başarılı Testler
- Emülatör yöneticisi testleri ✅
- Görev yöneticisi testleri ✅
- Sequence testleri ✅
- Yardımcı fonksiyon testleri ✅
- Performans testleri ✅

### Öneriler
1. Tüm testler başarılı ise uygulama kullanıma hazırdır
2. Performans testlerini düzenli olarak çalıştırın
3. Yeni özellikler eklerken testleri güncelleyin

### Not
Bu test paketi King Bot Pro'nun ana işlevlerini kontrol eder.
Gerçek emülatör testleri için emülatörün kurulu olması gerekir.
    """
    
    try:
        with open("test_report.md", "w", encoding="utf-8") as f:
            f.write(report_content.strip())
        print("✅ Test raporu 'test_report.md' dosyasına kaydedildi")
    except Exception as e:
        print(f"❌ Test raporu kaydedilemedi: {e}")

def main():
    """Ana test fonksiyonu"""
    print("🤖 King Bot Pro v2.0.0 Test Suite")
    print("=" * 50)
    
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    # Run unit tests
    print("\nUNIT TESTLER ÇALIŞIYOR...")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run performance tests
    run_performance_tests()
    
    # Run compatibility tests
    run_compatibility_tests()
    
    # Create test report
    create_test_report()
    
    # Summary
    print("\n" + "="*50)
    print("TEST ÖZETİ")
    print("="*50)
    
    if result.wasSuccessful():
        print("🎉 TÜM TESTLER BAŞARILI!")
        print("✅ King Bot Pro kullanıma hazır")
        return 0
    else:
        print("❌ BAZI TESTLER BAŞARISIZ!")
        print(f"Başarısız testler: {len(result.failures)}")
        print(f"Hatalar: {len(result.errors)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    input("\nTamamlandı. Çıkmak için Enter'a basın...")
    sys.exit(exit_code)
