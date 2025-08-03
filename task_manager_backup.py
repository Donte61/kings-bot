import time
import logging
import threading
from collections import deque

# Görev durumlarını tanımlamak için sabitler
class TaskStatus:
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"

class Task:
    def __init__(self, name, func, args=None, kwargs=None, is_timed=False, interval=0):
        self.name = name
        self.func = func
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.is_timed = is_timed
        self.interval = interval  # saniye cinsinden
        self.last_execution_time = 0
        self.next_execution_time = 0  # Bir sonraki çalıştırma zamanı
        self.retry_delay = 120  # Başarısızlık sonrası 2 dakika bekleme

    def can_execute(self, current_time):
        if not self.is_timed:
            return True
        return current_time >= self.next_execution_time

    def run(self):
        logging.info(f"--- Görev Başlatılıyor: {self.name} ---")
        start_time = time.time()
        try:
            result = self.func(*self.args, **self.kwargs)
            end_time = time.time()
            logging.info(f"--- Görev Tamamlandı: {self.name} | Sonuç: {'Başarılı' if result else 'Başarısız'} | Süre: {end_time - start_time:.2f}s ---")
            return TaskStatus.SUCCESS if result else TaskStatus.FAILURE
        except Exception as e:
            end_time = time.time()
            logging.error(f"--- Görev Hatası: {self.name} | Hata: {e} | Süre: {end_time - start_time:.2f}s ---", exc_info=True)
            return TaskStatus.FAILURE

class TaskManager:
    def __init__(self, on_stats_update=None):
        self.tasks = {}
        self.task_queue = deque()
        self.timed_tasks = deque()  # Changed from list to deque
        self.is_running = False
        self.lock = threading.Lock()
        self.on_stats_update = on_stats_update  # UI'ı güncellemek için callback

    def add_task(self, name, func, args=None, kwargs=None, is_timed=False, interval=0):
        task = Task(name, func, args, kwargs, is_timed, interval)
        with self.lock:
            self.tasks[name] = task
            if is_timed:
                self.timed_tasks.append(task)

    def update_task_selection(self, selections):
        """Kullanıcının UI'dan seçtiği görevlere göre kuyruğu günceller."""
        with self.lock:
            self.task_queue.clear()
            for name, task in self.tasks.items():
                if not task.is_timed and selections.get(name, False):
                    self.task_queue.append(task)

    def get_next_task(self, selections):
        with self.lock:
            current_time = time.time()
            
            # Zamanlanmış görevleri kontrol et
            for _ in range(len(self.timed_tasks)):
                task = self.timed_tasks[0]
                if selections.get(task.name, False) and task.can_execute(current_time):
                    self.timed_tasks.rotate(-1)
                    return task
                self.timed_tasks.rotate(-1)
            
            # Zamanlanmamış görevleri kontrol et
            while self.task_queue:
                task = self.task_queue[0]
                if selections.get(task.name, False):
                    return task
                else:
                    self.task_queue.popleft()  # Seçili değilse çıkar
            
            return None

    def process_task_result(self, task, result, selections):
        with self.lock:
            current_time = time.time()
            if result == TaskStatus.SUCCESS:
                task.last_execution_time = current_time
                task.next_execution_time = current_time + task.interval
                if self.on_stats_update:
                    self.on_stats_update("success", task.name, 1)
                if not task.is_timed and self.task_queue and self.task_queue[0] == task:
                    self.task_queue.popleft()
            else:
                if self.on_stats_update:
                    self.on_stats_update("failure", task.name, 1)
                task.next_execution_time = current_time + task.retry_delay
                if not task.is_timed and self.task_queue and self.task_queue[0] == task:
                    self.task_queue.popleft()  # Başarısız görevleri de kuyruktan çıkar
            
            for t in self.timed_tasks:
                if selections.get(t.name, False):
                    if t.can_execute(current_time):
                        if self.on_stats_update:
                            self.on_stats_update("countdown", t.name, "Hazır")
                    else:
                        remaining = t.next_execution_time - current_time
                        if self.on_stats_update:
                            self.on_stats_update("countdown", t.name, f"{int(remaining // 60)}dk")