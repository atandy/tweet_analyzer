#https://dev.twitter.com/rest/public/timelines
"""
Usage:
  For first-time run: python get_user_tweets.py --user_handle sweetastandy
  To append to existing pulled tweets: 
  python get_user_tweets.py --user_handle sweetastandy --existing_file sweetastandy_master_tweet_list.json

Script for getting the last 3200 Tweets from a user's timeline.
"""
import tweepy
import argparse
import sys

parser = argparse.ArgumentParser(description='Process user handle input')
parser.add_argument('--user_handle', 
    required=True,
    metavar='U',
    type=str,
    help="a twitter user handle. example: realDonaldTrump")
parser.add_argument('--existing_file',
    metavar='F',
    type=str, 
    help="""An existing file to write to. If you pass a file in, 
    it will get the last Tweet written at the top of that file, 
    and get Tweets added since that Tweet. 
    Results will be appended to the existing file""")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
args = parser.parse_args()
user_handle = args.user_handle
existing_file = args.existing_file

def write_tweets(write_type):
    ''' write type either a or w. 'w' for the first time. 'a' if existing file'''
    master_tweet_list.reverse() # reverse so oldest tweets are at top of file.
    try:
        with open(user_handle + '_master_tweet_list.json', write_type) as ff:
            for t in master_tweet_list:
                ff.write(str(t) + '\n')
    except Exception as e:
        print e

def get_all_pages(max_id=None, since_id=None):
    '''get all pages from a user timeline given different parameters.'''
    #TODO: ew.
    while len(master_tweet_list) < 3200:
        tweets = tweepy.get_user_timeline(
            user_handle, 
            max_id=max_id, 
            since_id=since_id)
        if len(tweets) == 0:
            print 'No more tweets to process.'
            break
        if min([t['id'] for t in tweets]) == max_id:
            break
        max_id = min([t['id'] for t in tweets])
        master_tweet_list.extend(tweets)
    return 

tweepy = tweepy.TwitterApi()
master_tweet_list = []

# if there is an existing file, process results to it.
if existing_file:
    with open(existing_file, 'r') as ef:
        last_tweet = ef.readlines()[-1] # get last tweet
        last_id = eval(last_tweet)["id"]
        get_all_pages(since_id=last_id)
        write_tweets('a') # append to existing file
else:
    tweets = tweepy.get_user_timeline(user_handle)
    try:
        master_tweet_list.extend(tweets)
    except TypeError as e:
        if str(e) == "'NoneType' object is not iterable":
            print "No tweets returned from Twitter API. Exiting script."
            #TODO: do a retry here.
            sys.exit()
    max_id = min([t['id'] for t in tweets]) # used for pagination
    get_all_pages(max_id)
    write_tweets('w') # write new file.