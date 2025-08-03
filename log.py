import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import logging
import queue

log_queue = queue.Queue()

class TkinterLogHandler(logging.Handler):
    def __init__(self, log_queue=None, level=logging.NOTSET):
        super().__init__(level)
        self.log_queue = log_queue or queue.Queue()
        
    def emit(self, record):
        log_entry = self.format(record)
        original_message = record.getMessage()
        
        task_category = "Genel"
        task_categories = {
            "İyileştirme Dizisi": "İyileştirme",
            "Günlük Görev Dizisi": "Günlük Görevler",
            "Kutu Dizisi": "Kutu",
            "Anahtar Dizisi": "Anahtar",
            "Asker Hasat Dizisi": "Asker",
            "Mesaj Kontrolü": "Mesaj",
            "Savaş Dizisi": "Savaş",
            "İttifak Dizisi": "İttifak",
            "Su Adası Dizisi": "Su Adası",
            "Geri Dönüş Dizisi": "Geri Dönüş",
            "Asker Baş Dizisi": "Asker Baş",
            "Dünya Heal Dizisi": "Dünya Heal",
            "Fetih Dizisi": "Fetih",
            "İsyancı Dizisi": "İsyancı",
        }
        for key, value in task_categories.items():
            if key in original_message:
                task_category = value
                break

        user_friendly_messages = {
            # Dünya Heal
            "[Dünya Heal] Dizisi başlatıldı": f"✅ [{task_category}] Dünya iyileştirme işlemi başladı.",
            "[Dünya Heal] Sekansı başarıyla tamamlandı.": f"✅ [{task_category}] Dünya iyileştirme tamamlandı.",
            "[Dünya Heal] Sekansı tamamlanamadı veya görsel bulunamadı.": f"❌ [{task_category}] Dünya iyileştirme yapılamadı.",
            "[Dünya Heal] Hiçbir dünya heal görseli bulunamadı.": f"❌ [{task_category}] Dünya iyileştirme görseli bulunamadı.",

            # İyileştirme
            "[İyileştirme] Dizisi başlatıldı": f"✅ [{task_category}] İyileştirme başladı.",
            "[İyileştirme] Sekansı başarıyla tamamlandı.": f"✅ [{task_category}] İyileştirme tamamlandı.",
            "[İyileştirme] Sekansı tamamlanamadı veya görsel bulunamadı.": f"❌ [{task_category}] İyileştirme yapılamadı.",
            "[İyileştirme] Hiçbir iyileştirme görseli bulunamadı.": f"❌ [{task_category}] İyileştirilecek asker bulunamadı.",

            # Günlük Görevler
            "[Günlük Görevler] Dizisi başlatıldı": f"✅ [{task_category}] Günlük görevler başladı.",
            "[Günlük Görevler] Sekansı başarıyla tamamlandı.": f"✅ [{task_category}] Günlük görevler tamamlandı.",
            "[Günlük Görevler] Sekansı tamamlanamadı veya görsel bulunamadı.": f"❌ [{task_category}] Günlük görev yapılamadı.",
            "[Günlük Görevler] Hiçbir günlük görev görseli bulunamadı.": f"❌ [{task_category}] Günlük görev bulunamadı.",

            # Kutu
            "[Kutu] Dizisi başlatıldı": f"✅ [{task_category}] Kutu açma başladı.",
            "[Kutu] Sekansı başarıyla tamamlandı.": f"✅ [{task_category}] Kutu açma tamamlandı.",
            "[Kutu] Sekansı tamamlanamadı veya görsel bulunamadı.": f"❌ [{task_category}] Kutu açma yapılamadı.",
            "[Kutu] Hiçbir kutu görseli bulunamadı.": f"❌ [{task_category}] Kutu bulunamadı.",

            # Anahtar
            "[Anahtar] Dizisi başlatıldı": f"✅ [{task_category}] Anahtar sandığı açma başladı.",
            "[Anahtar] Sekansı başarıyla tamamlandı.": f"✅ [{task_category}] Anahtar sandığı açma tamamlandı.",
            "[Anahtar] Sekansı tamamlanamadı veya görsel bulunamadı.": f"❌ [{task_category}] Anahtar sandığı açma yapılamadı.",
            "[Anahtar] Hiçbir anahtar görseli bulunamadı.": f"❌ [{task_category}] Anahtar sandığı bulunamadı.",

            # Asker Hasat
            "[Asker Hasat] Dizisi başlatıldı": f"✅ [{task_category}] Asker hasadı başladı.",
            "[Asker Hasat] Sekansı başarıyla tamamlandı.": f"✅ [{task_category}] Asker hasadı tamamlandı.",
            "[Asker Hasat] Sekansı tamamlanamadı veya görsel bulunamadı.": f"❌ [{task_category}] Asker hasadı yapılamadı.",
            "[Asker Hasat] Hiçbir asker hasat görseli bulunamadı.": f"❌ [{task_category}] Asker hasadı yapılamadı.",

            # Bekçi Kulesi
            "[Bekçi Kulesi] Dizisi başlatıldı": f"✅ [{task_category}] Bekçi kulesi görevi başladı.",
            "[Bekçi Kulesi] Sekansı başarıyla tamamlandı.": f"✅ [{task_category}] Bekçi kulesi görevi tamamlandı.",
            "[Bekçi Kulesi] Sekansı tamamlanamadı veya görsel bulunamadı.": f"❌ [{task_category}] Bekçi kulesi görevi yapılamadı.",
            "[Bekçi Kulesi] Hiçbir bekçi kulesi görseli bulunamadı.": f"❌ [{task_category}] Bekçi kulesi görevi bulunamadı.",

            # Mesaj Kontrolü
            "Mesaj kontrolü başlatıldı...": f"✅ [{task_category}] Mesaj kontrolü başladı.",
            "Mesaj bulundu ve işlendi": f"✅ [{task_category}] Mesaj işlendi.",
            "Mesaj işlemi başarılı": f"✅ [{task_category}] Mesaj işlemi başarılı.",
            "Hiçbir mesaj bulunamadı.": f"❌ [{task_category}] Mesaj bulunamadı.",

            # Savaş Görevleri
            "Savaş görevleri başlatıldı...": f"✅ [{task_category}] Savaş görevleri başladı.",
            "Savaş menüsü açıldı": f"✅ [{task_category}] Savaş menüsü açıldı.",
            "Savaş işlemi başarılı": f"✅ [{task_category}] Savaş işlemi başarılı.",
            "Hiçbir savaş görevi yapılamadı.": f"❌ [{task_category}] Savaş görevi yapılamadı.",

            # İttifak Görevleri
            "İttifak görevleri başlatıldı...": f"✅ [{task_category}] İttifak görevleri başladı.",
            "İttifak işlemi başarılı": f"✅ [{task_category}] İttifak işlemi başarılı.",
            "Hiçbir ittifak görevi yapılamadı.": f"❌ [{task_category}] İttifak görevi yapılamadı.",

            # Su Adası
            "Su Adası görevleri başlatıldı...": f"✅ [{task_category}] Su Adası görevleri başladı.",
            "Su Adası menüsü açıldı": f"✅ [{task_category}] Su Adası menüsü açıldı.",
            "Su Adası işlemi başarılı": f"✅ [{task_category}] Su Adası işlemi başarılı.",
            "Su Adası görevleri başarıyla tamamlandı.": f"✅ [{task_category}] Su Adası görevleri tamamlandı.",
            "Su Adası girişi bulunamadı veya işlem tamamlanamadı.": f"❌ [{task_category}] Su Adası görevi tamamlanamadı.",

            # Asker Basma
            "Asker basma başlatıldı...": f"✅ [{task_category}] Asker basma başladı.",
            "Asker basma başarılı": f"✅ [{task_category}] Asker basma başarılı.",
            "Hiçbir asker basma işlemi yapılamadı.": f"❌ [{task_category}] Asker basma yapılamadı.",

            # Fetih Görevleri
            "[Fetih] Dizisi başlatıldı": f"✅ [{task_category}] Fetih görevi başladı.",
            "[Fetih] Dizisi başarıyla tamamlandı.": f"✅ [{task_category}] Fetih görevi tamamlandı.",
            "[Fetih] Hiçbir fetih görseli bulunamadı veya işlem tamamlanamadı.": f"❌ [{task_category}] Fetih görevi yapılamadı.",

            # İsyancı Görevleri
            "[İsyancı] Dizisi başlatıldı": f"✅ [{task_category}] İsyancı görevi başladı.",
            "[İsyancı] 's1.png' bulundu ve tıklandı.": f"✅ [{task_category}] İsyancı 's1' bulundu ve tıklandı.",
            "[İsyancı] 's2.png' bulundu ve tıklandı.": f"✅ [{task_category}] İsyancı 's2' bulundu ve tıklandı.",
            "[İsyancı] Boş tıklama yapıldı (s2.png sonrası).": f"ℹ️ [{task_category}] İsyancı 's2' sonrası boş tıklama yapıldı.",
            "[İsyancı] 's3.png' bulundu ve tıklandı.": f"✅ [{task_category}] İsyancı 's3' bulundu ve tıklandı.",
            "[İsyancı] Dizisi tamamlandı": f"✅ [{task_category}] İsyancı görevi tamamlandı.",
            "[İsyancı] Hiçbir isyancı görseli bulunamadı veya işlem tamamlanamadı.": f"❌ [{task_category}] İsyancı görevi yapılamadı.",
            "[İsyancı] 's1.png' bulunamadı.": f"❌ [{task_category}] İsyancı 's1' bulunamadı.",
            "[İsyancı] 's2.png' bulunamadı.": f"❌ [{task_category}] İsyancı 's2' bulunamadı.",
            "[İsyancı] 's3.png' bulunamadı confidence=": f"❌ [{task_category}] İsyancı 's3' bulunamadı.",
            "[İsyancı] Confidence çok düşük. s3.png için.": f"⚠️ [{task_category}] İsyancı 's3' için güven seviyesi çok düşük.",

            # Genel Bilgi Mesajları (Çok Detaylı Olmayanlar)
            "Fare konumu alındı": f"ℹ️ [{task_category}] Fare konumu alındı.",
            "Ayarlar 'config.json' dosyasına başarıyla kaydedildi.": "✅ [Ayarlar] Ayarlar kaydedildi.",
            "Ayarlar 'config.json' dosyasından başarıyla yüklendi.": "✅ [Ayarlar] Ayarlar yüklendi.",
            "'config.json' dosyası bulunamadı. Boş ayarlar döndürülüyor.": "⚠️ [Ayarlar] Ayar dosyası bulunamadı, varsayılan ayarlar kullanılıyor.",
            "Kullanıcı verileri 'user_data.json' dosyasına başarıyla kaydedildi.": "✅ [Lisans] Kullanıcı verileri kaydedildi.",
            "Kullanıcı verileri 'user_data.json' dosyasından başarıyla yüklendi.": "✅ [Lisans] Kullanıcı verileri yüklendi.",
            "'user_data.json' dosyası bulunamadı. Boş veri döndürülüyor.": "⚠️ [Lisans] Kullanıcı veri dosyası bulunamadı.",
            "Yeni sürüm bulundu": "✅ [Güncelleme] Yeni sürüm mevcut!",
            "Uygulama zaten güncel": "✅ [Güncelleme] Botunuz güncel.",
            "Güncelleme indiriliyor": "ℹ️ [Güncelleme] Güncelleme indiriliyor...",
            "Güncelleme başarıyla indirildi ve yüklendi.": "✅ [Güncelleme] Güncelleme tamamlandı.",
            "BOT_API_KEY tanımlanmamış. Lisans API isteği gönderilemiyor.": "❌ [API] API anahtarı eksik, geliştirici ile iletişime geçin.",
            "Lisans aktivasyon isteği gönderiliyor": "ℹ️ [Lisans] Lisans aktivasyonu kontrol ediliyor...",
            "Lisans aktivasyon yanıtı": "ℹ️ [Lisans] Lisans sunucusundan yanıt alındı.",
            "Lisans durumu kontrol isteği gönderiliyor": "ℹ️ [Lisans] Lisans durumu kontrol ediliyor...",
            "Lisans durumu kontrol yanıtı": "ℹ️ [Lisans] Lisans sunucusundan yanıt alındı.",
            "Yerel lisans aktif. Kalan süre": "✅ [Lisans] Lisans aktif.",
            "Yerel lisans süresi dolmuş.": "❌ [Lisans] Lisans süresi doldu.",
            "Periyodik lisans sunucu kontrolü yapılıyor...": "ℹ️ [Lisans] Lisans durumu periyodik olarak kontrol ediliyor...",
            "Lisans durumu API'den güncellendi.": "✅ [Lisans] Lisans durumu sunucudan güncellendi.",
            "Lisans durumu API'den alınamadı": "❌ [Lisans] Lisans durumu sunucudan alınamadı.",
            "Bot başlatıldı.": "✅ [Bot] Bot başlatıldı.",
            "Bot durduruldu.": "❌ [Bot] Bot durduruldu.",
            "Oyun alanı kaydedildi": "✅ [Kurulum] Oyun alanı kaydedildi.",
            "Oyun alanı yüklendi.": "✅ [Kurulum] Oyun alanı yüklendi.",
            "Oyun alanı seçilmedi veya geçersiz.": "⚠️ [Kurulum] Oyun alanı seçilmedi veya geçersiz.",
            "Son çare koordinatları kaydedildi": "✅ [Kurulum] Son çare koordinatları kaydedildi.",
            "Yüklenecek ayar bulunamadı.": "⚠️ [Ayarlar] Kayıtlı ayar bulunamadı.",
            "TipsUI nesnesi yeniden oluşturuldu.": "ℹ️ [İpuçları] İpuçları arayüzü güncellendi.",
            "İpuçları butonu başlık çubuğuna eklendi.": "✅ [İpuçları] İpuçları butonu eklendi.",
            "Geri dönülüyor...": f"ℹ️ [{task_category}] Geri dönülüyor...",
            "Zaten ana ekranda": f"✅ [{task_category}] Zaten ana ekranda.",
            "Geri dönüş başarılı": f"✅ [{task_category}] Geri dönüş başarılı.",
            "Son çare tıklaması gerçekleştiriliyor...": f"ℹ️ [{task_category}] Tıkanma durumunda son çare tıklaması yapılıyor...",
            "Son çare tıklaması yapıldı": f"✅ [{task_category}] Son çare tıklaması yapıldı.",
            "Ana ekrana dönüldü": f"✅ [{task_category}] Ana ekrana dönüldü.",
            "Ana ekran resimleri eksik veya geçersiz.": f"❌ [{task_category}] Ana ekran resimleri eksik veya geçersiz. Lütfen Kurulum sekmesinden seçin.",
            "Tüm geri dönüş denemeleri başarısız oldu.": f"❌ [{task_category}] Bot ana ekrana dönemedi. Lütfen manuel kontrol edin.",
            "Ana ekran (gündüz) resmi güncellendi": "✅ [Kurulum] Ana ekran (gündüz) resmi güncellendi.",
            "Ana ekran (gece) resmi güncellendi": "✅ [Kurulum] Ana ekran (gece) resmi güncellendi.",
            "Güncelleme kontrolü zaman aşımına uğradı.": "❌ [Güncelleme] Güncelleme sunucusuna ulaşılamadı (Zaman aşımı).",
            "Güncelleme sunucusuna bağlanılamadı.": "❌ [Güncelleme] Güncelleme sunucusuna bağlanıladı. İnternet bağlantınızı kontrol edin.",
            "Güncelleme bilgisi okunurken hata: Geçersiz JSON yanıtı alındı.": "❌ [Güncelleme] Güncelleme bilgisi alınırken hata oluştu.",
            "İndirilen dosya geçerli bir zip dosyası değil.": "❌ [Güncelleme] İndirilen güncelleme dosyası bozuk.",
            "Lisans aktivasyonu: Sunucudan geçersiz tarih formatı alındı:": "❌ [Lisans] Lisans tarihi formatı hatası. Geliştirici ile iletişime geçin.",
            "Lisans aktivasyonu başarısız:": "❌ [Lisans] Lisans aktivasyonu başarısız oldu.",
            "API ile iletişim hatası": "❌ [API] Sunucu ile iletişim hatası.",
            "API'den geçersiz cevap alındı (JSON hatası).": "❌ [API] Sunucudan geçersiz yanıt alındı.",
            "Beklenmeyen hata": "❌ [Genel] Beklenmeyen bir hata oluştu.",
            "Geçersiz oyun alanı seçildi": "❌ [Kurulum] Geçersiz oyun alanı seçimi yapıldı.",
            "Önizleme ekran görüntüsü alınamadı": "❌ [Kurulum] Oyun alanı önizlemesi alınamadı.",
            "Lisans kodu aktive edilirken veritabanı hatası": "❌ [Lisans] Lisans veritabanı hatası. Geliştirici ile iletişime geçin.",
            "Geçersiz lisans kodu denemesi": "❌ [Lisans] Geçersiz lisans kodu denemesi.",
            "Geçersiz eylem isteği": "❌ [API] Geçersiz API eylemi.",
            "Geri düğmesi bulunamadı": f"⚠️ [{task_category}] Geri düğmesi bulunamadı.",
            "Son çare tıklaması başarısız": f"❌ [{task_category}] Son çare tıklaması başarısız oldu.",
            "Son çare sonrası ana ekran bulunamadı.": f"❌ [{task_category}] Son çare sonrası ana ekrana dönülemedi.",
            "Güncelleme notları penceresi kapatıldı.": "ℹ️ [Güncelleme] Güncelleme notları kapatıldı.",
            "Güncelleme notları v": "ℹ️ [Güncelleme] Güncelleme notları gösteriliyor.",
            "Yeni sürüm notları gösteriliyor": "ℹ️ [Güncelleme] Yeni sürüm notları gösteriliyor.",
            "Güncelleme notları v{self.latest_version} için 'Tekrar gösterme' seçildi.": "ℹ️ [Güncelleme] Bu sürüm notları tekrar gösterilmeyecek.",
            "Güncelleme notları v{self.latest_version} için 'Tekrar gösterme' iptal edildi.": "ℹ️ [Güncelleme] Bu sürüm notları tekrar gösterilecek.",
            "Güncelleme notları v{latest_version} daha önce gösterilmiş veya mevcut sürümle aynı.": "ℹ️ [Güncelleme] Güncel sürüm notları daha önce gösterildi.",
            "Güncelleme hazırlandı ve güncelleyici başlatıldı. Uygulama kapatılıyor...": "✅ [Güncelleme] Güncelleme hazırlandı, uygulama yeniden başlatılıyor.",
            "Güncelleme hazırlığı sırasında bir hata oluştu.": "❌ [Güncelleme] Güncelleme hazırlığı başarısız oldu.",
            "Güncelleme başlatılırken beklenmeyen hata:": "❌ [Güncelleme] Güncelleme başlatılırken beklenmeyen hata.",


            # PyAutoGUI detaylarını sadeleştirme
            "görseli bulundu ve tıklandı": "✅ [Otomasyon] Görsel bulundu ve tıklandı.",
            "görseli bulunamadı": "⚠️ [Otomasyon] Görsel bulunamadı.",
            "görselinin merkezi bulundu": "✅ [Otomasyon] Görsel konumu belirlendi.",
            "görseline tıklanırken beklenmeyen hata": "❌ [Otomasyon] Tıklama hatası.",
            "görseli aranırken beklenmeyen hata": "❌ [Otomasyon] Görsel arama hatası.",
            "Confidence çok düşük.": "⚠️ [Otomasyon] Eşleşme güven seviyesi düşük.",
            "İkinci tıklama": "ℹ️ [Otomasyon] İkinci tıklama yapılıyor.",
            "Boş tıklama yapıldı": "ℹ️ [Otomasyon] Boş tıklama yapıldı.",
            "Henüz zamanı gelmedi, kalan süre": "ℹ️ [Zamanlama] Henüz zamanı gelmedi.",
            "Rapid click için": "ℹ️ [Otomasyon] Hızlı tıklama yapılıyor.",
            "Geri düğmesi dosyası eksik": "❌ [Dosya] Geri düğmesi görseli eksik.",
        }
        
        # Orijinal mesajda bir anahtar kelime arayarak en uygun kullanıcı dostu mesajı bul
        display_message = original_message
        found_match = False
        for key, value in user_friendly_messages.items():
            if key in original_message:
                display_message = value
                found_match = True
                break
        
        # Eğer özel bir eşleşme bulunamazsa, yine de task_category'yi ekle
        if not found_match:
            display_message = f"[{task_category}] {original_message}"

        # Queue'ya log entry ekle
        self.log_queue.put(record)

