from setuptools import setup

setup(
    name='exc2dic',
    version='1.0.1',
    description='A package for reading Excel files',
    author='Mingyuan',
    author_email='mingyuanhuang@qq.com',
    url='https://github.com/MingyuanHuang/Excel2Dict',
    packages=['excel2dict'],
    install_requires=[
        'pandas',
    ],
)
