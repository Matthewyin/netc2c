import os
import logging
import time


def get_logger(function_name):
    # 获取当前日期和时间
    current_date = time.strftime('%Y-%m-%d')
    current_hour = time.strftime('%H')

    # 创建一个名为logs/"函数名-日期"的文件夹，如果不存在的话
    log_folder = os.path.join('logs', f"{function_name}-{current_date}")
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # 初始化日志记录器
    logger = logging.getLogger(function_name)
    logger.setLevel(logging.DEBUG)

    # 创建一个文件处理器，并设置级别为DEBUG，日志文件名为当前时间的时间戳（精确到秒）.log
    log_filename = os.path.join(log_folder, f"{function_name}-{current_date}-{current_hour}.log")
    fh = logging.FileHandler(log_filename, encoding='utf-8')  # 指定字符编码为UTF-8
    fh.setLevel(logging.DEBUG)

    # 创建格式化程序
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # 将格式化程序添加到处理器
    fh.setFormatter(formatter)

    # 将处理器添加到日志记录器
    logger.addHandler(fh)

    return logger
