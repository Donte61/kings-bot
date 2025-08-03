import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
from utils import check_for_updates, download_and_extract_update
from version import __version__

class UpdateUI:
    def __init__(self, parent, update_status_label, update_progress_bar, update_progress_label, check_update_btn, install_update_btn, update_info_text):
        self.parent = parent
        self.update_status_label = update_status_label
        self.update_progress_bar = update_progress_bar
        self.update_progress_label = update_progress_label
        self.btn_check_update = check_update_btn
        self.btn_install_update = install_update_btn
        self.update_info_text = update_info_text

    def create_update_tab(self):
        update_frame = ttk.Frame(self.parent.notebook, padding="10")
        self.parent.notebook.add(update_frame, text="Güncelleme")

        tk.Label(update_frame, text="Güncelleme Kontrolü", font=("Helvetica", 14, "bold"), bg=self.parent.bg_color, fg=self.parent.text_color).pack(pady=10)
        
        self.update_status_label.pack(pady=5)
        self.update_progress_bar.pack(pady=10)
        self.update_progress_label.pack(pady=5)
        self.btn_check_update.pack(pady=5)
        self.btn_install_update.pack(pady=5)
        self.update_info_text.pack(pady=10, padx=5, fill="both", expand=True)

    def check_for_updates_manual(self):
        threading.Thread(target=self._check_for_updates_thread, args=(True,), daemon=True).start()

    def _check_for_updates_thread(self, is_manual):
        self.update_status_label.config(text="Güncelleme kontrol ediliyor...")
        self.btn_check_update.config(state=tk.DISABLED)
        self.btn_install_update.config(state=tk.DISABLED)
        self.update_info_text.configure(state="normal")
        self.update_info_text.delete(1.0, tk.END)
        self.update_info_text.configure(state="disabled")

        update_available = check_for_updates(__version__)
        if update_available:
            self.parent.latest_update_info = update_available
            self.update_status_label.config(text=f"Yeni versiyon: v{update_available['latest_version']}")
            self.btn_install_update.config(state=tk.NORMAL)
            self.update_info_text.configure(state="normal")
            release_notes = "\n".join([f"- {note}" for note in update_available['release_notes'].split("\n") if note.strip()])
            self.update_info_text.insert(tk.END, f"Yeni Versiyon: v{update_available['latest_version']}\n\nSürüm Notları:\n{release_notes}")
            self.update_info_text.configure(state="disabled")
            if is_manual:
                messagebox.showinfo("Güncelleme", f"Yeni versiyon: v{update_available['latest_version']}")
        else:
            self.update_status_label.config(text="Bot güncel.")
            if is_manual:
                messagebox.showinfo("Güncelleme", "Bot güncel.")
        self.btn_check_update.config(state=tk.NORMAL)

    def install_update(self):
        if hasattr(self.parent, 'latest_update_info'):
            if messagebox.askyesno("Güncelleme", f"v{self.parent.latest_update_info['latest_version']} yüklenecek. Devam?"):
                self.btn_install_update.config(state=tk.DISABLED)
                self.btn_check_update.config(state=tk.DISABLED)
                self.update_status_label.config(text="Güncelleme yükleniyor...")
                threading.Thread(target=self._perform_update_and_restart, args=(self.parent.latest_update_info['download_url'], self._update_progress_callback,), daemon=True).start()

    def _update_progress_callback(self, bytes_downloaded, total_size):
        self.parent.update_progress_queue.put((bytes_downloaded, total_size))

    def _perform_update_and_restart(self, download_url, progress_callback):
        if download_and_extract_update(download_url, progress_callback):
            messagebox.showinfo("Başarılı", "Güncelleme yüklendi. Botu yeniden başlatın.")
            self.parent.root.quit()
        else:
            messagebox.showerror("Hata", "Güncelleme başarısız.")
            self.btn_install_update.config(state=tk.NORMAL)
            self.btn_check_update.config(state=tk.NORMAL)
            self.update_status_label.config(text="Güncelleme hatası.")