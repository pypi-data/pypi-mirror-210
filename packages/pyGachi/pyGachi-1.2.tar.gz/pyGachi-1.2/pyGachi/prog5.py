import numpy as np
a = np.random.randint(1,21,size=(5,5))
print(a)
for i in range(5):
    for j in range(5):
       if 0<=a[i,j]<=8:
           a[i,j]=0
print(a)