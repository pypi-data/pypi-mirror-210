
from setuptools import setup, find_packages
import os
import codecs

def get_requirements(filename='requirements.txt'):
    here = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(here, filename), 'r') as f:
        requires = [line.replace('\n', '') for line in f.readlines()]
    return requires

def read(fname):
	return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='textbsr',
      version='0.0.24',
      description='a simple version for blind text image super-resolution (current version is only for English and Chinese)',
      author='Xiaoming Li',
      author_email='csxmli@gmail.com',
      long_description=read("README.md"),
      long_description_content_type="text/markdown",
      #requires= ['numpy','torch','cv2','time','argparse','torchvision'], # 定义依赖哪些模块
      packages=find_packages(),  # 系统自动从当前目录开始找包
      # 如果有的文件不用打包，则只能指定需要打包的文件
      #packages=['代码1','代码2','__init__']  #指定目录中需要打包的py文件，注意不要.py后缀
      license="S-Lab License 1.0",
      keywords='blind text image super-resolution',
      url='https://github.com/csxmli2016/MARCONet',
      include_package_data=True,
      install_requires=get_requirements(),
      python_requires='>=3.6',
      entry_points = {
        'console_scripts': [
            'textbsr = textbsr.textbsr:textbsr',
        ],
      }
      )
