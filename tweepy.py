#!/usr/bin/python
"""
Usage:
    from tweepy import TwitterApi
    t = TwitterApi()
    tweets = t.get_user_timeline(user_handle)

Class for authing and getting a user's timeline from Twitter's API.
"""
import base64
import requests
import json
import pprint
import re
from dateutil import parser
from datetime import date
import time 
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
config = json.load(open(dir_path + '/config.json'))

class TwitterApi:
    def __init__(self):
        for key, value in config.items():
            setattr(self, key, value)
        self.auth()
        return

    def _get(self, url):
        headers= {'Authorization': 'Bearer ' + self.access_token}
        #self.base_url = https://api.twitter.com/1.1/
        try:
            print "Making Request: %s" % self.base_url + url
            r = requests.get(self.base_url + url, headers=headers)
            return r
        except Exception as e:
            print e
        return

    def auth(self):
        # get the bearer token by issuing a request to the api with the auth_string
        # using application-only auth method. https://dev.twitter.com/docs/auth/application-only-auth
        # declare the consumer key and secret, concat them, and base64 encode them
        params = {'grant_type':'client_credentials'}
        auth_string = self.consumer_key+':'+self.consumer_secret
        auth_string_b64 = base64.b64encode(auth_string)
        headers = {
            'Authorization': 'Basic ' + auth_string_b64,
            'content-type':'application/x-www-form-urlencoded;charset=UTF-8'}
        r = requests.post('https://api.twitter.com/oauth2/token',headers=headers,data=params).json()
        self.access_token = r["access_token"]
        return 

    #TODO: fix this implementation
    def search_tweets(self, search_term, result_type='recent', 
        count=100, language='en', since_id=None, max_id=None):
        # https://dev.twitter.com/rest/public/search
        if search_term.startswith('#'):
            search_term = search_term.replace('#', '%23')
        search_url = "search/tweets.json?q="
        request_url = search_url + search_term + '&result_type=' + result_type + '&count=' + str(count) + '&language=' + language
        if since_id:
            request_url = request_url + '&since_id={}'.format(since_id)
        response = self._get(request_url).json()
        return response

    #TODO: fix this implementation for true qstr usefulness. 
    def get_user_timeline(self, screen_name, max_id=None, count=200, since_id=None):
        #https://dev.twitter.com/rest/reference/get/statuses/user_timeline
        if max_id and since_id:
            tweets = self._get("statuses/user_timeline.json?screen_name={}&count={}&max_id={}&since_id={}".format(screen_name, count, max_id, since_id)).json()
            return tweets
        elif max_id:
            tweets = self._get("statuses/user_timeline.json?screen_name={}&count={}&max_id={}".format(screen_name, count, max_id)).json()
            return tweets
        elif since_id:
            tweets = self._get("statuses/user_timeline.json?screen_name={}&count={}&since_id={}".format(screen_name, count, since_id)).json()
            return tweets
        else:
            tweets = self._get("statuses/user_timeline.json?screen_name={}&count={}".format(screen_name, count)).json()
            return tweets 
