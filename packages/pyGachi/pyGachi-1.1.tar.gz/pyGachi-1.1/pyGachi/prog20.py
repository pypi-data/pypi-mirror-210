s=input('Задайте формулу: ')
i,n=0,0
while i<len(s) and n>=0:
    if s[i]=='(': n+=1
    elif s[i]==')': n-=1
    i+=1
if n<0: print('Неверный порядок скобок')
elif n>0: print('Несовпадает количество скобок')
else: print('Все хорошо со скобками')
