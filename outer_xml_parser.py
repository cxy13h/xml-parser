"""
外层XML解析器

只解析最外层的XML标签，内层的所有内容（包括嵌套的XML标签）都被当作纯文本内容处理。

例如：<Start><Reason>Observation</Reason></Start>
- Start 被识别为标签
- <Reason>Observation</Reason> 被当作 Start 标签的内容

支持的事件类型：
- ('START_TAG', tag_name): 最外层的起始标签
- ('END_TAG', tag_name): 最外层的结束标签  
- ('CONTENT', text_chunk): 标签间的文本内容（可能包含内层XML）
"""

import re
from enum import Enum
from typing import Generator, Tuple, Optional, List


class OuterParserState(Enum):
    """外层解析器状态枚举"""
    CONTENT = "content"          # 在最外层标签外，解析内容
    IN_TAG = "in_tag"           # 在标签内，收集标签名
    IN_CONTENT = "in_content"   # 在最外层标签内，收集内容


class OuterXMLParser:
    """外层XML解析器 - 只解析最外层标签"""

    def __init__(self):
        self.reset()

    def reset(self):
        """重置解析器状态"""
        self.state = OuterParserState.CONTENT
        self.buffer = ""  # 缓冲区，存储所有输入
        self.current_outer_tag = None  # 当前的最外层标签
        
    def parse_chunk(self, chunk: str) -> Generator[Tuple[str, str], None, None]:
        """
        解析一个文本块，产生事件

        Args:
            chunk: 输入的文本块

        Yields:
            Tuple[str, str]: (事件类型, 数据)
        """
        if not chunk:
            return

        # 将新的chunk添加到缓冲区
        self.buffer += chunk

        # 处理缓冲区中的内容
        while True:
            if self.state == OuterParserState.CONTENT:
                # 寻找下一个标签开始
                lt_pos = self.buffer.find('<')

                if lt_pos == -1:
                    # 没有找到标签，输出剩余内容并等待更多数据
                    if self.buffer.strip():
                        yield ('CONTENT', self.buffer)
                    self.buffer = ""
                    break
                else:
                    # 找到标签开始，先输出之前的内容
                    if lt_pos > 0:
                        content = self.buffer[:lt_pos]
                        if content.strip():
                            yield ('CONTENT', content)

                    # 进入标签解析状态
                    self.state = OuterParserState.IN_TAG
                    self.buffer = self.buffer[lt_pos + 1:]  # 移除 '<' 和之前的内容

            elif self.state == OuterParserState.IN_TAG:
                # 在标签内，寻找标签结束
                gt_pos = self.buffer.find('>')

                if gt_pos == -1:
                    # 标签未完整，等待更多数据
                    break
                else:
                    # 找到完整标签
                    tag_content = self.buffer[:gt_pos]
                    tag_name = self._extract_tag_name(tag_content)

                    if tag_name:
                        # 这是一个新的最外层标签
                        self.current_outer_tag = tag_name
                        yield ('START_TAG', tag_name)
                        self.state = OuterParserState.IN_CONTENT

                    self.buffer = self.buffer[gt_pos + 1:]  # 移除标签内容和 '>'

            elif self.state == OuterParserState.IN_CONTENT:
                # 在最外层标签内，寻找匹配的结束标签
                end_tag_pattern = f"</{self.current_outer_tag}>"
                end_pos = self.buffer.find(end_tag_pattern)

                if end_pos != -1:
                    # 找到完整的匹配结束标签
                    if end_pos > 0:
                        content = self.buffer[:end_pos]
                        if content:
                            yield ('CONTENT', content)

                    # 输出结束标签事件
                    yield ('END_TAG', self.current_outer_tag)

                    # 重置状态
                    self.current_outer_tag = None
                    self.state = OuterParserState.CONTENT
                    self.buffer = self.buffer[end_pos + len(end_tag_pattern):]
                else:
                    # 没有找到完整的结束标签，检查缓冲区末尾是否可能是结束标签的开始
                    max_keep = min(len(end_tag_pattern) - 1, len(self.buffer))

                    # 检查缓冲区末尾的各种长度是否匹配结束标签的开始
                    keep_length = 0
                    for length in range(1, max_keep + 1):
                        suffix = self.buffer[-length:]
                        if end_tag_pattern.startswith(suffix):
                            keep_length = length

                    if keep_length > 0:
                        # 保留可能的结束标签开始部分，输出其余内容
                        content_end = len(self.buffer) - keep_length
                        if content_end > 0:
                            content = self.buffer[:content_end]
                            if content:
                                yield ('CONTENT', content)
                        self.buffer = self.buffer[content_end:]
                        break
                    else:
                        # 没有可能的部分匹配，输出所有内容并等待更多数据
                        if self.buffer:
                            yield ('CONTENT', self.buffer)
                        self.buffer = ""
                        break
    

    

    
    def _extract_tag_name(self, tag_content: str) -> Optional[str]:
        """从标签内容中提取标签名"""
        if not tag_content:
            return None
            
        # 移除前后空白
        tag_content = tag_content.strip()
        
        # 提取标签名（第一个单词）
        match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_-]*)', tag_content)
        if match:
            return match.group(1)
        
        return None
    
    def finalize(self) -> Generator[Tuple[str, str], None, None]:
        """
        完成解析，输出剩余的内容

        Yields:
            Tuple[str, str]: 剩余的内容事件
        """
        # 如果还有未处理的内容
        if self.buffer:
            if self.buffer.strip():
                yield ('CONTENT', self.buffer)

        # 重置状态
        self.buffer = ""
        self.current_outer_tag = None


class OuterXMLEventHandler:
    """外层XML事件处理器基类"""
    
    def on_start_tag(self, tag_name: str):
        """处理最外层起始标签事件"""
        pass
    
    def on_end_tag(self, tag_name: str):
        """处理最外层结束标签事件"""
        pass
    
    def on_content(self, content: str):
        """处理内容事件（可能包含内层XML）"""
        pass
    
    def handle_event(self, event_type: str, data: str):
        """处理事件的统一入口"""
        if event_type == 'START_TAG':
            self.on_start_tag(data)
        elif event_type == 'END_TAG':
            self.on_end_tag(data)
        elif event_type == 'CONTENT':
            self.on_content(data)


def parse_outer_stream(chunks, event_handler: OuterXMLEventHandler):
    """
    便利函数：解析流式数据并处理外层标签事件
    
    Args:
        chunks: 可迭代的文本块
        event_handler: 事件处理器
    """
    parser = OuterXMLParser()
    
    for chunk in chunks:
        for event_type, data in parser.parse_chunk(chunk):
            event_handler.handle_event(event_type, data)
    
    # 处理剩余内容
    for event_type, data in parser.finalize():
        event_handler.handle_event(event_type, data)
