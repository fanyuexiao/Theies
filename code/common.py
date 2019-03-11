from utils import *

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = curPath[:curPath.find("\\fyx")+len("\\fyx")]  # 获取myProject，也就是项目的根路径

DATA_DIR = os.path.abspath(rootPath + CH + 'D')
