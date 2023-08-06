# publish-python-package

> Publish the Python package in PyPI

### Building the package files
------------------------

We need to build our python package:
> Before we begin this step, I should mention that I’m using Python3.

* In your terminal (at the root of the project) run:

``` 
python -m pip install --upgrade build

python -m build

python -m pip install --upgrade pip setuptools wheel

python setup.py sdist bdist_wheel

### This commands creates a source distribution and a shareable wheel that can be published on pypi.org.
```

* To test this, create a virtual Python environment.
* Then, install the convsn package using the wheel distribution. Depending on your Python installation. ```(you may need to use pip3)```
> Run: pip install <relative-path>python -m pip install .\publish-python-package\dist\package_pypi-0.0.2-py3-none-any.whl

> If need update then run: python -m pip install --upgrade py_package

* Use the python script file named test.py,
run the script while still in the virtual Python environment.

