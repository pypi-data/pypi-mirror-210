from setuptools import setup
with open("./README.md",mode='r',encoding='utf-8') as f:
    des = f.read()
setup(
    name="thztools",      # 包名，用于安装和调用该包
    version="1.0.2",               # 版本号
    author="Sen",
    description="由天狐宗开发的工具，方便开发时使用",
    long_description=des,
    long_description_content_type='text/markdown',
    author_email="tianhuzong@qq.com",
    url="https://github.com/tianhuzong/thztools",
    license="MIT",
    packages=["thztools"],     # 需要打包的包，可以是单个或多个包
    package_data={"thztools": ["*.py"]},  # 包需要包含的数据文件（可选）
    install_requires=[           # 安装依赖，可以是单个或多个依赖项
        "rsa",
        "Crypto",
    ],
    classifiers=[                # 分类标签（可选），使用 PyPI 标准分类
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)