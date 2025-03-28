import re


def read_cpp(filename):  # 读取Mini C源程序
    with open(filename, 'r') as file:
        content = file.read()
    return content


# 定义关键字符号等
key_word = {'else', 'if', 'int', 'float', 'double', 'return', 'void', 'do', 'while',
            'for', 'continue', 'break', 'main', 'cin', 'cout', 'char', 'printf', 'scanf'}
symbol = [
    '++', '+=', '--', '-=', '->', '*', '*=', '/=', '%', '%=', '>>', '<<', '<=', '>=', '==', '!=',
    ';', ',', '(', ')', '[', ']', '{', '}', '<', '>', '_', '+', '-', '/', '='
]
patterns = {
    '注释': r'//.*?$|/\*.*?\*/',  # .*?是贪婪匹配任意字符串
    '字符串': r'"(.*?)"',
    '数字': r'\d+(\.\d+)?[eE][+-]?\d+|0b[01]+|0o[0-7]+|0x[0-9a-fA-F]+|\d+.\d+|\d+',  # 数字类型以及匹配串模式
    '关键字': r'|'.join(map(re.escape, key_word)),  # 关键字要在标识符前因为会顺序识别
    '特殊符号': r'|'.join(map(re.escape, symbol)) + r'|#.*?$',  # 将列表中的每一个符号进行转义，确保它们能够被识别
    '标识符': r'[a-zA-Z_][a-zA-Z0-9_]*',
    '空格': r'\s+'
}


def get_token(code_content):
    tokens = []
    combined_pattern = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in patterns.items())  # 创建命名捕获组
    # print(combined_pattern)
    for match in re.finditer(combined_pattern, code_content, re.MULTILINE):
        token_type = match.lastgroup
        token_value = match.group(token_type)
        if token_type == '注释' or token_type == '空格':
            pass
        elif token_type == '数字':
            if token_value.startswith('0b'):
                tokens.append((token_value, '二进制数字'))
            elif token_value.startswith('0o'):
                tokens.append((token_value, '八进制数字'))
            elif token_value.startswith('0x'):
                tokens.append((token_value, '十六进制数字'))
            elif '.' in token_value or 'e' in token_value or 'E' in token_value:
                tokens.append((token_value, '浮点数'))
            else:
                tokens.append((token_value, '十进制整数'))
        else:
            tokens.append((token_value, token_type))
    return tokens


def main():
    cpp = read_cpp('Test.cpp')
    for c in get_token(cpp):
        print(f"{c[0]:<25} {c[1]}")


if __name__ == '__main__':
    main()
