import numpy as np
import matplotlib.pyplot as plt
# Независимая (x) и зависимая (y) переменные
# Линейная зависимость
t = np.linspace(0,5*np.pi,1000)
x = t * np.sin(t)
y = t * np.cos(t)
plt.plot(x, y)
plt.show()
