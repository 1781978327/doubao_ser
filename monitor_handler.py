# monitor_handler.py：监控逻辑（目录监控、后台服务启动）
import sys
import os
import subprocess
import time
from PyQt5.QtCore import QThread, pyqtSignal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtWidgets import QMessageBox
import config  # 导入全局变量


# -------------------------- 目录监控线程 --------------------------
class MonitorThread(QThread):
    """监控截图目录，发现新图片时发送信号"""
    new_image_signal = pyqtSignal(str)  # 信号：新图片路径

    def __init__(self):
        super().__init__()
        self.observer = None

    def run(self):
        # 自定义文件事件处理器
        class ImageFileHandler(FileSystemEventHandler):
            def __init__(self, signal):
                self.signal = signal
                self.processed_files = set()  # 避免重复处理同一文件

            def on_created(self, event):
                # 只处理图片文件，排除目录
                if not event.is_directory and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    time.sleep(1)  # 等待文件写入完成
                    if event.src_path not in self.processed_files:
                        self.processed_files.add(event.src_path)
                        self.signal.emit(event.src_path)

        # 启动监控（使用全局配置的监控目录）
        event_handler = ImageFileHandler(self.new_image_signal)
        self.observer = Observer()
        self.observer.schedule(event_handler, path=config.MONITOR_DIR, recursive=False)
        self.observer.start()
        
        # 保持线程运行
        try:
            while not self.isInterruptionRequested():
                time.sleep(1)
        finally:
            self.observer.stop()
            self.observer.join()


# -------------------# -------------------------- 后台启动截图接收服务 --------------------------
def start_image_server_in_background():
    """
    后台启动image_server.py（截图接收服务）
    返回：True=启动成功，False=启动失败
    """
    import sys
    import os
    import subprocess
    import time
    from PyQt5.QtWidgets import QMessageBox
    import config  # 确保已导入全局配置

    # 关键：根据运行环境动态获取 image_server.py 路径
    if getattr(sys, 'frozen', False):
        # 打包后环境（exe运行时）：获取exe所在目录，image_server.py与exe同级
        exe_path = os.path.abspath(sys.executable)  # 获取当前可执行文件路径
        base_dir = os.path.dirname(exe_path)       # 提取exe所在目录（dist目录）
    else:
        # 开发环境（直接运行Python脚本）：当前脚本所在目录，与image_server.py同级
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # 拼接image_server.py的完整路径
    image_server_path = os.path.join(base_dir, "image_server.py")

    # 检查文件是否存在
    if not os.path.exists(image_server_path):
        QMessageBox.critical(
            None, 
            "文件缺失", 
            f"未找到截图接收服务程序：\n{image_server_path}\n"
            f"请确保image_server.py与程序在同一目录！"
        )
        return False

    try:
        # 构造启动命令（传递全局配置的端口和目录）
        cmd = [
            sys.executable,  # 当前Python解释器路径（开发环境）或打包后的内置解释器（exe环境）
            image_server_path,
            "--port", str(config.SERVER_PORT),
            "--save-dir", config.MONITOR_DIR
        ]

        # Windows系统隐藏命令行窗口，其他系统默认显示
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # 启动后台进程，赋值给全局变量
        config.image_server_process = subprocess.Popen(
            cmd,
            startupinfo=startupinfo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 延迟1秒检查启动状态
        time.sleep(1)
        if config.image_server_process.poll() is None:
            # poll()返回None表示进程正在运行
            print(f"[服务整合] 截图接收服务已在后台启动（端口：{config.SERVER_PORT}，目录：{config.MONITOR_DIR}）")
            return True
        else:
            # 进程已退出，获取错误信息
            error = config.image_server_process.stderr.read()
            QMessageBox.critical(
                None, 
                "启动失败", 
                f"截图接收服务启动失败：\n{error}"
            )
            return False

    except Exception as e:
        QMessageBox.critical(
            None, 
            "启动异常", 
            f"启动截图接收服务时出错：\n{str(e)}"
        )
        return False