# import matplotlib.pyplot as plt
# import matplotlib.cm as cm
# import numpy as np
#
# # Создаем цветовую карту
# cmap = plt.get_cmap('seismic')
#
# # Индексы, для которых хотим получить цвета (от 0 до 1)
# indices = np.linspace(0, 1, 11)
#
# # Получаем цвета по индексам
# colors = cmap(indices)
#
# # Выводим значения цветов
# for i, color in zip(indices, colors):
#     print(f"Индекс: {i:.2f}, Цвет: {color}")
#
# # Пример использования цветов в графиках
# fig, ax = plt.subplots()
# for i, color in zip(indices, colors):
#     ax.plot([0, 1], [i, i], color=color, label=f"Индекс: {i:.2f}")
#
# ax.legend()
# plt.show()
import random

for i in range(50):
    print(random.randint(0, 5))