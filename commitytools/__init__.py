# -*- coding: utf-8 -*-
import collections
from typing import Union

from typeguard import typechecked


@typechecked
def plural(number: Union[int, collections.abc.Iterable], singular: str = '', plural: str = ''):
	if hasattr(number, "__len__"):
		# noinspection PyTypeChecker
		number = len(number)
	
	if number <= 0 or number >= 2:
		return plural
	else:
		return singular


def size_to_str(size: Union[int, float, str], decimal_places: int = 2) -> str:
	"""
	Transform the given size (in bytes) to a human-readable version of it. For instance,
	`size_to_str(1024) = "1kB"`.
	Source code inspired from https://stackoverflow.com/a/43690506/7347145
	:param size: The size in bytes to convert to string.
	:param decimal_places: The number of decimal behind. Default is 2.
	:return: Return a human-readable size.
	"""
	if isinstance(size, str):
		size = float(size)
	for unit in ['B', 'kB', 'MB', 'GB', 'TB']:
		if size < 1024.0:
			break
		size /= 1024.0
	return f"{size:.{decimal_places}f}{unit}"
