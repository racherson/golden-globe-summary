import copy
import json
import re
import spacy
import sys
import time
from difflib import SequenceMatcher
from spacy.tokenizer import Tokenizer

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
ner = spacy.load('en_core_web_sm', disable=['parser', 'tagger'])
tokenizer = Tokenizer(nlp.vocab)
custom_stop_words = [
    'Golden Globes', 'goldenglobes', '@', 'golden globes', 'RT', 'GoldenGlobes', '\n', '#', '#GoldenGlobes', 'gg',
    'Golden Globe.', 'Golden Globe', 'golden globe', '@goldenglobes', '@GG', '@gg', '#goldenglobes', '#gg', '#GG',
    'Golden Globes.', '@GoldenGlobes', 'tonight', 'this year', 'last year', 'next year', 'the golden globes',
    'The Golden Globes', 'the goldenglobes', 'the GoldenGlobes', 'The goldenglobes', 'The GoldenGlobes',
    'the Golden Globes', 'The golden globes', 'rt', 'golden', 'Golden', 'globes', 'Globes', 'GoldenGlobe', 'the year',
    'Globe', 'globe', 'award', 'awards', 'Awards', 'Award', 'goldenglobe']


def get_first_and_last(hosts, index):
    name = hosts[index]
    split_name = name.split(' ')
    if len(split_name) >= 2:
        return name  # return name if already two or more parts
    count = 1
    if index < 0:
        limit = len(hosts) + index + 1
    else:
        limit = index + 1
    max_limit = 5  # max number of additional names to check
    while count < min(limit, max_limit):
        next_name = hosts[index-count]
        split_next_name = next_name.split(' ')
        if split_next_name[0] == split_name[0]:
            return next_name
        count += 1
    return name


def find_dressed(dressed, tweet, key_words):
    names = find_names(tweet, key_words)
    if not names:
        return
    for token in tweet:
        word = token.text.lower()
        if word == 'beauty' or word == 'pretty' or word == 'gorgeous' or word == 'best' or word == 'fashionista':
            for person in names:
                dressed['best'].append(person)
            break
        if ((word == 'ugly' or word == 'ew' or word == 'bad' or word == 'terrible' or word == 'worst'
             or word == 'gross' or word == 'awful')):
            for person in names:
                dressed['worst'].append(person)
            break


def find_hosts(unique_hosts, counts):
    hosts = []
    if not unique_hosts:
        return hosts
    first_host = get_first_and_last(unique_hosts, -1)  # make sure to find the first and last name
    split_first_host = first_host.split(' ')
    first_host_count = counts[-1]
    hosts.append(first_host)
    # if the second highest name doesn't have the same first name and is within a percentage, add it as well
    count = 1
    limit = 10  # max number of additional potential hosts to check
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
    answer = load_data('answer' + str(year) + '.json')
    awards = answer['awards']
    return awards


def find_nominees(year, unique_nominees, counts, winners):
    nominees = {}
    official_awards = get_awards_by_year(year)
    for award in official_awards:
        nom_list = []
        mentions = counts[award]
        award_noms = unique_nominees[award]
        if len(mentions) > 1:
            if (mentions[-1] / 2) >= mentions[-2]:  # and mentions[-1] > 4:
                cutoff = mentions[-2] / 2
            else:
                cutoff = mentions[-1] / 2
            for i in range(1, len(mentions)):
                sim_flag = False
                if mentions[-i] >= cutoff:
                    curr_nom = award_noms[-i]
                    split_name = curr_nom.split(' ')
                    if not award_noms[-i] == winners[award]:
                        for nom in nom_list:
                            if SequenceMatcher(None, nom, curr_nom).ratio() >= 0.8:
                                sim_flag = True
                            split = nom.split(' ')
                            for word in split:
                                for new_word in split_name:
                                    if SequenceMatcher(None, new_word, word).ratio() >= 0.85:
                                        sim_flag = True
                        if not sim_flag:
                            nom_list.append(award_noms[-i])
                else:
                    break
        elif award_noms:
            nom_list.append(award_noms[-1])
        nominees[award] = nom_list
    return nominees


def get_nominees(year):
    '''Nominees is dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    answer = load_data('answer' + str(year) + '.json')
    award_data = answer['award_data']
    nominees = {}
    for award in award_data.keys():
        nominees[award] = award_data[award][0]
    return nominees


def nom_filter(tweet, key_words):
    nom_list = []
    for ent in tweet.ents:
        if not ent_filter(ent):
            continue
        ignore_flag = False
        nom = re.sub(r'[^A-Za-z ]+', '', ent.text)  # remove any characters that are not alphabetic or a space
        if ((not nom or nom[0] == ' ' or nom[-1] == ' ' or nom[0].islower() or nom.lower() in custom_stop_words
             or nom.strip(' ').lower() in custom_stop_words)):
            continue
        for word in nom.split(' '):
            if word.lower() in custom_stop_words or word.lower() in key_words:
                ignore_flag = True
        if not ignore_flag and not (nom == '' or nom == ' '):
            nom_list.append(nom)
    return nom_list


def find_winners(year, unique_winners):
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
    answer = load_data('answer' + str(year) + '.json')
    award_data = answer['award_data']
    winners = {}
    for award in award_data.keys():
        winners[award] = award_data[award][1]
    return winners


def find_presenters(year, unique_presenters, counts):
    official_awards = get_awards_by_year(year)
    presenters = {}
    similarity_coefficient = 0.9
    # get presenters
    for award in official_awards:
        award_presenters = unique_presenters[award]
        if len(award_presenters) == 0:
            presenters[award] = []
        else:
            first_presenter = award_presenters[-1]
            first_presenter_count = counts[award][-1]
            presenters[award] = [first_presenter]
            count = 1
            limit = 2  # set max number of potential presenters
            while count < min(len(award_presenters), limit):
                presenter = award_presenters[-1-count]
                if (counts[award][-1-count] / first_presenter_count) > similarity_coefficient:
                    presenters[award].append(presenter)
                count += 1
    return presenters


def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
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


# load json file as dictionary, eg. 'gg20XX.json'
def load_data(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data


def extract_text(tweets):
    tweet_text = []
    filtered_tweets = copy.deepcopy(tweets)
    for tweet in filtered_tweets:
        if tweet['text'][0:2].lower() != 'rt':  # exclude retweets
            tweet_text.append(tweet['text'])
    return tweet_text


# return True if we want to append token, otherwise False
def token_filter(token):
    return not (token.is_punct or token.is_space or token.is_stop or len(token.text) <= 3 or '@' in token.text
                or '#' in token.text or 'http' in token.text)


# return True if we want to append entity, otherwise False
def ent_filter(ent):
    return not (ent.text.lower() in custom_stop_words or '@' in ent.text or '#' in ent.text or 'http' in ent.text)


def get_awards_by_year(year):
    if year > 2018:
        return OFFICIAL_AWARDS_1819
    return OFFICIAL_AWARDS_1315


def find_award(year, tweet):
    official_awards = get_awards_by_year(year)
    best_match = ''
    best = 0  # must have at least one significant word in common
    official_tokens = tokenizer.pipe(official_awards)
    for award in official_tokens:
        temp = 0
        for award_token in award:
            # if award_token.lower == 'best' or award_token.is_stop:  # exclude shared and insignificant words
            #     continue
            for tweet_token in tweet:
                if award_token.lower == tweet_token.lower:
                    temp += 1
                    break
                elif award_token.lower == 'television' and tweet_token.lower == 'tv':
                    temp += 1
                    break
                elif award_token.lower == 'picture' and (tweet_token.lower == 'film' or tweet_token.lower == 'movie'):
                    temp += 1
                    break
        if temp > best:
            best = temp
            best_match = award.text
    return best_match


# can generalize this function to find names with any number of parts, eg. John Doe = 2, A Great Movie = 3
# then we can use it to find the names of movies as well as people whose names are more than 2 parts
def find_names(tweet, key_words):
    text = tweet.text
    pattern = r'([A-Z][a-z]+ [A-Z][a-z]+)'  # regex pattern to find capitalized two-part names
    matches = re.findall(pattern, text)
    names = []
    for match in matches:
        if match.lower() in custom_stop_words:
            continue
        split = match.split(' ')
        ignore_flag = False
        for word in split:
            if nlp.vocab[word.lower()].is_stop or word.lower() in key_words:  # ignore potential names that share words with the official awards list
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
        answer['award_data'][award] = [nominees[award], winners[award], presenters[award]]
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
        if winner is None:
            winner = 'N/A'
        file.write('\nWinner: ' + winner + '\n\n')
    file.close()
    # print results to console
    print('\nHost(s):\n')
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


def best_and_worst(year, best_dressed, worst_dressed, controversially_dressed):
    file = open('readableanswer' + str(year) + '.txt', 'a')
    file.write('Best Dressed: ' + best_dressed + '\n')
    file.write('Worst Dressed: ' + worst_dressed + '\n')
    file.write('Controversially Dressed: ' + controversially_dressed + '\n')
    file.close()
    # print results to console
    print('Red Carpet:\n')
    print('Best Dressed: ' + best_dressed)
    print('Worst Dressed: ' + worst_dressed)
    print('Controversially Dressed: ' + controversially_dressed)
    print('')


# experimental phrase tree implementation, uses less memory when storing lists of strings with similar substrings
class WordNode:
    def __init__(self, word):
        self.word = word
        self.children = {}
        self.count = 0


def add_phrase(node, split_phrase):
    if len(split_phrase) == 0:
        node.count += 1  # iterate count if end of phrase
        return
    next_word = None
    for child_word in node.children.keys():  # if one of the remaining words is a child, continue down that path
        if child_word in split_phrase:
            next_word = child_word
            split_phrase.remove(next_word)
            add_phrase(node.children[next_word], split_phrase)  # recurse with the word removed
            return
    if not next_word:
        next_word = split_phrase[0].lower()
        if nlp.vocab[next_word].is_stop:
            add_phrase(node, split_phrase[1:])  # recursively continue to add phrase with next word
        elif next_word in node.children.keys():
            add_phrase(node.children[next_word], split_phrase[1:])  # if path exists, recurse that way
        else:
            new_word_node = WordNode(next_word)  # otherwise create new node
            node.children[next_word] = new_word_node
            add_phrase(new_word_node, split_phrase[1:])  # continue recursively adding phrase with new node


def get_phrases(node, prepend_str, award_names):
    if not prepend_str:
        new_prepend_str = node.word
    else:
        new_prepend_str = prepend_str + ' ' + node.word  # add current node's word to current phrase
    if node.count > 0:
        award_names[new_prepend_str] = node.count  # if complete phrase, add to dict
    for child in node.children.keys():
        get_phrases(node.children[child], new_prepend_str, award_names)  # recurse on all children


def find_award_names(award_tree, tweet):
    text = tweet.text
    pattern = r'([Bb]est( [A-Za-z]+)+)'
    # aux_pattern = r'(\-( [A-Za-z]+)+)'  # for finding genres, possibly related entities
    matches = re.findall(pattern, text)
    # aux_matches = re.findall(aux_pattern, text)
    # aux_words = []
    # for aux_match in aux_matches:
    #     aux_split = aux_match[0][2:].split(' ')
    #     for word in aux_split:
    #         if word.lower() in award_words:  # if auxiliary words are common words in awards, append them
    #             aux_words += aux_split
    #             break
    for match in matches:
        split = match[0].split(' ')[1:]  # + aux_words
        add_phrase(award_tree, split)  # add phrase to phrase tree


def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or what it returns.'''
    # pre_ceremony()
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

    potential_hosts = []
    award_tree = WordNode('best')
    award_names = {}
    noms_split = {'misc': []}
    winners_split = {'misc': []}
    presenters_split = {'misc': []}
    unique_noms = {}
    unique_winners = {}
    unique_presenters = {}
    noms_counts = {}
    winners_counts = {}
    presenters_counts = {}
    possible_presenters = {}
    possible_noms = {}
    possible_winners = {}
    dressed = {'best': [], 'worst': []}
    curr_award = 'misc'  # take advantage of chronological ordering, keep track of what award is being talked about

    key_words = {'host', 'hosts', 'hosting', 'award', 'awards', 'awarding', 'awarded', 'nominate', 'nominates',
                 'nominating', 'nominated', 'nominee', 'win', 'wins', 'won', 'winner', 'present', 'presents',
                 'presenting', 'presented', 'accept', 'accepting', 'speech'}  # only used in finding nominees, winners, and presenters!
    official_awards = get_awards_by_year(data_year)
    for award in official_awards:
        noms_split[award] = []
        winners_split[award] = []
        presenters_split[award] = []
        split = award.split(' ')
        for word in split:
            if len(word) > 1 and not nlp.vocab[word].is_stop:
                key_words.add(word)  # populate list with significant words in award names

    for word in custom_stop_words:
        nlp.vocab[word].is_stop = True  # additional custom stop words

    num_tweets = len(data)  # total number of tweets
    n = 200000  # maximum number of tweets to check
    skip = int(num_tweets / n)  # number of tweets to skip per selection
    if skip != 0:
        data = data[0::skip]  # select n evenly spaced tweets from data
    tweets = ner.pipe(data, batch_size=50, n_threads=3)
    # check all tweets and extract necessary data in a single loop for better performance
    for tweet in tweets:
        tokens = []
        next_flag = False
        should_flag = False
        for token in tweet:
            t = token.lower
            if t == 'next':  # flag tweets about next year
                next_flag = True
                continue
            if t == 'should':  # flag opinion tweets
                should_flag = True
                continue
            if not token_filter(token):
                continue
            tokens.append(token.lemma_.lower())
        for index, token in enumerate(tokens):  # enumeration can be used to check tokens in close proximity
            # find hosts
            if token == 'host' and not (next_flag and should_flag):
                for ent in tweet.ents:  # store entities from spaCy's named entity recognizer
                    if ent_filter(ent):
                        potential_hosts.append(ent.text.lower())
                # break
            # find awards
            if token == 'best':
                # award_tweets.append(tweet)
                find_award_names(award_tree, tweet)  # store potential award names in award name phrase tree
                # for ent in tweet.ents:
                #     if len(ent.text) > 4 and ent.text[:4].lower() == 'best':
                #         award_names.append(ent.text.lower())
                # break  # just for performance while developing
            # find presenters
            if token == 'present':
                # presenter_tweets.append(tweet)
                a = find_award(data_year, tweet)
                if a != '':
                    curr_award = a
                    presenters_split[a] += find_names(tweet, key_words)
                else:
                    presenters_split['misc'] += find_names(tweet, key_words)
                # break
            # find winners
            if ((token == 'win' or token == 'congrats' or token == 'congratulations' or token == 'accept'
                 or token == 'speech')):  # or token == 'congratulate', 'receive'
                # winner_tweets.append(tweet)
                a = find_award(data_year, tweet)
                if should_flag:
                    if a != '':
                        curr_award = a
                        noms_split[a] += nom_filter(tweet, key_words)
                    else:
                        noms_split[curr_award] += nom_filter(tweet, key_words)
                else:
                    if a != '':
                        curr_award = a
                        winners_split[a] += find_names(tweet, key_words)
                    else:
                        winners_split['misc'] += find_names(tweet, key_words)
                # break
            # find nominees
            if token == 'nominate' or token == 'nominee' or token == 'deserve' or token == 'lose' or token == 'rob':
                # nominee_tweets.append(tweet)
                a = find_award(data_year, tweet)
                if a != '':
                    curr_award = a
                    noms_split[a] += nom_filter(tweet, key_words)
                else:
                    noms_split[curr_award] += nom_filter(tweet, key_words)
                # break
            if token == 'dress' or token == 'beauty' or token == 'pretty' or token == 'ugly' or token == 'fashion':
                find_dressed(dressed, tweet, key_words)
                # break
        if n == 0:
            break
        n -= 1

    # prepare potential hosts data
    unique_hosts = sorted(set(potential_hosts), key=potential_hosts.count)
    hosts_counts = [potential_hosts.count(host) for host in unique_hosts]
    # possible_hosts = list(zip(unique_hosts, hosts_counts))

    # prepare potential award names data
    award_tree.count = 0  # avoid considering 'best' as the name of an award in itself
    get_phrases(award_tree, '', award_names)  # populate award names list with phrases from phrase tree
    unique_award_names = sorted(set(award_names.keys()), key=lambda x: award_names[x])
    awards_counts = [award_names[award_name] for award_name in unique_award_names]
    # possible_award_names = list(zip(unique_award_names, awards_counts))

    # prepare best/worst/controversially dressed data
    best_dressed = sorted(set(dressed['best']), key=dressed['best'].count)
    worst_dressed = sorted(set(dressed['worst']), key=dressed['worst'].count)
    controversially_dressed = 'N/A'
    diff = len(best_dressed) + len(worst_dressed)
    if best_dressed and worst_dressed:
        for i in range(1, len(best_dressed)):
            for j in range(1, len(worst_dressed)):
                if best_dressed[-i] == worst_dressed[-j] and diff > abs(i-j):
                    diff = abs(i-j)
                    controversially_dressed = best_dressed[-i]
        best_dressed = best_dressed[-1]
        worst_dressed = worst_dressed[-1]
    else:
        best_dressed = 'N/A'
        worst_dressed = 'N/A'

    # prepare nominee/winner/presenter data for each award
    for award in official_awards:
        unique_noms[award] = sorted(set(noms_split[award]), key=noms_split[award].count)
        unique_winners[award] = sorted(set(winners_split[award]), key=winners_split[award].count)
        presenters_split_set = set(presenters_split[award])
        if unique_winners[award]:
            winner_name = get_first_and_last(unique_winners[award], -1)
            if winner_name in presenters_split_set:
                presenters_split_set.remove(winner_name)
        unique_presenters[award] = sorted(presenters_split_set, key=presenters_split[award].count)
        noms_counts[award] = [noms_split[award].count(possible_nom) for possible_nom in unique_noms[award]]
        winners_counts[award] = [winners_split[award].count(possible_winner)
                                 for possible_winner in unique_winners[award]]
        presenters_counts[award] = [presenters_split[award].count(possible_pres)
                                    for possible_pres in unique_presenters[award]]
        # possible_noms[award] = list(zip(unique_noms[award], noms_counts[award]))
        # possible_winners[award] = list(zip(unique_winners[award], winners_counts[award]))
        # possible_presenters[award] = list(zip(unique_presenters[award], presenters_counts[award]))

    hosts = find_hosts(unique_hosts, hosts_counts)
    awards = find_awards(unique_award_names, awards_counts)
    winners = find_winners(data_year, unique_winners)
    nominees = find_nominees(data_year, unique_noms, noms_counts, winners)
    presenters = find_presenters(data_year, unique_presenters, presenters_counts)

    print('Forming answer...')
    form_answer(data_year, hosts, awards, nominees, winners, presenters)  # serialize answers for access in get funcs
    best_and_worst(data_year, best_dressed, worst_dressed, controversially_dressed)
    end_time = time.time()
    print('Main complete')
    print('Time: ', str(end_time - start_time))
    return


if __name__ == '__main__':
    main()

# unused import statements
#
# import pdb
# import string
# from pprint import pprint
#
# unused functions
#
# def parse_text(tweets):
#     spacy_tweets = tokenizer.pipe(tweets)
#     ner = nernlp.pipe(tweets)
#     return spacy_tweets, ner
#
# def find_award_alt(tweet):
#     best = 0
#     best_match = ''
#     for award in OFFICIAL_AWARDS:
#         for index, token in enumerate(tweet):
#             if token.text == 'best':
#                 if tweet[index] == tweet[-1]:
#                     continue
#                 if 'dress' in tweet[index+1].text:
#                     continue
#                 text = tweet[index:(index+4)].text
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
# # found on https://stackoverflow.com/questions/17388213/find-the-similarity-metric-between-two-strings
# def similar(a, b):
#     return SequenceMatcher(None, a, b).ratio()
