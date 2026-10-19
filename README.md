# EvalView 部署与实践 —— AI Agent 快照回归测试

基于开源框架 [EvalView](https://github.com/hidai25/eval-view)（Apache-2.0）的部署与实践：为 AI Agent 做「快照式回归测试」，检测 prompt 修改、模型更换、provider 变更导致的行为漂移。

## 这个项目做什么

- 部署 EvalView（AI Agent 快照回归测试框架）
- 记录 Agent 的「工具调用轨迹」（调用了哪些工具、什么顺序、什么参数）作为基线
- 改动后与基线 diff，输出 `PASSED / TOOLS_CHANGED / REGRESSION`
- 纯 Python，`pip install` 即用；「确定性工具 + 序列 diff」离线跑，无需 API key

## 为什么选这个方向

2026 年「AI 应用测试」是测试领域的明显增量方向，而传统测试岗简历里几乎见不到。EvalView 纯 Python、pip 装完就能跑，改造成本低，是补上这条线的低成本切入点。

## 技术栈

- Python 3.12
- evalview 0.8.1（PyPI 包）
- CLI：`snapshot` / `check` / `replay` / `monitor` 等 20+ 命令

## 快速开始

```bash
# 1. 建 venv（国内直连 PyPI 慢，务必用清华镜像）
python -m venv .venv
.venv\Scripts\python -m pip install evalview -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 验证部署
.venv\Scripts\evalview --version

# 3. 核心用法
.venv\Scripts\evalview init        # 初始化测试项目
.venv\Scripts\evalview snapshot    # 录基线
.venv\Scripts\evalview check       # 改动后比对回归
```

## 踩坑记录

见 [部署技术文档.md](部署技术文档.md)，要点：

- 直连 PyPI 极慢 → 改用清华镜像
- 0.8.1 发布版 `demo` 命令卡住 → OpenAI Assistants API 已于 2026-08-26 关闭（上游已知问题）

## 许可证

本项目（部署文档与脚本）采用 [MIT License](LICENSE)，版权归 H-JiaBei 所有；被测对象 EvalView 为 Apache-2.0，本项目仅安装使用、未复制其源码。
