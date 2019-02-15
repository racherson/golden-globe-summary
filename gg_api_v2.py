import copy
import json
import pdb
import re
import spacy
import string
import sys
import time
from difflib import SequenceMatcher
from pprint import pprint
from spacy.tokenizer import Tokenizer
# from imdb import IMDb

nlp = spacy.load('en_core_web_sm')
nernlp = spacy.load('en_core_web_sm', disable=['parser', 'tagger'])
custom_stop_words = [
        'Golden Globes', 'goldenglobes', '@', 'golden globes', 'RT', 'GoldenGlobes', '\n', '#', "#GoldenGlobes", 'gg',
        'Golden Globe.', 'Golden Globe']
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
             'cecil', 'demille', 'award', 'tv', 'golden', 'globe', 'hollywood', 'press', 'association']

# tweets = {}
# awards_tweets = []
# presenter_tweets = []
# nominee_tweets = []
# winner_tweets = []
# hosts = []
# host_counts = []
# awards = []
# nominees = {}
# winners = {}
#
# presenters = {}
# answer = {}
# unique_winners = {}
# unique_noms = {}
# unique_presenters = {}
# possible_winners = {}
# possible_noms = {}
# possible_presenters = {}
# unique_award_names = []

def get_first_and_last(host_counts, index):
    # global host_counts
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
    sp_data = load_data('superprocessed_gg' + str(year) + '.json')
    host_counts = sp_data['host_counts']
    hosts = []
    # global host_counts
    # last element in host_counts has largest count since sorted
    first_name = host_counts[-1][0].split(' ')[0]
    first_host_count = host_counts[-1][1]
    hosts.append(get_first_and_last(host_counts, -1))  # make sure to find the first and last name of this host

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
            hosts.append(get_first_and_last(host_counts, index))
            percent_and_similar = False
        else:
            index -= 1

    return hosts


def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    sp_data = load_data('superprocessed_gg' + str(year) + '.json')
    unique_award_names = sp_data['unique_award_names']
    # global unique_award_names

    # get 26 most common award names
    if len(unique_award_names) > 26:
        awards = unique_award_names[-26:]
    else:
        awards = unique_award_names

    return awards


def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    sp_data = load_data('superprocessed_gg' + str(year) + '.json')
    possible_noms = sp_data['unique_noms']
    nominees = {}
    # global possible_noms

    # initialize value as empty list
    for award in OFFICIAL_AWARDS:
        nominees[award] = []

    # get top 5 nominees
    for award in OFFICIAL_AWARDS:
        curr_noms = possible_noms[award]
        if len(curr_noms) >= 5:
            nominees[award].append(possible_noms[award][-5:])
        elif len(curr_noms) == 0:
            continue
        elif len(curr_noms) < 5:
            nominees[award].append(possible_noms[award])
        # print ('here')
        # print (possible_noms[award])

    return nominees


def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    sp_data = load_data('superprocessed_gg' + str(year) + '.json')
    possible_winners = sp_data['unique_winners']
    winners = {}
    # global possible_winners
    # awards_split = {}
    # for award in OFFICIAL_AWARDS:
    #     awards_split[award] = []
    # awards_split['misc'] = []
    # for tweet in awards_tweets:
    #     a = find_award(tweet)
    #     if a:
    #         awards_split[a].append(tweet)
    #     else:
    #         awards_split['misc'].append(tweet)
    # pprint(awards_split)

    # get top winner
    for award in OFFICIAL_AWARDS:
        curr_winner = possible_winners[award]
        if len(curr_winner) >= 1:
            winners[award] = possible_winners[award][-1]
        else:
            winners[award] = None

    return winners


def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    sp_data = load_data('superprocessed_gg' + str(year) + '.json')
    possible_presenters = sp_data['unique_presenters']
    presenters = {}
    # global possible_presenters

    # initialize empty list
    for award in OFFICIAL_AWARDS:
        presenters[award] = []
    # get most common presenters
    for award in OFFICIAL_AWARDS:
        curr_presenters = possible_presenters[award]
        if len(curr_presenters) >= 1:
            presenters[award].append(possible_presenters[award][-1])

    # for award in OFFICIAL_AWARDS:
    #     nominees[award] = [None]
    #
    # # get top 5 nominees
    # for award in OFFICIAL_AWARDS:
    #     curr_noms = possible_noms[award]
    #     if len(curr_noms) >= 5:
    #         nominees[award].append(possible_noms[award][-5:][0])
    #     elif len(curr_noms) == 0:
    #         continue
    #     elif len(curr_noms) < 5:
    #         nominees[award].append(possible_noms[award][:][0])
    #     # print ('here')
    #     # print (possible_noms[award])

    return presenters


def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print('Starting pre-ceremony now...')
    tweets = {}
    for year in range(2000, 2020):
        try:
            print('Checking for  ' + str(year) + ' data')
            data = load_data('gg' + str(year) + '.json')
            tweets[year] = extract_text(data)
            print('Found ' + str(year) + ' data')
        except:
            print(str(year) + ' data not found')
    for year in tweets.keys():
        with open('processed_gg' + str(year) + '.json', 'w') as f:
            json.dump(tweets[year], f)
    print('Pre-ceremony complete')
    return


def form_answer(year, hosts, awards, winners, nominees, presenters):
    answer = {}
    answer["hosts"] = hosts
    answer["awards"] = awards
    answer["award_data"] = {}
    for award in OFFICIAL_AWARDS:
        answer["award_data"][award] = [nominees[award], presenters[award], winners[award]]
    with open('answer' + str(year) + 'v2.json', 'w') as f:
        json.dump(answer, f)
    print_answer(answer)


def print_answer(answer):
    print('Hosts:\n')
    print(answer['hosts'])

    print('\nAwards:\n')
    print(answer['awards'])

    print('\nAward Data:\n')
    for award in OFFICIAL_AWARDS:
        print(award)
        nominees, presenters, winners = answer['award_data'][award]
        print('Nominees: ')
        print(nominees)
        print('Presenter(s): ')
        print(presenters)
        print('Winner: ')
        print(winners)
        print('')


# load json file as dictionary
# file_name: 'gg2013.json'
def load_data(file_name):
    data = {}
    with open(file_name,'r') as f:
        data = json.load(f)
    return data


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
    best = 0
    best_match = ""
    temp = 0
    official_tokens = tokenizer.pipe(OFFICIAL_AWARDS)
    for award in official_tokens:
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


def find_award_alt(tweet):
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


def find_names(tweet):
    text = tweet.text
    pattern = r'(?=((?<![A-Za-z])[A-Z][a-z]+ [A-Z][a-z]+))'
    matches = re.findall(pattern, text)
    names = []
    for match in matches:
        w1, w2 = match.split(' ')
        if not (match in custom_stop_words or w1.lower() in key_words or w2.lower() in key_words):
            names.append(match)
    return names


def find_real_names(names_list):
    # ia = IMDb()
    real_names = {}
    # for name in names_list:
    #     if name not in custom_stop_words:
    #         if name in real_names:
    #             real_names[name] += 1
    #         elif ia.search_person(name) != []:
    #             real_names[name] = 1
    return real_names


def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    pre_ceremony()
    print ('Starting main now...')
    start_time = time.time()

    potential_hosts = []
    award_tweets = []
    presenters_split = {}
    noms_split = {}
    winners_split = {}
    unique_presenters = {}
    unique_noms = {}
    unique_winners = {}
    presenters_counts = {}
    noms_counts = {}
    winner_counts = {}
    possible_presenters = {}
    possible_noms = {}
    possible_winners = {}

    for award in OFFICIAL_AWARDS:
        presenters_split[award] = []
        noms_split[award] = []
        winners_split[award] = []
    presenters_split['misc'] = []
    noms_split['misc'] = []
    winners_split['misc'] = []

    data = None
    data_year = None
    for year in range(2000, 2020):
        try:
            data = load_data('processed_gg' + str(year) + '.json')
            print('Using data for ' + str(year))
            data_year = year
            break
        except:
            pass
    if not data:
        print('No processed data found, exiting program')
        sys.exit()

    for w in custom_stop_words:
        nlp.vocab[w].is_stop = True

    num_tweets = len(data) # total number of tweets
    n = 200000 # number of tweets to check
    skip = int(num_tweets / n) # number of tweets to skip per selection
    if skip != 0:
        data = data[0::skip] # select n tweets from data
    tweets = nernlp.pipe(data, batch_size=50, n_threads=3)
    for tweet in tweets:
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
            # awards checking
            if token == 'best':
                award_tweets.append(tweet)
                # break # just for performance while developing
            if token == 'present':
                # presenter_tweets.append(tweet)
                a = find_award(tweet)
                if a != "":
                    presenters_split[a] += find_names(tweet)
                else:
                    presenters_split['misc'] += find_names(tweet)
                # break
            if token == 'win' or token == 'congrats' or token == 'congratulations':
                # winner_tweets.append(tweet)
                a = find_award(tweet)
                if a != "":
                    winners_split[a] += find_names(tweet)
                else:
                    winners_split['misc'] += find_names(tweet)
                # break
            if token == 'nominate' or token == 'nominee':
                # nominee_tweets.append(tweet)
                a = find_award(tweet)
                if a != "":
                    noms_split[a] += find_names(tweet)
                else:
                    noms_split['misc'] += find_names(tweet)
                # break
        if n == 0:
            break
        n -= 1

    unique_hosts = sorted(set(potential_hosts), key=potential_hosts.count)
    counts = [potential_hosts.count(host) for host in unique_hosts]
    host_counts = list(zip(unique_hosts, counts))
    # pprint(host_counts)  # print our sorted list of potential hosts + mentions
    # hosts = get_hosts(2013)
    # print(hosts)
    # for award_tweet in award_tweets:
    #   pprint(award_tweet.text)
    award_names = []
    for award_tweet in award_tweets:
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
    # pdb.set_trace()

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
        possible_presenters[award] = list(zip(unique_presenters[award], presenters_counts[award]))

    with open('superprocessed_gg' + str(data_year) + '.json', 'w') as f:
        sp_data = {}
        sp_data['host_counts'] = host_counts
        sp_data['unique_award_names'] = unique_award_names
        sp_data['unique_presenters'] = unique_presenters
        sp_data['unique_noms'] = unique_noms
        sp_data['unique_winners'] = unique_winners
        json.dump(sp_data, f)

    # # METHOD FOR SERIALIZING SPACY DOC OBJECTS
    # serializable_data = []
    # for tweet in data:
    #     serializable_data.append(tweet.to_bytes())
    # recovered_data = []
    # for tweet in serializable_data:
    #     recovered_data.append(nlp('').from_bytes(tweet))
    # tweets = recovered_data

    # possible_presenters = find_real_names(possible_presenters)
    # possible_noms = find_real_names(possible_noms)
    # possible_winners = find_real_names(possible_winners)
    # pprint(possible_presenters)
    # pprint(possible_noms)
    # pprint(possible_winners)
    # pdb.set_trace()
    hosts = get_hosts(data_year)
    awards = get_awards(data_year)
    winners = get_winner(data_year)
    nominees = get_nominees(data_year)
    presenters = get_presenters(data_year)
    print ('Calling form_answer...')
    form_answer(data_year, hosts, awards, winners, nominees, presenters)
    end_time = time.time()
    print("Main complete")
    print('Time', str(end_time - start_time))
    return


if __name__ == '__main__':
    main()
