from utils import *

generateType = 2
IPs = getIPsFromFile("./D/IP{}.txt".format(generateType))
log_path = "./result/trainDataRA_{}.txt".format(generateType)

def last():
    log("OLD METHOD DELTA 2", log_path)
    for ss in range(1, 137):
        print("第{}季度：".format(ss))
        A, B = lastRA(IPs, ss, 2)
        log("{} {} {} {} {} {} {} {} {}".format(ss, A[0],A[1],A[2],A[3],B[0],B[1],B[2],B[3]), log_path)
        print("不利偏差额：{:.2f}；不利偏差率：{:.2f}%；实际偏差：{:.2f}；实际偏差率%：{:.2f}".format(A[0],A[1]*100,A[2],A[3]*100))
        print("l1：{:.2f}；l2：{:.2f}；n1：{:.2f}；n2：{:.2f}".format(B[0],B[1],B[2],B[3]))

    log("OLD METHOD DELTA 8", log_path)
    for ss in range(1, 131):
        A, B = lastRA(IPs, ss, 8)
        log("{} {} {} {} {} {} {} {} {}".format(ss, A[0],A[1],A[2],A[3],B[0],B[1],B[2],B[3]), log_path)
        print("第{}季度：".format(ss))
        print("不利偏差额：{:.2f}；不利偏差率：{:.2f}%；实际偏差：{:.2f}；实际偏差率%：{:.2f}".format(A[0],A[1]*100,A[2],A[3]*100))
        print("l1：{:.2f}；l2：{:.2f}；n1：{:.2f}；n2：{:.2f}".format(B[0], B[1], B[2], B[3]))

def new():
    with tf.Session() as sess:
        args = ARGS()
        FNNModel = FNN(args, sess)
        FNNModel.restoreModel("./result/model/FNNModel/{}/A0".format(generateType))
        log("NEW METHOD DELTA 2", log_path)
        for ss in range(1, 137):
            print("第{}季度：".format(ss))
            A, B = newRA(IPs, ss, 2, FNNModel)
            log("{} {} {} {} {} {} {} {} {}".format(ss, A[0],A[1],A[2],A[3],B[0],B[1],B[2],B[3]), log_path)
            print("不利偏差额：{:.2f}；不利偏差率：{:.2f}%；实际偏差：{:.2f}；实际偏差率%：{:.2f}".format(A[0],A[1]*100,A[2],A[3]*100))
            print("l1：{:.2f}；l2：{:.2f}；n1：{:.2f}；n2：{:.2f}".format(B[0], B[1], B[2], B[3]))

        log("NEW METHOD DELTA 8", log_path)
        for ss in range(1, 131):
            print("第{}季度：".format(ss))
            A, B = newRA(IPs, ss, 8, FNNModel)
            log("{} {} {} {} {} {} {} {} {}".format(ss, A[0],A[1],A[2],A[3],B[0],B[1],B[2],B[3]), log_path)
            print("不利偏差额：{:.2f}；不利偏差率：{:.2f}%；实际偏差：{:.2f}；实际偏差率%：{:.2f}".format(A[0],A[1]*100,A[2],A[3]*100))
            print("l1：{:.2f}；l2：{:.2f}；n1：{:.2f}；n2：{:.2f}".format(B[0], B[1], B[2], B[3]))

if __name__ == "__main__":
    last()
    new()