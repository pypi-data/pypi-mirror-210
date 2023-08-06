from setuptools import setup, find_packages
import codecs
import os


########SAVE THIS UNVALUABLE INFORMATION#########
#                change version                 #
#               rm -r build dist                # 
#      python3 setup.py sdist bdist_wheel       #
#        twine upload dist/* --verbose          #
########SAVE THIS UNVALUABLE INFORMATION#########


VERSION = '1.0.10'
DESCRIPTION = 'A Simple Game Engine Libary'
LONG_DESCRIPTION = 'Chech github: https://github.com/coding610/SEAS/tree/master'


# Setting up
setup(
    name="MySEAS_OLD",
    version=VERSION,
    author="Sixten Bohman",
    author_email="sixten.bohman.08@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,

    packages=find_packages(),
    
    install_requires=['pygame'],
    keywords=['python', 'pygame', 'Game Engine', 'Simple', 'Beginner', 'Learning', 'Funny?'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
