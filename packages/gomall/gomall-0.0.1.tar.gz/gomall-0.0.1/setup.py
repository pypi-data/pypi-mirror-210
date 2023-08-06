import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gomall",
    version="0.0.1",
    author="GoMall Development Team",
    author_email="wangwenshan@ict.ac.cn",
    description="和gomall平台配合使用的python依赖包，包括实验追踪、指令构造、模型评估等工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'torch <= 2.00',
    ],
)