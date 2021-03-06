# brainload Development information

This document is intended for developers who work on `brainload`. Users should ignore this file and install a release via `pip` instead. See the [README file in the repo root](../README.md) for details.

While `brainload` works on several platforms, development happens under Linux and sometimes MacOS, and this document and the development scripts assume a POSIX environment.

## Essential tools

You will need Python 3 and some standard development tools. Under Linux, this should be enough:

```console
sudo apt-get install python-pip build-essential git
```

Make sure you have Python 3, not Python 2. (Run `python --version` to find out.)

## Development installation

It is recommended to use a virtual environment for hacking on `brainload`. First, clone the repo:

```console
mkdir ~/develop/          # replace this dir with whatever you like or use an existing directory where you store all your code or projects.
cd ~/develop
git clone https://github.com/dfsp-spirit/brainload
cd brainload/             # we will refer to this directory as the `repository root` or `repo root` throughout this document.
```

Now let's prepare the dev environment. In the repo root:

```console
pip install --user virtualenv      # unless you already have it
python -m virtualenv env/          # creates a virtual python environment in the new directory `env/` in the repo root, i.e., `~/develop/brainload/env/` in our example
```


Note: Once you have created the virtual environment, all you have to do is use it:

```console
cd ~/develop/brainload             # replace with your repo root
source env/bin/activate            # to activate the virtual environment

some_command...                    # run stuff
another_command...

deactivate                         # to leave it
```

Ensure that you are still in the repo root, then activate the virtual environment and install `brainload` in development mode:

```console
source env/bin/activate
pip install --editable .           # installs brainload from the current directory, and grabs its dependencies from PyPI
```

You can now use the `brainload` module by typing `import brainload` in your python application or an interactive python session. Changes you make to the module source are applied automatically.



## Tests

Tests and test data are not shipped in the releases, clone the source repo and follow the installation instructions for the development version if you want to run them. Once you have done that, continue from here.

### Running the tests locally

#### Obtaining the test data

Not all data is included with the repo, as the test data is quite large and some fake subjects are generated by copying others. The good news is that you can get all test data by running a single shell script from the repo root:

```console
cd ~/develop/brainload               # replace with your repo root
./develop/get_test_data_all.bash
```

The script downloads all required [neuroimaging test data from Github](https://github.com/dfsp-spirit/neuroimaging_testdata). If you have a properly configured local installation of FreeSurfer (with environment variable `FREESURFER_HOME` pointing to the installation directory), it will prefer that for some data.

#### Running the tests

The easiest it to use the integration into `setup.py`, as this will install all test dependencies for you automatically. In the virtual environment and the top-level brainload directory, just run:

```console
python setup.py test
```

#### Test coverage

Test coverage statistics are displayed automatically when running the tests as described above. To see the coverage line by line, run `coverage html` and then open `htmlcov/index.html` in your favorite browser.



### Continuous Integration

The tests are run automatically when you push to master and developers get results by email. Build status from travis-ci.org (Linux, branch master):

[![Build Status](https://travis-ci.org/dfsp-spirit/brainload.svg?branch=master)](https://travis-ci.org/dfsp-spirit/brainload)


Note that not all test data is available on Travis and as a result, some tests get skipped. We are working on this. When run locally with all test data, coverage must be greater than 95% for all files.


## Packaging

If you want to get the tools you need for all steps below right now and all at once:

```console
pip install --upgrade setuptools wheel twine sphinx sphinx_rtd_theme
conda install conda-build anaconda-client
```

### Creating the release package


#### Update version information

Set the new version information:

```console
export OLD_VERSION="0.3.4"      # the old version that is already on pypi
export NEW_VERSION="0.3.5"      # the new version you are about to package
export NEW_RELEASE="v${NEW_VERSION}"
cd ~/develop/brainload/        # repo root
git checkout master
git pull

vim setup.py                   # update 'version' in here
vim doc/conf.py                # update 'version' and 'release' in here
vim MANIFEST.in                # update the new documentation to include: docs/${NEW_RELEASE}/ (hard-code the number, of course)
vim src/brainload/__init__.py  # update __version__ in here.

git add setup.py doc/conf.py MANIFEST.in src/brainload/__init__.py
```

#### Build docs

First note the difference between the directories 'doc' (source for documentation and sphinx templates) and 'docs' (Github page made containing the generated documentation). Do not confuse them.

If you added a new module (code file), be sure to add it to `doc/brainload.rst` so the documentation gets generated from the doc strings and it shows up in the docs.

We use sphinx with the theme from `readthedocs.org` to generate the documentation. In the virtual environment:

```console
pip install sphinx sphinx_rtd_theme
```

Now build the documentation:

```console
cd doc/
make html
```

This will build the documentation in HTML format and place it in `doc/_build/html/`. Now copy it to the correct location to be included in the release:

```console
cd ..    # back to repo root
mkdir docs/${NEW_RELEASE}/
cp -r doc/_build/html/* docs/${NEW_RELEASE}/
```

The [Brainload API documentation](http://dfsp-spirit.github.io/brainload) is made available on the internet using Github Pages, and our page is served from the directory `docs/` (note the `s` at the end) in this repo. You have to update the following HTML files:

- `docs/index.html`
- `docs/versions.html`

Now it's time to add all those changes to git:

```console
git add docs/${NEW_RELEASE}
git add docs/index.html docs/versions.html
git commit -m "Update version to ${NEW_VERSION}, add generated documentation."
```


#### Build the packages for PyPI / pip

We use setuptools for building:

```console
pip install --upgrade setuptools wheel              # just make sure we have the latest versions
rm -rf dist/
python setup.py sdist bdist_wheel --universal
```

Carefully check the output of the command for warnings or errors: wrong information in `setup.py` or `MANIFEST.in` may become obvious. If something is wrong, fix it and commit again.

### Distributing the packages


We are more or less just following the [official Python packaging user guide](https://packaging.python.org/tutorials/packaging-projects/) here. First make sure you have the required tools:

```console
pip install --upgrade twine            # in the virtual env. Add `--user` if you prefer to do it outside.
```

#### PyPI testing

```console
twine upload --repository-url https://test.pypi.org/legacy/ dist/*     # will ask for your PyPI test credentials for brainload
```

Now try it in a fresh virtual environment (you may have to wait a sec for it to become available):

```console
$ deactivate                                  # leave current virtual env
$ python -m virtualenv env_for_${NEW_VERSION}             # create a fresh one
$ source env_for_${NEW_VERSION}/bin/activate              # activate it
$ pip install nibabel six        # these are not on test.pypi.org
$ pip install --index-url https://test.pypi.org/simple/ brainload     # install it.
#now try the example client. e.g.:
$ python -c 'import brainload as bl; print(bl.__version__)'
0.3.4
$ python
>>> import brainload as bl
>>> # do more stuff
>>> quit()
$ deactivate
$ rm -rf env_for_${NEW_VERSION}
```

If something is wrong, fix it and commit again. If everything looks fine, tag the current version as the new release:

```console
git tag -a ${NEW_RELEASE} -m "Some annotation for this release."
git push origin --tags
```

It is finally time to upload it to the real PyPI:

#### PyPI

```console
twine upload dist/*                           # will ask for your PyPI credentials for brainload
```

Now, update the version information in the source code to the next dev release in `src/brainload/__init__.py`. Example: If you just released `v0.3.4`, set it to `v0.3.5dev` in there. The other files will be updated only at the next release (and the version in init.py will also be changed then, of course). But this allows you to always find out which version of the code somebody is running. Everything labeled as dev is not a release.


#### Anaconda (build and distribution, recipe)


If you are experienced with building for conda, all you want to know is maybe the following: the recipe can be found in `REPO_ROOT/develop/anaconda_dist/recipe/RELEASE/meta.yaml`.

This has been done successfully under Linux and MacOS. It more or less follows the [official conda build instructions](https://conda.io/docs/user-guide/tutorials/build-pkgs.html).

> IMPORTANT: This builds the anaconda package based on the PyPI package, so you have to upload to PyPI before starting this.

##### Prepare environment

Get the tools: install `conda` on your system and fire it up, then use it to get the build tools. We will assume you installed it into ${CONDA_DIR}, which could be something like `~/software/anaconda3`.

The first step is to activate conda if it is not yet active. Type `conda --version` to check whether the `conda` command is available. If the command is not found:


```console
source ${CONDA_DIR}/etc/profile.d/conda.sh     # does NOT activate the base conda environment
conda --version
conda activate                                 # activates the base environment
conda env list        # shows available environments, the one marked with an asterisk is active (should be base)
```


Now that conda is active, we are in the conda `base` environment. Let's create a new sub environment and install the required tools into it:

```console
cd develop/anaconda_dist/recipe/
conda update conda
conda create -y --name blbuild python=3.7                  # skip if you have done these steps before
conda activate blbuild
conda install -y conda-build anaconda-client conda-verify
mkdir /tmp/condaishacky         # just don't ask, you do not wanna know why this is needed...
conda config --add channels conda-forge      # add channel so the next command will find dependencies, e.g., nibabel
```

##### Prepare new recipe

If no recipe exists for the release (i.e., you are currently creating the recipe: there is no directory `develop/anaconda_dist/recipe/${NEW_RELEASE}`), follow this sub section. Otherwise, skip to `Build the conda package` below.

Create a new dir for the release, copy the old `meta.yaml` file in there. Create a new skeleton file just to get the new hash of the file on PyPI, then update the hash in the new `meta.yaml` file and you're ready to go. If you introduced or changed dependencies, you will have to do more, of course.

```console
# we are still in REPO_ROOT/develop/anaconda_dist/recipe/
mkdir ${NEW_RELEASE}
cp ${OLD_RELEASE}/meta.yaml ${NEW_RELEASE}        
mkdir /tmp/condaishacky         # just don't ask, you do not wanna know why this is needed...
# Before running the next command, delete the directory REPO_ROOT/develop/anaconda_dist/recipe/brainload in case it exists
CONDA_BLD_PATH=/tmp/condaishacky conda skeleton pypi brainload --version ${NEW_VERSION}
```

This created a new skeleton file at  `REPO_ROOT/develop/anaconda_dist/recipe/brainload/meta.yaml`. Open the file in a text editor and copy the file hash of the pypi release from there (see the sha256 line). This is the only reason why we need the file.

```console
vim ${NEW_RELEASE}/meta.yaml         # Update the version at the top AND paste the hash in here. Save and you have a new recipe.
```


##### Build the conda package

```console
CONDA_BLD_PATH=/tmp/condaishacky conda-build ${NEW_RELEASE}                        # may take a while... will output the full path to the file in the end. You will need this soon.
```

When the build is done, upload the package:

```console
anaconda upload /tmp/condaishacky/noarch/$PKG_FILENAME         # may ask for your condacloud credentials for brainload
```

Finally, add the conda recipe to the repo and delete the temporary directories:

```console
git add ${NEW_RELEASE}
git commit -m "Added conda recipe for release ${NEW_RELEASE}."
rm -rf pkg_converted/ tmp_brainload/ /tmp/condaishacky
```

The conda package release is done, remember to create a new release on GitHub (see below).


##### Anaconda: How the base recipe was created

You do not have to do this again, but still here is how I created the `meta.yaml` file that can be found in `develop/anaconda_dist/recipe`.

It follows the [official guide using the skeleton from PyPI method](https://conda.io/docs/user-guide/tutorials/build-pkgs-skeleton.html).

```console
cd develop/anaconda_dist
conda update conda
conda create -y --name blbuild python=3.7                 # skip if you have done these steps before
conda activate blbuild
conda install -y conda-build anaconda-client conda-verify
mkdir /tmp/condaishacky         # just don't ask, you do not wanna know why this is needed...
CONDA_BLD_PATH=/tmp/condaishacky conda skeleton pypi brainload --version ${NEW_VERSION}
```

The last command created a skeleton version of the conda `meta.yaml` build file based on the `setup.py` file from pip and placed it in a new directory named `brainload`. So you should now have a file at `REPO_ROOT/develop/anaconda_dist/brainload/meta_yaml`. This skeleton version is not ready for usage though and the build will fail with it. To create the final version, the following steps were needed:

- In the `extra` section, full in the `recipe-maintainers` information
- In the `about` section, full in the `doc_url` and `dev_url` information (http://dfsp-spirit.github.io/brainload and https://github.com/dfsp-spirit/brainload)
- Setuptools will download some dependencies at install time or later when installing via pip, e.g., pytest-runner, when you run `python setup.py test`. This does not work with conda, so you have to list all these dependencies manually in the `meta.yaml` file for conda. These dependencies currently are the following packages:
    - pytest
    - pytest-cov
    - pytest-runner

You have to add them in the following three sections:

    - requirements | hosts
    - requirements | run
    - test | requires

Save the file `meta.yaml`, and you should have a working recipe.

### Release on GitHub

Create a new release (from the tag we pushed earlier) on Github and attach the source and binary distributions created for PyPI. They are in `REPO_ROOT/dist/`.

This should be pretty self-explanatory, check the GitHub documentation if you need help.

## Supported Python major versions

Official support for Python 2.7 will end in December 2019. Python >= 3.5 is now the default Python version for Brainload and  we will drop support for Python 2.x soon.
