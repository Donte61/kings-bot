"""
📊 King Bot Pro - Analitik Dashboard Sistemi
Gelişmiş performans takibi ve görsel analitikler
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import threading
import time
import sqlite3
import pandas as pd


class AnalyticsDashboard:
    """Gelişmiş analitik ve istatistik sistemi"""
    
    def __init__(self, parent_frame, colors):
        self.parent_frame = parent_frame
        self.colors = colors
        self.db_path = "analytics.db"
        self.init_database()
        self.setup_dashboard()
        
        # Real-time güncelleme
        self.update_interval = 5000  # 5 saniye
        self.start_real_time_updates()
    
    def init_database(self):
        """Analytics veritabanını başlat"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ana performans tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT,
                    task_type TEXT,
                    task_status TEXT,
                    execution_time REAL,
                    success_rate REAL,
                    error_message TEXT,
                    screenshots_taken INTEGER DEFAULT 0,
                    clicks_performed INTEGER DEFAULT 0,
                    cpu_usage REAL,
                    memory_usage REAL
                )
            ''')
            
            # Görev bazlı istatistikler
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE,
                    task_type TEXT,
                    total_executions INTEGER DEFAULT 0,
                    successful_executions INTEGER DEFAULT 0,
                    failed_executions INTEGER DEFAULT 0,
                    avg_execution_time REAL,
                    total_runtime REAL
                )
            ''')
            
            # AI öğrenme verileri
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_learning_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    detection_accuracy REAL,
                    processing_time REAL,
                    objects_detected INTEGER,
                    confidence_score REAL,
                    learning_data TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Database init hatası: {e}")
    
    def setup_dashboard(self):
        """Dashboard arayüzünü oluştur"""
        # Ana container
        main_container = tk.Frame(self.parent_frame, bg=self.colors['background'])
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Üst panel - Özet kartlar
        self.create_summary_cards(main_container)
        
        # Orta panel - Grafikler
        self.create_charts_panel(main_container)
        
        # Alt panel - Detaylı tablolar
        self.create_data_tables(main_container)
        
        # Sağ panel - Kontroller
        self.create_controls_panel(main_container)
    
    def create_summary_cards(self, parent):
        """Özet kartlarını oluştur"""
        cards_frame = tk.Frame(parent, bg=self.colors['background'])
        cards_frame.pack(fill="x", pady=(0, 20))
        
        # Kartları oluştur
        self.cards = {}
        card_configs = [
            {"title": "Toplam Görevler", "key": "total_tasks", "color": "#3498db", "icon": "📊"},
            {"title": "Başarı Oranı", "key": "success_rate", "color": "#2ecc71", "icon": "✅"},
            {"title": "Ortalama Süre", "key": "avg_time", "color": "#f39c12", "icon": "⏱️"},
            {"title": "Son 24 Saat", "key": "last_24h", "color": "#9b59b6", "icon": "📈"}
        ]
        
        for i, config in enumerate(card_configs):
            card = self.create_summary_card(cards_frame, config)
            card.grid(row=0, column=i, padx=10, sticky="ew")
            self.cards[config['key']] = card
        
        # Grid ağırlıkları
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)
    
    def create_summary_card(self, parent, config):
        """Tek bir özet kartı oluştur"""
        card_frame = tk.Frame(parent, bg=config['color'], relief="raised", bd=2)
        card_frame.configure(width=200, height=120)
        card_frame.pack_propagate(False)
        
        # İkon
        icon_label = tk.Label(card_frame, text=config['icon'], 
                             font=("Segoe UI", 24), bg=config['color'], fg="white")
        icon_label.pack(pady=(10, 5))
        
        # Değer
        value_label = tk.Label(card_frame, text="--", 
                              font=("Segoe UI", 18, "bold"), bg=config['color'], fg="white")
        value_label.pack()
        
        # Başlık
        title_label = tk.Label(card_frame, text=config['title'], 
                              font=("Segoe UI", 10), bg=config['color'], fg="white")
        title_label.pack(pady=(0, 10))
        
        # Güncelleme fonksiyonu için referans
        card_frame.value_label = value_label
        card_frame.config_data = config
        
        return card_frame
    
    def create_charts_panel(self, parent):
        """Grafik panelini oluştur"""
        charts_frame = tk.Frame(parent, bg=self.colors['background'])
        charts_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Sol taraf - Performans grafiği
        left_frame = tk.Frame(charts_frame, bg=self.colors['background'])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.create_performance_chart(left_frame)
        
        # Sağ taraf - Görev dağılımı
        right_frame = tk.Frame(charts_frame, bg=self.colors['background'])
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.create_task_distribution_chart(right_frame)
    
    def create_performance_chart(self, parent):
        """Performans grafiğini oluştur"""
        # Başlık
        title_label = tk.Label(parent, text="📈 Performans Trendi", 
                              font=("Segoe UI", 14, "bold"), 
                              bg=self.colors['background'], fg=self.colors['text'])
        title_label.pack(pady=(0, 10))
        
        # Matplotlib figürü
        self.perf_fig = Figure(figsize=(6, 4), dpi=100, facecolor=self.colors['background'])
        self.perf_ax = self.perf_fig.add_subplot(111)
        
        # Canvas
        self.perf_canvas = FigureCanvasTkAgg(self.perf_fig, parent)
        self.perf_canvas.draw()
        self.perf_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # İlk grafiği çiz
        self.update_performance_chart()
    
    def create_task_distribution_chart(self, parent):
        """Görev dağılım grafiğini oluştur"""
        # Başlık
        title_label = tk.Label(parent, text="🥧 Görev Dağılımı", 
                              font=("Segoe UI", 14, "bold"), 
                              bg=self.colors['background'], fg=self.colors['text'])
        title_label.pack(pady=(0, 10))
        
        # Matplotlib figürü
        self.dist_fig = Figure(figsize=(6, 4), dpi=100, facecolor=self.colors['background'])
        self.dist_ax = self.dist_fig.add_subplot(111)
        
        # Canvas
        self.dist_canvas = FigureCanvasTkAgg(self.dist_fig, parent)
        self.dist_canvas.draw()
        self.dist_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # İlk grafiği çiz
        self.update_task_distribution_chart()
    
    def create_data_tables(self, parent):
        """Veri tablolarını oluştur"""
        tables_frame = tk.Frame(parent, bg=self.colors['background'])
        tables_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Sol taraf - Son aktiviteler
        left_table_frame = tk.Frame(tables_frame, bg=self.colors['background'])
        left_table_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.create_recent_activities_table(left_table_frame)
        
        # Sağ taraf - En iyi performanslar
        right_table_frame = tk.Frame(tables_frame, bg=self.colors['background'])
        right_table_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.create_top_performances_table(right_table_frame)
    
    def create_recent_activities_table(self, parent):
        """Son aktiviteler tablosu"""
        # Başlık
        title_label = tk.Label(parent, text="🕒 Son Aktiviteler", 
                              font=("Segoe UI", 12, "bold"), 
                              bg=self.colors['background'], fg=self.colors['text'])
        title_label.pack(pady=(0, 10))
        
        # Treeview
        columns = ("Zaman", "Görev", "Durum", "Süre")
        self.activities_tree = ttk.Treeview(parent, columns=columns, show="headings", height=8)
        
        # Sütun başlıkları
        for col in columns:
            self.activities_tree.heading(col, text=col)
            self.activities_tree.column(col, width=100)
        
        # Scrollbar
        activities_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.activities_tree.yview)
        self.activities_tree.configure(yscrollcommand=activities_scroll.set)
        
        # Pack
        self.activities_tree.pack(side="left", fill="both", expand=True)
        activities_scroll.pack(side="right", fill="y")
        
        # İlk verileri yükle
        self.update_activities_table()
    
    def create_top_performances_table(self, parent):
        """En iyi performanslar tablosu"""
        # Başlık
        title_label = tk.Label(parent, text="🏆 En İyi Performanslar", 
                              font=("Segoe UI", 12, "bold"), 
                              bg=self.colors['background'], fg=self.colors['text'])
        title_label.pack(pady=(0, 10))
        
        # Treeview
        columns = ("Görev", "Başarı %", "Ort. Süre", "Son Çalışma")
        self.performance_tree = ttk.Treeview(parent, columns=columns, show="headings", height=8)
        
        # Sütun başlıkları
        for col in columns:
            self.performance_tree.heading(col, text=col)
            self.performance_tree.column(col, width=100)
        
        # Scrollbar
        performance_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.performance_tree.yview)
        self.performance_tree.configure(yscrollcommand=performance_scroll.set)
        
        # Pack
        self.performance_tree.pack(side="left", fill="both", expand=True)
        performance_scroll.pack(side="right", fill="y")
        
        # İlk verileri yükle
        self.update_performance_table()
    
    def create_controls_panel(self, parent):
        """Kontrol panelini oluştur"""
        controls_frame = tk.Frame(parent, bg=self.colors['background'])
        controls_frame.pack(fill="x")
        
        # Başlık
        title_label = tk.Label(controls_frame, text="🎛️ Kontroller", 
                              font=("Segoe UI", 12, "bold"), 
                              bg=self.colors['background'], fg=self.colors['text'])
        title_label.pack(pady=(0, 10))
        
        # Butonlar
        buttons_frame = tk.Frame(controls_frame, bg=self.colors['background'])
        buttons_frame.pack(fill="x")
        
        tk.Button(buttons_frame, text="📊 Rapor Oluştur", 
                 command=self.generate_report, 
                 bg=self.colors['primary'], fg="white", 
                 font=("Segoe UI", 10), relief="flat").pack(side="left", padx=5)
        
        tk.Button(buttons_frame, text="📈 Excel'e Aktar", 
                 command=self.export_to_excel, 
                 bg=self.colors['success'], fg="white", 
                 font=("Segoe UI", 10), relief="flat").pack(side="left", padx=5)
        
        tk.Button(buttons_frame, text="🗑️ Verileri Temizle", 
                 command=self.clear_old_data, 
                 bg=self.colors['danger'], fg="white", 
                 font=("Segoe UI", 10), relief="flat").pack(side="left", padx=5)
        
        tk.Button(buttons_frame, text="🔄 Yenile", 
                 command=self.refresh_all_data, 
                 bg=self.colors['info'], fg="white", 
                 font=("Segoe UI", 10), relief="flat").pack(side="left", padx=5)
    
    def log_performance(self, session_id: str, task_type: str, task_status: str, 
                       execution_time: float, success_rate: float = 1.0, 
                       error_message: str = None, **kwargs):
        """Performans verisi kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_logs 
                (session_id, task_type, task_status, execution_time, success_rate, 
                 error_message, screenshots_taken, clicks_performed, cpu_usage, memory_usage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id, task_type, task_status, execution_time, success_rate,
                error_message, kwargs.get('screenshots_taken', 0),
                kwargs.get('clicks_performed', 0), kwargs.get('cpu_usage', 0.0),
                kwargs.get('memory_usage', 0.0)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Performance log hatası: {e}")
    
    def update_summary_cards(self):
        """Özet kartlarını güncelle"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Toplam görevler
            total_tasks = pd.read_sql_query(
                "SELECT COUNT(*) as count FROM performance_logs", conn
            ).iloc[0]['count']
            
            # Başarı oranı
            success_rate = pd.read_sql_query('''
                SELECT AVG(success_rate) * 100 as rate 
                FROM performance_logs 
                WHERE task_status = "completed"
            ''', conn).iloc[0]['rate'] or 0
            
            # Ortalama süre
            avg_time = pd.read_sql_query('''
                SELECT AVG(execution_time) as avg_time 
                FROM performance_logs 
                WHERE task_status = "completed"
            ''', conn).iloc[0]['avg_time'] or 0
            
            # Son 24 saat
            last_24h = pd.read_sql_query('''
                SELECT COUNT(*) as count 
                FROM performance_logs 
                WHERE timestamp >= datetime('now', '-24 hours')
            ''', conn).iloc[0]['count']
            
            conn.close()
            
            # Kartları güncelle
            self.cards['total_tasks'].value_label.config(text=str(total_tasks))
            self.cards['success_rate'].value_label.config(text=f"{success_rate:.1f}%")
            self.cards['avg_time'].value_label.config(text=f"{avg_time:.1f}s")
            self.cards['last_24h'].value_label.config(text=str(last_24h))
            
        except Exception as e:
            print(f"Özet kart güncelleme hatası: {e}")
    
    def update_performance_chart(self):
        """Performans grafiğini güncelle"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Son 30 günlük veri
            df = pd.read_sql_query('''
                SELECT DATE(timestamp) as date, 
                       AVG(success_rate) * 100 as success_rate,
                       AVG(execution_time) as avg_time,
                       COUNT(*) as task_count
                FROM performance_logs 
                WHERE timestamp >= datetime('now', '-30 days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', conn)
            
            conn.close()
            
            if not df.empty:
                self.perf_ax.clear()
                
                # Başarı oranı çizgisi
                self.perf_ax.plot(df['date'], df['success_rate'], 
                                 marker='o', color='#2ecc71', linewidth=2, 
                                 label='Başarı Oranı (%)')
                
                # İkinci y ekseni için ortalama süre
                ax2 = self.perf_ax.twinx()
                ax2.plot(df['date'], df['avg_time'], 
                        marker='s', color='#f39c12', linewidth=2, 
                        label='Ort. Süre (s)')
                
                # Grafik ayarları
                self.perf_ax.set_title('Son 30 Günlük Performans', fontsize=12, fontweight='bold')
                self.perf_ax.set_ylabel('Başarı Oranı (%)', color='#2ecc71')
                ax2.set_ylabel('Ortalama Süre (s)', color='#f39c12')
                
                # X ekseni tarih formatı
                self.perf_ax.tick_params(axis='x', rotation=45)
                
                # Grid
                self.perf_ax.grid(True, alpha=0.3)
                
                # Legend
                lines1, labels1 = self.perf_ax.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                self.perf_ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
                
                self.perf_fig.tight_layout()
                self.perf_canvas.draw()
            
        except Exception as e:
            print(f"Performans grafiği güncelleme hatası: {e}")
    
    def update_task_distribution_chart(self):
        """Görev dağılım grafiğini güncelle"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Görev tiplerinin dağılımı
            df = pd.read_sql_query('''
                SELECT task_type, COUNT(*) as count
                FROM performance_logs 
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY task_type
                ORDER BY count DESC
                LIMIT 10
            ''', conn)
            
            conn.close()
            
            if not df.empty:
                self.dist_ax.clear()
                
                # Pasta grafiği
                colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', 
                         '#1abc9c', '#34495e', '#f1c40f', '#e67e22', '#95a5a6']
                
                wedges, texts, autotexts = self.dist_ax.pie(
                    df['count'], 
                    labels=df['task_type'],
                    colors=colors[:len(df)],
                    autopct='%1.1f%%',
                    startangle=90
                )
                
                self.dist_ax.set_title('Son 7 Günlük Görev Dağılımı', 
                                      fontsize=12, fontweight='bold')
                
                self.dist_fig.tight_layout()
                self.dist_canvas.draw()
            
        except Exception as e:
            print(f"Dağılım grafiği güncelleme hatası: {e}")
    
    def update_activities_table(self):
        """Aktiviteler tablosunu güncelle"""
        try:
            # Mevcut verileri temizle
            for item in self.activities_tree.get_children():
                self.activities_tree.delete(item)
            
            conn = sqlite3.connect(self.db_path)
            
            # Son 50 aktivite
            df = pd.read_sql_query('''
                SELECT timestamp, task_type, task_status, execution_time
                FROM performance_logs 
                ORDER BY timestamp DESC 
                LIMIT 50
            ''', conn)
            
            conn.close()
            
            # Verileri tabloya ekle
            for _, row in df.iterrows():
                timestamp = datetime.fromisoformat(row['timestamp']).strftime('%H:%M:%S')
                status_icon = "✅" if row['task_status'] == "completed" else "❌"
                
                self.activities_tree.insert('', 0, values=(
                    timestamp,
                    row['task_type'],
                    f"{status_icon} {row['task_status']}",
                    f"{row['execution_time']:.1f}s"
                ))
            
        except Exception as e:
            print(f"Aktivite tablosu güncelleme hatası: {e}")
    
    def update_performance_table(self):
        """Performans tablosunu güncelle"""
        try:
            # Mevcut verileri temizle
            for item in self.performance_tree.get_children():
                self.performance_tree.delete(item)
            
            conn = sqlite3.connect(self.db_path)
            
            # Görev tipi bazında performans
            df = pd.read_sql_query('''
                SELECT task_type,
                       AVG(success_rate) * 100 as success_rate,
                       AVG(execution_time) as avg_time,
                       MAX(timestamp) as last_run
                FROM performance_logs 
                WHERE task_status = "completed"
                GROUP BY task_type
                ORDER BY success_rate DESC
            ''', conn)
            
            conn.close()
            
            # Verileri tabloya ekle
            for _, row in df.iterrows():
                last_run = datetime.fromisoformat(row['last_run']).strftime('%d.%m %H:%M')
                
                self.performance_tree.insert('', 'end', values=(
                    row['task_type'],
                    f"{row['success_rate']:.1f}%",
                    f"{row['avg_time']:.1f}s",
                    last_run
                ))
            
        except Exception as e:
            print(f"Performans tablosu güncelleme hatası: {e}")
    
    def start_real_time_updates(self):
        """Real-time güncellemeleri başlat"""
        def update_loop():
            while True:
                try:
                    self.refresh_all_data()
                    time.sleep(self.update_interval / 1000)
                except Exception as e:
                    print(f"Real-time güncelleme hatası: {e}")
                    time.sleep(10)
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    def refresh_all_data(self):
        """Tüm verileri yenile"""
        try:
            self.update_summary_cards()
            self.update_performance_chart()
            self.update_task_distribution_chart()
            self.update_activities_table()
            self.update_performance_table()
        except Exception as e:
            print(f"Veri yenileme hatası: {e}")
    
    def generate_report(self):
        """Detaylı rapor oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Rapor verileri
            report_data = {
                "generated_at": datetime.now().isoformat(),
                "summary": {},
                "detailed_stats": {},
                "recommendations": []
            }
            
            # Özet istatistikler
            summary_df = pd.read_sql_query('''
                SELECT 
                    COUNT(*) as total_tasks,
                    AVG(success_rate) * 100 as avg_success_rate,
                    AVG(execution_time) as avg_execution_time,
                    SUM(CASE WHEN task_status = "completed" THEN 1 ELSE 0 END) as completed_tasks,
                    SUM(CASE WHEN task_status = "failed" THEN 1 ELSE 0 END) as failed_tasks
                FROM performance_logs
            ''', conn)
            
            report_data["summary"] = summary_df.iloc[0].to_dict()
            
            # Görev tipi bazında detaylar
            detailed_df = pd.read_sql_query('''
                SELECT task_type,
                       COUNT(*) as total_executions,
                       AVG(success_rate) * 100 as success_rate,
                       AVG(execution_time) as avg_execution_time,
                       MIN(execution_time) as min_time,
                       MAX(execution_time) as max_time
                FROM performance_logs
                GROUP BY task_type
                ORDER BY total_executions DESC
            ''', conn)
            
            report_data["detailed_stats"] = detailed_df.to_dict('records')
            
            conn.close()
            
            # Öneriler oluştur
            report_data["recommendations"] = self.generate_recommendations(report_data)
            
            # Raporu kaydet
            report_filename = f"bot_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=4, ensure_ascii=False)
            
            tk.messagebox.showinfo("Rapor", f"Rapor oluşturuldu: {report_filename}")
            
        except Exception as e:
            tk.messagebox.showerror("Hata", f"Rapor oluşturma hatası: {e}")
    
    def generate_recommendations(self, report_data: Dict) -> List[str]:
        """AI tabanlı öneriler oluştur"""
        recommendations = []
        
        try:
            summary = report_data["summary"]
            
            # Başarı oranı analizi
            if summary["avg_success_rate"] < 80:
                recommendations.append("⚠️ Başarı oranı %80'in altında. Görev ayarlarını gözden geçirin.")
            
            # Çalışma süresi analizi
            if summary["avg_execution_time"] > 30:
                recommendations.append("🐌 Ortalama çalışma süresi yüksek. Performans optimizasyonu öneririz.")
            
            # Hata oranı analizi
            error_rate = (summary["failed_tasks"] / summary["total_tasks"]) * 100
            if error_rate > 10:
                recommendations.append(f"❌ Hata oranı %{error_rate:.1f}. Hata loglarını inceleyin.")
            
            # Görev bazlı öneriler
            for task_stat in report_data["detailed_stats"]:
                if task_stat["success_rate"] < 70:
                    recommendations.append(
                        f"🔧 {task_stat['task_type']} görevi için optimizasyon gerekli (Başarı: %{task_stat['success_rate']:.1f})"
                    )
            
        except Exception as e:
            recommendations.append(f"⚠️ Öneri oluşturma hatası: {e}")
        
        return recommendations
    
    def export_to_excel(self):
        """Verileri Excel'e aktar"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Tüm performans verilerini al
            df = pd.read_sql_query('SELECT * FROM performance_logs', conn)
            
            conn.close()
            
            # Excel dosyasına kaydet
            filename = f"bot_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            
            tk.messagebox.showinfo("Excel", f"Veriler Excel'e aktarıldı: {filename}")
            
        except Exception as e:
            tk.messagebox.showerror("Hata", f"Excel export hatası: {e}")
    
    def clear_old_data(self):
        """Eski verileri temizle"""
        try:
            result = tk.messagebox.askyesno(
                "Onay", 
                "30 günden eski veriler silinecek. Devam etmek istiyor musunuz?"
            )
            
            if result:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM performance_logs 
                    WHERE timestamp < datetime('now', '-30 days')
                ''')
                
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                
                tk.messagebox.showinfo("Temizlik", f"{deleted_count} eski kayıt silindi.")
                self.refresh_all_data()
                
        except Exception as e:
            tk.messagebox.showerror("Hata", f"Veri temizleme hatası: {e}")


# Test fonksiyonu
def test_analytics_dashboard():
    """Analytics dashboard'u test et"""
    root = tk.Tk()
    root.title("Analytics Dashboard Test")
    root.geometry("1200x800")
    
    colors = {
        'background': '#ffffff',
        'text': '#2c3e50',
        'primary': '#3498db',
        'success': '#2ecc71',
        'danger': '#e74c3c',
        'info': '#17a2b8'
    }
    
    dashboard = AnalyticsDashboard(root, colors)
    
    # Test verileri ekle
    import uuid
    session_id = str(uuid.uuid4())
    
    # Örnek performans verileri
    test_tasks = [
        ("healing", "completed", 2.5, 1.0),
        ("daily_tasks", "completed", 15.2, 1.0),
        ("warfare", "failed", 8.1, 0.0),
        ("kutu", "completed", 3.7, 1.0),
        ("healing", "completed", 2.1, 1.0)
    ]
    
    for task_type, status, exec_time, success_rate in test_tasks:
        dashboard.log_performance(session_id, task_type, status, exec_time, success_rate)
    
    # İlk veri yüklemesi
    dashboard.refresh_all_data()
    
    root.mainloop()


if __name__ == "__main__":
    test_analytics_dashboard()
