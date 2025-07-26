"""
流式XML解析器使用示例

演示如何使用StreamingXMLParser处理LLM的流式输出
"""

from src.streaming_xml_parser import StreamingXMLParser, XMLEventHandler, parse_stream


class LLMOutputHandler(XMLEventHandler):
    """处理LLM输出的事件处理器"""
    
    def __init__(self):
        self.current_state = None
        self.content_buffer = ""
        
    def on_start_tag(self, tag_name: str):
        print(f"🏷️  进入状态: {tag_name}")
        self.current_state = tag_name
        self.content_buffer = ""
        
    def on_end_tag(self, tag_name: str):
        print(f"🏁 离开状态: {tag_name}")
        if self.content_buffer.strip():
            print(f"📝 {tag_name} 完整内容: {self.content_buffer.strip()}")
        self.current_state = None
        self.content_buffer = ""
        
    def on_content(self, content: str):
        if content.strip():  # 只处理非空内容
            print(f"📄 内容块 ({self.current_state or 'ROOT'}): {repr(content)}")
            self.content_buffer += content


def simulate_llm_stream():
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
    chunk_size = 5
    for i in range(0, len(llm_output), chunk_size):
        chunk = llm_output[i:i + chunk_size]
        yield chunk
        # time.sleep(0.1)  # 模拟网络延迟


def example_basic_usage():
    parser = StreamingXMLParser()
    
    for chunk in simulate_llm_stream():
        print(f"📥 接收到chunk: {repr(chunk)}")
        
        for event_type, data in parser.parse_chunk(chunk):
            print(f"🎯 事件: {event_type} -> {repr(data)}")
        
        print("-" * 40)
    
    # 处理剩余内容
    for event_type, data in parser.finalize():
        print(f"🎯 最终事件: {event_type} -> {repr(data)}")


def example_with_handler():
    """使用事件处理器的示例"""
    print("\n" + "=" * 60)
    print("使用事件处理器示例")
    print("=" * 60)
    
    handler = LLMOutputHandler()
    chunks = list(simulate_llm_stream())  # 转换为列表以便重用
    
    parse_stream(chunks, handler)


def example_real_time_processing():
    """实时处理示例"""
    print("\n" + "=" * 60)
    print("实时处理示例 - 模拟真实的流式场景")
    print("=" * 60)
    
    class RealTimeHandler(XMLEventHandler):
        def __init__(self):
            self.tag_stack = []
            
        def on_start_tag(self, tag_name: str):
            self.tag_stack.append(tag_name)
            indent = "  " * (len(self.tag_stack) - 1)
            print(f"{indent}▶️ 开始 {tag_name}")
            
        def on_end_tag(self, tag_name: str):
            if self.tag_stack and self.tag_stack[-1] == tag_name:
                self.tag_stack.pop()
            indent = "  " * len(self.tag_stack)
            print(f"{indent}◀️ 结束 {tag_name}")
            
        def on_content(self, content: str):
            if content.strip():
                indent = "  " * len(self.tag_stack)
                # 只显示内容的前50个字符
                display_content = content.strip()[:50]
                if len(content.strip()) > 50:
                    display_content += "..."
                print(f"{indent}📝 {display_content}")
    
    handler = RealTimeHandler()
    parser = StreamingXMLParser()
    
    print("开始实时解析...")
    for chunk in simulate_llm_stream():
        for event_type, data in parser.parse_chunk(chunk):
            handler.handle_event(event_type, data)
    
    # 处理剩余内容
    for event_type, data in parser.finalize():
        handler.handle_event(event_type, data)


if __name__ == "__main__":
    # 运行所有示例
    # example_basic_usage()
    # example_with_handler()
    example_real_time_processing()
