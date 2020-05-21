# -*- coding: utf-8 -*-
import re
from typing import List, Optional

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

issue_pattern = re.compile(r"#(\d+)", re.IGNORECASE)
# noinspection PyUnresolvedReferences
fixed_issue_pattern: Optional[re.Pattern] = None


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
	if only_fixed:
		init_pattern()
		matches = re.findall(fixed_issue_pattern, content)
	else:
		matches = re.findall(issue_pattern, content)
	
	for match in matches:
		try:
			issue = int(match)
			if issue not in issues:
				issues.append(issue)
		except ValueError:
			pass
	
	return issues
