#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
created by：2018-2-23 14:15:57
modify by: 2023-05-17 17:46:40

功能：各种常用的方法函数的封装。
"""
import os
from pathlib import Path
import shutil
# import gzip
# import tarfile
import stat
import platform

class FileUtils:
    """FileUtils"""
    @staticmethod
    def open_lagre_file(filename:str):
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                yield line

    @staticmethod
    def create_folder(str1:str) -> None:
        """创建目录
        
        等同于：

        if not os.path.exists(str1):
            os.makedirs(str1)
        """
        Path(str1).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def copy(src:str, dst:str, ignore=None, dirs_exist_ok=True) -> None:
        """
        递归地复制一个目录树到指定目录.
        
        参数:
        src: str - 源目录的路径.
        dst: str - 目标目录的路径，该目录必须不存在.
        ignore: 可选参数, 默认为None. 忽略复制时的某些文件/目录，使用shutil.ignore_patterns()函数指定.
        dirs_exist_ok: 可选参数，默认为True. 当目标目录存在时是否抛出异常.
        
        返回值:
        None.
        """

        if ignore:
            # 忽略文件时，可以使用shutil.ignore_patterns()函数来指定要忽略的文件类型或者目录名
            # ignore=shutil.ignore_patterns('*.pyc', 'tmp*')"
            ignore = shutil.ignore_patterns(ignore)

        if not os.path.exists(dst) and os.path.exists(src):
             # 如果目录不存在，则递归复制源目录
             # 目标目录存在时，如果设置了dirs_exist_ok参数为True，则不会抛出异常
            shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=dirs_exist_ok)
        else:
            raise OSError("The target path already exists! After a minute retry ~!")

    @staticmethod
    def get_listfile_01(path:str) -> list:
        """
        使用os.walk()遍历指定目录, 返回目录下所有文件的路径(不包含文件夹).
        
        参数:
        path: str - 指定的目录路径.
        
        返回值:
        list - 包含指定目录下所有文件的路径的列表.
        """
        file_path_list = []
        for root, _, files in os.walk(path):
            file_path_list.extend(os.path.join(root, f) for f in files)

        return file_path_list

    @staticmethod
    def get_listfile_02(path:str) -> list:
        """
        使用递归遍历指定目录, 返回目录下所有文件的路径(不包含文件夹).
        
        参数:
        path: str - 指定的目录路径.
        
        返回值:
        list - 包含指定目录下所有文件的路径的列表.
        """
        file_path_list = []
        def scan_dir(dir):
            for entry  in os.scandir(dir):
                if entry.is_file():
                    file_path_list.append(entry.path)
                # 如果entry是文件夹，则递归调用scan_dir()来扫描其内部
                elif entry.is_dir():
                    scan_dir(entry.path)

        scan_dir(path)
        return file_path_list

    @staticmethod
    def get_listfile_02(path: str, include_files: bool = True, include_dirs: bool = False) -> list:
        """获取指定目录下的所有文件和文件夹列表.

        :param path: 目标文件夹路径.
        :type path: str
        :param include_files: 是否包含文件. (默认值为True.)
        :type include_files: bool
        :param include_dirs: 是否包含子文件夹. (默认值为False.)
        :type include_dirs: bool
        :return: 返回path下的文件或文件夹列表list.
        :rtype: list
        """
        if not os.path.exists(path):
            raise OSError(f"路径 {path} 不存在！")

        file_list = []
        dir_list = []

        for root, dirs, files in os.walk(path, topdown=False):
            if include_files:
                file_list.extend([os.path.join(root, f) for f in files])

            if include_dirs:
                dir_list.extend([os.path.join(root, d) for d in dirs])

        if include_dirs is False and include_files is True:
            return file_list
        elif include_dirs is True and include_files is False:
            return dir_list
        elif include_dirs is True and include_files is True:
            return [*file_list, *dir_list]
        else:
            raise ValueError("参数include_files/include_dirs无效！")

    @staticmethod
    def change_owner(src, uid, gid, loop=False):
        '''
        更改指定文件或目录的所有者（UID）和所属组（GID）

        src：要更改所有权的文件或目录路径；
        uid：新的所有者用户 ID；
        gid：新的所属组 ID；
        loop：bool 类型，可选参数，默认值为 False。
        如果为 True，则在更改目录所有权时也会递归处理其中的所有子文件和子目录。需要注意的是，在递归过程中，代码还会忽略符号链接，并跳过它们（因为在某些情况下，更改符号链接的所有权可能会导致不可预期的后果）。

        # 示例用法
        change_owner('/path/to/dir', 1000, 1000, loop=True)
        '''
        if platform.system().lower() == 'windows':
            raise OSError('Windows 系统无法设置文件或目录的所有者')
        
        if os.path.isfile(src):
            os.chown(src, uid, gid)
        elif os.path.isdir(src) and loop:
            for dirpath, dirnames, filenames in os.walk(src):
                for dirname in dirnames:
                    filepath = os.path.join(dirpath, dirname)
                    if os.path.islink(filepath):  # 如果是符号链接，则跳过
                        continue
                    os.chown(filepath, uid, gid)
                
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.islink(filepath):  # 如果是符号链接，则跳过
                        continue
                    os.chown(filepath, uid, gid)
                    
                    # 如果是目录则递归调用
                    if os.path.isdir(filepath):
                        FileUtils.change_owner(filepath, uid, gid, loop=True)

    @staticmethod
    def rename_files(file_lists:list, file_prefix: str = "", file_suffix: int = 1) -> None:
        """批量重命名文件

        :param file_lists: 要重命名的文件列表，即包含多个文件路径的字符串列表
        :param file_prefix: 新文件名的前缀，字符串类型
        :param file_suffix: 新文件名的后缀，正整数类型
        :return: None
        """
        if not isinstance(file_suffix, int) or file_suffix <= 0:
            raise ValueError("file_suffix must be a positive integer")

        backup_names = []

        try:
            for f in file_lists:
                backup_names.append(os.path.basename(f))
                file_name, file_ext = os.path.splitext(f)
                new_name = f"{file_prefix}{file_suffix + len(backup_names) - 1:03d}{file_ext}"
                os.rename(f, new_name)
        except Exception as e:
            print(f"Failed to rename {f}, error: {e}")
            # 回滚重命名操作
            for i, f in enumerate(file_lists):
                backup_name = backup_names[i]
                os.rename(f"{file_prefix}{i+file_suffix:03d}{os.path.splitext(f)[1]}", backup_name)


    def rename_file(old_path: str, new_path: str) -> None:
        """重命名文件"""
        try:
            if Path(new_path).exists():
                raise FileExistsError(f"{new_path} already exists.")
            Path(old_path).rename(new_path)
        except OSError as e:
            print(f"Error renaming {old_path} to {new_path}: {e}")



# class ZipToFiles:

#     def gzip_to_files(self):
#         with open('file.txt', 'rb') as f_in, gzip.open('file.txt.gz', 'wb') as f_out:
#             shutil.copyfileobj(f_in, f_out)

#     def tar_to_files(self):
#         pass

#     def tar_zip_to_files(self):
#         pass
