from distutils.core import  setup
import setuptools
packages = ['acrt']# 唯一的包名，自己取名
setup(name='acrt',
	version='1.0',
	author='lhz',
    packages=packages, 
    package_dir={'requests': 'requests'},)
