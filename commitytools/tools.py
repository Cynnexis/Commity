# -*- coding: utf-8 -*-
import os
from typing import Optional, Union, Tuple

import git
from typeguard import typechecked

from commitytools import plural
from commitytools.emoji import replace_emoji
from commitytools.issue_tracker import get_issues


@typechecked
def commity_repo(repo_path: Optional[str] = None,
					branch: Optional[str] = None,
					fixed_issues: bool = False,
					convert_emoji: bool = False) -> str:
	"""
	Core function or the program.
	:param repo_path: The path to the repository.
	:param branch: The git branch to analyze.
	:param fixed_issues: If `True`, the function will analyze the commits in the branch, and extract all issues
	following a keyword associated to "fix", "resolve" or "close", and print "Fixed " followed by the detected issues.
	Default value is `False`.
	:param convert_emoji: If `True`, all GitHub emoji markup will be converted to actual emoji. This requires an
	internet connection. If `False` (default value), the GitHub emoji markup are not treated.
	:return: Return the string representing the branch (all the commits messages).
	"""
	# If no repo has been given, take the current directory
	if repo_path is None:
		repo_path = os.getcwd()
	
	if os.name.strip().lower() == "nt":
		repo_path = repo_path.replace('\\', '/')
	else:
		repo_path = os.path.normpath(repo_path)
	
	# Get the repo
	repo = git.Repo(repo_path)
	
	# noinspection PyUnboundLocalVariable
	if repo.bare:
		raise git.exc.InvalidGitRepositoryError("The given repository is bare.")
	
	# If no branch has been given, take the current branch (it might be `master`)
	if branch is None:
		branch = repo.active_branch.name
	
	# noinspection PyTypeHints
	repo.branches: git.util.IterableList
	if branch not in repo.branches:
		raise git.exc.GitError("ERROR: The branch \"{}\" does not exist.\nAvailable branch{}: {}".format(
			branch, plural(repo.branches, plural="es"), ', '.join(map(lambda b: b.name, repo.branches))))
	
	content = ''
	
	# Get the list of all commits from the given branch
	for i, commit in enumerate(repo.iter_commits(rev=branch)):
		# Print the commit
		if i == 0 or len(commit.parents) <= 1:
			content += beautify_commit(commit) + '\n'
		else:
			break
	
	# Add fixed issues
	if fixed_issues:
		issues = get_issues(content, only_fixed=True)
		if len(issues) > 0:
			fixed_str = "Fixed "
			if len(issues) == 1:
				fixed_str += issues[0]
			else:
				# Join all the issues, except for the last (add an 'and' instead of comma)
				fixed_str += ", ".join(issue for issue in issues[:-1]) + f" and {issues[-1]}"
			
			content = fixed_str + ".\n\n" + content
	
	# Convert emoji
	if convert_emoji:
		content = replace_emoji(content)
	
	print(content)
	
	repo.close()
	return content


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
