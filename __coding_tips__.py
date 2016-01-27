# coding: utf-8
""" Бот. Ищет фавнутые @strizhechenko твиты @coding_tips_sys и ворует их """
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from twitterbot_utils import Twibot
from twitterbot_utils.TwiUtils import faved_for_steal, tweet_multiple

__author__ = "@strizhechenko"

BOT = Twibot()
SCHED = BlockingScheduler()


@SCHED.scheduled_job('interval', minutes=1)
def do_tweets():
    """ раз в минуту ищем новые фавнутые твиты """
    tweets = faved_for_steal('strizhechenko', 'coding_tips_sys', BOT.api)
    tweet_multiple(tweets, BOT, logging=True)

if __name__ == '__main__':
    if '--test' in sys.argv:
        do_tweets()
    else:
        SCHED.start()
