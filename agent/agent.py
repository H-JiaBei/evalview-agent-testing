"""EvalView 练习用 Mock Agent —— 计算器 Agent。

提供一个 calculator 工具（加/减/乘/除），通过 HTTP /execute 接口
接收 query，返回 output 与 tool_calls 轨迹，供 EvalView 做快照回归测试。

运行：python agent.py（监听 127.0.0.1:8002）
"""

import re
import time
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Calculator Mock Agent")


class Message(BaseModel):
    role: str
    content: str


class ExecuteRequest(BaseModel):
    query: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    messages: Optional[List[Message]] = None
    enable_tracing: bool = True


class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]
    result: Any
    latency: float = 0.0
    cost: float = 0.0


class ExecuteResponse(BaseModel):
    output: str
    tool_calls: List[ToolCall]
    cost: float = 0.0
    latency: float = 0.0
    tokens: Optional[Dict[str, int]] = None


def _calc(operation: str, a: float, b: float) -> float:
    if operation == "add":
        return a + b
    if operation == "subtract":
        return a - b
    if operation == "multiply":
        return a * b
    if operation == "divide":
        return a / b if b != 0 else 0.0
    return 0.0


def run_agent(query: str):
    """极简的「规则式 agent」：识别运算词，调用 calculator 工具。"""
    q = query.lower()
    numbers = re.findall(r"-?\d+(?:\.\d+)?", query)
    tool_calls: List[ToolCall] = []
    cost = 0.0

    op_map = [
        ("add", ["plus", "add", "+", "sum"], "+"),
        ("subtract", ["minus", "subtract", "-"], "-"),
        ("multiply", ["times", "multiply", "*"], "*"),
        ("divide", ["divided", "divide", "/"], "/"),
    ]
    for op, keywords, symbol in op_map:
        if any(k in q for k in keywords):
            if len(numbers) >= 2:
                a, b = float(numbers[0]), float(numbers[1])
                result = _calc(op, a, b)
                tool_calls.append(ToolCall(
                    name="calculator",
                    arguments={"operation": op, "a": a, "b": b},
                    result=result,
                    cost=0.001,
                ))
                return f"The result of {a} {symbol} {b} = {result}", tool_calls, 0.001
            break

    return f"I didn't understand: {query}", tool_calls, 0.0


@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    start = time.time()
    if request.query:
        query = request.query
    elif request.messages:
        user_msgs = [m for m in request.messages if m.role == "user"]
        if not user_msgs:
            raise HTTPException(status_code=400, detail="No user message")
        query = user_msgs[-1].content
    else:
        raise HTTPException(status_code=400, detail="Either query or messages must be provided")

    output, tools, cost = run_agent(query)
    latency_ms = (time.time() - start) * 1000
    if tools:
        per_step = latency_ms / len(tools)
        tools = [ToolCall(name=t.name, arguments=t.arguments, result=t.result, latency=per_step, cost=t.cost) for t in tools]
    tokens = {"input": len(query), "output": len(output)}
    return ExecuteResponse(output=output, tool_calls=tools, cost=cost, latency=latency_ms, tokens=tokens)


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    print("Calculator Mock Agent running on http://127.0.0.1:8002")
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="warning")
