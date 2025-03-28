from igraph import Graph  # 用于生成有向图
import igraph as ig
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class DFA:
    def __init__(self):
        self.mvexs = []  # DFA结点结合
        self.node_name = []  # 结点标签
        self.start_status = -1  # 开始状态
        self.end_status = []  # 接收状态
        self.dfa_graph = Graph(directed=True)  # 创造DFA图结构
        self.min_dfa_graph = Graph(directed=True)  # 最小化DFA图结构
        self.alphabet = []  # 字母表
        self.adjacency_matrix = []  # 邻接矩阵
        self.status_matrix = pd.DataFrame()  # 状态转移表
        self.status_matrix1 = pd.DataFrame()  # 没有结点名的状态转移表
        self.mini_dfa_status_matrix = pd.DataFrame()  # mini_DFA的状态转移表
        self.min_adjacency_matrix = []  # minDFA的邻接矩阵
        self.min_dfa_start = -1
        self.min_dfa_end = []

    def adjacency_matrix_and_status_matrix(self):
        m = np.array(self.dfa_graph.get_adjacency())  # 获得0/1邻接矩阵
        non_zero_index = [i.tolist() for i in m.nonzero()]  # 获得邻接顶点的索引
        # 构造邻接转移矩阵
        matrix = np.empty((self.dfa_graph.vcount(), self.dfa_graph.vcount()), dtype=object)
        for i in range(len(non_zero_index[0])):
            # print(non_zero_index[0][i], non_zero_index[1][i])
            label = self.dfa_graph.es[self.dfa_graph.get_eid(non_zero_index[0][i], non_zero_index[1][i])]['label']
            matrix[non_zero_index[0][i]][non_zero_index[1][i]] = label
        print(f'DFA邻接矩阵为:\n{matrix}')
        status_matrix = pd.DataFrame(index=self.node_name, columns=self.alphabet)
        status_matrix1 = pd.DataFrame(index=list(range(len(self.mvexs))), columns=self.alphabet)
        for edge in self.dfa_graph.es:
            # print(type(status_matrix.loc[edge.source][edge['label']]), status_matrix.loc[edge.source][edge['label']])
            status_matrix.loc[self.node_name[edge.source]][edge['label']]= self.node_name[edge.target]
            status_matrix1.loc[edge.source][edge['label']] = edge.target
        print(f'DFA的状态转移表为:\n{status_matrix}')
        # print(status_matrix1)
        self.adjacency_matrix = matrix
        self.status_matrix = status_matrix
        self.status_matrix1 = status_matrix1

    def draw_graph(self):
        self.dfa_graph.vs["label"] = [str(v) for v in self.dfa_graph.vs.indices]
        fig, ax = plt.subplots(figsize=(8, 5))
        # 设置边的标签
        # edge_labels = [e['label'] for e in self.dfa_graph.es]
        layout = self.dfa_graph.layout("auto")
        vertex_color = ['white' for _ in range(self.dfa_graph.vcount())]
        vertex_color[self.start_status] = 'blue'  # 开始状态结点颜色
        for s in self.end_status:  # 结束状态结点颜色
            vertex_color[s] = 'red'
        edge_labels = []
        for e in self.dfa_graph.es:
            if e.source != e.target:
                edge_labels.append(e['label'])
            else:
                edge_labels.append('')
                x, y = layout[e.source]
                ax.text(x-0.1, y-0.05, e['label'], color='black', fontsize=12, ha='center', va='center')

        ig.plot(self.dfa_graph, target=ax, layout=layout, bbox=(300, 300), margin=40, edge_label=edge_labels,
                vertex_label=self.node_name, vertex_size=40, vertex_color=vertex_color)
        plt.show()

    def min_adjacency_matrix_and_status_matrix(self):
        isolated_vertex = self.dfa_graph.vs.select(_degree=0)
        self.dfa_graph.delete_vertices(isolated_vertex)  # 删除孤立点
        isolated_vertex_list = isolated_vertex.indices
        isolated_vertex_list.sort(reverse=True)
        for i in range(len(self.min_dfa_end)):  # 去除孤立节点得到
            count = len([x for x in isolated_vertex_list if x <= self.min_dfa_end[i]])
            self.min_dfa_end[i] -= count
        # print(self.min_dfa_start, self.min_dfa_end)
        m = np.zeros((self.dfa_graph.vcount(), self.dfa_graph.vcount()))  # 0/1邻接矩阵
        adjacency_matrix = np.empty((self.dfa_graph.vcount(), self.dfa_graph.vcount()), dtype=object)  # 条件邻接矩阵
        status_matrix = pd.DataFrame(index=range(self.dfa_graph.vcount()), columns=self.alphabet)  # 状态转移表
        # print(status_matrix)
        for e in self.dfa_graph.es:
            # print(e)
            adjacency_matrix[e.source][e.target] = e['label']
            status_matrix.loc[e.source][e['label']] = e.target
        print('最小化DFA的邻接矩阵为：', adjacency_matrix, sep='\n')
        print('最小化DFA的状态转移表为：', status_matrix, sep='\n')
        self.mini_dfa_status_matrix = status_matrix
        self.min_adjacency_matrix = adjacency_matrix

    def draw_min_dfa(self):
        v_num = self.dfa_graph.vcount()
        self.min_dfa_graph.add_vertices(v_num)
        v_list = list(range(v_num))
        for row in self.mini_dfa_status_matrix.index:
            for col in self.mini_dfa_status_matrix.columns:
                if self.mini_dfa_status_matrix.loc[row][col] in v_list:
                    self.min_dfa_graph.add_edge(row, self.mini_dfa_status_matrix.loc[row][col], label=col)
        # edge_labels = [e["label"] for e in self.dfa_graph.es]
        vertex_labels = [i for i in range(v_num)]
        fig, ax = plt.subplots(figsize=(8, 5))

        layout = self.min_dfa_graph.layout("auto")
        vertex_color = ['white' for _ in range(v_num)]
        vertex_color[self.min_dfa_start] = 'blue'  # 开始状态结点颜色
        for s in self.min_dfa_end:  # 结束状态结点颜色
            vertex_color[s] = 'red'
        edge_labels = []
        for e in self.min_dfa_graph.es:
            if e.source != e.target:
                edge_labels.append(e['label'])
            else:
                edge_labels.append('')
                x, y = layout[e.source]
                ax.text(x + 0.1, y, e['label'], color='black', fontsize=12, ha='center', va='center')
        ig.plot(self.min_dfa_graph, layout='auto', target=ax, bbox=(300, 300), margin=20, edge_label=edge_labels,
                vertex_label=vertex_labels, vertex_color=vertex_color)
        plt.show()


class NFA:
    def __init__(self):
        self.start_status = -1  # 开始状态
        self.end_status = -1  # 接收状态
        self.nfa_graph = Graph(directed=True)  # 创建NFA图结构(有向图)
        self.mvexs = []  # NFA结点集合
        self.alphabet = []
        self.adjacency_matrix = []  # 邻接矩阵
        self.status_matrix = pd.DataFrame()  # 状态转移表

    def adjacency_matrix_and_status_matrix(self):  # 求邻接矩阵和状态转移表
        m = np.array(self.nfa_graph.get_adjacency())  # 获得0/1邻接矩阵
        non_zero_index = [i.tolist() for i in m.nonzero()]  # 获得邻接顶点的索引
        # 构造邻接转移矩阵
        matrix = np.empty((self.nfa_graph.vcount(), self.nfa_graph.vcount()), dtype=object)
        for i in range(len(non_zero_index[0])):
            # print(non_zero_index[0][i], non_zero_index[1][i])
            label = self.nfa_graph.es[self.nfa_graph.get_eid(non_zero_index[0][i], non_zero_index[1][i])]['label']
            matrix[non_zero_index[0][i]][non_zero_index[1][i]] = label

        self.alphabet.append('@')
        status_matrix = pd.DataFrame(index=self.mvexs, columns=self.alphabet)
        status_matrix = status_matrix.apply(lambda x: x.apply(lambda y: []))
        for edge in self.nfa_graph.es:
            # print(type(status_matrix.loc[edge.source][edge['label']]), status_matrix.loc[edge.source][edge['label']])
            status_matrix.loc[edge.source][edge['label']].append(edge.target)
            status_matrix.loc[edge.source][edge['label']].sort()
        self.adjacency_matrix = matrix
        self.status_matrix = status_matrix
        print(f'NFA邻接矩阵为:\n{matrix}')
        print(f'NFA状态转移表为:\n{status_matrix}')
        return matrix, status_matrix  # 返回邻接矩阵和状态转换表

    def draw_graph(self):  # 绘制有穷自动机
        # 设置顶点的标签
        self.nfa_graph.vs["label"] = [str(v) for v in self.nfa_graph.vs.indices]
        # 设置边的标签
        edge_labels = [e["label"] for e in self.nfa_graph.es]
        vertex_color = ['white' for _ in range(self.nfa_graph.vcount())]
        vertex_color[self.start_status], vertex_color[self.end_status] = 'blue', 'red'  # 设置开始状态和结束状态的节点颜色
        fig, ax = plt.subplots(figsize=(8, 5))
        ig.plot(self.nfa_graph, layout='auto',target=ax, bbox=(300, 300), margin=20, edge_label=edge_labels,
                vertex_color=vertex_color)
        plt.show()


class Lex:
    def __init__(self):
        self.lex_nfa = NFA()
        self.lex_dfa = DFA()
        self.operator_stack = list()  # 操作符栈
        self.alphabet = []  # 字符表
        self.nfa_status_stack = list()  # 状态栈
        self.operator = {'*', '|', '?', '+', '(', ')'}  # 运算符

    def create_basic_nfa(self, ch):  # 创建最基本的NFA
        start_point = len(self.lex_nfa.mvexs)
        end_point = start_point + 1
        self.lex_nfa.nfa_graph.add_vertices(2)  # 增加两个节点
        # 建立边连接，边转移条件为字符
        self.lex_nfa.nfa_graph.add_edge(start_point, end_point, label=ch)
        # 加入结点数组中
        self.lex_nfa.mvexs.append(start_point)
        self.lex_nfa.mvexs.append(end_point)
        # NFA栈中的NFA的起始点序号，0的位置代表起点，1的位置代表终点
        new_nfa_status_point = [start_point, end_point]
        self.nfa_status_stack.append(new_nfa_status_point)
        # 起点终点设置
        self.lex_nfa.start_status = start_point
        self.lex_nfa.end_status = end_point

    def select_operator(self):  # |或运算符
        # 从栈中取栈顶两个元素第一个元素为右式
        right_nfa = self.nfa_status_stack.pop()
        left_nfa = self.nfa_status_stack.pop()
        # 创建新节点
        new_start1 = len(self.lex_nfa.mvexs)
        new_start2 = new_start1 + 1
        self.lex_nfa.nfa_graph.add_vertices(2)  # 增加两个节点
        # 图链接,空转移
        self.lex_nfa.nfa_graph.add_edge(new_start1, left_nfa[0], label='@')
        self.lex_nfa.nfa_graph.add_edge(new_start1, right_nfa[0], label='@')
        self.lex_nfa.nfa_graph.add_edge(left_nfa[1], new_start2, label='@')
        self.lex_nfa.nfa_graph.add_edge(right_nfa[1], new_start2, label='@')
        # 结点添到结点列表中
        self.lex_nfa.mvexs.append(new_start1)
        self.lex_nfa.mvexs.append(new_start2)
        # 将新的NFA压入NFA栈中
        self.nfa_status_stack.append([new_start1, new_start2])
        # 设置起点终点
        self.lex_nfa.start_status = new_start1
        self.lex_nfa.end_status = new_start2

    def and_operator(self):  # &与运算符
        top_nfa1 = self.nfa_status_stack.pop()
        top_nfa2 = self.nfa_status_stack.pop()
        self.lex_nfa.nfa_graph.add_edge(top_nfa2[1], top_nfa1[0], label='@')
        self.nfa_status_stack.append([top_nfa2[0], top_nfa1[1]])

    def repeat_operator(self, operator_type):  # *、+、？闭包运算
        # 获取栈顶第一个元素,开始和结束
        top_nfa = self.nfa_status_stack.pop()
        new_start1 = len(self.lex_nfa.mvexs)
        new_start2 = new_start1 + 1
        self.lex_nfa.nfa_graph.add_vertices(2)  # 节点数增加2
        if operator_type == 'repeat':  # *闭包操作
            self.lex_nfa.nfa_graph.add_edge(new_start1, new_start2, label="@")
            self.lex_nfa.nfa_graph.add_edge(new_start1, top_nfa[0], label="@")
            self.lex_nfa.nfa_graph.add_edge(top_nfa[1], new_start2, label='@')
            self.lex_nfa.nfa_graph.add_edge(top_nfa[1], top_nfa[0], label="@")
        elif operator_type == 'repeat1':  # +正闭包操作
            self.lex_nfa.nfa_graph.add_edge(new_start1, top_nfa[0], label="@")
            self.lex_nfa.nfa_graph.add_edge(top_nfa[1], new_start2, label="@")
            self.lex_nfa.nfa_graph.add_edge(top_nfa[1], top_nfa[0], label="@")
        elif operator_type == 'once_or_not':  # 一次或没有操作
            self.lex_nfa.nfa_graph.add_edge(new_start1, top_nfa[0], label="@")
            self.lex_nfa.nfa_graph.add_edge(top_nfa[1], new_start2, label="@")
            self.lex_nfa.nfa_graph.add_edge(new_start1, new_start2, label="@")
        # 将新节点加入节点列表中
        self.lex_nfa.mvexs.append(new_start1)
        self.lex_nfa.mvexs.append(new_start2)
        # 新NFA入栈
        self.nfa_status_stack.append([new_start1, new_start2])

        self.lex_nfa.start_status = new_start1
        self.lex_nfa.end_status = new_start2

    def get_nfa(self, regex_input):  # 获得NFA
        strlen = len(regex_input)
        for i in range(strlen):
            ch = regex_input[i]
            if ch in self.operator:
                if ch == '*':
                    self.repeat_operator('repeat')
                    if i+1 < strlen and (regex_input[i+1]=='(' or regex_input[i+1] not in self.operator):  # 如果下一个字符是字母或是左括号需要增加连接符
                        self.operator_stack.append('&')
                elif ch == '+':
                    self.repeat_operator('repeat1')
                    if i + 1 < strlen and (regex_input[i + 1] == '(' or regex_input[i + 1] not in self.operator):  # 如果下一个字符是字母或是左括号需要增加连接符
                        self.operator_stack.append('&')
                elif ch == '?':
                    self.repeat_operator('once_or_not')
                    if i + 1 < strlen and (regex_input[i+1] == '(' or regex_input[i+1] not in self.operator):  # 如果下一个字符是字母或是左括号需要增加连接符
                        self.operator_stack.append('&')
                elif ch == '|':
                    if len(self.operator_stack) == 0:
                        print('运算符栈为空!')
                    else:
                        while len(self.operator_stack) != 0 and self.operator_stack[-1] != '(':
                            ch = self.operator_stack.pop()
                            if ch == '&':
                                self.and_operator()
                            else:
                                break
                    self.operator_stack.append('|')
                elif ch == '(':
                    self.operator_stack.append(ch)
                elif ch == ')':
                    ch = self.operator_stack[-1]
                    while ch != '(':
                        if ch == '&':
                            self.and_operator()
                        elif ch == '|':
                            self.select_operator()
                        else:
                            break
                        self.operator_stack.pop()
                        ch = self.operator_stack[-1]
                    self.operator_stack.pop()  # 移除左括号
                    if i+1 < strlen and (regex_input[i+1] == '(' or regex_input[i+1] not in self.operator):  # 如果下一个字符是字母或是左括号需要增加连接符
                        self.operator_stack.append('&')
                else:
                    print('ok', ch)

            else:  # 不是运算符
                flag = ch in self.alphabet  # 是否需要加入字母表
                if not flag:
                    self.alphabet.append(ch)
                self.create_basic_nfa(ch)  # 建立基本的NFA
                if i + 1 < strlen and (regex_input[i + 1] == '(' or regex_input[i + 1] not in self.operator):  # 如果下一个字符是字母或是左括号需要增加连接符
                    self.operator_stack.append('&')
        while len(self.operator_stack) != 0:
            ch = self.operator_stack.pop()
            if ch == '|':
                self.select_operator()
            elif ch == '&':
                self.and_operator()
            else:
                break
        # 查找NFA的起点和终点
        start, end = self.lex_nfa.nfa_graph.vs.select(_indegree=0), self.lex_nfa.nfa_graph.vs.select(_outdegree=0)
        self.lex_nfa.start_status = start.indices[0]
        self.lex_nfa.end_status = end.indices[0]
        self.lex_nfa.alphabet = self.alphabet

    def epsilon_closure(self, status_list):  # 求@闭包
        result_list = []  # 存放状态列表的@转换的集合
        status_stack = list()  # 存放递归过程的栈
        for i in range(len(status_list)):
            status_stack.append(status_list[i])  # 初始化状态栈
            result_list.append(status_list[i])  # 自身也在空转移到本身
        while status_stack:
            statu = status_stack.pop()
            for i in self.lex_nfa.mvexs:
                if i == statu:
                    for j in self.lex_nfa.mvexs:
                        if self.lex_nfa.adjacency_matrix[i][j] == '@':
                            status_stack.append(j)
                            result_list.append(j)
        result_list = list(set(result_list))  # 去重复状态
        result_list.sort()
        return result_list

    def nfa_move(self, status_list, ch):  # 从status_list某个状态出发，通过ch转换到达其他NFA状态的集合
        result_list = []  # 结果列表
        status_stack = list()  # 存放递归过程的栈
        for i in range(len(status_list)):
            status_stack.append(status_list[i])  # 初始化状态栈
            # result_list.append(status_list[i])
        while status_stack:
            statu = status_stack.pop()
            for i in self.lex_nfa.mvexs:
                if i == statu:
                    for j in self.lex_nfa.mvexs:
                        if self.lex_nfa.adjacency_matrix[i][j] == ch:
                            # status_stack.append(j)
                            result_list.append(j)
        result_list = list(set(result_list))  # 去重复状态
        result_list.sort()
        return result_list

    def get_dfa(self):  # 获得DFA
        init_status = list()
        init_status.append(self.lex_nfa.start_status)
        init_status_trans = self.epsilon_closure(init_status.copy())
        # 创建第一个节点
        new_dfa_point = self.lex_dfa.dfa_graph.vcount()
        self.lex_dfa.dfa_graph.add_vertex(1)  # 加一个结点
        self.lex_dfa.start_status = new_dfa_point
        dfa_status_stack = list()
        dfa_status_stack.append(new_dfa_point)
        self.lex_dfa.mvexs.append(init_status_trans)  # NFA起点的epsilon转移集合赋值给第一个节点
        self.alphabet.remove('@')  # 删除空字符
        while dfa_status_stack:
            top = dfa_status_stack.pop()
            for i in self.alphabet:
                temp = self.epsilon_closure(self.nfa_move(self.lex_dfa.mvexs[top], i))
                if not temp:
                    continue
                if temp not in self.lex_dfa.mvexs:  # 如果该状态不存在
                    temp_dfa_status = self.lex_dfa.dfa_graph.vcount()
                    self.lex_dfa.dfa_graph.add_vertex(1)
                    if self.lex_nfa.end_status in temp:
                        self.lex_dfa.end_status.append(temp_dfa_status)
                    self.lex_dfa.mvexs.append(temp)

                    dfa_status_stack.append(temp_dfa_status)  # 将新的状态加入栈中
                    position = temp_dfa_status

                else:
                    position = self.lex_dfa.mvexs.index(temp)
                self.lex_dfa.dfa_graph.add_edge(top, position, label=i)
        self.lex_dfa.node_name = [chr(i) for i in range(ord('A'), ord('A')+len(self.lex_dfa.mvexs))]
        self.lex_dfa.alphabet = self.alphabet
        # print(self.lex_dfa.node_name)

    def is_exist(self, a, b):  # 判断边是否存在并返回边标签
        try:
            eid = self.lex_dfa.dfa_graph.get_eid(a, b)
            # print(self.lex_dfa.dfa_graph.es[eid]['label'])
            return self.lex_dfa.dfa_graph.es[eid]['label']
        except ig.InternalError:
            return ''

    def merge_two_node(self, a, b):
        for i in range(len(self.lex_dfa.mvexs)):
            if i == b:
                for j in range(len(self.lex_dfa.mvexs)):
                    label = self.is_exist(b, j)
                    # print(label)
                    if label != '':
                        if j == b:
                            self.lex_dfa.dfa_graph.add_edge(a, a, label=label)
                        else:
                            self.lex_dfa.dfa_graph.add_edge(a, j, label=label)
                        self.lex_dfa.dfa_graph.delete_edges(self.lex_dfa.dfa_graph.get_eid(b, j))
                        self.lex_dfa.mvexs[b] = list()
            else:
                for j in range(len(self.lex_dfa.mvexs)):
                    label = self.is_exist(i, b)
                    # print(label)
                    if j == b and label != '':
                        self.lex_dfa.dfa_graph.add_edge(i, a, label=label)
                        self.lex_dfa.dfa_graph.delete_edges(self.lex_dfa.dfa_graph.get_eid(i, j))
                        self.lex_dfa.mvexs[b] = list()
                        break

    def minimize_dfa(self):
        no_end_list = []  # 非终结状态集合
        end_list = self.lex_dfa.end_status  # 终结状态集合
        for i in range(len(self.lex_dfa.mvexs)):  # 找到非终结状态
            if i not in end_list:
                no_end_list.append(i)
        divide_list = list()  # 用于存储划分的集合以及是否可继续划分
        divide_list.append([no_end_list, True])
        divide_list.append([end_list, True])
        flag = True
        while flag:
            for j in range(len(divide_list)):
                can_no_divided = 0
                if len(divide_list[j][0]) == 1:
                    divide_list[j][1] = False
                    continue

                for i in self.lex_dfa.alphabet:
                    num_list = list()  # 存放DFA经过某个字母转换到的结果集
                    status_map = list()  # 放了每个节点的转换后属于的集合序号——该节点本身序号
                    for k in range(len(divide_list[j][0])):
                        trans_status = self.lex_dfa.status_matrix1.loc[divide_list[j][0][k]][i]
                        status_in_num = -1  # 转换状态的集合序号
                        for d_index in range(len(divide_list)):
                            if trans_status in divide_list[d_index][0]:
                                status_in_num = d_index
                        if status_in_num == -1:
                            num_list.append(status_in_num)  # 新增集合序号
                        else:
                            if status_in_num not in num_list:  # 防止集合序号重复
                                num_list.append(status_in_num)
                        status_map.append([status_in_num, divide_list[j][0][k]])

                    if len(num_list) == 1:
                        can_no_divided += 1
                        continue
                    else:
                        for l in range(len(num_list)):
                            temp_list = list()
                            for k in range(len(status_map)):
                                if num_list[l] == -1 and status_map[k][0] == -1:  # 需要划分的
                                    status_map[k][0] = -2  # 表示删除状态
                                    temp_list.append(status_map[k][1])
                                    break
                                else:
                                    if status_map[k][0] == num_list[l]:  # 根据集合序号进行划分
                                        temp_list.append(status_map[k][1])
                            divide_list.append([temp_list, True])
                        divide_list.pop(j)  # 删除该位置上元素
                        j -= 1
                        break  # 当前集合结束，调到下一个集合位置
                if can_no_divided == len(self.alphabet):  # 如果一个集合经过转换后还是集合本身，则不需要进行划分
                    divide_list[j][1] = False

            flag = False
            for d in divide_list:
                if d[1]:
                    flag = True
                    break
        # 更新开始状态和接收状态
        new_start = self.lex_dfa.start_status
        new_end = set()
        for dl in range(len(divide_list)):
            if len(divide_list[dl][0]) > 1:
                represent = divide_list[dl][0][0]
                for dl2 in range(1, len(divide_list[dl][0])):  # 找到结束状态和开始状态
                    self.merge_two_node(represent, divide_list[dl][0][dl2])
                    if self.lex_dfa.start_status == divide_list[dl][0][dl2]:
                        new_start = represent
                    if divide_list[dl][0][dl2] in self.lex_dfa.end_status:
                        new_end.add(represent)
            else:
                if divide_list[dl][0][0] in self.lex_dfa.end_status:
                    new_end.add(divide_list[dl][0][0])
        self.lex_dfa.min_dfa_start = new_start
        self.lex_dfa.min_dfa_end = list(new_end)

