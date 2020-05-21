# -*- coding: utf-8 -*-
import re
from typing import List, Optional

# noinspection PyUnresolvedReferences
Pattern = re.Pattern

fix_keywords = frozenset([
	"close",
	"closes",
	"closed",
	"fix",
	"fixes",
	"fixed",
	"resolve",
	"resolves",
	"resolved",
])

issue_pattern: Pattern = re.compile(r"#(\d+)", re.IGNORECASE)
fixed_issue_pattern: Optional[Pattern] = None
separators_pattern: Pattern = re.compile(r"(?:\s+,\s*and|\s+and|\s*,)\s+", re.IGNORECASE)


def init_pattern():
	global fixed_issue_pattern
	
	if fixed_issue_pattern is None:
		fixed_issue_pattern = re.compile("(?:" + '|'.join(fix_keywords) + r")\s+" + issue_pattern.pattern,
											re.IGNORECASE)
	
	return fixed_issue_pattern


def get_issues(content: str, only_fixed: bool = False) -> List[int]:
	"""
	Get all the issues mentioned in the given content. An issue is a strictly positive number  beginning with a '#'
	(sharp sign).
	:param content: The string to parse.
	:param only_fixed: If `True`, only the issues following a synonym of "fix" will be returned. Defaults to `False`.
	:return: Return a list of number issues detected in the content. If an issue has an invalid number, it is ignored.
	If an issue is given with a correct number, but is actually not associated to any issues in the project, it will be
	given, as this function does not connect to the remote. If no issues are detected, an empty list is returned.
	:rtype: List[str]
	"""
	issues = []
	
	def extract_issues(matches: List[str]):
		for match in matches:
			try:
				issue = int(match)
				if issue not in issues:
					issues.append(issue)
			except ValueError:
				pass
	
	if only_fixed:
		init_pattern()
		
		# Try to get the issues after a separator
		parts = re.split(separators_pattern, content)
		found_first_fixed_issue = False
		i = 0
		for i, part in enumerate(parts):
			matches = re.findall(fixed_issue_pattern, part)
			
			# Remove empty elements
			matches = [match.strip() for match in matches if len(match.strip()) > 0]
			
			# If element matched, get all the issues from `part`
			if len(matches) > 0:
				extract_issues(matches)
				
				# If issues has been found, yeah! `i` is the starting point of the list
				if len(issues) > 0:
					found_first_fixed_issue = True
					break
		
		if found_first_fixed_issue and i + 1 < len(parts):
			# `i` is the index in `parts` where the fixed issues start
			for part in parts[(i + 1):]:
				# If the next "part" (after i) contains an issue after the separator, save it!
				matches = re.findall(r"^" + issue_pattern.pattern, part)
				# Remove empty elements
				matches = [match.strip() for match in matches if len(match.strip()) > 0]
				
				if len(matches) > 0:
					extract_issues(matches)
				else:
					# The list is finished.
					break
	else:
		matches = re.findall(issue_pattern, content)
		extract_issues(matches)
	
	return issues
