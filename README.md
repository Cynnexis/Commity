# Commity

![language: python][shield-language] ![license: GPL][shield-license] ![python: 3.7][shield-python-version] ![Commity CI/CD](https://github.com/Cynnexis/Commity/workflows/Commity%20CI/CD/badge.svg)

Commity is a script that print the commits from a git branch in a user-friendly way using Markdown format, inspired from
default pull-requests templates in BitBucket.

## Getting Started

### Prerequisites

You need [Python 3.7][python 3.7] to execute this script.

Here is the command to install all necessary packages:

With pip:

```bash
pip install --no-cache-dir -r requirements.txt
```

With conda (and its environment):

```bash
conda install --name myenv -c conda-forge --file requirements.txt
```

### Installing

To install this script, you first need to clone this project, and
then execute [`commity.py`](https://github.com/Cynnexis/Commity/blob/master/commity.py).

### Usage

To execute Commity, you might need to specify some arguments:

* `-r` or `--repo`: The path to the git directory. By default,
the current folder is taken.
* `-b` or `--branch`: The name of the branch where to get the
commits. By default, the current branch is taken.
* `-i` or `--issue`: If given, the first line will contain all the issues that have been marked as "fixed" in the
commits messages of the given branch.

**Example:**

`python commity.py -r C:\Users\Foo\MyProject -b feat/gui-buttons -i`

#### Run with Docker 🐳

It is possible to run `commity` from the given `Dockerfile`.

To execute `commity` using docker, please refer to the example below:

**With Makefile:**

```bash
cd path/to/commity
make docker-build
docker run -it -v "C:\Users\Foo\myproject:/myproject" cynnexis/commity run -r /myproject -b master --issue
```

**Without Makefile:**

```bash
cd path/to/commity
docker build -t cynnexis/commity .
docker run -it -v "C:\Users\Foo\myproject:/myproject" cynnexis/commity run -r /myproject -b master --issue
```

### Alias

If your using bash, you can setup an alias to call `commity`:

First, let's create a conda environment if you have not done iet yet:

```bash
cd path/to/commity
conda create --name commity python=3.7.6
conda install --name commity -c conda-forge --file requirements.txt
```

Then, activate the environment:

```bash
conda activate commity
```

Get the path to your Python environment:

```bash
which python
```

For this tutorial, let's assume the path is `/home/user/anaconda3/envs/commity/bin/python`. Create an alias with the
following command:

```bash
echo alias commity="/home/user/anaconda3/envs/commity/bin/python /absolute/path/to/commity/commity.py" >> ~/.bash_aliases
```

And it's ready! To get all the commits messages of a local repository, go to your project folder, and execute the
`commity` command such as:

```bash
commity -i
```

The command will assume the current working directory is the repository, and will analyze the current branch. The
fixed issues will be printed with the `-i` option.

## Built With

* [Python 3.7][python 3.7]
* [typeguard][typeguard]
* [GitPython][gitpython]
* [GitHub Actions][githubactions]
* [YAPF][yapf]

## Contributing

Contribution are not permitted yet, because this project is
really simple and should not be a real problem. You noticed a bug
in the script or in the source code? Feel free to post an issue
about it.

## Author

* **Valentin Berger ([Cynnexis](https://github.com/Cynnexis)):** developer

## License

This project is under the GNU Affero General Public License v3.0.
Please see the [LICENSE.txt](https://github.com/Cynnexis/Commity/blob/master/LICENSE.txt)
file for more detail (it's a really fascinating story written in
there!)

## Acknowledgments

* Git team ; what a flawless system they created!

[python 3.7]: https://www.python.org/downloads/release/python-374/
[typeguard]: https://pypi.org/project/typeguard/
[gitpython]: https://gitpython.readthedocs.io/en/stable/index.html
[githubactions]: https://github.com/features/actions
[yapf]: https://github.com/google/yapf
[shield-language]: https://img.shields.io/badge/language-python-yellow.svg
[shield-license]: https://img.shields.io/badge/license-GPL-blue.svg
[shield-python-version]: https://img.shields.io/badge/python-3.7-yellow.svg
