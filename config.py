# config.py：全局配置与默认参数
import os

# -------------------------- 默认配置参数 --------------------------
DEFAULT_API_KEY = "cbb4f72b-7880-4e53-995c-3ae71df8c313"
DEFAULT_SERVER_PORT = 7893  # 客户端/服务端通信端口
DEFAULT_MONITOR_DIR = "received_screenshots"  # 截图保存/监控目录
DEFAULT_CLEAR_INTERVAL = 180  # 自动清屏间隔（秒，默认3分钟）
WAIT_SECONDS_AFTER_ANALYSIS = 30  # AI分析后等待间隔（秒）
# -------------------------- Markdown样式（全局共用） --------------------------
MARKDOWN_CSS = """
<style>
    body { font-family: SimHei, Microsoft YaHei, sans-serif; font-size: 14px; line-height: 1.7; color: #333; margin: 5px; }
    h1, h2, h3 { color: #2c3e50; margin: 15px 0 8px 0; border-bottom: 1px solid #eee; padding-bottom: 3px; }
    h1 { font-size: 18px; } h2 { font-size: 16px; } h3 { font-size: 15px; border-bottom: none; }
    ul, ol { margin: 8px 0 8px 20px; padding-left: 10px; } li { margin: 5px 0; }
    .user-tag { color: #2980b9; font-weight: bold; }
    .ai-tag { color: #27ae60; font-weight: bold; }
    .reasoning-tag { color: #7f8c8d; font-weight: bold; }
    .status { color: #95a5a6; font-style: italic; margin: 5px 0; }
    .code-block { background-color: #2d2d2d; color: #f8f8f2; font-family: Consolas, Monaco, "Courier New", monospace; font-size: 12px; border: 1px solid #666; border-radius: 4px; padding: 12px; margin: 10px 0; overflow-x: auto; }
    .code-language { color: #f1c40f; font-size: 11px; margin: 0 0 5px 0; font-weight: bold; }
    .image-selected { color: #e67e22; font-weight: bold; }
    .auto-monitor { color: #e74c3c; font-weight: bold; }
    .wait-tip { color: #f39c12; font-weight: bold; }
    .clear-tip { color: #9b59b6; font-weight: bold; } 
    .config-info { color: #3498db; font-weight: bold; } 
    .server-status { color: #2ecc71; font-weight: bold; }
</style>
"""

# -------------------------- 全局变量（跨模块共用） --------------------------
# 初始化时赋值，后续被主程序修改
client = None  # OpenAI客户端实例
SERVER_PORT = DEFAULT_SERVER_PORT
MONITOR_DIR = DEFAULT_MONITOR_DIR
CLEAR_INTERVAL = DEFAULT_CLEAR_INTERVAL
image_server_process = None  # 后台截图接收服务进程