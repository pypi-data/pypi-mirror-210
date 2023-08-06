'''
Created on 2015/12/10

Origin Author: by wang_yang1980@hotmail.com
'''
from setuptools import setup

from os.path import abspath, dirname, join
with open(join(dirname(abspath(__file__)), 'target', 'src', 'AppiumSikuliLibrary', 'version.py')) as f:
      exec(f.read())


DESCRIPTION = """
Appium - Sikuli Robot Framework Library provide keywords for Robot Framework to test UI through Sikuli.

Notes: AppiumSikuliLibrary.jar file is OS dependent. The version for Windows 64bit is included.
If target OS is not Windows, please get source code from GITHUB, and use Maven to build
AppiumSikuliLibrary.jar on target OS, and replace the jar file in 'lib' folder.
"""[1:-1]
CLASSIFIERS = """
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Java
Topic :: Software Development :: Testing
"""[1:-1]

setup(name         = 'robotframework-AppiumSikuliLibrary',
      version      = VERSION,
      description  = 'Appium - Sikuli library for Robot Framework',
      long_description = DESCRIPTION,
      author       = 'Thinh Nguyen',
      author_email = 'nguyenvanthinh.dnn@gmail.com',
      url          = 'https://github.com/thinhntt/robotframework-AppiumSikuliLibrary',
      license      = 'Apache License 2.0',
      keywords     = 'robotframework testing testautomation sikuli UI',
      platforms    = 'any',
      classifiers  = CLASSIFIERS.splitlines(),
      package_dir  = {'' : 'target/src'},
      packages     = ['AppiumSikuliLibrary']
      )