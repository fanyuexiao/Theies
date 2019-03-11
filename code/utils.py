import os
from model.ann import *

CH = '\\'

d = 0.03

def judgeFileExist(path):
    dir = path[0: path.rindex(CH) + 1]
    if dir == "":
        dir = "." + CH
    return judgeDirExist(dir) and os.path.isfile(path)

def judgeDirExist(dir):
    return os.path.exists(dir)

def judgeFileExistAndDelCreate(path):
    dir = path[0: path.rindex(CH) + 1]
    if (judgeDirExist(dir)) :
        if (os.path.isfile(path)) :
            os.remove(path)
    else:
        os.mkdir(dir)
    file = open(path, 'w')
    file.close()

def updateAndSaveIPs(IPs, path):
    judgeFileExistAndDelCreate(path)
    with open(path, "a+") as f:
        i = 0
        s = ""
        for IP in IPs:
            i += 1
            if i % 10000 == 0:
                f.write(s)
                s = ""
            for m in IP:
                s += str(m) + " "
            s += "\n"
        f.write(s)

def updateAndSaveX1Y(trainDataX1, path):
    updateAndSaveIPs(trainDataX1, path)

def updateAndSaveX1X2X3Y(trainDataX1X2X3, path):
    updateAndSaveIPs(trainDataX1X2X3, path)



def getIPsFromFile(path):
    with open(path) as f:
        IPs = []
        for fLine in f:
            fLine = fLine.split('\n')[0]
            arr = fLine.split(' ')
            IP = []
            IP.append(arr[0])
            IP.append(float(arr[1]))
            IP.append(int(arr[2]))
            IP.append(int(arr[3]))
            IP.append(int(arr[4]))
            for i in range(5, len(arr)-1 ):
                IP.append(int(arr[i]))
            IPs.append(IP)
        return IPs

def lastRA(IPs, es, delta):
    return raForIPs(IPs, es, delta, StaticRsvtStrategy())

def newRA(IPs, es, delta, model):
    return raForIPs(IPs, es, delta, DynamicRsvtStrategy(model))

# 原始方法回溯分析
def raForIPs(IPs, es, delta, strategy):
    l1,l2,n1,n2 = 0,0,0,0
    for IP in IPs:
        # 0:国家名 1:初始概率 2:保险年 3:总保险期数 4:开始期数 5-:保单赔付过程
        if filter(IP, es):
            L1,L2,N1,N2 = raForIP(IP, es, delta, rsvtStrategy=strategy)
            l1 += L1
            l2 += L2
            n1 += N1
            n2 += N2
    # 不利偏差额
    B = n1 + n2 - l1 - l2
    # 不利偏差率
    BR = B / (n1 + n2)
    # 实际偏差
    RealB = n1 - l1
    # 实际偏差率
    RealBR = RealB / n1
    return (B, BR, RealB, RealBR), (l1,l2,n1,n2)

def filter(IP, es):
    if IP[4] > es or IP[4] + IP[3] - 1 < es:
        return False
    return True

# es 被回溯的期数， es+delta 回溯的时间点
# 回溯分析 es期还款时刻发生后，我们对未到期准备金的评估；
# 与 es+delta 期还款时刻发生后，我们对es期还款时刻后的回溯分析
def raForIP(IP, es, delta, rsvtStrategy):
    startSeason = IP[4]
    loanSeason = IP[3]
    priceRate = IP[1]

    # es 还款时刻发生后的准备金评估，即对es时刻之后的准备金进行评估
    RsvtEs,ppEs = rsvtStrategy.cal(IP, es)
    # es + delta
    RsvtEsDelta,ppEsDelta = rsvtStrategy.cal(IP, es+delta)
    # 真实的还款额
    left = getIndexInIPFromSeason(IP, es + 1)
    right = getIndexInIPFromSeason(IP, es+1+delta)
    if right > len(IP):
        right = len(IP)
    realPaid = discountCash(IP[left:right], es+1)

    L1 = discountCash([ppEs for j in range(left, right)], es+1)
    L2 = RsvtEs - L1

    N1 = realPaid
    N2 = RsvtEsDelta

    return L1,L2,N1,N2

def getIndexInIPFromSeason(IP, s):
    return s - IP[4] + 5

# 参数中的 i 表示未发生赔款的期数
# 即 i 从2开始逐步往后运算
def getX1X2X3DataFromIP(IP, i):
    i = i + 4
    index = i - 4 - 1  # 上一个的index
    if i < 8:
        if i == 6:
            return 0, 0, IP[i - 1]
        elif i == 7:
            return 0, IP[i - 2], IP[i - 1]
    else:
        x1, x2, x3 = 0, 0, 0
        n1, n2, n3 = 0, 0, 0
        if (index) % 3 == 0:
            n = int(index / 3)
            n1 = 4 + n
            n2 = n1 + n
            n3 = n2 + n
        if index % 3 == 1:
            n = int(index / 3)
            n1 = 4 + n + 1
            n2 = n1 + n
            n3 = n2 + n
        if index % 3 == 1:
            n = int(index / 3)
            n1 = 4 + n + 1
            n2 = n1 + n + 1
            n3 = n2 + n

        s = 0
        for j in range(5, i):
            s += IP[j]
            if j == n1:
                x1 = s / (n1 - 4)
                s = 0
            elif j == n2:
                x2 = s / (n2 - n1)
                s = 0
            elif j == n3:
                x3 = s / (n3 - n2)
                s = 0
        return x1, x2, x3

# 从i时刻起，计算IP未到期准备金
def calculateReservations(IP, i, rsvtStrategy):
    return rsvtStrategy.cal(IP, i)

# 折现
def discountCash(array, firstElementYear):
    if len(array) == 0:
        return 0
    cashRate = (1/(1+d))**((firstElementYear-1)/4)
    sum = 0
    for s in array:
        cashRate *= ((1 / (d + 1))**(1/4))
        sum += s * cashRate
    return sum

class RsvtStrategy(object):
    def cal(self, IP, i):
        return 0,0

class StaticRsvtStrategy(RsvtStrategy):
    # i 表示还款时刻的时间发生后
    def cal(self, IP, i):
        startSeason = IP[4]
        loanSeason = IP[3]
        priceRate = IP[1]
        # 评估准备金开始的时刻，在IP中的index
        index = i - startSeason + 1 + 5
        if startSeason + loanSeason - 1 > i and startSeason <= i:
            # x1,x2,x3 = getX1X2X3DataFromIP(IP, index)
            array = [priceRate for k in range(index, len(IP))]
            return discountCash(array, i+1), priceRate
        return 0,0

class DynamicRsvtStrategy(RsvtStrategy):
    # i 表示还款时刻的时间发生后
    def __init__(self, model):
        self.model = model

    def cal(self, IP, i):
        startSeason = IP[4]
        loanSeason = IP[3]
        priceRate = IP[1]
        # 评估准备金开始的时刻，在IP中的index
        index = i - startSeason + 1 + 5
        if index >= len(IP):
            return 0,0
        x1,x2,x3 = getX1X2X3DataFromIP(IP, index-4)
        np = self.model.getProb([priceRate, x1,x2,x3])

        if startSeason + loanSeason - 1 > i and startSeason <= i:
            # x1,x2,x3 = getX1X2X3DataFromIP(IP, index)
            array = [np for k in range(index, len(IP))]
            return discountCash(array, i+1), np
        return 0,0

def log(str, path):
    with open(path, "a+") as f:
        f.write(str + "\n")

def readResult(path):
    with open(path) as f:
        make = {}
        key = "default"
        for fLine in f:
            A = fLine.split('\n')[0].split(' ')
            if len(A) == 4:
                key = A[0] + "_" + A[3]
                make[key] = []
            elif len(A) == 9:
                arr = [float(A[i]) for i in range(1, len(A))]
                make[key].append(arr)
        return make
