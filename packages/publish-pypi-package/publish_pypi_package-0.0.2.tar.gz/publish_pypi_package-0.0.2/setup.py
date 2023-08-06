from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'A conversion package'
LONG_DESCRIPTION = 'A package that makes it easy to convert values between several units of measurement'

setup(
    name="publish_pypi_package",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author="Refael",
    author_email="beker.refael@gmail.com",
    license='MIT',
    packages=find_packages(),
    install_requires=[],
    keywords='conversion',
    classifiers= [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3"
    ]
)