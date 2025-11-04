# 截图分析服务端（PyQt5 + ARK）

一个用于考试/运维等场景的截图接收与智能分析服务端，集成 PyQt5 图形界面与火山方舟 ARK 多模态模型（如 Doubao、DeepSeek 系列），支持自动接收客户端截图、自动/手动分析、模型一键切换、目录监控与自动清屏等功能。

- 项目仓库：`https://github.com/1781978327/doubao_ser`

## 功能特性
- 自动接收客户端发送的截图并保存
- 目录实时监控，发现新截图自动触发分析
- 支持手动选择本地图片进行分析
- 支持模型切换（可编辑下拉；内置 Doubao/DeepSeek 多个 Model ID）
- 自动/手动清屏，且可动态开关“自动清屏”
- 完整 Markdown 渲染（粗体、列表、表格、围栏代码等）
- UI 保持置顶显示，状态提示友好

## 目录结构
```
服务器端/
├── ai_handler.py           # AI 接口调用与 Markdown 处理工具
├── config.py               # 全局配置与默认参数（模型、端口、目录、清屏间隔）
├── image_server.py         # 独立截图接收 TCP 服务
├── main.py                 # 程序入口，整合各模块并启动 UI
├── monitor_handler.py      # 目录监控与 image_server 后台进程启动
├── ui_components.py        # UI 主窗口与交互逻辑
├── received_screenshots/   # 已接收截图保存目录
└── README.md               # 项目说明
```

## 环境要求
- Python 3.8+
- Windows（已在 Windows 10/11 验证）

建议先安装如下依赖（若首次运行 `main.py` 会自动检查并提示缺失包）：
```bash
pip install pyqt5 openai watchdog markdown pybase64
```

或使用 `requirements.txt`（若仓库根目录存在）：
```bash
pip install -r requirements.txt
```

## 快速开始
1) 启动服务端：
```bash
python main.py
```
2) 弹出的“初始化配置”窗口中：
- ARK API Key：可直接填写；若留空将使用 `config.py` 中的默认值
- 服务端端口：默认 `7893`（需与客户端一致）
- 监控目录：默认 `received_screenshots`
- 清屏间隔：默认 `180` 秒（UI 中可开启/关闭自动清屏）

3) 进入主界面后：
- 左侧可手动选择图片
- 中部为对话/状态显示，支持 Markdown 渲染
- 顶部输入框为问题文本（自动/手动发送共用）
- “模型”下拉可编辑，支持即时切换到任意 Model ID
- “开启/关闭自动清屏”可动态控制定时清屏

## 模型切换
- `config.py` 中：
  - `DEFAULT_MODEL`：默认模型
  - `MODEL`：当前生效模型
- 界面中“模型”下拉为可编辑组件，内置示例：
  - doubao-seed-1-6-lite-251015
  - doubao-seed-1-6-vision-250815
  - doubao-seed-1-6-250615
  - doubao-seed-1-6-251015
  - doubao-seed-1-6-flash-250828
  - doubao-seed-1-6-thinking-250715
  - deepseek-v3-1-terminus
  - deepseek-v3-1-250821
- 你也可以直接输入任意自定义的 Model ID，选择后立刻生效。

## API Key 配置
- 程序默认从初始化窗口读取 API Key 并写入 `config.api_key`，供 `ai_handler.py` 初始化客户端使用。
- 如需从环境变量读取，可自行扩展读取 `ARK_API_KEY` 的逻辑；或在弹框中手动粘贴。

## 截图接收服务
- `image_server.py` 为独立的 TCP 服务，`monitor_handler.py` 会在后台启动它，并将标准输出/错误重定向以避免长时间运行时的阻塞。
- 服务默认监听 `config.SERVER_PORT`，保存目录为 `config.MONITOR_DIR`。

## 自动清屏
- 可在主界面随时“开启/关闭自动清屏”。
- 间隔为 `config.CLEAR_INTERVAL`（秒）。
- 清屏时会保留配置状态说明与服务状态信息。

## 常见问题
- 无法接收图片/长时间后停止：
  - 项目已将后台子进程输出重定向至 `DEVNULL`，避免缓冲阻塞。
  - 若端口被占用，请在初始化窗口更换端口。
- Markdown 显示为原始 `**加粗**` 文本：
  - 已改为使用 `markdown` 库完整渲染，确保粗体/列表/表格/代码块正常显示。
- AI 并发：
  - 当前串行处理：AI 忙时会暂存下一张，完成后立即处理，无固定冷却等待。

## 开发与调试
- 运行：`python main.py`
- 关键入口：
  - `ui_components.py`：UI 与交互逻辑
  - `ai_handler.py`：AI 调用线程 `ApiThread`，使用 `config.client`
  - `monitor_handler.py`：目录监控、后台进程管理
  - `image_server.py`：TCP 协议接收并写文件

## 打包发布（可选）
推荐使用 `pyinstaller`（如已有 spec 文件可直接使用）：
```bash
pyinstaller 截图分析服务端.spec
```
或最简命令：
```bash
pyinstaller -F -w main.py --name 截图分析服务端
```

## 许可证
- 个人/内部使用自由。若用于商业分发，请遵循所依赖三方库及模型服务条款。

---
如需功能扩展（例如：日志文件输出、批量任务队列、多模型并行评测、快捷键操作等），欢迎提需求或提交 PR。
