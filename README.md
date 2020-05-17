# Commity

![language: python][shield-language] ![license: GPL][shield-license] ![python: 3.7][shield-python-version] ![Commity CI/CD](https://github.com/Cynnexis/Commity/workflows/Commity%20CI/CD/badge.svg)

Commity is a script that print the commits from a git branch in a
user-friendly way using Markdown format, inspired from default
pull-requests templates in BitBucket.

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

> Note that if you want to change the source code of the project, you will need to run `yarn` in order to install the
> NPM modules. `Husky` is the module that help format the code using YAPF at each pre-commit.

### Usage

To execute Commity, you might need to specify some arguments:

* `-r` or `--repo`: The path to the git directory. By default,
the current folder is taken.
* `-b` or `--branch`: The name of the branch where to get the
commits. By default, the current branch is taken.
* `-o` or `--output`: The output file. All information will be written in the
given file. If the file is invalid, or no file is given, stdout is used instead.

**Example:**

`python commity.py -r C:\Users\Foo\MyProject -b feat/gui-buttons -o output.txt`

#### Run with Docker 🐳

It is possible to run `commity` from the given `Dockerfile`. Note that this method
is not optimized for this kind of usage, and is relatively long to execute, as you
will certainly have to build the image. Nevertheless, it is a good method if you
don't want to install Python and/or the required modules.

To execute `commity` using docker, please refer to the example below:

```bash
cd path/to/commity
docker build -t cynnexis/commity .
docker run -it -v "C:\Users\Foo\myproject:/myproject" cynnexis/commity run -r /myproject -b master -o /myproject/commity-output.txt
```

**Explanation:**

1. The first command is to move to the project repository.
2. Build the image, and name it "`cynnexis/commity`"
3. This command is the more complex one. It runs a container (`docker run -it`),
create a volume between your project on your host (your machine) and its copy
in the container (`-v "C:\Users\Foo\myproject:/myproject"`). Please replace the
first part with your project path on your host, and the second part with your
project name (with the `/` at the beginning). Then, the image name is specified
(`cynnexis/commity`), and the arguments are passed. After `run`, you can put any
arguments for `commity.py`. Make sure to replace `myproject` with your project
name again. If the command is successfully executed, you'll find the file
`commity-output.txt` under your project name on your host.

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
about it. You want to fight some scary and nasty segmentation
problem? Then go to the [Linux Kernel GitHub](https://github.com/torvalds/linux)
to fight some evil bugs, and help make UNIX a better system!

## Author

* **Valentin Berger ([Cynnexis](https://github.com/Cynnexis)):** developer

## License

This project is under the GNU Affero General Public License v3.0.
Please see the [LICENSE.txt](https://github.com/Cynnexis/Commity/blob/master/LICENSE.txt)
file for more detail (it's a really fascinating story written in
there!)

## Acknowledgments

* [Joey](https://stackoverflow.com/users/73070/joey) from
[this stackoverflow post](https://stackoverflow.com/a/12093994/7347145),
to have written the monstrous regex to match branch name.
* [NIKHIL C M](https://stackoverflow.com/users/3599013/nikhil-c-m) and
[Joe Chrysler](https://stackoverflow.com/users/361494/joe-chrysler) from
[this stackoverflow post](https://stackoverflow.com/a/52025740/7347145) for the git command to get a branch parent.
* Git team ; what a flawless system they created!

[python 3.7]: https://www.python.org/downloads/release/python-374/
[typeguard]: https://pypi.org/project/typeguard/
[gitpython]: https://gitpython.readthedocs.io/en/stable/index.html
[githubactions]: https://github.com/features/actions
[yapf]: https://github.com/google/yapf
[shield-language]: https://img.shields.io/badge/language-python-yellow.svg
[shield-license]: https://img.shields.io/badge/license-GPL-blue.svg
[shield-python-version]: https://img.shields.io/badge/python-3.7-yellow.svg
