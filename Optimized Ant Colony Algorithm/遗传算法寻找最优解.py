import math
import matplotlib.pyplot as plt
import numpy as np
import time


def rastrigin(x, y):  # 定义目标函数
    A = 10
    return A * 2 + x ** 2 - A * np.cos(2 * np.pi * x) + y ** 2 - A * np.cos(2 * np.pi * y)


def create_population(max1, min1, max2, min2, num_of_population):  # 初始化种群
    population = np.zeros((num_of_population, 2))
    for p in range(num_of_population):
        population[p][0] = (max1 - min1) * np.random.random() + min1
        population[p][1] = (max2 - min2) * np.random.random() + min2
    return population


def count_fit(population):  # 计算适应度
    fit = np.zeros((len(population), 1))
    for p in range(len(population)):
        fit[p] = 1/(rastrigin(population[p][0], population[p][1])+0.01)  # 增加0.1来避免除以零
    return fit


def selection(population, fit, num):  # 选择
    new = np.zeros((num, 2))
    prob = fit / np.sum(fit)
    for i in range(num):
        r = np.random.random()
        prob1 = 0.0
        for index in range(len(prob)):  # 采用轮盘赌的策略
            prob1 += prob[index]
            if r < prob1:
                new[i] = population[index]
                break
    return new


def variation(population, pm, max1, min1, max2, min2):  # 变异操作
    variation_population = []
    for p in population:
        if pm > np.random.random():
            new_p = np.zeros(2)
            variation_num = np.random.random()*2  # 变异基因个数
            if math.ceil(variation_num) == 1:  # 变异基因个数为1则随机变异一个基因
                if variation_num < 0.5:
                    new_p[0] += (-1) ** math.ceil(np.random.random() * 2) * np.random.random() * min(max1 - p[0],
                                                                                                 min1 - p[0]) / 10
                else:
                    new_p[1] += (-1) ** math.ceil(np.random.random() * 2) * np.random.random() * min(max2 - p[1],
                                                                                                 min2 - p[1]) / 10
            else:
                new_p[0] += (-1) ** math.ceil(np.random.random() * 2) * np.random.random() * min(max1 - p[0],
                                                                                             min1 - p[0]) / 10
                new_p[1] += (-1) ** math.ceil(np.random.random() * 2) * np.random.random() * min(max2 - p[1],
                                                                                             min2 - p[1]) / 10
            variation_population.append(new_p)
    return variation_population


def crossover(population, pc):  # 交叉操作
    crossover_population = []
    for i in range(0, population.shape[0], 2):
        if np.random.random() < pc:
            parent1 = population[i]
            parent2 = population[i + 1]
            child1 = np.array([parent1[0], parent2[1]])
            child2 = np.array([parent2[0], parent1[1]])
            crossover_population.extend([child1, child2])
    return np.array(crossover_population)


num_of_population, pc, pm, G = 10, 0.8, 0.2, 1000  # 种群大小，交叉率，变异率，遗传代数
max1, min1, max2, min2 = 5.12, -5.12, 5.12, -5.12
population = create_population(max1, min1, max2, min2, num_of_population)  # 1. 初始化种群
fit = count_fit(population)  # 2. 计算适应度
best_point = []
# print(population)
start_time = time.time()
for g in range(G):
    population = selection(population, fit, num_of_population)  # 3. 选择操作
    crossover_new = crossover(population, pc)  # 4. 交叉操作
    if len(crossover_new) != 0:
        population = np.vstack((population, crossover_new))
    variation_new = variation(population, pm, max1, min1, max2, min2)  # 5. 变异操作
    if len(variation_new) != 0:
        population = np.vstack((population, variation_new))
    fit = count_fit(population)
    best = max(fit)
    point = list(zip(*np.where(fit == best)))
    # print(point)
    best_point.append([population[point[0][0]], rastrigin(population[point[0][0]][0], population[point[0][0]][1])])
end_time = time.time()
consumption = end_time - start_time
print("消耗时间为：{}s".format(consumption))
# print(population)
# print(fit)
for i in best_point:
    print(i)
y = [i[1] for i in best_point]
x = list(range(G))
plt.plot(x, y)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.grid(True)
plt.ylabel('种群最优解')
plt.xlabel('遗传代数')
plt.show()

