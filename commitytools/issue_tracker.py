# -*- coding: utf-8 -*-
import re
from typing import List

issue_pattern = re.compile(r"#(\d+)", re.IGNORECASE)


def get_issues(content: str) -> List[int]:
	"""
	Get all the issues mentioned in the given content. An issue is a strictly positive number  beginning with a '#'
	(sharp sign). This does NOT detect the closed/fixed/resolved issues.
	:param content: The string to parse.
	:return: Return a list of number issues detected in the content. If an issue has an invalid number, it is ignored.
	If an issue is given with a correct number, but is actually not associated to any issues in the project, it will be
	given, as this function does not connect to the remote. If no issues are detected, an empty list is returned.
	:rtype: List[str]
	"""
	matches = re.findall(issue_pattern, content)
	issues = []
	for match in matches:
		try:
			issue = int(match)
			if issue not in issues:
				issues.append(issue)
		except ValueError:
			pass
	
	return issues
