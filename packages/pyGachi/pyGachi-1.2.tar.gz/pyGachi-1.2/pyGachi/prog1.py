import numpy as np
import matplotlib.pyplot as plt

# определяем координаты сетки
u, v = np.mgrid[0:3*np.pi:100j, -np.pi:np.pi:100j]

# задаем х, y, z шара
x = u * np.cos(u) * (np.cos(v) + 1)
y = u * np.sin(u) * (np.cos(v) + 1)
z = u * np.sin(v)

# рисуем систему координат
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

# рисуем фигуру
ax.plot_wireframe(x, y, z)

plt.show()

import numpy as np
import matplotlib.pyplot as plt

# определяем координаты сетки
u, v = np.mgrid[0:3*np.pi:100j, -np.pi:np.pi:100j]

# задаем х, y, z шара
x = u * np.cos(u) * (np.cos(v) + 1)
y = u * np.sin(u) * (np.cos(v) + 1)
z = u * np.sin(v)

# рисуем систему координат
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

# рисуем фигуру
ax.plot_surface(x, y, z, cmap='inferno')

plt.show()
