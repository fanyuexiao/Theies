from pylab import *
from utils import *

MAP = readResult("./result/trainDataRA1.txt")

def getLinesDataFromMap(MAP):
    NewMAP = {"OLD":{}, "NEW":{}}
    for key in MAP.keys():
        type = key.split("_")[0]
        delta = key.split("_")[1]

        AA = MAP[key]
        # 0：不利偏差额 1：不利偏差率 2：真实偏差额 3：真是偏差率
        # 4：l1 5：l2 6：n1 7：n2

        # line0 不利偏差率
        line0 = []
        # line1 真实偏差率
        line1 = []
        # line2 不利偏差额
        line2 = []
        # line3 真实偏差额
        line3 = []
        for A in AA:
            line0.append(A[1])
            line1.append(A[3])
            line2.append(A[0])
            line3.append(A[2])
        lines = []
        NewMAP[type][delta] = lines
        lines.append(line0)
        lines.append(line1)
        lines.append(line2)
        lines.append(line3)
    return NewMAP



NewMAP = getLinesDataFromMap(MAP)

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
for delta in NewMAP["OLD"].keys():

    lineOld = NewMAP["OLD"][delta]
    lineNew = NewMAP["NEW"][delta]
    # 不利偏差率
    plt.figure(1)
    # plt.title("buli")
    l1, = plt.plot(range(0, 80), lineOld[0][0:80])
    l2, = plt.plot(range(0, 80), lineNew[0][0:80])
    plt.legend(handles=[l1, l2], labels=["传统准备金评估方法","改进准备金评估方法"])
    plt.show()


    # 真实偏差率
    plt.figure(1)
    # plt.title("real")
    l1, = plt.plot(range(0, 80), lineOld[1][0:80])
    l2, = plt.plot(range(0, 80), lineNew[1][0:80])
    plt.legend(handles=[l1, l2], labels=["传统准备金评估方法","改进准备金评估方法"])
    plt.show()


