# -*- coding: utf-8 -*-
from setuptools import setup

from commitytools import VERSION

with open("README.md", 'r', encoding="utf-8") as f:
	setup(
		name='Commity',
		version=VERSION,
		packages=['test', 'commitytools'],
		url="https://github.com/Cynnexis/Commity",
		license='GNU AFFERO GENERAL PUBLIC LICENSE',
		author='Valentin Berger',
		author_email='',
		description="Commity is a script that print the commits from a git branch in a user-friendly way using Markdown "
		"format, inspired from default pull-requests templates in BitBucket.",
		long_description=f.read(),
		long_description_content_type="text/markdown",
		python_requires='>=3.7',
		classifiers=[
			"Development Status :: 4 - Beta",
			"Environment :: Console",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: GNU Affero General Public License v3",
			"Natural Language :: English",
			"Operating System :: POSIX :: Linux",
			"Operating System :: Unix",
			"Programming Language :: Python :: 3.7",
			"Topic :: Software Development :: Build Tools",
			"Topic :: Software Development :: Version Control :: Git",
		])
