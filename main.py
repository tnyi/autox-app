import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.core.device_manager import DeviceManager
from src.core.script_manager import ScriptManager
from src.core.scrcpy_manager import ScrcpyManager
from src.database.db_manager import DatabaseManager
from src.ui.device_dialog import DeviceSelectionDialog
from src.core.autojs_manager import AutoJsManager
import os

class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # 初始化数据库
        DatabaseManager.init_database()
        
        # 初始化管理器
        self.device_manager = DeviceManager()
        self.autojs_manager = AutoJsManager()
        self.script_manager = ScriptManager(self.autojs_manager)
        self.scrcpy_manager = ScrcpyManager()
        
        # 创建主窗口
        self.main_window = MainWindow()
        
        # 连接信号
        self._connect_signals()
        
        # 启动设备监控
        self.device_manager.start_monitoring()
    
    def _connect_signals(self):
        # 设备管理器信号
        self.device_manager.device_connected.connect(self._on_device_connected)
        self.device_manager.device_disconnected.connect(self._on_device_disconnected)
        self.device_manager.multiple_devices_detected.connect(self._on_multiple_devices)
        
        # 设备列表信号
        self.main_window.device_list.device_selected.connect(self._on_device_selected)
        
        # 脚本管理器信号
        self.script_manager.script_executed.connect(self._on_script_executed)
        
        # 屏幕镜像信号
        self.scrcpy_manager.connection_failed.connect(self._on_mirror_failed)
        self.scrcpy_manager.mirror_started.connect(self.main_window.screen_view.set_video_widget)
        
        # 添加按键控制信号连接
        self.main_window.screen_view.home_clicked.connect(self.scrcpy_manager.home)
        self.main_window.screen_view.back_clicked.connect(self.scrcpy_manager.back)
        self.main_window.screen_view.recent_clicked.connect(self.scrcpy_manager.recent_apps)
        
        # 脚本列表信号
        self.main_window.script_list.script_execute.connect(self._on_script_execute)
        
        # 脚本状态变化信号
        self.autojs_manager.script_status_changed.connect(self._on_script_status_changed)
    
    def _on_device_connected(self, device_id):
        """处理设备连接事件"""
        self.main_window.device_list.add_device(device_id)
        # 尝试连接 AutoJs
        if self.autojs_manager.connect_to_device(device_id):
            print(f"已连接到设备 {device_id} 的 AutoJs 服务")
        else:
            print(f"无法连接到设备 {device_id} 的 AutoJs 服务")
    
    def _on_device_disconnected(self, device_id):
        """处理设备断开事件"""
        self.main_window.device_list.remove_device(device_id)
        self.scrcpy_manager.stop_screen_mirror()
        # 断开 AutoJs 连接
        if self.autojs_manager.device_id == device_id:
            self.autojs_manager.disconnect()
    
    def _on_multiple_devices(self, devices):
        dialog = DeviceSelectionDialog(devices, self.main_window)
        dialog.device_selected.connect(self._on_device_selected)
        dialog.exec_()
    
    def _on_device_selected(self, device_id):
        """处理设备被选中的事件"""
        # 检查当前是否已经在投屏这个设备
        if (self.scrcpy_manager.process and 
            self.scrcpy_manager.device_id == device_id):
            return
            
        # 停止之前的投屏
        self.scrcpy_manager.stop_screen_mirror()
        # 启动新的投屏
        self.scrcpy_manager.start_screen_mirror(device_id, self.main_window.screen_view)
    
    def _on_script_executed(self, script_id, status, log):
        """处理脚本执行状态变化"""
        # 获取脚本路径
        script_path = self._get_script_path_by_id(script_id)
        if script_path:
            self.main_window.script_list.add_script_log(script_path, log)
    
    def _on_mirror_failed(self, error):
        self.main_window.screen_view.show_message(f"屏幕镜像失败: {error}")
    
    def _on_script_execute(self, script_path):
        """处理脚本执行请求"""
        # 检查是否有设备连接
        if not self.autojs_manager.connected:
            self.main_window.script_list.add_script_log(
                script_path, 
                "错误: AutoJs 服务未连接"
            )
            return
        
        try:
            # 从数据库获取脚本ID
            script_id = self._get_script_id_by_path(script_path)
            if not script_id:
                raise Exception("脚本未在数据库中注册")
            
            # 执行脚本
            if self.script_manager.execute_script(script_id, script_path):
                self.main_window.script_list.add_script_log(
                    script_path, 
                    f"开始执行脚本: {os.path.basename(script_path)}"
                )
            else:
                raise Exception("脚本执行失败")
                
        except Exception as e:
            self.main_window.script_list.add_script_log(
                script_path, 
                f"执行失败: {str(e)}"
            )
    
    def _get_script_id_by_path(self, script_path):
        """根据脚本路径获取ID"""
        scripts = DatabaseManager.get_scripts()
        for script_id, _, path in scripts:
            if path == script_path:
                return script_id
        return None
    
    def _get_script_path_by_id(self, script_id):
        """根据ID获取脚本路径"""
        scripts = DatabaseManager.get_scripts()
        for sid, _, path in scripts:
            if str(sid) == str(script_id):
                return path
        return None
    
    def _on_script_status_changed(self, script_id, status, message):
        """处理脚本状态变化"""
        script_path = self._get_script_path_by_id(script_id)
        if script_path:
            # 更新UI状态
            self.main_window.script_list.update_script_status(script_path, status)
            # 添加日志
            self.main_window.script_list.add_script_log(script_path, message)
    
    def run(self):
        self.main_window.show()
        return self.app.exec_()

if __name__ == "__main__":
    app = Application()
    sys.exit(app.run()) 