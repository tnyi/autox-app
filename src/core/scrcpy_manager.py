import subprocess
import threading
import asyncio
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel
import os
import win32gui
import win32con
import time
from asyncio.subprocess import PIPE
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtCore import Qt
import re

class ScrcpyManager(QObject):
    connection_established = Signal()
    connection_failed = Signal(str)
    mirror_started = Signal(QWidget)
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.scrcpy_window = None
        self.device_id = None
        self.adb_proc = None  # 异步adb进程
        self.event_loop = None  # 事件循环
        self.executor = ThreadPoolExecutor(max_workers=1)  # 线程池
        
        # 检查scrcpy是否安装
        self._check_scrcpy_installation()
        
        # 在新线程中启动事件循环
        self.loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()
    
    def _check_scrcpy_installation(self):
        """检查scrcpy是否已安装"""
        try:
            subprocess.run(['scrcpy', '--version'], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("请先安装scrcpy")
    
    def _run_event_loop(self):
        """在独立线程中运行事件循环"""
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_forever()
    
    async def _start_adb_shell(self):
        """异步启动adb shell会话"""
        if not self.device_id:
            return False
        try:
            # 异步启动adb shell进程
            self.adb_proc = await asyncio.create_subprocess_exec(
                'adb', '-s', self.device_id, 'shell',
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE
            )
            return True
        except Exception as e:
            print(f"启动adb shell失败: {e}")
            return False
    
    async def _send_keyevent_async(self, keycode):
        """异步发送按键事件"""
        if not self.device_id:
            return
            
        try:
            if not self.adb_proc or self.adb_proc.returncode is not None:
                # 如果进程不存在或已结束，重新启动
                if not await self._start_adb_shell():
                    return
            
            # 发送命令
            command = f'input keyevent {keycode}\n'
            self.adb_proc.stdin.write(command.encode())
            await self.adb_proc.stdin.drain()
            
        except Exception as e:
            print(f"发送按键事件失败: {e}")
            self.adb_proc = None
    
    def send_keyevent(self, keycode):
        """同步接口调用异步方法"""
        if self.event_loop:
            asyncio.run_coroutine_threadsafe(
                self._send_keyevent_async(keycode), 
                self.event_loop
            )
    
    def home(self):
        """发送HOME键事件"""
        self.send_keyevent('KEYCODE_HOME')
    
    def back(self):
        """发送返回键事件"""
        self.send_keyevent('KEYCODE_BACK')
    
    def recent_apps(self):
        """发送任务键事件"""
        self.send_keyevent('KEYCODE_APP_SWITCH')
    
    def start_screen_mirror(self, device_id, parent_widget=None):
        if self.process:
            self.stop_screen_mirror()
        
        self.device_id = device_id
        
        try:
            # 获取设备屏幕分辨率
            result = subprocess.run(
                ['adb', '-s', device_id, 'shell', 'wm', 'size'],
                capture_output=True,
                text=True
            )
            size_match = re.search(r'(\d+)x(\d+)', result.stdout)
            if not size_match:
                raise Exception("无法获取设备屏幕分辨率")
                
            device_width = int(size_match.group(1))
            device_height = int(size_match.group(2))
            device_ratio = device_width / device_height
            
            # 获取screen_label的尺寸（这是实际显示区域）
            if parent_widget:
                label_rect = parent_widget.screen_label.rect()
                panel_width = label_rect.width() - 50  # 减去控制按钮宽度
                panel_height = label_rect.height()
            else:
                panel_width = 1080
                panel_height = 1920
            
            # 计算最大可能的显示尺寸
            if device_ratio < (panel_width / panel_height):  # 设备更窄
                # 以高度为基准
                window_height = panel_height
                window_width = int(window_height * device_ratio)
            else:  # 设备更宽
                # 以宽度为基准
                window_width = panel_width
                window_height = int(window_width / device_ratio)
            
            # 启动scrcpy进程
            command = [
                'scrcpy',
                '-s', device_id,
                '--window-title', 'scrcpy-mirror',
                '--window-borderless',
                '--window-width', str(window_width),
                '--window-height', str(window_height),
                '--max-fps', '60',
                '--no-audio',
                '--stay-awake',
                '--window-x', '0',
                '--window-y', '0',
                '--show-touches',
                '--disable-screensaver',
                '--shortcut-mod', 'lctrl',
                '--always-on-top',
                '--mouse-bind', '++++'
            ]
            
            if os.name == 'nt':
                command.extend(['--render-driver', 'direct3d'])
            
            self.process = subprocess.Popen(command)
            
            # 等待scrcpy窗口创建
            hwnd = self._wait_for_window(max_attempts=15)
            
            if hwnd and parent_widget:
                # 获取screen_label的窗口句柄和位置
                parent_hwnd = parent_widget.screen_label.winId()
                parent_rect = win32gui.GetWindowRect(parent_hwnd)
                
                # 设置窗口样式
                style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                style = style & ~(win32con.WS_POPUP | win32con.WS_CAPTION | win32con.WS_THICKFRAME)
                style = style | win32con.WS_CHILD
                win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
                
                # 设置父窗口
                win32gui.SetParent(hwnd, parent_hwnd)
                
                # 计算居中位置（相对于父窗口）
                x = (parent_rect[2] - parent_rect[0] - window_width) // 2
                y = (parent_rect[3] - parent_rect[1] - window_height) // 2
                
                # 调整窗口位置和大小
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_TOP,
                    x, y,
                    window_width, window_height,
                    win32con.SWP_SHOWWINDOW
                )
                
                self.scrcpy_window = hwnd
                
                # 隐藏等待提示
                parent_widget.status_container.hide()
                
                # 发送成功信号
                self.connection_established.emit()
            else:
                # 检查进程输出以获取更详细的错误信息
                stdout, stderr = self.process.communicate()
                error_msg = f"无法找到scrcpy窗口\n{stderr if stderr else ''}"
                self.connection_failed.emit(error_msg)
                self.stop_screen_mirror()
                return
            
            # 启动监控线程
            threading.Thread(target=self._monitor_process, daemon=True).start()
            
        except Exception as e:
            self.connection_failed.emit(str(e))
            self.stop_screen_mirror()
    
    def _monitor_process(self):
        if self.process:
            self.process.wait()
            if self.process.returncode != 0:
                self.connection_failed.emit("屏幕镜像连接断开")
            self.process = None
            self.scrcpy_window = None
    
    def stop_screen_mirror(self):
        # 关闭adb shell会话
        if self.adb_proc:
            try:
                if self.event_loop:
                    asyncio.run_coroutine_threadsafe(
                        self.adb_proc.terminate(), 
                        self.event_loop
                    )
            except:
                pass
            self.adb_proc = None
        
        if self.scrcpy_window:
            try:
                win32gui.SetParent(self.scrcpy_window, 0)
                win32gui.ShowWindow(self.scrcpy_window, win32con.SW_HIDE)
            except:
                pass
            self.scrcpy_window = None
        
        if self.process:
            self.process.terminate()
            self.process = None 
    
    def __del__(self):
        """清理资源"""
        if self.event_loop:
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)
        if self.executor:
            self.executor.shutdown(wait=False) 
    
    def _find_scrcpy_window(self):
        """查找scrcpy窗口"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if 'scrcpy-mirror' in title.lower():
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        return windows[0] if windows else None

    def _wait_for_window(self, max_attempts=10):
        """等待scrcpy窗口创建，最多尝试指定次数"""
        for _ in range(max_attempts):
            hwnd = self._find_scrcpy_window()
            if hwnd:
                return hwnd
            time.sleep(0.5)  # 每次等待0.5秒
        return None 