import numpy

INPUT = "aloofAbacus"
OUTPUT = "aloofAsshat"
FILE = "aidan.npy"

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

def generate_tweet(chain, seeds):
    word = numpy.random.choice(list(seeds.keys()), p=list(seeds.values()))
    slen = len(word) + 1
    tweet = [word]
    while slen <= 140:
        curr = chain[word]
        word = numpy.random.choice(list(curr.keys()), p=list(curr.values()))
        if word == 0:
            break
        slen = slen + len(word) + 1
        tweet.append(word)
    while slen > 140:
        slen = slen - len(tweet.pop()) - 1
    stweet = ""
    for word in tweet:
        stweet = stweet + word + " "
    return stweet[0:-1]

def test():
    tweets = ["What if the real system updates were the friends we made along the way",
        "tfw you get reported to the FBI",
        "*regresses to weeb trash middle school state*",
        "why are people just totally wrong about everything",
        "sequel to Hamilton about Evariste Galois when",
        "but what about the emails that were assassinated in ben gazarra",
        "a set is perfect if and only if its closed and all its points are limit. stop narcissism by not telling every set that they're perfect!",
        "i should write a markov chain bot to automate my shitposts for me"]
    chain, seeds = generate_chain(tweets)
    #for prior in chain:
    #    print(str(prior) + ":")
    #    for word in chain[prior]:
    #        print("\t" + str(word) + ":" + str(chain[prior][word]))
    print(generate_tweet(chain, seeds))

test()
