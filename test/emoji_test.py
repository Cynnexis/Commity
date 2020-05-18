# -*- coding: utf-8 -*-
import unittest

from commitytools.emoji import get_emoji, replace_emoji


class EmojiTest(unittest.TestCase):
	
	def __init__(self, *args, **kwargs):
		super(EmojiTest, self).__init__(*args, **kwargs)
	
	@classmethod
	def setUpClass(cls) -> None:
		print("Loading emoji cache...")
		get_emoji(verbose=False)
	
	def test_get_emoji(self):
		emoji = get_emoji(verbose=False)
		self.assertIsInstance(emoji, list)
		self.assertGreater(len(emoji), 0)
		for emo in emoji:
			self.assertIsInstance(emo, dict)
			assert isinstance(emo["emoji"], str) or emo["emoji"] is None
			if isinstance(emo["emoji"], str):
				self.assertGreater(len(emo["emoji"]), 0)
			
			self.assertIsInstance(emo["image_url"], str)
			self.assertIsInstance(emo["code"], str)
			self.assertFalse(emo["code"].startswith(':'))
			self.assertFalse(emo["code"].endswith(':'))
	
	def test_replace_emoji(self):
		self.assertEqual(
			replace_emoji("This is a test :+1: :trollface: :card_file_box:."),
			"This is a test 👍 :trollface: :card_file_box:.")


if __name__ == '__main__':
	unittest.main()
