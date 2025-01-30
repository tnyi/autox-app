from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                              QListWidgetItem, QHBoxLayout, QPushButton,
                              QFileDialog, QDialog, QLineEdit, QMessageBox)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
import os
from .script_log_dialog import ScriptLogDialog
from ..database.db_manager import DatabaseManager

class AddScriptDialog(QDialog):
    """添加脚本对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加脚本")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 脚本名称输入
        name_layout = QHBoxLayout()
        name_label = QLabel("脚本名称:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入脚本名称")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 脚本文件选择
        file_layout = QHBoxLayout()
        file_label = QLabel("脚本文件:")
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        self.file_path.setPlaceholderText("请选择脚本文件")
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)
        
        # 确定取消按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def _browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择脚本文件", "", "JavaScript Files (*.js)"
        )
        if file_path:
            self.file_path.setText(file_path)
    
    def get_script_info(self):
        """获取脚本信息"""
        return {
            'name': self.name_input.text(),
            'file_path': self.file_path.text()
        }

class ScriptListWidget(QWidget):
    script_selected = Signal(str)  # 发送脚本ID
    script_execute = Signal(str)  # 发送执行脚本的信号
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题栏
        title_widget = QWidget()
        title_widget.setFixedHeight(30)
        title_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 1px solid #e8e8e8;
            }
        """)
        
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        title = QLabel("脚本列表")
        add_btn = QPushButton("添加脚本")
        add_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #1890ff;
                padding: 4px 12px;
                border-radius: 4px;
                background: white;
                color: #1890ff;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #1890ff;
                color: white;
            }
        """)
        add_btn.clicked.connect(self._add_script)
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(add_btn)
        
        layout.addWidget(title_widget)
        
        # 脚本列表
        self.script_list = QListWidget()
        self.script_list.setStyleSheet("""
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
        self.script_list.itemClicked.connect(self._on_script_clicked)
        layout.addWidget(self.script_list)
        
        # 添加脚本执行日志字典
        self.script_logs = {}
        
        # 从数据库加载脚本
        self._load_scripts_from_db()
    
    def _load_scripts_from_db(self):
        """从数据库加载脚本"""
        try:
            scripts = DatabaseManager.get_scripts()
            for script_id, name, file_path in scripts:
                script_info = {
                    'id': script_id,
                    'name': name,
                    'file_path': file_path
                }
                self.add_script(script_info)
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"加载脚本列表失败: {str(e)}")
    
    def _add_script(self):
        """添加脚本"""
        dialog = AddScriptDialog(self)
        if dialog.exec():
            script_info = dialog.get_script_info()
            try:
                # 保存到数据库
                script_id = DatabaseManager.add_script(
                    script_info['name'],
                    script_info['file_path']
                )
                
                # 添加ID到脚本信息
                script_info['id'] = script_id
                
                # 添加到列表
                self.add_script(script_info)
            except Exception as e:
                QMessageBox.warning(self, "添加失败", f"添加脚本失败: {str(e)}")
    
    def _on_script_clicked(self, item):
        """处理脚本被点击的事件"""
        script_id = item.data(Qt.UserRole)
        self.script_selected.emit(script_id)
    
    def add_script(self, script_info):
        """添加脚本到列表"""
        item = QListWidgetItem()
        
        # 创建脚本信息显示widget
        script_widget = QWidget()
        script_layout = QHBoxLayout(script_widget)  # 改用水平布局
        script_layout.setContentsMargins(15, 12, 15, 12)
        
        # 左侧信息布局
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        # 脚本名称
        name_label = QLabel(script_info['name'])
        name_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #333333;
        """)
        info_layout.addWidget(name_label)
        
        # 文件路径
        file_label = QLabel(os.path.basename(script_info['file_path']))
        file_label.setStyleSheet("""
            font-size: 12px;
            color: #666666;
        """)
        info_layout.addWidget(file_label)
        
        # 添加信息布局
        script_layout.addLayout(info_layout, stretch=1)
        
        # 右侧按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)  # 减小按钮间距
        
        # 执行按钮
        execute_btn = QPushButton("运行")
        execute_btn.setFixedWidth(60)
        execute_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #1890ff;
                border-radius: 4px;
                background: white;
                color: #1890ff;
                font-size: 13px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: #1890ff;
                color: white;
            }
        """)
        
        # 查看按钮
        view_btn = QPushButton("日志")
        view_btn.setFixedWidth(60)
        view_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #1890ff;
                border-radius: 4px;
                background: white;
                color: #1890ff;
                font-size: 13px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: #1890ff;
                color: white;
            }
        """)
        
        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setFixedWidth(60)
        delete_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #ff4d4f;
                border-radius: 4px;
                background: white;
                color: #ff4d4f;
                font-size: 13px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: #ff4d4f;
                color: white;
            }
        """)
        
        # 连接按钮信号
        execute_btn.clicked.connect(lambda: self._execute_script(script_info['file_path']))
        view_btn.clicked.connect(lambda: self._view_script_log(script_info['file_path']))
        delete_btn.clicked.connect(lambda: self._delete_script(item, script_info['file_path']))
        
        # 添加按钮到布局
        button_layout.addWidget(execute_btn)
        button_layout.addWidget(view_btn)
        button_layout.addWidget(delete_btn)
        
        script_layout.addLayout(button_layout)
        
        # 设置item大小
        item.setSizeHint(QSize(300, 80))
        
        # 存储脚本路径和ID
        item.setData(Qt.UserRole, script_info['file_path'])  # 用于查找
        item.setData(Qt.UserRole + 2, script_info['id'])     # 存储数据库ID
        
        # 添加到列表
        self.script_list.addItem(item)
        self.script_list.setItemWidget(item, script_widget)
    
    def _execute_script(self, script_path):
        """执行脚本"""
        if not os.path.exists(script_path):
            QMessageBox.warning(self, "错误", "脚本文件不存在")
            return
            
        # 发送执行信号
        self.script_execute.emit(script_path)
        
        # 初始化日志
        if script_path not in self.script_logs:
            self.script_logs[script_path] = []
    
    def _view_script_log(self, script_path):
        """查看脚本日志"""
        if script_path not in self.script_logs:
            QMessageBox.information(self, "提示", "暂无执行日志")
            return
            
        # 获取脚本名称
        script_name = os.path.basename(script_path)
        
        # 显示日志对话框
        log_content = "\n".join(self.script_logs[script_path])
        dialog = ScriptLogDialog(script_name, log_content, self)
        dialog.exec()
    
    def _delete_script(self, item, script_path):
        """删除脚本"""
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除脚本 {os.path.basename(script_path)} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 获取脚本ID
                script_id = item.data(Qt.UserRole + 2)  # 使用UserRole + 2存储数据库ID
                
                # 从数据库中删除
                DatabaseManager.delete_script(script_id)
                
                # 删除日志
                if script_path in self.script_logs:
                    del self.script_logs[script_path]
                
                # 从列表中移除
                row = self.script_list.row(item)
                self.script_list.takeItem(row)
                
            except Exception as e:
                QMessageBox.warning(self, "删除失败", str(e))
    
    def add_script_log(self, script_path, log_entry):
        """添加脚本执行日志"""
        if script_path not in self.script_logs:
            self.script_logs[script_path] = []
        self.script_logs[script_path].append(log_entry) 
    
    def update_script_status(self, script_path, status):
        """更新脚本状态"""
        for i in range(self.script_list.count()):
            item = self.script_list.item(i)
            if item.data(Qt.UserRole) == script_path:
                status_label = item.data(Qt.UserRole + 1)
                if status_label:
                    # 根据状态设置不同的样式
                    if status == 'running':
                        status_label.setText("执行中")
                        status_label.setStyleSheet("""
                            font-size: 12px;
                            color: #2196F3;
                            padding: 2px 6px;
                            border-radius: 2px;
                            background: #E3F2FD;
                        """)
                    elif status == 'success':
                        status_label.setText("成功")
                        status_label.setStyleSheet("""
                            font-size: 12px;
                            color: #4CAF50;
                            padding: 2px 6px;
                            border-radius: 2px;
                            background: #E8F5E9;
                        """)
                    elif status == 'failed':
                        status_label.setText("失败")
                        status_label.setStyleSheet("""
                            font-size: 12px;
                            color: #F44336;
                            padding: 2px 6px;
                            border-radius: 2px;
                            background: #FFEBEE;
                        """)
                    else:
                        status_label.setText("就绪")
                        status_label.setStyleSheet("""
                            font-size: 12px;
                            color: #666666;
                            padding: 2px 6px;
                            border-radius: 2px;
                            background: #f0f0f0;
                        """)
                break 