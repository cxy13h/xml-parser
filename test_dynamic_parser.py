"""
动态树形XML解析器的单元测试
"""

import unittest
from dynamic_tree_parser import DynamicTreeParser, DynamicTreeEventHandler


class TestDynamicTreeParser(unittest.TestCase):
    """测试DynamicTreeParser类"""
    
    def test_case_1_missing_expected_child(self):
        """测试情况1：缺少预期的子标签"""
        # 解析器知道 Action -> ToolName，但文本中没有ToolName
        hierarchy = {"Action": ["ToolName"]}
        parser = DynamicTreeParser(hierarchy)
        
        text = "<Action><Description><Feature>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Feature></Description></Action>"
        
        events = []
        for event in parser.parse_chunk(text):
            events.append(event)
        for event in parser.finalize():
            events.append(event)
        
        print("测试情况1 - 缺少预期子标签:")
        print(f"输入: {text}")
        print("事件:")
        for event in events:
            print(f"  {event}")
        
        # 应该只识别Action标签，其余都是内容
        expected_structure = [
            ('START_TAG', 'Action', 0),
            ('CONTENT', '<Description><Feature>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Feature></Description>', 1),
            ('END_TAG', 'Action', 0)
        ]
        
        # 合并连续的CONTENT事件
        merged_events = self._merge_content_events(events)
        self.assertEqual(merged_events, expected_structure)
    
    def test_case_2_pseudo_tag_in_content(self):
        """测试情况2：内容中的伪标签"""
        # 解析器知道 Action -> Feature，但Feature出现在不正确的位置
        hierarchy = {"Action": ["Feature"]}
        parser = DynamicTreeParser(hierarchy)
        
        text = "<Action><ToolName>image_gen</ToolName><Description><Feature>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Feature></Description></Action>"
        
        events = []
        for event in parser.parse_chunk(text):
            events.append(event)
        for event in parser.finalize():
            events.append(event)
        
        print("\n测试情况2 - 内容中的伪标签:")
        print(f"输入: {text}")
        print("事件:")
        for event in events:
            print(f"  {event}")
        
        # 应该只识别Action标签，Feature不在正确位置所以是内容
        expected_structure = [
            ('START_TAG', 'Action', 0),
            ('CONTENT', '<ToolName>image_gen</ToolName><Description><Feature>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Feature></Description>', 1),
            ('END_TAG', 'Action', 0)
        ]
        
        merged_events = self._merge_content_events(events)
        self.assertEqual(merged_events, expected_structure)
    
    def test_case_3_correct_hierarchy(self):
        """测试情况3：正确的层次结构"""
        hierarchy = {
            "Action": ["ToolName", "Description"],
            "Description": ["Feature"]
        }
        parser = DynamicTreeParser(hierarchy)
        
        text = "<Action><ToolName>image_gen</ToolName><Description><Feature>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Feature></Description></Action>"
        
        events = []
        for event in parser.parse_chunk(text):
            events.append(event)
        for event in parser.finalize():
            events.append(event)
        
        print("\n测试情况3 - 正确的层次结构:")
        print(f"输入: {text}")
        print("事件:")
        for event in events:
            print(f"  {event}")
        
        # 应该识别所有正确位置的标签
        expected_structure = [
            ('START_TAG', 'Action', 0),
            ('START_TAG', 'ToolName', 1),
            ('CONTENT', 'image_gen', 2),
            ('END_TAG', 'ToolName', 1),
            ('START_TAG', 'Description', 1),
            ('START_TAG', 'Feature', 2),
            ('CONTENT', '通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL', 3),
            ('END_TAG', 'Feature', 2),
            ('END_TAG', 'Description', 1),
            ('END_TAG', 'Action', 0)
        ]
        
        merged_events = self._merge_content_events(events)
        self.assertEqual(merged_events, expected_structure)
    
    def test_case_4_partial_hierarchy(self):
        """测试情况4：部分层次结构"""
        hierarchy = {
            "Action": ["ToolName", "Description"]
        }
        parser = DynamicTreeParser(hierarchy)
        
        text = "<Action><ToolName>image_gen</ToolName><Description><Feature>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Feature></Description></Action>"
        
        events = []
        for event in parser.parse_chunk(text):
            events.append(event)
        for event in parser.finalize():
            events.append(event)
        
        print("\n测试情况4 - 部分层次结构:")
        print(f"输入: {text}")
        print("事件:")
        for event in events:
            print(f"  {event}")
        
        # 应该识别Action、ToolName、Description，但Feature不在层次结构中
        expected_structure = [
            ('START_TAG', 'Action', 0),
            ('START_TAG', 'ToolName', 1),
            ('CONTENT', 'image_gen', 2),
            ('END_TAG', 'ToolName', 1),
            ('START_TAG', 'Description', 1),
            ('CONTENT', '<Feature>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Feature>', 2),
            ('END_TAG', 'Description', 1),
            ('END_TAG', 'Action', 0)
        ]
        
        merged_events = self._merge_content_events(events)
        self.assertEqual(merged_events, expected_structure)
    
    def test_case_5_valid_tag_after_invalid_tags(self):
        """测试情况5：有效标签出现在无效标签之后"""
        hierarchy = {"Action": ["Feature"]}
        parser = DynamicTreeParser(hierarchy)

        text = "<Action><ToolName>image_gen</ToolName><Description>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Description><Feature>第三方MCP工具</Feature></Action>"

        events = []
        for event in parser.parse_chunk(text):
            events.append(event)
        for event in parser.finalize():
            events.append(event)

        print("\n测试情况5 - 有效标签出现在无效标签之后:")
        print(f"输入: {text}")
        print("事件:")
        for event in events:
            print(f"  {event}")

        # 验证标签结构
        start_tags = [e for e in events if e[0] == 'START_TAG']
        end_tags = [e for e in events if e[0] == 'END_TAG']
        content_events = [e for e in events if e[0] == 'CONTENT']

        # 应该识别Action和Feature两个标签
        self.assertEqual(len(start_tags), 2)
        self.assertEqual(len(end_tags), 2)
        self.assertEqual(start_tags[0], ('START_TAG', 'Action', 0))
        self.assertEqual(start_tags[1], ('START_TAG', 'Feature', 1))
        self.assertEqual(end_tags[0], ('END_TAG', 'Feature', 1))
        self.assertEqual(end_tags[1], ('END_TAG', 'Action', 0))

        # 验证内容分布
        action_content = ""
        feature_content = ""

        for event_type, data, level in events:
            if event_type == 'CONTENT':
                if level == 1:  # Action内的内容
                    action_content += data
                elif level == 2:  # Feature内的内容
                    feature_content += data

        expected_action_content = "<ToolName>image_gen</ToolName><Description>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Description>"
        expected_feature_content = "第三方MCP工具"

        self.assertEqual(action_content, expected_action_content)
        self.assertEqual(feature_content, expected_feature_content)

    def test_streaming_processing(self):
        """测试流式处理"""
        hierarchy = {"Action": ["ToolName", "Description"]}
        parser = DynamicTreeParser(hierarchy)
        
        # 分块输入
        chunks = [
            "<Action><Tool",
            "Name>image_gen</Tool",
            "Name><Description>服务描述</Desc",
            "ription></Action>"
        ]
        
        events = []
        for chunk in chunks:
            for event in parser.parse_chunk(chunk):
                events.append(event)
        for event in parser.finalize():
            events.append(event)
        
        print("\n测试流式处理:")
        print("分块输入:", chunks)
        print("事件:")
        for event in events:
            print(f"  {event}")
        
        # 验证流式处理结果正确
        expected_structure = [
            ('START_TAG', 'Action', 0),
            ('START_TAG', 'ToolName', 1),
            ('CONTENT', 'image_gen', 2),
            ('END_TAG', 'ToolName', 1),
            ('START_TAG', 'Description', 1),
            ('CONTENT', '服务描述', 2),
            ('END_TAG', 'Description', 1),
            ('END_TAG', 'Action', 0)
        ]
        
        merged_events = self._merge_content_events(events)
        self.assertEqual(merged_events, expected_structure)
    
    def _merge_content_events(self, events):
        """合并连续的CONTENT事件"""
        merged = []
        content_buffer = ""
        current_level = 0
        
        for event_type, data, level in events:
            if event_type == 'CONTENT':
                if not content_buffer:
                    current_level = level
                content_buffer += data
            else:
                if content_buffer:
                    merged.append(('CONTENT', content_buffer, current_level))
                    content_buffer = ""
                merged.append((event_type, data, level))
        
        if content_buffer:
            merged.append(('CONTENT', content_buffer, current_level))
        
        return merged


class TestEventHandler(DynamicTreeEventHandler):
    """测试用的事件处理器"""
    
    def __init__(self):
        self.events = []
    
    def on_start_tag(self, tag_name: str, level: int):
        self.events.append(('START_TAG', tag_name, level))
    
    def on_end_tag(self, tag_name: str, level: int):
        self.events.append(('END_TAG', tag_name, level))
    
    def on_content(self, content: str, level: int):
        self.events.append(('CONTENT', content, level))


class TestDynamicTreeEventHandler(unittest.TestCase):
    """测试DynamicTreeEventHandler类"""
    
    def test_event_handler(self):
        """测试事件处理器"""
        from dynamic_tree_parser import parse_dynamic_stream
        
        handler = TestEventHandler()
        hierarchy = {"Action": ["ToolName"]}
        chunks = ["<Action><ToolName>test</ToolName></Action>"]
        
        parse_dynamic_stream(chunks, hierarchy, handler)
        
        # 验证事件处理器正确工作
        self.assertTrue(len(handler.events) > 0)
        self.assertEqual(handler.events[0][0], 'START_TAG')
        self.assertEqual(handler.events[0][1], 'Action')


if __name__ == '__main__':
    unittest.main()
