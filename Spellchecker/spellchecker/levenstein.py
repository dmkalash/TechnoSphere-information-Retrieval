import numpy as np
import math

class Levenstein:
    def __init__(self, weights):
        self.weights = weights.copy()
        for key in self.weights:
            self.weights[key] = -math.log(self.weights[key])
        self.eps = max(self.weights.values())
        # self.eps = min(self.weights.values())

    def get_distance(self, origin, fixed, alpha=1.1, coef=1):
        table = np.zeros((len(fixed) + 1, len(origin) + 1))

        for j in range(1, len(origin) + 1):
            table[0][j] = table[0, j - 1] + self.weights.get(origin[j - 1] + '_', 0)

        for i in range(1, len(fixed) + 1):
            table[i][0] = table[i - 1, 0] + self.weights.get('_' + fixed[i - 1], 0)

        # table[0] = #np.arange(len(origin) + 1)
        # table[:, 0] = #np.arange(len(fixed) + 1)

        for i in range(1, len(fixed) + 1):
            for j in range(1, len(origin) + 1):
                table[i, j] = min(table[i - 1, j] + self.weights.get('_' + fixed[i - 1], self.eps),
                                  table[i, j - 1] + self.weights.get(origin[j - 1] + '_', self.eps),
                                  table[i - 1, j - 1] + (origin[j - 1] != fixed[i - 1]) *
                                  self.weights.get(origin[j - 1] + fixed[i - 1], self.eps))
                # print(origin[j - 1], fixed[i - 1], self.weights.get(origin[j - 1] + fixed[i - 1]) )

        # print(table)
        # print('dist:', table[-1, -1])
        return alpha ** (-coef * table[-1, -1])
        # return 1 / 1 + math.exp(coef * table[-1, -1])


class Levenstein1:
    def __init__(self, weights=None):
        pass

    def get_distance(self, origin, fixed, alpha=2.7, coef=1):  # 10 TODO: вероятность
        table = np.zeros((len(fixed) + 1, len(origin) + 1))
        table[0] = np.arange(len(origin) + 1)
        table[:, 0] = np.arange(len(fixed) + 1)

        for i in range(1, len(fixed) + 1):
            for j in range(1, len(origin) + 1):
                table[i, j] = min(table[i - 1, j] + 1,
                                  table[i, j - 1] + 1,
                                  table[i - 1, j - 1] + (origin[j - 1] != fixed[i - 1]))

        # print('dist:', table[-1, -1])
        return alpha ** (-coef * table[-1, -1])
        # return 1 / 1 + math.exp(coef * table[-1, -1])
