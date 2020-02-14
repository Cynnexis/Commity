# -*- coding: utf-8 -*-
import os
import re
import subprocess
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

reflog_pattern = re.compile(
	r"^([a-f0-9]{7})\s*((?!.*/\.)(?!.*\.\.)(?!/)(?!.*//)(?!.*\\)[^\000-\037\177 ~^:?*[]+/?[^\000-\037\177 ~^:?*[]+(?<!\.lock)(?<!/)(?<!\.))(?:\^([0-9]+))?(?:~([0-9]+))?:\s*([^:]+):\s([^\n]+)",
	re.MULTILINE | re.IGNORECASE)

@typechecked
def commity_repo(repo: Optional[str] = None,
					branch: Optional[str] = None,
					output: Optional[str] = None) -> str:
	global log_buffer
	log_buffer = ""
	
	# Create graph for repo
	graph = nx.DiGraph()
	
	# Create graph for branch dependencies
	branch_graph = nx.DiGraph()
	
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
	
	if repo.currently_rebasing_on() is not None:
		log("ERROR: The given repo is being rebased.")
		exit(-3)
	
	if repo.is_dirty():
		log("ERROR: The given repo is dirty.")
		exit(-4)
	
	# Fill graph
	for b in repo.branches:
		for c in repo.iter_commits(rev=b.name):
			if c not in graph:
				graph.add_node(c, branch=None)
			for parent in c.parents:
				if parent not in graph:
					graph.add_node(parent, branch=None)
				if not graph.has_edge(parent, c):
					graph.add_edge(parent, c, weight=c.stats.total["lines"])
	
	dlog("Number of commits: {}", graph.number_of_nodes())
	
	# Draw the graph if in debug mode
	if DEBUG:
		try:
			import matplotlib.pyplot as plt
			from matplotlib.figure import Figure
			fig: Figure = plt.figure()
			nx.draw(
				graph,
				labels={
					c: re.sub(r":[a-zA-Z0-9\-+_]+:\s*",
								'',
								c.summary) for c in graph
				},
				node_size=400,
				font_size=16,
				font_color='r',
				pos=nx.spring_layout(graph,
										k=0.15,
										iterations=20))
			fig.savefig("{}.ignore.png".format(
				os.path.basename(os.path.normpath(repo.working_dir)).replace(' ',
																				'-')))
			plt.close(fig)
		except ImportError:
			pass
	
	# Create the branch graph
	# Source code inspired from https://stackoverflow.com/questions/3161204/how-to-find-the-nearest-parent-of-a-git-branch
	branch_graph.add_nodes_from(list(map(lambda b: b.name, repo.branches)))
	dlog("Branches in graph: {}", branch_graph.nodes)
	get_branch_parent_command = [
		"bash",
		"-c",
		"cd " + os.path.normpath(repo.working_dir) +
		" && git show-branch --no-color | grep '*' | grep -v \"$(git rev-parse --abbrev-ref HEAD)\" | head -n1 | sed 's/.*\\[\\(.*\\)\\].*/\\1/' | sed 's/[\\^~].*//'"
	]
	for b in repo.branches:
		checked_branch = b.checkout()
		if checked_branch.name != b.name:
			log("ERROR: Cannot checkout in the repo \"{}\". Please check that you have the permission to checkout, and that your repo is not clean."
				)
			exit(-5)
		result = subprocess.run(get_branch_parent_command, stdout=subprocess.PIPE)
		result = re.sub(r"\r?\n", '', result.stdout.decode("utf-8").replace('\r', ''))
		if result is not None and result != '':
			if result not in branch_graph.nodes:
				dlog(
					"WARNING: Parent branch \"{}\" is not a valid branch in the given repo. Ignoring this result.\n Available branches: {}",
					result,
					', '.join(branch_graph.nodes))
			else:
				# If a branch is the parent of "master", it means it was merged on master
				if b.name == "master":
					dlog("New branch dependency: {} -> {}", b.name, result)
					branch_graph.add_edge(b.name, result)
				else:
					dlog("New branch dependency: {} -> {}", result, b.name)
					branch_graph.add_edge(result, b.name)
	
	# Checkout on the given branch
	for b in repo.branches:
		if b.name == branch:
			b.checkout()
			break
	
	# Draw the graph if in debug mode
	if DEBUG:
		try:
			import matplotlib.pyplot as plt
			from matplotlib.figure import Figure
			fig: Figure = plt.figure()
			nx.draw(
				branch_graph,
				labels={b: b for b in branch_graph},
				node_size=400,
				font_size=16,
				font_color='r')
			fig.savefig("{}-branches.ignore.png".format(
				os.path.basename(os.path.normpath(repo.working_dir)).replace(' ',
																				'-')))
			plt.close(fig)
		except ImportError:
			pass
	
	# Parse the graph and add the branch of commits as attribute
	# Apply a reverse depth-first search to label the children branches, and then go back to master
	for b in reversed(list(nx.dfs_edges(branch_graph, "master"))):
		b = b[0]
		for c in repo.iter_commits(rev=b):
			graph.nodes[c]["branch"] = b
		# if b.name == "master":
		# 	continue
		# num_iter = 0
		# is_merged_branch = False
		# for c in repo.iter_commits(rev=b.name):
		# 	# Is it a merged branch?
		# 	if num_iter == 0 and graph.nodes[c]["branch"] is not None and graph.nodes[c]["branch"] != '' and graph.nodes[c]["branch"] != b.name:
		# 		# If the first commit of a branch is already tagged, it means this branch has been merged. We need to rewrite the attribute
		# 		is_merged_branch = True
		#
		# 	if (graph.nodes[c]["branch"] is None or graph.nodes[c]["branch"] == '') or (is_merged_branch and len(list(graph.successors(c))) <= 1):
		# 		graph.nodes[c]["branch"] = b.name
		# 	elif is_merged_branch and len(list(graph.successors(c))) > 1:
		# 		# If the source of the merged branch is found, stop here
		# 		break
		# 	num_iter += 1
	
	# for b in repo.branches:
	# 	for c in repo.iter_commits(rev=b.name):
	# 		if graph.nodes[c]["branch"] is None or graph.nodes[c]["branch"] == '':
	# 			branch_name = get_head_name_from_commit(c)
	# 			graph.nodes[c]["branch"] = branch_name
	# 			dlog("Commit \"{}\" is on branch \"{}\"\tname_rev=\"{}\"", c.summary, branch_name, c.name_rev)
	
	# reflogs = []
	# str_reflogs = result.stdout.decode("utf-8").replace('\r', '').split('\n')
	# for str_reflog in str_reflogs:
	# 	matches = list(re.finditer(reflog_pattern, str_reflog))
	# 	if len(matches) != 1:
	# 		dlog("The reflog line:\n{}\n... couldn't be parsed using regex. Number of matches: {}", str_reflog, len(matches))
	# 		continue
	# 	match = matches[0]
	# 	reflogs.append({
	# 		"hash": match.group(1),
	# 		"ref": match.group(2),
	# 		"action": match.group(5),
	# 		"message": match.group(6),
	# 	})
	# # Remove entries that are not related to branches and commits
	# # See https://regex101.com/r/I16vv5/1/
	# reflogs = filter(lambda reflog: not reflog["ref"].startswith("HEAD@{"), reflogs)
	
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
		# If we detect we are not in the same branch anymore (come back to the branch parent), then we stop the loop.
		branch_name = graph.nodes[commit]["branch"]
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
