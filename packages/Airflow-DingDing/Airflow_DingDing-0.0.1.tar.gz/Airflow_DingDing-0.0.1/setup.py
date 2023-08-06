# -*- coding:UTF-8 -*-
#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup

setup(
 name="Airflow_DingDing",
 version="0.0.1",
 author="WangBensen",
 author_email="bensen.wang@ycgame.com",
 license="Apache License",
 url="https://xxxxxxxxx",
 packages=["Airflow_DingDing"],
 install_requires=["requests<=2.28.1"],
 classifiers=[
 "Environment :: Web Environment",
 "Intended Audience :: Developers",
 "Operating System :: OS Independent",
 "Topic :: Text Processing :: Indexing",
 "Topic :: Utilities",
 "Topic :: Internet",
 "Topic :: Software Development :: Libraries :: Python Modules",
 "Programming Language :: Python",
 "Programming Language :: Python :: 3.8"
 ],
)

#name:打包的名称，以后会根据这个包名去下载包
#version:版本号
#author:作者
#author_email:作者email
#license:LiCENSE文件,授权方式
#url:项目地址
#package:打包的项目包名
#install_requires:依赖的包以及版本号
#classifieers:是要求的环境