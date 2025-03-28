# -*- coding: utf-8 -*-
import re


class Bool_exp:  # 布尔表达式
    def __init__(self, index, r=None, id1=None, op=None, id2=None):
        self.number = 100 + index
        self.begin_code = self.number  # 开始位置
        self.tetrad = Tetrad(index, r, id1, op, id2)  # 用于存放四元组
        self.tetrad.result = "?"  # result为真出口
        self.false_number = self.number + 1
        self.false = "?"  # 为假出口
        self.false_chain = set()
        self.true_chain = set()


class Tetrad:  # 三地址码中四元组表示中间代码形式
    def __init__(self, index, r=None, id1=None, op=None, id2=None):
        self.number = 100 + index
        self.result = r
        self.id1 = id1
        self.op = op
        self.id2 = id2


class Tiny_code:
    def __init__(self):
        self.my_string = ''
        self.error_string = ''
        self.index = 0
        self.middle_code = []  # 存放中间代码
        self.sign = {'(', ')', ';', '<', '>', '+', '-', '*', '/', '%', ':', '=', '^', '|',
                     '&', '#', '<>', '<=', '>=', '/=', '*=', '%=', '+=', '-='}  # 特殊符号
        self.fuzhi_sign = {'/=', '*=', '%=', '+=', '-=', ":="}
        self.end_set = {'endif', 'enddo'}
        self.temp_id = 0  # 临时变量的id
        self.tetrad_num = 0

    def set_String(self, temp_string):
        ts = ''
        # 去除注释: {...}
        flag = False
        for i in range(len(temp_string)):
            if temp_string[i] == "{":  # 如果是注释
                flag = True
            if not flag:
                ts += temp_string[i]
                if temp_string[i-1:i+1] == 'to':
                    ts += " := "
            if temp_string[i] == "}":
                flag = False
        if flag:
            self.error_string = "input error\n"  # 输入的语法有误
            return
        ts = re.sub(r'\s+', ' ', ts)  # 去除多余的空格
        self.my_string = ts

    def next_token(self):  # 获取下一个token
        token = ''
        if self.my_string[self.index] == ' ':
            self.index += 1
        s = self.my_string[self.index]
        if s in self.sign:
            while self.index < len(self.my_string) and self.my_string[self.index] != ' ' and self.my_string[self.index] in self.sign:
                token += self.my_string[self.index]
                self.index += 1
        else:
            while self.index < len(self.my_string) and self.my_string[self.index] != ' ' and self.my_string[self.index] not in self.sign:
                token += self.my_string[self.index]
                self.index += 1
        return token

    def match(self, match_s, temp_s):
        if match_s != temp_s:
            self.error_string += "error: unexpected token: " + temp_s + '\n'
        return

    def match1(self, the_set, temp_s):
        if temp_s not in the_set:
            self.error_string += "error: unexpected token: " + temp_s + '\n'
        return

    def emit(self):
        for m in self.middle_code:
            if isinstance(m, Tetrad):
                if m.result not in {"write", 'read'}:
                    print(m.number, m.result, ":=", m.id1, m.op if m.op is not None else "", m.id2 if m.id2 is not None else "")
                else:
                    print(m.number, m.result, m.id1)
            elif isinstance(m, Bool_exp):
                print(m.number, "if", m.tetrad.id1, m.tetrad.op, m.tetrad.id2, "goto", m.tetrad.result,)
                # print(m.number, "if", m.tetrad.id1, m.tetrad.op, m.tetrad.id2,"goto", m.tetrad.result, m.false, "begin_code", m.begin_code)
            else:
                print(m[0], 'goto', m[1])

    def stmt_sequence(self):
        self.statement()
        while self.index < len(self.my_string)-1 and self.my_string[self.index] == ';':
            self.index += 1  # 跳过;
            if self.statement():
                break

    def statement(self):
        token = self.next_token()
        # print(token)
        if token in self.end_set or token in {"else", "until"}:  # 跳过结束符
            if token in {"else", "until"}:
                self.index -= len(token)
            return "next"
        if token == 'while':
            self.while_stmt()
        elif token == 'for':
            self.for_stmt()
        elif token == 'if':
            self.if_stmt()
        elif token == 'repeat':
            self.repeat_stmt()
        elif token == 'write':
            self.write()
        elif token == 'read':
            self.read()
        else:  # 赋值语句
            # self.condition_exp(token)
            self.simple_exp(token, True)

    def if_stmt(self):
        token = self.next_token()
        self.match("(", token)
        token = self.next_token()
        E = self.condition_exp(token)  # 获取false_number和true_number集合
        # print(self.index, len(self.my_string))
        token = self.next_token()
        self.match("then", token)
        for t in E.true_chain:
            if isinstance(self.middle_code[t-100], Bool_exp):  # backpatch(E.true, nextstat);
                self.middle_code[t-100].tetrad.result = self.tetrad_num + 100
            else:
                self.middle_code[t-100][1] = self.tetrad_num + 100
        self.stmt_sequence()
        true_chain = self.tetrad_num+100
        self.middle_code.append([true_chain, "?"])  # 用于跳过else语句
        self.tetrad_num += 1
        for f in E.false_chain:  # C.chain = E.false,backpatch(C.chain, nextstat);
            if isinstance(self.middle_code[f - 100], Bool_exp):  # backpatch(E.true, nextstat);
                self.middle_code[f - 100].tetrad.result = self.tetrad_num + 100
            else:
                self.middle_code[f - 100][1] = self.tetrad_num + 100
        token = self.next_token()  # 检查下一个是否为else
        if token == 'else':
            self.stmt_sequence()
        else:
            self.index -= len(token)  # 不是else进行回退
        self.middle_code[true_chain-100][1] = self.tetrad_num + 100  # backpatch(E.false=C.chain, nextstat);

    def repeat_stmt(self):
        repeat_begin = self.tetrad_num  # R.codebegin = nextstat;
        self.stmt_sequence()
        token = self.next_token()
        self.match("until", token)
        token = self.next_token()
        self.match("(", token)
        # print(token)
        E = self.condition_exp('')
        for f in E.false_chain:  # backpatch(E.false, U.codebegin);
            if isinstance(self.middle_code[f - 100], Bool_exp):  # backpatch(E.true, nextstat);
                self.middle_code[f - 100].tetrad.result = repeat_begin + 100
            else:
                self.middle_code[f - 100][1] = repeat_begin + 100
        for t in E.true_chain:
            if isinstance(self.middle_code[t - 100], Bool_exp):  # backpatch(E.true, nextstat);
                self.middle_code[t - 100].tetrad.result = self.tetrad_num + 100
            else:
                self.middle_code[t - 100][1] = self.tetrad_num + 100

    def while_stmt(self):
        token = self.next_token()
        self.match('(', token)
        while_begin = self.tetrad_num  # W.codebegin = nextstat;
        E = self.condition_exp('')
        for t in E.true_chain:  # backpatch(E.true, nextstat);
            if isinstance(self.middle_code[t - 100], Bool_exp):  # backpatch(E.true, nextstat);
                self.middle_code[t - 100].tetrad.result = self.tetrad_num + 100
            else:
                self.middle_code[t - 100][1] = self.tetrad_num + 100
        token = self.next_token()
        self.match('do', token)
        self.stmt_sequence()
        self.middle_code.append([self.tetrad_num+100, while_begin+100])  # emit(’goto’, W.codebegin);
        self.tetrad_num += 1
        for f in E.false_chain:
            if isinstance(self.middle_code[f - 100], Bool_exp):  # S.chain = WD.chain = E.false;
                self.middle_code[f - 100].tetrad.result = self.tetrad_num + 100
            else:
                self.middle_code[f - 100][1] = self.tetrad_num + 100

    def for_stmt(self):
        id = self.next_token()  # 获取循环变量
        self.simple_exp(id, True)
        to_token = self.next_token()  # 是to/downto
        self.match1({'to', "downto"}, to_token)
        temp_max = "Max_R" + str(self.temp_id)
        self.temp_id += 1
        self.simple_exp(temp_max, True)
        token = self.next_token()
        self.match("do", token)
        S_code_begin = self.tetrad_num  # 内容代码的开始
        self.stmt_sequence()
        self.middle_code.append(Tetrad(self.tetrad_num, id1=id, op="+" if to_token == "to" else "-", id2=1, r="R"+str(self.temp_id)))
        self.temp_id += 1
        self.middle_code.append(Tetrad(self.tetrad_num+1, r=id, id1=self.middle_code[self.tetrad_num].result))
        self.tetrad_num += 2
        E = Bool_exp(self.tetrad_num, id1=id, id2=temp_max, op="<=" if to_token == "to" else ">=")
        self.tetrad_num += 1
        E.tetrad.result = S_code_begin + 100
        E.false = self.tetrad_num + 1
        # E.true_chain.add(E.number)
        # E.false_chain.add(self.tetrad_num+1)
        false_goto = [self.tetrad_num+100, self.tetrad_num+101]
        self.tetrad_num += 1
        self.middle_code.append(E)
        self.middle_code.append(false_goto)

    def write(self):  # write语句
        result = self.simple_exp('', False)
        self.middle_code.append(Tetrad(self.tetrad_num, 'write', id1=result))
        self.tetrad_num += 1

    def read(self):  # read语句
        token = self.next_token()
        self.middle_code.append(Tetrad(self.tetrad_num, 'read', id1=token))
        self.tetrad_num += 1

    def condition_exp(self, token):
        self.index -= len(token)
        tetrad_stack = []
        op_stack = []
        token = self.next_token()
        while token not in {'then', 'do', ";"} and self.index < len(self.my_string):
            if token[-1] == ';':
                self.index -= 1
                break
            # print(op_stack)
            # print(token)
            if token in {"and", "or", "not"}:
                op_stack.append(token)
            elif token == '(':
                op_stack.append(token)
            elif token == ')':
                break
            else:  # id
                begin = self.tetrad_num + 100  # 开始
                self.index -= len(token)
                id1 = self.simple_exp('', False)  # id1
                token = self.next_token()
                rop = token  # op
                # print(rop)
                id2 = self.simple_exp('', False)  # id2
                if token not in {"<=", ">=", "<", ">", "<>", "=="}:
                    self.error_string += f"unexpected miss {token}!"
                e = Bool_exp(self.tetrad_num, id1=id1, op=rop, id2=id2)
                self.tetrad_num += 1
                e.begin_code = begin
                e.false_chain.add(e.false_number)
                e.true_chain.add(e.number)
                self.middle_code.append(e)
                self.middle_code.append([e.false_number, e.false])
                self.tetrad_num += 1
                tetrad_stack.append(e)  # 压入栈中
                if op_stack and op_stack[-1] == "and":  # 栈顶为and
                    # e1的true为true，e2和e1的false相同
                    e2 = tetrad_stack.pop()
                    e1 = tetrad_stack.pop()
                    op_stack.pop()
                    num1 = e1.number
                    num2 = e2.number
                    if op_stack and op_stack[-1] == 'not':  # E.codebegin := E1.codebegin
                        temp = e1.false_chain
                        e1.false_chain = e1.true_chain  # E.false := E1.true
                        e1.true_chain = temp  # E.true := E1.false
                        op_stack.pop()
                    # begin1 = e1.begin_code
                    begin2 = e2.begin_code
                    new_begin = e1.begin_code
                    # print(num1, num2)
                    for true in e1.true_chain:
                        if isinstance(self.middle_code[true-100], Bool_exp):
                            self.middle_code[true - 100].tetrad.result = begin2  # backpatch(E .true, E2.codebegin)
                        else:
                            self.middle_code[true - 100][1] = begin2
                    temp_e = Bool_exp(num2-100, id1=num1, id2=num2)
                    temp_e.begin_code = new_begin  # E.codebegin := E.codebegin
                    # 将假出口放入chain中
                    temp_e.false_chain |= e1.false_chain | e2.false_chain  # E.false : merge(E .false, E  false);
                    temp_e.true_chain = e2.true_chain  # E.true := E2.true
                    tetrad_stack.append(temp_e)  # temp压入栈中

            token = self.next_token()
        while op_stack and tetrad_stack:  # 排空运算符栈
            op = op_stack.pop()
            if op == "or":
                self.match("or", op)
                e2 = tetrad_stack.pop()
                e1 = tetrad_stack.pop()
                num1 = e1.number
                num2 = e2.number
                # print(e1.false_chain, e2.false_chain)
                if op_stack and op_stack[-1] == 'not':  # E.codebegin := E1.codebegin
                    temp = e1.false_chain
                    e1.false_chain = e1.true_chain  # E.false := E1.true
                    e1.true_chain = temp  # E.true := E1.false
                    op_stack.pop()
                for false in e1.false_chain:  # backpatch(E .false, E.codebegin)
                    if isinstance(self.middle_code[false - 100], Bool_exp):
                        self.middle_code[false - 100].tetrad.result = e2.begin_code
                    else:
                        self.middle_code[false - 100][1] = e2.begin_code
                temp_e = Bool_exp(num2 - 100, id1=num1, id2=num2)
                temp_e.begin_code = e1.begin_code  # E.codebegin := E .codebegin;
                temp_e.true_chain = e1.true_chain | e2.true_chain  # E.true := merge(El.true, .true)
                temp_e.false_chain = e2.false_chain  # E.false := E.false
                tetrad_stack.append(temp_e)
            else:  # 为not
                e1 = tetrad_stack.pop()
                num1 = e1.number
                temp = e1.false_chain
                e1.false_chain = e1.true_chain  # E.false := E1.true
                e1.true_chain = temp  # E.true := E1.false
                tetrad_stack.append(e1)

        end_e = tetrad_stack.pop()
        print("假出口：", end_e.false_chain, "真出口：", end_e.true_chain)
        return end_e

    def simple_exp(self, token, flag):  # 赋值语句, flag用于表示是否为赋值语句
        id_stack = []
        op_stack = []
        if flag:
            result_id = token  # 结果标识符
            result_op = self.next_token()  # 赋值符号
            # print(result_id, result_op)
            self.match1(self.fuzhi_sign, result_op)
            if result_op in {"/=", "*=", "%=", "+=", "-="}:
                id_stack.append(result_id)
                op_stack.append(result_op[0])
                # print(op_stack, id_stack)
        if self.my_string[self.index] == ' ':
            self.index += 1
        token = self.my_string[self.index]
        self.index += 1
        temp_token = token
        while self.index < len(self.my_string) and token not in {';', "<=", ">=", "<", ">", "<>", "=", "=="}:
            if token in self.sign:
                op_stack.append(token)  # 符号入栈
                if token == ')' and '(' in op_stack:
                    op_stack.pop()
                    op = op_stack.pop()
                    while op_stack and op != '(':
                        id2 = id_stack.pop()
                        id1 = id_stack.pop()
                        result = 'R' + str(self.temp_id)  # 计算结果
                        id_stack.append(result)  # 将临时计算结果放入
                        t = Tetrad(self.tetrad_num, result, id1, op, id2)  # 构造四元组
                        self.middle_code.append(t)
                        self.temp_id += 1
                        self.tetrad_num += 1
                        op = op_stack.pop()

                    if op_stack and op_stack[-1] in {'*', '/', '%'}:
                        id2 = id_stack.pop()
                        id1 = id_stack.pop()
                        op = op_stack.pop()
                        result = 'R' + str(self.temp_id)
                        t = Tetrad(self.tetrad_num, result, id1, op, id2)
                        self.temp_id += 1
                        self.tetrad_num += 1
                        self.middle_code.append(t)
                        id_stack.append(result)  # 将临时计算结果放入
                elif token == ')' and '(' not in op_stack:
                    op_stack.pop()
                    break
                    # self.index -= 1
            else:  # id/布尔运算符
                self.index -= 1
                token = self.next_token()
                if token in {"to", "downto", 'do'}:  # 遇到to或downto终止
                    self.index -= len(token)
                    break
                # print(token)
                if token not in {'and', "or", "not"}:
                    id_stack.append(token)
                    if temp_token in {'*', '/', '%'}:
                        id2 = id_stack.pop()
                        id1 = id_stack.pop()
                        op = op_stack.pop()
                        result = 'R' + str(self.temp_id)
                        t = Tetrad(self.tetrad_num, result, id1, op, id2)
                        self.temp_id += 1
                        self.tetrad_num += 1
                        self.middle_code.append(t)
                        id_stack.append(result)  # 将临时计算结果放入
                else:
                    self.index -= len(token)
                    break
            temp_token = token
            # print(token)
            # print(id_stack, op_stack)
            if self.my_string[self.index] == ' ':
                self.index += 1
            token = self.my_string[self.index]
            self.index += 1

        while id_stack and op_stack:  # 排空运算符栈
            id2 = id_stack.pop()
            id1 = id_stack.pop()
            op = op_stack.pop()
            result = 'R' + str(self.temp_id)
            t = Tetrad(self.tetrad_num, result, id1, op, id2)
            self.temp_id += 1
            self.tetrad_num += 1
            self.middle_code.append(t)
            id_stack.append(result)  # 将临时计算结果放入
        # print(id_stack, op_stack)
        result = id_stack.pop()
        self.index -= 1
        if flag:
            self.middle_code.append(Tetrad(self.tetrad_num, result_id, id1=result))
            self.tetrad_num += 1
        # print("|")
        return result  # 返回最终的结果


def main():
    tiny = Tiny_code()
    # tiny.set_String("a *= a2 + a1 * (b+c)/(a6*b8+505);")
    # tiny.set_String('write a+b* (b+c)/(a6*b8+505);')
    # tiny.set_String('a+40 >= b/20 and a/6 <> 0 and a >= 10 and v <> 100; ')
    # tiny.set_String('a <> b and (a>0 and b < 1);')
    tiny.set_String('a:=0; if (a/10 < 10) then repeat a += 1; until (x >= 10); write a; endif;')
    tiny.set_String('read a; read b; for i := 1+b to b + 10 do a += i;enddo; write a;')
    tiny.set_String('read a; while (a>=0 and a<10 or a == 6) do a += 10; a %= 12; enddo;write a;')
    tiny.set_String('read a; a *= a2 + a1 * (b+c)/(a6*b8+505); write a%6+2;')
    tiny.set_String('read a;read b; a *= 10;if (a > 0 or not a < 5 and b/4 > 10 or b/3 <> 4) '
                    'then a := a + 1; a%=3; '
                    'if (a > b) then a += b; endif;'
                    'else a += 2;a /= 3;'
                    'endif; write a;')
    tiny.set_String("read a; read b; repeat a *= 1.25; repeat a + 0.5;until(a >= 5); until (a >= b); write a*100;")
    tiny.set_String("a := 0;b:=5; c := 7;\n for i := b to c+1 do\n if (a <= 2) then read a;else read b;\n" 
                    " while (not a >= b and b<>1) do b -= 1;\n enddo;\n repeat\n write a; until (b > 0);"
                    "endif;\n write a+c; enddo;")
    tiny.set_String("x1:= 1;x2:= 1;read times; for i := 1 to 5*times do temp := x2; x2 += x1; x1 := temp; if (x1>=50) "
                    "then write x2; else write x1;endif;enddo; write x1 + x2; while(x1 <= x2 and x1 >= 10) do x2 -= (x2-x1)/(x2+x1);"
                    "repeat x1 *= (x2+x1)/(x2-x1);until (not x1 >= x2-(x2-x1)/(x2+x1)); write x1; enddo; write x1;write x2;")
    tiny.set_String("for i := 1 to 5 do write i; enddo;")
    print(tiny.my_string)
    tiny.stmt_sequence()
    tiny.emit()
    print(tiny.error_string)


if __name__ == '__main__':
    main()
