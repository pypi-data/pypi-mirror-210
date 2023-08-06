#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
created by：2021-12-02 18:02:15
modify by: 2023-05-12 10:02:18

功能：json函数的封装。
"""

import json
from json import JSONDecodeError

class JsonUtils:
    """JsonUtils, 工具类

    Attributes:

        dumps是将dict转化成str格式，loads是将str转化成dict格式。

        dump和load也是类似的功能，只是与文件操作结合起来了。
    """
    @staticmethod
    def load_json(json_path:str) -> json:
        """加载json文件并返回一个json对象

        参数：
            json_path: json文件的路径

        返回值：
            一个json对象

        异常：
            OSError: 如果文件打开失败
            JSONDecodeError: 如果文件内容不是合法的json格式
        """
        try:
            with open(json_path, "r", encoding="utf8")  as frs:
                data = json.load(frs)
            return data
        except OSError as e:
            raise OSError(f"Failed to open file {json_path}: {e}")
        except JSONDecodeError as e:
            raise JSONDecodeError(f"Failed to decode JSON in file {json_path}: {e}")

    @staticmethod
    def set_json_to_file(value: str, file_path: str, ensure_ascii: bool = False) -> bool:
        """将 json 数据写入文件"""
        try:
            # 检查 value 是否为 json 格式
            json_data = json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError("Failed to parse the input as json format.") from e

        try:
            with open(file_path, "w", encoding="utf8")  as fws:
                json.dump(json_data, fws, indent=4, sort_keys=True, ensure_ascii=ensure_ascii)
            return True
        except OSError as e:
            raise IOError(f"Failed to write json file {file_path}: {e}") from e
    
    @staticmethod
    def get_json_value(file_path:str, key:str) -> json:
        """根据key获取json文件中的value"""
        with open(file_path, "r", encoding="utf8")  as frs:
            data  = json.load(frs)

        try:
            return data[key]
        except KeyError as err:
            raise KeyError("The key is not error %s." % (err))

    @staticmethod
    def set_value(file_path:str, key:str, value:str) -> bool:
        """根据key修改json文件中的value"""
        try:
            with open(file_path, "r", encoding="utf8")  as frs, \
                 open(file_path, "w", encoding="utf8")  as fws:
                res = json.load(frs)
                res[key] = value
                json.dump(res, fws, indent=4, sort_keys=True, ensure_ascii=False)
            return True
        except (OSError, JSONDecodeError) as e:
            raise ValueError(f"Failed to modify json file {file_path}: {e}")


    @staticmethod
    def loads_json_value(value:str) -> str:
        """将字符串转换为json对象

        参数：
            value: 需要转换的字符串

        返回值：
            一个json对象

        异常：
            ValueError: 如果value不是合法的json格式
            TypeError: 如果value不是字符串类型
        """
        try:
            json_data = json.loads(value)  
        except (ValueError, TypeError, JSONDecodeError) as e:
            # json_data = json.loads(json.dumps(value))
            raise (f"Failed to convert value to json: {e}")

        return json_data

    @staticmethod
    def is_json(value:str) -> bool:
        """判断数据是否是json"""
        try:
            json.loads(value)  
        except (ValueError, TypeError, JSONDecodeError) as err:
            # raise ("The format is not json. msg: %s" % (err))
            # 捕获解析错误，并返回False
            return False
        # 解析成功，返回True
        return True
        

if __name__ == "__main__":
    pass
