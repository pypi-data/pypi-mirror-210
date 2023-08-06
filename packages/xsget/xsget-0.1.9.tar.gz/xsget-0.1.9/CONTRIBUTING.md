# Contributing

## Setting up local development

To setup the development environment and run all tox tasks, we need to install
all supported Python version using <https://github.com/pyenv/pyenv>:

```console
pyenv install 3.7.16
pyenv install 3.8.16
pyenv install 3.9.16
pyenv install 3.10.11
pyenv install 3.11.3
```

Install and upgrade required Python packages:

```console
python -m pip install --upgrade pip flit pytest pylint pre-commit playwright "tox<4" tox-pyenv
```

Clone repository from GitHub and setting up the development environment:

```console
git clone https://github.com/kianmeng/xsget
cd xsget
python -m pip install -e .
playwright install
```

Show all available tox tasks:

```console
$ tox -av
...
default environments:
py37    -> testing against python3.7
py38    -> testing against python3.8
py39    -> testing against python3.9
py310   -> testing against python3.10
py311   -> testing against python3.11

additional environments:
cover   -> generate code coverage report in html
doc     -> generate sphinx documentation in html
gettext -> update pot/po/mo files
```

For code linting, we're using `pre-commit`:

```console
pre-commit install
pre-commit clean
pre-commit run --all-files
```

Or specific hook:

```console
pre-commit run pylint -a
```

## Create a Pull Request

Fork it at GitHub, <http://github.com/kianmeng/xsget/fork>

Create your feature branch:

```console
git checkout -b my-new-feature
```

Commit your changes:

```console
git commit -am 'Add some feature'
```

Push to the branch:

```console
git push origin my-new-feature
```

Create new Pull Request in GitHub.

## License

By contributing to xsget, you agree that your contributions will be licensed
under the LICENSE.md file in the root directory of this source tree.
