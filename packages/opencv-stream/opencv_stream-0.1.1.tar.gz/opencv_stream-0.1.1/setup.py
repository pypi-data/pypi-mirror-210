from setuptools import setup, find_packages
import codecs
import os


cwd = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(cwd, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()
    with open("./test.py") as p:
         long_description = long_description.format(python=p.read())


REQUIREMENTS = open("./requirements.txt").read().splitlines()
VERSION = '0.1.1'
DESCRIPTION = 'Wrapper over opencv for video processing and API development'

setup(
    name="opencv_stream",
    version=VERSION,
    author="Olivier",
    author_email="luowensheng2018@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    keywords=['python', 'video', 'stream', "AI", "API"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)