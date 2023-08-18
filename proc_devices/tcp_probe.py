import socket
import concurrent.futures
from utils.utils_logger import get_logger
import os

# 初始化日志记录器
get_filename = os.path.basename(__file__)
logger = get_logger(get_filename)


# 检查指定IP地址的22号端口是否开放，如果开放则返回 True，否则返回 False。
def is_port_open(ip_address, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            result = s.connect_ex((ip_address, port))
            if result == 0:
                return True
            return False
    except socket.timeout:
        return False
    except Exception as e:
        logger.error(f"检查 {ip_address} 的22号端口时发生错误：{e}")
        return False


# 对指定的IP地址进行TCP探测，如果22号端口开放则返回IP地址，否则返回 None。
def tcp_probe(ip_address):
    try:
        if is_port_open(ip_address, 22):
            return ip_address
        return None
    except Exception as e:
        logger.error(f"对 {ip_address} 进行TCP探测时发生错误：{e}")
        return None


# 使用多线程并发地对多个IP地址进行TCP探测，返回开放22号端口的IP地址列表。
def tcp_probe_concurrent(ips_to_probe):
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # 使用executor.map函数将tcp_probe函数映射到所有的IP地址上，并发地进行TCP探测。
            # 将结果存储在reachable_ips列表中。
            reachable_ips = set(executor.map(tcp_probe, ips_to_probe))
            # 筛选出返回值为非空的IP地址，存储在reachable_ips列表中。
            reachable_ips = [ip for ip in reachable_ips if ip]
            # 返回开放22号端口的IP地址列表
            return reachable_ips
    except Exception as e:
        logger.error(f"TCP探测过程中发生错误：{e}")
        return []
