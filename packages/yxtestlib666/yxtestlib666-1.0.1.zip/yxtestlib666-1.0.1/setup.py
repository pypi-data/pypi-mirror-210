
# from distutils.core import setup
from setuptools import setup

def readme_file():
      with open("README.rst",encoding="utf-8") as rf:
            return rf.read()

setup(name="yxtestlib666",version="1.0.1",description="this is a niubi lib",
      py_modules=["Tool"],author="yx",
      author_email="1063387453@qq.com",long_description=readme_file(),
      url="https://github.com/wangshunzi/Python_code",license="MIT")




