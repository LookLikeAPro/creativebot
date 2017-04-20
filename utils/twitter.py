# from functools import lru_cache
import tweepy
from tweepy import OAuthHandler

# @lru_cache()
def _get_api_twitter():
	# App of user @looklikepro
	consumer_key = 'OozDmxIloqX8LfdmYrwFmYipm'
	consumer_secret = 'U1lrqfoLHgdcgKetQPqRFYpchTsVKA3NxH6kBSj4EhV4BSg8CZ'
	access_token = '819677506844299269-5lb9JFNOsnit13nrGsDSNzIFjCjFwPi'
	access_secret = 'YbYEHiAWeB2eS4f1tg3J2LQRNnGJYWDVY208Z1QX9tyc0'
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_secret)
	api = tweepy.API(auth)
	return api

api_instance = None

def get_api_twitter():
	global api_instance
	if api_instance:
		return api_instance
	else:
		t = _get_api_twitter()
		api_instance = t
		return api_instance

def get_text_twitter(username):
	api = get_api_twitter()
	sentences = []
	timeline =  api.user_timeline(username, count=250)
	for status in timeline:
		sentences.append(status.text)
	text = "\n".join(sentences)
	return text
