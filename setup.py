from setuptools import setup

version = "1.1.1"

setup(
    name="stscpy",
    author="ccev",
    url="https://github.com/ccev/stscpy",
    version=version,
    install_requires=["requests", "Pillow"],
    packages=["tileserver"],
    long_description="For documentation, plase visit https://github.com/ccev/stscpy",
    description="Basic wrapper for SwiftTileserverCache"
)