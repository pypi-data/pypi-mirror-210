import numpy as np
a=np.random.randint(1,11,size=(5,5))
print(a)

частота= {n:0 for n in range(1,11)}
print(частота)
for i in range(5):
   for j in range(5):
       частота[a[i,j]]+=1
print(частота)
