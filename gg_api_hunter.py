import sys
import re
import string
import time
import json
import copy
from pprint import pprint
import spacy
from difflib import SequenceMatcher
from imdb import IMDb

nlp = spacy.load('en_core_web_sm')
nernlp = spacy.load('en_core_web_sm', disable=['parser', 'tagger'])
custom_stop_words = [
        'Golden Globes', 'goldenglobes', '@', 'golden globes', 'RT', 'GoldenGlobes', '\n', '#', "#GoldenGlobes", 'gg']
from spacy.tokenizer import Tokenizer
tokenizer = Tokenizer(nlp.vocab)

OFFICIAL_AWARDS = ['cecil b. demille award',
                   'best motion picture - drama',
                   'best performance by an actress in a motion picture - drama',
                   'best performance by an actor in a motion picture - drama',
                   'best motion picture - comedy or musical',
                   'best performance by an actress in a motion picture - comedy or musical',
                   'best performance by an actor in a motion picture - comedy or musical',
                   'best animated feature film', 'best foreign language film',
                   'best performance by an actress in a supporting role in a motion picture',
                   'best performance by an actor in a supporting role in a motion picture',
                   'best director - motion picture', 'best screenplay - motion picture',
                   'best original score - motion picture', 'best original song - motion picture',
                   'best television series - drama', 'best performance by an actress in a television series - drama',
                   'best performance by an actor in a television series - drama',
                   'best television series - comedy or musical',
                   'best performance by an actress in a television series - comedy or musical',
                   'best performance by an actor in a television series - comedy or musical',
                   'best mini-series or motion picture made for television',
                   'best performance by an actress in a mini-series or motion picture made for television',
                   'best performance by an actor in a mini-series or motion picture made for television',
                   'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television',
                   'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

key_words = ['best', 'motion', 'picture', 'drama', 'performance', 'actress', 'actor', 'comedy',  'musical',
             'animated', 'feature', 'film', 'foreign', 'language', 'supporting', 'role',
             'director', 'screenplay', 'original', 'score', 'song', 'television', 'series', 'miniseries', 'mini', 'mini-series',
             'cecil', 'demille']
tweets = {}
awards_tweets = []
presenter_tweets = []
nominee_tweets = []
winner_tweets = []
hosts = []
host_counts = []
awards = []
nominees = {}
winners = {}
presenters = {}
answer = {}


def get_first_and_last(index):
    global host_counts
    index_name = host_counts[index][0].split(' ')
    if len(index_name) >= 2:
        return host_counts[index][0]
    else:
        found_last_name = False
        curr_index = index - 1
        count = 1
        while not found_last_name and count <= 20:
            next_name = host_counts[curr_index][0].split(' ')
            if next_name[0] == index_name[0]:
                # use it
                found_last_name = True
            else:
                # move on to next index
                curr_index -= 1
                count += 1
        if found_last_name:  # if we found a last name in that count range
            return host_counts[curr_index][0]
        else:  # if we did not find a last name in that count range, return the original
            return host_counts[index][0]


def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    global host_counts

    # last element in host_counts has largest count since sorted
    # hosts.append(host_counts[-1][0])

    first_name = host_counts[-1][0].split(' ')[0]
    first_host_count = host_counts[-1][1]
    hosts.append(get_first_and_last(-1))  # make sure to find the first and last name of this host

    # if the second highest is not the same first name and within a percentage, add it too
    index = -2
    percent_and_similar = True
    while percent_and_similar:
        first_and_last = host_counts[index][0].split(' ')
        percent = (host_counts[index][1] / first_host_count)
        if percent < 0.6:
            break
        if first_and_last[0] != first_name and percent > 0.6:
            # hosts.append(host_counts[index][0])
            hosts.append(get_first_and_last(index))
            percent_and_similar = False
        else:
            index -= 1
    # print(hosts)
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
    global OFFICIAL_AWARDS
    for award in OFFICIAL_AWARDS:
        nominees[award] = [None]
        pass
    return nominees


def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    global OFFICIAL_AWARDS
    awards_split = {}
    for award in OFFICIAL_AWARDS:
        awards_split[award] = []
    awards_split['misc'] = []
    for tweet in awards_tweets:
        a = find_award(tweet)
        if a:
            awards_split[a].append(tweet)
        else:
            awards_split['misc'].append(tweet)
    pprint(awards_split)
    return winners


def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    global OFFICIAL_AWARDS
    for award in OFFICIAL_AWARDS:
        pass
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
    tweets_2013 = load_data('gg2013.json')
    pprint(tweets_2013[1])
    tweets_2013 = extract_text(tweets_2013)
    tweets[2013] = tweets_2013
    with open('processed_gg2013.json', 'w') as f:
        json.dump(tweets_2013, f)
    # gen, ner = parse_text(tweets_2013)
    # for doc in ner:
    #     for ent in doc.ents:
    #         if (ent.text not in custom_stop_words) and (ent.text not in names) and 'http' not in ent.text and 'RT' not
    #  in ent.text and '@' not in ent.text and '#' not in ent.text:
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
    return


def form_answer():
    global OFFICIAL_AWARDS
    answer["hosts"] = hosts
    answer["award_data"] = {}
    for award in OFFICIAL_AWARDS:
        answer["award_data"][award] = [nominees[award], presenters[award], winners[award]]
    with open('answer2013.json', 'w') as f:
        json.dump(answer, f)


# load json file as dictionary
# file_name: 'gg2013.json'
def load_data(file_name):
    tweets = {}
    with open(file_name,'r') as f:
        tweets = json.load(f)
    return tweets


# found on https://stackoverflow.com/questions/17388213/find-the-similarity-metric-between-two-strings
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


# return True if we want to append token
# return False
def token_filter(token):
    return not (token.is_punct or token.is_space or token.is_stop or len(token.text) <= 3 or '@' in token.text or '#' in token.text)


def ent_filter(ent):
    return not (ent.text in custom_stop_words or '@' in ent.text or '#' in ent.text)


def extract_text(tweets):
    tweet_text = []
    filtered_tweets = copy.deepcopy(tweets)
    for tweet in filtered_tweets:
        if tweet['text'][0:2].lower() != 'rt':
            tweet_text.append(tweet['text'])
    return tweet_text


def parse_text(tweets):
    spacy_tweets = tokenizer.pipe(tweets)
    ner = nernlp.pipe(tweets)
    return spacy_tweets, ner


def find_award(tweet):
    global OFFICIAL_AWARDS
    best = 0
    best_match = ""

    # for award in OFFICIAL_AWARDS:
    #     for index, token in enumerate(tweet):
    #         if token.text == 'best':
    #             if tweet[index] == tweet[-1]:
    #                 continue
    #             if 'dress' in tweet[index + 1].text:
    #                 continue
    #             text = tweet[index:(index + 4)].text
    #             if similar(award, text) > best:
    #                 best = similar(award, text)
    #                 best_match = award
    #                 break
    #         if token.text == 'foreign':
    #             best_match = 'best foreign language film'
    #             break
        # for ent in tweet.ents:
        #     if similar(award, ent.text) > best:
        #         best = similar(award, ent.text)
        #         best_match = award
    if best == 0:
        return None
    return best_match


def find_names(tweet):
    text = tweet.text
    names = []
    pattern = r'(?=((?<![A-Za-z.])[A-Z][a-z.]*[\s-][A-Z][a-z.]*))'
    names = re.findall(pattern, text)
    for name in names:
        if name in custom_stop_words:
            names.remove(name)
    return names


def find_real_names(names_list):
    ia = IMDb()
    real_names = {}
    for name in names_list:
        if name not in custom_stop_words:
            if name in real_names:
                real_names[name] += 1
            elif ia.search_person(name) != []:
                real_names[name] = 1
    return real_names

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    global tweets
    global host_counts
    global awards
    global awards_tweets
    global key_words
    potential_hosts = []
    potential_presenters = {}
    potential_awards = []
    awards_split = {}
    award_entities = {}
    for award in OFFICIAL_AWARDS:
        awards_split[award] = []
    awards_split['misc'] = []

    for w in custom_stop_words:
        nlp.vocab[w].is_stop = True
    pre_ceremony()

    # tweets_2013, ner = parse_text(tweets[2013])
    start_time = time.time()
    data = load_data('processed_gg2013.json')
    tweets[2013] = nernlp.pipe(data, batch_size = 50, n_threads = 3)
    n = 100000  # limit number of tweets we search
    for tweet in tweets[2013]:
        tokens = []
        next_flag = False
        should_flag = False
        for token in tweet:
            t = token.text.lower()
            if t == 'next':  # ignore tweets about next year
                next_flag = True
            if t == 'should':  # ignore opinion tweets
                should_flag = True
                continue
            if not token_filter(token):
                continue
            tokens.append(token.lemma_.lower())
        for index, token in enumerate(tokens):
            # find hosts
            # if token == 'host' and not (next_flag and should_flag):
            #     for ent in tweet.ents:
            #         if ent_filter(ent):
            #             potential_hosts.append(ent.text.lower())
                # pprint(tweet)
            # awards checking
            if token == 'best':
                awards_tweets.append(tweet)
                # a = find_award(tweet)
                # if a:
                #     awards_split[a].append(tweet)
                # else:
                #     awards_split['misc'].append(tweet)
                break  # just for performance while developing
            if token == 'present':
                presenter_tweets.append(tweet)
                break
            if token == 'win' or token == 'congrats' or token == 'congratulations':
                winner_tweets.append(tweet)
                break
            if token == 'nominate' or token == 'nominee':
                nominee_tweets.append(tweet)
                break

        if n == 0:
            break
        n -= 1

    unique_hosts = sorted(set(potential_hosts), key=potential_hosts.count)
    counts = [potential_hosts.count(host) for host in unique_hosts]
    host_counts = list(zip(unique_hosts, counts))
    # pprint(host_counts)  # print our sorted list of potential hosts + mentions
    # hosts = get_hosts(2013)
    # print(hosts)
    # for award_tweet in awards_tweets:
    #   pprint(award_tweet.text)
    award_names = []
    for award_tweet in awards_tweets:
        # pprint(award_tweet.text)
        # for token in award_tweet:
        #     pprint(token.pos_)
        for ent in award_tweet.ents:
            if len(ent.text) > 4 and ent.text[:4].lower() == 'best':
                award_names.append(ent.text.lower())
                # pprint(ent.text)
    unique_award_names = sorted(set(award_names), key=award_names.count)
    award_counts = [award_names.count(award_name) for award_name in unique_award_names]
    pprint(list(zip(unique_award_names, award_counts)))
    # get_awards(2013)
    # pprint(awards_split)
    possible_winners = []
    possible_noms = []
    possible_presenters = []
    for tweet in winner_tweets:
        possible_winners += find_names(tweet)
    for tweet in nominee_tweets:
        possible_noms += find_names(tweet)
    for tweet in presenter_tweets:
        possible_presenters += find_names(tweet)
    # possible_presenters = find_real_names(possible_presenters)
    # possible_noms = find_real_names(possible_noms)
    # possible_winners = find_real_names(possible_winners)
    pprint(possible_presenters)
    pprint(possible_noms)
    pprint(possible_winners)
    # get_winner(2013)
    end_time = time.time()
    print('Time', str(end_time - start_time))
    print("Pre-ceremony processing complete.")
    return


if __name__ == '__main__':
    main()
