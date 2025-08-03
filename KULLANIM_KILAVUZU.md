# 🤖 King Bot Pro v2.0.0 - Kullanım Kılavuzu

## 📋 İçindekiler
1. [Hızlı Başlangıç](#hızlı-başlangıç)
2. [Emülatör Kurulumu](#emülatör-kurulumu)
3. [Bot Konfigürasyonu](#bot-konfigürasyonu)
4. [Özellikler](#özellikler)
5. [Sorun Giderme](#sorun-giderme)
6. [İpuçları](#ipuçları)

---

## 🚀 Hızlı Başlangıç

### 1. İlk Kurulum
```bash
# Kısayol oluşturmak için (opsiyonel)
python create_shortcuts.py

# Uygulamayı başlatmak için
start.bat
# veya
python start.py
```

### 2. İlk Çalıştırma
1. `start.bat` dosyasını çift tıklayın
2. Gerekli kütüphaneler otomatik yüklenecek
3. Emülatörler otomatik algılanacak
4. Modern arayüz açılacak

---

## 🎮 Emülatör Kurulumu

### Desteklenen Emülatörler
- **BlueStacks** (Önerilen)
- **MEmu** 
- **LDPlayer**
- **NoxPlayer**
- **GameLoop**
- **MSI App Player**

### Emülatör Ayarları
```json
Önerilen Ayarlar:
- Çözünürlük: 1280x720 (16:9)
- DPI: 240
- RAM: 4GB+
- CPU Çekirdek: 4
- VT açık olmalı
```

### BlueStacks Özel Ayarlar
1. Gelişmiş → Performans → GPU: OpenGL
2. Gelişmiş → Aygıt → Telefon modeli: Galaxy S9+
3. Gelişmiş → Aygıt → Android sürümü: Android 9

---

## ⚙️ Bot Konfigürasyonu

### Ana Ayarlar
```
Genel Sekmesi:
✅ Emülatör seçimi
✅ Çözünürlük ayarı  
✅ Dil tercihi
✅ Tema seçimi
```

### Gelişmiş Ayarlar
```
Performans Sekmesi:
- Görüntü tanıma hassasiyeti
- İşlem hızı
- Bellek optimizasyonu
- CPU kullanımı
```

### Güvenlik Ayarları
```
Güvenlik Sekmesi:
- Rastgele gecikmeler
- İnsan benzeri hareketler
- Anti-detection koruması
- Proxy desteği
```

---

## 🎯 Özellikler

### 🔥 Ana Özellikler
- **Akıllı Emülatör Algılama**: Otomatik emülatör tespiti
- **Modern Arayüz**: Material Design tabanlı UI
- **Gelişmiş Görev Yönetimi**: Öncelikli görev sırası
- **Performans İzleme**: Gerçek zamanlı sistem durumu
- **Akıllı Hata Yönetimi**: Otomatik hata düzeltme

### 🤖 Bot Yetenekleri
- **Asker Eğitimi**: Otomatik asker üretimi
- **Kaynak Toplama**: Akıllı kaynak yönetimi
- **Savaş Yönetimi**: Otomatik saldırı sistemi
- **İttifak İşlemleri**: Otomatik ittifak yardımı
- **Bekçi Kulesi**: Otomatik savunma
- **Şehir Gelişimi**: Akıllı yapı yükseltme

### 📊 İstatistikler
- Gerçek zamanlı performans grafikleri
- Günlük/haftalık/aylık raporlar
- Kaynak üretim analizi
- Savaş başarı oranları

---

## 🔧 Sorun Giderme

### ❌ Yaygın Sorunlar

#### Emülatör Algılanmıyor
```bash
Çözüm:
1. Emülatörün çalıştığından emin olun
2. Admin yetkisiyle çalıştırın
3. Emülatör yolunu manuel ekleyin
4. Antivirus programını kontrol edin
```

#### Görüntü Tanıma Sorunları
```bash
Çözüm:
1. Emülatör çözünürlüğünü kontrol edin
2. DPI ayarını 240 yapın
3. Oyun dilini Türkçe yapın
4. Hassasiyet ayarını değiştirin
```

#### Performans Sorunları
```bash
Çözüm:
1. Sistem optimizasyonu çalıştırın
2. RAM kullanımını kontrol edin
3. Arka plan uygulamalarını kapatın
4. VT teknolojisini açın
```

### 🚨 Acil Durum Kurtarma
```bash
# Ayarları sıfırla
python -c "import os; os.remove('config_modern.json')"

# Cache temizle
python -c "import shutil, os; shutil.rmtree('__pycache__', True)"

# Log temizle
python -c "import os; [os.remove(f) for f in ['bot_logs.log', 'optimizer.log', 'crash_log.txt'] if os.path.exists(f)]"
```

---

## 💡 İpuçları ve Püf Noktaları

### 🎯 Verimlilik İpuçları
1. **Emülatör Optimizasyonu**
   - VT teknolojisini mutlaka açın
   - Gereksiz uygulamaları kapatın
   - RAM'i uygun ayarlayın

2. **Bot Optimizasyonu**
   - Rastgele gecikmeleri açın
   - Performans modunu ayarlayın
   - Görev önceliklerini belirleyin

3. **Güvenlik İpuçları**
   - Uzun süreli kullanımdan kaçının
   - Düzenli molalar verin
   - İnsan benzeri davranış açın

### 🔄 Bakım ve Güncelleme
```bash
# Güncellemeleri kontrol et
python -c "from version import __version__; print(f'Mevcut sürüm: {__version__}')"

# Sistem durumunu kontrol et
python -c "from utils import get_system_info; print(get_system_info())"

# Performans testi
python test_suite.py
```

### 📈 Performans Artırma
1. **Sistem Seviyesi**
   - Windows güncellemelerini yapın
   - Disk temizliği yapın
   - Registry temizliği yapın

2. **Emülatör Seviyesi**
   - GPU sürücülerini güncelleyin
   - Emülatör cache'ini temizleyin
   - Optimal ayarları kullanın

3. **Bot Seviyesi**
   - Log dosyalarını temizleyin
   - Ayarları optimize edin
   - Gereksiz özellikleri kapatın

---

## 📞 Destek ve İletişim

### 🌐 Sosyal Medya
- **Discord**: [Discord Linki]
- **Telegram**: [Telegram Linki]

### 📧 Destek
- **E-mail**: support@kingbotpro.com
- **Website**: www.kingbotpro.com

### 🐛 Hata Bildirimi
```bash
# Hata raporunu oluştur
python -c "
import sys, traceback, datetime
with open('error_report.txt', 'w') as f:
    f.write(f'King Bot Pro v2.0.0 Error Report\n')
    f.write(f'Date: {datetime.datetime.now()}\n')
    f.write(f'Python: {sys.version}\n')
    f.write('Please describe your issue here...\n')
print('Error report created: error_report.txt')
"
```

---

## 📄 Lisans ve Yasal Uyarılar

### ⚖️ Kullanım Koşulları
- Bu bot yalnızca eğitim amaçlıdır
- Oyun kurallarına uygun kullanın
- Kendi sorumluluğunuzda kullanın
- Ticari kullanım yasaktır

### 🔒 Gizlilik
- Hiçbir kişisel veri toplanmaz
- Tüm veriler yerel olarak saklanır
- İnternet bağlantısı sadece güncellemeler için kullanılır

---

**🎉 King Bot Pro v2.0.0 ile oyun keyfini çıkarın!**

*Son güncelleme: Aralık 2024*
