# -*- coding: utf-8 -*-
import os
import re
from typing import Optional, Union, Tuple, Any, Iterable
import networkx as nx

import git
from typeguard import typechecked

log_buffer = ""
DEBUG = bool(os.getenv("DEBUG", "False"))

# Pattern inspired from Joey's, https://stackoverflow.com/a/12093994/7347145 (consulted on July the 9th, 2019)
# This pattern detect the name of the branch in the revision string of a commit
rev_pattern = re.compile(
	r"([a-fA-F0-9]{40})\s((?!.*/\.)(?!.*\.\.)(?!/)(?!.*//)(?!.*@\{)(?!@$)(?!.*\\)[^\000-\037\177 ~^:?*[]+/?[^\000-\037\177 ~^:?*[]+(?<!\.lock)(?<!/)(?<!\.))(?:\^([0-9]+))?(?:~([0-9]+))?"
)

@typechecked
def commity_repo(repo: Optional[str] = None,
					branch: Optional[str] = None,
					output: Optional[str] = None) -> str:
	global log_buffer
	log_buffer = ""
	
	# Create graph for repo
	graph = nx.DiGraph()
	
	# If no repo has been given, take the current directory
	if repo is None:
		repo = os.path.dirname(os.path.realpath(__file__))
	
	# Get the repo
	try:
		repo = git.Repo(repo)
	except git.exc.InvalidGitRepositoryError:
		log("ERROR: The given folder is not a git repo: \"{}\"".format(repo),
			output=output)
		exit(-1)
	
	# noinspection PyUnboundLocalVariable
	if repo.bare:
		log("ERROR: The given repository is bare.", output=output)
		exit(-2)
	
	# Fill graph
	branches: Iterable[git.Head] = repo.branches
	for b in branches:
		for c in repo.iter_commits(rev=b.name):
			if c not in graph:
				graph.add_node(c)
			for parent in c.parents:
				if not graph.has_edge(parent, c):
					graph.add_edge(parent, c, weight=c.stats.total["lines"])
	
	# Draw the graph if in debug mode
	if DEBUG:
		try:
			import matplotlib.pyplot as plt
			nx.draw(
				graph,
				labels={c: c.summary for c in graph},
				node_size=400,
				font_size=16,
				font_color='r',
				pos=nx.spring_layout(graph,
										k=0.15,
										iterations=20))
			plt.savefig("graph.png")
		except ImportError:
			pass
	
	# If no branch has been given, take the current branch (it might be `master`)
	if branch is None:
		branch = repo.active_branch.name
	
	dlog("Analysing branch \"{}\"", branch)
	
	if branch not in repo.branches:
		log("The branch \"{}\" does not exist.".format(branch), output=output)
		exit(-3)
	
	# If an output has been given and the file already exist, remove it:
	if output is not None and os.path.exists(output) and os.path.isfile(output):
		os.remove(output)
	
	log("On branch " + branch, end="\n\n", output=output)
	
	# Get the list of all commits from the given branch
	for commit in repo.iter_commits(rev=branch):
		# If the commit has more than 1 child, then stop here. We just met a merge commit.
		if len(list(graph.successors(commit))) > 1:
			break
		# If we detect we are not in the same branch anymore (come back to the branch parent), then we stop the loop.
		branch_name = get_head_name_from_commit(commit)
		if branch_name == branch or branch_name not in repo.branches:
			# Print the commit
			log(beautify_commit(commit), output=output)
	
	repo.close()
	return log_buffer

@typechecked
def dlog(values: Any, *args):
	if DEBUG:
		if isinstance(values, str) and args is not None and len(args) > 0:
			values = values.format(*args)
		print("DEBUG> {}".format(values))

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
