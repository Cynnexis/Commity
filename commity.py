# -*- coding: utf-8 -*-
import argparse

# Parse the arguments
from commitytools.tools import commity_repo

p = argparse.ArgumentParser(prog="Commity", description="Print commits of a specific branch as a list.")
p.add_argument(
	"-r", "--repo", default=None, help="The repository. If not given, default value is the current directory.")
p.add_argument(
	"-b",
	"--branch",
	default=None,
	help="The branch were to collect the commits. If not given, default value is current branch.")
args = p.parse_args()

commity_repo(repo_path=args.repo, branch=args.branch)
