from bs4 import BeautifulSoup
import requests
import random

popular_choice = ['motivational', 'life', 'positive', 'friendship', 'success', 'happiness', 'love']

def get_quotes(type, number_of_quotes=1):
    url = "http://www.brainyquote.com/quotes/topics/topic_" + type + ".html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    quotes = []
    for quote in soup.find_all('a', {'title': 'view quote'}):
        quotes.append(quote.contents[0])
    random.shuffle(quotes)
    result = quotes[:number_of_quotes]
    return result

def get_quotes_author(author, number_of_quotes=1):
    url = "https://www.brainyquote.com/quotes/authors/{}/{}.html".format(author[0], author)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    quotes = []
    for quote in soup.find_all('span', {'class': 'bqQuoteLink'}):
        quotes.append(quote.find_all('a')[0].contents[0])
    random.shuffle(quotes)
    result = quotes[:number_of_quotes]
    return result

def get_quotes_keyword(keyword, number_of_quotes=1):
    url = "https://www.brainyquote.com/search_results.html?q={}".format(keyword)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    quotes = []
    for quote in soup.find_all('span', {'class': 'bqQuoteLink'}):
        quotes.append(quote.find_all('a')[0].contents[0])
    random.shuffle(quotes)
    result = quotes[:number_of_quotes]
    return result

def get_random_quote():
    result = get_quotes(popular_choice[random.randint(0, len(popular_choice) - 1)])
    return result

if __name__ == "__main__":
    print(get_quotes('nietzche'))
    print(get_quotes_author('sun_tzu'))
    print(get_quotes_keyword('sun_tzu', 10))
