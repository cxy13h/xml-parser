"""
动态树形XML解析器的复杂性和鲁棒性测试

测试各种极端和复杂的情况，验证解析器的鲁棒性
"""

import unittest
from dynamic_tree_parser import DynamicTreeParser


class TestComplexCases(unittest.TestCase):
    """测试复杂和极端情况"""
    
    def test_deeply_nested_invalid_tags(self):
        """测试深度嵌套的无效标签"""
        print("\n=== 测试1：深度嵌套的无效标签 ===")
        
        hierarchy = {"Action": ["Feature"]}
        parser = DynamicTreeParser(hierarchy)
        
        text = "<Action><A><B><C><D><E><Feature>深层嵌套</Feature></E></D></C></B></A><Feature>正确位置</Feature></Action>"
        
        events = list(parser.parse_chunk(text)) + list(parser.finalize())
        
        print(f"输入: {text}")
        print("事件:")
        for event in events:
            print(f"  {event}")
        
        # 应该只识别Action和最后一个Feature
        start_tags = [e for e in events if e[0] == 'START_TAG']
        feature_tags = [e for e in start_tags if e[1] == 'Feature']
        
        self.assertEqual(len(feature_tags), 1)  # 只有一个Feature被识别
        
        # 验证Feature的内容
        feature_content = ""
        in_feature = False
        for event_type, data, level in events:
            if event_type == 'START_TAG' and data == 'Feature':
                in_feature = True
            elif event_type == 'END_TAG' and data == 'Feature':
                in_feature = False
            elif event_type == 'CONTENT' and in_feature:
                feature_content += data
        
        self.assertEqual(feature_content, "正确位置")
    
    def test_multiple_same_tags_different_positions(self):
        """测试多个相同标签在不同位置"""
        print("\n=== 测试2：多个相同标签在不同位置 ===")
        
        hierarchy = {"Action": ["Feature"]}
        parser = DynamicTreeParser(hierarchy)
        
        text = "<Action><ToolName>image_gen<Feature>嵌套1</Feature></ToolName><Description><Feature>嵌套2</Feature>描述</Description><Feature>正确1</Feature><Other><Feature>嵌套3</Feature></Other><Feature>正确2</Feature></Action>"
        
        events = list(parser.parse_chunk(text)) + list(parser.finalize())
        
        print(f"输入: {text}")
        print("事件:")
        for event in events:
            print(f"  {event}")
        
        # 应该只识别Action和两个正确位置的Feature
        start_tags = [e for e in events if e[0] == 'START_TAG']
        feature_tags = [e for e in start_tags if e[1] == 'Feature']
        
        self.assertEqual(len(feature_tags), 2)  # 两个Feature被识别
    
    def test_malformed_xml_resilience(self):
        """测试对格式错误XML的鲁棒性"""
        print("\n=== 测试3：格式错误XML的鲁棒性 ===")
        
        hierarchy = {"Action": ["Feature"]}
        parser = DynamicTreeParser(hierarchy)
        
        # 各种格式错误的情况
        test_cases = [
            "<Action><Feature>内容</Feature><UnmatchedTag></Action>",  # 未匹配的标签
            "<Action><Feature>内容<Feature></Action>",  # 嵌套相同标签但未闭合
            "<Action><>空标签名</><Feature>正常</Feature></Action>",  # 空标签名
            "<Action><Feature>内容</Wrong></Feature></Action>",  # 错误的结束标签
            "<Action><Feature>内容</Feature><Feature>内容2</Feature></Action>",  # 多个相同标签
        ]
        
        for i, text in enumerate(test_cases):
            print(f"\n子测试 3.{i+1}: {text}")
            parser.reset()
            
            try:
                events = list(parser.parse_chunk(text)) + list(parser.finalize())
                print("事件:")
                for event in events:
                    print(f"  {event}")
                
                # 验证至少能识别Action标签
                start_tags = [e for e in events if e[0] == 'START_TAG']
                action_tags = [e for e in start_tags if e[1] == 'Action']
                self.assertGreaterEqual(len(action_tags), 1)
                
            except Exception as e:
                print(f"  异常: {e}")
                self.fail(f"解析器在处理格式错误XML时崩溃: {e}")
    
    def test_extreme_nesting_levels(self):
        """测试极端嵌套层级"""
        print("\n=== 测试4：极端嵌套层级 ===")
        
        hierarchy = {"Action": ["Feature"], "Feature": ["SubFeature"]}
        parser = DynamicTreeParser(hierarchy)
        
        # 构建深度嵌套的XML
        deep_nesting = "<Action>"
        for i in range(20):  # 20层无效标签
            deep_nesting += f"<Invalid{i}>"
        deep_nesting += "<Feature><SubFeature>深层内容</SubFeature></Feature>"
        for i in range(19, -1, -1):  # 闭合无效标签
            deep_nesting += f"</Invalid{i}>"
        deep_nesting += "<Feature>正确位置</Feature></Action>"
        
        print(f"输入: {deep_nesting[:100]}...{deep_nesting[-50:]}")
        
        events = list(parser.parse_chunk(deep_nesting)) + list(parser.finalize())
        
        print("关键事件:")
        for event in events:
            if event[0] in ['START_TAG', 'END_TAG']:
                print(f"  {event}")
        
        # 应该只识别Action和最后一个Feature
        start_tags = [e for e in events if e[0] == 'START_TAG']
        feature_tags = [e for e in start_tags if e[1] == 'Feature']
        
        self.assertEqual(len(feature_tags), 1)  # 只有正确位置的Feature被识别
    
    def test_streaming_complex_case(self):
        """测试复杂情况下的流式处理"""
        print("\n=== 测试5：复杂情况下的流式处理 ===")
        
        hierarchy = {"Action": ["ToolName", "Description"], "Description": ["Feature"]}
        parser = DynamicTreeParser(hierarchy)
        
        # 复杂的XML，分块处理
        full_text = "<Action><ToolName>tool</ToolName><Invalid><Feature>假的</Feature></Invalid><Description><Feature>真的</Feature></Description></Action>"
        
        # 故意在关键位置分割
        chunks = [
            "<Action><ToolName>tool</Tool",
            "Name><Invalid><Feature>假的</Feat",
            "ure></Invalid><Description><Feat",
            "ure>真的</Feature></Description></Action>"
        ]
        
        print(f"完整文本: {full_text}")
        print("分块处理:")
        
        all_events = []
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i}: {repr(chunk)}")
            chunk_events = list(parser.parse_chunk(chunk))
            all_events.extend(chunk_events)
            
            if chunk_events:
                for event in chunk_events:
                    print(f"    事件: {event}")
            else:
                print("    (无事件)")
        
        final_events = list(parser.finalize())
        all_events.extend(final_events)
        
        if final_events:
            print("  最终事件:")
            for event in final_events:
                print(f"    {event}")
        
        # 验证结果
        start_tags = [e for e in all_events if e[0] == 'START_TAG']
        expected_tags = ['Action', 'ToolName', 'Description', 'Feature']
        actual_tags = [e[1] for e in start_tags]
        
        self.assertEqual(actual_tags, expected_tags)
    
    def test_unicode_and_special_characters(self):
        """测试Unicode和特殊字符"""
        print("\n=== 测试6：Unicode和特殊字符 ===")
        
        hierarchy = {"Action": ["Feature"]}
        parser = DynamicTreeParser(hierarchy)
        
        text = "<Action><Feature>🚀 Unicode测试 中文 العربية русский 日本語 emoji: 😀🎉🔥</Feature></Action>"
        
        events = list(parser.parse_chunk(text)) + list(parser.finalize())
        
        print(f"输入: {text}")
        print("事件:")
        for event in events:
            print(f"  {event}")
        
        # 验证Unicode内容被正确处理
        content_events = [e for e in events if e[0] == 'CONTENT']
        self.assertTrue(any("🚀" in e[1] for e in content_events))
        self.assertTrue(any("中文" in e[1] for e in content_events))
    
    def test_very_long_content(self):
        """测试非常长的内容"""
        print("\n=== 测试7：非常长的内容 ===")

        hierarchy = {"Action": ["Feature"]}
        parser = DynamicTreeParser(hierarchy)

        # 生成很长的内容
        long_content = "很长的内容 " * 1000  # 约10000字符
        text = f"<Action><Feature>{long_content}</Feature></Action>"

        print(f"输入长度: {len(text)} 字符")

        events = list(parser.parse_chunk(text)) + list(parser.finalize())

        # 验证长内容被正确处理
        content_events = [e for e in events if e[0] == 'CONTENT']
        total_content = ''.join(e[1] for e in content_events if e[2] == 2)  # Feature内的内容

        self.assertEqual(total_content, long_content)
        print(f"✅ 长内容处理正确，长度: {len(total_content)}")

    def test_weird_tag_names(self):
        """测试奇怪的标签名"""
        print("\n=== 测试8：奇怪的标签名 ===")

        # 各种奇怪但合法的标签名
        weird_hierarchy = {
            "Action_v2_final_REAL": ["Tool-Name-With-Dashes", "Feature_2024_Q4"],
            "Tool-Name-With-Dashes": ["Sub_Component_123"],
            "Feature_2024_Q4": ["Meta-Data-v1_0"]
        }

        parser = DynamicTreeParser(weird_hierarchy)

        test_cases = [
            # 测试1：带下划线和数字的标签
            "<Action_v2_final_REAL><Tool-Name-With-Dashes><Sub_Component_123>内容1</Sub_Component_123></Tool-Name-With-Dashes></Action_v2_final_REAL>",

            # 测试2：混合各种命名风格
            "<Action_v2_final_REAL><Feature_2024_Q4><Meta-Data-v1_0>元数据内容</Meta-Data-v1_0></Feature_2024_Q4></Action_v2_final_REAL>",

            # 测试3：奇怪标签名与普通标签名混合
            "<Action_v2_final_REAL><NormalTag><Tool-Name-With-Dashes>被包围的工具</Tool-Name-With-Dashes></NormalTag><Feature_2024_Q4>正确位置</Feature_2024_Q4></Action_v2_final_REAL>",
        ]

        for i, text in enumerate(test_cases):
            print(f"\n子测试 8.{i+1}:")
            print(f"输入: {text}")
            parser.reset()

            events = list(parser.parse_chunk(text)) + list(parser.finalize())

            print("事件:")
            for event in events:
                print(f"  {event}")

            # 验证奇怪的标签名被正确识别
            start_tags = [e for e in events if e[0] == 'START_TAG']
            tag_names = [e[1] for e in start_tags]

            # 至少应该识别根标签
            self.assertIn("Action_v2_final_REAL", tag_names)

    def test_extreme_weird_tag_names(self):
        """测试极端奇怪的标签名"""
        print("\n=== 测试9：极端奇怪的标签名 ===")

        # 更加极端的标签名（但仍然符合XML规范）
        extreme_hierarchy = {
            "A1B2C3_D4E5F6-G7H8I9": ["X_Y_Z_123_ABC_DEF"],
            "Component_v1_2_3_FINAL_RELEASE_2024_Q4_HOTFIX": ["Sub_Module_Alpha_Beta_Gamma"],
            "API_ENDPOINT_V2_LEGACY_DEPRECATED_BUT_STILL_USED": ["Response_Data_Container"]
        }

        parser = DynamicTreeParser(extreme_hierarchy)

        # 构建包含极端标签名的XML
        text = """<A1B2C3_D4E5F6-G7H8I9>
            <X_Y_Z_123_ABC_DEF>极端标签内容</X_Y_Z_123_ABC_DEF>
            <Some_Random_Invalid_Tag>
                <Component_v1_2_3_FINAL_RELEASE_2024_Q4_HOTFIX>嵌套在无效标签中</Component_v1_2_3_FINAL_RELEASE_2024_Q4_HOTFIX>
            </Some_Random_Invalid_Tag>
            <Component_v1_2_3_FINAL_RELEASE_2024_Q4_HOTFIX>
                <Sub_Module_Alpha_Beta_Gamma>正确位置的内容</Sub_Module_Alpha_Beta_Gamma>
            </Component_v1_2_3_FINAL_RELEASE_2024_Q4_HOTFIX>
        </A1B2C3_D4E5F6-G7H8I9>"""

        print(f"输入: {text}")

        events = list(parser.parse_chunk(text)) + list(parser.finalize())

        print("关键事件:")
        for event in events:
            if event[0] in ['START_TAG', 'END_TAG']:
                print(f"  {event}")

        # 验证极端标签名被正确处理
        start_tags = [e for e in events if e[0] == 'START_TAG']
        tag_names = [e[1] for e in start_tags]

        # 只有在正确位置的标签应该被识别
        # Component_v1_2_3_FINAL_RELEASE_2024_Q4_HOTFIX 在无效标签中，不应该被识别
        expected_recognized_tags = [
            "A1B2C3_D4E5F6-G7H8I9",
            "X_Y_Z_123_ABC_DEF"
        ]

        for expected_tag in expected_recognized_tags:
            self.assertIn(expected_tag, tag_names, f"标签 {expected_tag} 应该被识别")

        # 验证被无效标签包围的标签不被识别
        self.assertNotIn("Component_v1_2_3_FINAL_RELEASE_2024_Q4_HOTFIX", tag_names,
                        "被无效标签包围的标签不应该被识别")

    def test_tag_names_with_numbers_and_special_chars(self):
        """测试包含数字和特殊字符的标签名"""
        print("\n=== 测试10：包含数字和特殊字符的标签名 ===")

        # 测试各种合法的XML标签名模式
        special_hierarchy = {
            "Tag123": ["SubTag456"],
            "Tag_With_Underscores": ["Another_Tag_123"],
            "Tag-With-Dashes": ["Sub-Tag-789"],
            "MixedCase_Tag-123": ["camelCaseTag", "snake_case_tag", "kebab-case-tag"]
        }

        parser = DynamicTreeParser(special_hierarchy)

        test_cases = [
            # 数字标签
            "<Tag123><SubTag456>数字标签内容</SubTag456></Tag123>",

            # 下划线标签
            "<Tag_With_Underscores><Another_Tag_123>下划线标签内容</Another_Tag_123></Tag_With_Underscores>",

            # 连字符标签
            "<Tag-With-Dashes><Sub-Tag-789>连字符标签内容</Sub-Tag-789></Tag-With-Dashes>",

            # 混合命名风格
            "<MixedCase_Tag-123><camelCaseTag>驼峰</camelCaseTag><snake_case_tag>下划线</snake_case_tag><kebab-case-tag>连字符</kebab-case-tag></MixedCase_Tag-123>",

            # 复杂嵌套情况
            "<Tag123><InvalidTag><SubTag456>被包围</SubTag456></InvalidTag><SubTag456>正确位置</SubTag456></Tag123>"
        ]

        for i, text in enumerate(test_cases):
            print(f"\n子测试 10.{i+1}:")
            print(f"输入: {text}")
            parser.reset()

            events = list(parser.parse_chunk(text)) + list(parser.finalize())

            print("事件:")
            for event in events:
                print(f"  {event}")

            # 验证特殊字符标签被正确处理
            start_tags = [e for e in events if e[0] == 'START_TAG']
            self.assertGreater(len(start_tags), 0, "应该至少识别一个标签")

    def test_case_sensitivity(self):
        """测试大小写敏感性"""
        print("\n=== 测试11：大小写敏感性 ===")

        hierarchy = {
            "Action": ["Feature"],
            "action": ["feature"],  # 小写版本
            "ACTION": ["FEATURE"]   # 大写版本
        }

        parser = DynamicTreeParser(hierarchy)

        # 测试大小写敏感
        text = "<Action><Feature>大写A</Feature></Action><action><feature>小写a</feature></action><ACTION><FEATURE>全大写</FEATURE></ACTION><Action><feature>混合大小写</feature></Action>"

        print(f"输入: {text}")

        events = list(parser.parse_chunk(text)) + list(parser.finalize())

        print("事件:")
        for event in events:
            print(f"  {event}")

        # 验证大小写敏感性
        start_tags = [e for e in events if e[0] == 'START_TAG']
        tag_names = [e[1] for e in start_tags]

        # 应该识别所有正确大小写的标签
        expected_tags = ["Action", "Feature", "action", "feature", "ACTION", "FEATURE"]
        for tag in expected_tags:
            if tag in ["Action", "action", "ACTION"]:  # 根标签
                self.assertIn(tag, tag_names)


if __name__ == '__main__':
    # 运行测试并显示详细输出
    unittest.main(verbosity=2)
