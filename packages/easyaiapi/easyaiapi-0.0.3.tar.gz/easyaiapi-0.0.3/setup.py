from setuptools import setup, find_packages
import codecs
import os

cwd = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(cwd, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

VERSION = '0.0.3'
DESCRIPTION = 'Easy ai api'
install_requires = [r for r in open(os.path.join(cwd, "requirements.txt")).read().splitlines() ]

setup(
    name="easyaiapi",
    version=VERSION,
    author="Olivier",
    author_email="luowensheng2018@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=install_requires,
    keywords=['python', 'api', 'websocket', "AI"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)