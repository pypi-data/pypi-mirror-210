

from setuptools import find_packages, setup
name = 'nonebot_plugin_homo_mathematician'

setup(
    name=name,  
    version='0.0.1',
    author="Special-Week",
    author_email='2749903559@qq.com',
    description="encapsulate logger",
    python_requires=">=3.8.0",
    packages=find_packages(),
    long_description="任何实数都用连续的114514通过加减乘除达成, 任给一组数据都能找出其内在规律(函数表达式)",
    url="https://github.com/Special-Week/Hinata-Bot/tree/main/src/plugins/homo_mathematician",

    # 设置依赖包
    install_requires=["fractions","scipy", "nonebot2","nonebot-adapter-onebot"],
)