import numpy as np
import matplotlib.pyplot as plt
import time


def rastrigin(x, y):  # 定义目标函数
    A = 10
    return A * 2 + x ** 2 - A * np.cos(2 * np.pi * x) + y ** 2 - A * np.cos(2 * np.pi * y)


dx, dy = [1, 0, -1, 0], [0, 1, 0, -1]


def initialize_ant(max1, min1, max2, min2, n):  # 初始化蚁群
    interval1 = (max1-min1)/n  # 计算区间间隔
    interval2 = (max2-min2)/n
    ant_num = np.ones((n, n))  # 蚂蚁数量分布
    ant_position = np.zeros((n, n, 2))  # 蚂蚁所在位置(坐标)
    for i in range(n):
        x1 = min1 + (i+1/2)*interval1
        for j in range(n):
            x2 = min2 + (j+1/2)*interval2
            ant_position[i][j] = [x1, x2]
    return ant_position, ant_num, interval1, interval2


def count_fitness(ant_position, n):  # 计算蚂蚁适应度
    fit = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            fit[i][j] = rastrigin(ant_position[i][j][0], ant_position[i][j][1])
    return fit


def roulette(p):  # 定义轮盘赌
    if np.sum(p) == 0:
        return -1
    prob = p/np.sum(p)  # 计算蚂蚁的迁移概率
    r = np.random.random()
    prob1 = 0.0
    for index in range(4):
        prob1 += prob[index]
        if r < prob1:
            return index


def update_tau(tau, delta_tau, rho):  # 蚂蚁更新策略
    return (1-rho)*tau + delta_tau


def ant_move_and_update(ant_num, fit, tau, n, alpha, beta, rho, c1=1):  # 蚂蚁的移动
    count = 1  # 移动次数
    while count > 0:
        count = 0
        nonzero_index = np.where(ant_num != 0)
        nonzero_index = list(zip(*nonzero_index))  # 有蚂蚁的区间的索引
        delta_tau = np.zeros((n, n))  # 信息素增量
        for index in nonzero_index:  # 遍历所有有蚂蚁的区间
            while ant_num[index[0]][index[1]] != 0:  # 遍历区间内所有蚂蚁
                prob = np.zeros((4, 1))
                for i in range(4):
                    x, y = index[0] + dx[i], index[1] + dy[i]
                    if 0 <= x < n and 0 <= y < n and fit[x][y] < fit[index[0]][index[1]]:
                        prob[i] = tau[x][y] ** alpha * (fit[index[0]][index[1]] - fit[x][y]) ** beta
                move_index = roulette(prob)  # 使用轮盘赌的策略进行蚂蚁迁移
                if move_index != -1:  # 蚂蚁迁移
                    x, y = index[0] + dx[move_index], index[1] + dy[move_index]  # 迁移后区间 索引
                    ant_num[index[0]][index[1]] -= 1  # 久区域的蚂蚁减少
                    ant_num[x][y] += 1  # 新区域蚂蚁数量加一
                    count += 1
                    delta_tau[x][y] += c1 * (fit[index[0]][index[1]] - fit[x][y])
                else:  # 如果四个方向没有可以去的地方则跳过这个区间
                    break
        tau = update_tau(tau, delta_tau, rho)
    return nonzero_index


# 初始化参数
alpha, beta, rho = 1, 2, 0.1
n = 25  # 单个维度的蚂蚁数量
max1, min1, max2, min2 = 5.12, -5.12, 5.12, -5.12
best_value = []
tau = np.ones((n, n))  # 初始化信息素

# 开始蚁群算法
start_time = time.time()
ant_position, ant_num, len1, len2 = initialize_ant(max1, min1, max2, min2, n)  # 初始化蚂蚁
fit = count_fitness(ant_position, n)  # 计算对应适应度
extremum = []  # 存放极值点
ant_list = []  # 存放蚂蚁位置和区间间隔

index = ant_move_and_update(ant_num, fit, tau, n, alpha, beta, rho)
for i in index:
    ant_list.append([ant_position[i[0]][i[1]], len1, len2])
serial_num = 0  # 记录区间数目
# print(ant_list)
while len(ant_list) > serial_num:  # 广度优先搜索
    ant = ant_list[serial_num]
    if ant[1] < 1e-5 and ant[2] < 1e-5:
        extremum.append([ant[0], rastrigin(ant[0][0], ant[0][1])])
    else:
        ant_position, ant_num, len1, len2 = initialize_ant(ant[0][0]+1/2*ant[1], ant[0][0]-1/2*ant[1],
                                                           ant[0][1]+1/2*ant[2], ant[0][1]-1/2*ant[2], n)
        fit = count_fitness(ant_position, n)
        index = ant_move_and_update(ant_num, fit, tau, n, alpha, beta, rho)
        for i in index:
            ant_list.append([ant_position[i[0]][i[1]], len1, len2])
    serial_num += 1
end_time = time.time()
consumption = end_time - start_time
extremum = sorted(extremum, key=lambda x: x[1])
print("消耗时间为：{}s".format(consumption))
for i in extremum:
    print(i)
print(len(extremum))
x = np.linspace(-5.12, 5.12, 100)
y = np.linspace(-5.12, 5.12, 100)
X, Y = np.meshgrid(x, y)
Z = rastrigin(X, Y)
x1 = [i[0][0] for i in extremum]
y1 = [i[0][1] for i in extremum]
z1 = [i[1] for i in extremum]
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis')
ax.scatter(x1, y1, z1, marker='*', color='red', s=20)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('R(x, y)')
plt.show()
