# -*- coding: utf-8 -*-
"""
created by：2022-07-29 16:17:18
modify by: 2022-08-01 18:51:42
功能：时间相关的函数封装
"""

import pytz
import datetime

class TimeUtils:

    @staticmethod
    def datetime_strftime_now(tz_info:str="Asia/Shanghai", strftime:str="%Y-%m-%d %H:%M:%S") -> str:
        """
        Returns an aware or naive datetime.datetime, depending on settings.tz_info.
        """

        if tz_info:
            as_info = pytz.timezone(tz_info)
            return datetime.datetime.now(tz=as_info).strftime(strftime) 
        else:
            return datetime.datetime.now().strftime(strftime)

    @staticmethod
    def timegm_timestamp(value:datetime) -> int:
        '''uninx时间戳转换'''
        # return timegm(datetime.datetime.now(tz=datetime.timezone.utc).utctimetuple())
        return value.timestamp()

    @staticmethod
    def datetime_utc_now(date_type:str="seconds", tz="", timedelta:int="") -> datetime:
        """
        返回 UTC时间的偏移量 例如
            In [15]: datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=111)
            Out[15]: datetime.datetime(2022, 8, 1, 10, 48, 17, 464785, tzinfo=datetime.timezone.utc)

            In [16]: datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=0)
            Out[16]: datetime.datetime(2022, 8, 1, 10, 46, 28, 592419, tzinfo=datetime.timezone.utc)

        如果timedelta为空，则默认为当前的UTC时间
        """
        if timedelta:
            # 使用关键字参数解包，而不是多个if-else语句
            datetime_timedelta = datetime.timedelta(**{date_type.lower(): timedelta}) 
        else:
            datetime_timedelta = datetime.timedelta()
 
        return datetime.datetime.now(tz=datetime.timezone.utc) + datetime_timedelta
