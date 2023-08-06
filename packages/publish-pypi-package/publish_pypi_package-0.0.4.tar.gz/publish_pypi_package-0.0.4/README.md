# publish-python-package

> Publish the Python package in PyPI

### Building the package files in local
------------------------

We need to build our python package:
> Before we begin this step, I should mention that I’m using Python3.

1. In your terminal (at the root of the project) run:

``` 
python -m pip install --upgrade build

python -m build

python -m pip install --upgrade pip setuptools wheel

python setup.py sdist bdist_wheel

### This commands creates a source distribution and a shareable wheel that can be published on pypi.org.
```

2. To test this, create a virtual Python environment.
3. Then, install the convsn package using the wheel distribution. Depending on your Python installation. ```(you may need to use pip3)```
> Run: pip install <relative-path>python -m pip install .\publish-python-package\dist\package_pypi-0.0.2-py3-none-any.whl

> If need update then run: python -m pip install --upgrade py_package

4. Use the python script named `tests/test_tempertaure.py`,
run the script while still in the virtual Python environment.

## Using the publish Python package
> pip searches for the package files in the official Python Package Index, on pypi.org.

> Installing Python pip on your system allows you to manage PyPI packages easily.

- There are two installation options, via test pypi or via pypi. </br>Both work and have been tested successfully. </br>
The way to use:
```
## Test PyPi - test.pypi.org
python -m pip install --upgrade --index-url https://test.pypi.org/simple publish_pypi_package

## PyPi - pypi.org
python -m pip install publish_pypi_package
```
- Run the tests/test_tempertaure.py script
