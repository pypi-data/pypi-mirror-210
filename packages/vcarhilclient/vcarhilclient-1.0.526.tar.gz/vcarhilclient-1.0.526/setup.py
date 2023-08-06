# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vcarhilclient",  # 包名
    version="1.0.526",
    author="vcarsystem",
    author_email="service@vcarsystem.com",
    description="vcarhilclient",  # 包的简述
    long_description=long_description,  # 包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires = ["minio==7.1.13"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

