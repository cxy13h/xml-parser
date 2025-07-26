"""
事件驱动的流式XML解析器

该解析器能够处理流式输入的XML文本，实时产生解析事件。
支持的事件类型：
- (XMLEventType.START_TAG, tag_name): 完整的起始标签
- (XMLEventType.END_TAG, tag_name): 完整的结束标签
- (XMLEventType.CONTENT, text_chunk): 标签间的文本内容
"""

import re
from enum import Enum
from typing import Generator, Tuple, Optional
from src.common.xml_events import XMLEventType


class ParserState(Enum):
    """解析器状态枚举"""
    CONTENT = "content"          # 在标签外，解析内容
    IN_START_TAG = "in_start_tag"    # 在起始标签内
    IN_END_TAG = "in_end_tag"        # 在结束标签内


class StreamingXMLParser:
    """流式XML解析器"""

    def __init__(self):
        self.reset()

    def reset(self):
        """重置解析器状态"""
        self.state = ParserState.CONTENT
        self.buffer = ""  # 缓冲区，存储所有输入
        self.position = 0  # 当前处理位置
        
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
        while self.position < len(self.buffer):
            if self.state == ParserState.CONTENT:
                # 寻找下一个标签开始
                lt_pos = self.buffer.find('<', self.position)

                if lt_pos == -1:
                    # 没有找到标签，输出剩余内容
                    if self.position < len(self.buffer):
                        content = self.buffer[self.position:]
                        if content:
                            yield (XMLEventType.CONTENT, content)
                        self.position = len(self.buffer)
                    break
                else:
                    # 找到标签开始，先输出之前的内容
                    if lt_pos > self.position:
                        content = self.buffer[self.position:lt_pos]
                        if content:
                            yield (XMLEventType.CONTENT, content)

                    # 检查是否是结束标签
                    if lt_pos + 1 < len(self.buffer) and self.buffer[lt_pos + 1] == '/':
                        # 结束标签
                        self.state = ParserState.IN_END_TAG
                        self.position = lt_pos + 2  # 跳过 '</'
                    elif lt_pos + 1 < len(self.buffer):
                        # 开始标签
                        self.state = ParserState.IN_START_TAG
                        self.position = lt_pos + 1  # 跳过 '<'
                    else:
                        # 缓冲区结束，等待更多数据
                        break

            elif self.state == ParserState.IN_START_TAG:
                # 寻找标签结束
                gt_pos = self.buffer.find('>', self.position)

                if gt_pos == -1:
                    # 标签未完整，等待更多数据
                    break
                else:
                    # 找到完整标签
                    tag_content = self.buffer[self.position:gt_pos]
                    tag_name = self._extract_tag_name(tag_content)
                    if tag_name:
                        yield (XMLEventType.START_TAG, tag_name)

                    self.position = gt_pos + 1
                    self.state = ParserState.CONTENT

            elif self.state == ParserState.IN_END_TAG:
                # 寻找标签结束
                gt_pos = self.buffer.find('>', self.position)

                if gt_pos == -1:
                    # 标签未完整，等待更多数据
                    break
                else:
                    # 找到完整标签
                    tag_content = self.buffer[self.position:gt_pos]
                    tag_name = self._extract_tag_name(tag_content)
                    if tag_name:
                        yield (XMLEventType.END_TAG, tag_name)

                    self.position = gt_pos + 1
                    self.state = ParserState.CONTENT

        # 清理已处理的缓冲区内容（保留未处理的部分）
        if self.position > 0:
            self.buffer = self.buffer[self.position:]
            self.position = 0
    

    


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
        # 如果还有未处理的内容且处于内容状态，输出它
        if self.state == ParserState.CONTENT and self.position < len(self.buffer):
            remaining_content = self.buffer[self.position:]
            if remaining_content:
                yield (XMLEventType.CONTENT, remaining_content)

        # 重置状态
        self.buffer = ""
        self.position = 0


class XMLEventHandler:
    """XML事件处理器基类"""
    
    def on_start_tag(self, tag_name: str):
        """处理起始标签事件"""
        pass
    
    def on_end_tag(self, tag_name: str):
        """处理结束标签事件"""
        pass
    
    def on_content(self, content: str):
        """处理内容事件"""
        pass
    
    def handle_event(self, event_type: str, data: str):
        """处理事件的统一入口"""
        if event_type == 'START_TAG':
            self.on_start_tag(data)
        elif event_type == 'END_TAG':
            self.on_end_tag(data)
        elif event_type == 'CONTENT':
            self.on_content(data)


def parse_stream(chunks, event_handler: XMLEventHandler):
    """
    便利函数：解析流式数据并处理事件
    
    Args:
        chunks: 可迭代的文本块
        event_handler: 事件处理器
    """
    parser = StreamingXMLParser()
    
    for chunk in chunks:
        for event_type, data in parser.parse_chunk(chunk):
            event_handler.handle_event(event_type, data)
    
    # 处理剩余内容
    for event_type, data in parser.finalize():
        event_handler.handle_event(event_type, data)
