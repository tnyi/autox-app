from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QStackedWidget, 
                              QHBoxLayout, QPushButton, QGridLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

class ScreenView(QWidget):
    # 添加按键信号
    home_clicked = Signal()
    back_clicked = Signal()
    recent_clicked = Signal()
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 标题
        title = QLabel("设备屏幕")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(30)
        title.setStyleSheet("""
            QLabel {
                background-color: white;
                border-bottom: 1px solid #e8e8e8;
                padding: 8px;
                font-size: 14px;
                color: #333;
            }
        """)
        self.layout.addWidget(title)
        
        # 创建内容容器
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f5f5f5;")
        self.layout.addWidget(content_widget)
        
        # 使用相对布局
        content_widget.setLayout(None)  # 移除默认布局
        
        # 投屏区域容器
        self.screen_container = QWidget(content_widget)
        screen_container_layout = QVBoxLayout(self.screen_container)
        screen_container_layout.setContentsMargins(0, 0, 0, 0)
        screen_container_layout.setSpacing(0)
        
        # 堆叠部件
        self.stack = QStackedWidget()
        screen_container_layout.addWidget(self.stack)
        
        # 默认视图
        self.default_widget = QWidget()
        default_layout = QVBoxLayout(self.default_widget)
        default_layout.setContentsMargins(0, 0, 0, 0)
        default_layout.setSpacing(0)
        
        # 屏幕显示区域
        self.screen_label = QLabel()
        self.screen_label.setAlignment(Qt.AlignCenter)
        self.screen_label.setStyleSheet("background-color: #f5f5f5;")
        default_layout.addWidget(self.screen_label)
        
        # 状态标签容器 - 改为内容容器的子部件
        self.status_container = QWidget(content_widget)  # 修改父部件
        self.status_container.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QLabel {
                background-color: rgba(0, 0, 0, 50%);
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        
        # 状态标签
        self.status_label = QLabel("等待设备连接...")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # 将状态标签添加到容器
        status_layout = QVBoxLayout(self.status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.addWidget(self.status_label)
        status_layout.setAlignment(Qt.AlignCenter)
        
        self.stack.addWidget(self.default_widget)
        
        # 创建控制按钮面板
        control_panel = QWidget(content_widget)
        control_panel.setObjectName("control_panel")  # 设置对象名称
        control_panel.setFixedWidth(50)
        control_panel.setStyleSheet("""
            QWidget {
                background-color: white;
                border-left: 1px solid #e8e8e8;
            }
            QPushButton {
                border: 1px solid #1890ff;
                padding: 8px 12px;
                margin: 4px;
                border-radius: 4px;
                background-color: white;
                color: #1890ff;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1890ff;
                color: white;
            }
        """)
        
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(4, 4, 4, 4)
        control_layout.setSpacing(4)
        
        # 添加控制按钮
        self.home_btn = QPushButton("⌂")
        self.home_btn.setToolTip("主页")
        self.home_btn.clicked.connect(self.home_clicked)
        
        self.back_btn = QPushButton("←")
        self.back_btn.setToolTip("返回")
        self.back_btn.clicked.connect(self.back_clicked)
        
        self.recent_btn = QPushButton("□")
        self.recent_btn.setToolTip("任务")
        self.recent_btn.clicked.connect(self.recent_clicked)
        
        # 添加按钮到布局
        control_layout.addWidget(self.home_btn)
        control_layout.addWidget(self.back_btn)
        control_layout.addWidget(self.recent_btn)
        control_layout.addStretch()
    
    def resizeEvent(self, event):
        """处理窗口大小变化事件"""
        super().resizeEvent(event)
        
        # 调整投屏区域和控制面板的位置和大小
        content_rect = self.rect()
        content_rect.setTop(30)  # 标题高度
        
        # 设置投屏区域大小和位置
        screen_width = content_rect.width()
        self.screen_container.setGeometry(0, 30, screen_width, content_rect.height() - 30)
        
        # 调整状态容器位置到中间
        if self.status_container:
            label_size = self.status_label.sizeHint()
            container_width = label_size.width() + 40  # 添加一些边距
            container_height = label_size.height() + 20
            
            # 计算居中位置
            x = (screen_width - container_width) // 2
            y = (content_rect.height() - container_height) // 2
            
            self.status_container.setGeometry(x, y, container_width, container_height)
        
        # 获取scrcpy窗口的位置和大小
        scrcpy_window = None
        for child in self.screen_label.children():
            if isinstance(child, QWidget) and child.windowTitle() == 'scrcpy-mirror':
                scrcpy_window = child
                break
        
        if scrcpy_window:
            # 获取scrcpy窗口的几何信息
            scrcpy_rect = scrcpy_window.geometry()
            
            # 设置控制面板大小和位置
            control_panel = self.findChild(QWidget, "control_panel")
            if control_panel:
                x = scrcpy_rect.right()  # 放在scrcpy窗口右侧
                y = scrcpy_rect.top()    # 与scrcpy窗口顶部对齐
                control_panel.setGeometry(x, y, 50, scrcpy_rect.height())
    
    def set_video_widget(self, widget):
        """设置视频窗口部件"""
        # 如果堆叠部件中已有超过一个部件，移除旧的视频窗口
        if self.stack.count() > 1:
            old_widget = self.stack.widget(1)
            self.stack.removeWidget(old_widget)
            old_widget.deleteLater()
        
        # 添加新的视频窗口并切换到它
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)
        
        # 隐藏状态容器
        if self.status_container:
            self.status_container.setVisible(False)  # 使用setVisible替代hide
    
    def update_screen(self, pixmap):
        """更新屏幕显示"""
        scaled_pixmap = pixmap.scaled(
            self.screen_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.screen_label.setPixmap(scaled_pixmap)
    
    def show_message(self, message):
        """显示状态信息"""
        self.status_label.setText(message)
        self.status_container.show()
        # 立即触发重新布局以更新位置
        self.resizeEvent(None)
        # 切换回默认视图
        self.stack.setCurrentWidget(self.default_widget) 