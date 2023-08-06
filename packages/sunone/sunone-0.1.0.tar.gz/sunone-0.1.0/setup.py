from setuptools import setup
about = {"__title__":"sunone","__version__":"0.1.0","__description__":"这是一个测试包",
         "__author__":"yonghuiXu","__author_email__":"2541128175@qq.com","__url__":""}
# 这里以默认的编码格式读文件
with open("README.md", "r") as f:
    readme = f.read()
requires = [
    "charset_normalizer>=2,<4",
    "idna>=2.5,<4",
    "urllib3>=1.21.1,<3",
    "certifi>=2017.4.17",
]

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=requires,
    zip_safe=True,
)