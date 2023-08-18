from proc_devices.tcp_probe import tcp_probe_concurrent
from proc_databases import db_tables_op
from utils.utils_logger import get_logger
import os
import time

# # 获取当前函数名作为日志文件夹名
get_filename = os.path.basename(__file__)

# function_name = "devices_discover"
logger = get_logger(get_filename)


def devices_discover():
    global cursor, conn
    try:
        # 连接数据库
        conn, cursor = db_tables_op.get_connection()

        while True:
            # 获取当前数据库中已有的IP列表
            current_ips = db_tables_op.get_management_ips()

            # 获取所有IP地址列表，并转换为集合类型
            ips_to_probe = set(f"10.1.62.{i}" for i in range(1, 255))

            # 执行并发的tcp探测
            reachable_ips = set(tcp_probe_concurrent(ips_to_probe))

            # 插入新的IP地址
            new_ips = reachable_ips - set(current_ips)
            if new_ips:
                db_tables_op.insert_new_ips(new_ips)
                conn.commit()
                logger.info("插入新的IP地址成功")

            # 删除不可达的IP地址
            db_tables_op.delete_unreachable_ips(set(current_ips), reachable_ips)
            conn.commit()
            logger.info("标记不可达IP地址成功")

            # # 暂停60分钟
            time.sleep(60)

    except Exception as e:
        logger.error(f"发生错误：{e}")
    finally:
        cursor.close()
        conn.close()
