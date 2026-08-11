# Contributing

感谢你帮助 Video2Text 恢复维护。优先提交能让真实用户更快得到可靠转写结果的小改动。

## 开始前

1. 搜索现有 issue 和 PR，确认问题尚未解决。
2. Bug 请提供系统、Python/FFmpeg 版本、最小输入特征、命令和完整错误信息。
3. 大功能先开 issue，说明用户痛点、最小范围、依赖成本和验收方式。

## 本地闭环

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m compileall -q main.py video_converter tests
python -m unittest discover -s tests -v
```

提交前还应手动运行 `video2text --help`。修改媒体解码或识别后端时，请至少补一个不会
访问外网的回归测试；需要在线服务或大型模型的测试必须显式标注并与默认 CI 隔离。

## 代码约定

- 支持 Python 3.10–3.13，文本文件统一 UTF-8、LF。
- 遵循 PEP 8；公共函数提供类型标注和简短 docstring。
- 优先标准库和已有依赖，不为单一调用添加抽象层。
- 不吞异常；面向用户的失败应有可理解消息和非零退出码。
- 文件、网络、模型等边界必须验证输入；密钥不得写入代码、日志或测试 fixture。
- 一个 PR 解决一个问题，并包含能在修复前失败、修复后通过的最小测试。

## PR 说明

请写清楚：问题、最小方案、验证命令、兼容性/隐私影响，以及未覆盖的边界。维护者会
优先审查小而完整、可复现、无需猜测结果的 PR。
