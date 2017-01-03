"""
Usage:
    from tweet_analyzer import TextAnalyzer
    analyzer = TextAnalyzer(list_of_tweet_dicts)
    tweet_df = analyzer.make_tweet_df(
        with_pos_tags=False,
        columns_to_filter=['id', 'created_at', 'text', 'retweet_count', 'favorite_count'])

Class for analyzing tweets primarily with NLTK
"""
import nltk
from nltk.corpus import cmudict
from nltk.corpus import wordnet # for synonyms
from itertools import chain
from nltk import word_tokenize
import random
import pandas as pd
import os
from nltk.tokenize import TweetTokenizer


class TextAnalyzer:
    def __init__(self, raw_tweets_list=None):
        '''Initialize the object with a list of dictionaries, used for creating
        dataframe with make_tweet_df()'''
        if raw_tweets_list is None:
            raw_tweets_list = [{}]
        self.list_of_tweet_dicts = raw_tweets_list
        return

    def make_tweet_df(self, with_pos_tags=False, columns_to_filter=[]):
        '''Make a pandas dataframe with list of tweets'''
        if len(columns_to_filter) > 0:
            df = pd.DataFrame(self.list_of_tweet_dicts, columns=columns_to_filter)
        else:
            df = pd.DataFrame(self.list_of_tweet_dicts)
        if with_pos_tags:
            df['pos_tags'] = df.text.apply(lambda x: self.get_pos_tags(x))
        df['tweet_words'] = df.text.apply(lambda x: self.tweet_tokenize(x))
        self.core_analysis_df = df
        return df

    def get_top_tweets_by(self, dataframe, by_column, top_number):
        return dataframe.sort(by_column, ascending=False)[:top_number]

    def get_average_length(self, tweets_list):
        '''Get the average tweet length from the entire list of tweets.'''
        return sum(map(len, tweets_list))/float(len(tweets_list))
    
    def tweet_tokenize(self, tweet):
        #http://www.nltk.org/api/nltk.tokenize.html
        tknzr = TweetTokenizer()
        tokens = tknzr.tokenize(tweet)
        return tokens

    def lookup_word(self, df, word, pos_tag): 
        return df[(df['word'] == word) & (df['pos_tag'] == pos_tag)]

    def get_pos_tags(self, tweet):
        ''' Get parts of speech tags from a tweet. 
        Read about POS tags at nltk.help.upenn_tagset()'''
        pos_tags = nltk.tag.pos_tag(self.tweet_tokenize(tweet))
        return pos_tags

    def count_syllables(self, word):
        #http://stackoverflow.com/questions/405161/detecting-syllables-in-a-word
        d = cmudict.dict()
        return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]] 

    def get_word_synonym(self, word):
        '''Get synonyms for a given word.'''
        #http://stackoverflow.com/questions/19348973/all-synonyms-for-word-in-python
        #http://stackoverflow.com/questions/19258652/how-to-get-synonyms-from-nltk-wordnet-python
        synonyms = wordnet.synsets(word)
        lemmas = set(chain.from_iterable([word.lemma_names for word in synonyms]))
        return lemmas

    def make_df_csv(self, dataframe, csv_name, columns_to_encode=[]):
        if '.csv' in csv_name:
            csv_name = csv_name.rstrip('.csv')
        if len(columns_to_encode) > 0:
            for col in columns_to_encode:
                dataframe[col] = dataframe[col].apply(lambda x: x.encode("utf-8"))
        try:
            dataframe.to_csv('data/' + csv_name + '.csv')
        except UnicodeDecodeError: #TODO: not sure if we need this one.
            dataframe[col] = dataframe[col].apply(lambda x: unicode(x, 'utf-8'))
        except IOError:
            os.makedirs('data')
            dataframe.to_csv('data/' + csv_name + '.csv', encoding='utf-8')
        return 

    def make_pos_df(self, tweets_list, make_csv=False):
        '''take list of tweets, non tokenized, and return a dataframe of all words
        with their pos tags'''
        word_pos_mlist = []
        for t in tweets_list:
            temp_df = self.core_analysis_df[self.core_analysis_df.text == t]
            pos_tags = self.get_pos_tags(t)
            ld =[{'word': tag[0], 'pos_tag': tag[1]} for tag in pos_tags]
            word_pos_mlist.extend(ld)

        df = pd.DataFrame(word_pos_mlist)
        if make_csv:  
            self.make_df_csv(df, csv_name='pos_df', columns_to_encode=['word'])
        return df

    def make_word_frequency_df(self, pos_df, frequency_col, pos_tag_slice=None, make_csv=False):
        '''return a frequency dataframe. optionally slice on a part of speech tag'''
        true_raw_df_size = len(pos_df)
        if pos_tag_slice:
            pos_df = pos_df[pos_df.pos_tag == pos_tag_slice]
        s = pos_df[frequency_col].value_counts()
        df = pd.DataFrame(s, columns=['abs_frequency']).reset_index().rename(
            columns={'index':frequency_col})
        df['rel_frequency'] = (df['abs_frequency'] / true_raw_df_size) * 100
        if make_csv:
            self.make_df_csv(df, csv_name='word_frequency_df.csv')
        return df

    def make_word_in_articles_frequency_df(self, lookup_words, tweets_list, make_csv=False):
        ''' Looks up each word against a list of tweets. 
        Counts the number of times it occurs at least once across all tweets given'''
        dl = []
        lookup_words = list(set(lookup_words))
        for w in lookup_words:
            counter = 0
            for tweet in tweets_list:
                temp_df = self.core_analysis_df[self.core_analysis_df.text == tweet]
                tweet_words = temp_df.ix[temp_df.get('tweet_words').first_valid_index()].tweet_words
                if w in tweet_words:
                    counter+=1 
                    continue
            dl.append({'word': w, 'occurs_at_least_once_count':counter})
        df = pd.DataFrame(dl, columns=['word', 'occurs_at_least_once_count']).sort('occurs_at_least_once_count', ascending=False)
        df['occurs_in_tweets_pct'] = (df['occurs_at_least_once_count'] / float(len(tweets_list))) * 100 
        if make_csv:
            self.make_df_csv(df, csv_name='word_occurrences_in_tweet.csv')
        return df

    def word_length(self, word):
        return len(word)
