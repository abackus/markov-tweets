import numpy
import twitter
import sys
from my_api import api

# my_api should be of the following form
#import twitter
#api = twitter.Api(consumer_key='',
#    consumer_secret='',
#    access_token_key='',
#    access_token_secret='')

# Configuration
INPUT = "aloofAbacus"
OUTPUT = "aloofAsshat"
FILE = "aidan.npy"
DOSE = 3 # how many to tweet at one time
NOMENTIONS = True # False if you want to @ people

def generate_chain(tweets):
    # Create counts of everything
    counters = {}
    sums = {}
    for tweet in tweets:
        tweet = tweet.split()
        prior_word = 0
        for word in tweet:
            if prior_word not in counters:
                counters[prior_word] = {}
                sums[prior_word] = 0
            if word in counters[prior_word]:
                counters[prior_word][word] = counters[prior_word][word] + 1
            else:
                counters[prior_word][word] = 1
            sums[prior_word] = sums[prior_word] + 1
            prior_word = word
        if prior_word not in counters:
            counters[prior_word] = {}
            sums[prior_word] = 0
        counters[prior_word][0] = 1
        sums[prior_word] = sums[prior_word] + 1
    
    # Create a Markov chain from the counts
    chain = {}
    seeds = {}
    for prior in counters:
        if prior == 0:
            for word in counters[prior]:
                seeds[word] = counters[prior][word] * 1.0 / sums[prior]
            continue
        for word in counters[prior]:
            if prior not in chain:
                chain[prior] = {}
            chain[prior][word] = counters[prior][word] * 1.0 / sums[prior]
    return chain, seeds

def get_seed(seeds):
    return numpy.random.choice(list(seeds.keys()), p=list(seeds.values()))

def generate_tweet(chain, seeds):
    word = get_seed(seeds)
    slen = len(word) + 1
    tweet = [word]
    while slen <= 140:
        curr = chain[word]
        try:
            word = numpy.random.choice(list(curr.keys()), p=list(curr.values()))
        except ValueError:
            word = get_seed(seeds)
        if word == 0:
            break
        slen = slen + len(word) + 1
        tweet.append(word)
    while slen > 140:
        slen = slen - len(tweet.pop()) - 1
    stweet = ""
    for word in tweet:
        stweet = stweet + word + " "
    if NOMENTIONS:
        stweet = stweet.replace("@", "")
    return stweet[0:-1]

def get_tweets():
    statuses = api.GetUserTimeline(screen_name=INPUT, include_rts=False, exclude_replies=True)
    try:
        old_statuses = numpy.load(FILE)
    except IOError:
        old_statuses = []
    for s in old_statuses:
        statuses.append(s)
    numpy.save(FILE, statuses)
    return [s.text for s in statuses]

def tweet(count):
    tweets = get_tweets()
    chain, seeds = generate_chain(tweets)
    for i in range(count):
        tweet = generate_tweet(chain, seeds)
        try:
            api.PostUpdate(tweet)
        except twitter.error.TwitterError:
            print("failed tweet: " + tweet)

if len(sys.argv) > 1 and "markov" in sys.argv[1]:
    chain, seeds = generate_chain(get_tweets())
    print("SEEDS:")
    for seed in seeds:
        print("\t" + seed + " : " + str(seeds[seed]))
    for prior in chain:
        print("PRIOR: " + prior)
        for word in chain[prior]:
            if word == 0:
                print("\tTERMINATE : " + str(chain[prior][0]))
            else:
                print("\t" + word + " : " + str(chain[prior][word]))
else:
    tweet(DOSE)
