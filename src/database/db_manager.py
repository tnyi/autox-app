import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    DB_FILE = "autox.db"
    
    @classmethod
    def init_database(cls):
        """初始化数据库"""
        conn = sqlite3.connect(cls.DB_FILE)
        cursor = conn.cursor()
        
        # 创建脚本表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建脚本执行日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS script_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_id INTEGER,
                device_id TEXT,
                status TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (script_id) REFERENCES scripts (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    @classmethod
    def add_script(cls, name, file_path):
        """添加脚本"""
        conn = sqlite3.connect(cls.DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO scripts (name, file_path) VALUES (?, ?)',
                (name, file_path)
            )
            script_id = cursor.lastrowid
            conn.commit()
            return script_id
        finally:
            conn.close()
    
    @classmethod
    def get_scripts(cls):
        """获取所有脚本"""
        conn = sqlite3.connect(cls.DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id, name, file_path FROM scripts')
            return cursor.fetchall()
        finally:
            conn.close()
    
    @classmethod
    def delete_script(cls, script_id):
        """删除脚本"""
        conn = sqlite3.connect(cls.DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM scripts WHERE id = ?', (script_id,))
            cursor.execute('DELETE FROM script_logs WHERE script_id = ?', (script_id,))
            conn.commit()
        finally:
            conn.close()
    
    @classmethod
    def add_script_log(cls, script_id, device_id, status, message):
        """添加脚本执行日志"""
        conn = sqlite3.connect(cls.DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO script_logs (script_id, device_id, status, message) VALUES (?, ?, ?, ?)',
                (script_id, device_id, status, message)
            )
            conn.commit()
        finally:
            conn.close()
    
    @classmethod
    def get_script_logs(cls, script_id):
        """获取脚本的执行日志"""
        conn = sqlite3.connect(cls.DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'SELECT device_id, status, message, created_at FROM script_logs WHERE script_id = ? ORDER BY created_at DESC',
                (script_id,)
            )
            return cursor.fetchall()
        finally:
            conn.close() 