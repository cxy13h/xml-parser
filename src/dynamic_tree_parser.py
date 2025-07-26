"""
动态树形流式XML解析器

根据预定义的标签层次结构，智能识别哪些是真正的标签，哪些是内容。
支持流式处理，具有高度的鲁棒性。

核心特性：
1. 上下文感知：标签的有效性取决于它在层次结构中的位置
2. 鲁棒性：缺少预期的子标签时仍能正常工作
3. 歧义处理：区分真正的标签和内容中的伪标签
4. 流式处理：支持任意大小的chunk输入

事件类型：
- (XMLEventType.START_TAG, tag_name, level): 识别到的真正标签开始
- (XMLEventType.END_TAG, tag_name, level): 识别到的真正标签结束
- (XMLEventType.CONTENT, text_chunk, level): 内容（包括伪标签）
"""

from typing import Dict, List, Optional, Tuple, Generator
from enum import Enum
import re
from src.common.xml_events import XMLEventType


class TagNode:
    """标签节点，表示标签层次结构中的一个节点"""
    
    def __init__(self, name: str, level: int = 0):
        self.name = name
        self.level = level
        self.children: Dict[str, 'TagNode'] = {}
        self.parent: Optional['TagNode'] = None
    
    def add_child(self, child_name: str) -> 'TagNode':
        """添加子标签"""
        if child_name not in self.children:
            child = TagNode(child_name, self.level + 1)
            child.parent = self
            self.children[child_name] = child
        return self.children[child_name]
    
    def has_child(self, child_name: str) -> bool:
        """检查是否有指定的子标签"""
        return child_name in self.children
    
    def get_child(self, child_name: str) -> Optional['TagNode']:
        """获取子标签节点"""
        return self.children.get(child_name)
    
    def is_valid_child(self, tag_name: str) -> bool:
        """检查指定标签是否是有效的子标签"""
        return tag_name in self.children
    
    def __repr__(self):
        return f"TagNode({self.name}, level={self.level}, children={list(self.children.keys())})"


class ParserState(Enum):
    """解析器状态"""
    CONTENT = "content"
    IN_TAG = "in_tag"
    IN_CONTENT = "in_content"


class DynamicTreeParser:
    """动态树形流式XML解析器"""
    
    def __init__(self, tag_hierarchy: Dict[str, List[str]]):
        """
        初始化解析器
        
        Args:
            tag_hierarchy: 标签层次结构，格式为 {parent: [child1, child2, ...]}
                          例如: {"Action": ["ToolName", "Description"], "Description": ["Feature"]}
        """
        self.tag_tree = self._build_tag_tree(tag_hierarchy)
        self.reset()
    
    def _build_tag_tree(self, hierarchy: Dict[str, List[str]]) -> Dict[str, TagNode]:
        """构建标签树"""
        # 创建所有节点
        nodes = {}
        
        # 首先创建所有提到的标签节点
        all_tags = set()
        for parent, children in hierarchy.items():
            all_tags.add(parent)
            all_tags.update(children)
        
        for tag in all_tags:
            nodes[tag] = TagNode(tag)
        
        # 建立父子关系
        for parent_name, children in hierarchy.items():
            parent_node = nodes[parent_name]
            for child_name in children:
                child_node = parent_node.add_child(child_name)
                nodes[child_name] = child_node
        
        # 找出根节点（没有父节点的节点）
        root_nodes = {}
        for name, node in nodes.items():
            if node.parent is None:
                root_nodes[name] = node
        
        return root_nodes
    
    def reset(self):
        """重置解析器状态"""
        self.state = ParserState.CONTENT
        self.buffer = ""
        self.tag_stack: List[TagNode] = []  # 当前标签栈
        self.current_context: Optional[TagNode] = None  # 当前上下文节点
        self.invalid_tag_depth = 0  # 当前无效标签的嵌套深度
    
    def parse_chunk(self, chunk: str) -> Generator[Tuple[str, str, int], None, None]:
        """
        解析一个文本块，产生事件
        
        Args:
            chunk: 输入的文本块
            
        Yields:
            Tuple[str, str, int]: (事件类型, 数据, 层级)
        """
        if not chunk:
            return
        
        # 将新的chunk添加到缓冲区
        self.buffer += chunk
        
        while True:
            if self.state == ParserState.CONTENT:
                # 寻找下一个可能的标签开始
                lt_pos = self.buffer.find('<')
                
                if lt_pos == -1:
                    # 没有找到标签，输出剩余内容
                    if self.buffer.strip():
                        yield (XMLEventType.CONTENT, self.buffer, 0)
                    self.buffer = ""
                    break
                else:
                    # 找到标签开始，先输出之前的内容
                    if lt_pos > 0:
                        content = self.buffer[:lt_pos]
                        if content.strip():
                            yield (XMLEventType.CONTENT, content, 0)
                    
                    # 进入标签解析状态
                    self.state = ParserState.IN_TAG
                    self.buffer = self.buffer[lt_pos + 1:]  # 移除 '<'
            
            elif self.state == ParserState.IN_TAG:
                # 在标签内，寻找标签结束
                gt_pos = self.buffer.find('>')
                
                if gt_pos == -1:
                    # 标签未完整，等待更多数据
                    break
                else:
                    # 找到完整标签
                    tag_content = self.buffer[:gt_pos]
                    self.buffer = self.buffer[gt_pos + 1:]  # 移除标签内容和 '>'
                    
                    # 解析标签
                    tag_processed = False

                    if tag_content.startswith('/'):
                        # 结束标签
                        tag_name = self._extract_tag_name(tag_content[1:])
                        if tag_name:
                            end_result = self._handle_end_tag(tag_name)
                            if end_result:
                                event_type, data, level = end_result
                                yield (event_type, data, level)
                                tag_processed = True
                            else:
                                # 不是有效的结束标签，减少无效标签深度
                                self.invalid_tag_depth = max(0, self.invalid_tag_depth - 1)
                    else:
                        # 开始标签
                        tag_name = self._extract_tag_name(tag_content)
                        if tag_name:
                            start_result = self._handle_start_tag(tag_name)
                            if start_result:
                                event_type, data, level = start_result
                                yield (event_type, data, level)
                                tag_processed = True
                            else:
                                # 不是有效标签，增加无效标签深度
                                self.invalid_tag_depth += 1

                    # 如果标签没有被处理（不是有效标签），将其作为内容输出
                    if not tag_processed:
                        level = self.tag_stack[-1].level + 1 if self.tag_stack else 0
                        full_tag = f"<{tag_content}>"
                        yield (XMLEventType.CONTENT, full_tag, level)

                    # 根据当前状态决定下一步
                    if self.tag_stack:
                        self.state = ParserState.IN_CONTENT
                    else:
                        self.state = ParserState.CONTENT
            
            elif self.state == ParserState.IN_CONTENT:
                # 在已识别标签内，寻找子标签或结束标签
                if not self.tag_stack:
                    # 标签栈为空，回到CONTENT状态
                    self.state = ParserState.CONTENT
                    continue
                
                current_tag = self.tag_stack[-1]
                
                # 寻找可能的结束标签
                end_tag_pattern = f"</{current_tag.name}>"
                end_pos = self.buffer.find(end_tag_pattern)
                
                # 寻找可能的子标签
                lt_pos = self.buffer.find('<')
                
                if end_pos != -1 and (lt_pos == -1 or end_pos <= lt_pos):
                    # 找到当前标签的结束标签，且它在任何其他标签之前
                    if end_pos > 0:
                        content = self.buffer[:end_pos]
                        if content:
                            yield (XMLEventType.CONTENT, content, current_tag.level + 1)

                    # 处理结束标签
                    yield (XMLEventType.END_TAG, current_tag.name, current_tag.level)
                    self.tag_stack.pop()
                    self.buffer = self.buffer[end_pos + len(end_tag_pattern):]
                    
                    # 更新当前上下文
                    self.current_context = self.tag_stack[-1] if self.tag_stack else None
                    
                    if not self.tag_stack:
                        self.state = ParserState.CONTENT
                
                elif lt_pos != -1:
                    # 找到可能的标签开始
                    if lt_pos > 0:
                        content = self.buffer[:lt_pos]
                        if content:
                            yield (XMLEventType.CONTENT, content, current_tag.level + 1)
                    
                    # 进入标签解析状态
                    self.state = ParserState.IN_TAG
                    self.buffer = self.buffer[lt_pos + 1:]  # 移除 '<'
                
                else:
                    # 没有找到任何标签，输出剩余内容
                    if self.buffer:
                        yield (XMLEventType.CONTENT, self.buffer, current_tag.level + 1)
                    self.buffer = ""
                    break
    
    def _handle_start_tag(self, tag_name: str) -> Optional[Tuple[str, str, int]]:
        """处理开始标签"""
        # 检查这个标签是否在当前上下文中有效，并且没有被无效标签包围
        if not self.tag_stack:
            # 当前在根级别，检查是否是根标签，且没有无效标签包围
            if tag_name in self.tag_tree and self.invalid_tag_depth == 0:
                node = self.tag_tree[tag_name]
                self.tag_stack.append(node)
                self.current_context = node
                return (XMLEventType.START_TAG, tag_name, node.level)
        else:
            # 当前在某个标签内，检查是否是有效的直接子标签，且没有无效标签包围
            current_tag = self.tag_stack[-1]

            if (current_tag.is_valid_child(tag_name) and
                self.invalid_tag_depth == 0):
                child_node = current_tag.get_child(tag_name)
                self.tag_stack.append(child_node)
                self.current_context = child_node
                return (XMLEventType.START_TAG, tag_name, child_node.level)

        # 如果不是有效标签，不产生事件（将作为内容处理）
        return None
    
    def _handle_end_tag(self, tag_name: str) -> Optional[Tuple[str, str, int]]:
        """处理结束标签"""
        # 检查是否匹配当前标签栈顶的标签
        if self.tag_stack and self.tag_stack[-1].name == tag_name:
            node = self.tag_stack.pop()
            self.current_context = self.tag_stack[-1] if self.tag_stack else None
            return (XMLEventType.END_TAG, tag_name, node.level)
        
        # 如果不匹配，不产生事件（将作为内容处理）
        return None
    
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
    
    def finalize(self) -> Generator[Tuple[str, str, int], None, None]:
        """
        完成解析，输出剩余的内容
        
        Yields:
            Tuple[str, str, int]: 剩余的内容事件
        """
        if self.buffer:
            level = self.tag_stack[-1].level + 1 if self.tag_stack else 0
            if self.buffer.strip():
                yield (XMLEventType.CONTENT, self.buffer, level)
        
        # 重置状态
        self.buffer = ""
        self.tag_stack = []
        self.current_context = None
        self.invalid_tag_depth = 0
    
    def get_tag_hierarchy_info(self) -> str:
        """获取标签层次结构信息"""
        info = "标签层次结构:\n"
        for name, node in self.tag_tree.items():
            info += self._format_node(node, 0)
        return info
    
    def _format_node(self, node: TagNode, indent: int) -> str:
        """格式化节点信息"""
        result = "  " * indent + f"- {node.name} (level {node.level})\n"
        for child in node.children.values():
            result += self._format_node(child, indent + 1)
        return result


class DynamicTreeEventHandler:
    """动态树形解析器事件处理器基类"""
    
    def on_start_tag(self, tag_name: str, level: int):
        """处理开始标签事件"""
        pass
    
    def on_end_tag(self, tag_name: str, level: int):
        """处理结束标签事件"""
        pass
    
    def on_content(self, content: str, level: int):
        """处理内容事件"""
        pass
    
    def handle_event(self, event_type: str, data: str, level: int):
        """处理事件的统一入口"""
        if event_type == 'START_TAG':
            self.on_start_tag(data, level)
        elif event_type == 'END_TAG':
            self.on_end_tag(data, level)
        elif event_type == 'CONTENT':
            self.on_content(data, level)


def parse_dynamic_stream(chunks, tag_hierarchy: Dict[str, List[str]], 
                        event_handler: DynamicTreeEventHandler):
    """
    便利函数：使用动态树形解析器解析流式数据
    
    Args:
        chunks: 可迭代的文本块
        tag_hierarchy: 标签层次结构
        event_handler: 事件处理器
    """
    parser = DynamicTreeParser(tag_hierarchy)
    
    for chunk in chunks:
        for event_type, data, level in parser.parse_chunk(chunk):
            event_handler.handle_event(event_type, data, level)
    
    # 处理剩余内容
    for event_type, data, level in parser.finalize():
        event_handler.handle_event(event_type, data, level)
