# -*- coding: utf-8 -*-
from TINY_Intermediate_Code_Generation import Tiny_code


def input_tiny_code():
    str1 = input("请输入Tiny语句，空换行为结束输出：\n")
    code_str = str1
    while str1 != '':
        str1 = input()
        code_str += str1
    return code_str


if __name__ == "__main__":
    code = input_tiny_code()
    print(code)
    tiny_code = Tiny_code()
    tiny_code.set_String(code)  # 接收tiny代码
    tiny_code.stmt_sequence()  # 开始解析
    tiny_code.emit()  # 写入文件
    print(tiny_code.error_string)  # 打印错误信息
