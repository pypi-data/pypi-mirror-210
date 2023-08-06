from twoip import TwoIP
import socket
twoip = TwoIP(key = None)
class IP:
    def __is_ipv4(self,ip:str) -> bool:
            try:
                # 将地址转换为二进制表示
                socket.inet_aton(ip)
                # 如果转换成功，则说明该字符串是合法的 IPv4 地址
                return True
            except socket.error:
                return False
    def jbxx(self , ip : str) -> dict:
        """
        获取一个ip的基本信息
        'ip'：表示查询到的 IP 地址。
        'ip_range_start' 和 'ip_range_end'：分别表示该 IP 地址所处的 IP 范围的起始和结束地址。
        'mask'：表示子网掩码的位数。
        'name_ripe' 和 'name_rus'：分别表示英文和俄文形式的公司名称或组织名称。
        'route'：表示与 IP 地址相关联的路由。
        Args:
            ip : (str) 一个合法的IPv4地址
        Return:
            返回这个ip的基本信息
        Error:
            如果填入的ip不是合法的IPv4，则会报错
        """
        if self.__is_ipv4(ip) == False:
            raise ValueError(f'{ip}不是合法的IPv4地址')
        re = twoip.provider(ip=ip)
        return re
    def geo(self,ip : str) -> dict:
        """
        返回一个ip地址的地理位置等信息
        'ip'：表示查询到的 IP 地址。
        'country' 和 'country_rus' 和 'country_ua'：分别表示英文、俄文和乌克兰文形式的国家名称。
        'country_code'：表示该 IP 地址所属国家的 ISO 3166-1 alpha-2 代码。
        'region'、'region_rus' 和 'region_ua'：分别表示英文、俄文和乌克兰文形式的区域或州的名称。
        'city'：表示城市名称。
        'zip_code'：表示邮政编码
        'latitude' 和 'longitude'：表示该 IP 地址的纬度和经度。
        'time_zone'：表示该地的时区。
        Error:
            如果填入的ip不是合法的IPv4，则会报错
        """
        if self.__is_ipv4(ip) == False:
            raise ValueError(f'{ip}不是合法的IPv4地址')
        re = twoip.geo(ip = ip)
        return re

