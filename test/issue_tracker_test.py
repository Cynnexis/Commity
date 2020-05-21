# -*- coding: utf-8 -*-
import unittest

from commitytools.issue_tracker import get_issues


class IssueTrackerTest(unittest.TestCase):
	
	def __init__(self, *args, **kwargs):
		super(IssueTrackerTest, self).__init__(*args, **kwargs)
	
	def test_get_issues(self):
		self.assertEqual(get_issues("Fixed #36"), ["#36"])
		self.assertEqual(get_issues("Fixed #1."), ["#1"])
		self.assertEqual(get_issues("Fixed #-1."), [])
		self.assertEqual(get_issues("Fixed #."), [])
		self.assertEqual(get_issues("Fixed ####."), [])
		self.assertEqual(get_issues("Fixed ##35##."), ["#35"])
		self.assertEqual(get_issues("Fixed # 35."), [])
		self.assertEqual(get_issues("Fixed #45, #25 and #92."), ["#45", "#25", "#92"])
		self.assertEqual(
			get_issues("Fixed #45, user/project#25 and other/idea#92."), ["#45", "user/project#25", "other/idea#92"])
		self.assertEqual(get_issues("Fixed #1, but #1 will stay open just in case the bug re-appears."), ["#1"])


if __name__ == '__main__':
	unittest.main()
