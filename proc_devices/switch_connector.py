import os
from ncclient import manager
from resources.netconf_conn_Info_huawei import port, device_params, allow_agent, look_for_keys
from utils.utils_logger import get_logger


# 初始化日志记录器
# function_name = "switch_connector"
get_filename = os.path.basename(__file__)
logger = get_logger(get_filename)


def connect_to_switch(ip_address, username, password, filter_file):
    if not os.path.exists(filter_file):
        logger.error(f"Filter file '{filter_file}' 不存在。")
        return None

    try:
        with open(filter_file, "r") as f:
            filter_str = f.read()

        with manager.connect(
                host=ip_address,
                port=port,
                username=username,
                password=password,
                hostkey_verify=False,
                device_params=device_params,
                allow_agent=allow_agent,
                look_for_keys=look_for_keys
        ) as m:
            logger.info(f"与交换机 {ip_address}:{port} 通信成功")
            result = m.get(filter=filter_str)
            return result.xml

    except Exception as e:
        logger.error(f"与交换机 {ip_address}:{port}通信时发生错误：{e}")
        return None
