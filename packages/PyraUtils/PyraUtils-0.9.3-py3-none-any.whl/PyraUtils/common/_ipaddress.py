#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
created by：2022-07-28 16:17:47
modify by: 2022-07-28 19:34:04

功能：ipaddress函数的封装。
"""
import ipaddress
import numpy as np


class IpaddressUtils:
    """IpaddressUtils"""
    def __init__(self) -> None:
        pass

    def _ip_network(self, network):
        '''
        验证网络地址是否合法；如果输入值异常，返回None
        '''
        try:
            return ipaddress.ip_network(network)
        except ValueError as e:
            return None

    def _ip_address(self, address):
        '''
        验证IP是否合法；如果输入值异常，返回None
        '''
        try:
            return ipaddress.ip_address(address)
        except ValueError as e:
            return None

    def check_ipaddress(self, address:str, network_list:list="") -> bool:
        '''
        验证address是否在network_list内
        '''
        address = self._ip_address(address)
         # 使用numpy数组
        network_list = np.array([self._ip_network(n) for n in network_list]) 
        for network in network_list:
            if address in network:
                return True
        return False
