import time
import logging
import threading
import json
import queue
from collections import deque
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import datetime

class TaskStatus(Enum):
    """Görev durumları"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"

class TaskPriority(Enum):
    """Görev öncelik seviyeleri"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class TaskResult:
    """Görev sonucu"""
    status: TaskStatus
    message: str
    execution_time: float
    timestamp: datetime.datetime
    error_info: Optional[Dict[str, Any]] = None

@dataclass
class TaskStats:
    """Görev istatistikleri"""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time: float = 0.0
    last_execution: Optional[datetime.datetime] = None
    success_rate: float = 0.0

class AdvancedTask:
    """Gelişmiş görev sınıfı"""
    
    def __init__(self, name: str, func: Callable, args: List = None, kwargs: Dict = None,
                 priority: TaskPriority = TaskPriority.NORMAL, timeout: float = 30.0,
                 max_retries: int = 3, retry_delay: float = 5.0,
                 is_timed: bool = False, interval: float = 0,
                 dependencies: List[str] = None, tags: List[str] = None):
        
        self.name = name
        self.func = func
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.priority = priority
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.current_retries = 0
        
        # Zamanlama
        self.is_timed = is_timed
        self.interval = interval
        self.last_execution_time = 0
        self.next_execution_time = 0
        
        # Bağımlılıklar ve etiketler
        self.dependencies = dependencies if dependencies is not None else []
        self.tags = tags if tags is not None else []
        
        # Durum bilgileri
        self.status = TaskStatus.PENDING
        self.results_history = deque(maxlen=100)  # Son 100 sonucu sakla
        self.stats = TaskStats()
        
        # Threading
        self.is_running = False
        self.cancel_event = threading.Event()
        
    def can_execute(self, current_time: float, completed_tasks: set) -> bool:
        """Görevin çalıştırılıp çalıştırılamayacağını kontrol et"""
        # İptal edilmişse çalıştırma
        if self.cancel_event.is_set():
            return False
            
        # Zaten çalışıyorsa çalıştırma
        if self.is_running:
            return False
            
        # Zamanlı görev kontrolü
        if self.is_timed and current_time < self.next_execution_time:
            return False
            
        # Bağımlılık kontrolü
        for dependency in self.dependencies:
            if dependency not in completed_tasks:
                return False
                
        return True
        
    def execute(self) -> TaskResult:
        """Görevi çalıştır"""
        if self.cancel_event.is_set():
            return TaskResult(TaskStatus.CANCELLED, "Görev iptal edildi", 0.0, datetime.datetime.now())
            
        self.is_running = True
        self.status = TaskStatus.RUNNING
        start_time = time.time()
        
        try:
            logging.info(f"[TASK] Başlatılıyor: {self.name}")
            
            # Timeout ile çalıştır
            result = self._execute_with_timeout()
            
            execution_time = time.time() - start_time
            
            if result:
                self.status = TaskStatus.SUCCESS
                self.stats.successful_executions += 1
                self.current_retries = 0  # Başarılıysa retry sayısını sıfırla
                
                task_result = TaskResult(
                    status=TaskStatus.SUCCESS,
                    message=f"Görev başarıyla tamamlandı",
                    execution_time=execution_time,
                    timestamp=datetime.datetime.now()
                )
                
                logging.info(f"[TASK] Başarılı: {self.name} - Süre: {execution_time:.2f}s")
                
            else:
                self.status = TaskStatus.FAILURE
                self.stats.failed_executions += 1
                
                task_result = TaskResult(
                    status=TaskStatus.FAILURE,
                    message=f"Görev başarısız",
                    execution_time=execution_time,
                    timestamp=datetime.datetime.now()
                )
                
                logging.warning(f"[TASK] Başarısız: {self.name} - Süre: {execution_time:.2f}s")
                
        except TimeoutError:
            execution_time = time.time() - start_time
            self.status = TaskStatus.TIMEOUT
            self.stats.failed_executions += 1
            
            task_result = TaskResult(
                status=TaskStatus.TIMEOUT,
                message=f"Görev zaman aşımına uğradı ({self.timeout}s)",
                execution_time=execution_time,
                timestamp=datetime.datetime.now()
            )
            
            logging.error(f"[TASK] Timeout: {self.name} - Süre: {execution_time:.2f}s")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.status = TaskStatus.FAILURE
            self.stats.failed_executions += 1
            
            error_info = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": logging.traceback.format_exc() if hasattr(logging, 'traceback') else str(e)
            }
            
            task_result = TaskResult(
                status=TaskStatus.FAILURE,
                message=f"Görev hatası: {str(e)}",
                execution_time=execution_time,
                timestamp=datetime.datetime.now(),
                error_info=error_info
            )
            
            logging.error(f"[TASK] Hata: {self.name} - {str(e)} - Süre: {execution_time:.2f}s")
            
        finally:
            self.is_running = False
            self.last_execution_time = time.time()
            
            # Zamanlı görev için bir sonraki çalıştırma zamanını ayarla
            if self.is_timed:
                self.next_execution_time = self.last_execution_time + self.interval
                
            # İstatistikleri güncelle
            self.stats.total_executions += 1
            self.stats.last_execution = task_result.timestamp
            
            # Ortalama çalıştırma süresi
            total_time = (self.stats.average_execution_time * (self.stats.total_executions - 1) + 
                         task_result.execution_time)
            self.stats.average_execution_time = total_time / self.stats.total_executions
            
            # Başarı oranı
            if self.stats.total_executions > 0:
                self.stats.success_rate = (self.stats.successful_executions / self.stats.total_executions) * 100
                
            # Sonucu geçmişe ekle
            self.results_history.append(task_result)
            
        return task_result
        
    def _execute_with_timeout(self) -> bool:
        """Timeout ile görev çalıştırma"""
        result_queue = queue.Queue()
        
        def worker():
            try:
                result = self.func(*self.args, **self.kwargs)
                result_queue.put(result)
            except Exception as e:
                result_queue.put(e)
                
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        
        try:
            result = result_queue.get(timeout=self.timeout)
            if isinstance(result, Exception):
                raise result
            return result
        except queue.Empty:
            raise TimeoutError(f"Görev {self.timeout} saniye içinde tamamlanamadı")
            
    def should_retry(self) -> bool:
        """Retry yapılıp yapılmayacağını kontrol et"""
        return (self.status in [TaskStatus.FAILURE, TaskStatus.TIMEOUT] and 
                self.current_retries < self.max_retries)
                
    def cancel(self):
        """Görevi iptal et"""
        self.cancel_event.set()
        self.status = TaskStatus.CANCELLED
        logging.info(f"[TASK] İptal edildi: {self.name}")
        
    def reset(self):
        """Görevi sıfırla"""
        self.status = TaskStatus.PENDING
        self.current_retries = 0
        self.cancel_event.clear()
        self.is_running = False
        
    def get_info(self) -> Dict[str, Any]:
        """Görev bilgilerini al"""
        return {
            "name": self.name,
            "status": self.status.value,
            "priority": self.priority.value,
            "is_timed": self.is_timed,
            "interval": self.interval,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "stats": asdict(self.stats),
            "last_result": asdict(self.results_history[-1]) if self.results_history else None
        }

class AdvancedTaskManager:
    """Gelişmiş görev yöneticisi"""
    
    def __init__(self, on_stats_update: Optional[Callable] = None, max_concurrent_tasks: int = 3):
        self.tasks: Dict[str, AdvancedTask] = {}
        self.task_queue = queue.PriorityQueue()
        self.running_tasks: Dict[str, threading.Thread] = {}
        self.completed_tasks = set()
        
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        self.max_concurrent_tasks = max_concurrent_tasks
        self.on_stats_update = on_stats_update
        
        # İstatistikler
        self.global_stats = {
            "total_tasks_executed": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_task_time": 0.0,
            "uptime": 0.0,
            "start_time": None
        }
        
        # Event callbacks
        self.event_callbacks = {
            "task_started": [],
            "task_completed": [],
            "task_failed": [],
            "queue_empty": [],
            "manager_started": [],
            "manager_stopped": []
        }
        
    def add_task(self, task: AdvancedTask) -> bool:
        """Görev ekle"""
        try:
            with self.lock:
                if task.name in self.tasks:
                    logging.warning(f"Görev zaten mevcut: {task.name}")
                    return False
                    
                self.tasks[task.name] = task
                
                # Önceliğe göre sıraya ekle (negatif çünkü PriorityQueue min-heap)
                priority = -task.priority.value
                self.task_queue.put((priority, time.time(), task.name))
                
                logging.info(f"Görev eklendi: {task.name} (Öncelik: {task.priority.name})")
                return True
                
        except Exception as e:
            logging.error(f"Görev eklenemedi: {e}")
            return False
            
    def remove_task(self, task_name: str) -> bool:
        """Görev kaldır"""
        try:
            with self.lock:
                if task_name in self.tasks:
                    task = self.tasks[task_name]
                    task.cancel()
                    
                    # Çalışan görevse thread'i bekle
                    if task_name in self.running_tasks:
                        thread = self.running_tasks[task_name]
                        thread.join(timeout=5.0)
                        del self.running_tasks[task_name]
                        
                    del self.tasks[task_name]
                    self.completed_tasks.discard(task_name)
                    
                    logging.info(f"Görev kaldırıldı: {task_name}")
                    return True
                    
        except Exception as e:
            logging.error(f"Görev kaldırılamadı: {e}")
            
        return False
        
    def start(self) -> bool:
        """Task manager'ı başlat"""
        if self.is_running:
            logging.warning("Task manager zaten çalışıyor")
            return False
            
        try:
            self.is_running = True
            self.global_stats["start_time"] = time.time()
            
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            
            self._trigger_event("manager_started")
            logging.info("Task manager başlatıldı")
            return True
            
        except Exception as e:
            logging.error(f"Task manager başlatılamadı: {e}")
            self.is_running = False
            return False
            
    def stop(self) -> bool:
        """Task manager'ı durdur"""
        if not self.is_running:
            return True
            
        try:
            self.is_running = False
            
            # Tüm görevleri iptal et
            with self.lock:
                for task in self.tasks.values():
                    task.cancel()
                    
            # Çalışan thread'leri bekle
            for thread in list(self.running_tasks.values()):
                thread.join(timeout=5.0)
                
            # Worker thread'i bekle
            if self.worker_thread:
                self.worker_thread.join(timeout=5.0)
                
            self.running_tasks.clear()
            self._trigger_event("manager_stopped")
            
            logging.info("Task manager durduruldu")
            return True
            
        except Exception as e:
            logging.error(f"Task manager durdurulamadı: {e}")
            return False
            
    def _worker_loop(self):
        """Ana çalışma döngüsü"""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Zamanlı görevleri kontrol et ve sıraya ekle
                self._schedule_timed_tasks(current_time)
                
                # Yeni görev al
                if len(self.running_tasks) < self.max_concurrent_tasks:
                    task_name = self._get_next_task(current_time)
                    
                    if task_name:
                        self._execute_task(task_name)
                        
                # Tamamlanan thread'leri temizle
                self._cleanup_completed_threads()
                
                # İstatistikleri güncelle
                self._update_global_stats()
                
                # Kısa bekleme
                time.sleep(0.1)
                
            except Exception as e:
                logging.error(f"Worker loop hatası: {e}")
                time.sleep(1.0)
                
    def _schedule_timed_tasks(self, current_time: float):
        """Zamanlı görevleri planla"""
        with self.lock:
            for task in self.tasks.values():
                if (task.is_timed and 
                    not task.is_running and 
                    task.status != TaskStatus.CANCELLED and
                    current_time >= task.next_execution_time):
                    
                    # Sıraya ekle
                    priority = -task.priority.value
                    self.task_queue.put((priority, current_time, task.name))
                    
    def _get_next_task(self, current_time: float) -> Optional[str]:
        """Sıradaki görevi al"""
        try:
            # Sıradan görev al (5 saniye timeout)
            priority, queued_time, task_name = self.task_queue.get(timeout=5.0)
            
            # Görev hala mevcut mu?
            if task_name not in self.tasks:
                return None
                
            task = self.tasks[task_name]
            
            # Görev çalıştırılabilir mi?
            if task.can_execute(current_time, self.completed_tasks):
                return task_name
            else:
                # Geri sıraya koy
                self.task_queue.put((priority, queued_time, task_name))
                return None
                
        except queue.Empty:
            # Sıra boş
            self._trigger_event("queue_empty")
            return None
            
    def _execute_task(self, task_name: str):
        """Görevi çalıştır"""
        task = self.tasks[task_name]
        
        def task_runner():
            try:
                self._trigger_event("task_started", task_name, task)
                
                result = task.execute()
                
                with self.lock:
                    if result.status == TaskStatus.SUCCESS:
                        self.completed_tasks.add(task_name)
                        self.global_stats["successful_tasks"] += 1
                        self._trigger_event("task_completed", task_name, task, result)
                    else:
                        self.global_stats["failed_tasks"] += 1
                        self._trigger_event("task_failed", task_name, task, result)
                        
                        # Retry kontrolü
                        if task.should_retry():
                            task.current_retries += 1
                            task.status = TaskStatus.RETRY
                            
                            # Retry delay sonrası tekrar sıraya ekle
                            def retry_later():
                                time.sleep(task.retry_delay)
                                if self.is_running and task_name in self.tasks:
                                    priority = -task.priority.value
                                    self.task_queue.put((priority, time.time(), task_name))
                                    
                            threading.Thread(target=retry_later, daemon=True).start()
                            
                    self.global_stats["total_tasks_executed"] += 1
                    
            except Exception as e:
                logging.error(f"Task runner hatası: {e}")
            finally:
                # Running tasks listesinden çıkar
                with self.lock:
                    if task_name in self.running_tasks:
                        del self.running_tasks[task_name]
                        
        # Thread başlat
        thread = threading.Thread(target=task_runner, daemon=True)
        thread.start()
        
        with self.lock:
            self.running_tasks[task_name] = thread
            
    def _cleanup_completed_threads(self):
        """Tamamlanan thread'leri temizle"""
        with self.lock:
            completed = []
            for task_name, thread in self.running_tasks.items():
                if not thread.is_alive():
                    completed.append(task_name)
                    
            for task_name in completed:
                del self.running_tasks[task_name]
                
    def _update_global_stats(self):
        """Global istatistikleri güncelle"""
        if self.global_stats["start_time"]:
            self.global_stats["uptime"] = time.time() - self.global_stats["start_time"]
            
        # Ortalama görev süresi
        total_time = 0.0
        total_tasks = 0
        
        with self.lock:
            for task in self.tasks.values():
                if task.stats.total_executions > 0:
                    total_time += task.stats.average_execution_time * task.stats.total_executions
                    total_tasks += task.stats.total_executions
                    
        if total_tasks > 0:
            self.global_stats["average_task_time"] = total_time / total_tasks
            
        # Callback çağır
        if self.on_stats_update:
            try:
                self.on_stats_update(self.global_stats)
            except Exception as e:
                logging.error(f"Stats update callback hatası: {e}")
                
    def _trigger_event(self, event_name: str, *args):
        """Event callback'lerini tetikle"""
        if event_name in self.event_callbacks:
            for callback in self.event_callbacks[event_name]:
                try:
                    callback(*args)
                except Exception as e:
                    logging.error(f"Event callback hatası ({event_name}): {e}")
                    
    def add_event_listener(self, event_name: str, callback: Callable):
        """Event listener ekle"""
        if event_name in self.event_callbacks:
            self.event_callbacks[event_name].append(callback)
            
    def remove_event_listener(self, event_name: str, callback: Callable):
        """Event listener kaldır"""
        if event_name in self.event_callbacks and callback in self.event_callbacks[event_name]:
            self.event_callbacks[event_name].remove(callback)
            
    def get_task_info(self, task_name: str) -> Optional[Dict[str, Any]]:
        """Görev bilgilerini al"""
        if task_name in self.tasks:
            return self.tasks[task_name].get_info()
        return None
        
    def get_all_tasks_info(self) -> Dict[str, Dict[str, Any]]:
        """Tüm görev bilgilerini al"""
        with self.lock:
            return {name: task.get_info() for name, task in self.tasks.items()}
            
    def get_global_stats(self) -> Dict[str, Any]:
        """Global istatistikleri al"""
        return self.global_stats.copy()
        
    def pause_task(self, task_name: str) -> bool:
        """Görevi duraklat"""
        if task_name in self.tasks:
            task = self.tasks[task_name]
            task.cancel()
            return True
        return False
        
    def resume_task(self, task_name: str) -> bool:
        """Görevi devam ettir"""
        if task_name in self.tasks:
            task = self.tasks[task_name]
            task.reset()
            
            # Sıraya tekrar ekle
            priority = -task.priority.value
            self.task_queue.put((priority, time.time(), task_name))
            return True
        return False
        
    def get_tasks_by_tag(self, tag: str) -> List[str]:
        """Etikete göre görevleri al"""
        with self.lock:
            return [name for name, task in self.tasks.items() if tag in task.tags]
            
    def get_tasks_by_status(self, status: TaskStatus) -> List[str]:
        """Duruma göre görevleri al"""
        with self.lock:
            return [name for name, task in self.tasks.items() if task.status == status]
            
    def export_stats(self, filename: str) -> bool:
        """İstatistikleri dosyaya aktar"""
        try:
            stats_data = {
                "global_stats": self.get_global_stats(),
                "task_stats": self.get_all_tasks_info(),
                "export_time": datetime.datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=4, ensure_ascii=False, default=str)
                
            logging.info(f"İstatistikler dışa aktarıldı: {filename}")
            return True
            
        except Exception as e:
            logging.error(f"İstatistik dışa aktarma hatası: {e}")
            return False

# Backwards compatibility
TaskManager = AdvancedTaskManager
Task = AdvancedTask
