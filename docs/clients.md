# Video2Text 客户端入口

这些入口共用同一个转写核心，不维护多套产品逻辑。

## Python 本地 UI

```bash
python -m video_converter.web_ui
```

默认打开 `http://127.0.0.1:8765/`。这个方式适合 Windows、Linux、macOS，也是打包桌面 exe 的最低成本入口。

```bash
python -m pip install pyinstaller
pyinstaller --onefile --name video2text-ui --add-data "clients/web-ui.html;clients" desktop_ui.py
```

Linux/macOS 的 `--add-data` 分隔符是冒号：

```bash
pyinstaller --onefile --name video2text-ui --add-data "clients/web-ui.html:clients" desktop_ui.py
```

## Node 本地服务

```bash
node clients/node-server.js
```

默认打开 `http://127.0.0.1:8766/`，不需要安装 npm 包。它上传文件后调用仓库里的 Python CLI，所以仍然需要 Python 依赖和 FFmpeg。

如果 `python` 不在 PATH，可显式指定：

```bash
VIDEO2TEXT_PYTHON=/path/to/python node clients/node-server.js
```

## 本地 HTML

直接打开：

```text
clients/web-ui.html
```

浏览器本地文件模式不能直接调用 Python，只能预览参数和等价命令。要真正执行转写，请用 Python UI 或 Node 服务打开页面。

## Linux / macOS

优先使用 Python 本地 UI：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m video_converter.web_ui
```

## iOS / iPadOS

iOS 不能直接运行本项目的 Python 转写流程。最低成本方式是在同一局域网内的电脑上启动服务：

```bash
python -m video_converter.web_ui --host 0.0.0.0
```

然后用 iPhone 或 iPad 浏览器访问电脑局域网地址，例如 `http://192.168.1.10:8765/`。

## 选择建议

| 入口 | 适合场景 | 代价 |
| --- | --- | --- |
| Python UI | 本机快速可视化使用 | 无新增依赖 |
| Desktop exe | Windows 双击启动 | 只增加打包步骤 |
| Node 服务 | 已有 Node 环境的本地网页入口 | 无 npm 依赖 |
| 本地 HTML | 展示参数和命令 | 不能直接转写 |
| iOS 浏览器 | 手机查看和上传 | 需要电脑做服务端 |
