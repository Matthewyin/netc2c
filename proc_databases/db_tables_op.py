import mysql.connector
from resources import db_config
from utils.utils_logger import get_logger
import os

get_filename = os.path.basename(__file__)
logger = get_logger(get_filename)


def get_connection():
    try:
        conn = mysql.connector.connect(
            host=db_config.db_host,
            user=db_config.db_username,
            password=db_config.db_password,
            database=db_config.db_database,
            port=db_config.db_port
        )
        cursor = conn.cursor(buffered=True)
        logger.info("成功连接到MySQL数据库")
        return conn, cursor
    except Exception as e:
        logger.error(f"与MySQL数据库通信时发生错误：{e}")
        return None, None


def close_connection(conn, cursor):
    try:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("成功关闭MySQL数据库连接")
    except Exception as e:
        logger.error(f"关闭MySQL数据库连接时发生错误：{e}")


def get_account():
    conn, cursor = get_connection()
    if not conn or not cursor:
        logger.warning("数据库连接或游标未初始化。")
        return None

    try:
        query = "SELECT username, password FROM devices_account LIMIT 1"
        logger.info(f"执行查询：{query}")
        cursor.execute(query)
        account = cursor.fetchone()
        logger.info(query)

        if not account:
            logger.warning("没有可用的设备账户信息。")
        else:
            logger.debug(f"获取到的设备账户信息：{account}")

        return account
    except Exception as e:
        logger.error(f"获取第一个账户时发生错误：{e}")
        return None
    finally:
        close_connection(conn, cursor)


def get_management_ips():
    conn, cursor = get_connection()
    if not conn or not cursor:
        return []

    try:
        query = "SELECT mgmt_ip FROM devices_mgmt_ip ORDER BY id"
        cursor.execute(query)
        ips = [row[0] for row in cursor.fetchall()]
        return ips
    except Exception as e:
        logger.error(f"获取管理IP时发生错误：{e}")
        return []
    finally:
        close_connection(conn, cursor)


def get_current_mgmt_ips():
    conn, cursor = get_connection()
    if not conn or not cursor:
        return set()

    try:
        cursor.execute("SELECT mgmt_ip FROM devices_mgmt_ip")
        ips = {ip[0] for ip in cursor.fetchall()}
        return ips
    except Exception as e:
        logger.error(f"获取当前管理IP列表时发生错误：{e}")
        return set()
    finally:
        close_connection(conn, cursor)


def insert_new_ips(new_ips):
    conn, cursor = get_connection()
    if not conn or not cursor:
        return

    try:
        for ip in new_ips:
            cursor.execute("INSERT INTO devices_mgmt_ip (mgmt_ip) VALUES (%s)", (ip,))
        conn.commit()
    except Exception as e:
        logger.error(f"插入新的IP地址时发生错误：{e}")
    finally:
        close_connection(conn, cursor)


def delete_unreachable_ips(current_ips, reachable_ips):
    conn, cursor = get_connection()
    if not conn or not cursor:
        return

    try:
        ips_to_mark_unreachable = current_ips - reachable_ips

        for ip in ips_to_mark_unreachable:
            cursor.execute("UPDATE devices_mgmt_ip SET status = '不可达' WHERE mgmt_ip = %s", (ip,))

        conn.commit()
    except Exception as e:
        logger.error(f"标记不能访问的IP为不可达时发生错误：{e}")
    finally:
        close_connection(conn, cursor)


#
# def update_device_info(ip_address, hostname, manufacturer, device_model, uptime, SN):
#     conn, cursor = get_connection()
#     if not conn or not cursor:
#         return
#
#     try:
#         query = "SELECT * FROM devices_cmdb WHERE mgmt_ip = %s"
#         cursor.execute(query, (ip_address,))
#         result = cursor.fetchone()
#
#         if result:
#             query = "UPDATE devices_cmdb SET hostname = %s, manufacturer = %s, " \
#                     "device_model = %s, uptime = %s, SN = %s WHERE mgmt_ip = %s"
#             cursor.execute(query, (hostname, manufacturer, device_model, uptime, SN, ip_address))
#         else:
#             query = "INSERT INTO devices_cmdb (mgmt_ip, hostname, manufacturer, " \
#                     "device_model, uptime, SN) VALUES (%s, %s, %s, %s, %s, %s)"
#             cursor.execute(query, (ip_address, hostname, manufacturer, device_model, uptime, SN))
#
#         conn.commit()
#     except Exception as e:
#         logger.error(f"更新设备信息时发生错误：{e}")

def update_device_info(device_info):
    conn, cursor = get_connection()
    if not conn or not cursor:
        return

    try:
        query = "SELECT * FROM devices_cmdb WHERE SN = %s"
        cursor.execute(query, (device_info['SN'],))
        result = cursor.fetchone()

        if result:
            # 如果已存在相同SN号的设备，则更新数据库中该行的数据
            query = "UPDATE devices_cmdb SET hostname = %s, manufacturer = %s, " \
                    "products_model = %s, uptime = %s, data_center = %s, " \
                    "block = %s, cabinet = %s, start_u = %s, network_area = %s, device_type = %s " \
                    "WHERE SN = %s"
            logger.info('+++++++++++++++++++++++++++')
            logger.info(f'{cursor.execute}')
            logger.info(type(cursor))
            cursor.execute(query, (device_info['hostname'], device_info['manufacturer'],
                                   device_info['products_model'], device_info['uptime'],
                                   device_info['data_center'], device_info['block'],
                                   device_info['cabinet'], device_info['start_u'],
                                   device_info['network_area'], device_info['device_type'],
                                   device_info['SN']))
            logger.info('333')
        else:
            # 如果数据库中不存在相同SN号的设备，则插入新的设备信息
            query = "INSERT INTO devices_cmdb (mgmt_ip, hostname, manufacturer, " \
                    "products_model, uptime, SN, data_center, block, cabinet, " \
                    "start_u, network_area, device_type) " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (device_info['ip_address'], device_info['hostname'],
                                   device_info['manufacturer'], device_info['products_model'],
                                   device_info['uptime'], device_info['SN'],
                                   device_info['data_center'], device_info['block'],
                                   device_info['cabinet'], device_info['start_u'],
                                   device_info['network_area'], device_info['device_type']))
        logger.info('666')
        conn.commit()
    except Exception as e:
        logger.exception(f"更新设备信息时发生错误：{e}")
    finally:
        close_connection(conn, cursor)
