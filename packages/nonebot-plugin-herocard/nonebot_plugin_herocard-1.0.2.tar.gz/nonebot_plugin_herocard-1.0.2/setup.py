import codecs
import os
from setuptools import setup, find_packages

# these things are needed for the README.md show on pypi (if you dont need delete it)
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

# you need to change all these
VERSION = '1.0.2'
DESCRIPTION = 'nonebot小插件，提供简单的文本提取功能'
LONG_DESCRIPTION = 'nonebot插件【herocard】，用于提取含“平假名/片假名”文本中的关键文本，使用方法详见README.md'

setup(
    name="nonebot_plugin_herocard",
    version=VERSION,
    author="Xie-Tiao",
    author_email="1183004468@qq.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'hero', 'nonebot','nonebot2','tieba','hiragana','katakana','benzi'],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Operating System :: Microsoft :: Windows",
    ]
)
