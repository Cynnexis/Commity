# -*- coding: utf-8 -*-
import collections
import os
from typing import Optional, Union, Tuple, Any

import git
from typeguard import typechecked

log_buffer = ""

@typechecked
def commity_repo(repo_path: Optional[str] = None,
					branch: Optional[str] = None,
					output: Optional[str] = None) -> str:
	global log_buffer
	log_buffer = ""
	
	# If no repo has been given, take the current directory
	if repo_path is None:
		repo_path = os.getcwd()
	
	if os.name.strip().lower() == "nt":
		repo_path = repo_path.replace('\\', '/')
	else:
		repo_path = os.path.normpath(repo_path)
	
	# Get the repo
	try:
		repo = git.Repo(repo_path)
	except git.exc.InvalidGitRepositoryError:
		log("ERROR: The given folder is not a git repo: \"{}\"".format(repo_path),
			output=output)
		exit(1)
	
	# noinspection PyUnboundLocalVariable
	if repo.bare:
		log("ERROR: The given repository is bare.", output=output)
		exit(2)
	
	# If no branch has been given, take the current branch (it might be `master`)
	if branch is None:
		branch = repo.active_branch.name
	
	# noinspection PyTypeHints
	repo.branches: git.util.IterableList
	if branch not in repo.branches:
		log("ERROR: The branch \"{}\" does not exist.\nAvailable branch{}: {}".format(
			branch,
			plural(repo.branches,
					plural="es"),
			', '.join(map(lambda b: b.name, repo.branches))),
			output=output)
		exit(5)
	
	# If an output has been given and the file already exist, remove it:
	if output is not None and os.path.exists(output) and os.path.isfile(output):
		os.remove(output)
	
	log("On branch " + branch, end="\n\n", output=output)
	
	# Get the list of all commits from the given branch
	for i, commit in enumerate(repo.iter_commits(rev=branch)):
		# Print the commit
		if i == 0 or len(commit.parents) <= 1:
			log(beautify_commit(commit), output=output)
		else:
			break
	
	repo.close()
	return log_buffer

@typechecked
def plural(number: Union[int,
							collections.abc.Iterable],
			singular: str = '',
			plural: str = ''):
	if hasattr(number, "__len__"):
		# noinspection PyTypeChecker
		number = len(number)
	
	if number <= 0 or number >= 2:
		return plural
	else:
		return singular

@typechecked
def log(values: Any = '',
		output: Optional[str] = None,
		mode: str = 'a',
		encoding: str = "utf-8",
		end='\n',
		flush: bool = True,
		*args):
	global log_buffer
	log_buffer += values + end
	if isinstance(values, str) and args is not None and len(args) > 0:
		values = values.format(*args)
	if output is not None:
		try:
			f = open(output, mode=mode, encoding=encoding)
			f.write(values + end)
		except OSError:
			print(values, end=end, flush=flush)
	else:
		print(values, end=end, flush=flush)

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
	
	def add_bullet(part: str,
					bullet: str = '*',
					prefix: str = '',
					suffix: str = '\n') -> str:
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
