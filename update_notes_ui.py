import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import logging

class UpdateNotesUI:
    def __init__(self, parent, release_notes, latest_version, colors, save_callback):
        self.parent = parent
        self.release_notes = release_notes
        self.latest_version = latest_version
        self.colors = colors
        self.save_callback = save_callback # Kaydetme fonksiyonu
        self.do_not_show_again_var = tk.BooleanVar(value=False)
        self.notes_window = None
        self.setup_ui()

    def setup_ui(self):
        self.notes_window = tk.Toplevel(self.parent)
        self.notes_window.title(f"King Bot v{self.latest_version} - Güncelleme Notları")
        self.notes_window.geometry("600x500")
        self.notes_window.configure(bg=self.colors['background'])
        self.notes_window.resizable(True, True)

        # Pencereyi ekranın ortasına yerleştir
        self.notes_window.update_idletasks()
        x = self.notes_window.winfo_screenwidth() // 2 - self.notes_window.winfo_width() // 2
        y = self.notes_window.winfo_screenheight() // 2 - self.notes_window.winfo_height() // 2
        self.notes_window.geometry(f"+{x}+{y}")
        
        # Pencere kapatma olayını yakala
        self.notes_window.protocol("WM_DELETE_WINDOW", self.on_closing)

        ttk.Label(self.notes_window, text=f"Sürüm v{self.latest_version} Yenilikleri:",
                  font=("Helvetica", 14, "bold"), background=self.colors['background'],
                  foreground=self.colors['accent']).pack(pady=10)

        self.notes_text = ScrolledText(self.notes_window, height=15, state="disabled",
                                       bg=self.colors['frame'], fg=self.colors['text'],
                                       font=("Consolas", 10), relief="solid", bd=1)
        self.notes_text.pack(pady=5, padx=10, fill="both", expand=True)
        self.notes_text.config(state="normal")
        self.notes_text.insert(tk.END, self.release_notes)
        self.notes_text.config(state="disabled")

        checkbox_frame = ttk.Frame(self.notes_window, padding=5, style="TFrame")
        checkbox_frame.pack(pady=5, padx=10, fill="x")
        ttk.Checkbutton(checkbox_frame, text="Bu sürüm için tekrar gösterme",
                        variable=self.do_not_show_again_var,
                        command=self.toggle_do_not_show_again,
                        style="TCheckbutton").pack(side="left")

        close_button = ttk.Button(self.notes_window, text="Kapat", command=self.on_closing, style="TButton")
        close_button.pack(pady=10)

        self.notes_window.attributes("-topmost", True) # Pencereyi en üste getir
        self.notes_window.focus_set() # Pencereye odaklan

    def toggle_do_not_show_again(self):
        # Checkbox durumu değiştiğinde loglama yap
        if self.do_not_show_again_var.get():
            logging.info(f"Güncelleme notları v{self.latest_version} için 'Tekrar gösterme' seçildi.")
        else:
            logging.info(f"Güncelleme notları v{self.latest_version} için 'Tekrar gösterme' iptal edildi.")

    def on_closing(self):
        if self.do_not_show_again_var.get():
            self.save_callback(self.latest_version) # Sürümü kaydet
            logging.info(f"Güncelleme notları penceresi kapatıldı. v{self.latest_version} için tekrar gösterilmeyecek.")
        else:
            logging.info("Güncelleme notları penceresi kapatıldı.")
        self.notes_window.destroy()

    def show(self):
        self.notes_window.deiconify()

    def hide(self):
        self.notes_window.withdraw()

