import numpy as np
import matplotlib.pyplot as plt
t=np.linspace(0,8*np.pi,1000)
plt.figure()
plt.polar(t,np.sin(1.75*t))
plt.show()
