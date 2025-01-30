import subprocess
from PySide6.QtCore import QObject, Signal
import threading
import time

class DeviceManager(QObject):
    device_connected = Signal(str)
    device_disconnected = Signal(str)
    multiple_devices_detected = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.connected_devices = set()
        self.monitoring = False
    
    def start_monitoring(self):
        self.monitoring = True
        threading.Thread(target=self._monitor_devices, daemon=True).start()
    
    def _monitor_devices(self):
        while self.monitoring:
            try:
                # 获取已连接设备列表
                result = subprocess.check_output(['adb', 'devices']).decode()
                current_devices = set()
                
                for line in result.split('\n')[1:]:
                    if '\tdevice' in line:
                        device_id = line.split('\t')[0]
                        current_devices.add(device_id)
                
                # 检查新连接的设备
                new_devices = current_devices - self.connected_devices
                for device_id in new_devices:
                    if len(current_devices) > 1:
                        self.multiple_devices_detected.emit(list(current_devices))
                    else:
                        self.device_connected.emit(device_id)
                        self._check_autojs_installation(device_id)
                
                # 检查断开连接的设备
                disconnected_devices = self.connected_devices - current_devices
                for device_id in disconnected_devices:
                    self.device_disconnected.emit(device_id)
                
                self.connected_devices = current_devices
                time.sleep(1)
                
            except Exception as e:
                print(f"设备监控错误: {e}")
                time.sleep(1)
    
    def _check_autojs_installation(self, device_id):
        try:
            result = subprocess.check_output(
                ['adb', '-s', device_id, 'shell', 'pm', 'list', 'packages', '|', 'grep', 'org.autojs']
            ).decode()
            
            if 'org.autojs' not in result:
                self._install_autojs(device_id)
                
        except subprocess.CalledProcessError:
            self._install_autojs(device_id)
    
    def _install_autojs(self, device_id):
        try:
            subprocess.check_call([
                'adb', '-s', device_id, 'install', 'resources/autojs.apk'
            ])
            print(f"AutoX.js 已成功安装到设备 {device_id}")
        except Exception as e:
            print(f"安装 AutoX.js 失败: {e}") 