# -*- coding: utf-8 -*-
import os
import unittest

class CommityTest(unittest.TestCase):
	
	def __init__(self, *args, **kwargs):
		super(CommityTest, self).__init__(*args, **kwargs)
		self.test_repo_dir = os.getenv("TEST_REPO", "~/git-test-repo")
	
	def test_repo(self):
		print("Does {} exists?".format(self.test_repo_dir))
		self.assertTrue(os.path.exists(self.test_repo_dir))
	
	def test_something(self):
		self.assertEqual(True, True)

if __name__ == '__main__':
	unittest.main()
