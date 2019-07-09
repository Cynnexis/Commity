# Commity

![language: python][shield-language] ![license: GPL][shield-license] ![python: 3.7][shield-python-version]

Commity is a script that print the commits from a git branch in a
user-friendly way using Markdown format, inspired from default
pull-requests templates in BitBucket.

## Getting Started

### Prerequisites

You need [Python 3.7][python 3.7] to execute this script.

Here is a list of Python package to install to make this program
works:

```bash
pip install typeguard
pip install gitpython
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

**Example:**

`python commity.py -r C:\Users\Foo\MyProject -b feat/gui-buttons`

## Built With

* [Python 3.7][python 3.7]
* [typeguard][typeguard]
* [GitPython][gitpython]

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
* Git team ; what a flawless system they created!

[python 3.7]: https://www.python.org/downloads/release/python-374/
[typeguard]: https://pypi.org/project/typeguard/
[gitpython]: https://gitpython.readthedocs.io/en/stable/index.html
[shield-language]: https://img.shields.io/badge/language-python-yellow.svg
[shield-license]: https://img.shields.io/badge/license-GPL-blue.svg
[shield-python-version]: https://img.shields.io/badge/python-3.7-yellow.svg
