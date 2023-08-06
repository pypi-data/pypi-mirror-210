from setuptools import setup


def read_rst():
    with open("README.rst", mode="r", encoding="utf-8") as fp:
        return fp.read()


setup(name="kinneykits",
      version="1.0.0",
      author="kinney",
      description="This is a PyPackage that support some tools to python spider.",
      long_description=read_rst(),
      py_modules=[""],
      url="https://gitee.com/miss-table/kinneykit",
      license="MIT",
      author_email="3572484312@qq.com",
      packages=["crawlkits"]
      )
