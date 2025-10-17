@echo off
echo 开始打包截图分析服务端...
pyinstaller -F --noconsole --name "截图分析服务端" ^
  --hidden-import "watchdog.observers" ^
  --hidden-import "watchdog.events" ^
  --hidden-import "PyQt5.QtWidgets" ^
  --hidden-import "PyQt5.QtCore" ^
  --hidden-import "PyQt5.QtGui" ^
  --hidden-import "openai" ^
  main.py
echo 打包完成！可执行文件在 dist 目录下
echo 注意：需将 image_server.py 复制到 dist 目录与 exe 同目录
pause