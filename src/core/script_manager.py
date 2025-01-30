from PySide6.QtCore import QObject, Signal
from ..database.db_manager import DatabaseManager

class ScriptManager(QObject):
    script_executed = Signal(str, str, str)  # script_id, status, log
    
    def __init__(self, autojs_manager):
        super().__init__()
        self.autojs_manager = autojs_manager
        self.autojs_manager.script_status_changed.connect(self._on_script_status_changed)
    
    def add_script(self, name, file_path):
        """添加脚本"""
        return DatabaseManager.add_script(name, file_path)
    
    def delete_script(self, script_id):
        """删除脚本"""
        DatabaseManager.delete_script(script_id)
    
    def get_scripts(self):
        """获取所有脚本"""
        return DatabaseManager.get_scripts()
    
    def execute_script(self, script_id, script_path):
        """执行脚本"""
        if self.autojs_manager.execute_script(script_id, script_path):
            DatabaseManager.add_script_log(
                script_id,
                self.autojs_manager.device_id,
                'started',
                '开始执行脚本'
            )
            return True
        return False
    
    def _on_script_status_changed(self, script_id, status, message):
        """处理脚本状态变化"""
        DatabaseManager.add_script_log(
            script_id,
            self.autojs_manager.device_id,
            status,
            message
        )
        self.script_executed.emit(script_id, status, message) 