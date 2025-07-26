# 🌊 流式XML解析器套件

专为**实时流式XML处理**设计的高性能解析器套件，能够处理**不完整、分块到达的XML数据**，实时产生解析事件。

## 💡 为什么需要流式XML解析？

在现代应用中，XML数据往往不是一次性完整到达的：

- **🤖 LLM流式输出**: AI模型逐字符生成XML格式的回复
- **🌐 网络传输**: 大型XML文档通过网络分块传输
- **📡 实时数据流**: WebSocket、SSE等实时数据推送
- **📱 移动应用**: 网络不稳定导致数据分片到达

传统XML解析器需要等待**完整文档**才能开始解析，而流式解析器能够：
- ✅ **边接收边解析** - 无需等待完整数据
- ✅ **实时响应** - 毫秒级延迟产生解析事件
- ✅ **内存高效** - 恒定内存占用，不受数据大小影响
- ✅ **容错性强** - 优雅处理网络中断和数据分割

## 🎯 核心特性

- **🌊 真正的流式处理**: 处理任意分割的XML数据块
- **⚡ 零等待解析**: 数据到达即刻开始解析，无需缓存完整文档
- **🔥 事件驱动架构**: 实时产生 START_TAG、END_TAG、CONTENT 事件
- **📦 任意块大小**: 支持1字节到MB级别的任意输入块
- **🎨 三种解析策略**: 完整解析、外层解析、智能树形解析
- **🛡️ 生产级鲁棒性**: 处理格式错误、网络中断、数据损坏
- **🌍 完整Unicode支持**: 处理多语言和特殊字符
- **📊 零内存泄漏**: 恒定内存占用，适合长时间运行

## 🔧 三种解析器策略

### 1. 📋 完整XML解析器 (`streaming_xml_parser.py`)
**适用场景**: 标准XML结构化数据处理
- 解析所有层级的XML标签
- 产生详细的标签和内容事件
- 适合完整的XML文档处理

### 2. 🎯 外层XML解析器 (`outer_xml_parser.py`)
**适用场景**: LLM输出中的主要结构识别
- 只解析最外层标签，内层XML被当作纯文本内容
- 解决"内容本身包含XML"的问题
- 专为LLM输出设计的简化解析

### 3. 🧠 动态树形解析器 (`dynamic_tree_parser.py`)
**适用场景**: 基于预定义结构的智能解析
- 根据预定义的标签层次结构智能识别真正的标签
- 区分真正的标签和内容中的伪标签
- 支持复杂的上下文感知和鲁棒性处理

## 📊 事件类型

所有解析器都产生统一的事件类型：

- `('START_TAG', tag_name, level)`: 识别到的起始标签
- `('END_TAG', tag_name, level)`: 识别到的结束标签
- `('CONTENT', text_chunk, level)`: 文本内容（可能包含伪标签）

*注：完整解析器和外层解析器的level参数为兼容性保留*

## 🌊 流式解析演示

### 💫 核心概念：真正的流式处理

```python
from streaming_xml_parser import StreamingXMLParser

# 模拟网络数据流 - 数据分块到达
chunks = [
    "<Action><Tool",      # 第1块：不完整的开始标签
    "Name>image_gen</Tool",  # 第2块：跨越多个标签
    "Name><Description>AI图像", # 第3块：标签和内容混合
    "生成</Description></Action>"  # 第4块：结束部分
]

parser = StreamingXMLParser()

print("🌊 流式解析过程：")
for i, chunk in enumerate(chunks):
    print(f"\n📦 接收数据块 {i+1}: {repr(chunk)}")

    # 实时解析每个数据块
    for event_type, data in parser.parse_chunk(chunk):
        print(f"  ⚡ 实时事件: {event_type} -> {repr(data)}")

# 处理剩余数据
for event_type, data in parser.finalize():
    print(f"  🔚 最终事件: {event_type} -> {repr(data)}")
```

**输出效果**：
```
🌊 流式解析过程：

📦 接收数据块 1: '<Action><Tool'
  ⚡ 实时事件: START_TAG -> 'Action'

📦 接收数据块 2: 'Name>image_gen</Tool'
  ⚡ 实时事件: START_TAG -> 'ToolName'
  ⚡ 实时事件: CONTENT -> 'image_gen'

📦 接收数据块 3: 'Name><Description>AI图像'
  ⚡ 实时事件: END_TAG -> 'ToolName'
  ⚡ 实时事件: START_TAG -> 'Description'
  ⚡ 实时事件: CONTENT -> 'AI图像'

📦 接收数据块 4: '生成</Description></Action>'
  ⚡ 实时事件: CONTENT -> '生成'
  ⚡ 实时事件: END_TAG -> 'Description'
  ⚡ 实时事件: END_TAG -> 'Action'
```

### 🚀 三种流式解析策略

#### 1️⃣ 完整XML解析器 - 解析所有标签层级

```python
from streaming_xml_parser import StreamingXMLParser

# 模拟LLM逐字符输出
llm_output = "<Thought><Content>我需要调用工具</Content></Thought>"
parser = StreamingXMLParser()

# 逐字符流式处理
for char in llm_output:
    for event_type, data in parser.parse_chunk(char):
        print(f"{event_type}: {data}")

# 解析所有层级：Thought、Content都被识别为标签
```

#### 2️⃣ 外层XML解析器 - 只解析最外层结构

```python
from outer_xml_parser import OuterXMLParser

# 模拟包含嵌套XML的流式数据
stream_data = "<Response><Data><User>张三</User><Age>25</Age></Data></Response>"
parser = OuterXMLParser()

# 分块处理
for chunk in [stream_data[:20], stream_data[20:40], stream_data[40:]]:
    for event_type, data in parser.parse_chunk(chunk):
        print(f"{event_type}: {data}")

# 只识别Response标签，<Data><User>张三</User><Age>25</Age></Data>作为内容
```

#### 3️⃣ 动态树形解析器 - 智能识别真假标签

```python
from dynamic_tree_parser import DynamicTreeParser

# 定义已知的标签结构
hierarchy = {"Action": ["ToolName"], "Response": ["Message"]}
parser = DynamicTreeParser(hierarchy)

# 模拟复杂的流式XML
complex_stream = "<Action><ToolName>test</ToolName><FakeTag><ToolName>假的</ToolName></FakeTag></Action>"

# 流式处理
for chunk in [complex_stream[:15], complex_stream[15:30], complex_stream[30:]]:
    for event_type, data, level in parser.parse_chunk(chunk):
        print(f"{event_type}: {data} (level {level})")

# 智能区分：只识别正确位置的ToolName，假的被当作内容
```

## LLM输出示例

解析器特别适合处理LLM的结构化输出：

```xml
<UserInput><Content>现在给我画个五彩斑斓的黑</Content></UserInput>

<Start><Reason>UserInput</Reason></Start>

<Thought><Content>用户希望画一个五彩斑斓的黑色，我应该使用通义万相API来生成一张五彩斑斓的黑的图片。</Content></Thought>

<Action><ToolName>image_gen</ToolName></Action>

<End><Reason>ActionInput</Reason></End>
```

## 🎯 实际应用场景

### 🤖 LLM流式输出处理

```python
# 模拟ChatGPT/Claude等LLM的流式回复
def simulate_llm_stream():
    response = "<Thought>我需要生成图片</Thought><Action><ToolName>image_gen</ToolName></Action>"
    for char in response:
        yield char  # 逐字符流式输出

from outer_xml_parser import OuterXMLParser
parser = OuterXMLParser()

print("🤖 LLM流式输出解析：")
for chunk in simulate_llm_stream():
    for event_type, data in parser.parse_chunk(chunk):
        print(f"实时解析: {event_type} -> {data}")
```

### 🌐 网络数据流处理

```python
import asyncio
from streaming_xml_parser import StreamingXMLParser

async def process_network_stream(websocket):
    parser = StreamingXMLParser()

    async for chunk in websocket:  # 网络数据分块到达
        # 实时处理每个数据块
        for event_type, data in parser.parse_chunk(chunk):
            await handle_event(event_type, data)

    # 处理连接结束时的剩余数据
    for event_type, data in parser.finalize():
        await handle_event(event_type, data)
```

### 📱 移动应用实时数据

```python
# 处理不稳定网络环境下的XML数据
class MobileXMLProcessor:
    def __init__(self):
        self.parser = StreamingXMLParser()
        self.buffer = []

    def on_data_received(self, chunk):
        """网络数据到达时调用"""
        print(f"📱 收到数据: {len(chunk)} 字节")

        # 立即解析，无需等待完整数据
        for event_type, data in self.parser.parse_chunk(chunk):
            self.handle_parsed_event(event_type, data)

    def on_connection_lost(self):
        """网络中断时处理剩余数据"""
        for event_type, data in self.parser.finalize():
            self.handle_parsed_event(event_type, data)
```

## 🔥 解析器选择指南

| 应用场景 | 推荐解析器 | 流式特性 | 适用原因 |
|----------|------------|----------|----------|
| **LLM对话系统** | 外层解析器 | ⚡ 逐字符处理 | 只关心主要结构，内容可能包含XML |
| **实时聊天应用** | 外层解析器 | 🌊 消息分片 | 简单快速，适合实时响应 |
| **API网关** | 完整解析器 | 📦 请求分块 | 需要解析完整的XML结构 |
| **配置热更新** | 完整解析器 | 🔄 文件流式读取 | 结构化配置需要完整解析 |
| **智能客服** | 动态树形解析器 | 🧠 意图识别 | 区分真假标签，理解用户意图 |
| **数据采集** | 动态树形解析器 | 📊 流式ETL | 基于预定义结构过滤数据 |
| **WebSocket通信** | 外层解析器 | ⚡ 实时双向 | 低延迟，高吞吐量 |
| **文件上传处理** | 完整解析器 | 📁 分片上传 | 处理大文件的分块传输 |

## 🌊 流式处理核心特性

### ⚡ 零延迟解析
```python
# 传统解析器：需要等待完整数据
traditional_parser.parse(complete_xml_string)  # ❌ 必须等待完整数据

# 流式解析器：数据到达即刻解析
for chunk in data_stream:
    for event in streaming_parser.parse_chunk(chunk):  # ✅ 实时处理
        handle_event_immediately(event)
```

### 📦 任意块大小支持
```python
# 支持任意大小的数据块
test_cases = [
    "a",                    # 1字节
    "<tag>content</tag>",   # 完整标签
    "<ta" + "g>con" + "tent</tag>",  # 标签被分割
    "x" * 1024 * 1024,     # 1MB大块
]

for chunk in test_cases:
    parser.parse_chunk(chunk)  # 都能正确处理
```

### 🔄 状态保持机制
```python
parser = StreamingXMLParser()

# 第1块：不完整的开始标签
parser.parse_chunk("<Action><Tool")  # 解析器记住状态

# 第2块：标签完成
for event in parser.parse_chunk("Name>test</ToolName>"):
    print(event)  # START_TAG: ToolName, CONTENT: test, END_TAG: ToolName

# 解析器自动维护内部状态，无需手动管理
```

### 🛡️ 错误恢复能力
```python
# 即使数据有问题，也能继续处理
chunks = [
    "<Action>",
    "<InvalidTag>",  # 格式错误
    "content",
    "</Action>"      # 仍能正确识别结束
]

for chunk in chunks:
    try:
        for event in parser.parse_chunk(chunk):
            print(f"✅ {event}")
    except Exception as e:
        print(f"❌ 错误: {e}")
        # 解析器仍能继续处理后续数据
```

### 📊 内存效率对比

| 解析方式 | 内存占用 | 延迟 | 适用数据大小 |
|----------|----------|------|--------------|
| **传统解析** | O(n) | 高 | 受内存限制 |
| **流式解析** | O(1) | 极低 | 无限制 |

```python
# 处理1GB的XML数据
# 传统方式：需要1GB内存
traditional_parser.parse(gigabyte_xml)  # 💥 内存爆炸

# 流式方式：只需几KB内存
for chunk in read_file_in_chunks(xml_file, chunk_size=8192):
    for event in streaming_parser.parse_chunk(chunk):  # 🚀 恒定内存
        process_event(event)
```

## 🎮 运行示例

### 🌊 流式处理演示
```bash
# 🔥 核心推荐：流式处理演示套件
python streaming_demo.py    # 完整的流式处理演示
                            # 包含：网络流、LLM逐字符、内存效率、异步处理

# 基础示例
python main.py              # 基本演示
python example.py           # 详细示例

# 各解析器专门演示
python outer_example.py     # 外层解析演示
python dynamic_example.py   # 智能解析演示
```

### 测试套件
```bash
# 单元测试
python test_parser.py           # 完整解析器测试
python test_outer_parser.py     # 外层解析器测试
python test_dynamic_parser.py   # 动态解析器测试

# 复杂性测试
python test_complex_cases.py    # 极端情况和鲁棒性测试
```

### 性能测试
```bash
# 长内容处理测试
python -c "
from dynamic_tree_parser import DynamicTreeParser
import time

hierarchy = {'Action': ['Description']}
parser = DynamicTreeParser(hierarchy)
long_text = '<Action><Description>' + '长内容测试 ' * 10000 + '</Description></Action>'

start_time = time.time()
events = list(parser.parse_chunk(long_text)) + list(parser.finalize())
end_time = time.time()

print(f'处理 {len(long_text)} 字符耗时: {end_time - start_time:.4f} 秒')
print(f'产生 {len(events)} 个事件')
"
```

## 📚 API参考

### 🔧 核心解析器类

#### StreamingXMLParser (完整解析器)
```python
parser = StreamingXMLParser()
parser.parse_chunk(chunk: str) -> Generator[Tuple[str, str], None, None]
parser.finalize() -> Generator[Tuple[str, str], None, None]
parser.reset() -> None
```

#### OuterXMLParser (外层解析器)
```python
parser = OuterXMLParser()
parser.parse_chunk(chunk: str) -> Generator[Tuple[str, str], None, None]
parser.finalize() -> Generator[Tuple[str, str], None, None]
parser.reset() -> None
```

#### DynamicTreeParser (动态树形解析器)
```python
hierarchy = {"Action": ["ToolName", "Description"]}
parser = DynamicTreeParser(hierarchy)
parser.parse_chunk(chunk: str) -> Generator[Tuple[str, str, int], None, None]
parser.finalize() -> Generator[Tuple[str, str, int], None, None]
parser.reset() -> None
parser.get_tag_hierarchy_info() -> str  # 获取层次结构信息
```

### 🎭 事件处理器

#### XMLEventHandler (完整解析器)
```python
class MyHandler(XMLEventHandler):
    def on_start_tag(self, tag_name: str): pass
    def on_end_tag(self, tag_name: str): pass
    def on_content(self, content: str): pass
```

#### OuterXMLEventHandler (外层解析器)
```python
class MyHandler(OuterXMLEventHandler):
    def on_start_tag(self, tag_name: str): pass
    def on_end_tag(self, tag_name: str): pass
    def on_content(self, content: str): pass
```

#### DynamicTreeEventHandler (动态树形解析器)
```python
class MyHandler(DynamicTreeEventHandler):
    def on_start_tag(self, tag_name: str, level: int): pass
    def on_end_tag(self, tag_name: str, level: int): pass
    def on_content(self, content: str, level: int): pass
```

### 🚀 便利函数

```python
# 完整解析器
parse_stream(chunks, event_handler: XMLEventHandler)

# 外层解析器
parse_outer_stream(chunks, event_handler: OuterXMLEventHandler)

# 动态树形解析器
parse_dynamic_stream(chunks, hierarchy: Dict[str, List[str]],
                    event_handler: DynamicTreeEventHandler)
```

## 🏗️ 设计原理

### 📋 完整解析器
**状态机设计**：
- `CONTENT` → `IN_START_TAG` → `IN_END_TAG` → `CONTENT`
- 解析所有遇到的XML标签，构建完整的标签树

### 🎯 外层解析器
**简化状态机**：
- `CONTENT` → `IN_TAG` → `IN_CONTENT` → `CONTENT`
- 只识别最外层标签，通过完整结束标签模式匹配

### 🧠 动态树形解析器
**智能上下文感知**：
- 基于预定义层次结构构建标签树
- 使用`invalid_tag_depth`跟踪无效标签嵌套
- 只有在正确上下文且未被无效标签包围时才识别标签

## ⚡ 性能特性

| 特性 | 完整解析器 | 外层解析器 | 动态树形解析器 |
|------|------------|------------|----------------|
| **内存占用** | 低 | 极低 | 低 |
| **处理速度** | 快 | 极快 | 快 |
| **CPU占用** | 低 | 极低 | 中等 |
| **适用数据量** | 大 | 极大 | 大 |

## 🛡️ 鲁棒性保证

### ✅ 错误处理
- **格式错误XML**: 优雅降级，不会崩溃
- **不匹配标签**: 当作内容处理
- **空标签名**: 安全忽略
- **Unicode字符**: 完美支持

### ✅ 边界情况
- **极长内容**: 流式处理，内存占用恒定
- **深度嵌套**: 支持任意嵌套深度
- **奇怪标签名**: 支持各种命名约定
- **网络分割**: 任意位置分割都能正确处理

## 📝 注意事项

- 🎯 **设计目标**: 专为类XML格式设计，不是完整的XML解析器
- 🚫 **不支持**: XML属性、命名空间、DTD、CDATA等高级特性
- ✅ **专注于**: 简单标签结构，适合LLM输出格式
- 📦 **流式特性**: 内容可能分成多个CONTENT事件，这是正常行为
- 🎨 **选择建议**: 根据具体场景选择最适合的解析器

## 📁 项目结构

```
xml-parser/
├── streaming_xml_parser.py    # 完整XML解析器
├── outer_xml_parser.py        # 外层XML解析器
├── dynamic_tree_parser.py     # 动态树形解析器
├── main.py                    # 基本演示
├── example.py                 # 完整解析器详细示例
├── outer_example.py           # 外层解析器示例
├── dynamic_example.py         # 动态树形解析器示例
├── test_parser.py             # 完整解析器测试
├── test_outer_parser.py       # 外层解析器测试
├── test_dynamic_parser.py     # 动态解析器测试
├── test_complex_cases.py      # 复杂性和鲁棒性测试
└── README.md                  # 项目文档
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境
```bash
# 克隆项目
git clone <repository-url>
cd xml-parser

# 运行所有测试
python test_parser.py
python test_outer_parser.py
python test_dynamic_parser.py
python test_complex_cases.py

# 运行示例
python dynamic_example.py
```

### 测试覆盖
- ✅ 基础功能测试
- ✅ 流式处理测试
- ✅ 边界情况测试
- ✅ 错误处理测试
- ✅ 性能压力测试
- ✅ Unicode支持测试

## 📄 许可证

MIT License - 详见LICENSE文件

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

**🚀 开始使用流式XML解析器套件，让你的LLM输出处理更加高效！**