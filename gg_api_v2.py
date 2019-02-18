import copy
import json
import pdb
import re
import spacy
import sys
import time
from spacy.tokenizer import Tokenizer
from difflib import SequenceMatcher

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama',
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
                        'best television series - drama',
                        'best performance by an actress in a television series - drama',
                        'best performance by an actor in a television series - drama',
                        'best television series - comedy or musical',
                        'best performance by an actress in a television series - comedy or musical',
                        'best performance by an actor in a television series - comedy or musical',
                        'best mini-series or motion picture made for television',
                        'best performance by an actress in a mini-series or motion picture made for television',
                        'best performance by an actor in a mini-series or motion picture made for television',
                        'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television',
                        'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy',
                        'best performance by an actress in a motion picture - drama',
                        'best performance by an actor in a motion picture - drama',
                        'best performance by an actress in a motion picture - musical or comedy',
                        'best performance by an actor in a motion picture - musical or comedy',
                        'best performance by an actress in a supporting role in any motion picture',
                        'best performance by an actor in a supporting role in any motion picture',
                        'best director - motion picture', 'best screenplay - motion picture',
                        'best motion picture - animated', 'best motion picture - foreign language',
                        'best original score - motion picture', 'best original song - motion picture',
                        'best television series - drama', 'best television series - musical or comedy',
                        'best television limited series or motion picture made for television',
                        'best performance by an actress in a limited series or a motion picture made for television',
                        'best performance by an actor in a limited series or a motion picture made for television',
                        'best performance by an actress in a television series - drama',
                        'best performance by an actor in a television series - drama',
                        'best performance by an actress in a television series - musical or comedy',
                        'best performance by an actor in a television series - musical or comedy',
                        'best performance by an actress in a supporting role in a series, limited series or motion picture made for television',
                        'best performance by an actor in a supporting role in a series, limited series or motion picture made for television',
                        'cecil b. demille award']

nlp = spacy.load('en_core_web_sm')
nernlp = spacy.load('en_core_web_sm', disable=['parser', 'tagger'])
tokenizer = Tokenizer(nlp.vocab)
custom_stop_words = [
    'Golden Globes', 'goldenglobes', '@', 'golden globes', 'RT', 'GoldenGlobes', '\n', '#', "#GoldenGlobes", 'gg',
    'Golden Globe.', 'Golden Globe']

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
    max_limit = 20  # max number of additional names to check
    while count < min(limit, max_limit):
        next_name = hosts[index - count]
        split_next_name = next_name.split(' ')
        if split_next_name[0] == split_name[0]:
            return next_name
        count += 1
    return name


def find_dressed(dressed, tweet, key_words):
    posdress = dressed['best']
    negdress = dressed['worst']
    # dressed = {}
    names = find_names(tweet, key_words)
    if len(names) > 0:
        for token in tweet:
            word = token.text.lower()
            # print(word)
            if word == 'ugly' or word == 'ew' or word == 'bad' or word == 'not' or word == 'worst':
                for pers in names:
                    negdress.append(pers)
                break
            if word == 'beauty' or word == 'pretty' or word == 'gorgeous' or word == 'best':
                # print('pos')
                for pers in names:
                    posdress.append(pers)
                break
    dressed['best'] = posdress
    dressed['worst'] = negdress
    return dressed


def find_hosts(unique_hosts, counts):
    hosts = []
    if not unique_hosts:
        return hosts
    first_host = get_first_and_last(unique_hosts, -1)  # make sure to find the first and last name
    split_first_host = first_host.split(' ')
    first_host_count = counts[-1]
    hosts.append(first_host)
    # if the second highest name doesn't have the same first name and is within a percentage, add it too
    count = 1
    limit = 5  # max number of additional potential hosts to check
    similarity_coefficient = 0.6
    while count < min(len(unique_hosts), limit):
        name = get_first_and_last(unique_hosts, -1 - count)
        split_name = name.split(' ')
        similarity = counts[-1 - count] / first_host_count
        if split_name[0] != split_first_host[0] and similarity > similarity_coefficient:
            hosts.append(name)
            break
        count += 1
    return hosts


def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
        of this function or what it returns.'''
    # answer = load_data('answer2013.json')
    answer = load_data('answer' + str(year) + '.json')
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
    # answer = load_data('answer2013.json')
    answer = load_data('answer' + str(year) + '.json')
    awards = answer['awards']
    return awards


def find_nominees(year, unique_nominees, counts, winners):
    official_awards = get_awards_by_year(year)
    nominees = {}
    print('start')
    # print(counts)
    # print(unique_nominees)
    print('end')

    for award in official_awards:
        lst = list()
        mentions = counts[award]
        award_noms = unique_nominees[award]
        if len(mentions) > 1:
            if (mentions[-1] / 2) >= mentions[-2]:  # and mentions[-1] > 4:
                cutoff = mentions[-2] / 2
            else:
                cutoff = mentions[-1] / 2
            # if cutoff <= 1:
            #     cutoff = 2
            print(award)
            print('cutoff')
            print(cutoff)
            for i in range(1, len(mentions)):
                simflag = False
                if mentions[-i] >= cutoff:
                    # print('hi')
                    curr = award_noms[-i]
                    split_name = curr.split(' ')
                    if not award_noms[-i] == winners[award]:
                        for x in lst:
                            if SequenceMatcher(None, x, curr).ratio() >= 0.8:
                                simflag = True
                            xsplit = x.split(' ')
                            for word in xsplit:
                                for newword in split_name:
                                    if SequenceMatcher(None, newword, word).ratio() >= 0.85:
                                        simflag = True
                        if simflag == False:
                            lst.append(award_noms[-i])
                else:
                    break
        else:
            if award_noms:
                lst.append(award_noms[-1])
        nominees[award] = lst
    return nominees


def get_nominees(year):
    '''Nominees is dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # answer = load_data('answer2013.json')
    answer = load_data('answer' + str(year) + '.json')
    award_data = answer['award_data']
    nominees = {}
    for award in award_data.keys():
        nominees[award] = award_data[award][0]
    return nominees


def nomfilter(tweet, key_words):
    lst = list()
    for ent in tweet.ents:
        ignoreflag = False
        txt = ent.text
        txt = re.sub(r'[^a-zA-Z ]+', '', txt)
        for x in txt.split(' '):
            if x in custom_stop_words or x.lower() in key_words:
                ignoreflag = True
        if not ignoreflag and not (txt == '' or txt == ' '):
            stri = txt.lower()
            lst.append(stri)
    return lst


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
    # answer = load_data('answer2013.json')
    answer = load_data('answer' + str(year) + '.json')
    award_data = answer['award_data']
    winners = {}
    for award in award_data.keys():
        winners[award] = award_data[award][1]
    return winners


def find_presenters(year, unique_presenters, counts):
    official_awards = get_awards_by_year(year)
    presenters = {}
    # get presenters
    similarity_coefficient = 0.8
    for award in official_awards:
        award_presenters = unique_presenters[award]
        if len(award_presenters) == 0:
            presenters[award] = []
        else:
            first_presenter = award_presenters[-1]
            first_presenter_count = counts[award][-1]
            presenters[award] = [first_presenter]
            count = 1
            limit = 10  # max number of additional potential presenters to check
            while count < min(len(award_presenters), limit):
                presenter = award_presenters[-1 - count]
                if counts[award][-1 - count] / first_presenter_count > similarity_coefficient:
                    presenters[award].append(presenter)
                count += 1
    return presenters


def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # answer = load_data('answer2013.json')
    answer = load_data('answer' + str(year) + '.json')
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
            # print('Checking for  ' + str(year) + ' data')
            data = load_data('gg' + str(year) + '.json')
            tweets[year] = extract_text(data)
            # print('Found ' + str(year) + ' data')
        except:
            pass
            # print(str(year) + ' data not found')
    for year in tweets.keys():
        with open('processed_gg' + str(year) + '.json', 'w') as f:
            json.dump(tweets[year], f)
    print('Pre-ceremony complete')
    return


# load json file as dictionary, eg. 'gg2013.json'
def load_data(file_name):
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


# return True if we want to append token, otherwise False
def token_filter(token):
    return not (token.is_punct or token.is_space or token.is_stop or len(
        token.text) <= 3 or '@' in token.text or '#' in token.text)


# return True if we want to append entity, otherwise False
def ent_filter(ent):
    return not (ent.text in custom_stop_words or '@' in ent.text or '#' in ent.text)


def get_awards_by_year(year):
    if year > 2018:
        return OFFICIAL_AWARDS_1819
    return OFFICIAL_AWARDS_1315


def find_award(year, tweet):
    official_awards = get_awards_by_year(year)
    best = 0
    best_match = ''
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
def find_names(tweet, key_words):
    text = tweet.text
    pattern = r'([A-Z][a-z]+ [A-Z][a-z]+)'
    matches = re.findall(pattern, text)
    names = []
    for match in matches:
        if match in custom_stop_words:
            continue
        split = match.split(' ')
        ignore_flag = False
        for word in split:
            if word.lower() in key_words:
                ignore_flag = True
                break
        if not ignore_flag:
            names.append(match)
    return names


# serializes answer dict for access in get functions
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
    file = open('readableanswer' + str(year) + '.txt', 'w')
    file.write('Hosts: ')
    for name in answer['hosts']:
        file.write(name + '; ')
    file.write('\n\n')
    for award in official_awards:
        file.write('Award: ' + award)
        nominees, winner, presenters = answer['award_data'][award]
        file.write('\nPresenters: ')
        for name in presenters:
            file.write(name + '; ')
        file.write('\nNominees: ')
        for name in nominees:
            file.write(name + '; ')
        file.write('\nWinner: ' + winner + '\n\n')
    file.close()
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


def best_and_worst(year, best_dress, worst_dress):
    file = open('readableanswer' + str(year) + '.txt', 'a')
    file.write('Best Dressed: '  + best_dress + '\n')
    file.write('Worst Dressed: '  + worst_dress + '\n')
    file.close()


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
    next_word = split_phrase[0].lower()
    if nlp.vocab[next_word].is_stop:
        add_phrase(node, split_phrase[1:])
    elif next_word in node.children.keys():
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
    pattern = r'([Bb]est( [A-Za-z]+)+)'
    # aux_pattern = r'(\-( [A-Za-z]+)+)'
    matches = re.findall(pattern, text)
    # aux_matches = re.findall(aux_pattern, text)
    aux_words = []
    # for aux_match in aux_matches:
    #     aux_split = aux_match[0][2:].split(' ')
    #     for word in aux_split:
    #         if word.lower in award_words:
    #             aux_words += aux_split
    #             break
    for match in matches:
        split = match[0].split(' ')[1:] + aux_words
        add_phrase(award_tree, split)


def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or what it returns.'''
    pre_ceremony()
    print('Starting main now...')
    start_time = time.time()

    data = None
    data_year = None
    for year in range(2000, 2020):
        try:
            data = load_data('processed_gg' + str(year) + '.json')
            data_year = year
            # print('Using data for ' + str(year))
            break
        except:
            pass
    if not data:
        print('No processed data found, exiting program')
        sys.exit()
    official_awards = get_awards_by_year(year)
    key_words = set()  # only used in finding nominees, winners, and presenters!
    for award in official_awards:
        split = award.split(' ')
        for word in split:
            if len(word) > 1 and not nlp.vocab[word].is_stop:
                key_words.add(word)

    potential_hosts = []
    award_tree = WordNode('best')
    award_names = {}
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
    bestdress = []
    worstdress = []
    dressed = dict()
    dressed['worst'] = list()
    dressed['best'] = list()
    curraward = 'misc'

    for award in official_awards:
        noms_split[award] = []
        winners_split[award] = []
        presenters_split[award] = []
    noms_split['misc'] = []
    winners_split['misc'] = []
    presenters_split['misc'] = []

    for word in custom_stop_words:
        nlp.vocab[word].is_stop = True

    num_tweets = len(data)  # total number of tweets
    n = 1000  # maximum number of tweets to check
    skip = int(num_tweets / n)  # number of tweets to skip per selection
    if skip != 0:
        data = data[0::skip]  # select n evenly spaced tweets from data
    tweets = nernlp.pipe(data, batch_size=50, n_threads=3)
    # check all tweets in one loop for performance
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
            # find awards
            if token == 'best' and not should_flag:
                # award_tweets.append(tweet)
                find_award_names(award_tree, tweetj)
                # for ent in tweet.ents:
                #     if len(ent.text) > 4 and ent.text[:4].lower() == 'best':
                #         award_names.append(ent.text.lower())
                # break # just for performance while developing
            # find presenters
            if token == 'present':
                # presenter_tweets.append(tweet)
                a = find_award(year, tweet)
                if a != "":
                    curraward = a
                    presenters_split[a] += find_names(tweet, key_words)
                else:
                    presenters_split['misc'] += find_names(tweet, key_words)
                # break
            # find winners
            if token == 'win' or token == 'congrats' or token == 'congratulations' and not should_flag:
                # winner_tweets.append(tweet)
                a = find_award(year, tweet)
                if should_flag:
                    if a != '':
                        curraward = a
                        noms_split[a] += nomfilter(tweet, key_words)
                    else:
                        noms_split[curraward] += nomfilter(tweet, key_words)
                else:
                    if a != '':
                        curraward = a
                        winners_split[a] += find_names(tweet, key_words)
                    else:
                        winners_split['misc'] += find_names(tweet, key_words)
                # break
            # find nominees
            if token == 'nominate' or token == 'nominee' or token == 'deserve' or token == 'rob' or token == "lose":  # or token == 'lost' or token == "lose":
                # nominee_tweets.append(tweet)
                a = find_award(year, tweet)
                if a != '':
                    curraward = a
                    lst = nomfilter(tweet, key_words)
                    noms_split[a] += lst
                else:
                    noms_split[curraward] += nomfilter(tweet, key_words)
            if token == 'beauty' or token == 'pretty' or token == 'dress' or token == 'ugly':
                dressed = find_dressed(dressed, tweet, key_words)
        if n == 0:
            break
        n -= 1

    unique_hosts = sorted(set(potential_hosts), key=potential_hosts.count)
    hosts_counts = [potential_hosts.count(host) for host in unique_hosts]
    # possible_hosts = list(zip(unique_hosts, hosts_counts))

    award_tree.count = 0
    get_phrases(award_tree, '', award_names)
    unique_award_names = sorted(set(award_names.keys()), key=lambda x: award_names[x])
    awards_counts = [award_names[award_name] for award_name in unique_award_names]
    possible_award_names = list(zip(unique_award_names, awards_counts))
    for award in possible_award_names:
        print(award)
    print(key_words)
    print(len(key_words))

    lstbestdress = sorted(set(dressed['best']), key=dressed['best'].count)
    lstworstdress = sorted(set(dressed['worst']), key=dressed['worst'].count)
    contraversaldressed = 'no one'
    diff = 100
    for i in range(1, len(lstbestdress)):
        for j in range(1, 10):
            if lstbestdress[-i] == lstworstdress[-j] and diff > abs(i - j):
                diff = abs(i - j)
                contraversaldressed = lstbestdress[-i]
    bestdressed = lstbestdress[-1]
    worstdressed = lstworstdress[-1]

    for award in official_awards:
        unique_noms[award] = sorted(set(noms_split[award]), key=noms_split[award].count)
        unique_winners[award] = sorted(set(winners_split[award]), key=winners_split[award].count)
        unique_presenters[award] = sorted(set(presenters_split[award]), key=presenters_split[award].count)
        noms_counts[award] = [noms_split[award].count(possible_nom) for possible_nom in unique_noms[award]]
        winners_counts[award] = [winners_split[award].count(possible_winner) for possible_winner in
                                 unique_winners[award]]
        presenters_counts[award] = [presenters_split[award].count(possible_pres) for possible_pres in
                                    unique_presenters[award]]
        # possible_noms[award] = list(zip(unique_noms[award], noms_counts[award]))
        # possible_winners[award] = list(zip(unique_winners[award], winners_counts[award]))
        # possible_presenters[award] = list(zip(unique_presenters[award], presenters_counts[award]))

    hosts = find_hosts(unique_hosts, hosts_counts)
    awards = find_awards(unique_award_names, awards_counts)
    winners = find_winners(data_year, unique_winners, winners_counts)
    nominees = find_nominees(data_year, unique_noms, noms_counts, winners)
    presenters = find_presenters(data_year, unique_presenters, presenters_counts)

    print('Calling form_answer...')
    form_answer(data_year, hosts, awards, nominees, winners, presenters)
    best_and_worst(data_year, bestdressed, worstdressed)
    end_time = time.time()
    print("Main complete")
    print('Time: ', str(end_time - start_time))
    return


if __name__ == '__main__':
    main()

# unused import statements
#
# import string
# from difflib import SequenceMatcher
# from pprint import pprint
#
# unused functions
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