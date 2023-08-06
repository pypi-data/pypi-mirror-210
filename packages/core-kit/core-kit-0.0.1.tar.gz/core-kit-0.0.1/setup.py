import setuptools #导入setuptools打包工具
 
with open("README.md", "r", encoding="utf-8") as readme:
    description = readme.read()
 
setuptools.setup(
    name="core-kit", # 用自己的名替换其中的YOUR_USERNAME_
    version="0.0.1",    #包版本号，便于维护版本
    author="MeDeity",    #作者，可以写自己的姓名
    author_email="langrenbule@gmail.com",    #作者联系方式，可写自己的邮箱地址
    description="An underlying tool library that can be used by any script",#包的简述
    long_description=description,    #包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    url="https://github.com/MeDeity/core-kit",    #自己项目地址，比如github的项目地址
    packages=setuptools.find_packages(),
    install_requires=['paramiko'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',    #对python的最低版本要求
)

