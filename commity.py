# -*- coding: utf-8 -*-

import os
import re
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
	args.branch = repo.active_branch.name

if args.branch not in repo.branches:
	print("The branch \"{}\" does not exist.".format(args.branch))
	exit(-3)

print("On branch " + args.branch)

# Pattern inspired from Joey's, https://stackoverflow.com/a/12093994/7347145 (consulted on July the 9th, 2019)
rev_pattern = re.compile(r"([a-fA-F0-9]{40})\s((?!.*/\.)(?!.*\.\.)(?!/)(?!.*//)(?!.*@\{)(?!@$)(?!.*\\)[^\000-\037\177 ~^:?*[]+/?[^\000-\037\177 ~^:?*[]+(?<!\.lock)(?<!/)(?<!\.))(?:\^([0-9]+))?(?:~([0-9]+))?")


@typechecked
def decompose_commit(commit: Union[str, git.Commit]) -> Tuple[str, ...]:
	if isinstance(commit, git.Commit):
		commit = commit.message
	
	lines = commit.split('\n')
	if len(lines) > 2 and lines[0] != '' and lines[1] == '':
		return tuple(commit.split("\n\n", 2))
	else:
		if len(lines) == 2 and lines[1] == '':
			return commit.replace("\n", ''),
		else:
			return commit,


@typechecked
def get_head_name_from_commit(commit: Union[str, git.Commit]) -> str:
	if isinstance(commit, git.Commit):
		commit = commit.name_rev
	
	global rev_pattern
	matches = re.findall(rev_pattern, commit)
	if matches is None or len(matches) == 0:
		return ''
	matches = matches[0]
	if matches is None or len(matches) < 2:
		return ''
	
	return matches[1]


@typechecked
def beautify_commit(commit: Union[str, git.Commit]) -> str:
	def add_bullet(part: str, prefix: str = '', suffix: str = '\n') -> str:
		if not part.startswith('*'):
			return prefix + "* " + part + suffix
		else:
			return prefix + part + suffix
	
	if isinstance(commit, git.Commit):
		commit = commit.message
	
	parts = decompose_commit(commit)
	if parts is None or len(parts) == 0:
		return ''
	
	content = add_bullet(parts[0])
	
	if len(parts) > 1:
		for i in range(1, len(parts)):
			lines = parts[i].split('\n')
			for line in lines:
				if line != '':
					content += add_bullet(line, prefix='\t')
		content += '\n'
	
	return content


commits = list(repo.iter_commits(args.branch))
for commit in commits:
	branch_name = get_head_name_from_commit(commit)
	if branch_name != args.branch:
		break
	
	print(beautify_commit(commit))
