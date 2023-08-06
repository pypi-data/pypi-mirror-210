"""
@Date    : 2020-12-18
@Author  : liyachao
"""
from setuptools import setup, find_packages
from ios_device import __version__

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]


setup(name='pyidevice',
      version=__version__,
      description='Get ios data and operate ios devices',
      author='chenpeijie',
      author_email='cpjsf@163.com',
      url='https://github.com/YueChen-C/py-ios-device',
      packages=['pyidevice'],
      package_dir={"pyidevice": "ios_device"},
      include_package_data=True,
      long_description=open('README.md').read(),
      long_description_content_type="text/markdown",
      install_requires=REQUIREMENTS,
      python_requires=">=3.7",
      classifiers=[
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
      ],
      entry_points={
          'console_scripts':{
              'pyidevice=ios_device.main:cli'
          }
      },
)
