import sys
import re
import string
import nltk
nltk.download('stopwords')
import time
import json
import copy
from pprint import pprint

OFFICIAL_AWARDS = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

hosts = {}
awards = {}
nominees = {}
winners = {}
presenters = {}

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    return hosts


def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    return awards


def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    return nominees


def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    return winners


def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    return presenters


def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print("Pre-ceremony processing complete.")
    return

# load json file as dictionary
# file_name: 'gg2013.json'
def load_data(file_name):
    tweets = {}
    with open(file_name,'r') as f:
        tweets = json.load(f)
    return tweets

# remove nltk English stop words from all tweets
def remove_stop_words(tweets):
    stops = set(nltk.corpus.stopwords.words("english"))
    filtered_tweets = copy.deepcopy(tweets)
    for tweet in filtered_tweets:
        words = tweet['text'].split() # array of word
        lower_words = [word.lower() for word in words]
        tweet['text'] = ' '.join([word for word in lower_words if word not in stops])

    return filtered_tweets

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    print ('Starting...')
    start_time = time.time()

    # save filtered tweets 2013 as 'filtered_2013.json'
    tweets_2013 = load_data('gg2013.json')
    pprint (tweets_2013[1])
    filtered_tweets_2013 = remove_stop_words(tweets_2013)
    with open('filtered_2013.json', 'w') as fp:
        json.dump(filtered_tweets_2013, fp)
    pprint (filtered_tweets_2013[1])

    # save filtered tweets 2015 as 'filtered_2015.json'
    tweets_2015 = load_data('gg2015.json')
    pprint (tweets_2015[1])
    filtered_tweets_2015 = remove_stop_words(tweets_2015)
    with open('filtered_2015.json', 'w') as fp:
        json.dump(filtered_tweets_2015, fp)
    pprint (filtered_tweets_2015[1])

    end_time = time.time()
    print ('Time', str(end_time - start_time))
    print ('Finished!')
    return

if __name__ == '__main__':
    main()
