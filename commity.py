# -*- coding: utf-8 -*-

import os
import re
import traceback

import git
import argparse
from typing import *
from typeguard import typechecked

# Parse the arguments
p = argparse.ArgumentParser(prog="Commity", description="Print commits of a specific branch as a list.")
p.add_argument("-r", "--repo", default=None, help="The repository. If not given, default value is the current directory.")
p.add_argument("-b", "--branch", default=None, help="The branch were to collect the commits. If not given, default value is current branch.")
p.add_argument("-o", "--output", default=None, help="The output file. All information will be written in the given file. If the file is invalid, or no file is given, stdout is used instead.")
args = p.parse_args()


def log(values, end='\n', flush: bool = True):
	global args
	if args.output is not None:
		try:
			f = open(args.output, mode='a', encoding="utf-8")
			f.write(values + end)
		except OSError:
			print(values, end=end, flush=flush)
	else:
		print(values, end=end, flush=flush)


# If no repo has been given, take the current directory
if args.repo is None:
	args.repo = os.path.dirname(os.path.realpath(__file__))

# Get the repo
try:
	repo = git.Repo(args.repo)
except git.exc.InvalidGitRepositoryError:
	log("ERROR: The given folder is not a git repo: \"{}\"".format(args.repo))
	exit(-1)

# noinspection PyUnboundLocalVariable
if repo.bare:
	log("ERROR: The given repository is bare.")
	exit(-2)

# If no branch has been given, take the current branch (it can be `master`)
if args.branch is None:
	args.branch = repo.active_branch.name

if args.branch not in repo.branches:
	log("The branch \"{}\" does not exist.".format(args.branch))
	exit(-3)

# If an output has been given and the file already exist, remove it:
if os.path.exists(args.output) and os.path.isfile(args.output):
	os.remove(args.output)

log("On branch " + args.branch, end="\n\n")

# Pattern inspired from Joey's, https://stackoverflow.com/a/12093994/7347145 (consulted on July the 9th, 2019)
# This pattern detect the name of the branch in the revision string of a commit
rev_pattern = re.compile(r"([a-fA-F0-9]{40})\s((?!.*/\.)(?!.*\.\.)(?!/)(?!.*//)(?!.*@\{)(?!@$)(?!.*\\)[^\000-\037\177 ~^:?*[]+/?[^\000-\037\177 ~^:?*[]+(?<!\.lock)(?<!/)(?<!\.))(?:\^([0-9]+))?(?:~([0-9]+))?")


@typechecked
def decompose_commit(commit: Union[str, git.Commit]) -> Tuple[str, ...]:
	"""
	Decompose a commit message into two parts: its title and its main content.
	:param commit: The commit. It can be a commit object or the message itself.
	:return: Return a tuple containing at least one item (the title, or the entire message if no format has been
	detected), and a second one if the format has been detected (the content).
	"""
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
	"""
	Return the name of the branch associated to the given commit.
	:param commit: The commit. It can be a Commit object, or the revision string.
	:return: Return the branch name. If not found, return an empty string.
	"""
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
	"""
	Beautify the given commit according to the markdown format.
	:param commit: The commit. It can be the object Commit or the message itself.
	:return: Return the commit in a more adapted format.
	"""
	def add_bullet(part: str, bullet: str = '*', prefix: str = '', suffix: str = '\n') -> str:
		if not part.startswith(bullet):
			return prefix + bullet + ' ' + part + suffix
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
					if not line.startswith('*'):
						content += add_bullet(line, prefix='\t', bullet='')
					else:
						content += add_bullet(line, prefix='\t')
		content += '\n'
	
	return content


# Get the list of all commits from the given branch
commits = list(repo.iter_commits(args.branch))
for commit in commits:
	# If we detect we are not in the same branch anymore (come back to the branch parent), then we stop the loop.
	branch_name = get_head_name_from_commit(commit)
	if branch_name == args.branch or branch_name not in repo.branches:
		# Print the commit
		log(beautify_commit(commit))

repo.close()
