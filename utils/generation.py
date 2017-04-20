import markovify
# from functools import lru_cache
# import shelve
import atexit
from .reddit import get_text_reddit
from .twitter import get_text_twitter

# local_data = shelve.open("data/text.shelve")
# local_data_source = shelve.open("data/text_source.shelve")

def onexit():
	# local_data.close()
	# local_data_source.close()
	pass

# @lru_cache(maxsize=100)
def _get_model(username):
	# if username in local_data:
	# 	return markovify.Text(local_data[username]), local_data_source[username]
	try:
		t1 = get_text_reddit(username)
	except:
		t1 = ""
	try:
		t2 = get_text_twitter(username)
	except:
		t2 = ""
	source = "reddit"
	if len(t1)>len(t2):
		text = t1
		source = "reddit"
	else:
		text = t2
		source = "twitter"
	if len(text) < 1000:
		return None, "special"
	# local_data[username] = text
	# local_data_source[username] = source
	return markovify.Text(text), source

models = {}
models_order = []
models_count = 0

def get_model(username):
	global models, models_order, models_count
	if username in models:
		return models[username]
	else:
		models_order.insert(0, username)
		models_count += 1
		if models_count > 100:
			temp = models_order.pop()
			del models[temp]
		model, source = _get_model(username)
		models[username] = (model, source)
		return models[username]

def generate(username):
	model, source = get_model(username.lower())
	if source == "twitter":
		return model.make_short_sentence(140), source
	elif source == "reddit":
		return model.make_sentence(), source
	return "Something is not right, try another name", source

atexit.register(onexit)
