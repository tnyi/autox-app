from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                              QListWidgetItem, QHBoxLayout)
from PySide6.QtCore import Qt, Signal, QSize
import subprocess

class DeviceListWidget(QWidget):
    device_selected = Signal(str)  # 发送设备ID
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title = QLabel("设备列表")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                background-color: white;
                border-bottom: 1px solid #e8e8e8;
                padding: 8px;
                font-size: 14px;
                color: #333;
            }
        """)
        title.setFixedHeight(30)
        layout.addWidget(title)
        
        # 设备列表
        self.device_list = QListWidget()
        self.device_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: white;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e6f7ff;
                color: #1890ff;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        self.device_list.itemClicked.connect(self._on_device_clicked)
        layout.addWidget(self.device_list)
    
    def _get_device_info(self, device_id):
        """获取设备型号和安卓版本"""
        try:
            # 获取设备型号
            model = subprocess.check_output(
                ['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.model'],
                universal_newlines=True
            ).strip()
            
            # 获取安卓版本
            version = subprocess.check_output(
                ['adb', '-s', device_id, 'shell', 'getprop', 'ro.build.version.release'],
                universal_newlines=True
            ).strip()
            
            return model, version
        except:
            return "未知设备", "未知版本"
    
    def _on_device_clicked(self, item):
        """处理设备被点击的事件"""
        # 发送设备ID（存储在item的data中）
        device_id = item.data(Qt.UserRole)
        self.device_selected.emit(device_id)
    
    def add_device(self, device_id):
        """添加设备到列表"""
        # 获取设备信息
        model, version = self._get_device_info(device_id)
        
        # 创建设备信息显示widget
        item = QListWidgetItem()
        
        # 创建设备信息标签
        device_widget = QWidget()
        device_layout = QVBoxLayout(device_widget)
        device_layout.setContentsMargins(15, 15, 15, 15)  # 增加整体边距
        device_layout.setSpacing(12)  # 增加标题和底部信息的间距
        
        # 设备型号
        model_label = QLabel(f"{model}")
        model_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold;
            color: #333333;
            padding: 2px 0;
        """)
        device_layout.addWidget(model_label)
        
        # 创建水平布局来放置ID和版本号
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)  # 增加ID和版本号之间的间距
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # 设备ID
        id_label = QLabel(f"ID: {device_id}")
        id_label.setStyleSheet("""
            font-size: 12px; 
            color: #666666;
            background-color: #f5f5f5;
            padding: 6px 10px;
            border-radius: 4px;
            min-width: 180px;  /* 设置最小宽度 */
            min-height: 20px;
        """)
        info_layout.addWidget(id_label)
        
        # 安卓版本
        version_label = QLabel(f"Android {version}")
        version_label.setStyleSheet("""
            font-size: 12px; 
            color: #666666;
            background-color: #f5f5f5;
            padding: 6px 10px;
            border-radius: 4px;
            min-width: 80px;  /* 设置最小宽度 */
            min-height: 20px;
        """)
        info_layout.addWidget(version_label)
        info_layout.addStretch()
        
        device_layout.addLayout(info_layout)
        
        # 设置item的最小高度和宽度
        item.setSizeHint(QSize(300, 120))  # 设置固定大小
        
        # 存储设备ID
        item.setData(Qt.UserRole, device_id)
        
        # 添加到列表
        self.device_list.addItem(item)
        self.device_list.setItemWidget(item, device_widget)
    
    def remove_device(self, device_id):
        """移除设备"""
        for i in range(self.device_list.count()):
            item = self.device_list.item(i)
            if item.data(Qt.UserRole) == device_id:
                self.device_list.takeItem(i)
                break 