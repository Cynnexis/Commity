# -*- coding: utf-8 -*-
import os
import re
import subprocess
from typing import Optional, Union, Tuple, Any, Iterable, List
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

branch_parent_pattern = re.compile(r" *\* +(.*)", re.MULTILINE | re.IGNORECASE)

@typechecked
def commity_repo(repo_path: Optional[str] = None,
					branch: Optional[str] = None,
					output: Optional[str] = None) -> str:
	global log_buffer
	log_buffer = ""
	
	# Create graph for repo
	graph = nx.DiGraph()
	
	# Create graph for branch dependencies
	branch_graph = nx.DiGraph()
	
	# If no repo has been given, take the current directory
	if repo_path is None:
		repo_path = os.path.dirname(os.path.realpath(__file__))
	
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
	
	if repo.currently_rebasing_on() is not None:
		log("ERROR: The given repo is being rebased.")
		exit(3)
	
	if repo.is_dirty():
		log("ERROR: The given repo is dirty.")
		exit(4)
	
	if branch not in repo.branches:
		log("ERROR: The branch \"{}\" does not exist.\nAvailable branch: {}".format(
			branch,
			', '.join(repo.branches)),
			output=output)
		exit(5)
	
	# Fill graph
	for b in repo.branches:
		for commit in repo.iter_commits(rev=b.name):
			if commit not in graph:
				graph.add_node(commit, branch=None)
			for parent in commit.parents:
				if parent not in graph:
					graph.add_node(parent, branch=None)
				if not graph.has_edge(parent, commit):
					graph.add_edge(parent, commit, weight=commit.stats.total["lines"])
	
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
				os.path.basename(repo_path).replace(' ',
													'-')))
			plt.close(fig)
		except ImportError:
			pass
	
	# Create the branch graph
	# Source code inspired from https://stackoverflow.com/questions/3161204/how-to-find-the-nearest-parent-of-a-git-branch
	branch_graph.add_nodes_from(
		list(map(lambda b: b.name,
					repo.branches)),
		merged=False)
	dlog("Branches in graph: {}", branch_graph.nodes)
	get_branch_parent_command = [
		"bash",
		"-c",
		"cd " + repo_path +
		" && git show-branch --no-color | grep '*' | grep -v \"$(git rev-parse --abbrev-ref HEAD)\" | head -n1 | sed 's/.*\\[\\(.*\\)\\].*/\\1/' | sed 's/[\\^~].*//'"
	]
	for b in repo.branches:
		checked_branch = b.checkout()
		if checked_branch.name != b.name:
			log("ERROR: Cannot checkout in the repo \"{}\". Please check that you have the permission to checkout, and that your repo is not clean."
				)
			exit(6)
		del checked_branch
		
		# Check if branch is merged by looking at the number of parents of the most recent commit
		
		# If the most recent commit of the given branch is a merge commit (commit with multiple parents), or if the
		# commit right after the most recent commit is a merge commit, then the branch is merged.
		
		could_find_parent = False
		
		# If the branch contains at least one commit and...
		if len(list(repo.iter_commits(rev=b.name))) > 0 and (
			# ... the most recent commit has one successor and...
			(
				len(list(graph.successors(list(repo.iter_commits(rev=b.name))[0]))) == 1
				and
				# ... the successor is a merge commit (has 2 parents or more)
				len(
					list(
						list(graph.successors(list(
							repo.iter_commits(rev=b.name))[0]))[0].parents)) > 1)):
			# then the branch is merged
			dlog("Branch {} is merged.", b.name)
			branch_graph.nodes[b.name]["merged"] = True
			
			result = get_branch_parent_from_merged_branched(repo, b.name)
			if result is not None:
				could_find_parent = True
				dlog("New branch dependency: {} -> {}", b.name, result)
				branch_graph.add_edge(result, b.name)
		
		if not could_find_parent:
			result = subprocess.run(get_branch_parent_command, stdout=subprocess.PIPE)
			result = re.sub(r"\r?\n", '', result.stdout.decode("utf-8").replace('\r', ''))
			if result is not None and result != '':
				if result not in branch_graph.nodes:
					dlog(
						"WARNING: Parent branch \"{}\" is not a valid branch in the given repo. Ignoring this result.",
						result)
				else:
					# If a branch is the parent of "master", it means it was merged on master
					if b.name == "master":
						dlog("New branch dependency: {} -> {}\t(inverted)", b.name, result)
						branch_graph.add_edge(b.name, result)
					else:
						dlog("New branch dependency: {} -> {}", result, b.name)
						branch_graph.add_edge(result, b.name)
	
	# Checkout on the given branch
	checkout_on_branch(repo, branch)
	
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
				os.path.basename(repo_path).replace(' ',
													'-')))
			plt.close(fig)
		except ImportError:
			pass
	
	# Parse the graph and add the branch of commits as attribute
	# Construct reverse-DNF list, that go from leafs to root
	reversed_dnf = []
	dnf_buffer = []
	original_dfs = nx.dfs_edges(branch_graph, "master")
	for edge in original_dfs:
		if len(dnf_buffer) == 0 or (len(dnf_buffer) > 0 and edge[0] != "master"):
			dnf_buffer.append(edge)
		else:
			reversed_dnf.extend(list(reversed(dnf_buffer)))
			dnf_buffer.clear()
			dnf_buffer.append(edge)
	if len(dnf_buffer) > 0:
		reversed_dnf.extend(list(reversed(dnf_buffer)))
	del dnf_buffer
	del original_dfs
	# Select only the second element of all tuples in the list (thus, master will be removed from the list)
	reversed_dnf = list(map(lambda edge: edge[1], reversed_dnf))
	# Add master at the end of the list
	reversed_dnf.append("master")
	
	# Apply a reverse depth-first search to label the children branches, and then go back to master (do not parse master)
	dlog("Parsing {}", reversed_dnf)
	for b in reversed_dnf:
		is_parsing_merged_branch = False
		do_not_fall_back_in_merged_mode = False
		# Construct the list of commits to iterate (take the last parent each time, see https://stackoverflow.com/a/46455760/7347145)
		commits = []
		most_recent_commit = next(repo.iter_commits(rev=b))
		commit = most_recent_commit
		while len(commit.parents) > 0:
			commits.append(commit)
			if len(commit.parents) > 1:
				dlog(
					"WARNING: Ignoring potential commits on current branch \"{}\". Preferring fetching commits in feature branch \"{}\".",
					b,
					graph.nodes[commit.parents[-1]]["branch"])
			commit = commit.parents[
				-1] # TODO, Take the other commits to, with a DFS Traversal Algorithm
		commits.append(commit)
		del most_recent_commit, commit
		
		for commit in commits:
			# If the current commit has the name of a branch that is not `b` and that is tagged as "merged", ignore it and enter in "merge mode"
			if not is_parsing_merged_branch and not do_not_fall_back_in_merged_mode and graph.nodes[
				commit]["branch"] not in [
					None,
					'',
					b
				] and branch_graph.nodes[graph.nodes[commit]["branch"]]["merged"]:
				is_parsing_merged_branch = True
			# Stop considering branch as merged if the current commit is a merge commit and the branch we analyse is merged
			elif is_parsing_merged_branch and len(list(graph.successors(commit))) > 1:
				is_parsing_merged_branch = False
				do_not_fall_back_in_merged_mode = True
			
			if not is_parsing_merged_branch:
				# if DEBUG and graph.nodes[commit]["branch"] is not None and graph.nodes[
				# 	commit]["branch"] != '':
				# 	dlog(
				# 		"WARNING: Overwriting previous commit label:\n\tCommit:    {}\n\tOld label: {}\n\tNew label: {}",
				# 		commit.summary,
				# 		graph.nodes[commit]["branch"],
				# 		b)
				
				graph.nodes[commit]["branch"] = b
	
	# If no branch has been given, take the current branch (it might be `master`)
	if branch is None:
		branch = repo.active_branch.name
	
	dlog("Analysing branch \"{}\"", branch)
	
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
def get_branch_parent_from_merged_branched(repo: git.Repo, branch_name: str) -> Optional[str]:
	"""
	Get the branch parent from `branch_name`. This method works only if the given branch is merged. If not, the function
	will return `None`.
	:param repo: The git repo.
	:param branch_name: The branch name.
	:return: Return the name of the branch parent if the given branch name is merged onto the parent. Otherwise `None`.
	"""
	if not checkout_on_branch(repo, branch_name):
		return None
	
	result: subprocess.CompletedProcess = subprocess.run(
		["bash", "-c", "git branch --contains " + branch_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	
	if result is None or (result.stderr is not None and result.stderr.decode("utf-8").startswith("error: malformed object name ")):
		dlog("WARNING: branch name {} not found in \"git branch --contains ...\"", branch_name)
		return None
	
	matches = list(re.finditer(branch_parent_pattern, result.stdout.decode("utf-8")))
	
	if len(matches) != 1:
		return None
	
	branch_parent: Optional[str] = matches[0].group(1)
	
	# If the branch parent does not exist or is the branch name, then no parent has been detected with this method.
	if branch_parent is None or branch_parent == '' or branch_parent == branch_name:
		return None
	
	dlog("Branch {} is merged on {}", branch_name, branch_parent)
	
	return branch_parent

@typechecked
def checkout_on_branch(repo: git.Repo, branch_name: str) -> bool:
	"""
	Checkout on the given repo into the given branch.
	:param repo: The repo to checkout.
	:param branch_name: The branch.
	:return: Return `True` if the branch has been found, `False` otherwise.
	"""
	# Checkout on the given branch
	for b in repo.branches:
		if b.name == branch_name:
			b.checkout()
			return True
	return False

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
