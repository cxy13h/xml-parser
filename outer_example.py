"""
外层XML解析器使用示例

演示如何使用OuterXMLParser处理LLM的流式输出，只解析最外层标签
"""

import time
from outer_xml_parser import OuterXMLParser, OuterXMLEventHandler, parse_outer_stream


class LLMOuterHandler(OuterXMLEventHandler):
    """处理LLM输出的外层事件处理器"""
    
    def __init__(self):
        self.current_tag = None
        self.content_buffer = ""
        
    def on_start_tag(self, tag_name: str):
        print(f"🏷️  进入外层状态: {tag_name}")
        self.current_tag = tag_name
        self.content_buffer = ""
        
    def on_end_tag(self, tag_name: str):
        print(f"🏁 离开外层状态: {tag_name}")
        if self.content_buffer.strip():
            print(f"📝 {tag_name} 完整内容: {self.content_buffer.strip()}")
        self.current_tag = None
        self.content_buffer = ""
        
    def on_content(self, content: str):
        if content.strip():  # 只处理非空内容
            print(f"📄 内容块 ({self.current_tag or 'ROOT'}): {repr(content)}")
            self.content_buffer += content


def simulate_llm_outer_stream():
    """模拟LLM的流式输出"""
    llm_output = """<UserInput><Content>现在给我画个五彩斑斓的黑</Content></UserInput>

<Start><Reason>UserInput</Reason></Start>

<Thought><Content>用户希望画一个五彩斑斓的黑色，我应该使用通义万相API来生成一张五彩斑斓的黑的图片。</Content></Thought>

<Action><ToolName>image_gen</ToolName><Description>通义万相是一个图像生成服务，输入文本描述，可以得到图片的URL</Description></Action>

<ActionInput><ToolName>image_gen</ToolName><Arguments>{"query": "五彩斑斓的黑"}</Arguments></ActionInput>

<End><Reason>ActionInput</Reason></End>

<Observation><Content>Agent客户端调用Tool产生的"五彩斑斓的黑"图片url</Content></Observation>

<Start><Reason>Observation</Reason></Start>

<UserInteraction><Content>访问该url即可看到图片，请问您对这张图片满意吗？</Content></UserInteraction>

<End><Reason>UserInteraction</Reason></End>

<UserInput><Content>我很满意！</Content></UserInput>

<Start><Reason>UserInput</Reason></Start>

<Thought><Content>用户说很满意，说明我给出的图片非常符合用户的预期。</Content></Thought>

<FinalAnswer><Content>很高兴听到您说很满意，如果还有什么需要我帮助的欢迎向我询问！</Content></FinalAnswer>

<End><Reason>FinalAnswer</Reason></End>"""
    
    # 模拟流式输出，每次输出几个字符
    chunk_size = 20
    for i in range(0, len(llm_output), chunk_size):
        chunk = llm_output[i:i + chunk_size]
        yield chunk
        time.sleep(0.05)  # 模拟网络延迟


def example_basic_outer_usage():
    """基本外层解析使用示例"""
    print("=" * 60)
    print("外层XML解析器基本使用示例")
    print("=" * 60)
    
    parser = OuterXMLParser()
    
    for chunk in simulate_llm_outer_stream():
        print(f"📥 接收到chunk: {repr(chunk)}")
        
        for event_type, data in parser.parse_chunk(chunk):
            print(f"🎯 事件: {event_type} -> {repr(data)}")
        
        print("-" * 40)
    
    # 处理剩余内容
    for event_type, data in parser.finalize():
        print(f"🎯 最终事件: {event_type} -> {repr(data)}")


def example_with_outer_handler():
    """使用外层事件处理器的示例"""
    print("\n" + "=" * 60)
    print("使用外层事件处理器示例")
    print("=" * 60)
    
    handler = LLMOuterHandler()
    chunks = list(simulate_llm_outer_stream())  # 转换为列表以便重用
    
    parse_outer_stream(chunks, handler)


def example_comparison():
    """对比示例：展示外层解析器与完整解析器的区别"""
    print("\n" + "=" * 60)
    print("对比示例：外层解析器 vs 完整解析器")
    print("=" * 60)
    
    test_xml = "<Start><Reason>Observation</Reason></Start>"
    
    print("输入XML:", test_xml)
    print()
    
    # 外层解析器
    print("🔹 外层解析器结果:")
    outer_parser = OuterXMLParser()
    for event_type, data in outer_parser.parse_chunk(test_xml):
        print(f"  {event_type}: {repr(data)}")
    for event_type, data in outer_parser.finalize():
        print(f"  {event_type}: {repr(data)}")
    
    print()
    
    # 完整解析器（用于对比）
    print("🔹 完整解析器结果:")
    from streaming_xml_parser import StreamingXMLParser
    full_parser = StreamingXMLParser()
    for event_type, data in full_parser.parse_chunk(test_xml):
        print(f"  {event_type}: {repr(data)}")
    for event_type, data in full_parser.finalize():
        print(f"  {event_type}: {repr(data)}")


def example_real_time_outer_processing():
    """实时外层处理示例"""
    print("\n" + "=" * 60)
    print("实时外层处理示例")
    print("=" * 60)
    
    class RealTimeOuterHandler(OuterXMLEventHandler):
        def __init__(self):
            self.outer_tag_stack = []
            
        def on_start_tag(self, tag_name: str):
            self.outer_tag_stack.append(tag_name)
            indent = "  " * (len(self.outer_tag_stack) - 1)
            print(f"{indent}▶️ 开始外层标签: {tag_name}")
            
        def on_end_tag(self, tag_name: str):
            if self.outer_tag_stack and self.outer_tag_stack[-1] == tag_name:
                self.outer_tag_stack.pop()
            indent = "  " * len(self.outer_tag_stack)
            print(f"{indent}◀️ 结束外层标签: {tag_name}")
            
        def on_content(self, content: str):
            if content.strip():
                indent = "  " * len(self.outer_tag_stack)
                # 只显示内容的前80个字符
                display_content = content.strip()[:80]
                if len(content.strip()) > 80:
                    display_content += "..."
                print(f"{indent}📝 {display_content}")
    
    handler = RealTimeOuterHandler()
    parser = OuterXMLParser()
    
    print("开始实时外层解析...")
    for chunk in simulate_llm_outer_stream():
        for event_type, data in parser.parse_chunk(chunk):
            handler.handle_event(event_type, data)
    
    # 处理剩余内容
    for event_type, data in parser.finalize():
        handler.handle_event(event_type, data)


def example_practical_usage():
    """实际使用场景示例"""
    print("\n" + "=" * 60)
    print("实际使用场景示例 - 提取特定外层标签的内容")
    print("=" * 60)
    
    class ContentExtractor(OuterXMLEventHandler):
        def __init__(self, target_tags):
            self.target_tags = set(target_tags)
            self.extracted_content = {}
            self.current_tag = None
            self.current_content = ""
            
        def on_start_tag(self, tag_name: str):
            if tag_name in self.target_tags:
                self.current_tag = tag_name
                self.current_content = ""
                
        def on_end_tag(self, tag_name: str):
            if tag_name == self.current_tag:
                if tag_name not in self.extracted_content:
                    self.extracted_content[tag_name] = []
                self.extracted_content[tag_name].append(self.current_content.strip())
                self.current_tag = None
                self.current_content = ""
                
        def on_content(self, content: str):
            if self.current_tag:
                self.current_content += content
    
    # 提取特定标签的内容
    extractor = ContentExtractor(['Thought', 'Action', 'UserInput'])
    chunks = list(simulate_llm_outer_stream())
    
    parse_outer_stream(chunks, extractor)
    
    print("提取的内容:")
    for tag_name, contents in extractor.extracted_content.items():
        print(f"\n🏷️ {tag_name}:")
        for i, content in enumerate(contents, 1):
            print(f"  {i}. {content[:100]}{'...' if len(content) > 100 else ''}")


if __name__ == "__main__":
    # 运行所有示例
    example_basic_outer_usage()
    example_with_outer_handler()
    example_comparison()
    example_real_time_outer_processing()
    example_practical_usage()
