

from setuptools import find_packages, setup
name = 'nonebot_plugin_BitTorrent'

setup(
    name=name,  
    version='0.0.8',
    author="Special-Week",
    author_email='2749903559@qq.com',
    description="encapsulate logger",
    python_requires=">=3.8.0",
    packages=find_packages(),
    long_description="nonebot2磁力搜索插件",
    url="https://github.com/Special-Week/nonebot_plugin_BitTorrent",

    # 设置依赖包
    install_requires=["lxml","httpx","bs4","nonebot2","nonebot-adapter-onebot"],
)