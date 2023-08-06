def isprime(x,y):
    l = []
    for i in range(x,y+1):
        if i <2 :
            continue
        flag = 0
        for j in range(2,i//2 + 1):
            if i%j == 0:
                flag = 1
        if flag == 0:
            l.append(i)
    return l