# Building MeerkatPM

## Prerequisites
- **Python >=3.8**
- **pip >=20.0.2**
- **build >=0.10.0**

## Building from source (on Linux machine)
To build MeerkatPM from source you need to preform the following steps:

1. Clone the repo from GitHub:
    ```bash
    $ git clone https://github.com/MeerkatBoss/MeerkatPM.git
    ```
2. Change your working directory:
    ```bash
    $ cd MeerkatPM
    ```
3. Build Python package
    ```bash
    $ python3 -m build
    ```

## Installation (on Linux machine)
MeerkatPM can be installed via `pip`. To install MeerkatPM, download release archive and unpack it. There, you will
find `.tar.gz` file, that can be installed with `pip`. Alternatively, you can build package from source and install
it yourself with `pip`.

## Uninstalling (on Linux machine)
MeerkatPM can be uninstalled with pip:
```bash
$ pip uninstall meerkatpm
```
