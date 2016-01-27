# coding: utf-8
""" раз в час пытаемся запостить цитатку про то как надо программировать """

import sys
from time import sleep

import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler
from twitterbot_utils import tweet_to_text, get_hash, Twibot, tweet_length_ok
from twitterbot_utils import RATE_LIMIT_INTERVAL, get_maximum_tweets


sched = BlockingScheduler()
hashes = []

not_hashtag_or_reply = lambda tweet: u'@' not in tweet and u'#' not in tweet

blacklist = (
    u'выпущено 24 кролика', u'учёные выяснили', u'ученые выяснили',
    u'учёные узнали', u'ученые узнали', u'как часто',
    u'психологи узнали', u'психологи выяснили', u'http://',
    u'https://', u'.com', u't.co', u'сраться', u'Нарния', u'шкафу',
    u'за девственность',
)

replacements = {
    u'надо ебаться': {
        u'надо ебаться': u'программировать надо',
        u'в жопу': u'',
    },
    u'ебаться надо': {
        u'ебаться': u'программировать',
        u'в жопу': u'',
    },
    u'ебаться нужно': {
        u'ебаться': u'программировать',
        u'в жопу': u'',
        u'нужно': u'надо',
    },
    u'трахаться надо': {
        u'трахаться': u'программировать',
        u'в жопу': u'',
    },
    u'трахаться нужно': {
        u'трахаться': u'программировать',
        u'в жопу': u'',
        u'нужно': u'надо',
    },
    u'заниматься сексом надо': {
        u'заниматься сексом': u'программировать',
        u'сексом заниматься': u'программировать',
    },
    u'покажите сиськи': {
        u'покажите': u'откройте',
        u'сиськи': u'исходники',
    },
}


def not_blacklisted(tweet):
    """ некоторые твиты очень часто проскальзывают из-за модификаций """
    for phrase in blacklist:
        if phrase in tweet:
            return False
    return True


def any_tweet_to_str(tweet):
    if isinstance(tweet, tweepy.models.Status):
        tweet_text = tweet_to_text(tweet)
    else:
        tweet_text = tweet
    if isinstance(tweet_text, unicode):
        return tweet_text.encode('utf-8')
    elif isinstance(tweet, str):
        return tweet_text
    else:
        print 'Unknown tweet type:', type(tweet)
        return None


def get_hashes(tweets=None):
    """ По умолчанию - хэшики последних 200 своих твитов """
    hashlist = []
    if not tweets:
        tweets = list(set(bot.api.me().timeline(count=200)))
    if not (tweets and isinstance(tweets, list)):
        return []
    for tweet in tweets:
        tweet_text = any_tweet_to_str(tweet)
        if tweet_text:
            hashlist.append(get_hash(tweet_text))
    return list(set(hashlist))


def apply_replacements(tweet):
    """ совершаем все возможные замены в твите """
    replaced_tweet = tweet
    for replaces in replacements.values():
        for word, replace in replaces.items():
            replaced_tweet = replaced_tweet.replace(word, replace)
    if tweet == replaced_tweet:
        return None
    return replaced_tweet


def _encode(tweet):
    """ tweet должен быть str """
    if isinstance(tweet, unicode):
        return tweet.encode('utf-8')
    return tweet


def process_tweets(tweets, hashlist):
    tweets = map(tweet_to_text, tweets)
    tweets = map(lambda t: t.lower(), tweets)
    tweets = filter(not_hashtag_or_reply, tweets)
    tweets = filter(not_blacklisted, tweets)
    tweets = map(apply_replacements, tweets)
    tweets = filter(lambda tweet: tweet, tweets)
    tweets = map(_encode, tweets)
    tweets = filter(tweet_length_ok, tweets)
    tweets = [tweet for tweet in tweets if get_hash(tweet) not in hashlist]
    return list(set(tweets))


def log_stat(phrase, tweets, tweets_text, tweets_text_all):
    print '##', phrase.encode('utf-8'), len(tweets), len(tweets_text), len(tweets_text_all)


@sched.scheduled_job('interval', hours=1)
def do_tweets():
    """ тянем нужные твиты и скармливаем постилке """
    global hashes
    print "# New tick"
    hashes_len = len(hashes)
    hashes.extend(get_hashes())
    hashes = list(set(hashes))
    print "- hashes: before:", hashes_len, "after", len(hashes)
    tweets_text_all = []
    for phrase in ['"' + key + '"' for key in replacements.keys()]:
        tweets = bot.api.search(phrase, count=200, result_type='recent')
        tweets_text = process_tweets(tweets, hashes)
        tweets_text_all.extend(tweets_text)
        log_stat(phrase, tweets, tweets_text, tweets_text_all)
        sleep(RATE_LIMIT_INTERVAL)
    bot.tweet_multiple(tweets_text_all, logging=True)
    print "Tick end, wait about 30 min"


if __name__ == '__main__':
    bot = Twibot()
    my_tweets = get_maximum_tweets(bot.api.me().timeline)
    hashes.extend(get_hashes(my_tweets))
    # hashes = list(set(hashes))
    print "after extend: hashes %s, tweets %s" % (len(hashes), len(my_tweets))
    if '--test' in sys.argv:
        do_tweets()
        exit(0)
    do_tweets()
    sched.start()
