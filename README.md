## 项目简介

本项目为考试场景下的 AI 辅助截图分析服务端，结合 PyQt5 图形界面、ARK AI 图像识别能力，实现自动接收客户端截图并智能分析，支持自动/手动处理、定时清屏、目录监控等功能。

## 主要功能

- 自动接收客户端发送的截图并保存
- 支持本地图片手动选择分析
- 调用 ARK AI 接口进行图片内容识别与问答
- 自动/手动清屏，定时刷新对话历史
- 目录实时监控，发现新截图自动分析
- 丰富的界面交互与状态提示

## 目录结构

```
服务端/
├── ai_handler.py           # AI接口调用与Markdown处理
├── config.py               # 全局配置与参数
├── image_server.py         # 独立截图接收服务
├── main.py                 # 程序入口，整合所有模块
├── monitor_handler.py      # 目录监控与服务启动
├── README.md               # 项目说明文档
├── requirements.txt        # 依赖库列表
├── ui_components.py        # UI界面组件
├── 截图分析服务端.spec     # 打包配置
├── build/                  # 打包生成文件
├── received_screenshots/   # 接收到的截图保存目录
└── __pycache__/            # Python缓存文件
```

## 环境依赖

- Python 3.7+
- PyQt5
- openai
- watchdog
- markdown
- pybase64

安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. **配置 API Key 和参数**
   - 启动后会弹出配置窗口，可填写 ARK API Key、服务端口、监控目录、清屏间隔等参数。
   - 默认参数可直接使用。

2. **启动服务端**
   - 运行 main.py 即可启动服务端界面和后台截图接收服务。

   ```bash
   python main.py
   ```

3. **客户端发送截图**
   - 客户端需配置与服务端一致的端口，并将截图发送到服务端。
   - 服务端会自动保存并分析收到的截图。

4. **界面操作**
   - 支持手动选择本地图片进行分析
   - 支持手动/自动清屏
   - 实时显示服务状态与分析结果

## 打包说明

如需打包为可执行文件，可使用 `pyinstaller` 并参考 `截图分析服务端.spec` 文件。

```bash
pyinstaller 截图分析服务端.spec
```

## 常见问题

- **未找到 image_server.py**  
  请确保 image_server.py 文件与主程序在同一目录下，打包时也需包含该文件。

- **依赖库缺失**  
  按照 `requirements.txt` 安装所有依赖。

- **端口冲突或权限问题**  
  请确保配置的端口未被占用，且有权限监听。

## 联系方式
若遇到软件运行问题或功能需求，可通过以下方式反馈：
- 开发者：Arlen Liu
- 联系邮箱：liuml2003@163.com
- 版本信息：V1.0（2025-10-17）"# doubao_ser" 
