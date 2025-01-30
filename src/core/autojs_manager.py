import subprocess
import threading
import time
from PySide6.QtCore import QObject, Signal
import os
import re
from datetime import datetime

class AutoJsManager(QObject):
    script_status_changed = Signal(str, str, str)  # script_id, status, message
    
    def __init__(self):
        super().__init__()
        self.device_id = None
        self.connected = False
        self.script_monitor = None
        self.current_script_id = None
        self.current_script_name = None
    
    def connect_to_device(self, device_id):
        """连接到设备"""
        try:
            # 检查设备是否安装了 AutoJs
            result = subprocess.run(
                ['adb', '-s', device_id, 'shell', 'pm', 'list', 'packages', 'org.autojs.autojs6'],
                capture_output=True,
                text=True
            )
            
            if 'org.autojs.autojs6' in result.stdout:
                # 创建必要的目录
                subprocess.run([
                    'adb', '-s', device_id, 'shell',
                    'mkdir', '-p', '/sdcard/脚本'
                ])
                
                self.device_id = device_id
                self.connected = True
                return True
            else:
                print(f"设备 {device_id} 未安装 AutoJs")
                return False
                
        except Exception as e:
            print(f"连接AutoJs失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        self.device_id = None
        self.connected = False
        if self.script_monitor:
            self.script_monitor.stop()
            self.script_monitor = None
    
    def execute_script(self, script_id, script_path):
        """执行脚本"""
        if not self.connected:
            raise Exception("未连接到设备")
        
        try:
            script_name = os.path.basename(script_path)
            # 使用 /sdcard/脚本 目录
            remote_path = f"/sdcard/脚本/{script_name}"
            
            # 推送文件
            result = subprocess.run([
                'adb', '-s', self.device_id, 'push',
                script_path, remote_path
            ], capture_output=True, text=True)
            
            if "failed" in result.stderr:
                raise Exception(f"推送脚本失败: {result.stderr}")
            
            # 启动 AutoJs 执行脚本
            subprocess.run([
                'adb', '-s', self.device_id, 'shell',
                'am', 'start',
                '-n', 'org.autojs.autojs6/org.autojs.autojs.external.open.RunIntentActivity',
                '-d', f'file://{remote_path}',
                '-t', 'text/javascript'
            ])
            
            # 记录当前执行的脚本信息
            self.current_script_id = str(script_id)
            self.current_script_name = script_name
            
            # 发送状态变化信号
            self.script_status_changed.emit(
                self.current_script_id,
                'running',
                f'开始执行脚本: {script_name}'
            )
            
            # 启动脚本监控
            if not self.script_monitor:
                self.script_monitor = ScriptMonitor(self)
                self.script_monitor.start()
            
            return True
            
        except Exception as e:
            print(f"执行脚本失败: {e}")
            self.script_status_changed.emit(
                str(script_id),
                'failed',
                f'执行失败: {str(e)}'
            )
            return False
    
    def get_script_log(self):
        """获取脚本执行日志"""
        if not self.current_script_name:
            return None
            
        try:
            # 从设备获取日志文件
            log_path = f'/storage/emulated/0/AutoJs/logs/{self.current_script_name}.log'
            result = subprocess.run([
                'adb', '-s', self.device_id, 'shell',
                'cat', log_path
            ], capture_output=True, text=True)
            
            return result.stdout if result.stdout else None
        except:
            return None


class ScriptMonitor(threading.Thread):
    """脚本执行状态监控"""
    
    def __init__(self, manager):
        super().__init__(daemon=True)
        self.manager = manager
        self.running = True
        self.last_log_size = 0
    
    def run(self):
        while self.running:
            try:
                if not self.manager.current_script_name:
                    time.sleep(1)
                    continue
                
                # 获取日志内容
                log_content = self.manager.get_script_log()
                if log_content:
                    # 只处理新增的日志内容
                    if len(log_content) > self.last_log_size:
                        new_content = log_content[self.last_log_size:]
                        self.last_log_size = len(log_content)
                        
                        # 检查是否执行完成
                        if "AutoJs 执行完成" in new_content:
                            self.manager.script_status_changed.emit(
                                self.manager.current_script_id,
                                'success',
                                '脚本执行成功'
                            )
                            self.manager.current_script_id = None
                            self.manager.current_script_name = None
                            self.last_log_size = 0
                        elif "AutoJs 执行异常" in new_content:
                            # 提取错误信息
                            error_match = re.search(r"错误信息：(.*)", new_content)
                            error_msg = error_match.group(1) if error_match else "未知错误"
                            
                            self.manager.script_status_changed.emit(
                                self.manager.current_script_id,
                                'failed',
                                f'脚本执行失败: {error_msg}'
                            )
                            self.manager.current_script_id = None
                            self.manager.current_script_name = None
                            self.last_log_size = 0
                        else:
                            # 发送日志更新
                            self.manager.script_status_changed.emit(
                                self.manager.current_script_id,
                                'running',
                                new_content.strip()
                            )
                
                time.sleep(1)  # 每秒检查一次
                
            except Exception as e:
                print(f"监控脚本状态失败: {e}")
                time.sleep(1)
    
    def stop(self):
        """停止监控"""
        self.running = False 