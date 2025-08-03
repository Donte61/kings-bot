"""
🔄 King Bot Pro - Gelişmiş Makro Sistemi
Karmaşık otomasyonlar için akıllı makro sistemi
"""

import json
import time
import threading
import uuid
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass, asdict
import pyautogui
import cv2
import numpy as np
import random
import re


class ActionType(Enum):
    """Aksiyon tipleri"""
    CLICK = "click"
    TYPE = "type"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    TEMPLATE_FIND = "template_find"
    TEMPLATE_CLICK = "template_click"
    LOOP = "loop"
    CONDITION = "condition"
    VARIABLE = "variable"
    FUNCTION = "function"
    RANDOM_DELAY = "random_delay"
    MOUSE_MOVE = "mouse_move"
    KEY_PRESS = "key_press"
    SCROLL = "scroll"


class ConditionType(Enum):
    """Koşul tipleri"""
    TEMPLATE_EXISTS = "template_exists"
    TEMPLATE_NOT_EXISTS = "template_not_exists"
    VARIABLE_EQUALS = "variable_equals"
    VARIABLE_GREATER = "variable_greater"
    VARIABLE_LESS = "variable_less"
    TIME_ELAPSED = "time_elapsed"
    RANDOM_CHANCE = "random_chance"


@dataclass
class MacroAction:
    """Makro aksiyonu"""
    id: str
    action_type: ActionType
    parameters: Dict[str, Any]
    description: str = ""
    enabled: bool = True
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 30.0
    
    def to_dict(self):
        """Dictionary'ye çevir"""
        return {
            'id': self.id,
            'action_type': self.action_type.value,
            'parameters': self.parameters,
            'description': self.description,
            'enabled': self.enabled,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'timeout': self.timeout
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Dictionary'den oluştur"""
        return cls(
            id=data['id'],
            action_type=ActionType(data['action_type']),
            parameters=data['parameters'],
            description=data.get('description', ''),
            enabled=data.get('enabled', True),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3),
            timeout=data.get('timeout', 30.0)
        )


@dataclass
class MacroSequence:
    """Makro dizisi"""
    id: str
    name: str
    description: str
    actions: List[MacroAction]
    variables: Dict[str, Any]
    created_at: datetime
    modified_at: datetime
    tags: List[str]
    enabled: bool = True
    
    def to_dict(self):
        """Dictionary'ye çevir"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'actions': [action.to_dict() for action in self.actions],
            'variables': self.variables,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'tags': self.tags,
            'enabled': self.enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Dictionary'den oluştur"""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            actions=[MacroAction.from_dict(action_data) for action_data in data['actions']],
            variables=data['variables'],
            created_at=datetime.fromisoformat(data['created_at']),
            modified_at=datetime.fromisoformat(data['modified_at']),
            tags=data.get('tags', []),
            enabled=data.get('enabled', True)
        )


class MacroExecutionContext:
    """Makro çalıştırma bağlamı"""
    
    def __init__(self):
        self.variables = {}
        self.loop_stack = []
        self.execution_log = []
        self.start_time = None
        self.current_action = None
        self.screenshots = []
        self.error_count = 0
        self.success_count = 0


class MacroEngine:
    """Gelişmiş makro motoru"""
    
    def __init__(self, ai_vision_system=None):
        self.ai_vision = ai_vision_system
        self.macros = {}
        self.execution_contexts = {}
        self.running_macros = {}
        self.macro_library = {}
        
        # Dosya yolları
        self.macros_file = "macros.json"
        self.library_file = "macro_library.json"
        
        # Yükleme
        self.load_macros()
        self.load_macro_library()
        
        # Custom functions
        self.custom_functions = {}
        self.register_builtin_functions()
    
    def register_builtin_functions(self):
        """Yerleşik fonksiyonları kaydet"""
        
        @self.register_function("random_number")
        def random_number(min_val: int = 1, max_val: int = 100):
            """Random sayı üret"""
            return random.randint(min_val, max_val)
        
        @self.register_function("current_time")
        def current_time(format_str: str = "%H:%M:%S"):
            """Mevcut zamanı döndür"""
            return datetime.now().strftime(format_str)
        
        @self.register_function("calculate")
        def calculate(expression: str, variables: Dict = None):
            """Matematiksel ifade hesapla"""
            try:
                # Güvenli değişken değiştirme
                if variables:
                    for var_name, var_value in variables.items():
                        expression = expression.replace(f"{{{var_name}}}", str(var_value))
                
                # Güvenli eval (sadece matematik)
                allowed_chars = "0123456789+-*/()."
                if all(c in allowed_chars for c in expression.replace(' ', '')):
                    return eval(expression)
                else:
                    raise ValueError("Güvenli olmayan ifade")
            except Exception as e:
                print(f"Hesaplama hatası: {e}")
                return 0
        
        @self.register_function("wait_for_template")
        def wait_for_template(template_name: str, timeout: int = 30):
            """Template görünene kadar bekle"""
            start_time = time.time()
            while time.time() - start_time < timeout:
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                if self.find_template(screenshot, template_name):
                    return True
                
                time.sleep(1)
            
            return False
        
        @self.register_function("get_pixel_color")
        def get_pixel_color(x: int, y: int):
            """Piksel rengini al"""
            try:
                screenshot = pyautogui.screenshot()
                return screenshot.getpixel((x, y))
            except Exception as e:
                print(f"Piksel rengi alma hatası: {e}")
                return (0, 0, 0)
    
    def register_function(self, name: str):
        """Fonksiyon kaydetme decorator'ü"""
        def decorator(func: Callable):
            self.custom_functions[name] = func
            return func
        return decorator
    
    def create_macro(self, name: str, description: str = "", tags: List[str] = None) -> MacroSequence:
        """Yeni makro oluştur"""
        macro_id = str(uuid.uuid4())
        now = datetime.now()
        
        macro = MacroSequence(
            id=macro_id,
            name=name,
            description=description,
            actions=[],
            variables={},
            created_at=now,
            modified_at=now,
            tags=tags or []
        )
        
        self.macros[macro_id] = macro
        self.save_macros()
        
        return macro
    
    def add_action(self, macro_id: str, action_type: ActionType, 
                   parameters: Dict[str, Any], description: str = "") -> MacroAction:
        """Makroya aksiyon ekle"""
        if macro_id not in self.macros:
            raise ValueError(f"Makro bulunamadı: {macro_id}")
        
        action_id = str(uuid.uuid4())
        action = MacroAction(
            id=action_id,
            action_type=action_type,
            parameters=parameters,
            description=description
        )
        
        self.macros[macro_id].actions.append(action)
        self.macros[macro_id].modified_at = datetime.now()
        self.save_macros()
        
        return action
    
    def execute_macro(self, macro_id: str, variables: Dict[str, Any] = None) -> bool:
        """Makroyu çalıştır"""
        if macro_id not in self.macros:
            raise ValueError(f"Makro bulunamadı: {macro_id}")
        
        macro = self.macros[macro_id]
        if not macro.enabled:
            print(f"Makro devre dışı: {macro.name}")
            return False
        
        # Execution context oluştur
        context = MacroExecutionContext()
        context.variables = {**(variables or {}), **macro.variables}
        context.start_time = time.time()
        
        self.execution_contexts[macro_id] = context
        
        print(f"🔄 Makro başlatılıyor: {macro.name}")
        
        try:
            # Thread'de çalıştır
            def run_macro():
                self.running_macros[macro_id] = True
                success = self._execute_actions(macro.actions, context)
                self.running_macros[macro_id] = False
                
                execution_time = time.time() - context.start_time
                print(f"✅ Makro tamamlandı: {macro.name} ({execution_time:.1f}s)")
                print(f"📊 Başarılı: {context.success_count}, Hatalı: {context.error_count}")
                
                return success
            
            # Arkaplan thread'i başlat
            thread = threading.Thread(target=run_macro, daemon=True)
            thread.start()
            
            return True
            
        except Exception as e:
            print(f"Makro çalıştırma hatası: {e}")
            self.running_macros[macro_id] = False
            return False
    
    def _execute_actions(self, actions: List[MacroAction], context: MacroExecutionContext) -> bool:
        """Aksiyonları çalıştır"""
        for action in actions:
            if not action.enabled:
                continue
            
            context.current_action = action
            
            try:
                print(f"🎯 Aksiyon: {action.description or action.action_type.value}")
                
                success = self._execute_single_action(action, context)
                
                if success:
                    context.success_count += 1
                    context.execution_log.append({
                        "action_id": action.id,
                        "status": "success",
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    context.error_count += 1
                    
                    # Retry logic
                    if action.retry_count < action.max_retries:
                        action.retry_count += 1
                        print(f"🔄 Retry {action.retry_count}/{action.max_retries}")
                        success = self._execute_single_action(action, context)
                    
                    if not success:
                        context.execution_log.append({
                            "action_id": action.id,
                            "status": "failed",
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        # Critical error durumunda dur
                        if action.parameters.get("critical", False):
                            print(f"❌ Critical aksiyon başarısız: {action.description}")
                            return False
                
            except Exception as e:
                print(f"❌ Aksiyon hatası: {e}")
                context.error_count += 1
                
                if action.parameters.get("critical", False):
                    return False
        
        return True
    
    def _execute_single_action(self, action: MacroAction, context: MacroExecutionContext) -> bool:
        """Tek aksiyonu çalıştır"""
        try:
            action_type = action.action_type
            params = action.parameters
            
            # Variable substitution
            params = self._substitute_variables(params, context.variables)
            
            if action_type == ActionType.CLICK:
                return self._execute_click(params)
            
            elif action_type == ActionType.TYPE:
                return self._execute_type(params)
            
            elif action_type == ActionType.WAIT:
                return self._execute_wait(params)
            
            elif action_type == ActionType.SCREENSHOT:
                return self._execute_screenshot(params, context)
            
            elif action_type == ActionType.TEMPLATE_FIND:
                return self._execute_template_find(params, context)
            
            elif action_type == ActionType.TEMPLATE_CLICK:
                return self._execute_template_click(params)
            
            elif action_type == ActionType.LOOP:
                return self._execute_loop(params, context)
            
            elif action_type == ActionType.CONDITION:
                return self._execute_condition(params, context)
            
            elif action_type == ActionType.VARIABLE:
                return self._execute_variable(params, context)
            
            elif action_type == ActionType.FUNCTION:
                return self._execute_function(params, context)
            
            elif action_type == ActionType.RANDOM_DELAY:
                return self._execute_random_delay(params)
            
            elif action_type == ActionType.MOUSE_MOVE:
                return self._execute_mouse_move(params)
            
            elif action_type == ActionType.KEY_PRESS:
                return self._execute_key_press(params)
            
            elif action_type == ActionType.SCROLL:
                return self._execute_scroll(params)
            
            else:
                print(f"Bilinmeyen aksiyon tipi: {action_type}")
                return False
                
        except Exception as e:
            print(f"Aksiyon çalıştırma hatası: {e}")
            return False
    
    def _substitute_variables(self, params: Any, variables: Dict[str, Any]) -> Any:
        """Değişkenleri değiştir"""
        if isinstance(params, str):
            # {variable_name} formatındaki değişkenleri değiştir
            for var_name, var_value in variables.items():
                params = params.replace(f"{{{var_name}}}", str(var_value))
            return params
        
        elif isinstance(params, dict):
            result = {}
            for key, value in params.items():
                result[key] = self._substitute_variables(value, variables)
            return result
        
        elif isinstance(params, list):
            return [self._substitute_variables(item, variables) for item in params]
        
        else:
            return params
    
    def _execute_click(self, params: Dict) -> bool:
        """Click aksiyonu"""
        try:
            x = params.get("x", 0)
            y = params.get("y", 0)
            button = params.get("button", "left")
            clicks = params.get("clicks", 1)
            
            pyautogui.click(x, y, clicks=clicks, button=button)
            
            # Random delay
            delay = params.get("delay", random.uniform(0.1, 0.3))
            time.sleep(delay)
            
            return True
            
        except Exception as e:
            print(f"Click hatası: {e}")
            return False
    
    def _execute_type(self, params: Dict) -> bool:
        """Type aksiyonu"""
        try:
            text = params.get("text", "")
            interval = params.get("interval", 0.05)
            
            pyautogui.type(text, interval=interval)
            return True
            
        except Exception as e:
            print(f"Type hatası: {e}")
            return False
    
    def _execute_wait(self, params: Dict) -> bool:
        """Wait aksiyonu"""
        try:
            duration = params.get("duration", 1.0)
            time.sleep(duration)
            return True
            
        except Exception as e:
            print(f"Wait hatası: {e}")
            return False
    
    def _execute_screenshot(self, params: Dict, context: MacroExecutionContext) -> bool:
        """Screenshot aksiyonu"""
        try:
            filename = params.get("filename", f"screenshot_{int(time.time())}.png")
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            
            # Context'e ekle
            context.screenshots.append({
                "filename": filename,
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            print(f"Screenshot hatası: {e}")
            return False
    
    def _execute_template_find(self, params: Dict, context: MacroExecutionContext) -> bool:
        """Template find aksiyonu"""
        try:
            template_name = params.get("template")
            threshold = params.get("threshold", 0.8)
            save_result = params.get("save_result", True)
            
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            matches = self.find_template(screenshot, template_name, threshold)
            
            if save_result:
                var_name = params.get("variable_name", "template_found")
                context.variables[var_name] = len(matches) > 0
                
                if matches:
                    context.variables[f"{var_name}_location"] = matches[0]
            
            return len(matches) > 0
            
        except Exception as e:
            print(f"Template find hatası: {e}")
            return False
    
    def _execute_template_click(self, params: Dict) -> bool:
        """Template click aksiyonu"""
        try:
            template_name = params.get("template")
            threshold = params.get("threshold", 0.8)
            
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            matches = self.find_template(screenshot, template_name, threshold)
            
            if matches:
                x, y, w, h = matches[0]
                center_x = x + w // 2
                center_y = y + h // 2
                
                # Random offset
                offset_x = random.randint(-3, 3)
                offset_y = random.randint(-3, 3)
                
                pyautogui.click(center_x + offset_x, center_y + offset_y)
                
                delay = params.get("delay", random.uniform(0.1, 0.3))
                time.sleep(delay)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Template click hatası: {e}")
            return False
    
    def _execute_loop(self, params: Dict, context: MacroExecutionContext) -> bool:
        """Loop aksiyonu"""
        try:
            loop_type = params.get("type", "count")
            
            if loop_type == "count":
                count = params.get("count", 1)
                actions = params.get("actions", [])
                
                for i in range(count):
                    context.variables["loop_index"] = i
                    context.loop_stack.append({"type": "count", "index": i, "count": count})
                    
                    # Actions'ları MacroAction objelerine çevir
                    loop_actions = []
                    for action_data in actions:
                        if isinstance(action_data, dict):
                            loop_actions.append(MacroAction.from_dict(action_data))
                        else:
                            loop_actions.append(action_data)
                    
                    success = self._execute_actions(loop_actions, context)
                    context.loop_stack.pop()
                    
                    if not success and params.get("break_on_error", False):
                        return False
                
                return True
            
            elif loop_type == "while":
                condition = params.get("condition", {})
                actions = params.get("actions", [])
                max_iterations = params.get("max_iterations", 100)
                
                iteration = 0
                while iteration < max_iterations:
                    # Koşulu kontrol et
                    if not self._check_condition(condition, context):
                        break
                    
                    context.variables["loop_index"] = iteration
                    context.loop_stack.append({"type": "while", "index": iteration})
                    
                    # Actions'ları çalıştır
                    loop_actions = []
                    for action_data in actions:
                        if isinstance(action_data, dict):
                            loop_actions.append(MacroAction.from_dict(action_data))
                        else:
                            loop_actions.append(action_data)
                    
                    success = self._execute_actions(loop_actions, context)
                    context.loop_stack.pop()
                    
                    if not success and params.get("break_on_error", False):
                        return False
                    
                    iteration += 1
                
                return True
            
        except Exception as e:
            print(f"Loop hatası: {e}")
            return False
    
    def _execute_condition(self, params: Dict, context: MacroExecutionContext) -> bool:
        """Condition aksiyonu"""
        try:
            condition = params.get("condition", {})
            true_actions = params.get("true_actions", [])
            false_actions = params.get("false_actions", [])
            
            if self._check_condition(condition, context):
                actions_to_run = true_actions
            else:
                actions_to_run = false_actions
            
            # Actions'ları çalıştır
            condition_actions = []
            for action_data in actions_to_run:
                if isinstance(action_data, dict):
                    condition_actions.append(MacroAction.from_dict(action_data))
                else:
                    condition_actions.append(action_data)
            
            return self._execute_actions(condition_actions, context)
            
        except Exception as e:
            print(f"Condition hatası: {e}")
            return False
    
    def _check_condition(self, condition: Dict, context: MacroExecutionContext) -> bool:
        """Koşulu kontrol et"""
        try:
            condition_type = ConditionType(condition.get("type"))
            
            if condition_type == ConditionType.TEMPLATE_EXISTS:
                template_name = condition.get("template")
                threshold = condition.get("threshold", 0.8)
                
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                matches = self.find_template(screenshot, template_name, threshold)
                return len(matches) > 0
            
            elif condition_type == ConditionType.TEMPLATE_NOT_EXISTS:
                template_name = condition.get("template")
                threshold = condition.get("threshold", 0.8)
                
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                matches = self.find_template(screenshot, template_name, threshold)
                return len(matches) == 0
            
            elif condition_type == ConditionType.VARIABLE_EQUALS:
                var_name = condition.get("variable")
                expected_value = condition.get("value")
                
                actual_value = context.variables.get(var_name)
                return actual_value == expected_value
            
            elif condition_type == ConditionType.VARIABLE_GREATER:
                var_name = condition.get("variable")
                threshold = condition.get("value")
                
                actual_value = context.variables.get(var_name, 0)
                return actual_value > threshold
            
            elif condition_type == ConditionType.VARIABLE_LESS:
                var_name = condition.get("variable")
                threshold = condition.get("value")
                
                actual_value = context.variables.get(var_name, 0)
                return actual_value < threshold
            
            elif condition_type == ConditionType.TIME_ELAPSED:
                duration = condition.get("duration", 0)
                elapsed = time.time() - context.start_time
                return elapsed >= duration
            
            elif condition_type == ConditionType.RANDOM_CHANCE:
                chance = condition.get("chance", 0.5)  # 0.0 - 1.0
                return random.random() < chance
            
        except Exception as e:
            print(f"Condition check hatası: {e}")
            return False
        
        return False
    
    def _execute_variable(self, params: Dict, context: MacroExecutionContext) -> bool:
        """Variable aksiyonu"""
        try:
            var_name = params.get("name")
            var_value = params.get("value")
            operation = params.get("operation", "set")  # set, add, subtract, multiply
            
            if operation == "set":
                context.variables[var_name] = var_value
            
            elif operation == "add":
                current_value = context.variables.get(var_name, 0)
                context.variables[var_name] = current_value + var_value
            
            elif operation == "subtract":
                current_value = context.variables.get(var_name, 0)
                context.variables[var_name] = current_value - var_value
            
            elif operation == "multiply":
                current_value = context.variables.get(var_name, 1)
                context.variables[var_name] = current_value * var_value
            
            return True
            
        except Exception as e:
            print(f"Variable hatası: {e}")
            return False
    
    def _execute_function(self, params: Dict, context: MacroExecutionContext) -> bool:
        """Function aksiyonu"""
        try:
            function_name = params.get("function")
            function_params = params.get("parameters", {})
            save_result = params.get("save_result", False)
            result_variable = params.get("result_variable", "function_result")
            
            if function_name in self.custom_functions:
                func = self.custom_functions[function_name]
                
                # Parametreleri hazırla
                if isinstance(function_params, dict):
                    result = func(**function_params)
                else:
                    result = func(*function_params)
                
                if save_result:
                    context.variables[result_variable] = result
                
                return True
            else:
                print(f"Fonksiyon bulunamadı: {function_name}")
                return False
                
        except Exception as e:
            print(f"Function hatası: {e}")
            return False
    
    def _execute_random_delay(self, params: Dict) -> bool:
        """Random delay aksiyonu"""
        try:
            min_delay = params.get("min", 0.1)
            max_delay = params.get("max", 1.0)
            
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
            
            return True
            
        except Exception as e:
            print(f"Random delay hatası: {e}")
            return False
    
    def _execute_mouse_move(self, params: Dict) -> bool:
        """Mouse move aksiyonu"""
        try:
            x = params.get("x", 0)
            y = params.get("y", 0)
            duration = params.get("duration", 0.5)
            
            pyautogui.moveTo(x, y, duration=duration)
            return True
            
        except Exception as e:
            print(f"Mouse move hatası: {e}")
            return False
    
    def _execute_key_press(self, params: Dict) -> bool:
        """Key press aksiyonu"""
        try:
            key = params.get("key")
            modifier = params.get("modifier")  # ctrl, alt, shift
            
            if modifier:
                pyautogui.hotkey(modifier, key)
            else:
                pyautogui.press(key)
            
            return True
            
        except Exception as e:
            print(f"Key press hatası: {e}")
            return False
    
    def _execute_scroll(self, params: Dict) -> bool:
        """Scroll aksiyonu"""
        try:
            direction = params.get("direction", "down")  # up, down
            clicks = params.get("clicks", 3)
            x = params.get("x")
            y = params.get("y")
            
            scroll_amount = clicks if direction == "up" else -clicks
            
            if x and y:
                pyautogui.scroll(scroll_amount, x=x, y=y)
            else:
                pyautogui.scroll(scroll_amount)
            
            return True
            
        except Exception as e:
            print(f"Scroll hatası: {e}")
            return False
    
    def find_template(self, screenshot, template_name, threshold=0.8):
        """Template matching"""
        try:
            if isinstance(template_name, str):
                template_path = template_name
                if not os.path.exists(template_path):
                    # Relative path dene
                    template_path = os.path.join("templates", template_name)
                    if not os.path.exists(template_path):
                        return []
                
                template = cv2.imread(template_path)
            else:
                template = template_name
            
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)
            
            if len(locations[0]) > 0:
                matches = []
                for pt in zip(*locations[::-1]):
                    matches.append((pt[0], pt[1], template.shape[1], template.shape[0]))
                return matches
            
        except Exception as e:
            print(f"Template matching hatası: {e}")
        
        return []
    
    def stop_macro(self, macro_id: str):
        """Makroyu durdur"""
        self.running_macros[macro_id] = False
        print(f"🛑 Makro durduruldu: {macro_id}")
    
    def get_macro_status(self, macro_id: str) -> Dict:
        """Makro durumunu al"""
        status = {
            "running": self.running_macros.get(macro_id, False),
            "context": None
        }
        
        if macro_id in self.execution_contexts:
            context = self.execution_contexts[macro_id]
            status["context"] = {
                "start_time": context.start_time,
                "current_action": context.current_action.description if context.current_action else None,
                "success_count": context.success_count,
                "error_count": context.error_count,
                "variables": context.variables
            }
        
        return status
    
    def save_macros(self):
        """Makroları kaydet"""
        try:
            data = {}
            for macro_id, macro in self.macros.items():
                data[macro_id] = macro.to_dict()
            
            with open(self.macros_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f"Makro kaydetme hatası: {e}")
    
    def load_macros(self):
        """Makroları yükle"""
        try:
            if os.path.exists(self.macros_file):
                with open(self.macros_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for macro_id, macro_data in data.items():
                    self.macros[macro_id] = MacroSequence.from_dict(macro_data)
                    
        except Exception as e:
            print(f"Makro yükleme hatası: {e}")
    
    def load_macro_library(self):
        """Makro kütüphanesini yükle"""
        try:
            if os.path.exists(self.library_file):
                with open(self.library_file, 'r', encoding='utf-8') as f:
                    self.macro_library = json.load(f)
        except Exception as e:
            print(f"Makro kütüphanesi yükleme hatası: {e}")
    
    def export_macro(self, macro_id: str, filename: str):
        """Makroyu dışa aktar"""
        try:
            if macro_id not in self.macros:
                raise ValueError(f"Makro bulunamadı: {macro_id}")
            
            macro_data = self.macros[macro_id].to_dict()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(macro_data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Makro dışa aktarıldı: {filename}")
            
        except Exception as e:
            print(f"Makro dışa aktarma hatası: {e}")
    
    def import_macro(self, filename: str) -> str:
        """Makroyu içe aktar"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                macro_data = json.load(f)
            
            # Yeni ID oluştur
            new_macro_id = str(uuid.uuid4())
            macro_data['id'] = new_macro_id
            
            macro = MacroSequence.from_dict(macro_data)
            self.macros[new_macro_id] = macro
            self.save_macros()
            
            print(f"✅ Makro içe aktarıldı: {macro.name}")
            return new_macro_id
            
        except Exception as e:
            print(f"Makro içe aktarma hatası: {e}")
            return None


# Örnek makro oluşturma fonksiyonları
def create_healing_macro(engine: MacroEngine) -> str:
    """Healing makrosu oluştur"""
    macro = engine.create_macro(
        name="Otomatik Healing",
        description="Tüm yaralı askerleri otomatik olarak iyileştirir",
        tags=["healing", "automatic", "troops"]
    )
    
    # Hospital butonuna tıkla
    engine.add_action(macro.id, ActionType.TEMPLATE_CLICK, {
        "template": "hospital_button.png",
        "threshold": 0.8,
        "delay": 1.0
    }, "Hospital'a git")
    
    # Heal all butonunu bekle ve tıkla
    engine.add_action(macro.id, ActionType.TEMPLATE_CLICK, {
        "template": "heal_all_button.png",
        "threshold": 0.8,
        "delay": 0.5
    }, "Heal All'a tıkla")
    
    # Confirm butonuna tıkla
    engine.add_action(macro.id, ActionType.TEMPLATE_CLICK, {
        "template": "confirm_button.png",
        "threshold": 0.8,
        "delay": 1.0
    }, "Healing'i onayla")
    
    # Geri dön
    engine.add_action(macro.id, ActionType.TEMPLATE_CLICK, {
        "template": "back_button.png",
        "threshold": 0.8,
        "delay": 0.5
    }, "Geri dön")
    
    return macro.id


def create_resource_gathering_macro(engine: MacroEngine) -> str:
    """Resource gathering makrosu oluştur"""
    macro = engine.create_macro(
        name="Kaynak Toplama",
        description="Otomatik kaynak toplama march'ları başlatır",
        tags=["resource", "gathering", "march"]
    )
    
    # Değişkenler
    engine.add_action(macro.id, ActionType.VARIABLE, {
        "name": "march_count",
        "value": 0,
        "operation": "set"
    }, "March sayacını sıfırla")
    
    # Loop - 4 march başlat
    engine.add_action(macro.id, ActionType.LOOP, {
        "type": "count",
        "count": 4,
        "actions": [
            {
                "id": str(uuid.uuid4()),
                "action_type": "template_click",
                "parameters": {"template": "world_map.png"},
                "description": "World map'e git"
            },
            {
                "id": str(uuid.uuid4()),
                "action_type": "template_click", 
                "parameters": {"template": "resource_tile.png"},
                "description": "Resource tile'ı seç"
            },
            {
                "id": str(uuid.uuid4()),
                "action_type": "template_click",
                "parameters": {"template": "gather_button.png"},
                "description": "Gather'a tıkla"
            },
            {
                "id": str(uuid.uuid4()),
                "action_type": "template_click",
                "parameters": {"template": "march_button.png"},
                "description": "March'ı başlat"
            },
            {
                "id": str(uuid.uuid4()),
                "action_type": "random_delay",
                "parameters": {"min": 2.0, "max": 5.0},
                "description": "Random bekle"
            }
        ]
    }, "4 kaynak march'ı başlat")
    
    return macro.id


# Test fonksiyonu
def test_macro_engine():
    """Makro motorunu test et"""
    engine = MacroEngine()
    
    print("🔄 Makro Motoru Test Ediliyor...")
    
    # Örnek makrolar oluştur
    healing_macro_id = create_healing_macro(engine)
    gathering_macro_id = create_resource_gathering_macro(engine)
    
    print(f"✅ Healing Makro ID: {healing_macro_id}")
    print(f"✅ Gathering Makro ID: {gathering_macro_id}")
    
    # Makroları listele
    print("\n📋 Kayıtlı Makrolar:")
    for macro_id, macro in engine.macros.items():
        print(f"- {macro.name}: {len(macro.actions)} aksiyon")
    
    print("\n✅ Test tamamlandı!")


if __name__ == "__main__":
    test_macro_engine()
