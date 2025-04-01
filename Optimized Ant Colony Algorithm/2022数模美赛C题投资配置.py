import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
# 蚂蚁转移的四个方向
dx = [0, 1, 0, -1]
dy = [1, 0, -1, 0]


def f(y, x1, x2, a2, z1, z2, u1, u2, m2, lamb=0):  # 定义目标函数
    target = lamb * (u1 * (z1 + x1) + u2 * (z2 + x2)) / (u1 + u2) - (1 - lamb) * (a2 * (z1 + x1) + m2 * (z2 + x2) + (y - a2 * x1 - m2 * x2))
    return target


def profit(y, x1, x2, z1, z2, a3, m3):  # 利润
    return a3*(z1+x1)+m3*(z2+x2) + y


def condition(y, x1, x2, a2, a3, z1, z2, m2, m3):  # 约束条件判断
    if a2 * (z1 + x1) + m2 * (z2 + x2) + (y - a2 * x1 - m2 * x2) > z1 * a3 + z2 * m3 + y:
        return True
    else:
        return False


def initialize_ant(y, z1, z2, n, a2, a3, m2, m3):  # 初始化蚂蚁分布(蚂蚁所在点)
    max1 = y / a2  # x1的上界
    min1 = -z1
    min2 = -z2
    Len_section1 = (max1-min1)/n  # x1区间的间隔
    Len_section2 = []
    Ant_position = np.zeros((n, n, 2))  # 蚂蚁位置
    Ant_num = np.ones((n, n))  # 蚂蚁数量
    for i in range(n):
        x1 = min1 + (i+1/2)*Len_section1
        max2 = (y-a2*x1)/m2  # x2的上界
        len_section2 = (max2 - min2)/n
        Len_section2.append(len_section2)  # x2区间的间隔
        for j in range(n):
            x2 = min2 + (j+1/2)*len_section2
            Ant_position[i][j] = [x1, x2]
            if not condition(y, x1, x2, a2, a3, z1, z2, m2, m3):
                Ant_num[i][j] = 0  # 不符合条件的蚂蚁清除
    return Ant_position, Ant_num, Len_section1, Len_section2  # 返回蚂蚁位置分布，蚂蚁数量分布，x1的区间的长度和x2的区间的长度


def reduction_range(y, ant_position, section_len1, section_len2, n, a2, a3, m2, m3):  # 缩小范围初始化蚁群
    Ant_position = np.zeros((n, n, 2))
    Ant_num = np.ones((n, n))
    # 确定上下界
    min1, max1 = ant_position[0] - section_len1/2, ant_position[0] + section_len1/2
    min2, max2 = ant_position[1] - section_len2/2, ant_position[1] + section_len2/2
    # 计算缩小后的区间的长度
    sec1 = (max1-min1)/n
    sec2 = (max2-min2)/n
    for i in range(n):
        x1 = min1 + (i+1/2)*sec1
        for j in range(n):
            x2 = min2 + (j+1/2)*sec2
            Ant_position[i][j] = [x1, x2]
            if not condition(y, x1, x2, a2, a3, z1, z2, m2, m3):
                Ant_num[i][j] = 0  # 不符合条件的蚂蚁清除
    return Ant_position, Ant_num, sec1, sec2


def count_fitness(Ant_position, n, y, a2, a3, z1, z2, m2, m3):  # 计算蚂蚁适应度
    fit = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if condition(y, Ant_position[i][j][0], Ant_position[i][j][1], a2, a3, z1, z2, m2, m3):
                fit[i][j] = f(y, Ant_position[i][j][0], Ant_position[i][j][1], a2, z1, z2, u1, u2, m2)
            else:
                fit[i][j] = inf
    return fit


def roulette(p):  # 定义轮盘赌
    if np.sum(p) == 0:
        return -1
    prob = p/np.sum(p)  # 计算蚂蚁转移概率
    r = random.random()
    prob1 = 0.0
    for index in range(4):
        prob1 += prob[index]
        if r < prob1:
            return index


def update_tau(tau, delta_tau, rho):  # 蚂蚁更新策略
    return (1-rho)*tau + delta_tau


def Ant_move_and_update(Ant_num, Fit, tau, n, rho, c1=5):  # 蚂蚁的移动
    count = 1  # 移动次数
    while count > 0:
        count = 0
        nonzero_index = np.where(Ant_num != 0)
        nonzero_index = list(zip(*nonzero_index))  # 有蚂蚁的区间的索引
        delta_tau = np.zeros((n, n))  # 信息素增量
        if len(nonzero_index) == 1:  # 只有一个区间有蚂蚁则不进行迁移
            break
        for index in nonzero_index:  # 遍历有蚂蚁的区间
            while Ant_num[index[0]][index[1]] != 0:  # 遍历区间内所有蚂蚁
                prob = np.zeros((4, 1))
                for i in range(4):
                    x, y = index[0] + dx[i], index[1] + dy[i]
                    if 0 <= x < n and 0 <= y < n and Fit[x][y] < Fit[index[0]][index[1]]:
                        prob[i] = tau[x][y] ** alpha * (Fit[index[0]][index[1]] - Fit[x][y]) ** beta
                move_index = roulette(prob)  # 蚂蚁使用轮盘赌迁移
                if move_index != -1:
                    x, y = index[0] + dx[move_index], index[1] + dy[move_index]  # 迁移后区间 索引
                    Ant_num[index[0]][index[1]] -= 1  # 久区域的蚂蚁减少
                    Ant_num[x][y] += 1  # 新区域蚂蚁数量加一
                    count += 1
                    delta_tau[x][y] += c1 * (Fit[index[0]][index[1]] - Fit[x][y])
                else:  # 如果四个方向没有可以去的地方则停止循环
                    break
        tau = update_tau(tau, delta_tau, rho)
    # print(tau)
    return nonzero_index  # 返回区间 索引


def get_interval(index, Ant_position, sec1, sec2):  # 用于返回蚂蚁所在区间间隔和位置
    position = Ant_position[index[0]][index[1]]
    interval1 = sec1
    if isinstance(sec2, list):
        interval2 = sec2[index[0]]
    else:
        interval2 = sec2
    return position, interval1, interval2


'''def condition(y, x1, x2, a2, a3, z1, z2, m2, m3):  # 约束条件判断
    if x1 * a2 + x2 * m2 <= y and a2 * (z1 + x1) + m2 * (z2 + x2) + (y - a2 * x1 - m2 * x2) > z1 * a3 + z2 * m3 + y:
        return True
    else:
        return False'''


inf = float('inf')  # 无穷大
data = pd.read_csv('D:\\E\\程序设计\\计算智能\\课题作业\\数据.csv', encoding='gbk')
goal = data['USD_1_pred']  # 黄金预测价格
bitcoin = data['Value_pred']  # 比特币预测价格
g = data['USD_1']
b = data['Value']
u1 = goal.var()
u2 = bitcoin.var()
times = len(goal)  # 循环迭代次数
# print(times, u1, u2, sep='\n')
# 参数设置
yy, z1, z2 = 1000, 0, 0  # 初始本金
alpha, beta, rho = 1, 2, 0.1
n = 20  # 单个维度蚂蚁数量
gold_true_value = 0
gold_value = 0
profit_record = [1000]

for t in range(times-1):
    print(t+1, ":")
    # 接收参数值
    a1, a2, a3 = goal.iloc[t], goal.iloc[t + 1], g.iloc[t + 1]  # 金价
    m1, m2, m3 = bitcoin.iloc[t], bitcoin.iloc[t + 1], b.iloc[t + 1]  # 比特币
    x1, x2 = 0, 0
    if a2 != 0:
        gold_value = a2
        gold_true_value = a3
        tau = np.ones((n, n))
        Ant_position, Ant, Len1, Len2 = initialize_ant(yy, z1, z2, n, a2, a3, m2, m3)  # 初始化蚁群分布
        Fit = count_fitness(Ant_position, n, yy, a2, a3, z1, z2, m2, m3)  # 计算对应的适应度
        if not np.all(Fit == inf):
            index = Ant_move_and_update(Ant, Fit, tau, n, rho)
            extremum = []  # 存放极值点
            Ant_list = []  # 存放蚂蚁的位置和区间的间隔
            for i in index:
                Ant_list.append(get_interval(i, Ant_position, Len1, Len2))
            serial_num = 0
            while len(Ant_list) > serial_num:  # 广度优先搜索
                ant = Ant_list[serial_num]
                if ant[1] < 0.05 and ant[2] < 0.05:  # 间隔小于0.05则将区间中点作为极值点
                    extremum.append([ant[0], f(yy, ant[0][0], ant[0][1], a2, z1, z2, u1, u2, m2)])  # 加入坐标和适应度
                else:
                    Ant_position, Ant, Len1, Len2 = reduction_range(yy, ant[0], ant[1], ant[2], n, a2, a3, m2,
                                                                    m3)  # 缩小搜索范围
                    Fit = count_fitness(Ant_position, n, yy, a2, a3, z1, z2, m2, m3)  # 计算对应的适应度
                    index = Ant_move_and_update(Ant, Fit, tau, n, rho)  # 蚂蚁移动
                    for i in index:
                        Ant_list.append(get_interval(i, Ant_position, Len1, Len2))
                serial_num += 1
            extremum = sorted(extremum, key=lambda x: x[1])
            # profit_record.append(profit(yy, extremum[0][0][0], extremum[0][0][1], a2, z1, z2, m2))  # 存放收益
            x1, x2 = extremum[0][0][0], extremum[0][0][1]  # 交易量
            yy -= (x1 * a2 + x2 * m2)
    print(x1, x2)
    profit_record.append(profit(yy, x1, x2, z1, z2, gold_true_value, m3))  # 存放收益
    z1 += x1
    z2 += x2
    print(yy, z1, z2, profit_record[t+1])
plt.plot(list(range(times)), profit_record)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.grid(True)
plt.ylabel('总资产/$')
plt.xlabel('time/days')
plt.show()
