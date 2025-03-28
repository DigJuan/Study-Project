import regex_to_DFA


def read_regular():  # 读取多行/一行正则表达式，并用|连接
    reg = input('请输入正则表达式：(空串为结束)\n')
    while True:
        x = input()
        if x != '':
            reg += '|' + x
        else:
            return reg


def main():
    # regex_input = read_regular()
    regex_input = '(a|b)*abb'  # 'a(b|c)*(b?d)+'
    print(regex_input)
    lex = regex_to_DFA.Lex()
    lex.get_nfa(regex_input)
    lex.lex_nfa.adjacency_matrix_and_status_matrix()
    print(f'NFA的开始状态为{lex.lex_nfa.start_status}, 接收状态为{lex.lex_nfa.end_status}')
    lex.lex_nfa.draw_graph()
    lex.get_dfa()
    lex.lex_dfa.adjacency_matrix_and_status_matrix()
    print(f'DFA的开始状态为{lex.lex_dfa.node_name[lex.lex_dfa.start_status]}, 接收状态为{[lex.lex_dfa.node_name[i] for i in lex.lex_dfa.end_status]}')
    lex.lex_dfa.draw_graph()
    lex.minimize_dfa()
    lex.lex_dfa.min_adjacency_matrix_and_status_matrix()
    print(f'最小化DFA的开始状态为{lex.lex_dfa.min_dfa_start}, 接收状态为{lex.lex_dfa.min_dfa_end}')
    lex.lex_dfa.draw_min_dfa()


if __name__ == "__main__":
    main()
