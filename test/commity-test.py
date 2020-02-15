# -*- coding: utf-8 -*-
import os
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
		self.check_lines(
			"master",
			[
				"* :twisted_rightwards_arrows: Merge branch 'acknowledgements' onto master",
				"* :see_no_evil: Add .gitignore",
				"* :pencil: Update README",
				"* :twisted_rightwards_arrows: Merge branch 'getting-started' onto master",
				"* :pencil: Add description",
				"* :tada: First commit"
			])
	
	def test_getting_started(self):
		self.check_lines("getting-started",
							[
								"* :pencil: Add more content in Getting Started",
								"* :pencil: Add Getting Started section"
							])
	
	def test_license(self):
		self.check_lines("license", "* :page_facing_up: Add LICENSE")
	
	def test_lorem(self):
		self.check_lines("lorem",
							[
								"* :sparkles: Add lorem again!",
								"* :sparkles: Add more lorem!",
								"* :sparkles: Add lorem"
							])
	
	def test_change_first_lorem_paragraph(self):
		self.check_lines("change-first-lorem-paragraph",
							"* :pencil: Update first paragraph of lorem text")
	
	def check_lines(self, branch: str, expected_lines: Union[List[str], str]):
		if isinstance(expected_lines, str):
			expected_lines = [expected_lines]
		output = commity_repo(self.test_repo_dir, branch)
		lines = output.split("\n\n")
		# Remove first and empty lines
		del lines[0]
		lines = list(filter(lambda s: len(s) > 0, lines))
		self.assertEqual(
			len(lines),
			len(expected_lines),
			"Expected {} lines.\nExpected lines:\n\t{}\nGot lines:\n\t{}".format(
				len(expected_lines),
				'\n\t'.join(expected_lines),
				'\n\t'.join(lines)))
		for i, line in enumerate(lines):
			self.assertEqual(
				line,
				expected_lines[i],
				"Expected: \"{}\"\nGot: \"{}\"".format(expected_lines[i],
														line))

if __name__ == '__main__':
	unittest.main()
