import re

# 需要测试的函数
def extract_from_file(file_path: str, pattern: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                match = re.search(pattern, line)
                if match:
                    return match.group(1)
        return "No match found"
    except FileNotFoundError:
        return f"File not found: {file_path}"

# 测试函数
def test_extract_from_file():
    # 创建测试文件内容
    test_file_path = "test_file.txt"
    test_content = """2024-12-22 19:12:49,017 - MainThread - INFO - +------------------+-------+
| Parameter        | Value |
+------------------+-------+
| settings_n       | 4.2.2 |
+------------------+-------+
| price_umax       | 1     |
+------------------+-------+
| price_alpha      | 1     |
+------------------+-------+
| bid_bmax         | 1     |
+------------------+-------+
| bid_beta         | 1     |
+------------------+-------+
| bid_lambda       | 1     |
+------------------+-------+
| seed_main        | 42    |
+------------------+-------+
| sample_interval  | 0.200 |
+------------------+-------+
| sample_frequency | 5     |
+------------------+-------+
| assign_bid_num   | 1     |
+------------------+-------+
"""
    # 将测试内容写入文件
    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write(test_content)

    # 定义正则表达式
    settings_n_pattern = r"\| settings_n\s*\| ([\d\.]+) \|"

    # 调用测试函数
    result = extract_from_file(test_file_path, settings_n_pattern)

    # 输出测试结果
    print(f"Extracted value: {result}")  # 应输出: 4.2.2

    # 验证结果
    assert result == "4.2.2", f"Test failed! Expected '4.2.2' but got '{result}'"
    print("Test passed!")

# 执行测试
if __name__ == "__main__":
    test_extract_from_file()
