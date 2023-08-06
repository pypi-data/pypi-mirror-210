from setuptools import setup, find_packages

VERSION = '1.0.1'
DESCRIPTION = 'QuranSbuSample'
LONG_DESCRIPTION = 'My first Python package with a slightly longer description'

# Setting up
setup(
    name="QuranSbuSample",
    version=VERSION,
    author="Masoud_shafiei",
    author_email="masoudshafiei625@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['quran', 'sbu'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
    ]
)
