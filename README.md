# Video2Text

把本地音频和视频可靠地变成可搜索、可编辑、可继续交给 AI 使用的文本。

Video2Text 当前提供一个轻量 Python CLI：用 FFmpeg 读取常见媒体格式，分段后通过
SpeechRecognition 的 Google Web Speech 后端识别，最后按原顺序合并为 UTF-8 文本。

> 项目正在恢复维护。当前后端适合体验和短音频，不承诺离线、隐私或服务稳定性；
> 本地 Whisper 后端是下一阶段最高优先级，详见 [ROADMAP.md](ROADMAP.md)。

## 为什么做这个项目

很多课程、访谈、会议录音和存量视频里的信息无法被搜索，也很难进入总结、翻译、
知识库和智能问答流程。Video2Text 不追求做一个庞大的音视频平台，而是解决最靠前、
最通用的一步：用尽可能低的安装和使用成本，得到可信、开放格式的转写结果。

## 使命、愿景与价值观

**使命**：让个人和小团队用普通电脑，把音视频内容低成本地转成可复用知识。

**愿景**：成为一个小而可靠的本地优先转写入口——输入一个文件，得到文本、字幕和
结构化时间轴，并能自然接入现代 AI 工作流。

**价值观**：

- 直切痛点：先把“输入媒体 → 得到可靠文本”做好，再考虑 UI 和平台化。
- 本地优先：能在用户设备完成的工作尽量不上传；必须联网时明确说明数据去向。
- 开放可迁移：优先 TXT、SRT、JSON 等通用格式，不锁定模型或云厂商。
- 小而可验证：每个非平凡改动都带一个能失败的测试，拒绝只增加框架的工程化。
- 诚实兼容：明确支持范围、外部依赖和已知限制，不把偶然可运行当成正式支持。

## 快速开始

### 1. 准备环境

- Python 3.10–3.13
- [FFmpeg](https://ffmpeg.org/download.html)，并确保 `ffmpeg -version` 可执行

Windows 可使用 `winget install Gyan.FFmpeg`，macOS 可使用 `brew install ffmpeg`，
Debian/Ubuntu 可使用 `sudo apt install ffmpeg`。

### 2. 安装并运行

```bash
git clone https://github.com/tangly1024/Video2Text.git
cd Video2Text
python -m venv .venv
```

激活虚拟环境后：

```bash
python -m pip install -r requirements.txt
video2text path/to/demo.mp4
```

结果默认写入 `output/demo/demo.txt`。也可以直接运行：

```bash
python main.py path/to/demo.mp4 -o my-output --language zh-CN
```

常用参数：

```text
-o, --output DIR          输出根目录，默认 output
--language CODE           识别语言，默认 zh-CN
--segment-length SECONDS  分段时长，默认 30
--workers N               最大并发数，默认 5
```

Python 调用方式：

```python
from video_converter import convert_to_text

result = convert_to_text("demo.mp4", output_path="output", language="zh-CN")
print(result)
```

## 当前能力与边界

| 项目 | 当前状态 |
| --- | --- |
| 输入格式 | WAV、MP3、M4A、MP4、FLV（非 WAV 格式依赖 FFmpeg） |
| 输出格式 | UTF-8 TXT |
| 默认识别 | Google Web Speech，经网络发送音频片段，无 SLA |
| 断点续跑 | 已成功生成的片段会复用 |
| 失败处理 | 跳过失败片段并保留其余结果；全部失败时返回错误 |
| 目标兼容 | Python 3.10–3.13；Windows、macOS、Linux 由 CI 验证基础流程 |

当前不适合敏感音频、严格离线场景或无人值守的大批量任务。文本准确率取决于语言、
噪声、说话人和外部识别服务。请确认你有权处理输入媒体，并遵守所在地法律及服务条款。

## 开发与测试

```bash
python -m pip install -r requirements.txt
python -m compileall -q main.py video_converter tests
python -m unittest discover -s tests -v
```

CI 使用同一组命令覆盖 Python 3.10/3.13，以及 Windows、macOS、Linux。代码约定和
提交要求见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 路线图

项目接下来只押注一个核心方向：**本地优先、带时间戳的可靠转写**。近期重点是接入
单一 Whisper 本地后端、输出 SRT/JSON、长任务可恢复；摘要、翻译和知识库接入建立在
稳定转写之上。完整取舍、验收标准和 issue 划分见 [ROADMAP.md](ROADMAP.md)。

## 参与维护

欢迎提交真实样例、兼容性反馈和小而完整的修复。开始编码前请先搜索已有 issue；新增
后端或依赖时，请说明它解决的真实问题、安装成本、隐私边界和最小测试。

本项目采用 [MIT License](LICENSE)，欢迎在保留版权和许可声明的前提下使用、修改与分发。
