# Packaging and uploading to pypi

These steps are derived from the offical [Packaging Python Projects article](https://packaging.python.org/tutorials/packaging-projects/).

0. Remember to update the version number tuple in `scienceio/__init__.py`.

1. [Create a release](https://docs.github.com/en/github/administering-a-repository/releasing-projects-on-github/managing-releases-in-a-repository) in our GitHub repo.

2. Clone this repo at the point of the newly-created release into a working directory.

3. Create and activate a virtual environment in the repo root directory.

4. Install `build`: `python3 -m pip install --upgrade build`

5. In the repo root directory, run: `python3 -m build`

6. Verify that a `dist/` subdirectory is created, and that it contains both a `*.tar.gz` and a `*.whl` file matching the new package version.

7. Create a TestPyPI account if needed, as described [here](https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives), saving the API key.

8. Install `twine`: `python3 -m pip install --upgrade twine`

9. Upload package to TestPyPI, using `__token__` and your TestPyPI API key for the username and password, respectively: `python3 -m twine upload --repository testpypi dist/*`

10. Create a new demo project to test installation of the new package.

11. Create and activate a demo virtualenv.

12. Install the package from TestPyPI in the demo virtualenv: `python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps scienceio`

13. Test that the package can be imported and the version number is present: `python -c 'import scienceio; print(scienceio.__version__)'`

14. Create a PyPI account if needed, as described [here](https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives), saving the API key.

15. Upload package to PyPI, using `__token__` and your PyPI API key for the username and password, respectively: `python3 -m twine upload --repository testpypi dist/*`

16. Done!


### Important files

- `pyproject.toml` tells build tools (like pip and build) what is required to build your project
- `setup.cfg` is the configuration file for setuptools. Content on this file is considered static metadata and should be preferred.
- `setup.py` setup.py is the build script for setuptools. This is dynamic data and should be used only when absolutely necessary, for any items that are dynamic or determined at install-time, as well as extension modules or extensions to setuptools.

**Help:** https://packaging.python.org/tutorials/packaging-projects/
