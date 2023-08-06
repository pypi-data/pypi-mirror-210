#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
created by：2017-05-10 20:11:31
modify by: 2023-05-25 13:55:46

功能：各种常用的字符串处理方法函数的封装。
"""

import re
import string
import unicodedata
from functools import reduce, lru_cache
from pypinyin import Style, pinyin
from collections import defaultdict
from typing import Any, List, Tuple, TypeVar


K = TypeVar('K')
V = TypeVar('V')

class StringsUtils:
    """StringsUtils, 工具类

    Attributes:

    # 创建 StringsUtils 实例
    obj = StringsUtils()

    # 将缓存大小设置为 2048
    obj.set_cache_size(2048)

    # 现在，my_method 方法的缓存大小为 2048
    result = obj.my_method('some_arg')

    """
    # CACHE_SIZE = 0 禁用缓存
    CACHE_SIZE = 2048

    @classmethod
    def set_cache_size(cls, size):
        '''传递缓存'''
        cls.CACHE_SIZE = size


    @staticmethod
    def remove_duplicate_01(lst:any) -> list:
        """python 字典列表/列表套字典 数据去重

        这段代码实现了一个去除列表中重复元素的方法 remove_duplicate_01。
        其具体实现方式是使用列表推导式和一个额外的空列表 seen，对原列表中的每个元素进行判断，如果该元素不在 seen 列表中，则加入其中并返回该元素，否则忽略该元素。
        同时也会使用 seen.append(x) 将该元素加入到 seen 列表中去，以便后续比较时可以正确判定。
        这种方法相较于其他去重方法在代码简洁性和效率上有一定优势，但需要额外的空间来存储已经出现过的元素。

        """
        seen = []
        return [x for x in lst if x not in seen and not seen.append(x)]

    # @staticmethod
    # def remove_duplicate_02(lst:any) -> list:
    #     """python 字典列表/列表套字典 数据去重

    #     使用unique_everseen（有序，高效）：如果想要一个更高效和优雅的方法，可以使用iteration_utilities模块中的unique_everseen函数。
    #                                     这个函数可以找到可迭代对象中所有唯一的元素，并保留它们出现的顺序。它会记住所有在可迭代对象中出现过的元素。

    #      iteration-utilities 仅支持3.9,因此这个方法弃用
        
    #     """
    #     from iteration_utilities import unique_everseen
    #     return list(unique_everseen(lst))

    @staticmethod
    def multidict(key_values: List[Tuple[K, V]], default_factory: callable = list) -> dict:
        """

        key_values 的可选值是任何包含多个 (key, value) 元组的列表对象。
        default_factory 参数是可选的，其默认值为 Python 内置的 list() 函数。实际上，该参数可以接受任何无参函数（callable）作为输入。
        当对于一个字典的某个键第一次创建值时，若该键不存在，则会调用default_factory()函数来创建默认值，然后把这个默认值加入该键的值列表中。


        这段代码实现了一个将 key-value 转换为多个值对应同一键的字典的方法 `multidict`。
        具体实现方式是使用 `defaultdict(list)` 创建一个默认值为列表的字典 `multi_dict`，遍历 `key_values` 列表中的每个元素，并将该元素的键作为字典的键，将该元素的值加入到该键所对应的列表中。
        最终返回一个包含所有值的字典 `multi_dict`。

        其中，`defaultdict` 是 Python 内置的一种字典类型，与普通字典的区别在于，它在初始化时需要传入一个默认工厂函数，用于创建默认值。
        在本例中，默认工厂函数为 `list`，因此当新的键被添加到 `multi_dict` 中时，对应的值将自动初始化为空列表。
        这样一来，在向字典中添加元素时，就无需先判断该键是否已经存在，只需直接操作值列表即可。

        举个例子，如果有如下的 key-value 列表：

        ```python
        key_values = [('even',2),('odd',1),('even',8),('odd',3),('float',2.4),('odd',7)]
        ```

        使用 `multidict` 方法将其转换为对应的字典，可以得到以下结果：

        ```python
        defaultdict(<class 'list'>, {'float': [2.4], 'even': [2, 8], 'odd': [1, 3, 7]})
        ```

        可以看到，所有的键值对都被正确地转换为了多个值对应同一键的形式，并存储在了一个字典对象中。
        这种方法相较于普通字典在添加键值时不需要判断该键是否已经存在，能够自动为新键设置默认值，因此比较方便。
        """
        multi_dict = defaultdict(default_factory)
        for key, value in key_values:
            multi_dict[key].append(value)
        return multi_dict

    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def str_to_pinyin(str1:str, style=Style.FIRST_LETTER, strict=False) -> str:
        """拼音缩写

        参数:

            str1: 字符串
            style: NORMAL,zhao,TONE,zh4ao,TONE2,zha4o,TONE3,zhao4,\
                   INITIALS,zh,FIRST_LETTER,z,FINALS,ao,FINALS_TONE,\
                   4ao,FINALS_TONE2,a4o,FINALS_TONE3,ao4,BOPOMOFO,\
                   BOPOMOFO_FIRST,CYRILLIC,CYRILLIC_FIRST}
        """
        # 输入参数类型校验
        if not isinstance(str1, str):
            raise TypeError("The argument 'str1' must be a string.")

        if not isinstance(style, Style):
            raise TypeError("The argument 'style' must be a 'Style' object.")
    
        character_list = pinyin(str1, style=style, strict=strict)      # [[c],[h]]
        return "".join(map(str, reduce(lambda x,y:x+y, character_list)))

    @staticmethod
    def is_empty(str1) -> bool:
        """判空"""
        if str1 is None or str1 == "":
            return True
        return False

    @staticmethod
    def valid_str_is_digit(num) -> bool:
        """
        限制输入数字

        以下為 tk.Tk().register() 的參數說明，
        %d：Type of action (1 for insert, 0 for delete, -1 for focus, forced or textvariable validation)
        %i：index of char string to be inserted/deleted, or -1
        %P：value of the entry if the edit is allowed
        %s：value of entry prior to editing
        %S：the text string being inserted or deleted, if any
        %v：the type of validation that is currently set
        %V：the type of validation that triggered the callback (key, focusin, focusout, forced)
        %W：the tk name of the widget
        
        https://shengyu7697.github.io/python-tkinter-entry-number-only/
        """
        if str.isdigit(num) or num == '':
            return True
        else:
            return False

    @staticmethod
    def valid_str_01(value:str) -> str:
        """
        如果value是一个字符串，返回一个只包含字母、数字和-_.符号的字符串，否则抛出ValueError异常。

        >>> get_valid_filename("john's portrait in 2004.jpg")
        'johns_portrait_in_2004.jpg'

        https://github.com/django/django/blob/main/django/utils/text.py

        """
        try:
            # 检查name是否是一个字符串，如果不是，抛出ValueError异常
            if not isinstance(value, str):
                raise ValueError(f"name must be a string, got {type(value)}")

            # 将name两端的空白去掉，并用下划线替换空格
            s = str(value).strip().replace(' ', '_')
            # 用空字符串替换不是字母数字或-_.符号的字符
            s1 = re.sub(r'(?u)[^-\w.]', '', s)
            # 检查s1是否为空或只包含.或..，如果是，抛出ValueError异常
            if s1 in {'', '.', '..'}:
                raise ValueError("Could not derive file name from '%s'" % value)
            return s1
        except ValueError as e:
            raise e

    @staticmethod
    def valid_str_02(value:str) -> str:
        """
        In [45]: valid_filename_02("陈aaa ll%.jpg") -> Out[45]: 'aaall.jpg'
        In [44]: valid_filename_02("aaa ll%.jpg")   -> Out[44]: 'aaall.jpg'
        """
        try:
            # abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_.
            # safechars = string.ascii_letters + string.digits + " -_."

            # abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.

            # 检查name是否是一个字符串，如果不是，抛出ValueError异常
            if not isinstance(value, str):
                raise ValueError(f"name must be a string, got {type(value)}")
            # 定义安全的字符集，包括字母、数字和-_.符号
            safechars = string.ascii_letters + string.digits + "-_."
            # 用列表推导式过滤掉不在安全字符集中的字符，并用空字符串连接
            return "".join([c for c in value if c in safechars])
        except ValueError as e:
            raise ValueError(f"Could not derive file name from '{value}': {e}") 

    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def slugify(value:str, allow_unicode: bool = False) -> str:
        """
        如果allow_unicode为False，转换为ASCII。
        
        将空格或重复的破折号转换为单个破折号。删除不是字母数字、下划线或破折号的字符。转换为小写。
        
        还要去掉开头和结尾的空白、破折号和下划线。


        https://github.com/django/django/blob/main/django/utils/text.py

        In [20]: slugify("陈 ll%.jpg")  --> In [20]: slugify("陈 ll%.jpg")
        In [22]: slugify("陈aaa ll%.jpg", allow_unicode=True)  --> Out[23]: '陈aaa-lljpg'
        """

        if allow_unicode:
            # 将字符串规范化为兼容性分解
            value_1 = unicodedata.normalize('NFKC', str(value))
        else:
            # 将字符串规范化为兼容性分解，然后编码为ASCII并忽略错误，再解码为字符串
            value_1 = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')

        # 将字符串转换为小写，并用空字符串替换不是字母数字、空白或破折号的字符
        value_2 = re.sub(r'[^\w\s-]', '', value_1.lower())
         # 用单个破折号替换连续的破折号或空白，并去掉开头和结尾的破折号和下划线
        return re.sub(r'[-\s]+', '-', value_2).strip('-_')

    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def natural_sort_01(value:list) -> list: 
        """自然排序

        自然排序是一种按照人类直觉进行排序的算法，
        例如将“file1”、“file2”、“file10”按顺序排列时，自然排序会将它们排序为“file1”、“file2”、“file10”，而不是“file1”、“file10”、“file2”。
        
        https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/
        """
        
        # 定义一个函数，将字符串转换为整数或小写
        convert = lambda x: int(x) if x.isdigit() else x.lower() 
        # 定义一个函数，将字符串按数字和非数字分割，并转换为列表
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        # 返回按自然顺序排序的列表
        return sorted(value, key=alphanum_key)

    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def natural_sort_02(value:list) -> list:
        """自然排序
        
        对于大型列表的排序，可以使用list.sort()方法并将key参数设置为alphanum_key函数，这比使用sorted()函数更快。
        如果输入列表已经是有序的，则不需要进行排序。因此，可以在代码中添加一个检查来避免额外的排序操作。
        如果列表元素都是数字，无需执行字符串转换操作

        使用 Python 标准库中的 functools.lru_cache 装饰器，可以很容易地为函数添加缓存功能
        我们设置了缓存的最大大小为 None，表示缓存不受限制。如果希望限制缓存大小，可以将 maxsize 参数设置为想要的值（整数类型）。

        """
            
        # 定义一个函数，将字符串按数字和非数字分割，并转换为列表
        def alphanum_key(key):
            return [int(c) if c.isdigit() else c for c in re.split('([0-9]+)', key)]
        
        # 检查输入列表是否已经排序，如果是，直接返回
        is_sorted = all(value[i] <= value[i+1] for i in range(len(value)-1))
        if is_sorted:
            return value
        
        # 由于 lambda 和 sorted 不是内置函数，受 GIL 限制，在多核 CPU 中性能可能较差。
        # 使用 list.sort() 更好。同时也不需要显式地记住前一次排序结果，
        # Python 会记得它并尝试在下一次排序时使用它（称为 timsort）
        value.sort(key=alphanum_key)
        
        return value
    
    @staticmethod
    def natural_sort_03(value):
        """自然排序
        
        手动实现缓存功能，可以使用 Python 中的字典对象来保存已经计算过的结果
        我们新增了一个空字典 cache，用于保存已经计算过的结果。
        在每次调用 natural_sort() 函数时，首先检查输入值 value 是否已经计算过，并保存在缓存中。
        如果是，则直接从缓存中返回计算结果。否则，执行原来的排序逻辑，将结果保存到缓存中，然后返回。
        这样就可以避免反复计算，提高程序性能

        请注意，手动实现的缓存功能可能比 Python 内置的 LRU Cache 更灵活，但也需要更多的代码和维护工作。
        例如，我们需要在适当的时候清空缓存、控制缓存大小等。如果你不确定是否需要这些高级功能，建议还是使用 Python 内置的 LRU Cache 实现缓存功能。
        
        """
        # 新增一个空字典用于保存缓存结果
        cache = dict()
            
        # 定义一个函数，将字符串按数字和非数字分割，并转换为列表
        def alphanum_key(key):
            return [int(c) if c.isdigit() else c for c in re.split('([0-9]+)', key)]
        
        # 如果 value 已经计算过且保存在缓存中，直接返回结果
        if value in cache:
            return cache[value]
            
        # 检查输入列表是否已经排序，如果是，直接返回
        is_sorted = all(value[i] <= value[i+1] for i in range(len(value)-1))
        if is_sorted:
            result = value
        
        else:
            # 由于 lambda 和 sorted 不是内置函数，受 GIL 限制，在多核 CPU 中性能可能较差。
            # 使用 list.sort() 更好。同时也不需要显式地记住前一次排序结果，
            # Python 会记得它并尝试在下一次排序时使用它（称为 timsort）
            result = sorted(value, key=alphanum_key)
            
        # 将结果加入缓存中
        cache[value] = result
        
        return result
