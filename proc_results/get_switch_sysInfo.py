import os
import xml.etree.ElementTree as ET
from proc_databases import db_tables_op
from proc_devices.switch_connector import connect_to_switch
from utils.utils_logger import get_logger
from resources import dataSet_path
from utils.util_format import cut_str, convert_seconds_to_time, devices_location_info

# 获取当前函数名作为日志文件夹名
get_filename = os.path.basename(__file__)
logger = get_logger(get_filename)


def get_switch_info():
    logger.info("开始获取设备信息...")
    # 连接数据库
    db_tables_op.get_connection()
    # 全局变量 sys_manufacturer, sys_device_model

    management_ips = db_tables_op.get_management_ips()
    if not management_ips:
        logger.warning("没有可用的管理IP地址。")
        return

    switches_account = db_tables_op.get_account()
    if not switches_account:
        logger.warning("没有可用的设备账户信息。")
        return

    # 获取用户名和密码
    username, password = switches_account
    # 从配置文件中读取过滤器文件路径
    filter_file = dataSet_path.sysInfo

    for ip_address in management_ips:
        switch_info = connect_to_switch(ip_address, username, password, filter_file)

        if switch_info:
            logger.info(f"与交换机 {ip_address} 830端口通信成功。")
            try:
                # 解析XML文件
                root = ET.fromstring(switch_info)
                # 在这里根据XML的结构，提取数据并进行相应处理
                sys_name = root.find('.//{http://www.huawei.com/netconf/vrp}sysName').text
                sys_desc = root.find('.//{http://www.huawei.com/netconf/vrp}sysDesc').text
                sys_sn = root.find('.//{http://www.huawei.com/netconf/vrp}esn').text
                sys_uptime = int(root.find('.//{http://www.huawei.com/netconf/vrp}sysUpTime').text)

                uptime = convert_seconds_to_time(sys_uptime)

                sys_uptime_str = str(uptime.get('years')) + '年' + str(uptime.get('months')) + '月' + str(
                    uptime.get('days')) + '日' + str(uptime.get('hours')) + '时' + str(
                    uptime.get('minutes')) + '分' + str(
                    uptime.get('seconds')) + '秒'

                # 将数据存入数据库
                device_info = {
                    'ip_address': ip_address,
                    'hostname': sys_name,
                    'manufacturer': cut_str(sys_desc).get('manufacturer'),
                    'products_model': cut_str(sys_desc).get('products_model'),
                    'uptime': sys_uptime_str,
                    'SN': sys_sn,
                    'data_center': devices_location_info(sys_name).get('data_center'),
                    'block': devices_location_info(sys_name).get('block'),
                    'cabinet': devices_location_info(sys_name).get('cabinet'),
                    'start_u': devices_location_info(sys_name).get('start_u'),
                    'network_area': devices_location_info(sys_name).get('network_area'),
                    'device_type': devices_location_info(sys_name).get('device_type')
                }
                db_tables_op.update_device_info(device_info)
                print(type(cut_str(sys_desc).get('products_model')))
                print(cut_str(sys_desc).get('products_model'))
                print('---------------------------')
                # db_tables_op.update_device_info(ip_address, hostname=sys_name,
                #                                 manufacturer=device.get('manufacturer'),
                #                                 device_mode=device.get('device_model'),
                #                                 uptime=sys_uptime_str,
                #                                 SN=sys_sn,
                #                                 data_center=location_info.get('data_center'),
                #                                 block=location_info.get('block'),
                #                                 cabinet=location_info.get('cabinet'),
                #                                 start_u=location_info.get('start_u'),
                #                                 network_area=location_info.get('network_area'),
                #                                 device_type=location_info.get('device_type')
                #                                 )
                # db_tables_op.update_device_info(devices_location_info(sys_name))

                logger.info("===========华丽的分割线===============")

            except Exception as e:
                logger.error(f"解析XML时发生错误：{e}")
        else:
            logger.error(f"与交换机 {ip_address} 830端口通信失败。。。")
