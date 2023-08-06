with open('grades.txt', encoding='UTF-8') as f:
    for line in f:
        s=line.split(' ')
        s[-1]=s[-1][0] #убрали \n
        n=0
        for i in range(1,len(s)):
            if s[i]=='5': n+=1
        if n==5: print(s[0])
