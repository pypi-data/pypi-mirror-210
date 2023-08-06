import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="rain_orm",
    version="0.1",
    author="rain",
    author_email="948628463@qq.com",
    description="a tiny orm frame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=['pymysql == 1.0.3'],
)