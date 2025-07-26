"""
流式XML解析器的单元测试
"""

import unittest
from streaming_xml_parser import StreamingXMLParser, XMLEventHandler


class TestStreamingXMLParser(unittest.TestCase):
    """测试StreamingXMLParser类"""
    
    def setUp(self):
        """测试前的设置"""
        self.parser = StreamingXMLParser()
    
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
    
    def test_simple_tag(self):
        """测试简单标签"""
        text = "<tag>content</tag>"
        events = self.parse_text(text)

        # 验证标签结构
        start_tags = [e for e in events if e[0] == 'START_TAG']
        end_tags = [e for e in events if e[0] == 'END_TAG']
        content_events = [e for e in events if e[0] == 'CONTENT']

        self.assertEqual(len(start_tags), 1)
        self.assertEqual(len(end_tags), 1)
        self.assertEqual(start_tags[0], ('START_TAG', 'tag'))
        self.assertEqual(end_tags[0], ('END_TAG', 'tag'))

        # 合并所有内容
        full_content = ''.join(e[1] for e in content_events)
        self.assertEqual(full_content, 'content')
    
    def test_nested_tags(self):
        """测试嵌套标签"""
        text = "<outer><inner>content</inner></outer>"
        events = self.parse_text(text)

        # 验证标签顺序
        tag_events = [(e[0], e[1]) for e in events if e[0] in ['START_TAG', 'END_TAG']]
        content_events = [e for e in events if e[0] == 'CONTENT']

        expected_tags = [
            ('START_TAG', 'outer'),
            ('START_TAG', 'inner'),
            ('END_TAG', 'inner'),
            ('END_TAG', 'outer')
        ]

        self.assertEqual(tag_events, expected_tags)

        # 合并所有内容
        full_content = ''.join(e[1] for e in content_events)
        self.assertEqual(full_content, 'content')
    
    def test_multiple_content_chunks(self):
        """测试多个内容块"""
        text = "<tag>hello world</tag>"
        events = self.parse_text(text, chunk_size=3)
        
        # 应该有一个START_TAG，多个CONTENT事件，一个END_TAG
        start_tags = [e for e in events if e[0] == 'START_TAG']
        end_tags = [e for e in events if e[0] == 'END_TAG']
        content_events = [e for e in events if e[0] == 'CONTENT']
        
        self.assertEqual(len(start_tags), 1)
        self.assertEqual(len(end_tags), 1)
        self.assertEqual(start_tags[0], ('START_TAG', 'tag'))
        self.assertEqual(end_tags[0], ('END_TAG', 'tag'))
        
        # 合并所有内容
        full_content = ''.join(e[1] for e in content_events)
        self.assertEqual(full_content, 'hello world')
    
    def test_whitespace_handling(self):
        """测试空白字符处理"""
        text = "<tag>  content with spaces  </tag>"
        events = self.parse_text(text)

        # 验证标签结构
        start_tags = [e for e in events if e[0] == 'START_TAG']
        end_tags = [e for e in events if e[0] == 'END_TAG']
        content_events = [e for e in events if e[0] == 'CONTENT']

        self.assertEqual(len(start_tags), 1)
        self.assertEqual(len(end_tags), 1)
        self.assertEqual(start_tags[0], ('START_TAG', 'tag'))
        self.assertEqual(end_tags[0], ('END_TAG', 'tag'))

        # 合并所有内容，应该保留空白
        full_content = ''.join(e[1] for e in content_events)
        self.assertEqual(full_content, '  content with spaces  ')
    
    def test_empty_tag(self):
        """测试空标签"""
        text = "<tag></tag>"
        events = self.parse_text(text)
        
        expected = [
            ('START_TAG', 'tag'),
            ('END_TAG', 'tag')
        ]
        
        self.assertEqual(events, expected)
    
    def test_complex_llm_output(self):
        """测试复杂的LLM输出格式"""
        text = """<UserInput><Content>test</Content></UserInput>
<Start><Reason>UserInput</Reason></Start>
<Thought><Content>thinking</Content></Thought>"""
        
        events = self.parse_text(text, chunk_size=5)
        
        # 验证标签顺序
        tag_events = [(e[0], e[1]) for e in events if e[0] in ['START_TAG', 'END_TAG']]
        
        expected_tags = [
            ('START_TAG', 'UserInput'),
            ('START_TAG', 'Content'),
            ('END_TAG', 'Content'),
            ('END_TAG', 'UserInput'),
            ('START_TAG', 'Start'),
            ('START_TAG', 'Reason'),
            ('END_TAG', 'Reason'),
            ('END_TAG', 'Start'),
            ('START_TAG', 'Thought'),
            ('START_TAG', 'Content'),
            ('END_TAG', 'Content'),
            ('END_TAG', 'Thought')
        ]
        
        self.assertEqual(tag_events, expected_tags)
    
    def test_incomplete_tag_handling(self):
        """测试不完整标签的处理"""
        # 测试标签被分割的情况
        parser = StreamingXMLParser()
        
        # 第一个chunk只包含标签的一部分
        events1 = list(parser.parse_chunk("<ta"))
        self.assertEqual(events1, [])  # 应该没有事件产生
        
        # 第二个chunk完成标签
        events2 = list(parser.parse_chunk("g>content</tag>"))
        
        expected = [
            ('START_TAG', 'tag'),
            ('CONTENT', 'content'),
            ('END_TAG', 'tag')
        ]
        
        self.assertEqual(events2, expected)
    
    def test_tag_name_extraction(self):
        """测试标签名提取"""
        test_cases = [
            ("<simple>", "simple"),
            ("<tag-with-dash>", "tag-with-dash"),
            ("<tag_with_underscore>", "tag_with_underscore"),
            ("<Tag123>", "Tag123"),
            ("</endtag>", "endtag"),
        ]
        
        for xml_text, expected_name in test_cases:
            parser = StreamingXMLParser()
            events = list(parser.parse_chunk(xml_text))
            
            if xml_text.startswith('</'):
                self.assertEqual(events[0], ('END_TAG', expected_name))
            else:
                self.assertEqual(events[0], ('START_TAG', expected_name))


class TestEventHandler(XMLEventHandler):
    """测试用的事件处理器"""
    
    def __init__(self):
        self.events = []
    
    def on_start_tag(self, tag_name: str):
        self.events.append(('START_TAG', tag_name))
    
    def on_end_tag(self, tag_name: str):
        self.events.append(('END_TAG', tag_name))
    
    def on_content(self, content: str):
        self.events.append(('CONTENT', content))


class TestXMLEventHandler(unittest.TestCase):
    """测试XMLEventHandler类"""
    
    def test_event_handler(self):
        """测试事件处理器"""
        from streaming_xml_parser import parse_stream
        
        handler = TestEventHandler()
        chunks = ["<tag>", "content", "</tag>"]
        
        parse_stream(chunks, handler)
        
        expected = [
            ('START_TAG', 'tag'),
            ('CONTENT', 'content'),
            ('END_TAG', 'tag')
        ]
        
        self.assertEqual(handler.events, expected)


if __name__ == '__main__':
    unittest.main()
