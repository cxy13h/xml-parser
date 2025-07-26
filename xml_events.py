"""
XML解析器事件类型定义

统一定义所有XML解析器使用的事件类型，便于维护和管理。
"""

from enum import Enum


class XMLEventType(Enum):
    """XML解析器事件类型枚举"""
    
    START_TAG = "START_TAG"
    """起始标签事件，如 <tag>"""
    
    END_TAG = "END_TAG"
    """结束标签事件，如 </tag>"""
    
    CONTENT = "CONTENT"
    """内容事件，标签之间的文本内容"""
    
    def __str__(self):
        """返回事件类型的字符串表示"""
        return self.value
    
    def __repr__(self):
        """返回事件类型的详细表示"""
        return f"XMLEventType.{self.name}"


# 为了向后兼容，提供字符串常量
START_TAG = XMLEventType.START_TAG.value
END_TAG = XMLEventType.END_TAG.value
CONTENT = XMLEventType.CONTENT.value

# 导出所有事件类型
__all__ = [
    'XMLEventType',
    'START_TAG', 
    'END_TAG', 
    'CONTENT'
]
