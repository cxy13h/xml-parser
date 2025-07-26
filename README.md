# 🚀 流式XML解析器套件

一套专为LLM流式输出设计的高性能XML解析器，提供三种不同的解析策略以满足各种应用场景。

## 🎯 核心特性

- **🔥 事件驱动**: 实时产生解析事件，无需等待完整文档
- **⚡ 极低延迟**: 毫秒级响应流式输入
- **📦 流式处理**: 支持任意大小的chunk输入，内存占用恒定
- **🎨 多种策略**: 三种解析器满足不同需求
- **🛡️ 高鲁棒性**: 优雅处理各种边界情况和格式错误
- **🌍 国际化**: 完美支持Unicode和各种特殊字符
- **📊 生产就绪**: 企业级性能和稳定性

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

## 🚀 快速开始

### 1️⃣ 完整XML解析器

```python
from streaming_xml_parser import StreamingXMLParser

parser = StreamingXMLParser()
text = "<Action><ToolName>image_gen</ToolName><Description>AI图像生成</Description></Action>"

for event_type, data in parser.parse_chunk(text):
    print(f"{event_type}: {data}")

# 输出：
# START_TAG: Action
# START_TAG: ToolName
# CONTENT: image_gen
# END_TAG: ToolName
# START_TAG: Description
# CONTENT: AI图像生成
# END_TAG: Description
# END_TAG: Action
```

### 2️⃣ 外层XML解析器

```python
from outer_xml_parser import OuterXMLParser

parser = OuterXMLParser()
text = "<Action><ToolName>image_gen</ToolName><Description>AI图像生成</Description></Action>"

for event_type, data in parser.parse_chunk(text):
    print(f"{event_type}: {data}")

# 输出：
# START_TAG: Action
# CONTENT: <ToolName>image_gen</ToolName><Description>AI图像生成</Description>
# END_TAG: Action
```

### 3️⃣ 动态树形解析器

```python
from dynamic_tree_parser import DynamicTreeParser

# 定义标签层次结构
hierarchy = {
    "Action": ["ToolName", "Description"],
    "Description": ["Feature"]
}

parser = DynamicTreeParser(hierarchy)
text = "<Action><ToolName>image_gen</ToolName><Invalid><Feature>假标签</Feature></Invalid><Description><Feature>真标签</Feature></Description></Action>"

for event_type, data, level in parser.parse_chunk(text):
    print(f"{event_type}: {data} (level {level})")

# 输出：
# START_TAG: Action (level 0)
# START_TAG: ToolName (level 1)
# CONTENT: image_gen (level 2)
# END_TAG: ToolName (level 1)
# CONTENT: <Invalid><Feature>假标签</Feature></Invalid> (level 1)
# START_TAG: Description (level 1)
# START_TAG: Feature (level 2)
# CONTENT: 真标签 (level 3)
# END_TAG: Feature (level 2)
# END_TAG: Description (level 1)
# END_TAG: Action (level 0)
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

## 🎨 使用场景对比

### 📋 完整XML解析器
**最适合**: 标准XML文档处理
```xml
<!-- 输入 -->
<config><database><host>localhost</host><port>5432</port></database></config>

<!-- 解析结果：所有标签都被识别 -->
START_TAG: config → START_TAG: database → START_TAG: host → CONTENT: localhost
```

### 🎯 外层XML解析器
**最适合**: LLM输出的主要结构识别
```xml
<!-- 输入 -->
<Thought><Content>我需要调用<Tool>image_gen</Tool>来生成图片</Content></Thought>

<!-- 解析结果：只识别最外层 -->
START_TAG: Thought → CONTENT: <Content>我需要调用<Tool>image_gen</Tool>来生成图片</Content>
```

### 🧠 动态树形解析器
**最适合**: 基于预定义结构的智能解析
```xml
<!-- 层次结构：{"Action": ["ToolName"], "Response": ["Message"]} -->
<!-- 输入 -->
<Action><ToolName>test</ToolName><Invalid><ToolName>假的</ToolName></Invalid></Action>

<!-- 解析结果：只识别正确位置的标签 -->
START_TAG: Action → START_TAG: ToolName → CONTENT: test → CONTENT: <Invalid><ToolName>假的</ToolName></Invalid>
```

## 🔥 解析器选择指南

| 场景 | 推荐解析器 | 原因 |
|------|------------|------|
| 标准XML文档 | 完整解析器 | 需要解析所有层级结构 |
| LLM对话输出 | 外层解析器 | 只关心主要结构，内容可能包含XML |
| 已知标签结构 | 动态树形解析器 | 能区分真假标签，最智能 |
| 配置文件解析 | 完整解析器 | 结构化数据需要完整解析 |
| 实时聊天消息 | 外层解析器 | 简单快速，适合实时处理 |
| 复杂嵌套场景 | 动态树形解析器 | 最强的上下文感知能力 |

## 🎮 运行示例

### 基础示例
```bash
# 完整解析器
python main.py              # 基本演示
python example.py           # 详细示例

# 外层解析器
python outer_example.py     # 外层解析演示

# 动态树形解析器
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