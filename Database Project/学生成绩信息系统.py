import pymysql
import time
import tkinter as tk
from tkinter import ttk

# 连接数据库，接受数据库的主机名、用户名、密码和数据库名称作为参数
conn = pymysql.connect(host='localhost', user='root', password='2024ai', database='数据库实验4')
# 创建游标对象，用于执行SQL语句
cursor = conn.cursor()
conn.begin()  # 开启事务
keyword = input('请输入命令:\n0:结束\n1:查询\n2:插入\n3:删除\n4:修改\n')
while not keyword.isdigit():  # 判断输入命令是否为数字
    keyword = input('{}不是定义的命令！请重新输入命令！\n'.format(keyword))
keyword = int(keyword)
# 各表的属性/列
s = {'SNO', 'SNAME'}
c = {'CNO', 'CNAME'}
sc = {'SNO', 'CNO', 'SCORE'}


def is_float(string):  # 定义判断字符串是否为数字的函数
    try:
        float(string)
        return True
    except:
        return False


def delete_condition(table, condition):  # 用于连接删除条件
    sql = ''
    if condition:
        if table == 'sc':
            for i in range(len(condition)):
                condition[i] = condition[i].upper()
                cno_index = condition[i].find('CNO') + 3
                sno_index = condition[i].find('SNO') + 3
                if cno_index != 2:
                    condition[i] = condition[i][0:cno_index] + '1' + condition[i][cno_index:]
                elif sno_index != 2:
                    condition[i] = condition[i][0:sno_index] + '1' + condition[i][sno_index:]

        for i in range(len(condition)):
            if i == 0:
                sql += '{}.'.format(table) + condition[i]
            else:
                sql += ' and {}.'.format(table) + condition[i]
    return sql


# 表格显示查询结果函数
def show_result(column, result):
    window = tk.Tk()
    window.title('查询结果')
    table = ttk.Treeview(window)
    table['columns'] = column
    table['show'] = 'headings'  # 仅显示表头
    for h in column:
        table.heading(h, text=h.upper())
        table.column(h, anchor='center')  # 居中
    for row in result:
        table.insert('', 'end', values=row)
    table.pack()  # 表格显示
    window.mainloop()  # 窗口显示


#  定义构成sql语句函数
def search_sql(col, table, condition, condition2):
    sql = 'SELECT '
    for i in range(len(col)):  # 将查找列加入
        if i == 0:
            sql += str(col[i])
        else:
            sql += ', ' + str(col[i])
    sql += ' FROM'
    if len(table) > 1:  # 需要查找的表
        for i in range(len(table)):  # 将所有改为小写字母
            table[i] = table[i].lower()
            if i == 0:
                sql += ' {}'.format(table[i])
            else:
                sql += ', {}'.format(table[i])
        if 's' in table and 'sc' in table:  # 自然连接s和sc表
            condition.append('SNO = SNO1')
        if 'c' in table and 'sc' in table:  # 自然连接c和sc表
            condition.append('CNO = CNO1')
    else:
        sql += ' {}'.format(table[0])
    if condition[0] != '' and condition:  # 条件列表不为空，将条件加入sql语句
        sql += ' WHERE '
        for i in range(len(condition)):
            if i == 0:
                sql += str(condition[i])
            else:
                sql += ' and ' + str(condition[i])
    elif condition[0] == '' and len(condition) > 1:
        sql += ' WHERE '
        for i in range(1, len(condition)):
            if i == 1:
                sql += str(condition[i])
            else:
                sql += ' and ' + str(condition[i])
    if condition2:
        sql += condition2
    return sql


# 定义操作循环
while keyword != 0:
    # 1.实现查询功能
    if keyword == 1:
        ok = True  # 用于标记列名是否均在表中
        print('-'*30, '查询', '-'*30)
        table = []  # 所需要访问的表
        # 输入需要查询的列名
        col = input('请输入需要查询的列名:(请使用\',\'将列名隔开！)\n')
        column = col.split(',')
        column = [i.strip().upper() for i in column]
        cond = input('请输入查询的条件:(请使用\',\'将条件隔开！)\n')
        condition = cond.split(',')
        condition = [i.strip() for i in condition]
        set_of_column = set()  # 用于记录所需元素的集合
        set_of_column |= set(column)
        if cond != '':  # 条件不为空
            dot = ['=', '<', '>', '>=', '<=']
            for c1 in condition:  # 记录条件中涉及到的列
                index = -1
                for d in dot:
                    index = c1.find(d)
                    if index != -1:
                        break
                set_of_column |= {c1[:index].upper().strip()}
        # 使用是否为子集来查看所涉及到的表
        if set_of_column.issubset(s):
            table = ['s']
        elif set_of_column.issubset(c):
            table = ['c']
        elif set_of_column.issubset(sc):  # 若查询只涉及到sc表则将sno和cno分别改为sno1和cno1
            table = ['sc']
            for i in range(len(condition)):
                condition[i] = condition[i].upper()
                cno_index = condition[i].find('CNO')+3
                sno_index = condition[i].find('SNO')+3
                if cno_index != 2:
                    condition[i] = condition[i][0:cno_index] + '1' + condition[i][cno_index:]
                elif sno_index != 2:
                    condition[i] = condition[i][0:sno_index] + '1' + condition[i][sno_index:]
        elif set_of_column.issubset(s | sc):
            table = ['s', 'sc']
        elif set_of_column.issubset(c | sc):
            table = ['c', 'sc']
        elif set_of_column.issubset(c | s | sc):
            table = ['c', 'sc', 's']
        else:
            ok = False
            print('!'*2, '-'*60, '!'*2)
            print(' '*19, '查询错误！请检查输入是否正确！')
            print('!'*2, '-'*60, '!'*2)
        if ok:
            sql = search_sql(column, table, condition, '')
            print(sql)
            cursor.execute(sql)
            result = cursor.fetchall()
            show_result(column, result)  # 表格显示结果

    # 2.实现插入功能
    elif keyword == 2:
        print('-'*30, '插入', '-'*30)
        elect = input('请输入需要插入的表：S(学生表)/C(课程表)/SC(成绩表)\n')  # 选择需要插入的表
        base_sql = 'INSERT INTO {} VALUE '.format(elect)  # 定义插入语句的前半段
        elect1 = elect.lower()
        if elect1 == 's':  # 插入学生表
            value1 = input('请输入学号:')
            sql = search_sql(['SNO'], ['s'], ['SNO = \'{}\''.format(value1)], '')
            #  print(sql)
            cursor.execute(sql)
            if set(cursor.fetchall()):  # 存在该学号
                print('该学号已存在！')
            else:
                value2 = input('请输入学生姓名:')
                sql = base_sql + str((value1, value2))
                cursor.execute(sql)
                if cursor.rowcount > 0:  # 影响行数大于0
                    print('插入成功!')
                else:
                    print('插入失败!')
                conn.commit()  # 提交事务
        elif elect1 == 'c':  # 插入课程表
            value1 = input('请输入课程号:')
            sql = search_sql(['CNO'], ['c'], ['CNO = \'{}\''.format(value1)], '')
            #  print(sql)
            cursor.execute(sql)
            if set(cursor.fetchall()):  # 存在该课程号
                print('该课程号已存在！')
            else:
                value2 = input('请输入课程名:')
                sql = base_sql + str((value1, value2))
                cursor.execute(sql)
                if cursor.rowcount > 0:  # 影响行数大于0
                    print('插入成功!')
                else:
                    print('插入失败!')
                conn.commit()  # 提交事务
        elif elect1 == 'sc':
            value1 = input('请输入学号:')
            value2 = input('请输入课程号:')
            sql = search_sql(['SNO1', 'CNO1'], ['sc'],
                             ['SNO1 = \'{}\''.format(value1), 'CNO1 = \'{}\''.format(value2)], '')
            #  print(sql)
            cursor.execute(sql)
            if set(cursor.fetchall()):  # 存在该成绩
                print('该成绩已存在！')
            else:  # 检查是否符合外码约束
                sql = search_sql(['SNO'], ['s'], ['SNO = \'{}\''.format(value1)], '')
                cursor.execute(sql)
                set1 = set(cursor.fetchall())
                sql = search_sql(['CNO'], ['c'], ['CNO = \'{}\''.format(value2)], '')
                cursor.execute(sql)
                set2 = set(cursor.fetchall())
                if bool(set1) and bool(set2):
                    value3 = int(input('请输入成绩:'))
                    sql = base_sql + '({}, {}, {})'.format(value1, value2, value3)
                    cursor.execute(sql)
                    if cursor.rowcount > 0:  # 影响行数大于0
                        print('插入成功!')
                    else:
                        print('插入失败!')
                    conn.commit()  # 提交事务
                else:
                    print('输入的学号或课程号不存在!')
        else:
            print('输入的"{}"表不存在！'.format(elect1))

    # 3.实现删除功能
    elif keyword == 3:
        print('-'*30, '删除', '-'*30)
        elect = input('请输入需要删除元组的表(only one)：S(学生表)/C(课程表)/SC(成绩表)\n')  # 选择需要删除的表
        sql = 'DELETE FROM {} WHERE '.format(elect)  # 基础删除语句
        if elect.lower() == 's':
            cond = input('请输入删除条件，并使用\',\'隔开各个条件:\n')
            condition = [i.strip() for i in cond.split(',')]
            set_of_column = set()
            dot = ['=', '<', '>', '>=', '<=']
            for c1 in condition:  # 记录条件中涉及到的列
                index = -1
                for d in dot:
                    index = c1.find(d)
                    if index != -1:
                        break
                set_of_column |= {c1[:index].upper().strip()}
            if set_of_column.issubset(s):
                sql += delete_condition('s', condition)
                # ！！先将外键约束全部删除！！
                search = search_sql(['sno'], ['s'], condition, [])
                cursor.execute('DELETE FROM sc WHERE sc.sno1=({})'.format(search))
                cursor.execute(sql)

                if cursor.rowcount > 0:  # 影响行数大于0
                    print('删除成功!')
                else:
                    print('不存在满足该条件的课程!')
                conn.commit()  # 提交事务
            else:
                print('删除条件中涉及的列超出s表范围!')

        elif elect.lower() == 'c':
            cond = input('请输入删除条件，并使用\',\'隔开各个条件:\n')
            condition = [i.strip() for i in cond.split(',')]
            set_of_column = set()
            dot = ['=', '<', '>', '>=', '<=']
            for c1 in condition:  # 记录条件中涉及到的列
                index = -1
                for d in dot:
                    index = c1.find(d)
                    if index != -1:
                        break
                set_of_column |= {c1[:index].upper().strip()}
            if set_of_column.issubset(c):
                sql += delete_condition('c', condition)
                # ！！先将外键约束全部删除！！
                search = search_sql(['cno'], ['c'], condition, [])
                cursor.execute('DELETE FROM sc WHERE sc.cno1=({})'.format(search))
                cursor.execute(sql)

                if cursor.rowcount > 0:  # 影响行数大于0
                    print('删除成功!')
                else:
                    print('不存在满足该条件的课程!')
                conn.commit()  # 提交事务
            else:
                print('删除条件中涉及的列超出c表范围!')

        elif elect.lower() == 'sc':
            cond = input('请输入删除条件，并使用\',\'隔开各个条件:\n')
            condition = [i.strip() for i in cond.split(',')]
            set_of_column = set()
            dot = ['=', '<', '>', '>=', '<=']
            for c1 in condition:  # 记录条件中涉及到的列
                index = -1
                for d in dot:
                    index = c1.find(d)
                    if index != -1:
                        break
                set_of_column |= {c1[:index].upper().strip()}
            if set_of_column.issubset(sc):
                sql += delete_condition('sc', condition)
                # print(sql)
                cursor.execute(sql)
                if cursor.rowcount > 0:  # 影响行数大于0
                    print('删除成功!')
                else:
                    print('不存在满足该条件的课程!')
                conn.commit()  # 提交事务
            else:
                print('删除条件中涉及的列超出sc表范围!')

        else:
            print('该数据库不存在{}表!'.format(elect))

    # 4.实现修改功能
    elif keyword == 4:
        print('-'*30, '修改', '-'*30)
        table = input('请输入需要修改的表(only one S/C/SC):\n')
        update_sql = 'UPDATE {} '.format(table)  # 构建MySQL语言
        if table.lower() == 's':
            print('*'*10+'学生表只能修改学生姓名SNAME'+'*'*10)
            condition = input('请输入需要修改的条件范围，如SCORE、SNAME、CNAME等值的限制，使用\',\'隔开\n')
            while condition == '':
                condition = input('条件不可为空！请重新输入！\n')
            condition = [i.strip() for i in condition.split(',')]
            set_of_column = set()
            dot = ['=', '<', '>', '>=', '<=']
            for c1 in condition:  # 记录条件中涉及到的列
                index = -1
                for d in dot:
                    index = c1.find(d)
                    if index != -1:
                        break
                set_of_column |= {c1[:index].upper().strip()}
            if set_of_column.issubset(s | c | sc):
                if set_of_column.issubset(s):  # 只涉及s表的情况
                    pass
                else:  # 所涉及的列是否均在s、c、sc表中
                    update_sql += 'JOIN sc ON s.SNO = sc.SNO1 JOIN c ON c.CNO = sc.CNO1 '
                value1 = input('请输入修改后的姓名\n')
                update_sql += 'SET SNAME = \'{}\' WHERE '.format(value1)
                for i in range(len(condition)):
                    if i == 0:
                        update_sql += '{}'.format(condition[i])
                    else:
                        update_sql += ' and {}'.format(condition[i])
                # print(update_sql)
                cursor.execute(update_sql)
                if cursor.rowcount > 0:
                    print('修改成功!')
                else:
                    print('不存在符合条件的元组，修改失败!')
                conn.commit()  # 提交事务
            else:
                print('修改失败!\n涉及的列超出数据库范围!')

        elif table.lower() == 'c':
            print('*' * 10 + '课程表只能修改课程名称CNAME' + '*' * 10)
            condition = input('请输入需要修改的条件范围，如SCORE、SNAME、CNAME等值的限制，使用\',\'隔开\n')
            while condition == '':
                condition = input('条件不可为空！请重新输入！\n')
            condition = [i.strip() for i in condition.split(',')]
            set_of_column = set()
            dot = ['=', '<', '>', '>=', '<=']
            for c1 in condition:  # 记录条件中涉及到的列
                index = -1
                for d in dot:
                    index = c1.find(d)
                    if index != -1:
                        break
                set_of_column |= {c1[:index].upper().strip()}
            if set_of_column.issubset(s | c | sc):
                if set_of_column.issubset(c):  # 只涉及s表的情况
                    pass
                else:  # 所涉及的列是否均在s、c、sc表中
                    update_sql += 'JOIN sc ON c.CNO = sc.CNO1 JOIN s ON s.SNO = sc.SNO1 '
                value1 = input('请输入修改后的课程名称:\n')
                update_sql += 'SET CNAME = \'{}\' WHERE '.format(value1)
                for i in range(len(condition)):
                    if i == 0:
                        update_sql += '{}'.format(condition[i])
                    else:
                        update_sql += ' and {}'.format(condition[i])
                # print(update_sql)
                cursor.execute(update_sql)
                if cursor.rowcount > 0:
                    print('修改成功!')
                else:
                    print('不存在符合条件的元组，修改失败!')
                conn.commit()  # 提交事务
            else:
                print('修改失败!\n涉及的列超出数据库范围!')

        elif table.lower() == 'sc':
            print('*'*10+'成绩表只能修改学生成绩SCORE'+'*'*10)
            condition = input('请输入需要修改成绩的条件范围，如SCORE、SNAME、CNAME等值的限制，字符需要用\'\'，使用\',\'隔开\n')
            while condition == '':
                condition = input('条件不可为空！请重新输入！\n')
            condition = [i.strip() for i in condition.split(',')]
            set_of_column = set()
            dot = ['=', '<', '>', '>=', '<=']
            for c1 in condition:  # 记录条件中涉及到的列
                index = -1
                for d in dot:
                    index = c1.find(d)
                    if index != -1:
                        break
                set_of_column |= {c1[:index].upper().strip()}
            if set_of_column.issubset(s|sc|c):  # 所涉及的列是否均在s、c、sc表中
                update_sql += 'JOIN s ON s.SNO = sc.SNO1 JOIN c ON c.CNO = sc.CNO1 '
                score = input('请输入修改后成绩的值\n')
                while not is_float(score):  # 判断输入是否为数字
                    score = input('输入并不是数字！请重新输入修改后成绩的值\n')
                score = float(score)
                update_sql += 'SET SCORE = {} WHERE '.format(score)
                for i in range(len(condition)):
                    if i == 0:
                        update_sql += condition[i]
                    else:
                        update_sql += ' and ' + condition[i]
                # print(update_sql)
                cursor.execute(update_sql)
                if cursor.rowcount > 0:  # 影响行数大于0
                    print('修改成功!')
                else:
                    print('不存在符合条件的元组，修改失败!')
                conn.commit()  # 提交事务
            else:
                print('修改失败!\n涉及的列超出数据库范围!')

        else:
            print('{}表不存在！'.format(table))

    else:
        print('{}不是规定命令！\n'.format(keyword))
    keyword = input('请输入命令:\n0:结束\n1:查询\n2:插入\n3:删除\n4:修改\n')
    while not keyword.isdigit():
        keyword = input('{}不是定义的命令！请重新输入命令！\n'.format(keyword))
    keyword = int(keyword)
conn.close()
print('-'*30, '结束操作', '-'*30)
time.sleep(3)
exit()
