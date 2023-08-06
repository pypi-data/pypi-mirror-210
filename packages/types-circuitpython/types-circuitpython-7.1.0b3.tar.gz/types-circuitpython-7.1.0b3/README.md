# types-circuitpython

![Package Version](https://img.shields.io/pypi/v/types-circuitpython?label=types-circuitpython&style=flat-square)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/types-circuitpython?style=flat-square)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/types-circuitpython?style=flat-square)

Type Support (typings) for [CircuitPython](https://github.com/adafruit/circuitpython) built-in binding packages.

Coding with `adafruit-circuitpython-typing`:

![adafruit-circuitpython-typing](https://raw.githubusercontent.com/hardfury-labs/types-circuitpython/master/screen-records/adafruit-circuitpython-typing.gif)

Coding with `types-circuitpython`:

![types-circuitpython](https://raw.githubusercontent.com/hardfury-labs/types-circuitpython/master/screen-records/types-circuitpython.gif)

## Usage

```bash
$ pip install types-circuitpython
```

## Long Term Support for 7.x and 8.x

Following [CircuitPython release versions](https://github.com/adafruit/circuitpython/releases), or [CircuitPython tags](https://github.com/adafruit/circuitpython/tags)

[Published versions](https://pypi.org/project/types-circuitpython/#history)

## Development

## Initialization

```bash
$ virtualenv .venv
$ . ./.venv/bin/activate
$ pip install -r requirements.txt
$ python setup.py develop
# or
$ pip install -e .
```

## Generate bindings

```bash
$ make generate version=<CIRCUITPYTHON VERSION>
```

## Code styles

```bash
$ make format
$ make lint
```
