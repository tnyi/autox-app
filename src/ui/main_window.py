from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from .device_list import DeviceListWidget
from .script_list import ScriptListWidget
from .screen_view import ScreenView
from ..core.scrcpy_manager import ScrcpyManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoX.js 控制台")
        
        # 固定窗口尺寸为 1600x900 (16:9)
        self.setFixedSize(1600, 900)
        
        # 设置窗口标志，只允许最小化和关闭
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowMinimizeButtonHint |  # 允许最小化
            Qt.WindowCloseButtonHint       # 允许关闭
        )
        
        # 创建主窗口布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建左侧布局
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加设备列表
        self.device_list = DeviceListWidget()
        left_layout.addWidget(self.device_list)
        
        # 添加脚本列表
        self.script_list = ScriptListWidget()
        left_layout.addWidget(self.script_list)
        
        # 设置左侧布局比例
        left_layout.setStretch(0, 1)  # 设备列表占比
        left_layout.setStretch(1, 2)  # 脚本列表占比
        
        # 创建中间投屏区域
        self.screen_view = ScreenView()
        
        # 将左侧和中间添加到主布局
        main_layout.addWidget(left_widget, 1)         # 左侧占比1
        main_layout.addWidget(self.screen_view, 3)    # 中间占比3，增加投屏区域的比例 