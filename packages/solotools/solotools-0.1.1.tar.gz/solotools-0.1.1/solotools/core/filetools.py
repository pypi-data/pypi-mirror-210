import os
import shutil
import logging

# using suggestion: 包含路径的参数均为绝对路径



def new_folder(folder_path):
    """
    创建新的文件夹
    :param folder_path: 指定新建文件夹路径
    :return:
    """
    is_Exist = os.path.exists(folder_path)  # 判断该文件夹是否存在
    if not is_Exist:  # 不存在时创建该文件夹
        os.mkdir(folder_path)
    else:
        logging.warning("当前文件夹已存在，文件夹路径为：" + folder_path)

def new_file(file_path):
    """
    新建任意后缀文件
    :param file_path:
    :return:
    """
    is_Exist = os.path.exists(file_path)  # 判断该文件夹是否存在
    if not is_Exist:  # 不存在时创建该文件夹
        cur_file = open(file_path, 'w')
        cur_file.close()
    else:
        logging.warning("当前文件夹已存在，文件夹路径为：" + file_path)


def copy_folder_to_folder(src, dst):
    """
    复制文件夹到指定文件夹路径下:(并且包含里面的文件)
    :param src:  需要复制的文件夹路径
    :param dst: 新的文件夹路径
    :return:
    """
    if not os.path.exists(dst):
        print("folder_path not exist!")
    if not os.path.exists(dst):
        print("new_folder_path not exist!")
    for root, dirs, files in os.walk(src, True):
        for eachfile in files:
            shutil.copy(os.path.join(root, eachfile), dst)

def delete_empty_folder(path):
    """
    删除指定空的文件夹
    :param path: 空文件夹地址
    :return:
    """
    # param1:需要删除的空的文件夹路径
    os.rmdir(path)

def delete_folder(path):
    """
    删除包含文件内容的文件夹
    :param path: 需要删除的文件夹路径
    :return:
    """
    shutil.rmtree(path, True)

def delete_file(file_path):
    """
    删除指定的文件
    :param file_path:  删除文件的路径
    :return:
    """
    is_Exist = os.path.exists(file_path)  # 先判断是否该文件存在
    if not is_Exist:
        logging.warning("当前文件路径不存在")
    else:
        os.remove(file_path)
