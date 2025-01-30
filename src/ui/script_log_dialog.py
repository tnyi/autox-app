from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class ScriptLogDialog(QDialog):
    def __init__(self, script_name, log_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"脚本日志 - {script_name}")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
            }
        """)
        self.log_text.setText(log_content)
        layout.addWidget(self.log_text)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout) 