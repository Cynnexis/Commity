# -*- coding: utf-8 -*-
import os
import re
import unittest
from typing import List, Union

from commitytools.tools import commity_repo


class CommityTest(unittest.TestCase):
	
	def __init__(self, *args, **kwargs):
		super(CommityTest, self).__init__(*args, **kwargs)
		self.test_repo_dir = os.getenv("TEST_REPO", "/git-test-repo")
	
	def test_repo(self):
		print("Does {} exists?".format(self.test_repo_dir))
		self.assertTrue(os.path.exists(self.test_repo_dir))
	
	def test_master(self):
		self.check_lines("master", [
			"* :twisted_rightwards_arrows: Merge branch 'acknowledgements' onto master",
			"* :see_no_evil: Add .gitignore", "* :sparkles: Add Acknowledgements.txt", "* :pencil: Update README"
		])
	
	def test_getting_started(self):
		self.check_lines("getting-started", [
			"* :pencil: Add more content in Getting Started", "* Improved #1.",
			"* :pencil: Add Getting Started section", "* :pencil: Add description", "* Started #1.",
			"* :tada: First commit"
		])
	
	def test_license(self):
		self.check_lines("license", ["Fixed #2.", "* :page_facing_up: Add LICENSE", "* Fixed #2."])
	
	def test_lorem(self):
		self.check_lines("lorem", [
			"Fixed #5, #4 and #2.", "* :sparkles: Add lorem again!", "* Fixed #5", "* :sparkles: Add more lorem!",
			"* Fixed #4 and #2.", "* :sparkles: Add lorem", "* :pencil: Update README"
		])
	
	def test_change_first_lorem_paragraph(self):
		self.check_lines("change-first-lorem-paragraph", [
			"Fixed #4 and #2.", "* :pencil: Update first paragraph of lorem text", "* :sparkles: Add more lorem!",
			"* Fixed #4 and #2.", "* :sparkles: Add lorem", "* :pencil: Update README"
		])
	
	def check_lines(self, branch: str, expected_lines: Union[List[str], str], *args: str):
		if isinstance(expected_lines, str):
			expected_lines = [expected_lines]
		
		if len(args) > 0:
			expected_lines.extend(args)
		
		output = commity_repo(self.test_repo_dir, branch)
		lines = re.sub(r"\t+", '', re.sub(r"\n+", '\n', output)).split("\n")
		
		# Remove empty strings
		lines = [line for line in lines if len(line.strip()) > 0]
		
		lines = list(filter(lambda s: len(s) > 0, lines))
		self.assertEqual(
			len(lines), len(expected_lines), "Expected {} lines.\nExpected lines:\n\t{}\nGot lines:\n\t{}".format(
				len(expected_lines), '\n\t'.join(expected_lines), '\n\t'.join(lines)))
		for i, line in enumerate(lines):
			self.assertEqual(line, expected_lines[i], "Expected: \"{}\"\nGot: \"{}\"".format(expected_lines[i], line))


if __name__ == '__main__':
	unittest.main()
