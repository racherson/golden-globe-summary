import copy
import json
import spacy
import time
from pprint import pprint
from spacy.tokenizer import Tokenizer

nlp = spacy.load('en_core_web_sm', disable=['parser', 'tagger'])
custom_stop_words = [
    'Golden Globes', 'goldenglobes', '@', 'golden globes', 'RT', 'GoldenGlobes', '\n', '#', "#GoldenGlobes"
]

tokenizer = Tokenizer(nlp.vocab)

OFFICIAL_AWARDS = ['cecil b. demille award', 'best motion picture - drama',
                   'best performance by an actress in a motion picture - drama',
                   'best performance by an actor in a motion picture - drama',
                   'best motion picture - comedy or musical',
                   'best performance by an actress in a motion picture - comedy or musical',
                   'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film',
                   'best foreign language film',
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

tweets = {}
awards_tweets = []
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
    global tweets
    # names = {}
    # docs = []
    tweets_2013 = load_data('gg2013.json')
    tweets_2013 = extract_text(tweets_2013)
    tweets[2013] = tweets_2013
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
    return


# load json file as dictionary
# file_name: 'gg2013.json'
def load_data(file_name):
    tweets = {}
    with open(file_name, 'r') as f:
        tweets = json.load(f)
    return tweets


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
    ner = nlp.pipe(tweets)
    return spacy_tweets, ner


def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    global tweets
    global hosts
    global awards
    global awards_tweets

    print('Starting...')
    start_time = time.time()
    for w in custom_stop_words:
        nlp.vocab[w].is_stop = True
    pre_ceremony()

    # data = load_data('processed_gg2013.json')
    # num_tweets = len(data)
    # n = 100000
    # skip = int(num_tweets/n)
    # data = data[0::skip]
    # tweets[2013] = nlp.pipe(data)

    # tweets_2013, ner = parse_text(tweets[2013])
    data = load_data('processed_gg2013.json')
    # tweets[2013] = nlp.pipe(data)
    data = nlp.pipe(data)
    serializable_data = []
    test = True
    for tweet in data:
        if test:
            pprint(type(tweet))
            test = False
        serializable_data.append(tweet.to_bytes())
    recovered_data = []
    for tweet in serializable_data:
        recovered_data.append(nlp('').from_bytes(tweet))
    pprint(type(recovered_data[0]))
    tweets[2013] = recovered_data
    n = 100000  # limit number of tweets we search
    for tweet in tweets[2013]:
        tokens = []
        next_flag = False
        should_flag = False
        ignore_flag = False
        for token in tweet:
            t = token.text.lower()
            if t == 'next':  # ignore tweets about next year
                next_flag = True
            if t == 'should':  # ignore opinion tweets
                should_flag = True
            if not token_filter(token):
                continue
            # tokens.append(token.lemma_.lower())
            tokens.append(token.text.lower())
        for token in tokens:
            # if token == 'host' and not (next_flag and should_flag):
            #     for ent in tweet.ents:
            #         if ent_filter(ent):
            #             hosts.append(ent.text.lower())
            #     pprint(tweet)
            # awards checking
            if token == 'best' and not should_flag:
                awards_tweets.append(tweet)
                break  # just for performance while developing
        if n == 0:
            break
        n -= 1

    # unique_hosts = sorted(set(hosts), key=hosts.count)
    # counts = [hosts.count(host) for host in unique_hosts]
    # pprint(list(zip(unique_hosts, counts)))  # print our sorted list of potential hosts + mentions
    # award_names = []
    # for award_tweet in awards_tweets:
    #     # pprint(award_tweet.text)
    #     # for token in award_tweet:
    #     #     pprint(token.pos_)
    #     for ent in award_tweet.ents:
    #         if len(ent.text) > 4 and ent.text[:4].lower() == 'best':
    #             award_names.append(ent.text)
    #             # pprint(ent.text)

    ROLES = {'actor': 'Performance by an Actor in a ',
             'actress': 'Performance by an Actress in a ',
             'director': 'Director - ',
             'screenplay': 'Screenplay - ',
             'score': 'Original Score - ',
             'song': 'Original Song - '}
    MEDIAS = {'animated': 'Animated Feature Film',
              'foreign': 'Foreign Language Film',
              'motion': 'Motion Picture',
              'tv': 'Television Series',
              'television': 'Television Series',
              'mini-series': 'Mini-Series or Motion Picture made for Television'}
    GENRES = {'drama': ' - Drama',
              'comedy': ' - Comedy or Musical',
              'musical': ' - Comedy or Musical'}

    award_names = []
    for award_tweet in awards_tweets:
        role = ''
        supporting = False
        media = ''
        genre = ''
        for token in award_tweet:
            if token.lemma_.lower() == 'dress':
                break
            if token.text.lower() in ROLES.keys():
                if not role:
                    role = token.text.lower()
                continue
            if token.text.lower() == 'supporting':
                supporting = True
                continue
            if token.text.lower() in MEDIAS.keys():
                if not media:
                    media = token.text.lower()
                continue
            if token.text.lower() in GENRES.keys():
                if not genre:
                    genre = token.text.lower()
        if not media:
            continue
        if role == 'director' or role == 'screenplay' or role == 'score' or role == 'song':
            if supporting or genre:
                continue
        if supporting:
            if not role:
                continue
            if genre:
                continue
        if media == 'animated' or media == 'foreign':
            if role or genre:
                continue
        else:
            if not supporting and not genre:
                continue
        if role:
            role = ROLES[role]
        if genre:
            genre = GENRES[genre]
        award_name = 'Best ' + role
        if supporting:
            award_name += 'Supporting Role in a '
        award_name += MEDIAS[media] + genre
        award_names.append(award_name)

    unique_award_names = sorted(set(award_names), key=award_names.count)
    award_counts = [award_names.count(award_name) for award_name in unique_award_names]
    pprint(list(zip(unique_award_names, award_counts)))
    awards = get_awards(2013)
    pprint(awards)

    end_time = time.time()
    print('Time', str(end_time - start_time))
    print("Pre-ceremony processing complete.")
    return


if __name__ == '__main__':
    main()
