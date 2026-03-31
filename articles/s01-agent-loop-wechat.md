# 30行代码实现一个AI编程助手：揭秘Claude Code的核心循环

> "一个工具 + 一个循环 = 一个 Agent"——这是所有AI Agent的起点。

---

## 引言

当我们使用 Claude Code、Cursor 等 AI 编程助手时，你是否好奇过它们是如何工作的？它们如何读懂你的代码、执行命令、修改文件？

答案出奇简单：**一个循环**。

今天，让我们从零开始，用不到 30 行核心代码，揭开 AI Agent 的神秘面纱。

---

## 问题：模型被困在"盒子"里

语言模型（LLM）能推理代码，但它碰不到真实世界：

- ❌ 不能读文件
- ❌ 不能跑测试
- ❌ 不能看报错

没有 Agent 循环时，每次工具调用你都得手动把结果"喂"回去。**你自己就是那个循环。**

---

## 解决方案：让模型自己"动手"

核心思路极其简洁：

```
+----------+      +-------+      +---------+
|   User   | ---> |  LLM  | ---> |  Tool   |
|  prompt  |      |       |      | execute |
+----------+      +---+---+      +----+----+
                      ^               |
                      |   tool_result |
                      +---------------+
                      (循环继续，直到模型决定停止)
```

**一个退出条件控制整个流程。循环持续运行，直到模型不再调用工具。**

---

## 核心代码：不到30行的Agent

```python
def agent_loop(query):
    messages = [{"role": "user", "content": query}]

    while True:
        # 1. 调用LLM
        response = client.messages.create(
            model=MODEL, system=SYSTEM, messages=messages,
            tools=TOOLS, max_tokens=8000,
        )

        # 2. 记录助手回复
        messages.append({"role": "assistant", "content": response.content})

        # 3. 检查退出条件：模型没有调用工具
        if response.stop_reason != "tool_use":
            return

        # 4. 执行工具调用，收集结果
        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = run_bash(block.input["command"])
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })

        # 5. 将工具结果作为用户消息追加，回到第1步
        messages.append({"role": "user", "content": results})
```

就是这样！这就是整个 Agent 的核心。

---

## 逐步拆解：五个步骤

### 第一步：用户输入作为第一条消息

```python
messages = [{"role": "user", "content": query}]
```

消息列表从这里开始累积。

---

### 第二步：将消息和工具定义一起发给LLM

```python
response = client.messages.create(
    model=MODEL, system=SYSTEM, messages=messages,
    tools=TOOLS, max_tokens=8000,
)
```

`tools` 参数告诉模型："你可以调用这些工具"。

---

### 第三步：追加助手响应，检查退出条件

```python
messages.append({"role": "assistant", "content": response.content})

if response.stop_reason != "tool_use":
    return
```

关键点：**模型自己决定何时停止**。

当 `stop_reason` 不是 `"tool_use"` 时，说明模型认为任务完成，不再需要调用工具。

---

### 第四步：执行每个工具调用

```python
results = []
for block in response.content:
    if block.type == "tool_use":
        output = run_bash(block.input["command"])
        results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": output,
        })
```

这里我们只提供了一个 `bash` 工具，但原理是通用的。

---

### 第五步：工具结果追加到消息列表，循环回到第一步

```python
messages.append({"role": "user", "content": results})
```

**这就是神奇之处**：工具执行结果作为"用户消息"发回给模型，模型基于这些新信息继续推理。

---

## 完整工具定义：只有一个bash

```python
TOOLS = [{
    "name": "bash",
    "description": "Run a shell command.",
    "input_schema": {
        "type": "object",
        "properties": {"command": {"type": "string"}},
        "required": ["command"],
    },
}]

def run_bash(command: str) -> str:
    # 安全检查
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"

    # 执行命令
    r = subprocess.run(command, shell=True, cwd=os.getcwd(),
                       capture_output=True, text=True, timeout=120)
    return (r.stdout + r.stderr).strip()[:50000]
```

一个工具 + 一个循环 = 一个 Agent。

---

## 动手试试

```bash
cd learn-claude-code
python agents/s01_agent_loop.py
```

试试这些 prompt：

```
1. Create a file called hello.py that prints "Hello, World!"
2. List all Python files in this directory
3. What is the current git branch?
4. Create a directory called test_output and write 3 files in it
```

---

## 为什么这很重要？

这个简单的循环是所有现代 AI Agent 的基础：

| Agent 产品 | 核心机制 |
|-----------|---------|
| Claude Code | 工具循环 + 文件操作/命令执行 |
| Cursor Agent | 工具循环 + 代码编辑/终端 |
| Devin | 工具循环 + 浏览器/终端/编辑器 |
| AutoGPT | 工具循环 + 自主目标规划 |

**后面所有的"智能"——记忆管理、任务分解、多Agent协作——都是在这个循环之上叠加的机制。循环本身始终不变。**

---

## 小结

```
while stop_reason == "tool_use":
    response = LLM(messages, tools)
    execute tools
    append results
```

这四行伪代码，道尽了 AI Agent 的本质。

下次当你使用 Claude Code 让它帮你写代码时，你知道发生了什么：

1. 你说："帮我重构这个函数"
2. 模型调用工具读取文件
3. 模型看到文件内容，决定如何修改
4. 模型调用工具写入新代码
5. 模型说："完成了"（stop_reason != "tool_use"）

循环结束，任务完成。

---

**这个系列的后续章节会在这个循环上叠加更多机制：子代理、任务系统、后台任务、Agent团队协作……但核心循环始终是那个循环。**

> 代码来源：[learn-claude-code](https://github.com/anthropics/learn-claude-code) - Anthropic 官方开源的 Claude Code 学习项目

---

*如果这篇文章对你有帮助，欢迎点赞、在看、转发三连～*