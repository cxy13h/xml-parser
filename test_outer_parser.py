"""
外层XML解析器的单元测试
"""

import unittest
from outer_xml_parser import OuterXMLParser, OuterXMLEventHandler


class TestOuterXMLParser(unittest.TestCase):
    """测试OuterXMLParser类"""
    
    def setUp(self):
        """测试前的设置"""
        self.parser = OuterXMLParser()
    
    def parse_text(self, text: str, chunk_size: int = 1):
        """辅助方法：将文本分块解析并收集所有事件"""
        events = []
        
        # 分块解析
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            for event in self.parser.parse_chunk(chunk):
                events.append(event)
        
        # 获取最终事件
        for event in self.parser.finalize():
            events.append(event)
            
        return events
    
    def test_simple_outer_tag(self):
        """测试简单的外层标签"""
        text = "<Start>simple content</Start>"
        events = self.parse_text(text)
        
        expected = [
            ('START_TAG', 'Start'),
            ('CONTENT', 'simple content'),
            ('END_TAG', 'Start')
        ]
        
        self.assertEqual(events, expected)
    
    def test_nested_xml_as_content(self):
        """测试嵌套XML被当作内容处理"""
        text = "<Start><Reason>Observation</Reason></Start>"
        events = self.parse_text(text)
        
        expected = [
            ('START_TAG', 'Start'),
            ('CONTENT', '<Reason>Observation</Reason>'),
            ('END_TAG', 'Start')
        ]
        
        self.assertEqual(events, expected)
    
    def test_complex_nested_content(self):
        """测试复杂的嵌套内容"""
        text = "<Thought><Content>用户希望<Action>画图</Action>，我需要调用API</Content></Thought>"
        events = self.parse_text(text)
        
        expected = [
            ('START_TAG', 'Thought'),
            ('CONTENT', '<Content>用户希望<Action>画图</Action>，我需要调用API</Content>'),
            ('END_TAG', 'Thought')
        ]
        
        self.assertEqual(events, expected)
    
    def test_multiple_outer_tags(self):
        """测试多个外层标签"""
        text = "<Start><Reason>UserInput</Reason></Start><Thought><Content>thinking</Content></Thought>"
        events = self.parse_text(text)
        
        expected = [
            ('START_TAG', 'Start'),
            ('CONTENT', '<Reason>UserInput</Reason>'),
            ('END_TAG', 'Start'),
            ('START_TAG', 'Thought'),
            ('CONTENT', '<Content>thinking</Content>'),
            ('END_TAG', 'Thought')
        ]
        
        self.assertEqual(events, expected)
    
    def test_content_between_tags(self):
        """测试标签之间的内容"""
        text = "<Start>content1</Start>\n\n<Thought>content2</Thought>"
        events = self.parse_text(text)
        
        expected = [
            ('START_TAG', 'Start'),
            ('CONTENT', 'content1'),
            ('END_TAG', 'Start'),
            ('CONTENT', '\n\n'),
            ('START_TAG', 'Thought'),
            ('CONTENT', 'content2'),
            ('END_TAG', 'Thought')
        ]
        
        self.assertEqual(events, expected)
    
    def test_empty_outer_tag(self):
        """测试空的外层标签"""
        text = "<Start></Start>"
        events = self.parse_text(text)
        
        expected = [
            ('START_TAG', 'Start'),
            ('END_TAG', 'Start')
        ]
        
        self.assertEqual(events, expected)
    
    def test_streaming_with_incomplete_tags(self):
        """测试流式处理中的不完整标签"""
        parser = OuterXMLParser()
        
        # 第一个chunk只包含标签的一部分
        events1 = list(parser.parse_chunk("<Sta"))
        self.assertEqual(events1, [])  # 应该没有事件产生
        
        # 第二个chunk完成外层标签
        events2 = list(parser.parse_chunk("rt><Reason>test</Reason></Start>"))
        
        expected = [
            ('START_TAG', 'Start'),
            ('CONTENT', '<Reason>test</Reason>'),
            ('END_TAG', 'Start')
        ]
        
        self.assertEqual(events2, expected)
    
    def test_deeply_nested_content(self):
        """测试深度嵌套的内容"""
        text = "<Action><Tool><Name>image_gen</Name><Args><Query>test</Query></Args></Tool></Action>"
        events = self.parse_text(text)
        
        expected = [
            ('START_TAG', 'Action'),
            ('CONTENT', '<Tool><Name>image_gen</Name><Args><Query>test</Query></Args></Tool>'),
            ('END_TAG', 'Action')
        ]
        
        self.assertEqual(events, expected)
    
    def test_mixed_content_and_tags(self):
        """测试混合内容和标签"""
        text = "<Start>前缀<Reason>原因</Reason>后缀</Start>"
        events = self.parse_text(text)
        
        expected = [
            ('START_TAG', 'Start'),
            ('CONTENT', '前缀<Reason>原因</Reason>后缀'),
            ('END_TAG', 'Start')
        ]
        
        self.assertEqual(events, expected)
    
    def test_chunk_size_variations(self):
        """测试不同的chunk大小"""
        text = "<Start><Reason>UserInput</Reason></Start>"
        
        # 测试不同的chunk大小都能得到相同结果
        for chunk_size in [1, 3, 5, 10, 20]:
            with self.subTest(chunk_size=chunk_size):
                events = self.parse_text(text, chunk_size)
                expected = [
                    ('START_TAG', 'Start'),
                    ('CONTENT', '<Reason>UserInput</Reason>'),
                    ('END_TAG', 'Start')
                ]
                
                # 合并连续的CONTENT事件
                merged_events = []
                content_buffer = ""
                
                for event_type, data in events:
                    if event_type == 'CONTENT':
                        content_buffer += data
                    else:
                        if content_buffer:
                            merged_events.append(('CONTENT', content_buffer))
                            content_buffer = ""
                        merged_events.append((event_type, data))
                
                if content_buffer:
                    merged_events.append(('CONTENT', content_buffer))
                
                self.assertEqual(merged_events, expected)


class TestEventHandler(OuterXMLEventHandler):
    """测试用的事件处理器"""
    
    def __init__(self):
        self.events = []
    
    def on_start_tag(self, tag_name: str):
        self.events.append(('START_TAG', tag_name))
    
    def on_end_tag(self, tag_name: str):
        self.events.append(('END_TAG', tag_name))
    
    def on_content(self, content: str):
        self.events.append(('CONTENT', content))


class TestOuterXMLEventHandler(unittest.TestCase):
    """测试OuterXMLEventHandler类"""
    
    def test_event_handler(self):
        """测试事件处理器"""
        from outer_xml_parser import parse_outer_stream
        
        handler = TestEventHandler()
        chunks = ["<Start>", "<Reason>test</Reason>", "</Start>"]
        
        parse_outer_stream(chunks, handler)
        
        # 合并连续的CONTENT事件
        merged_events = []
        content_buffer = ""
        
        for event_type, data in handler.events:
            if event_type == 'CONTENT':
                content_buffer += data
            else:
                if content_buffer:
                    merged_events.append(('CONTENT', content_buffer))
                    content_buffer = ""
                merged_events.append((event_type, data))
        
        if content_buffer:
            merged_events.append(('CONTENT', content_buffer))
        
        expected = [
            ('START_TAG', 'Start'),
            ('CONTENT', '<Reason>test</Reason>'),
            ('END_TAG', 'Start')
        ]
        
        self.assertEqual(merged_events, expected)


if __name__ == '__main__':
    unittest.main()
