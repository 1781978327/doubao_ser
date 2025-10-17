# ui_components.py：UI组件（配置窗口、主窗口）
import os
import base64
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QLabel, QTextEdit, 
                             QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                             QLineEdit, QDialog, QMessageBox, QApplication)
from PyQt5.QtGui import QPixmap, QFont, QTextCursor
from PyQt5.QtCore import Qt, QTimer
from config import (MARKDOWN_CSS, WAIT_SECONDS_AFTER_ANALYSIS,
                    DEFAULT_API_KEY, DEFAULT_SERVER_PORT, DEFAULT_MONITOR_DIR, DEFAULT_CLEAR_INTERVAL)
import config  # 导入全局变量
from ai_handler import format_markdown_with_code, ApiThread
from monitor_handler import MonitorThread


# -------------------------- 初始化配置窗口 --------------------------
class InitConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("服务端初始化配置")
        self.setGeometry(200, 200, 450, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 1. API Key配置
        api_layout = QHBoxLayout()
        api_label = QLabel("ARK API Key：")
        api_label.setFixedWidth(100)
        self.api_edit = QLineEdit()
        self.api_edit.setPlaceholderText(f"不填使用默认值：{DEFAULT_API_KEY[:10]}...")
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_edit)
        main_layout.addLayout(api_layout)

        # 2. 服务端端口配置
        port_layout = QHBoxLayout()
        port_label = QLabel("服务端端口：")
        port_label.setFixedWidth(100)
        self.port_edit = QLineEdit()
        self.port_edit.setPlaceholderText(f"不填使用默认值：{DEFAULT_SERVER_PORT}（需与客户端一致）")
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_edit)
        main_layout.addLayout(port_layout)

        # 3. 监控目录配置
        dir_layout = QHBoxLayout()
        dir_label = QLabel("监控目录：")
        dir_label.setFixedWidth(100)
        self.dir_edit = QLineEdit()
        self.dir_edit.setPlaceholderText(f"不填使用默认值：{DEFAULT_MONITOR_DIR}")
        self.dir_btn = QPushButton("选择目录")
        self.dir_btn.clicked.connect(self.select_dir)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(self.dir_btn)
        main_layout.addLayout(dir_layout)

        # 4. 清屏间隔配置
        clear_layout = QHBoxLayout()
        clear_label = QLabel("清屏间隔(秒)：")
        clear_label.setFixedWidth(100)
        self.clear_edit = QLineEdit()
        self.clear_edit.setPlaceholderText(f"不填使用默认值：{DEFAULT_CLEAR_INTERVAL}（3分钟）")
        clear_layout.addWidget(clear_label)
        clear_layout.addWidget(self.clear_edit)
        main_layout.addLayout(clear_layout)

        # 5. 确认/取消按钮
        btn_layout = QHBoxLayout()
        self.confirm_btn = QPushButton("确认配置并启动服务")
        self.confirm_btn.clicked.connect(self.confirm_config)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch(1)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def select_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择截图监控目录")
        if dir_path:
            self.dir_edit.setText(dir_path)

    def confirm_config(self):
        # 1. 处理API Key
        api_key = self.api_edit.text().strip() or DEFAULT_API_KEY
        # 2. 处理端口
        port_input = self.port_edit.text().strip()
        try:
            server_port = int(port_input) if port_input else DEFAULT_SERVER_PORT
            if not (1024 <= server_port <= 65535):
                QMessageBox.warning(self, "配置错误", "端口需在1024-65535之间！")
                return
        except ValueError:
            QMessageBox.warning(self, "配置错误", "端口需为整数！")
            return
        # 3. 处理监控目录
        monitor_dir = self.dir_edit.text().strip() or DEFAULT_MONITOR_DIR
        if not os.path.exists(monitor_dir):
            os.makedirs(monitor_dir)
        # 4. 处理清屏间隔
        clear_input = self.clear_edit.text().strip()
        try:
            clear_interval = int(clear_input) if clear_input else DEFAULT_CLEAR_INTERVAL
            if clear_interval <= 0:
                QMessageBox.warning(self, "配置错误", "清屏间隔需为正整数！")
                return
        except ValueError:
            QMessageBox.warning(self, "配置错误", "清屏间隔需为整数！")
            return

        # 更新全局变量
        config.api_key = api_key
        config.SERVER_PORT = server_port
        config.MONITOR_DIR = monitor_dir
        config.CLEAR_INTERVAL = clear_interval
        self.accept()


# -------------------------- 主窗口 --------------------------
class ImageChatMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base64_image = None
        self.monitor_thread = None
        self.is_ai_busy = False
        self.remaining_wait = 0
        self.wait_timer = QTimer()
        self.pending_image = None
        self.clear_timer = QTimer()
        self.init_ui()
        self.start_monitoring()
        self.init_timers()
        self.show_current_config()

    def init_ui(self):
        self.setWindowTitle("截图分析服务端（整合版）")
        self.setGeometry(100, 100, 950, 750)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # 主布局
        main_layout = QVBoxLayout()

        # 1. 图片选择区
        image_layout = QHBoxLayout()
        self.select_btn = QPushButton("选择本地图片")
        self.select_btn.clicked.connect(self.select_image)
        self.image_label = QLabel("未选择图片")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(220)
        self.image_label.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
        image_layout.addWidget(self.select_btn)
        image_layout.addWidget(self.image_label, stretch=1)
        main_layout.addLayout(image_layout)

        # 2. 对话历史区
        self.history_area = QTextEdit()
        self.history_area.setReadOnly(True)
        self.history_area.setAcceptRichText(True)
        self.history_area.setPlaceholderText("对话历史将显示在这里...")
        global_font = QFont("SimHei", 10)
        self.history_area.setFont(global_font)
        main_layout.addWidget(self.history_area)

        # 3. 输入区+控制按钮
        input_layout = QHBoxLayout()
        self.question_edit = QTextEdit()
        self.question_edit.setMaximumHeight(70)
        self.question_edit.setPlaceholderText("输入问题（自动/手动发送均用此问题）")
        self.question_edit.setFont(global_font)
        self.question_edit.setPlainText("怎么做。")
        
        self.skip_wait_btn = QPushButton("跳过30秒等待")
        self.skip_wait_btn.clicked.connect(self.skip_wait)
        self.skip_wait_btn.setEnabled(False)
        
        self.manual_clear_btn = QPushButton("手动清屏")
        self.manual_clear_btn.clicked.connect(self.manual_clear_history)
        
        self.send_btn = QPushButton("手动发送请求")
        self.send_btn.clicked.connect(self.send_question)
        self.send_btn.setEnabled(False)

        input_layout.addWidget(self.question_edit, stretch=1)
        input_layout.addWidget(self.skip_wait_btn)
        input_layout.addWidget(self.manual_clear_btn)
        input_layout.addWidget(self.send_btn)
        main_layout.addLayout(input_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def init_timers(self):
        # 等待定时器（分析后冷却）
        self.wait_timer.setInterval(1000)
        self.wait_timer.timeout.connect(self.update_wait_time)
        # 清屏定时器
        self.clear_timer.setInterval(config.CLEAR_INTERVAL * 1000)
        self.clear_timer.timeout.connect(self.auto_clear_history)
        self.clear_timer.start()

    def show_current_config(self):
        # 显示全局配置和服务状态
        server_status = "✅ 运行中" if (config.image_server_process and config.image_server_process.poll() is None) else "❌ 已停止"
        config_text = f"""
<div class='config-info'>📋 当前服务端配置：</div>
- 服务端端口：{config.SERVER_PORT}（客户端需填写相同端口）
- 截图监控目录：{os.path.abspath(config.MONITOR_DIR)}
- 自动清屏间隔：{config.CLEAR_INTERVAL // 60}分钟（{config.CLEAR_INTERVAL}秒）
- API Key：已配置（显示前10位：{config.client.api_key[:10]}...）
<div class='server-status'>🔌 截图接收服务状态：{server_status}</div>
"""
        self.append_markdown(config_text)
        self.append_markdown(f"<div class='clear-tip'>🗑️ 自动清屏已开启，每{config.CLEAR_INTERVAL//60}分钟清屏一次</div>\n")

    def auto_clear_history(self):
        # 自动清屏（保留配置信息）
        clear_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        server_status = "✅ 运行中" if (config.image_server_process and config.image_server_process.poll() is None) else "❌ 已停止"
        base_info = f"""
<div class='clear-tip'>📅 历史记录已清屏（清屏时间：{clear_time}）</div>
<div class='config-info'>📋 当前配置：端口{config.SERVER_PORT} | 监控目录{os.path.abspath(config.MONITOR_DIR)} | 清屏{config.CLEAR_INTERVAL//60}分钟</div>
<div class='server-status'>🔌 截图接收服务状态：{server_status}</div>
<div class='auto-monitor'>🔍 目录监控正常，等待新截图...</div>
<div class='clear-tip'>🗑️ 下次自动清屏：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
"""
        full_html = f"<html><head>{MARKDOWN_CSS}</head><body>{format_markdown_with_code(base_info)}</body></html>"
        self.history_area.setHtml(full_html)
        self.scroll_to_bottom()

    def manual_clear_history(self):
        # 手动清屏
        clear_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        server_status = "✅ 运行中" if (config.image_server_process and config.image_server_process.poll() is None) else "❌ 已停止"
        base_info = f"""
<div class='clear-tip'>📅 手动清屏完成（清屏时间：{clear_time}）</div>
<div class='config-info'>📋 当前配置：端口{config.SERVER_PORT} | 监控目录{os.path.abspath(config.MONITOR_DIR)} | 清屏{config.CLEAR_INTERVAL//60}分钟</div>
<div class='server-status'>🔌 截图接收服务状态：{server_status}</div>
<div class='auto-monitor'>🔍 目录监控正常，等待新截图...</div>
<div class='clear-tip'>🗑️ 下次自动清屏：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
"""
        full_html = f"<html><head>{MARKDOWN_CSS}</head><body>{format_markdown_with_code(base_info)}</body></html>"
        self.history_area.setHtml(full_html)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        # 滚动到对话底部
        cursor = self.history_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.history_area.setTextCursor(cursor)
        self.history_area.ensureCursorVisible()

    def start_monitoring(self):
        # 启动目录监控线程（调用monitor_handler模块）
        self.monitor_thread = MonitorThread()
        self.monitor_thread.new_image_signal.connect(self.handle_new_image)
        self.monitor_thread.start()
        self.append_markdown(f"<div class='auto-monitor'>🔍 已启动监控：{os.path.abspath(config.MONITOR_DIR)}</div>")
        self.append_markdown(f"<div class='auto-monitor'>📌 上轮分析完成后，将等待{WAIT_SECONDS_AFTER_ANALYSIS}秒再处理新截图</div>\n")

    def handle_new_image(self, image_path):
        # 处理新截图（自动分析）
        if self.is_ai_busy:
            self.pending_image = image_path
            self.append_markdown(f"<div class='auto-monitor'>📥 发现新截图（{os.path.basename(image_path)}），等待上轮分析完成...</div>")
        elif self.remaining_wait > 0:
            self.pending_image = image_path
            self.append_markdown(f"<div class='auto-monitor'>📥 发现新截图（{os.path.basename(image_path)}），等待{self.remaining_wait}秒后处理...</div>")
        else:
            self.auto_send_new_image(image_path)

    def auto_send_new_image(self, image_path):
        # 自动发送截图到AI分析
        self.is_ai_busy = True
        self.skip_wait_btn.setEnabled(False)
        self.append_markdown(f"<div class='auto-monitor'>📥 开始处理新截图：{os.path.basename(image_path)}</div>")
        
        # 图片转Base64
        self.base64_image = self.image_to_base64(image_path)
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(
            self.image_label.width(), self.image_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        
        # 调用AI分析（调用ai_handler模块）
        question = self.question_edit.toPlainText().strip() or "请分析这张截图的内容。"
        self.append_markdown(f"<div class='user-tag'>👤 自动提问：</div>{question}\n")
        self.append_markdown(f"<div class='status'>🤖 AI：正在分析新截图...</div>\n")
        
        self.ai_thread = ApiThread(self.base64_image, question)
        self.ai_thread.result_signal.connect(self.show_ai_result)
        self.ai_thread.start()

    def show_ai_result(self, reasoning, answer):
        # 显示AI分析结果
        self.is_ai_busy = False
        self.append_markdown(f"<div class='reasoning-tag'>📝 AI推理：</div>{reasoning}\n")
        formatted_answer = format_markdown_with_code(answer)
        self.append_markdown(f"<div class='ai-tag'>💡 AI回答：</div>{formatted_answer}\n")
        
        # 启动冷却等待
        self.remaining_wait = WAIT_SECONDS_AFTER_ANALYSIS
        self.append_markdown(f"<div class='wait-tip'>⌛ 上轮分析完成，{self.remaining_wait}秒后可处理新截图（可点击「跳过等待」立即处理）</div>\n")
        self.wait_timer.start()
        self.skip_wait_btn.setEnabled(True)
        
        # 处理等待中的截图
        if self.pending_image:
            self.append_markdown(f"<div class='auto-monitor'>⏳ 等待期间有暂存截图，将在{self.remaining_wait}秒后自动处理</div>")

    def update_wait_time(self):
        # 更新冷却倒计时
        self.remaining_wait -= 1
        current_html = self.history_area.toHtml()
        wait_pattern = r"<div class='wait-tip'>⌛ 上轮分析完成，\d+秒后可处理新截图（可点击「跳过等待」立即处理）</div>"
        new_wait_tip = f"<div class='wait-tip'>⌛ 上轮分析完成，{self.remaining_wait}秒后可处理新截图（可点击「跳过等待」立即处理）</div>"
        import re
        current_html = re.sub(wait_pattern, new_wait_tip, current_html)
        self.history_area.setHtml(current_html)
        self.scroll_to_bottom()
        
        if self.remaining_wait <= 0:
            self.wait_timer.stop()
            self.skip_wait_btn.setEnabled(False)
            self.append_markdown(f"<div class='wait-tip'>✅ 等待结束，可正常处理新截图</div>\n")
            if self.pending_image:
                self.append_markdown(f"<div class='auto-monitor'>📤 开始处理等待中的截图：{os.path.basename(self.pending_image)}</div>")
                self.auto_send_new_image(self.pending_image)
                self.pending_image = None

    def skip_wait(self):
        # 跳过冷却等待
        self.wait_timer.stop()
        self.remaining_wait = 0
        self.skip_wait_btn.setEnabled(False)
        self.append_markdown(f"<div class='wait-tip'>🚀 已跳过等待，可立即处理新截图</div>")
        if self.pending_image:
            self.append_markdown(f"<div class='auto-monitor'>📤 立即处理等待中的截图：{os.path.basename(self.pending_image)}</div>")
            self.auto_send_new_image(self.pending_image)
            self.pending_image = None

    def select_image(self):
        # 手动选择本地图片
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.base64_image = self.image_to_base64(file_path)
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(
                self.image_label.width(), self.image_label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.append_markdown(f"<div class='image-selected'>✅ 已选择图片：{os.path.basename(file_path)}</div>\n")
            self.send_btn.setEnabled(True)

    def image_to_base64(self, image_path):
        # 图片转Base64（工具函数）
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def send_question(self):
        # 手动发送AI请求
        if self.is_ai_busy:
            self.append_markdown(f"<div class='status'>⚠️ AI正在分析其他截图，请稍后再手动发送</div>\n")
            return
        question = self.question_edit.toPlainText().strip()
        if not question or not self.base64_image:
            return
        self.is_ai_busy = True
        self.append_markdown(f"<div class='user-tag'>👤 你：</div>{question}\n")
        self.append_markdown(f"<div class='status'>🤖 AI：正在分析...</div>\n")
        
        self.ai_thread = ApiThread(self.base64_image, question)
        self.ai_thread.result_signal.connect(self.show_ai_result)
        self.ai_thread.start()

    def append_markdown(self, md_text):
        # 渲染Markdown并添加到对话区（调用ai_handler模块）
        processed_md = format_markdown_with_code(md_text)
        html = format_markdown_with_code(processed_md)  # 复用Markdown处理函数
        current_html = self.history_area.toHtml()
        
        if "body></html>" in current_html:
            new_html = current_html.replace("</body></html>", f"{html}</body></html>")
        else:
            new_html = f"<html><head>{MARKDOWN_CSS}</head><body>{html}</body></html>"
        
        self.history_area.setHtml(new_html)
        self.scroll_to_bottom()

    def closeEvent(self, event):
        # 关闭窗口时清理资源
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.monitor_thread.requestInterruption()
            self.monitor_thread.wait()
        # 终止后台截图接收服务
        if config.image_server_process and config.image_server_process.poll() is None:
            config.image_server_process.terminate()
            print("[服务整合] 已停止后台截图接收服务")
        self.wait_timer.stop()
        self.clear_timer.stop()
        event.accept()