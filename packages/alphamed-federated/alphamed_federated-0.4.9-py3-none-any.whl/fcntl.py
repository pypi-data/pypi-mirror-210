"""Windows 平台 fcntl 模块替身.

由于 Windows 平台不支持 fcntl 模块，无法直接运行 mock 环境。为了方便 Windows 平台上的调试，创建本替身模块。
本模块仅能帮助 mock 代码运行起来，不具备 fcntl 模块的实际功能，因此仅可用于辅助开发。
"""

import warnings


LOCK_EX = 1
LOCK_UN = 2

def flock(*args):
    return


warnings.warn('fcntl 替身模块已加载')
