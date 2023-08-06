"""
一些辅助功能函数
"""

import os
from xlsxwriter.utility import xl_rowcol_to_cell
from xlsxwriter.utility import xl_cell_to_rowcol


def makedir(folder: str):
    """
    创建文件夹，在当前py文件的相对地址下，创建一个文件夹
    Args:
        folder: 相对地址后面，需要添加的新的文件夹的字符串名称
    Returns:
    """
    raw_path = os.getcwd()
    full_path = raw_path + "\\" + folder
    if not os.path.exists(folder):
        os.makedirs(full_path)





    


if __name__ == '__main__':
    makedir("ABC")
