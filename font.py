# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 18:11:44 2016

1. 查看matplotlib支持的中文字体。
用python运行以下代码：

#! /usr/bin/env python
# -*- coding: utf-8 -*-
from matplotlib.font_manager import FontManager
import subprocess

fm = FontManager()
mat_fonts = set(f.name for f in fm.ttflist)

output = subprocess.check_output(
    'fc-list :lang=zh -f "%{family}\n"', shell=True)
# print '*' * 10, '系统可用的中文字体', '*' * 10
# print output
zh_fonts = set(f.split(',', 1)[0] for f in output.split('\n'))
available = mat_fonts & zh_fonts

print '*' * 10, '可用的字体', '*' * 10
for f in available:
    print f
2. 配置matplotlibrc文件。
修改matplotlibrc文件（Ubuntu默认对应的是/etc/matplotlibrc）：

font.family         : serif
font.serif : {zh_family}, serif
其中{zh_family}为上一步中找到的其中一个可用中文字体。如果上步可用的字体为空，则需要将中文字体文件(tff)复制到matplotlib的字体目录下，再重复以上步骤。

*对于Windows，没有fc-list命令，找到对应可以字体直接在第2步里修改也可。

@author: megahertz
"""


from matplotlib.font_manager import FontManager
import subprocess

fm = FontManager()
mat_fonts = set(f.name for f in fm.ttflist)

output = subprocess.check_output(
    'fc-list :lang=zh -f "%{family}\n"', shell=True)
# print '*' * 10, '系统可用的中文字体', '*' * 10
# print output
zh_fonts = set(f.split(',', 1)[0] for f in output.split('\n'))
available = mat_fonts & zh_fonts

print '*' * 10, '可用的字体', '*' * 10
for f in available:
    print f
    