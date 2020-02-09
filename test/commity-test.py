# -*- coding: utf-8 -*-
import os
import unittest

from commitytools.tools import commity_repo

class CommityTest(unittest.TestCase):
	
	def __init__(self, *args, **kwargs):
		super(CommityTest, self).__init__(*args, **kwargs)
		self.test_repo_dir = os.getenv("TEST_REPO", "~/git-test-repo")
	
	def test_repo(self):
		print("Does {} exists?".format(self.test_repo_dir))
		self.assertTrue(os.path.exists(self.test_repo_dir))
	
	def test_getting_started(self):
		output = commity_repo(self.test_repo_dir, "getting-started")
		lines = output.split("\n\n")
		# Remove first line which is just the description
		del lines[0]
		# Remove empty lines
		lines = list(filter(lambda s: len(s) > 0, lines))
		
		self.assertEqual(len(lines), 2, "Expected 2 lines.\nLines: {}".format(lines))
		self.assertEqual(lines[0],
							"* :pencil: Add more content in Getting Started",
							"Actual value: {}".format(lines[0]))
		self.assertEqual(lines[1],
							"* :pencil: Add Getting Started section",
							"Actual value: {}".format(lines[1]))
	
	def test_license(self):
		output = commity_repo(self.test_repo_dir, "license")
		lines = output.split("\n\n")
		# Remove first and empty lines
		del lines[0]
		lines = list(filter(lambda s: len(s) > 0, lines))
		
		self.assertEqual(len(lines), 1, "Expected 1 line.\nLines: {}".format(lines))
		self.assertEqual(lines[0],
							"* :page_facing_up: Add LICENSE",
							"Actual value: {}".format(lines[0]))
	
	def test_lorem(self):
		output = commity_repo(self.test_repo_dir, "lorem")
		lines = output.split("\n\n")
		# Remove first and empty lines
		del lines[0]
		lines = list(filter(lambda s: len(s) > 0, lines))
		
		self.assertEqual(len(lines), 2, "Expected 2 lines.\nLines: {}".format(lines))
		self.assertEqual(lines[0],
							"* :sparkles: Add more lorem!",
							"Actual value: {}".format(lines[0]))
		self.assertEqual(lines[1],
							"* :sparkles: Add lorem",
							"Actual value: {}".format(lines[1]))

if __name__ == '__main__':
	unittest.main()
