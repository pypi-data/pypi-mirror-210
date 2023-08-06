import setuptools

with open("README.md", "r", encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="FreeplanIr",
    version="1.0.3",
    author="wangdashuai",
    author_email="hanchaodaming@outlook.com",
    description="一个可以解析freeplan *.mm格式文件的工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leslie110",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "XlsxWriter>=3.1.1",
    ],
    python_requires='>=3.6',

)
