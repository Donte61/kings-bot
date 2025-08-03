#!/usr/bin/env python3
"""
King Bot Pro v2.0.0 - Modern Edition
Hızlı Başlatma Script'i
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_requirements():
    """Gerekli kütüphaneleri kontrol et"""
    required = {
        'tkinter': 'tkinter',
        'PIL': 'Pillow',
        'cv2': 'opencv-python', 
        'numpy': 'numpy',
        'pyautogui': 'pyautogui',
        'psutil': 'psutil',
        'requests': 'requests'
    }
    
    missing = []
    
    for module, package in required.items():
        try:
            if module == 'PIL':
                from PIL import Image
            elif module == 'cv2':
                import cv2
            else:
                __import__(module)
        except ImportError:
            missing.append(package)
    
    return missing

def install_requirements():
    """Eksik kütüphaneleri yükle"""
    missing = check_requirements()
    
    if not missing:
        return True
        
    root = tk.Tk()
    root.withdraw()
    
    response = messagebox.askyesno(
        "Eksik Kütüphaneler",
        f"Şu kütüphaneler eksik:\n{', '.join(missing)}\n\n"
        "Otomatik olarak yüklensin mi?"
    )
    
    root.destroy()
    
    if response:
        try:
            for package in missing:
                print(f"Yükleniyor: {package}")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"Hata: {package} yüklenemedi")
                    return False
                    
            print("Tüm kütüphaneler başarıyla yüklendi!")
            return True
            
        except Exception as e:
            print(f"Yükleme hatası: {e}")
            return False
    
    return False

def main():
    """Ana başlatıcı"""
    print("🤖 King Bot Pro v2.0.0 - Modern Edition")
    print("="*50)
    
    # Gerekli kütüphaneleri kontrol et
    print("Kütüphaneler kontrol ediliyor...")
    
    if not install_requirements():
        print("❌ Gerekli kütüphaneler yüklenemedi!")
        input("Çıkmak için Enter'a basın...")
        return 1
    
    print("✅ Tüm gereksinimler karşılandı!")
    
    # Ana uygulamayı başlat
    try:
        print("Uygulama başlatılıyor...")
        from main import main as app_main
        return app_main()
        
    except ImportError as e:
        print(f"❌ Modül yükleme hatası: {e}")
        print("Lütfen tüm dosyaların mevcut olduğundan emin olun.")
        input("Çıkmak için Enter'a basın...")
        return 1
        
    except Exception as e:
        print(f"❌ Başlatma hatası: {e}")
        input("Çıkmak için Enter'a basın...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
