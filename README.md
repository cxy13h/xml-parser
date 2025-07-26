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

## 运行示例

```bash
# 运行基本示例
python main.py

# 运行详细示例
python example.py

# 运行测试
python test_parser.py
```