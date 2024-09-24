# 导入sys模块：sys模块提供了对Python解释器相关功能的访问，包括模块搜索路径
import sys
# 导入Path模块：Path模块是pathlib模块的一部分，用于处理文件系统路径
from pathlib import Path

# 将当前文件所在目录的字符串形式添加到sys.path：sys.path.append(str(Path(__file__).parent))将当前文件所在目录的字符串形式添加到sys.path列表中
sys.path.append(str(Path(__file__).parent))
# 这样，Python解释器在搜索模块时，会先查找这个目录