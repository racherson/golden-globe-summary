import json
import spacy
import time
from pprint import pprint

OFFICIAL_AWARDS = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

tweets = None
stop_words = ['rt', 'goldenglobes', 'golden', 'globes']
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
    data = load_data('gg2013.json')
    tweets = []
    for tweet in data:
        if tweet['text'][0:2].lower() != 'rt': # ignoring retweets
            tweets.append(tweet['text']) # do we need the rest of the tweet data?
    # for i in range(len(data)):
    #     data[i] = data[i]['text']

    pprint(len(tweets)) # number of relevant twweets
    # pprint(data[0])
    # pprint(type(data[0]))

    with open('processed_gg2013.json', 'w') as f:
        json.dump(tweets, f)
    print("Pre-ceremony processing complete.")
    return


# check if a token is desirable
def token_filter(token, stop=True):
    if token.text[0] == '@':
        return False
    if token.text[0] == '#':
        return False
    if token.text.lower() in stop_words:
        return False
    if stop and token.is_stop:
        return False
    return True


# load json file as dictionary
# file_name: 'gg2013.json'
def load_data(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data


def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    print ('Starting...')
    start_time = time.time()

    pre_ceremony() # comment out if processed json files are already present

    global tweets # only accessing one year's worth of tweets, not set up to take in year arguments yet
    global stop_words
    global hosts
    global awards
    global presenters
    global nominees
    global winners

    tweets = load_data('processed_gg2013.json')
    nlp = spacy.load('en_core_web_sm', disable=['tagger', 'parser'])
    tweets = nlp.pipe(tweets)
    n = 100000 # limit number of tweets we search, 2015 has 1.7 million
    for tweet in tweets:
        tokens = []
        ignore_flag = False
        for token in tweet:
            t = token.text.lower()
            if t == 'next' or t == 'should': # ignore opinion tweets
                ignore_flag = True
                continue
            if not token_filter(token):
                continue
            tokens.append(token.lemma_.lower())
        for token in tokens:
            if token == 'host' and not ignore_flag:
                for ent in tweet.ents:
                    if token_filter(ent, False):
                        hosts.append(ent.text.lower())
                pprint(tweet)
                break
        if n == 0:
            break
        n -= 1
    # pprint(len(hosts))
    # pprint(hosts)
    unique_hosts = sorted(set(hosts), key=hosts.count)
    counts = [hosts.count(host) for host in unique_hosts]
    pprint(list(zip(unique_hosts, counts))) # print our sorted list of potential hosts + mentions
    # ok results, should not add non-name named ents to hosts and somehow consolidate mentions of first and full names

    end_time = time.time()
    print ('Time', str(end_time - start_time))
    print ('Finished!')
    return


if __name__ == '__main__':
    main()
