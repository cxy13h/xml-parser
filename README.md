# 流式XML解析器

一个事件驱动的、用于解析流式类XML文本的解析器，专为处理LLM的流式输出而设计。

## 特性

- **事件驱动**: 实时产生解析事件，无需等待完整文档
- **极低延迟**: 能够以极低的延迟响应流式输入
- **流式处理**: 支持任意大小的chunk输入
- **简单易用**: 提供简洁的API和事件处理器

## 事件类型

解析器产生三种类型的事件：

- `('START_TAG', tag_name)`: 当解析到一个完整的起始标签时产生，如 `<Thought>`
- `('END_TAG', tag_name)`: 当解析到一个完整的结束标签时产生，如 `</Thought>`
- `('CONTENT', text_chunk)`: 在两个标签之间的所有文本内容，会被分块产生

## 快速开始

### 基本使用

```python
from streaming_xml_parser import StreamingXMLParser

# 创建解析器
parser = StreamingXMLParser()

# 模拟流式输入
chunks = ["<tag>", "content", "</tag>"]

for chunk in chunks:
    for event_type, data in parser.parse_chunk(chunk):
        print(f"{event_type}: {data}")

# 处理剩余内容
for event_type, data in parser.finalize():
    print(f"Final {event_type}: {data}")
```

### 使用事件处理器

```python
from streaming_xml_parser import XMLEventHandler, parse_stream

class MyHandler(XMLEventHandler):
    def on_start_tag(self, tag_name: str):
        print(f"开始标签: {tag_name}")

    def on_end_tag(self, tag_name: str):
        print(f"结束标签: {tag_name}")

    def on_content(self, content: str):
        print(f"内容: {content}")

# 使用处理器
handler = MyHandler()
chunks = ["<tag>", "content", "</tag>"]
parse_stream(chunks, handler)
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

## 外层XML解析器

除了完整的XML解析器，我们还提供了一个**外层XML解析器**，专门用于只解析最外层标签的场景。

### 使用场景

在LLM输出中，我们经常遇到这样的情况：很难分清楚哪些是"标签"，哪些是"内容"，因为"内容"本身就可能是XML格式。

例如：`<Start><Reason>Observation</Reason></Start>`

- 使用**完整解析器**：会解析出 `Start`, `Reason` 两个标签
- 使用**外层解析器**：只解析 `Start` 标签，`<Reason>Observation</Reason>` 被当作内容

### 外层解析器示例

```python
from outer_xml_parser import OuterXMLParser

parser = OuterXMLParser()
text = "<Start><Reason>Observation</Reason></Start>"

for event_type, data in parser.parse_chunk(text):
    print(f"{event_type}: {data}")

# 输出：
# START_TAG: Start
# CONTENT: <Reason>Observation</Reason>
# END_TAG: Start
```

### 对比两种解析器

| 特性 | 完整解析器 | 外层解析器 |
|------|------------|------------|
| 解析层级 | 所有层级 | 仅最外层 |
| 内层XML | 解析为标签 | 当作内容 |
| 适用场景 | 结构化XML | LLM输出解析 |
| 复杂度 | 较高 | 较低 |

## 运行示例

```bash
# 完整解析器示例
python main.py
python example.py
python test_parser.py

# 外层解析器示例
python outer_example.py
python test_outer_parser.py
```

## API参考

### StreamingXMLParser (完整解析器)

解析所有层级的XML标签。

#### 方法

- `parse_chunk(chunk: str) -> Generator[Tuple[str, str], None, None]`
  - 解析一个文本块，产生事件
  - 返回: 事件生成器

- `finalize() -> Generator[Tuple[str, str], None, None]`
  - 完成解析，输出剩余的内容

- `reset()` - 重置解析器状态

### OuterXMLParser (外层解析器)

只解析最外层的XML标签。

#### 方法

- `parse_chunk(chunk: str) -> Generator[Tuple[str, str], None, None]`
  - 解析一个文本块，只产生外层标签事件
  - 返回: 事件生成器

- `finalize() -> Generator[Tuple[str, str], None, None]`
  - 完成解析，输出剩余的内容

- `reset()` - 重置解析器状态

### 事件处理器

#### XMLEventHandler (完整解析器)

- `on_start_tag(tag_name: str)` - 处理起始标签事件
- `on_end_tag(tag_name: str)` - 处理结束标签事件
- `on_content(content: str)` - 处理内容事件

#### OuterXMLEventHandler (外层解析器)

- `on_start_tag(tag_name: str)` - 处理外层起始标签事件
- `on_end_tag(tag_name: str)` - 处理外层结束标签事件
- `on_content(content: str)` - 处理内容事件（可能包含内层XML）

### 便利函数

- `parse_stream(chunks, event_handler: XMLEventHandler)` - 使用完整解析器
- `parse_outer_stream(chunks, event_handler: OuterXMLEventHandler)` - 使用外层解析器

## 设计原理

### 完整解析器

使用状态机跟踪解析状态：
1. **CONTENT**: 在标签外，解析内容
2. **IN_START_TAG**: 在起始标签内
3. **IN_END_TAG**: 在结束标签内

### 外层解析器

使用简化的状态机：
1. **CONTENT**: 在最外层标签外
2. **IN_TAG**: 在最外层标签内
3. **IN_CONTENT**: 在最外层标签内收集内容

外层解析器通过匹配完整的结束标签模式（如 `</Start>`）来识别最外层标签的结束。

## 注意事项

- 两个解析器都是为类XML格式设计的，不是完整的XML解析器
- 不支持XML属性、命名空间等高级特性
- 专注于简单的标签结构，适合LLM输出格式
- 在流式处理中，内容可能会被分成多个CONTENT事件，这是正常行为
- 外层解析器特别适合处理LLM输出中的嵌套XML内容