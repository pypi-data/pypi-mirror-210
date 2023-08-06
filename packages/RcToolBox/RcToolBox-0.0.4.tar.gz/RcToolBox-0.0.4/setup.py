#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, find_packages            

setup(
    name = "RcToolBox",      # 这里是pip项目发布的名称
    version = "0.0.4",  # 版本号，数值大的会优先被pip
    keywords = ["pip", "RcToolBox"],			# 关键字
    description = "RC personal ToolBox",	# 描述
    long_description = "RC personal ToolBox",
    license = "MIT Licence",		# 许可证

    url = "",     #项目相关文件地址，一般是github项目地址即可
    author = "RC",			# 作者
    author_email = "yilingyaomeng@gmail.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["numpy", "PyYAML", "SimpleITK", "Pathos", "seaborn", "pandas", "fastremap", "openpyxl", "vtk"]          #这个项目依赖的第三方库
)
