# -*- coding: utf-8 -*-
import argparse

# Parse the arguments
from commitytools.tools import commity_repo

p = argparse.ArgumentParser(prog="Commity", description="Print commits of a specific branch as a list.")
p.add_argument("-r", "--repo", default=None, help="The repository. If not given, default value is the current directory.")
p.add_argument("-b", "--branch", default=None, help="The branch were to collect the commits. If not given, default value is current branch.")
p.add_argument("-o", "--output", default=None, help="The output file. All information will be written in the given file. If the file is invalid, or no file is given, stdout is used instead.")
args = p.parse_args()

commity_repo(repo=args.repo, branch=args.branch, output=args.output)
