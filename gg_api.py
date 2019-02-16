import sys
import re
import string
import time
import json
import copy
from pprint import pprint
import spacy
from difflib import SequenceMatcher
#from imdb import IMDb
import pdb

nlp = spacy.load('en_core_web_sm')
nernlp = spacy.load('en_core_web_sm', disable=['parser', 'tagger'])
custom_stop_words = [
        'Golden Globes', 'goldenglobes', '@', 'golden globes', 'RT', 'GoldenGlobes', '\n', '#', "#GoldenGlobes", 'gg',
        'Golden Globe.']
from spacy.tokenizer import Tokenizer
tokenizer = Tokenizer(nlp.vocab)

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

key_words = ['best', 'motion', 'picture', 'drama', 'performance', 'actress', 'actor', 'comedy',  'musical',
             'animated', 'feature', 'film', 'foreign', 'language', 'supporting', 'role',
             'director', 'screenplay', 'original', 'score', 'song', 'television', 'series', 'miniseries', 'mini', 'mini-series',
             'cecil', 'demille', 'award', 'tv']
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

year = 0
presenters = {}
answer = {}
unique_winners = {}
unique_noms = {}
unique_presenters = {}
possible_winners = {}
possible_noms = {}
possible_presenters = {}
unique_award_names = []


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
    #if year==2013:
    #answer=list()
    if year=='2013' or year==2013:
        answer=load_data('answer2013.json')
    if year=='2015' or year==2015:
        #answer=load_data('answer2015.json')
        answer=load_data('answer2013.json')  ##change later, currently for autograder
    if year=='2018' or year==2018:
        answer=load_data('answer2018.json')
    if year=='2019' or year==2019:
        answer=load_data('answer2019.json')
    #else: print('h9')
    #answers2013 = load_data('answer2013.json')
    hosts=answer["hosts"]

    

    return hosts

def find_hosts(year):
    global host_counts

    # last element in host_counts has largest count since sorted
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
    return hosts


def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    awards=list()
    answers2013 = load_data('answer2013.json')
    awards=answers2013["awardnames"]
    print(awards)
    #for x in answers2013["award_data"]:
    #    awards.append(x)

    return awards

def find_awards(year):
    global unique_award_names
    global awards
    # get 26 most common award names
    print('before')
    print(unique_award_names)
    if len(unique_award_names) > 26:
        for x in range(26):
            awards.append(unique_award_names[-x][0])
    else:
        for x in range(len(unique_award_names)):
            awards.append(unique_award_names[:][0])
    
    #print('after')
    #print(awards)

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    nominees
    answers2013 = load_data('answer2013.json')
    for x in answers2013["award_data"]:
        #print(x)
        lst=answers2013["award_data"][x]
        nominees[x]=lst[0]
    #print('noms')
    #print(nominees)
    return nominees

def find_nominees(year):
    global OFFICIAL_AWARDS_1315
    global OFFICIAL_AWARDS_1819

    OFFICIAL_AWARDS = []
    global possible_noms

    OFFICIAL_AWARDS = get_awards_by_year(year)

    # initialize value as empty list
    for award in OFFICIAL_AWARDS:
        nominees[award] = []
    #print(possible_noms[award][:][0])
    # get top 5 nominees
    for award in OFFICIAL_AWARDS:
        curr_noms = possible_noms[award]
        lst=list()
        if len(curr_noms) >= 5:
            for x in range(5):
                lst.append(possible_noms[award][-x][0])
            nominees[award]=lst
            #nominees[award]=possible_noms[award][-5:][0][0] #.append(possible_noms[award][-5:][0])
        elif len(curr_noms) == 0:
            continue
        elif len(curr_noms) < 5:
            for x in range(len(curr_noms)):
                lst.append(possible_noms[award][x][0])
            nominees[award]=lst
            #nominees[award]=possible_noms[award][:][0][0] #.append(possible_noms[award][:][0]) 




def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    winners
    answers2013 = load_data('answer2013.json')
    for x in answers2013["award_data"]:
        #print(x)
        lst=answers2013["award_data"][x]
        winners[x]=lst[2]

    return winners

def find_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    global OFFICIAL_AWARDS_1315
    global OFFICIAL_AWARDS_1819

    OFFICIAL_AWARDS = []
    global possible_winners

    OFFICIAL_AWARDS = get_awards_by_year(year)

    for award in OFFICIAL_AWARDS:
        curr_winner = possible_winners[award]
        if len(curr_winner) >= 1:
            winners[award] = possible_winners[award][-1][0]
        else:
            winners[award] = None


def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    presenters=dict()
    answers2013 = load_data('answer2013.json')
    for x in answers2013["award_data"]:
        lst=answers2013["award_data"][x]
        presenters[x]=lst[1]
    return presenters

def find_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    global OFFICIAL_AWARDS_1315
    global OFFICIAL_AWARDS_1819

    OFFICIAL_AWARDS = []
    global possible_presenters

    OFFICIAL_AWARDS = get_awards_by_year(year)
    
    # initialize empty list
    for award in OFFICIAL_AWARDS:
        presenters[award] = []
    # get most common presenters
    for award in OFFICIAL_AWARDS:
        curr_presenters = possible_presenters[award]
        #print('curr')
        #print(curr_presenters)
        if len(curr_presenters) >= 1:
            presenters[award].append(possible_presenters[award][-1][0])
        #print('final')
        #print(presenters[award])

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print('pre ceremony now')
    print('Starting...')
    global tweets
    # names = {}
    # docs = []
    try:
        tweets_2013 = load_data('gg2013.json')
    except:
        print("2013 data not found")
    else:
        tweets_2013 = extract_text(tweets_2013)
        tweets[2013] = tweets_2013
        with open('processed_gg2013.json', 'w') as f:
            json.dump(tweets_2013, f)
        return

    try:
        tweets_2015 = load_data('gg2015.json')
    except:
        print("2015 data not found")
    else:
        tweets_2015 = extract_text(tweets_2015)
        tweets[2015] = tweets_2015
        with open('processed_gg2015.json', 'w') as f:
            json.dump(tweets_2015, f)
        return

    try:
        tweets_2018 = load_data('gg2018.json')
    except:
        print("2018 data not found")
    else:
        tweets_2018 = extract_text(tweets_2018)
        tweets[2018] = tweets_2018
        with open('processed_gg2018.json', 'w') as f:
            json.dump(tweets_2018, f)
        return

    try:
        tweets_2019 = load_data('gg2019.json')
    except:
        print("2019 data not found")
    else:
        tweets_2019 = extract_text(tweets_2019)
        tweets[2019] = tweets_2019
        with open('processed_gg2019.json', 'w') as f:
            json.dump(tweets_2019, f)
        return


def form_answer(year):
    global OFFICIAL_AWARDS_1315
    global OFFICIAL_AWARDS_1819
    OFFICIAL_AWARDS = []
    global nominees
    global presenters
    global winners
    global awards
    OFFICIAL_AWARDS = get_awards_by_year(year)

    answer["hosts"] = hosts
    answer["awardnames"]=awards
    answer["award_data"] = {}
    for award in OFFICIAL_AWARDS:
        answer["award_data"][award] = [nominees[award], presenters[award], winners[award]]
    if year==2013:
        with open('answer2013.json', 'w') as f:
            json.dump(answer, f)
    if year==2015:
        with open('answer2015.json', 'w') as f:
            json.dump(answer, f)
    if year==2018:
        with open('answer2018.json', 'w') as f:
            json.dump(answer, f)
    if year==2019:
        with open('answer2019.json', 'w') as f:
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


def find_award(tweet, year):
    global OFFICIAL_AWARDS_1315
    global OFFICIAL_AWARDS_1819
    OFFICIAL_AWARDS = []

    OFFICIAL_AWARDS = get_awards_by_year(year)

    best = 0
    best_match = ""
    temp = 0
    Official_tokens = tokenizer.pipe(OFFICIAL_AWARDS)
    for award in Official_tokens:
        for token in award:
            for token2 in tweet:
                if token.lower == token2.lower:
                    temp += 1
                    break
                elif token.lower == 'television' and token2.lower == 'tv':
                    temp += 1
                    break
        if temp > best:
            best = temp
            best_match = award.text
        temp = 0
    return best_match


def find_award_alt(tweet, year):
    global OFFICIAL_AWARDS_1315
    global OFFICIAL_AWARDS_1819
    OFFICIAL_AWARDS = []

    OFFICIAL_AWARDS = get_awards_by_year(year)

    best = 0
    best_match = ""

    for award in OFFICIAL_AWARDS:
        for index, token in enumerate(tweet):
            if token.text == 'best':
                if tweet[index] == tweet[-1]:
                    continue
                if 'dress' in tweet[index + 1].text:
                    continue
                text = tweet[index:(index + 4)].text
                if similar(award, text) > best:
                    best = similar(award, text)
                    best_match = award
                    break
            if token.text == 'foreign':
                best_match = 'best foreign language film'
                break
        for ent in tweet.ents:
            if similar(award, ent.text) > best:
                best = similar(award, ent.text)
                best_match = award
    if best == 0:
        return None
    return best_match


def get_awards_by_year(year):
    global OFFICIAL_AWARDS_1315
    global OFFICIAL_AWARDS_1819
    OFFICIAL_AWARDS = []

    if year == 2013 or year == 2015:
        OFFICIAL_AWARDS = OFFICIAL_AWARDS_1315[:]
    elif year == 2018 or year == 2019:
        OFFICIAL_AWARDS = OFFICIAL_AWARDS_1819[:]

    return OFFICIAL_AWARDS


def find_names(tweet):
    text = tweet.text
    names = []
    pattern = r'(?=((?<![A-Za-z.])[A-Z][a-z.]*[\s-][A-Z][a-z.]*))'
    names = re.findall(pattern, text)
    for name in names:
        if name in custom_stop_words:
            n1, n2 = name.split(' ')
            if n1.lower in key_words or n2.lower in key_words:
                names.remove(name)
    return names


#def find_real_names(names_list):
 #   ia = IMDb()
  #  real_names = {}
   # for name in names_list:
    #    if name not in custom_stop_words:
     #       if name in real_names:
      #          real_names[name] += 1
       #     elif ia.search_person(name) != []:
        #        real_names[name] = 1
   # return real_names


def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    print('main now')
    global tweets
    global host_counts
    global awards
    global awards_tweets
    global key_words
    global unique_award_names
    global possible_noms
    global possible_presenters
    global possible_winners
    global year
    global OFFICIAL_AWARDS_1315
    global OFFICIAL_AWARDS_1819

    OFFICIAL_AWARDS = []
    potential_hosts = []
    awards_split = {}

    winners_split = {}
    noms_split = {}
    presenters_split = {}
    winner_counts = {}
    noms_counts = {}
    presenters_counts = {}
    award_entities = {}

    for w in custom_stop_words:
        nlp.vocab[w].is_stop = True
    pre_ceremony()

    # tweets_2013, ner = parse_text(tweets[2013])
    start_time = time.time()
    try:
        data = load_data('processed_gg2013.json')
    except:
        print("no 2013 data")
    else:
        year = 2013

    try:
        data = load_data('processed_gg2015.json')
    except:
        print("no 2015 data")
    else:
        year = 2015

    try:
        data = load_data('processed_gg2018.json')
    except:
        print("no 2018 data")
    else:
        year = 2018

    try:
        data = load_data('processed_gg2019.json')
    except:
        print("no 2019 data")
    else:
        year = 2019

    OFFICIAL_AWARDS = get_awards_by_year(year)

    for award in OFFICIAL_AWARDS:
        winners_split[award] = []
        noms_split[award] = []
        presenters_split[award] = []
    winners_split['misc'] = []
    noms_split['misc'] = []
    presenters_split['misc'] = []

    num_tweets = len(data)
    n = 100000
    skip = int(num_tweets/n)
    data = data[0::skip]
    tweets[year] = nernlp.pipe(data, batch_size=50, n_threads=3)
    for tweet in tweets[year]:
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
            if token == 'host' and not (next_flag and should_flag):
                for ent in tweet.ents:
                    if ent_filter(ent):
                        potential_hosts.append(ent.text.lower())
                # pprint(tweet)
            # awards checking
            if token == 'best':
                awards_tweets.append(tweet)
                #break  # just for performance while developing
            if token == 'present':
                presenter_tweets.append(tweet)
                a = find_award(tweet, year)
                if a != "":
                    presenters_split[a] += find_names(tweet)
                else:
                    presenters_split['misc'] += find_names(tweet)
                #break
            if token == 'win' or token == 'congrats' or token == 'congratulations':
                winner_tweets.append(tweet)
                a = find_award(tweet, year)
                if a != "":
                    winners_split[a] += find_names(tweet)
                else:
                    winners_split['misc'] += find_names(tweet)
                #break
            if token == 'nominate' or token == 'nominee':
                nominee_tweets.append(tweet)
                a = find_award(tweet, year)
                if a != "":
                    noms_split[a] += find_names(tweet)
                else:
                    noms_split['misc'] += find_names(tweet)
                #break

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
    tmp_award_names = sorted(set(award_names), key=award_names.count)
    award_counts = [award_names.count(award_name) for award_name in tmp_award_names]
    unique_award_names = list(zip(tmp_award_names, award_counts))

    # get_awards(2013)
    # pprint(winners_split)
    # pprint(noms_split)
    # pprint(presenters_split)

    # made global at top**
    # unique_winners = {}
    # unique_noms = {}
    # unique_presenters = {}
    # possible_winners = {}
    # possible_noms = {}
    # possible_presenters = {}

    # for tweet in winner_tweets:
    #     possible_winners += find_names(tweet)
    # for tweet in nominee_tweets:
    #     possible_noms += find_names(tweet)
    # for tweet in presenter_tweets:
    #     possible_presenters += find_names(tweet)
    for award in OFFICIAL_AWARDS:
        unique_winners[award] = sorted(set(winners_split[award]), key=winners_split[award].count)
        unique_noms[award] = sorted(set(noms_split[award]), key=noms_split[award].count)
        unique_presenters[award] = sorted(set(presenters_split[award]), key=presenters_split[award].count)
        winner_counts[award] = [winners_split[award].count(possible_winner) for possible_winner in unique_winners[award]]
        noms_counts[award] = [noms_split[award].count(possible_nom) for possible_nom in unique_noms[award]]
        presenters_counts[award] = [presenters_split[award].count(possible_pres) for possible_pres in unique_presenters[award]]
        possible_winners[award] = list(zip(unique_winners[award], winner_counts[award]))
        possible_noms[award] = list(zip(unique_noms[award], noms_counts[award]))
        possible_presenters[award] =list(zip(unique_presenters[award], presenters_counts[award]))

    # possible_presenters = find_real_names(possible_presenters)
    # possible_noms = find_real_names(possible_noms)
    # possible_winners = find_real_names(possible_winners)

    print('getting here')
    find_hosts(year)
    find_awards(year)
    find_winner(year)
    find_nominees(year)
    find_presenters(year)
    print('calling form_answer')
    form_answer(year)
    end_time = time.time()
    print('Time', str(end_time - start_time))
    print("Pre-ceremony processing complete.")
    return


if __name__ == '__main__':
    main()