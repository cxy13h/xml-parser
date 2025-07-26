"""
流式XML解析器主程序

演示如何使用StreamingXMLParser处理LLM的流式输出
"""

from streaming_xml_parser import StreamingXMLParser, XMLEventHandler


def main():
    print("🚀 流式XML解析器演示")
    print("=" * 50)

    # 示例LLM输出
    llm_output = """<UserInput><Content>现在给我画个五彩斑斓的黑</Content></UserInput>

<Start><Reason>UserInput</Reason></Start>

<Thought><Content>用户希望画一个五彩斑斓的黑色，我应该使用通义万相API来生成一张五彩斑斓的黑的图片。</Content></Thought>

<Action><ToolName>image_gen</ToolName></Action>

<End><Reason>ActionInput</Reason></End>"""

    # 创建解析器
    parser = StreamingXMLParser()

    # 模拟流式输入，每次处理10个字符
    chunk_size = 10
    print(f"📥 开始解析，chunk大小: {chunk_size}")
    print("-" * 50)

    for i in range(0, len(llm_output), chunk_size):
        chunk = llm_output[i:i + chunk_size]
        print(f"📦 处理chunk: {repr(chunk)}")

        # 解析chunk并处理事件
        for event_type, data in parser.parse_chunk(chunk):
            if event_type == 'START_TAG':
                print(f"  🏷️  开始标签: {data}")
            elif event_type == 'END_TAG':
                print(f"  🏁 结束标签: {data}")
            elif event_type == 'CONTENT':
                print(f"  📝 内容: {repr(data)}")

        print()

    # 处理剩余内容
    print("🔚 处理剩余内容:")
    for event_type, data in parser.finalize():
        if event_type == 'CONTENT':
            print(f"  📝 最终内容: {repr(data)}")

    print("\n✅ 解析完成!")


if __name__ == "__main__":
    main()
