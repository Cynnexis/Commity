# -*- coding: utf-8 -*-
import sys
from functools import lru_cache
from typing import Dict, Optional, List

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from typeguard import typechecked

from commitytools import plural, size_to_str


@typechecked
@lru_cache(maxsize=2)
def get_emoji(verbose: bool = False) -> List[Dict[str, Optional[str]]]:
	# Else, download the page
	response = requests.get("https://gist.github.com/rxaviers/7360908")
	if response.status_code != 200:
		raise IOError(f"Could not connect to github. Status code: {response.status_code}")
	
	emoji: List[Dict[str, Optional[str]]] = []
	
	soup = BeautifulSoup(response.content, "html.parser")
	gist_article = soup.find("article")
	emoji_tables = gist_article.find_all("table")
	
	emoji_table: Tag
	for emoji_table in emoji_tables:
		thead = emoji_table.find("thead")
		tbody = emoji_table.find("tbody")
		
		tr_th = tbody.find_all("tr") + thead.find_all("th")
		tr: Tag
		for tr in tr_th:
			td: Tag
			for td in tr.find_all("td"):
				emoji_tag = td.find("g-emoji")
				emoji_code_tag = td.find("code")
				
				if emoji_tag is not None:
					emoji_characters = emoji_tag.get_text()
					# Get the image fallback
					emoji_image_url = emoji_tag["fallback-src"]
				else:
					emoji_characters = None
					# Get the image
					emoji_tag = td.find("img", class_="emoji")
					if emoji_tag is not None:
						emoji_image_url = emoji_tag["src"]
					else:
						emoji_image_url = None
				
				if emoji_code_tag is not None:
					emoji_code = emoji_code_tag.get_text()
				else:
					emoji_code = None
				
				if (emoji_characters is not None or emoji_image_url is not None) and emoji_code is not None:
					emoji.append({"emoji": emoji_characters, "image_url": emoji_image_url, "code": emoji_code})
	
	if verbose:
		num_emo = len(emoji)
		num_emo_char = len([True for e in emoji if e['emoji'] is not None])
		num_emo_url = len([True for e in emoji if e['image_url'] is not None])
		num_emo_code = len([True for e in emoji if e['code'] is not None])
		
		print(f"{num_emo} emoji collected.")
		print(f"{num_emo_char}/{num_emo} ({'{:.2%}'.format(num_emo_char/num_emo)}) ha{plural(num_emo_char, 's', 've')} "
				f"a valid emoji character.")
		print(f"{num_emo_url}/{num_emo} ({'{:.2%}'.format(num_emo_url/num_emo)}) ha{plural(num_emo_url, 's', 've')} a "
				f"valid emoji image url.")
		print(f"{num_emo_code}/{num_emo} ({'{:.2%}'.format(num_emo_code/num_emo)}) ha{plural(num_emo_code, 's', 've')} "
				f"a valid emoji code.")
		print("Size: {}".format(size_to_str(sys.getsizeof(emoji))))
	
	return emoji


if __name__ == "__main__":
	get_emoji(verbose=True)
