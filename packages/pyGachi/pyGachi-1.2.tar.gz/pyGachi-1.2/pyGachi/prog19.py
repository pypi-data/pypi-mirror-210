s = input('Введите строку: ')
# удаление разделителей
r='.,:;!?/\)([]'
for i in r:
    s = s.replace(i,' ')
# переворачивание
a = s.split(' ')
i=0
while i<len(a):
    if a[i]=='': del a[i]
    else: i+=1
a.reverse()
b=' '.join(a)
print(b)
