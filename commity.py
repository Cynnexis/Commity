# -*- coding: utf-8 -*-

import os
import argparse
from typing import *
from typeguard import typechecked

import git

p = argparse.ArgumentParser(prog="Commity", description="Print commits of a specific branch as a list.")
p.add_argument("-r", "--repo", default=None, help="The repository. If not given, default value is the current directory.")
p.add_argument("-b", "--branch", default=None, help="The branch were to collect the commits. If not given, default value is current branch.")
args = p.parse_args()

if args.repo is None:
	args.repo = os.path.dirname(os.path.realpath(__file__))

# Get the repo
try:
	repo = git.Repo(args.repo)
except git.exc.InvalidGitRepositoryError:
	print("ERROR: The given folder is not a git repo.")
	exit(-1)

# noinspection PyUnboundLocalVariable
if repo.bare:
	print("ERROR: The given repository is bare.")
	exit(-2)

if args.branch is None:
	args.branch = repo.active_branch

if args.branch not in repo.branches:
	print("The branch \"{}\" does not exist.".format(args.branch))
	exit(-3)

print("On branch " + args.branch.name)


@typechecked
def decompose_commit(commit: str) -> Tuple[str, ...]:
	lines = commit.split('\n')
	if len(lines) > 2 and lines[0] != '' and lines[1] == '':
		return tuple(commit.split("\n\n", 2))
	else:
		if len(lines) == 2 and lines[1] == '':
			return commit.replace("\n", ''),
		else:
			return commit,


commits = list(repo.iter_commits(args.branch.name))
for commit in commits:
	print(decompose_commit(commit.message)[0])
