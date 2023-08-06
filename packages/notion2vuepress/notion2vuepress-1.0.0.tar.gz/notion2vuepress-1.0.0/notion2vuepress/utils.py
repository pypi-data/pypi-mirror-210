import datetime
import logging
import os
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('notion2markdown')


def random_name():
    """随机文件名称"""
    return str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + str(random.randint(0, 100))


def create_file_folder(directory):
    """创建文件夹"""
    if not os.path.exists(directory):
        os.makedirs(directory)
