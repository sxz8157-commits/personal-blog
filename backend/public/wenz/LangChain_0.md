#  LangChain 保姆级学习手册（从0到实战）

# 一、先搞清楚：LangChain 是干嘛的？

👉 一句话：

👉 **LangChain = 帮你用大模型（如 GPT）做“复杂任务”的工具**

------

## 🧩 举个例子（你就懂了）

不用 LangChain：

```python
问 GPT -> 得到回答
```

用 LangChain：

```python
问问题
→ 自动查数据库
→ 自动调用API
→ 自动整理答案
→ 返回结果
```

👉 它帮你把 AI 变成“系统”，不是“聊天机器人”

------

# 二、你需要准备什么（环境）

------

## 🟢 第1步：安装 Python（必须）

检查：

```bash
python --version
```

👉 没有就去装 Python（3.9+）

------

## 🟢 第2步：安装 LangChain

```bash
pip install langchain
```

👉 新版本建议：

```bash
pip install langchain openai
```

------

## 🟢 第3步：配置 API Key（以 OpenAI 为例）

去获取 API Key，然后设置：

Windows：

```bash
setx OPENAI_API_KEY "你的key"
```

------

# 三、你的第一个 LangChain 程序（必须跑）

------

## 🟢 示例1：最简单调用

```python
from langchain.llms import OpenAI

llm = OpenAI()

result = llm.invoke("帮我解释什么是数据库")

print(result)
```

------

## ❗ 如果报错

👉 很可能是版本问题，改用：

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

print(llm.invoke("你好"))
```

------

# 四、核心概念（只学3个就够用）

别贪多，新手只需要这3个：

------

## 1️⃣ Prompt（提示词）

👉 就是你给 AI 的指令

```python
"你是一个老师，解释什么是 MongoDB"
```

------

## 2️⃣ Chain（链）

👉 把多个步骤串起来

------

## 3️⃣ Memory（记忆）

👉 让 AI 记住上下文

------

# 五、真正入门：Prompt 模板（重点）

------

## 🟢 示例：动态提问

```python
from langchain.prompts import PromptTemplate

template = PromptTemplate.from_template(
    "你是老师，请用简单语言解释：{topic}"
)

prompt = template.format(topic="MongoDB")

print(prompt)
```

------

👉 输出：

```text
你是老师，请用简单语言解释：MongoDB
```

------

# 六、Chain（核心能力）

------

## 🟢 示例：组合 Prompt + AI

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

llm = ChatOpenAI()

prompt = PromptTemplate.from_template(
    "请解释：{topic}"
)

chain = prompt | llm

result = chain.invoke({"topic": "LangChain"})

print(result)
```

------

👉 这就是 LangChain 的核心用法

------

# 七、实战1：做一个问答助手

------

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

while True:
    q = input("你问：")
    if q == "exit":
        break

    res = llm.invoke(q)
    print("AI：", res)
```

------

👉 你已经做了一个 AI 聊天程序

------

# 八、实战2：加“记忆”（更真实）

------

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()
memory = ConversationBufferMemory()

conversation = ConversationChain(
    llm=llm,
    memory=memory
)

while True:
    q = input("你：")
    if q == "exit":
        break

    print("AI：", conversation.run(q))
```

------

👉 现在 AI 会“记住你说的话”

------

# 九、LangChain 真正强大的地方（你必须知道）

------

## 🔥 1. 可以接数据库（比如 MongoDB）

👉 AI 自动查数据

------

## 🔥 2. 可以接文件（PDF / TXT）

👉 做知识库问答

------

## 🔥 3. 可以调用工具

👉 比如：

- 查天气
- 调接口
- 执行代码