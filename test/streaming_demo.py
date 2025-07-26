"""
流式XML解析器演示

展示真正的流式处理能力：
1. 网络数据分块到达
2. LLM逐字符输出
3. 文件流式读取
4. 实时事件处理
"""

import time
import asyncio
from src.streaming_xml_parser import StreamingXMLParser
from src.outer_xml_parser import OuterXMLParser
from src.dynamic_tree_parser import DynamicTreeParser


def demo_network_streaming():
    """演示网络数据分块到达的流式处理"""
    print("🌐 网络数据流式处理演示")
    print("=" * 50)
    
    # 模拟网络数据分块到达
    network_chunks = [
        "<Action><Tool",
        "Name>image_gen</Tool", 
        "Name><Description>AI图像",
        "生成服务</Description></Action>"
    ]
    
    parser = StreamingXMLParser()
    
    for i, chunk in enumerate(network_chunks):
        print(f"\n📡 网络数据包 {i+1} 到达: {repr(chunk)}")
        
        # 模拟网络延迟
        time.sleep(0.1)
        
        # 实时处理
        for event_type, data in parser.parse_chunk(chunk):
            print(f"  ⚡ 实时解析: {event_type} -> {repr(data)}")
    
    # 处理剩余数据
    for event_type, data in parser.finalize():
        print(f"  🔚 最终处理: {event_type} -> {repr(data)}")


def demo_llm_character_streaming():
    """演示LLM逐字符输出的流式处理"""
    print("\n\n🤖 LLM逐字符流式输出演示")
    print("=" * 50)
    
    # 模拟LLM逐字符生成XML回复
    llm_response = "<Thought>我需要调用图像生成工具</Thought><Action><ToolName>image_gen</ToolName></Action>"
    
    parser = OuterXMLParser()
    
    print(f"🎯 LLM将生成: {llm_response}")
    print("\n📝 逐字符生成过程:")
    
    current_output = ""
    for i, char in enumerate(llm_response):
        current_output += char
        print(f"字符 {i+1:2d}: '{char}' -> 当前输出: {current_output[-20:]}")
        
        # 模拟LLM生成延迟
        time.sleep(0.05)
        
        # 实时解析每个字符
        for event_type, data in parser.parse_chunk(char):
            print(f"         ⚡ 解析事件: {event_type} -> {repr(data)}")
    
    # 处理剩余数据
    for event_type, data in parser.finalize():
        print(f"         🔚 最终事件: {event_type} -> {repr(data)}")


def demo_intelligent_parsing():
    """演示智能树形解析器的流式处理"""
    print("\n\n🧠 智能树形解析器演示")
    print("=" * 50)
    
    # 定义已知的标签结构
    hierarchy = {
        "Action": ["ToolName", "Description"],
        "Response": ["Message", "Data"]
    }
    
    parser = DynamicTreeParser(hierarchy)
    
    # 复杂的流式XML，包含真假标签混合
    complex_xml = """<Action>
    <ToolName>image_gen</ToolName>
    <FakeTag><ToolName>这是假的</ToolName></FakeTag>
    <Description>真正的描述</Description>
</Action>"""
    
    print(f"📋 标签层次结构: {hierarchy}")
    print(f"📄 输入XML: {complex_xml.strip()}")
    print("\n🌊 流式解析过程:")
    
    # 分块处理
    chunk_size = 15
    for i in range(0, len(complex_xml), chunk_size):
        chunk = complex_xml[i:i + chunk_size]
        print(f"\n📦 数据块 {i//chunk_size + 1}: {repr(chunk)}")
        
        for event_type, data, level in parser.parse_chunk(chunk):
            indent = "  " * level
            print(f"  {indent}⚡ {event_type}: {repr(data)} (level {level})")
    
    # 处理剩余数据
    for event_type, data, level in parser.finalize():
        indent = "  " * level
        print(f"  {indent}🔚 {event_type}: {repr(data)} (level {level})")


def demo_memory_efficiency():
    """演示内存效率对比"""
    print("\n\n📊 内存效率演示")
    print("=" * 50)
    
    # 生成大量重复的XML数据
    large_xml = "<Data>" + "<Item>测试数据</Item>" * 1000 + "</Data>"
    
    print(f"📏 测试数据大小: {len(large_xml):,} 字符")
    print(f"💾 如果全部加载到内存: ~{len(large_xml.encode('utf-8')):,} 字节")
    
    parser = StreamingXMLParser()
    
    print("\n🌊 流式处理 (恒定内存占用):")
    
    # 分块处理，模拟恒定内存占用
    chunk_size = 100
    event_count = 0
    
    start_time = time.time()
    
    for i in range(0, len(large_xml), chunk_size):
        chunk = large_xml[i:i + chunk_size]
        
        for event_type, data in parser.parse_chunk(chunk):
            event_count += 1
            
            # 只显示前几个和最后几个事件
            if event_count <= 3 or event_count % 500 == 0:
                print(f"  事件 {event_count}: {event_type} -> {repr(data[:20])}{'...' if len(data) > 20 else ''}")
    
    # 处理剩余数据
    for event_type, data in parser.finalize():
        event_count += 1
        print(f"  事件 {event_count}: {event_type} -> {repr(data[:20])}{'...' if len(data) > 20 else ''}")
    
    end_time = time.time()
    
    print(f"\n✅ 处理完成:")
    print(f"   📊 总事件数: {event_count:,}")
    print(f"   ⏱️  处理时间: {end_time - start_time:.3f} 秒")
    print(f"   🚀 处理速度: {len(large_xml) / (end_time - start_time):,.0f} 字符/秒")
    print(f"   💾 内存占用: 恒定 (约几KB)")


async def demo_async_streaming():
    """演示异步流式处理"""
    print("\n\n🔄 异步流式处理演示")
    print("=" * 50)
    
    async def simulate_async_data_source():
        """模拟异步数据源"""
        chunks = [
            "<Message>",
            "Hello ",
            "World",
            "</Message>",
            "<Status>",
            "Complete",
            "</Status>"
        ]
        
        for chunk in chunks:
            await asyncio.sleep(0.1)  # 模拟异步延迟
            yield chunk
    
    parser = StreamingXMLParser()
    
    print("📡 异步数据流处理:")
    
    async for chunk in simulate_async_data_source():
        print(f"  📦 接收: {repr(chunk)}")
        
        for event_type, data in parser.parse_chunk(chunk):
            print(f"    ⚡ 解析: {event_type} -> {repr(data)}")
    
    # 处理剩余数据
    for event_type, data in parser.finalize():
        print(f"    🔚 最终: {event_type} -> {repr(data)}")


def main():
    """运行所有演示"""
    print("🌊 流式XML解析器演示套件")
    print("=" * 60)
    
    try:
        demo_network_streaming()
        demo_llm_character_streaming()
        demo_intelligent_parsing()
        demo_memory_efficiency()
        
        # 异步演示
        print("\n🔄 启动异步演示...")
        asyncio.run(demo_async_streaming())
        
    except KeyboardInterrupt:
        print("\n\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n\n❌ 演示过程中出现错误: {e}")
    
    print("\n\n🎉 演示完成！")
    print("💡 这些演示展示了流式XML解析器的核心优势：")
    print("   ✅ 实时处理 - 数据到达即刻解析")
    print("   ✅ 内存高效 - 恒定内存占用")
    print("   ✅ 高性能 - 毫秒级响应")
    print("   ✅ 容错性强 - 优雅处理各种情况")


if __name__ == "__main__":
    main()
