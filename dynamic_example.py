"""
动态树形XML解析器使用示例

演示如何使用DynamicTreeParser根据预定义的标签层次结构
智能识别真正的标签和内容
"""

import time
from dynamic_tree_parser import DynamicTreeParser, DynamicTreeEventHandler, parse_dynamic_stream


class DynamicTreeHandler(DynamicTreeEventHandler):
    """动态树形解析器事件处理器"""
    
    def __init__(self):
        self.tag_stack = []
        self.content_buffer = {}
        
    def on_start_tag(self, tag_name: str, level: int):
        indent = "  " * level
        print(f"{indent}🏷️  开始标签: {tag_name} (level {level})")
        self.tag_stack.append((tag_name, level))
        self.content_buffer[tag_name] = ""
        
    def on_end_tag(self, tag_name: str, level: int):
        indent = "  " * level
        print(f"{indent}🏁 结束标签: {tag_name} (level {level})")
        if self.tag_stack and self.tag_stack[-1][0] == tag_name:
            self.tag_stack.pop()
        
        if tag_name in self.content_buffer and self.content_buffer[tag_name].strip():
            print(f"{indent}📝 {tag_name} 内容: {self.content_buffer[tag_name].strip()}")
        
    def on_content(self, content: str, level: int):
        if content.strip():
            indent = "  " * level
            print(f"{indent}📄 内容 (level {level}): {repr(content)}")
            
            # 记录到当前标签的内容缓冲区
            if self.tag_stack:
                current_tag = self.tag_stack[-1][0]
                self.content_buffer[current_tag] += content


def example_basic_streaming():
    """基本流式处理示例"""
    print("=" * 80)
    print("动态树形解析器基本流式处理示例")
    print("=" * 80)

    hierarchy = {"Action": ["ToolName", "Description"]}
    parser = DynamicTreeParser(hierarchy)

    print("标签层次结构:")
    print(parser.get_tag_hierarchy_info())

    # 模拟流式输入
    test_xml = "<Action><ToolName>image_gen</ToolName><Description>服务描述</Description></Action>"
    chunks = []
    chunk_size = 10

    for i in range(0, len(test_xml), chunk_size):
        chunks.append(test_xml[i:i + chunk_size])

    print(f"完整输入: {test_xml}")
    print(f"分块大小: {chunk_size}")
    print()

    for i, chunk in enumerate(chunks):
        print(f"📥 接收到chunk {i}: {repr(chunk)}")

        for event_type, data, level in parser.parse_chunk(chunk):
            print(f"🎯 事件: {event_type} -> {repr(data)} (level {level})")

        print("-" * 40)

    # 处理剩余内容
    for event_type, data, level in parser.finalize():
        print(f"🎯 最终事件: {event_type} -> {repr(data)} (level {level})")


def example_case_1():
    """示例1：缺少预期的子标签"""
    print("=" * 80)
    print("示例1：缺少预期的子标签")
    print("=" * 80)
    
    # 解析器知道 Action -> ToolName，但文本中没有ToolName
    hierarchy = {"Action": ["ToolName"]}
    parser = DynamicTreeParser(hierarchy)
    
    print("标签层次结构:")
    print(parser.get_tag_hierarchy_info())
    
    text = "<Action><Description><Feature>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Feature></Description></Action>"
    print(f"输入文本: {text}")
    print("\n解析结果:")
    
    handler = DynamicTreeHandler()
    for event_type, data, level in parser.parse_chunk(text):
        handler.handle_event(event_type, data, level)
    for event_type, data, level in parser.finalize():
        handler.handle_event(event_type, data, level)
    
    print("\n结论: 只识别了Action标签，Description和Feature被当作内容处理")


def example_case_2():
    """示例2：内容中的伪标签"""
    print("\n" + "=" * 80)
    print("示例2：内容中的伪标签")
    print("=" * 80)
    
    # 解析器知道 Action -> Feature，但Feature出现在错误位置
    hierarchy = {"Action": ["Feature"]}
    parser = DynamicTreeParser(hierarchy)
    
    print("标签层次结构:")
    print(parser.get_tag_hierarchy_info())
    
    text = "<Action><ToolName>image_gen</ToolName><Description><Feature>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Feature></Description></Action>"
    print(f"输入文本: {text}")
    print("\n解析结果:")
    
    handler = DynamicTreeHandler()
    for event_type, data, level in parser.parse_chunk(text):
        handler.handle_event(event_type, data, level)
    for event_type, data, level in parser.finalize():
        handler.handle_event(event_type, data, level)
    
    print("\n结论: 只识别了Action标签，Feature虽然在层次结构中，但位置不对，被当作内容处理")


def example_case_3():
    """示例3：正确的层次结构"""
    print("\n" + "=" * 80)
    print("示例3：正确的层次结构")
    print("=" * 80)
    
    # 完整的层次结构
    hierarchy = {
        "Action": ["ToolName", "Description"],
        "Description": ["Feature"]
    }
    parser = DynamicTreeParser(hierarchy)
    
    print("标签层次结构:")
    print(parser.get_tag_hierarchy_info())
    
    text = "<Action><ToolName>image_gen</ToolName><Description><Feature>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Feature></Description></Action>"
    print(f"输入文本: {text}")
    print("\n解析结果:")
    
    handler = DynamicTreeHandler()
    for event_type, data, level in parser.parse_chunk(text):
        handler.handle_event(event_type, data, level)
    for event_type, data, level in parser.finalize():
        handler.handle_event(event_type, data, level)
    
    print("\n结论: 所有标签都在正确位置，全部被识别")


def example_case_4():
    """示例4：复杂的流式处理"""
    print("\n" + "=" * 80)
    print("示例4：复杂的流式处理")
    print("=" * 80)

    hierarchy = {
        "Action": ["ToolName", "Description"],
        "Description": ["Feature", "Usage"]
    }
    parser = DynamicTreeParser(hierarchy)

    print("标签层次结构:")
    print(parser.get_tag_hierarchy_info())

    # 模拟流式输入
    chunks = [
        "<Action><Tool",
        "Name>image_gen</Tool",
        "Name><Description><Feature>图像生成</Feature><Usage>输入文本描述</Usage><Other>其他信息</Other></Desc",
        "ription></Action>"
    ]

    print("流式输入chunks:")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i}: {repr(chunk)}")

    print("\n流式解析过程:")
    for i, chunk in enumerate(chunks):
        print(f"📥 接收到chunk {i}: {repr(chunk)}")

        events_in_chunk = []
        for event_type, data, level in parser.parse_chunk(chunk):
            events_in_chunk.append((event_type, data, level))

        if events_in_chunk:
            for event_type, data, level in events_in_chunk:
                indent = "  " * level
                if event_type == 'START_TAG':
                    print(f"  🎯 事件: START_TAG -> {repr(data)} (level {level})")
                elif event_type == 'END_TAG':
                    print(f"  🎯 事件: END_TAG -> {repr(data)} (level {level})")
                elif event_type == 'CONTENT':
                    print(f"  🎯 事件: CONTENT -> {repr(data)} (level {level})")
        else:
            print("  (本chunk未产生事件)")

        print("-" * 40)

    # 处理剩余内容
    final_events = list(parser.finalize())
    if final_events:
        print("🔚 处理剩余内容:")
        for event_type, data, level in final_events:
            print(f"  🎯 最终事件: {event_type} -> {repr(data)} (level {level})")

    print("\n结论: Feature和Usage被识别为标签，Other不在层次结构中被当作内容")


def example_case_5():
    """示例5：多根节点的层次结构"""
    print("\n" + "=" * 80)
    print("示例5：多根节点的层次结构")
    print("=" * 80)
    
    hierarchy = {
        "Action": ["ToolName"],
        "Thought": ["Content"],
        "Response": ["Message"]
    }
    parser = DynamicTreeParser(hierarchy)
    
    print("标签层次结构:")
    print(parser.get_tag_hierarchy_info())
    
    text = "<Thought><Content>我需要调用工具</Content></Thought><Action><ToolName>image_gen</ToolName></Action><Response><Message>完成</Message></Response>"
    print(f"输入文本: {text}")
    print("\n解析结果:")
    
    handler = DynamicTreeHandler()
    for event_type, data, level in parser.parse_chunk(text):
        handler.handle_event(event_type, data, level)
    for event_type, data, level in parser.finalize():
        handler.handle_event(event_type, data, level)
    
    print("\n结论: 多个根节点都能正确识别")


def example_streaming_detailed():
    """示例：详细的流式处理演示"""
    print("\n" + "=" * 80)
    print("详细流式处理演示")
    print("=" * 80)

    hierarchy = {"Action": ["ToolName", "Description"]}
    parser = DynamicTreeParser(hierarchy)

    print("标签层次结构:")
    print(parser.get_tag_hierarchy_info())

    # 模拟LLM的流式输出
    llm_output = "<Action><ToolName>image_gen</ToolName><Description>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Description></Action>"

    print(f"完整输入: {llm_output}")
    print()

    # 分块处理，每次15个字符
    chunk_size = 15
    print(f"📥 开始流式解析，chunk大小: {chunk_size}")
    print("-" * 50)

    for i in range(0, len(llm_output), chunk_size):
        chunk = llm_output[i:i + chunk_size]
        print(f"📦 处理chunk {i//chunk_size}: {repr(chunk)}")

        # 解析chunk并处理事件
        events_in_chunk = []
        for event_type, data, level in parser.parse_chunk(chunk):
            events_in_chunk.append((event_type, data, level))

        if events_in_chunk:
            for event_type, data, level in events_in_chunk:
                if event_type == 'START_TAG':
                    print(f"  🏷️  开始标签: {data} (level {level})")
                elif event_type == 'END_TAG':
                    print(f"  🏁 结束标签: {data} (level {level})")
                elif event_type == 'CONTENT':
                    print(f"  📝 内容: {repr(data)} (level {level})")
        else:
            print("  (本chunk未产生事件，等待更多数据)")

        print()

    # 处理剩余内容
    final_events = list(parser.finalize())
    if final_events:
        print("🔚 处理剩余内容:")
        for event_type, data, level in final_events:
            if event_type == 'CONTENT':
                print(f"  📝 最终内容: {repr(data)} (level {level})")

    print("✅ 流式解析完成!")


def example_robustness_test():
    """示例6：鲁棒性测试"""
    print("\n" + "=" * 80)
    print("示例6：鲁棒性测试")
    print("=" * 80)
    
    hierarchy = {"Action": ["ToolName", "Description"]}
    parser = DynamicTreeParser(hierarchy)
    
    print("标签层次结构:")
    print(parser.get_tag_hierarchy_info())
    
    # 测试各种边界情况
    test_cases = [
        "<Action></Action>",  # 空标签
        "<Action>纯文本内容</Action>",  # 只有文本
        "<Action><UnknownTag>未知标签</UnknownTag></Action>",  # 未知标签
        "<Action><ToolName></ToolName></Action>",  # 空子标签
        "<NotInHierarchy>不在层次结构中</NotInHierarchy>",  # 根级别未知标签
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {text}")
        print("解析结果:")
        
        parser.reset()  # 重置解析器
        handler = DynamicTreeHandler()
        
        for event_type, data, level in parser.parse_chunk(text):
            handler.handle_event(event_type, data, level)
        for event_type, data, level in parser.finalize():
            handler.handle_event(event_type, data, level)


if __name__ == "__main__":
    example_basic_streaming()
    example_case_1()
    example_case_2()
    example_case_3()
    example_case_4()
    example_case_5()
    example_streaming_detailed()
    example_robustness_test()
