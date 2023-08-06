from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Neuralint package'
LONG_DESCRIPTION = 'Neuralint package.'

# Setting up
setup(
    name="neuralint",
    version=VERSION,
    author="Poly",
    author_email="<ghassendaoud99@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    package_data={},
    install_requires=['tensorflow==1.15'],
    keywords=['python', 'cnn', 'test'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)