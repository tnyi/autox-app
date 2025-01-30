from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                              QListWidget, QListWidgetItem, QPushButton)
from PySide6.QtCore import Signal

class DeviceSelectionDialog(QDialog):
    device_selected = Signal(str)  # device_id
    
    def __init__(self, devices, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择设备")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 提示信息
        label = QLabel("检测到多个设备，请选择要连接的设备：")
        layout.addWidget(label)
        
        # 设备列表
        self.device_list = QListWidget()
        for device_id in devices:
            item = QListWidgetItem(device_id)
            self.device_list.addItem(item)
        layout.addWidget(self.device_list)
        
        # 确认按钮
        confirm_btn = QPushButton("确认")
        confirm_btn.clicked.connect(self._on_confirm)
        layout.addWidget(confirm_btn)
    
    def _on_confirm(self):
        current_item = self.device_list.currentItem()
        if current_item:
            self.device_selected.emit(current_item.text())
            self.accept() 