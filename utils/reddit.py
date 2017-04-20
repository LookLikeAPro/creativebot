import requests
import sys

def get_text_reddit(username):
	r = requests.get('https://www.reddit.com/user/{}/comments.json?limit=100'.format(username))
	if sys.version_info >= (3, 0):
		comments = list(map(lambda c: c["data"]["body"], r.json()["data"]["children"]))
	else:
		comments = map(lambda c: c["data"]["body"], r.json()["data"]["children"])
	text = "\n\n".join(comments)
	return text
