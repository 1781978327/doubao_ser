# main.py：程序入口（整合所有模块）
import sys
from PyQt5.QtWidgets import QApplication
import config  # 导入全局配置
from ui_components import InitConfigDialog, ImageChatMainWindow
from ai_handler import init_ai_client
from monitor_handler import start_image_server_in_background


def check_dependency():
    """检查必要依赖库是否安装"""
    required_libs = ["markdown", "watchdog", "PyQt5", "openai", "pybase64"]
    missing_libs = []
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            missing_libs.append(lib)
    if missing_libs:
        print(f"❌ 请先安装缺失的依赖库：")
        print(f"pip install {' '.join(missing_libs)}")
        return False
    return True


if __name__ == "__main__":
    # 1. 检查依赖库
    if not check_dependency():
        sys.exit(1)
    
    # 2. 初始化Qt应用
    app = QApplication(sys.argv)
    
    # 3. 显示配置窗口，获取用户配置
    init_dialog = InitConfigDialog()
    if init_dialog.exec_() != InitConfigDialog.Accepted:
        # 用户取消配置，退出程序
        sys.exit(0)
    
    # 4. 初始化AI客户端（使用配置的API Key）
    init_ai_client(config.api_key)
    
    # 5. 后台启动截图接收服务
    if not start_image_server_in_background():
        sys.exit(1)
    
    # 6. 启动主窗口
    main_window = ImageChatMainWindow()
    main_window.show()
    
    # 7. 运行应用
    sys.exit(app.exec_())