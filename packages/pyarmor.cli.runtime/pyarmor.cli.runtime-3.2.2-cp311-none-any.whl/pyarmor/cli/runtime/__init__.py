#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2023 -  Dashingsoft corp.                #
#      All rights reserved.                                 #
#                                                           #
#      Pyarmor                                              #
#                                                           #
#      Version: 8.0.1 -                                     #
#                                                           #
#############################################################
#
#
#  @File: pyarmor/runtime/__init__.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Mon Feb 13 09:17:27 CST 2023
#
import os
import zipfile

__VERSION__ = '3.2'


def map_platform(platname):
    if platname == 'darwin.aarch64':
        return 'darwin.arm64'
    return platname


class PyarmorRuntime(object):

    @staticmethod
    def get(platform):
        platname = map_platform(platform)
        path = os.path.join(__file__.replace('__init__.py', 'libs'), platname)
        if os.path.exists(path):
            for x in os.listdir(path):
                if x.startswith('pyarmor_runtime'):
                    return x, os.path.abspath(os.path.join(path, x))

    def _get_from_zip(self, platform):
        path = __file__.replace('__init__.py', 'libs.zip')
        prefix = platform.replace('darwin', 'macos').replace('.', '_')
        with zipfile.ZipFile(path) as f:
            for name in f.namelist:
                if name.startswith(prefix):
                    return name[len(prefix)+1:], f.read(name)
