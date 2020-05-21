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
p.add_argument(
	"-i",
	"--issue",
	default=False,
	help="If given, the first line will contain all the issues that have been marked as \"fixed\" in the commits "
	"messages of the given branch.",
	action="store_true")
p.add_argument(
	"-e", "--convert-emoji", default=False, help="Convert GitHub Emoji Markup to actual emoji.", action="store_true")
args = p.parse_args()

commity_repo(repo_path=args.repo, branch=args.branch, fixed_issues=args.issue, convert_emoji=args.convert_emoji)
