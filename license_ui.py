import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from enhanced_utils import activate_license_code, check_license_status, save_user_data, load_user_data, open_url

class ModernLicenseUI:
    """Modern lisans aktivasyon arayüzü"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.setup_window()
        self.create_interface()
        
    def setup_window(self):
        """Pencere ayarları"""
        self.window.title("King Bot Pro - Lisans Aktivasyonu")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        self.window.configure(bg="#f8f9fa")
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"500x600+{x}+{y}")
        
        # Modal dialog
        if self.parent:
            self.window.transient(self.parent)
            self.window.grab_set()
            
        # Icon
        try:
            self.window.iconbitmap("app_icon.ico")
        except:
            pass
            
    def create_interface(self):
        """Arayüzü oluştur"""
        # Ana container
        main_frame = tk.Frame(self.window, bg="#f8f9fa")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        self.create_header(main_frame)
        
        # License info
        self.create_license_info(main_frame)
        
        # License input
        self.create_license_input(main_frame)
        
        # Buttons
        self.create_buttons(main_frame)
        
        # Footer
        self.create_footer(main_frame)
        
    def create_header(self, parent):
        """Başlık bölümü"""
        header_frame = tk.Frame(parent, bg="#f8f9fa")
        header_frame.pack(fill="x", pady=(0, 30))
        
        # Logo placeholder
        logo_frame = tk.Frame(header_frame, bg="#3498db", width=80, height=80)
        logo_frame.pack(pady=(0, 20))
        logo_frame.pack_propagate(False)
        
        logo_label = tk.Label(logo_frame, text="👑", font=("Segoe UI", 32), 
                             bg="#3498db", fg="white")
        logo_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title_label = tk.Label(header_frame, text="King Bot Pro", 
                              font=("Segoe UI", 24, "bold"),
                              bg="#f8f9fa", fg="#2c3e50")
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Lisans Aktivasyonu Gerekli",
                                 font=("Segoe UI", 12),
                                 bg="#f8f9fa", fg="#7f8c8d")
        subtitle_label.pack(pady=(5, 0))
        
    def create_license_info(self, parent):
        """Lisans bilgi bölümü"""
        info_frame = tk.LabelFrame(parent, text="Lisans Bilgileri", 
                                  font=("Segoe UI", 12, "bold"),
                                  bg="#f8f9fa", fg="#2c3e50",
                                  relief="groove", bd=2)
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_text = """
🔐 King Bot Pro kullanmak için geçerli bir lisans kodu gereklidir.

✅ Lisans Özellikleri:
• Tam özellik erişimi
• 7/24 teknik destek
• Ücretsiz güncellemeler
• 3 cihaza kadar kurulum

📧 Lisans satın almak için:
• Discord sunucumuz: discord.gg/pJ8Sf464
• Telegram kanalımız: t.me/+wHPg9nJt1qljMDFk
• E-posta: support@kingbotpro.com
        """
        
        info_label = tk.Label(info_frame, text=info_text.strip(),
                             font=("Segoe UI", 10),
                             bg="#f8f9fa", fg="#34495e",
                             justify="left")
        info_label.pack(padx=15, pady=15)
        
    def create_license_input(self, parent):
        """Lisans girişi bölümü"""
        input_frame = tk.LabelFrame(parent, text="Lisans Kodu", 
                                   font=("Segoe UI", 12, "bold"),
                                   bg="#f8f9fa", fg="#2c3e50",
                                   relief="groove", bd=2)
        input_frame.pack(fill="x", pady=(0, 20))
        
        # License key entry
        self.license_var = tk.StringVar()
        
        tk.Label(input_frame, text="Lisans kodunuzu girin:",
                font=("Segoe UI", 10),
                bg="#f8f9fa", fg="#2c3e50").pack(anchor="w", padx=15, pady=(15, 5))
        
        entry_frame = tk.Frame(input_frame, bg="#f8f9fa")
        entry_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.license_entry = tk.Entry(entry_frame,
                                     textvariable=self.license_var,
                                     font=("Consolas", 12),
                                     width=40,
                                     relief="solid",
                                     bd=1)
        self.license_entry.pack(side="left", fill="x", expand=True)
        
        # Format example
        example_label = tk.Label(input_frame, 
                                text="Örnek: KBPRO-XXXXX-XXXXX-XXXXX-XXXXX",
                                font=("Segoe UI", 9),
                                bg="#f8f9fa", fg="#95a5a6")
        example_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Load existing license if any
        self.load_existing_license()
        
    def create_buttons(self, parent):
        """Buton bölümü"""
        button_frame = tk.Frame(parent, bg="#f8f9fa")
        button_frame.pack(fill="x", pady=(0, 20))
        
        # Activate button
        self.activate_btn = tk.Button(button_frame,
                                     text="🔓 Lisansı Aktive Et",
                                     font=("Segoe UI", 12, "bold"),
                                     bg="#27ae60",
                                     fg="white",
                                     relief="flat",
                                     padx=20,
                                     pady=10,
                                     cursor="hand2",
                                     command=self.activate_license)
        self.activate_btn.pack(side="left", padx=(0, 10))
        
        # Check button
        check_btn = tk.Button(button_frame,
                             text="🔍 Lisansı Kontrol Et",
                             font=("Segoe UI", 12),
                             bg="#3498db",
                             fg="white",
                             relief="flat",
                             padx=20,
                             pady=10,
                             cursor="hand2",
                             command=self.check_license)
        check_btn.pack(side="left", padx=(0, 10))
        
        # Cancel button
        cancel_btn = tk.Button(button_frame,
                              text="❌ İptal",
                              font=("Segoe UI", 12),
                              bg="#e74c3c",
                              fg="white",
                              relief="flat",
                              padx=20,
                              pady=10,
                              cursor="hand2",
                              command=self.close_window)
        cancel_btn.pack(side="right")
        
        # Hover effects
        for btn in [self.activate_btn, check_btn, cancel_btn]:
            self.add_hover_effect(btn)
            
    def create_footer(self, parent):
        """Alt bölüm"""
        footer_frame = tk.Frame(parent, bg="#f8f9fa")
        footer_frame.pack(fill="x", pady=(20, 0))
        
        # Separator
        separator = tk.Frame(footer_frame, height=1, bg="#bdc3c7")
        separator.pack(fill="x", pady=(0, 15))
        
        # Social links
        social_frame = tk.Frame(footer_frame, bg="#f8f9fa")
        social_frame.pack()
        
        tk.Label(social_frame, text="Yardım ve Destek:",
                font=("Segoe UI", 10, "bold"),
                bg="#f8f9fa", fg="#2c3e50").pack()
        
        links_frame = tk.Frame(social_frame, bg="#f8f9fa")
        links_frame.pack(pady=(5, 0))
        
        # Discord link
        discord_btn = tk.Button(links_frame,
                               text="💬 Discord",
                               font=("Segoe UI", 9),
                               bg="#7289da",
                               fg="white",
                               relief="flat",
                               padx=15,
                               pady=5,
                               cursor="hand2",
                               command=lambda: open_url("https://discord.gg/pJ8Sf464"))
        discord_btn.pack(side="left", padx=(0, 10))
        
        # Telegram link
        telegram_btn = tk.Button(links_frame,
                                text="📱 Telegram",
                                font=("Segoe UI", 9),
                                bg="#0088cc",
                                fg="white",
                                relief="flat",
                                padx=15,
                                pady=5,
                                cursor="hand2",
                                command=lambda: open_url("https://t.me/+wHPg9nJt1qljMDFk"))
        telegram_btn.pack(side="left")
        
        # Add hover effects
        self.add_hover_effect(discord_btn, "#5b6eae", "#7289da")
        self.add_hover_effect(telegram_btn, "#0077b3", "#0088cc")
        
    def add_hover_effect(self, button, hover_color=None, normal_color=None):
        """Buton hover efekti ekle"""
        if not hover_color:
            current_bg = button.cget("bg")
            # Rengi biraz koyulaştır
            hover_color = self.darken_color(current_bg)
        if not normal_color:
            normal_color = button.cget("bg")
            
        def on_enter(e):
            button.config(bg=hover_color)
        
        def on_leave(e):
            button.config(bg=normal_color)
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
    def darken_color(self, color):
        """Rengi koyulaştır"""
        color_map = {
            "#27ae60": "#229954",
            "#3498db": "#2980b9",
            "#e74c3c": "#c0392b",
            "#7289da": "#5b6eae",
            "#0088cc": "#0077b3"
        }
        return color_map.get(color, color)
        
    def load_existing_license(self):
        """Mevcut lisansı yükle"""
        try:
            user_data = load_user_data()
            existing_license = user_data.get("license_key", "")
            if existing_license:
                self.license_var.set(existing_license)
        except Exception as e:
            logging.debug(f"Mevcut lisans yüklenemedi: {e}")
            
    def activate_license(self):
        """Lisansı aktive et"""
        license_key = self.license_var.get().strip()
        
        if not license_key:
            messagebox.showwarning("Uyarı", "Lütfen lisans kodunu girin!")
            self.license_entry.focus()
            return
            
        # Format check
        if not self.validate_license_format(license_key):
            messagebox.showerror("Geçersiz Format", 
                               "Lisans kodu formatı geçersiz!\n"
                               "Doğru format: KBPRO-XXXXX-XXXXX-XXXXX-XXXXX")
            return
            
        # Disable button during activation
        self.activate_btn.config(state="disabled", text="🔄 Aktive Ediliyor...")
        
        def activation_worker():
            try:
                result = activate_license_code(license_key)
                self.window.after(0, lambda: self.handle_activation_result(result))
            except Exception as e:
                error_msg = f"Aktivasyon hatası: {str(e)}"
                self.window.after(0, lambda: self.handle_activation_error(error_msg))
                
        threading.Thread(target=activation_worker, daemon=True).start()
        
    def handle_activation_result(self, result):
        """Aktivasyon sonucunu işle"""
        self.activate_btn.config(state="normal", text="🔓 Lisansı Aktive Et")
        
        if result.get("status") == "success":
            messagebox.showinfo("Başarılı!", 
                               "✅ Lisans başarıyla aktive edildi!\n"
                               "King Bot Pro kullanıma hazır.")
            
            # Save license data
            user_data = load_user_data()
            user_data["license_key"] = self.license_var.get().strip()
            user_data["license_status"] = "active"
            user_data["activation_date"] = result.get("activation_date")
            save_user_data(user_data)
            
            self.close_window()
            
        else:
            error_msg = result.get("message", "Bilinmeyen hata")
            messagebox.showerror("Aktivasyon Başarısız", 
                               f"❌ Lisans aktive edilemedi:\n{error_msg}")
            
    def handle_activation_error(self, error_msg):
        """Aktivasyon hatasını işle"""
        self.activate_btn.config(state="normal", text="🔓 Lisansı Aktive Et")
        messagebox.showerror("Bağlantı Hatası", 
                           f"❌ Aktivasyon sırasında hata oluştu:\n{error_msg}\n\n"
                           "Lütfen internet bağlantınızı kontrol edin.")
        
    def check_license(self):
        """Lisans durumunu kontrol et"""
        license_key = self.license_var.get().strip()
        
        if not license_key:
            messagebox.showwarning("Uyarı", "Lütfen lisans kodunu girin!")
            return
            
        def check_worker():
            try:
                result = check_license_status(license_key)
                self.window.after(0, lambda: self.handle_check_result(result))
            except Exception as e:
                error_msg = f"Kontrol hatası: {str(e)}"
                self.window.after(0, lambda: self.handle_check_error(error_msg))
                
        threading.Thread(target=check_worker, daemon=True).start()
        
    def handle_check_result(self, result):
        """Kontrol sonucunu işle"""
        if result.get("status") == "active":
            info_text = f"""
✅ Lisans Aktif

📋 Lisans Bilgileri:
• Durum: {result.get('status', 'Bilinmiyor')}
• Kullanıcı: {result.get('username', 'Bilinmiyor')}
• Son Geçerlilik: {result.get('expiry_date', 'Bilinmiyor')}
• Kalan Gün: {result.get('days_remaining', 'Bilinmiyor')}
            """
            messagebox.showinfo("Lisans Durumu", info_text.strip())
        else:
            error_msg = result.get("message", "Lisans geçersiz veya süresi dolmuş")
            messagebox.showerror("Lisans Geçersiz", f"❌ {error_msg}")
            
    def handle_check_error(self, error_msg):
        """Kontrol hatasını işle"""
        messagebox.showerror("Bağlantı Hatası", 
                           f"❌ Lisans kontrolü yapılamadı:\n{error_msg}")
        
    def validate_license_format(self, license_key):
        """Lisans formatını doğrula"""
        # KBPRO-XXXXX-XXXXX-XXXXX-XXXXX formatını kontrol et
        import re
        pattern = r'^KBPRO-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$'
        return re.match(pattern, license_key.upper()) is not None
        
    def close_window(self):
        """Pencereyi kapat"""
        if self.parent:
            self.window.grab_release()
        self.window.destroy()

# Backwards compatibility
LicenseUI = ModernLicenseUI

def show_license_dialog(parent=None):
    """Lisans dialog'unu göster"""
    return ModernLicenseUI(parent)

if __name__ == "__main__":
    # Test için
    app = ModernLicenseUI()
    app.window.mainloop()
