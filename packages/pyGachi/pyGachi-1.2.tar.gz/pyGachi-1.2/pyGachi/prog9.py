from random import *
ошибки = 0
for i in range(10):
    a = randint(2,10)
    b = randint(2,10)
    r = int(input(str(a)+' x '+str(b)+' = '))
    if r!=a*b:
          print('Неверно. Ответ = ',b)
          ошибки+=1
print('Число ошибок: ',ошибки)
if ошибки==0: print('отлично')
elif 8<=ошибки<=9: print('хорошо')
elif 6<=ошибки<=7: print('удовлетворительно')
elif ошибки<6: print('плохо')
