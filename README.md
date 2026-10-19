# EvalView 实践 —— AI Agent 快照回归测试

基于开源框架 [EvalView](https://github.com/hidai25/eval-view)（Apache-2.0），自建一个 mock agent，完整跑通「快照回归测试」流程：**录基线 → 改动 → 检测漂移**。

## 这个项目做什么

- 用 FastAPI 自建一个 mock agent（计算器，带 tool-call 轨迹）
- 用 EvalView 的 `snapshot` / `check` 做快照回归测试
- **实测演示**：故意给 agent 引入「除法 → 乘法」bug，EvalView 成功检测出 REGRESSION

## 项目亮点

- **零 API key 离线跑**：`--no-judge` 跳过 LLM 评分，确定性 diff 离线完成
- **真实回归检测**：工具名、参数没变，但输出悄悄漂移，也能抓出来
- **快照工作流**：`snapshot`（录基线）→ `check`（比对）→ 改动 → `check`（报警）

## 项目结构

```
evalview/
├── agent/
│   ├── agent.py            # mock agent（FastAPI，/execute 接口）
│   └── requirements.txt    # fastapi + uvicorn
├── tests/
│   └── test-cases/         # YAML 测试用例
│       ├── calculator-addition.yaml
│       ├── calculator-subtraction.yaml
│       └── calculator-division.yaml
├── .evalview/
│   ├── config.yaml         # adapter: http + endpoint
│   └── golden/             # 快照基线（commit 后团队共享）
├── 部署技术文档.md
└── README.md
```

## 快速开始

```bash
# 1. 安装（国内用清华镜像）
python -m venv .venv
.venv\Scripts\python -m pip install evalview fastapi uvicorn -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 启动 mock agent（监听 127.0.0.1:8002）
.venv\Scripts\python agent/agent.py

# 3. 录基线（Windows 需加 PYTHONUTF8=1）
PYTHONUTF8=1 .venv\Scripts\evalview snapshot --no-judge

# 4. 回归检查
PYTHONUTF8=1 .venv\Scripts\evalview check --no-judge
```

## 核心演示：回归检测

基线录制后，把 `agent/agent.py` 里的除法改成乘法（模拟模型升级引入的 bug）：

```python
if operation == "divide":
    return a * b   # 引入 bug
```

再跑 `evalview check --no-judge`，EvalView 立即报警：

```
✗ REGRESSION: calculator-division  -10.0 pts
    -The result of 100.0 / 4.0 = 25.0    ← 基线
    +The result of 100.0 / 4.0 = 400.0   ← 改坏后
  健康度：100% → 67%
```

## 踩坑记录

见 [部署技术文档.md](部署技术文档.md)，额外两点：

- **YAML 用例含中文时**，Windows 下需 `PYTHONUTF8=1`，否则报 GBK 编码错误
- **配置文件位置**：`config.yaml` 在 `.evalview/` 下，测试用例在 `tests/test-cases/` 下（不是 `tests/` 根目录）

## 许可证

本项目代码采用 [MIT License](LICENSE)，版权归 H-JiaBei 所有；框架 EvalView 为 Apache-2.0。
