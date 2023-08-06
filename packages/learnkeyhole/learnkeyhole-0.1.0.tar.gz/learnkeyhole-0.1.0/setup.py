from __future__ import print_function
import distutils.spawn
import sys
sys.path
sys.path.append('src/learnkeyhole/__main__.py')


from setuptools import setup, find_packages

setup(
    packages=find_packages(),

        package_data = {
        # 如果包中含有.txt文件，则包含它
        '': ['*.txt'],
        '': ['*.ui'],
        },
    entry_points={
        'console_scripts':[
            'learnkeyhole = learnkeyhole.__main__:main'
        ]
    }
      
      )
