import re
import os
from utils.utils_logger import get_logger

# 获取当前函数名作为日志文件夹名
get_filename = os.path.basename(__file__)
logger = get_logger(get_filename)


def cut_str(sys_desc):
    sys_desc = sys_desc.replace('\r', '').replace('\n', '')  # 去除换行符和回车符
    logger.info(sys_desc)

    manufacturer = sys_desc[0:6]
    logger.info(manufacturer)

    products_model = sys_desc[-20:].strip()

    ce_index = products_model.find('CE')
    if ce_index != -1:
        products_model = products_model[ce_index:]
    else:
        products_model = ''

    logger.info(products_model)
    logger.info('==========================')
    device = {'manufacturer': manufacturer, 'products_model': products_model}

    return device


def convert_seconds_to_time(seconds):
    # 计算年、月、日、时、分、秒
    years = seconds // (365 * 24 * 60 * 60)
    remaining_seconds = seconds % (365 * 24 * 60 * 60)

    months = remaining_seconds // (30 * 24 * 60 * 60)
    remaining_seconds = remaining_seconds % (30 * 24 * 60 * 60)

    days = remaining_seconds // (24 * 60 * 60)
    remaining_seconds = remaining_seconds % (24 * 60 * 60)

    hours = remaining_seconds // (60 * 60)
    remaining_seconds = remaining_seconds % (60 * 60)

    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60

    # logger.info(years, months, days, hours, minutes, seconds)
    uptime = {
        'years': years,
        'months': months,
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds
    }
    logger.info(type(uptime))
    return uptime


# 获取设备位置信息
def devices_location_info(sys_name):
    location_info = {
        'data_center': '',
        'block': '',
        'cabinet': '',
        'start_u': '',
        'network_area': '',
        'device_type': ''
    }

    # 数据中心（data_center）
    if sys_name[:2] == 'YZ':
        location_info['data_center'] = '亦庄'
    elif sys_name[:2] == 'XW':
        location_info['data_center'] = '西五环'
    elif sys_name[:2] == 'YJ':
        location_info['data_center'] = '翌景'

    # 机房编号（block）
    location_info['block'] = sys_name[4]

    # 机柜位置编号（cabinet）
    location_info['cabinet'] = sys_name[5:8]

    # 起始U位（start_u）
    location_info['start_u'] = sys_name[9:12]

    # 网络区域（network_area）
    network_area_mapping = {
        'NTS': '测试环境',
        'CR': '核心区',
        'IA': '内联接入区',
        'INA': '互联网接入A区'
    }
    network_area_start = 13
    network_area_end = sys_name.find('-', network_area_start)
    if network_area_end != -1:
        network_area = sys_name[network_area_start:network_area_end]
        for key in network_area_mapping:
            if key in network_area:
                location_info['network_area'] = network_area_mapping[key]
                break
        else:
            location_info['network_area'] = ''

    # 设备类型（device_type）
    device_type_mapping = {
        'SW': '交换机',
        'RT': '路由器',
        'DWDM': '光传输',
        'LB': '负载均衡',
        'FW': '防火墙',
        'DNS': '域名解析',
        'GSLB': '全局负载',
        'NTP': '时钟源'
    }
    device_type_start = network_area_end + 1
    if device_type_start < len(sys_name):
        device_type = sys_name[device_type_start:]
        for key in device_type_mapping:
            if key in device_type:
                location_info['device_type'] = device_type_mapping[key]
                break
        else:
            location_info['device_type'] = ''
    return location_info
