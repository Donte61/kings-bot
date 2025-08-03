"""
King Bot Pro v2.0.0 - Desktop Kısayolu Oluşturucu
"""

import os
import sys
import winshell
from win32com.client import Dispatch

def create_desktop_shortcut():
    """Masaüstüne kısayol oluştur"""
    try:
        desktop = winshell.desktop()
        
        # Kısayol yolu
        shortcut_path = os.path.join(desktop, "King Bot Pro v2.0.0.lnk")
        
        # Hedef dosya
        target = os.path.join(os.getcwd(), "start.bat")
        
        # Çalışma dizini
        working_dir = os.getcwd()
        
        # Icon (varsa)
        icon_path = os.path.join(os.getcwd(), "app_icon.ico")
        
        # Kısayol oluştur
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = working_dir
        shortcut.Description = "King Bot Pro v2.0.0 - Modern Bot Uygulaması"
        
        if os.path.exists(icon_path):
            shortcut.IconLocation = icon_path
            
        shortcut.save()
        
        print(f"✅ Masaüstü kısayolu oluşturuldu: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"❌ Kısayol oluşturulamadı: {e}")
        return False

def create_start_menu_shortcut():
    """Başlat menüsüne kısayol oluştur"""
    try:
        programs = winshell.programs()
        
        # Kısayol yolu
        shortcut_path = os.path.join(programs, "King Bot Pro v2.0.0.lnk")
        
        # Hedef dosya
        target = os.path.join(os.getcwd(), "start.bat")
        
        # Çalışma dizini
        working_dir = os.getcwd()
        
        # Icon (varsa)
        icon_path = os.path.join(os.getcwd(), "app_icon.ico")
        
        # Kısayol oluştur
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = working_dir
        shortcut.Description = "King Bot Pro v2.0.0 - Modern Bot Uygulaması"
        
        if os.path.exists(icon_path):
            shortcut.IconLocation = icon_path
            
        shortcut.save()
        
        print(f"✅ Başlat menüsü kısayolu oluşturuldu: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"❌ Başlat menüsü kısayolu oluşturulamadı: {e}")
        return False

def main():
    print("🔗 King Bot Pro v2.0.0 - Kısayol Oluşturucu")
    print("="*50)
    
    try:
        # Masaüstü kısayolu
        if create_desktop_shortcut():
            print("Masaüstü kısayolu başarıyla oluşturuldu!")
        
        # Başlat menüsü kısayolu  
        if create_start_menu_shortcut():
            print("Başlat menüsü kısayolu başarıyla oluşturuldu!")
            
        print("\n✅ Kısayol oluşturma işlemi tamamlandı!")
        print("Artık King Bot Pro'yu masaüstünden veya başlat menüsünden çalıştırabilirsiniz.")
        
    except Exception as e:
        print(f"❌ Kısayol oluşturma hatası: {e}")
        print("Manuel olarak start.bat dosyasını çalıştırabilirsiniz.")

if __name__ == "__main__":
    main()
    input("\nÇıkmak için Enter'a basın...")
