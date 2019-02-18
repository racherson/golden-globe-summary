import copy
import json
import pdb
import re
import spacy
import sys
import time
from spacy.tokenizer import Tokenizer
# unused import functions
# import string
# from difflib import SequenceMatcher
# from pprint import pprint

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

nlp = spacy.load('en_core_web_sm')
nernlp = spacy.load('en_core_web_sm', disable=['parser', 'tagger'])
tokenizer = Tokenizer(nlp.vocab)
custom_stop_words = [
        'Golden Globes', 'goldenglobes', '@', 'golden globes', 'RT', 'GoldenGlobes', '\n', '#', "#GoldenGlobes", 'gg',
        'Golden Globe.', 'Golden Globe']
key_words = ['best', 'motion', 'picture', 'drama', 'performance', 'actress', 'actor', 'comedy',  'musical',
             'animated', 'feature', 'film', 'foreign', 'language', 'supporting', 'role',
             'director', 'screenplay', 'original', 'score', 'song', 'television', 'series', 'miniseries', 'mini', 'mini-series',
             'cecil', 'demille', 'award', 'tv', 'golden', 'globe', 'hollywood', 'press', 'association']
# can dynamically create key_words from the official awards to improve generalization

def get_first_and_last(hosts, index):
    name = hosts[index]
    split_name = name.split(' ')
    if len(split_name) >= 2:
        return name
    count = 1
    if index < 0:
        limit = len(hosts) + index + 1
    else:
        limit = index + 1
    max_limit = 20 # max number of additional names to check
    while count < min(limit, max_limit):
        next_name = hosts[index-count]
        split_next_name = next_name.split(' ')
        if split_next_name[0] == split_name[0]:
            return next_name
        count += 1
    return name


def find_hosts(unique_hosts, counts):
    hosts = []
    if not unique_hosts:
        return hosts
    first_host = get_first_and_last(unique_hosts, -1) # make sure to find the first and last name of this host
    split_first_host = first_host.split(' ')
    first_host_count = counts[-1]
    hosts.append(first_host)
    # if the second highest is not the same first name and within a percentage, add it too
    count = 1
    limit = 5 # max number of additional potential hosts to check
    similarity_coefficient = 0.6
    while count < min(len(unique_hosts), limit):
        name = get_first_and_last(unique_hosts, -1-count)
        split_name = name.split(' ')
        similarity = counts[-1-count] / first_host_count
        if split_name[0] != split_first_host[0] and similarity > similarity_coefficient:
            hosts.append(name)
            break
        count += 1
    return hosts


def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
        of this function or what it returns.'''
    answer = load_data('answer2013.json')
    # answer = load_data('answer' + str(year) + '.json')
    hosts = answer['hosts']
    return hosts


def find_awards(unique_awards, counts):
    if len(unique_awards) > 26:
        awards = unique_awards[-26:][::-1]
    else:
        awards = unique_awards[::-1]
    return awards


def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    answer = load_data('answer2013.json')
    # answer = load_data('answer' + str(year) + '.json')
    awards = answer['awards']
    return awards


def find_nominees(year, unique_nominees, counts):
    official_awards = get_awards_by_year(year)
    nominees = {}
    # get top 5 nominees
    for award in official_awards:
        award_noms = unique_nominees[award]
        if len(award_noms) == 0:
            nominees[award] = []
        elif len(award_noms) < 5:
            nominees[award] = award_noms[::-1]
        else:
            nominees[award] = award_noms[-5:][::-1]
    return nominees


def get_nominees(year):
    '''Nominees is dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    answer = load_data('answer2013.json')
    # answer = load_data('answer' + str(year) + '.json')
    award_data = answer['award_data']
    nominees = {}
    for award in award_data.keys():
        nominees[award] = award_data[award][0]
    return nominees


def find_winners(year, unique_winners, counts):
    official_awards = get_awards_by_year(year)
    winners = {}
    # get winners
    for award in official_awards:
        award_winners = unique_winners[award]
        if not award_winners:
            winners[award] = None
        else:
            winners[award] = award_winners[-1]
    return winners


def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    answer = load_data('answer2013.json')
    # answer = load_data('answer' + str(year) + '.json')
    award_data = answer['award_data']
    winners = {}
    for award in award_data.keys():
        winners[award] = award_data[award][1]
    return winners


def find_presenters(year, unique_presenters, counts):
    official_awards = get_awards_by_year(year)
    presenters = {}
    # get presenters
    similarity_coefficient = 0.6
    for award in official_awards:
        award_presenters = unique_presenters[award]
        if len(award_presenters) == 0:
            presenters[award] = []
        else:
            first_presenter = award_presenters[-1]
            first_presenter_count = counts[award][-1]
            presenters[award] = [first_presenter]
            count = 1
            limit = 10 # max number of additional potential presenters to check
            while count < min(len(award_presenters), limit):
                presenter = award_presenters[-1-count]
                if counts[award][-1-count] / first_presenter_count > similarity_coefficient:
                    presenters[award].append(presenter)
                count += 1
    return presenters


def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    answer = load_data('answer2013.json')
    # answer = load_data('answer' + str(year) + '.json')
    award_data = answer['award_data']
    presenters = {}
    for award in award_data.keys():
        presenters[award] = award_data[award][2]
    return presenters


def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
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


# load json file as dictionary
# file_name: 'gg20XX.json'
def load_data(file_name):
    data = {}
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data


def extract_text(tweets):
    tweet_text = []
    filtered_tweets = copy.deepcopy(tweets)
    for tweet in filtered_tweets:
        if tweet['text'][0:2].lower() != 'rt':
            tweet_text.append(tweet['text'])
    return tweet_text


# return True if we want to append token
# return False
def token_filter(token):
    return not (token.is_punct or token.is_space or token.is_stop or len(token.text) <= 3 or '@' in token.text or '#' in token.text)


def ent_filter(ent):
    return not (ent.text in custom_stop_words or '@' in ent.text or '#' in ent.text)


def get_awards_by_year(year):
    if year > 2018:
        return OFFICIAL_AWARDS_1819
    return OFFICIAL_AWARDS_1315


def find_award(year, tweet):
    official_awards = get_awards_by_year(year)
    best = 0
    best_match = ""
    temp = 0
    official_tokens = tokenizer.pipe(official_awards)
    for award in official_tokens:
        for award_token in award:
            for tweet_token in tweet:
                if award_token.lower == tweet_token.lower:
                    temp += 1
                    break
                elif award_token.lower == 'television' and tweet_token.lower == 'tv':
                    temp += 1
                    break
                elif award_token.lower == 'picture' and tweet_token.lower == 'film':
                    temp += 1
                    break
        if temp > best:
            best = temp
            best_match = award.text
        temp = 0
    return best_match


# can generalize this function to find names with any number of parts, eg. John Doe = 2, A Great Movie = 3
# then we can use it to find the names of movies as well as people whose names are more than 2 parts
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


def form_answer(year, hosts, awards, nominees, winners, presenters):
    official_awards = get_awards_by_year(year)
    answer = {}
    answer['hosts'] = hosts
    answer['awards'] = awards
    answer['award_data'] = {}
    for award in official_awards:
        answer["award_data"][award] = [nominees[award], winners[award], presenters[award]]
    with open('answer' + str(year) + '.json', 'w') as f:
        json.dump(answer, f)
    print_answer(year, answer)


def print_answer(year, answer):
    official_awards = get_awards_by_year(year)
    print('Hosts:\n')
    print(answer['hosts'])

    print('\nAwards:\n')
    for award in answer['awards']:
        print(award)

    print('\nAward Data:\n')
    for award in official_awards:
        print(award)
        nominees, winner, presenters = answer['award_data'][award]
        print('Nominees: ')
        print(nominees)
        print('Winner: ')
        print(winner)
        print('Presenter(s): ')
        print(presenters)
        print('')


# phrase tree implementation
class WordNode:
    def __init__(self, word):
        self.word = word
        self.children = {}
        self.count = 0


def add_phrase(node, split_phrase):
    if len(split_phrase) == 0:
        node.count += 1
        return
    next_word = split_phrase[0]
    if next_word in node.children.keys():
        add_phrase(node.children[next_word], split_phrase[1:])
    else:
        new_word_node = WordNode(next_word)
        node.children[next_word] = new_word_node
        add_phrase(new_word_node, split_phrase[1:])


def get_phrases(node, prepend_str, award_names):
    if not prepend_str:
        new_prepend_str = node.word
    else:
        new_prepend_str = prepend_str + ' ' + node.word
    if node.count > 0:
        award_names[new_prepend_str] = node.count
    for child in node.children.keys():
        get_phrases(node.children[child], new_prepend_str, award_names)


def find_award_names(award_tree, tweet):
    text = tweet.text
    pattern = r'(?=((?<![A-Za-z])([Bb]est)( [A-Za-z]+)+))'
    matches = re.findall(pattern, text)
    for match in matches:
        split = match[0].split()
        add_phrase(award_tree, split[1:])


def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or what it returns.'''
    pre_ceremony()
    print ('Starting main now...')
    start_time = time.time()

    data = None
    data_year = None
    for year in range(2000, 2020):
        try:
            data = load_data('processed_gg' + str(year) + '.json')
            data_year = year
            print('Using data for ' + str(year))
            break
        except:
            pass
    if not data:
        print('No processed data found, exiting program')
        sys.exit()
    official_awards = get_awards_by_year(year)

    potential_hosts = []
    award_names = {}
    award_tree = WordNode('best')
    noms_split = {}
    winners_split = {}
    presenters_split = {}
    unique_noms = {}
    unique_winners = {}
    unique_presenters = {}
    noms_counts = {}
    winners_counts = {}
    presenters_counts = {}
    possible_presenters = {}
    possible_noms = {}
    possible_winners = {}

    for award in official_awards:
        noms_split[award] = []
        winners_split[award] = []
        presenters_split[award] = []
    noms_split['misc'] = []
    winners_split['misc'] = []
    presenters_split['misc'] = []

    for word in custom_stop_words:
        nlp.vocab[word].is_stop = True

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
            if token == 'best' and not should_flag:
                # award_tweets.append(tweet)
                find_award_names(award_tree, tweet)
                # for ent in tweet.ents:
                #     if len(ent.text) > 4 and ent.text[:4].lower() == 'best':
                #         award_names.append(ent.text.lower())
                # break # just for performance while developing
            if token == 'present':
                # presenter_tweets.append(tweet)
                a = find_award(year, tweet)
                if a != "":
                    presenters_split[a] += find_names(tweet)
                else:
                    presenters_split['misc'] += find_names(tweet)
                # break
            if token == 'win' or token == 'congrats' or token == 'congratulations' and not should_flag:
                # winner_tweets.append(tweet)
                a = find_award(year, tweet)
                if a != "":
                    winners_split[a] += find_names(tweet)
                else:
                    winners_split['misc'] += find_names(tweet)
                # break
            if token == 'nominate' or token == 'nominee':
                # nominee_tweets.append(tweet)
                a = find_award(year, tweet)
                if a != "":
                    noms_split[a] += find_names(tweet)
                else:
                    noms_split['misc'] += find_names(tweet)
                # break
        if n == 0:
            break
        n -= 1

    unique_hosts = sorted(set(potential_hosts), key=potential_hosts.count)
    hosts_counts = [potential_hosts.count(host) for host in unique_hosts]
    # possible_hosts = list(zip(unique_hosts, hosts_counts))

    get_phrases(award_tree, '', award_names)
    unique_award_names = sorted(set(award_names.keys()), key=lambda x: award_names[x])
    awards_counts = [award_names[award_name] for award_name in unique_award_names]
    # possible_award_names = list(zip(unique_award_names, awards_counts))
    # for award in possible_award_names:
    #     print(award)

    for award in official_awards:
        unique_noms[award] = sorted(set(noms_split[award]), key=noms_split[award].count)
        unique_winners[award] = sorted(set(winners_split[award]), key=winners_split[award].count)
        unique_presenters[award] = sorted(set(presenters_split[award]), key=presenters_split[award].count)
        noms_counts[award] = [noms_split[award].count(possible_nom) for possible_nom in unique_noms[award]]
        winners_counts[award] = [winners_split[award].count(possible_winner) for possible_winner in unique_winners[award]]
        presenters_counts[award] = [presenters_split[award].count(possible_pres) for possible_pres in unique_presenters[award]]
        # possible_noms[award] = list(zip(unique_noms[award], noms_counts[award]))
        # possible_winners[award] = list(zip(unique_winners[award], winners_counts[award]))
        # possible_presenters[award] = list(zip(unique_presenters[award], presenters_counts[award]))

    hosts = find_hosts(unique_hosts, hosts_counts)
    awards = find_awards(unique_award_names, awards_counts)
    nominees = find_nominees(data_year, unique_noms, noms_counts)
    winners = find_winners(data_year, unique_winners, winners_counts)
    presenters = find_presenters(data_year, unique_presenters, presenters_counts)

    print ('Calling form_answer...')
    form_answer(data_year, hosts, awards, nominees, winners, presenters)
    end_time = time.time()
    print("Main complete")
    print('Time: ', str(end_time - start_time))
    return


if __name__ == '__main__':
    main()

# seemingly unused functions saved below
#
# def parse_text(tweets):
#     spacy_tweets = tokenizer.pipe(tweets)
#     ner = nernlp.pipe(tweets)
#     return spacy_tweets, ner
#
# # found on https://stackoverflow.com/questions/17388213/find-the-similarity-metric-between-two-strings
# def similar(a, b):
#     return SequenceMatcher(None, a, b).ratio()
#
# def find_award_alt(tweet):
#     best = 0
#     best_match = ""
#     for award in OFFICIAL_AWARDS:
#         for index, token in enumerate(tweet):
#             if token.text == 'best':
#                 if tweet[index] == tweet[-1]:
#                     continue
#                 if 'dress' in tweet[index + 1].text:
#                     continue
#                 text = tweet[index:(index + 4)].text
#                 if similar(award, text) > best:
#                     best = similar(award, text)
#                     best_match = award
#                     break
#             if token.text == 'foreign':
#                 best_match = 'best foreign language film'
#                 break
#         for ent in tweet.ents:
#             if similar(award, ent.text) > best:
#                 best = similar(award, ent.text)
#                 best_match = award
#     if best == 0:
#         return None
#     return best_match
#
# def find_real_names(names_list):
#     ia = IMDb()
#     real_names = {}
#     for name in names_list:
#         if name not in custom_stop_words:
#             if name in real_names:
#                 real_names[name] += 1
#             elif ia.search_person(name) != []:
#                 real_names[name] = 1
#     return real_names
#