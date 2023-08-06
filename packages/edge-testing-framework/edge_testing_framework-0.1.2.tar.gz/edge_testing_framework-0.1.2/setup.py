# coding: utf-8

# @Time:2020/3/15 12:34
# @Auther:sahala

from setuptools import setup, find_packages  # 这个包没有的可以pip一下

setup(
    name="edge_testing_framework",  # 这里是pip项目发布的名称
    version="0.1.2",  # 版本号，数值大的会优先被pip
    keywords=["pip", "edge_testing_framework", "featureextraction"],
    description="关键字驱动测试框架：支持c++接口文件dll/so的加载测试、http、mqtt、db、modbus等",
    long_description="关键字驱动测试框架：支持c++接口文件dll/so的加载测试、http、mqtt、db、modbus等",
    license="MIT Licence",

    url="https://github.com/",  # 项目相关文件地址，一般是github
    author="liyubin",
    author_email="1399393088@qq.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        'xlrd==1.2.0',
        'paho-mqtt==1.6.1',
        'modbus-tk==1.1.3',
        'XlsxWriter==3.1.0',
        'openpyxl==3.1.2',
        'urllib3==1.26.15',
        'arrow==1.2.3',
        'pymongo==4.3.3',
        'PyMySQL==1.0.3',
        'pymssql==2.2.7',
        'cx_Oracle==8.3.0',
        'requests==2.28.2',
        'injson-check',
        'requests-toolbelt==1.0.0'
    ],  # 这个项目需要的第三方库
    entry_points={
            'console_scripts': [
                'edge_testing_framework = client.cli:main'
            ]
        },  # 命令行cli启动的命令
)

# 步骤：

# 配置 MANIFEST.in 需要打包的非 py 文件, 注意： *.dll前面有空格 和 路径隔开

# 1.setup.py放在被打包同级
# 本地打包项目文件
# python setup.py sdist

# 2.上传项目到pypi服务器
# pip install twine
# twine upload injson_ok/name.tar.gz

# 3.下载上传的库
# pip install name
