# -*- coding: utf-8 -*-
import re


class TreeNode:
    def __init__(self, the_type='', data=''):
        self.type = the_type  # 结点类型
        self.data = data  # 节点的值
        self.child = []  # 孩子节点
        self.sibling = []  # 兄弟节点


class Tiny:
    def __init__(self):
        self.my_string = ''
        self.error_string = ''
        self.index = 0
        self.root = None
        self.sign = {'(', ')', ';', '<', '>', '+', '-', '*', '/', '%', ':', '=', '^', '|', '&', '#'}
        self.end_set = {'endif', 'enddo'}
        self.end_stack = list()  # 用于存放终止标志的栈

    def set_String(self, temp_string):
        ts = ''
        # 去除注释: {...}
        flag = False
        for i in range(len(temp_string)):
            if temp_string[i] == "{":  # 如果是注释
                flag = True
            if not flag:
                ts += temp_string[i]
            if temp_string[i] == "}":
                flag = False
        if flag:
            self.error_string = "input error\n"  # 输入的语法有误
            return
        ts = re.sub(r'\s+', ' ', ts)  # 去除多余的空格
        self.my_string = ts

    def next_Token(self):
        temp_string = ''
        if self.my_string[self.index] == ' ':  # 以空格作为分界
            self.index += 1
        while self.index < len(self.my_string) and self.my_string[self.index] not in self.sign and self.my_string[self.index] != ' ':
            temp_string += self.my_string[self.index]
            self.index += 1
        return temp_string

    def match(self, match_s, temp_s):
        if match_s != temp_s:
            self.error_string += "error: unexpected token: "+temp_s+'\n'
        return

    def program(self):
        if self.error_string != '':
            return
        else:
            self.root = TreeNode('Program', 'Program')
            self.root.child.append(self.stmt_sequence())

    def end_missing(self):  # end部分缺失
        if not self.end_stack == []:
            new_list = self.end_stack
            new_list.reverse()
            for e in new_list:
                self.error_string += f"error: Missing '{e}' to close the '{e[3:]}'\n" if e == 'endif' else f"error: Missing '{e}' to close the loop statement\n"

    def stmt_sequence(self):
        this_node = self.statement()
        if this_node is not None:
            while self.my_string[self.index] == ';' and self.index != len(self.my_string) - 1:
                self.index += 1
                sibling = self.statement()
                if sibling is not None:
                    this_node.sibling.append(sibling)
                else:
                    break
                if self.my_string[self.index] == " ":
                    self.index += 1
        return this_node

    def statement(self):
        token = self.next_Token()
        if token in self.end_set:  # 是否为终止符号
            expected_end = self.end_stack.pop()
            self.match(expected_end, token)
            return None
        if token == 'if':
            self.end_stack.append('endif')
            self.match('if', token)
            this_node = self.if_stmt()
            this_node.data = 'If'
            this_node.type = 'If'
        elif token == 'else':
            # print('else')
            self.index -= 4
            # print(self.my_string[self.index])
            return None
        elif token == 'repeat':
            self.end_stack.append('until')
            self.match('repeat', token)
            this_node = self.repeat_stmt()
            this_node.data = 'Repeat'
            this_node.type = "Repeat"
        elif token == 'until':
            end = self.end_stack.pop()
            self.match(end, token)
            self.index -= 5
            return None

        elif token == 'read':
            self.match('read', token)
            this_node = self.read_stmt()
            this_node.type = "Read"
        elif token == 'write':
            self.match('write', token)
            this_node = self.write_stmt()
            this_node.type = 'Write'
        elif token == 'while':
            self.end_stack.append('enddo')
            self.match('while', token)
            this_node = self.while_stmt()
            this_node.type = 'While'
            this_node.data = 'While'
        elif token == 'for':
            self.end_stack.append('enddo')
            self.match('for', token)
            this_node = self.for_stmt()
            this_node.type = 'For'
            this_node.data = 'For'
        else:
            this_node = self.assign_stmt_or_ID_stmt()
            new_node = TreeNode()
            new_node.data = token
            new_node.type = 'Id'
            this_node.child.append(new_node)
            this_node.child.reverse()

        return this_node

    def if_stmt(self):
        this_node = TreeNode()
        this_node.data = 'If'
        this_node.type = 'If'
        if self.my_string[self.index] == ' ':
            self.index += 1
        token = self.my_string[self.index]
        self.index += 1
        self.match('(', token)  # 匹配左括号(
        this_node.child.append(self.exp1())  # 匹配exp
        if self.my_string[self.index] == ' ':
            self.index += 1
        token = self.my_string[self.index]
        self.index += 1
        self.match(')', token)  # 匹配左括号(
        token = self.next_Token()
        self.match('then', token)  # 匹配then
        this_node.child.append(self.stmt_sequence())
        if self.my_string[self.index] == ' ':
            self.index += 1
        if self.my_string[self.index] == "e":
            token = self.next_Token()
            self.match('else', token)  # 匹配else
            else_node = TreeNode('Else', 'Else')
            else_node.child.append(self.stmt_sequence())
            this_node.sibling.append(else_node)

        return this_node

    def while_stmt(self):
        this_node = TreeNode()
        this_node.data = 'While'
        this_node.type = 'While'
        if self.my_string[self.index] == ' ':
            self.index += 1
        token = self.my_string[self.index]
        self.index += 1
        self.match('(', token)  # 匹配左括号(
        this_node.child.append(self.exp1())  # 匹配exp
        if self.my_string[self.index] == ' ':
            self.index += 1
        token = self.my_string[self.index]
        self.index += 1
        self.match(')', token)  # 匹配左括号(
        token = self.next_Token()
        self.match('do', token)  # 匹配do
        this_node.child.append(self.stmt_sequence())

        return this_node

    def for_stmt(self):
        this_node = TreeNode()
        this_node.data = 'For'
        this_node.type = 'For'
        id_token = self.next_Token()  # 匹配循环变量
        if self.my_string[self.index] == ' ':
            self.index += 1
        token = self.my_string[self.index: self.index+2]  # 匹配:=
        self.index += 2
        self.match(':=', token)
        ID_Assign_node = TreeNode('ID_Assign ' + token, '')  # :=的结点
        circle_ID = TreeNode('Cycle_Id', id_token)
        ID_Assign_node.child.append(circle_ID)
        circle_ID.child.append(self.simple_exp())
        token = self.next_Token()  # 取to/downto
        if token == 'to':
            self.match('to', token)
        else:
            self.match('downto', token)
        circle_ID.child.append(TreeNode(token.upper(), token.upper()))  # TO/DOWNTO
        circle_ID.child.append(self.simple_exp())
        this_node.child.append(ID_Assign_node)
        token = self.next_Token()
        self.match('do', token)  # 匹配do
        this_node.child.append(self.stmt_sequence())

        return this_node

    def read_stmt(self):  # 匹配read
        this_node = TreeNode()
        this_node.type = "Read"
        # 匹配identifier
        token = self.next_Token()
        this_node.data = token
        return this_node

    def write_stmt(self):  # 匹配write
        this_node = TreeNode()
        this_node.data = "Write"
        this_node.data = "Write"
        this_node.child.append(self.exp())
        return this_node

    def repeat_stmt(self):  # 重复部分
        this_node = TreeNode()
        this_node.data = "Repeat"
        this_node.type = "Repeat"
        this_node.child.append(self.stmt_sequence())
        token = self.next_Token()
        self.match('until', token)
        new_node = TreeNode('UNTIL', 'UNTIL')
        new_node.child.append(self.exp1())
        this_node.child.append(new_node)
        return this_node

    def assign_stmt_or_ID_stmt(self):  # 判断符号后面是-=、+=还是:=
        this_node = TreeNode()
        if self.my_string[self.index] == " ":
            self.index += 1
        # 匹配+=或是-=
        if self.my_string[self.index] == '+' or self.my_string[self.index] == '-':
            token = ''
            if self.my_string[self.index] == '+':
                token += self.my_string[self.index: self.index+2]
                self.index += 2
                self.match('+=', token)
            else:
                token += self.my_string[self.index: self.index+2]
                self.index += 2
                self.match('-=', token)
            this_node.type = 'Assign ' + token
            this_node.child.append(self.exp1())
        else:  # 是:=
            token = ''
            token += self.my_string[self.index:self.index+2]
            self.index += 2
            self.match(':=', token)
            this_node.type = "ID_Assign "+token
            this_node.child.append(self.exp())

        return this_node

    def exp1(self):  # 匹配or
        this_node = self.exp2()
        if self.my_string[self.index] == ' ':
            self.index += 1
        while self.my_string[self.index] == "o":
            token = self.next_Token()
            self.match('or', token)
            new_node = TreeNode()
            new_node.data = 'Or'
            new_node.type = 'OP'
            new_node.child.append(this_node)
            new_node.child.append(self.exp1())
            this_node = new_node

        return this_node

    def exp2(self):  # 匹配and
        this_node = self.exp()
        if self.my_string[self.index] == " ":
            self.index += 1
        while self.my_string[self.index] == "a":
            token = self.next_Token()
            self.match('and', token)
            new_node = TreeNode()
            new_node.data = "And"
            new_node.type = "OP"
            new_node.child.append(this_node)
            new_node.child.append(self.exp())
            this_node = new_node

        return this_node

    def exp(self):
        this_node = TreeNode()
        if self.my_string[self.index] == " ":
            self.index += 1
        if self.my_string[self.index] == '(':  # 如果是(exp1)
            # 匹配左括号(
            token = self.my_string[self.index]
            self.index += 1
            self.match('(', token)
            this_node = self.exp1()
            # 匹配有括号)
            if self.my_string[self.index] == " ":
                self.index += 1
            token = self.my_string[self.index]
            self.index += 1
            self.match(')', token)
        # 如果是not exp1
        elif self.my_string[self.index] == 'n':
            # 匹配not
            token = self.next_Token()
            self.match('not', token)
            this_node.data = 'not'
            this_node.type = 'Op'
            this_node.child.append(self.exp1())
        # 如果是simple_exp[compare_op simple_exp]
        else:
            this_node = self.simple_exp()
            if self.my_string[self.index] == " ":
                self.index += 1
            if self.my_string[self.index] == '<' or self.my_string[self.index] == '=' or self.my_string[self.index] == '>':
                new_node = self.compare_op()
                # TODO:print(new_node.data)
                new_node.child.append(this_node)
                new_node.child.append(self.simple_exp())
                this_node = new_node
        return this_node

    def compare_op(self):
        this_node = TreeNode()
        this_node.type = "Op"
        if self.my_string[self.index] == ' ':
            self.index += 1
        if self.my_string[self.index] == '<':  # 判断是否为</<=/<>
            token = self.my_string[self.index]
            self.index += 1
            if self.my_string[self.index] == '=' or self.my_string[self.index] == '>':
                # print('act this')
                token += self.my_string[self.index]
                self.index += 1
        elif self.my_string[self.index] == '>':  # 判断是否为>/>=
            token = self.my_string[self.index]
            self.index += 1
            if self.my_string[self.index] == '=':
                token += self.my_string[self.index]
                self.index += 1
        elif self.my_string[self.index:self.index+2] == '==':  # 判断是否为==
            token = self.my_string[self.index:self.index+2]
            self.index += 2
        else:
            # TODO:print('act to this')
            print(self.my_string[self.index])
            self.error_string += 'error: Op error'
            return None
        this_node.data = token
        return this_node

    def simple_exp(self):
        this_node = self.term()
        # 匹配add_op
        if self.my_string[self.index] == " ":
            self.index += 1
        while self.my_string[self.index] == '+' or self.my_string[self.index] == '-':
            new_node = TreeNode()
            new_node.data = self.my_string[self.index]
            self.index += 1
            new_node.type = 'Op'
            new_node.child.append(this_node)
            new_node.child.append(self.term())
            this_node = new_node

            if self.my_string[self.index] == ' ':
                self.index += 1

        return this_node

    def term(self):
        this_node = self.term1()
        # 匹配mul_op
        if self.my_string[self.index] == ' ':
            self.index += 1
        while self.my_string[self.index] == '*' or self.my_string[self.index] == '%' or self.my_string[self.index] == '/':
            # print(self.my_string[self.index])
            new_node = TreeNode()
            new_node.data = self.my_string[self.index]
            self.index += 1
            new_node.type = 'Op'
            new_node.child.append(this_node)
            new_node.child.append(self.term1())
            this_node = new_node
            if self.my_string[self.index] == ' ':
                self.index += 1

        return this_node

    def term1(self):
        this_node = self.factor()
        if self.my_string[self.index] == ' ':
            self.index += 1
        # 匹配mul_op
        while self.my_string[self.index] == '^':
            new_node = TreeNode()
            new_node.data = self.my_string[self.index]
            self.index += 1
            new_node.type = 'Op'
            new_node.child.append(this_node)
            new_node.child.append(self.factor())
            this_node = new_node
            if self.my_string[self.index] == " ":
                self.index += 1
        return this_node

    def factor(self):
        this_node = TreeNode()
        if self.my_string[self.index] == ' ':
            self.index += 1
        # 如果(exp)，分别匹配(、exp、)
        if self.my_string[self.index] == '(':
            token = self.my_string[self.index]
            self.match(token, '(')
            self.index += 1
            this_node = self.exp1()
            if self.my_string[self.index] == ' ':
                self.index += 1
            token = self.my_string[self.index]
            self.match(token, ')')
            self.index += 1
        else:
            if "0" <= self.my_string[self.index] <= "9":
                this_node.type = "Const"
            else:
                this_node.type = "Id"
            token = self.next_Token()
            this_node.data = token

        return this_node

    def print_tree(self, t, deep):
        temp_s = ""
        for _ in range(deep):
            temp_s += "\t"
        if t.data == t.type or 'Assign' in t.type:
            temp_s += t.type + "\n"

        else:
            temp_s += t.type + ": " + t.data + "\n"

        for child in t.child:
            temp_s += self.print_tree(child, deep + 1)

        for sibling in t.sibling:
            temp_s += self.print_tree(sibling, deep)

        return temp_s

if __name__ == "__main__":
    tiny = Tiny()
    # tiny.set_String('if ((a >= b) and (b<1)) then \na -= (b+1*(c+4));\nif (b == 0) then b := 1;endif;\n endif;')
    # tiny.set_String('while ((a >= b) and (b<>1)) do \n'
    #                'a -= (b+1*(c+4));\nif (b == 0) then b := b + 1;endif;\nsum := a + b;\n enddo;')
    # tiny.set_String("a := 0; for i := 10+5 to 20 do\nread a;\n for j:= 2 downto 1 do\n a += i+j;\nwrite a;\nenddo;\n enddo;")
    # tiny.set_String("repeat\n write a;\n a:= a-1;\n until a <= 0 ;")
    code_string = "a := 0;b:=5; c := 7;\n for i := b to c+1 do\n if (a <= 2) then read a;else read b;\n" \
                  " while ((a >= b) and (b<>1)) do b -= 1;\n enddo;\n repeat\n write a; until b > 0;" \
                  "endif;\n write a+c; enddo;"
    tiny.set_String(code_string)
    print(tiny.my_string)
    tiny.program()
    tiny.end_missing()
    print(tiny.error_string)
    print(tiny.print_tree(tiny.root, 0))

    tiny = Tiny()
    #code_string = 'if (a>0) then a += 1; repeat a -= 1;until a <= 0; write a;else a += 1; endif;'
    code_string = '''{ 这是一个 Tiny 语言的示例程序 }
                        read x;
                        read y;
                        if (x > y) then
                            write x;
                        endif;
                        repeat
                            x := x + 1;
                            y := y - 1;
                        until (x >= y);
                        write x+y;
                        for i := 1 to 10 do
                            write i;
                        enddo;
                        while (x > 0) do
                            x := x - 1;
                            write x;
                        enddo;
                        a := 5;
                        b := 10;
                        c := a + b;
                        write c;
                        
                        if (c > 15) then
                            write c;
                        else
                            write 15;
                        endif;'''
    tiny.set_String(code_string)
    print(tiny.my_string)
    tiny.program()
    tiny.end_missing()
    print(tiny.error_string)
    print(tiny.print_tree(tiny.root, 0))
