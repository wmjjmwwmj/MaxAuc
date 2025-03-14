import re

def extract_from_file(file_path: str, pattern) -> str:
    # 正则表达式，用于匹配 "4.2.2"
    # r字符串实际上和普通字符串类型是一样的，只是它的写法会让反斜杠 \ 直接作为字面意义，而不是转义字符。
    # pattern = r"\| settings_n \| ([\d\.]+) \|"
    
    try:
        # 打开文件并读取内容
        with open(file_path, 'r', encoding="utf-8") as file:
            # 遍历文件的每一行
            for line in file:
                line = line.strip()  # 去掉每行的空白字符和换行符
                # print(f"Reading line: {line}")  # 打印每一行，调试用
                # 查找匹配项
                # 查找匹配项
                match = re.search(pattern, line)
                if match:
                    # 如果匹配成功，返回版本号
                    return match.group(1)
        return "No match found"
    except FileNotFoundError:
        return f"File not found: {file_path}"