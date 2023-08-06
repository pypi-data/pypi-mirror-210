#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
created by：2017-05-10 20:11:31
modify by: 2017-6-30 15:56:58

功能：实现rsync命令的二次封装

"""

import sysrsync

class RsyncUtil:
    """Rsync, 工具类

    这段代码是一个封装了 sysrsync 模块的 Rsync 工具类，提供了两个方法：

    rsync_use_ssh()：使用 SSH 方式进行 Rsync；
    rsync_daemon()：使用 Rsync daemon 方式进行 Rsync。
    具体来说，这两个函数都接受一些参数，包括本地的源路径、远端目标路径、IP 和端口等信息。使用 sysrsync.run() 函数调用 rsync 命令实现文件同步。

    要使用该工具类，需要确保本地和远程系统中都已经安装 rsync 命令，否则无法正常使用。同时，在使用 rsync_daemon() 方法时还需要准备存储密码的文本文件，并且需要设置该文件的权限为 600。
    """

    @staticmethod
    def rsync_use_ssh(workspace, source_dir, rsync_user,
                      rsync_ip, target, rsync_port="22"):
        """使用 SSH 方式进行 Rsync

        :param workspace: Rsync 工作路径，路径任意
        :type workspace: str

        :param source_dir: Rsync 源路径，这里为 svn code 本地路径
        :type source_dir: str

        :param rsync_user: Rsync 用户名
        :type rsync_user: str

        :param rsync_ip: Rsync IP 地址
        :type rsync_ip: str

        :param target: Rsync 远端路径
        :type target: str

        :param rsync_port: ssh 端口，默认为 22
        :type rsync_port: int

        :return: 执行状态码，0 为正常，其他为异常
        :rtype: int
        """
        destination = f"{rsync_user}@{rsync_ip}:{target}"
        ssh_opts = f"ssh -p {rsync_port}"
        return RsyncUtil.do_rsync(workspace, source_dir, destination, ssh_opts)

    @staticmethod
    def rsync_daemon(workspace, source_dir, rsync_user, rsync_ip,
                     rsync_remote_module, rsync_passwd_file, rsync_port="873"):
        """使用 Rsync daemon 方式进行 Rsync

        :param workspace: Rsync 工作路径，路径任意
        :type workspace: str

        :param source_dir: Rsync 源路径，这里为 svn code 本地路径
        :type source_dir: str

        :param rsync_user: Rsync 用户名
        :type rsync_user: str

        :param rsync_ip: Rsync IP 地址
        :type rsync_ip: str

        :param rsync_remote_module: Rsync module
        :type rsync_remote_module: str

        :param rsync_passwd_file: 存储 rsync 密码的文本，PS: 文件权限要为 600
        :type rsync_passwd_file: str

        :param rsync_port: Rsync 端口，默认为 873
        :type rsync_port: int

        :return: 执行状态码，0 为正常，其他为异常
        :rtype: int
        """
        destination = f"{rsync_user}@{rsync_ip}::{rsync_remote_module}"
        extra_opts = f"--port={rsync_port} --password-file={rsync_passwd_file}"
        return RsyncUtil.do_rsync(workspace, source_dir, destination, extra_opts)

    @staticmethod
    def do_rsync(workspace, source, destination, options=""):
        """执行 rsync 命令

        :param workspace: Rsync 工作路径，路径任意
        :type workspace: str

        :param source: Rsync 源路径
        :type source: str

        :param destination: Rsync 目标路径
        :type destination: str

        :param options: 其他 rsync 参数，比如 ssh 选项、daemon 选项等
        :type options: str

        :return: 执行状态码，0 为正常，其他为异常
        :rtype: int
        """
        command = f"rsync {options} '{source}' '{destination}'"
        return sysrsync.check_call(command, shell=True, cwd=workspace)
           