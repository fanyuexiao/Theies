import random
from common import *
from utils import *


# 费率父类
class PRstrategySuper(object):
    def getPR(self, IP, p_):
        pass

# 费率策略0 高洪忠费率假设
class PRstrategy0(PRstrategySuper):
    def getPR(self, IP, p_):
        for i in range(len(IP)):
            if IP[i] == 1:
                return 1
        return p_

# 费率策略1 数据方案一费率假设
class PRstrategy1(PRstrategySuper):
    # 策略1中的 alpha 参数
    def __init__(self, alpha):
        self.alpha = alpha
    def getPR(self, IP, p_):
        # R: IP中发生保单赔偿的集合
        # currentIndex: 当前下一次还款的期数
        # sumOf1: 求和
        # sumOf2: 求和
        # p_: 原始概率
        currentIndex = len(IP) + 1
        sumOf1 = 0
        sumOf2 = 0
        for i in range(len(IP)):
            index = i + 1
            sumOf2 += 1/(currentIndex - index)
            if IP[i] == 1:
                sumOf1 += 1/(currentIndex - index)
        return p_ + (self.alpha * sumOf1 / sumOf2)

# 费率策略2 数据方案二费率假设
class PRstrategy2(PRstrategySuper):
    # 策略1中的 alpha 参数
    def __init__(self, alpha):
        self.alpha = alpha
    def getPR(self, IP, p_):
        # R: IP中发生保单赔偿的集合
        # numberOfR: IP中发生保单赔偿的数量
        # currentIndex: 当前下一次还款的期数
        # sumOf1: 求和
        # sumOf2: 求和
        # p_: 原始概率
        currentIndex = len(IP) + 1

        sumOf1 = 0
        sumOf2 = 0
        for i in range(len(IP)):
            index = i + 1
            sumOf2 += index / currentIndex
            if IP[i] == 1:
                sumOf1 += index / currentIndex
        return p_ + (sumOf1 / sumOf2) * self.alpha

# 数据生成参数类
class DataParams(object):
    countryNames = ['A', 'B']
    # 不同国家的定价费率
    pricingRates = [0.010, 0.08]

    # 贷款年限，每个年内四个季度还款日
    # 每个保单分别为 20个季度， 40个季度， 60个季度
    loanYears = [10, 15]
    loanSeasons = [40, 60]
    loanYearPAddPerYear = 0.004

    # 购买保单的时刻是 1,2,3,...,20
    totalYears = 20
    totalSeasons = 20 * 4

    # IP insurance policy
    numberOfIP = 100 * 10000
    # 0：高洪忠 1：数据生成方案一 2：数据生成方案二
    IPGenetateType = 1
    priceRateStrategies = [PRstrategy0(), PRstrategy1(0.3), PRstrategy2(0.3)]

# 具体策略类
class PRcalculate(object):
    def __init__(self, strategy):
        self.strategy = strategy
    def getPR(self):
        return self.strategy.getPR()

class Data(object):
    # 数据生成
    def generateData(self, dataParams):
        i = 0
        IPs = []
        while i < dataParams.numberOfIP:
            i += 1
            countryIndex = self._randCountry(dataParams)
            countryName = dataParams.countryNames[countryIndex]
            pricingRate = dataParams.pricingRates[countryIndex]

            loadYearIndex = self._randLoadYears(dataParams)
            loadYear = dataParams.loanYears[loadYearIndex]
            loadSeason = dataParams.loanSeasons[loadYearIndex]

            startSeason = self._randStartSeason(dataParams)

            # CN PR LY LS 0 0 1 1 ...
            IP = self._generateIP(countryName, self._getRealPricingRate(pricingRate, loadYear, dataParams.loanYearPAddPerYear), loadYear, loadSeason,
                            startSeason, dataParams.priceRateStrategies, dataParams.IPGenetateType)
            IPs.append(IP)

            if i % 10000 == 0:
                print(i / dataParams.numberOfIP)
        return IPs

    # countryName pricingRate loadYear loadSeason startSeason
    # IPGenetateType 0：高洪忠 1：数据生成方案一 2：数据生成方案二
    def _generateIP(self, cn, pr, ly, ls, ss, strategies, IPGenetateType=0):
        IP = [cn, pr, ly, ls, ss]
        currentPR = pr
        # 遍历所有的还款日期
        for i in range(ls):
            r = random.random()
            if r < currentPR:
                IP.append(1)
            else:
                IP.append(0)
            currentPR = strategies[IPGenetateType].getPR(IP[5:], pr)
            if currentPR > 1:
                currentPR = 1
        return IP

    def _randCountry(self, dataParams):
        return int(len(dataParams.countryNames) * random.random())

    def _randLoadYears(self, dataParams):
        return int(len(dataParams.loanYears) * random.random())

    def _randStartSeason(self, dataParams):
        return int(dataParams.totalSeasons * random.random())

    def _getRealPricingRate(self, pr_, loadYear, loanYearPAddPerYear):
        return pr_ + loadYear * loanYearPAddPerYear

class PreProcessor(object):
    def __init__(self, IPs):
        self.IPs = IPs
    def preprocessData(self):
        keyMapN = {}
        keyMapM = {}
        trainData = []
        # key countryName _ loadYear

        for IP in self.IPs:
            countryName = IP[0]
            pricingRate = IP[1]
            loadYear = IP[2]
            loadSeason = IP[3]
            startSeason = IP[4]
            keyPre = countryName + "_" + str(loadYear) + "_" + str(pricingRate)
            # 出现索赔的个数 和 总次数
            M, N = 0, 0
            for i in range(6,len(IP)):
                N += 1
                if IP[i-1] == 1:
                    M += 1
                keyEnd = '%.2f' % (float(M) / N)
                key = keyPre + "_" + keyEnd

                if key not in keyMapM:
                    keyMapM[key] = 0
                    keyMapN[key] = 0

                if IP[i] == 1:
                    lastM = keyMapM[key] + 1
                    keyMapM[key] = lastM
                lastN = keyMapN[key] + 1
                keyMapN[key] = lastN
        for key in keyMapM.keys():
            kk = key.split('_')
            x1 = float(kk[2])
            x2 = float(kk[3])
            y = float(keyMapM[key]) / keyMapN[key]
            trainData.append([x1, x2, y, keyMapN[key]])
        return trainData

    def preprocessDataX1X2X3(self):
        keyMap = {}
        trainData1 = []
        trainData3 = []
        # key countryName _ loadYear
        for IP in self.IPs:
            countryName = IP[0]
            pricingRate = IP[1]
            loadYear = IP[2]
            loadSeason = IP[3]
            startSeason = IP[4]

            keyPre = countryName + "_" + str(loadYear) + "_" + str(pricingRate)
            keyEnd = ""
            # 出现索赔的个数 和 总次数
            M, N = IP[5], 1
            for i in range(6,len(IP)):
                index = i - 4 - 1 # 上一个的index
                if i < 8:
                    keyEnd = '%.2f' % (float(M) / N)
                    N += 1
                    M += IP[i]
                else:
                    x1,x2,x3 = 0,0,0
                    n1,n2,n3 = 0,0,0
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


                    keyEnd = '%.1f' % (x1) + "_" + '%.1f' % (x2) + "_" + '%.1f' % (x3)

                key = keyPre + "_" + keyEnd
                if key not in keyMap:
                    keyMap[key] = [0,0]

                keyMap[key][0] += IP[i]
                keyMap[key][1] += 1
        for key in keyMap.keys():
            kk = key.split('_')
            if len(kk) == 6:
                x0 = float(kk[2]) # 原始 priceRate
                x1 = float(kk[3]) # x1
                x2 = float(kk[4]) # x2
                x3 = float(kk[5]) # x3
                y = float(keyMap[key][0]) / keyMap[key][1] # 概率
                trainData3.append([x0, x1, x2, x3, y, keyMap[key][0], keyMap[key][1]])
            else:
                x0 = float(kk[2])
                x1 = float(kk[3])
                y = float(keyMap[key][0]) / keyMap[key][1]
                trainData1.append([x0, x1, y, keyMap[key]])
        return trainData3, trainData1

    def preprocessDataX1X2X3NN(self):
        trainDataX1X2X3 = []
        for IP in self.IPs:
            countryName = IP[0]
            pricingRate = IP[1]
            loadYear = IP[2]
            loadSeason = IP[3]
            startSeason = IP[4]
            # 出现索赔的个数 和 总次数
            M, N = IP[5], 1
            for i in range(2,loadSeason):
                x1, x2, x3 = getX1X2X3DataFromIP(IP, i)
                trainDataX1X2X3.append([pricingRate,x1,x2,x3,IP[i+4]])
        return trainDataX1X2X3


if __name__ == "__main__":
    dataParams = DataParams()
    dataParams.IPGenetateType = 2
    dataParams.numberOfIP = 100000

    # 模拟数据的生成
    DATA = Data()
    IPs = DATA.generateData(dataParams)
    updateAndSaveIPs(IPs, DATA_DIR + CH + "IP" + str(dataParams.IPGenetateType) + ".txt")

    # 数据处理器
    PREProcessor = PreProcessor(IPs)
    trainDataX1X2X3 = PREProcessor.preprocessDataX1X2X3NN()
    trainData3, trainData1 = PREProcessor.preprocessDataX1X2X3()

    updateAndSaveX1X2X3Y(trainDataX1X2X3, DATA_DIR + CH + "trainDataX1X2X3_" + str(dataParams.IPGenetateType) + ".txt")
    updateAndSaveIPs(trainData3, DATA_DIR + CH + "resultData_" + str(dataParams.IPGenetateType) + ".txt")

    # 展示数据
    print(len(trainDataX1X2X3))
    for i in range(100):
        print(trainDataX1X2X3[i])

    print("-------------")

    for d in trainData3:
        print(d)