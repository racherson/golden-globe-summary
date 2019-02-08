import sys
import re
import string
import time
import json
import copy
from pprint import pprint
import spacy

nlp = spacy.load('en_core_web_sm')
nernlp = spacy.load('en_core_web_sm', disable=['parser', 'tagger'])
custom_stop_words = [
        'Golden Globes', 'goldenglobes', '@', 'golden globes', 'RT', 'GoldenGlobes', '\n', '#', "#GoldenGlobes"
    ]
from spacy.tokenizer import Tokenizer
tokenizer = Tokenizer(nlp.vocab)

OFFICIAL_AWARDS = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

tweets = {}
hosts = []
awards = []
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
    print('Starting...')
    global tweets
    # names = {}
    # docs = []
    start_time = time.time()
    tweets_2013 = load_data('gg2013.json')
    pprint(tweets_2013[1])
    tweets[2013]=tweets_2013
    tweets_2013 = extract_text(tweets_2013)
    with open('processed_gg2013.json', 'w') as f:
        json.dump(tweets_2013, f)
    # gen, ner = parse_text(tweets_2013)
    # for doc in ner:
    #     for ent in doc.ents:
    #         if (ent.text not in custom_stop_words) and (ent.text not in names) and 'http' not in ent.text and 'RT' not in ent.text and '@' not in ent.text and '#' not in ent.text:
    #             names[ent.text] = 1
    #         elif ent.text in names:
    #             names[ent.text] += 1
    # for doc in gen:
    #     # print(doc)
    #     docs.append(doc)
    #     # pass
    # for k, v in list(names.items()):
    #     if v <= 50:
    #         del names[k]
    # print(docs[1])
    # print(names)
    end_time = time.time()
    print('Time', str(end_time - start_time))
    print("Pre-ceremony processing complete.")
    return


# load json file as dictionary
# file_name: 'gg2013.json'
def load_data(file_name):
    tweets = {}
    with open(file_name,'r') as f:
        tweets = json.load(f)
    return tweets


def token_filter(token):
    return not (token.is_punct | token.is_space | token.is_stop | len(token.text) <= 3 | '@' not in token.text)


def extract_text(tweets):
    tweet_text = []
    filtered_tweets = copy.deepcopy(tweets)
    for tweet in filtered_tweets:
         tweet_text.append(tweet['text'])
    return tweet_text


def parse_text(tweets):
    spacy_tweets = []
    spacy_tweets = tokenizer.pipe(tweets)
    ner = nernlp.pipe(tweets)
    return spacy_tweets, ner


def main():
    for w in custom_stop_words:
        nlp.vocab[w].is_stop = True
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    pre_ceremony()
    tweets, ner = parse_text(tweets[2013])
    n = 100000 # limit number of tweets we search
    for tweet in tweets:
        tokens = []
        next_flag = False
        should_flag = False
        for token in tweet:
            t = token.text.lower()
            if t == 'next': # ignore tweets about next year
              	next_flag = True
            if t == 'should': # ignore opinion tweets
                should_flag = True
                continue
            if not token_filter(token):
                continue
            tokens.append(token.lemma_.lower())
        for token in tokens:
            if token == 'host' and not (next_flag and should_flag):
                for ent in tweet.ents:
                    if token_filter(ent, False):
                        hosts.append(ent.text.lower())
                pprint(tweet)
                break # maybe remove?
            # awards checking, maybe use hunter's names collection to try and do awards idk
        if n == 0:
            break
        n -= 1
    return


if __name__ == '__main__':
    main()
