"""
Usage:
    I would not run this file. You can use this code in an interpreter session,
    or a notebook.
"""
from tweet_analyzer import TextAnalyzer
from nltk.sentiment.util import demo_liu_hu_lexicon
from nltk.corpus import stopwords
from nltk import FreqDist
import pytz
import datetime

def make_data(file_name):
    '''Returns Tuple of dataframes used in analysis:
    core_tweet_df, tweets_list, pos_df, adj_df, word_frequency_df, hash_df'''
    #realDonaldTrump_master_tweet_list.json
    
    #TODO: fix so strings aren't written to file and we can just load it as json.
    with open(file_name) as tfile:
        lines = tfile.readlines()
    raw_tweets_data =  [eval(t) for t in lines]

    analyzer = TextAnalyzer(raw_tweets_data)
    english_stopwords = stopwords.words("english")

    core_tweet_df = analyzer.make_tweet_df(
        with_pos_tags=False,
        columns_to_filter=['id', 'created_at', 'text', 'retweet_count', 'favorite_count'])

    # get list of tweets as text
    tweets_list = core_tweet_df.text.tolist()
    pos_df = analyzer.make_pos_df(tweets_list, make_csv=False)
    adj_df = pos_df[pos_df.pos_tag=='JJ']
    adj_df = analyzer.make_word_frequency_df(adj_df, 'word', make_csv=False)

    # calculate word frequencies among other words in data set. can't merge with pos
    # because certain words have many parts of speech. 
    word_frequency_df = analyzer.make_word_frequency_df(pos_df, 'word', make_csv=False)


    #Most common hashtags and total unique hashtags.
    all_hashtags = []
    for i in raw_tweets_data:
        all_hashtags.extend([d['text'] for d in i['entities']['hashtags']])
    fd = FreqDist(all_hashtags)

    hash_df = pd.DataFrame([{'hashtag':x,'abs_frequency': y, 'rel_frequency_pct': float(y)/len(all_hashtags)*100} for x,y in fd.most_common()])

    return core_tweet_df, tweets_list, pos_df, adj_df, word_frequency_df, hash_df

trump_core_tweet_df, trump_tweets, trump_pos_df, trump_adj_df, trump_word_frequency_df, trump_hash_df = make_data('realDonaldTrump_master_tweet_list.json')
hillary_core_tweet_df, hillary_tweets, hillary_pos_df, hillary_adj_df, hillary_word_frequency_df, hillary_hash_df = make_data('HillaryClinton_master_tweet_list.json')
cnn_core_tweet_df, cnn_tweets, cnn_pos_df, cnn_adj_df, cnn_word_frequency_df, cnn_hash_df = make_data('CNN_master_tweet_list.json')
foxnews_core_tweet_df, foxnews_tweets, foxnews_pos_df, foxnews_adj_df, foxnews_word_frequency_df, foxnews_hash_df = make_data('FoxNews_master_tweet_list.json')


#TODO: all of the stuff below is gross, but I'm trying to get this done. 

print trump_adj_df[trump_adj_df.word.str.islower() & (~trump_adj_df.word.isin(english_stopwords))][:15]
print hillary_adj_df[hillary_adj_df.word.str.islower() & (~hillary_adj_df.word.isin(english_stopwords))][:15]
print cnn_adj_df[cnn_adj_df.word.str.islower() & (~cnn_adj_df.word.isin(english_stopwords))][:15]
print foxnews_adj_df[foxnews_adj_df.word.str.islower() & (~foxnews_adj_df.word.isin(english_stopwords))][:15]

#total hashtag dataframe.
trumptotalhash = pd.DataFrame([{'total_hashtags_used': trump_hash_df.abs_frequency.sum()}]).transpose().rename(columns={0:'@realDonaldTrump'})
hilltotalhash = pd.DataFrame([{'total_hashtags_used': hillary_hash_df.abs_frequency.sum()}]).transpose().rename(columns={0:'@HillaryClinton'})
cnntotal_hash = pd.DataFrame([{'total_hashtags_used': cnn_hash_df.abs_frequency.sum()}]).transpose().rename(columns={0:'@CNN'})
foxnewstotal_hash = pd.DataFrame([{'total_hashtags_used': foxnews_hash_df.abs_frequency.sum()}]).transpose().rename(columns={0:'@FoxNews'})
print pd.concat([trumptotalhash, hilltotalhash, cnntotal_hash, foxnewstotal_hash], axis=1).to_html()

# top 10 favorited tweets
print trump_core_tweet_df.sort('favorite_count', ascending=False).drop_duplicates('id')[:10] 
print hillary_core_tweet_df.sort('favorite_count', ascending=False).drop_duplicates('id')[:10]
print cnn_core_tweet_df.sort('favorite_count', ascending=False).drop_duplicates('id')[:10] 
print foxnews_core_tweet_df.sort('favorite_count', ascending=False).drop_duplicates('id')[:10]

# top 10 retweeted tweets
print trump_core_tweet_df.sort('retweet_count', ascending=False).drop_duplicates('id')[:10] 
print hillary_core_tweet_df.sort('retweet_count', ascending=False).drop_duplicates('id')[:10]
print cnn_core_tweet_df.sort('retweet_count', ascending=False).drop_duplicates('id')[:10] 
print foxnews_core_tweet_df.sort('retweet_count', ascending=False).drop_duplicates('id')[:10] 

def get_favorites(core_df):
    df = core_df.sort('favorite_count', ascending=False).drop_duplicates('id')[:10] 
    return df[['text','favorite_count','created_at']].to_html(index=False).replace('\n', '')

#TODO: insanely slow.
excla_in_tweet_freq = analyzer.make_word_in_articles_frequency_df(['!'], trump_tweets)


# calculate sentence construction and most-used parts of speech. 
pos_grouping = trump_pos_df.groupby('pos_tag').agg({'pos_tag': len}).rename(columns={'pos_tag':'total'}).sort('total', ascending=False)
pos_grouping = analyzer.make_word_frequency_df(trump_pos_df, 'pos_tag')

#TODO: this needs to be way way faster.
trump_core_tweet_df['tweet_sentiment'] = trump_core_tweet_df.text.apply(lambda x: demo_liu_hu_lexicon(x))
trump_core_tweet_df.tweet_sentiment.value_counts()
trump_core_tweet_df.tweet_sentiment.value_counts() / len(trump_core_tweet_df)

# make tweet sentiment df
tsdf = (pd.DataFrame(trump_core_tweet_df.tweet_sentiment.value_counts()).transpose() / 3200).reindex_axis(
    ['Positive', 'Netural', 'Negative'], axis=1).rename(
    columns={'Netural':'Neutral'}).transpose().rename(columns={0:'@realDonaldTrump'})

hcsdf = (pd.DataFrame(hillary_core_tweet_df.tweet_sentiment.value_counts()).transpose() / 3200).reindex_axis(
    ['Positive', 'Netural', 'Negative'], axis=1).rename(
    columns={'Netural':'Neutral'}).transpose().rename(columns={0:'@HillaryClinton'})

cnnsdf = (pd.DataFrame(cnn_core_tweet_df.tweet_sentiment.value_counts()).transpose() / 3200).reindex_axis(
    ['Positive', 'Netural', 'Negative'], axis=1).rename(
    columns={'Netural':'Neutral'}).transpose().rename(columns={0:'@CNN'})

fnewssdf = (pd.DataFrame(foxnews_core_tweet_df.tweet_sentiment.value_counts()).transpose() / 3200).reindex_axis(
    ['Positive', 'Netural', 'Negative'], axis=1).rename(
    columns={'Netural':'Neutral'}).transpose().rename(columns={0:'@FoxNews'})

 print pd.concat([tsdf, hcsdf, cnnsdf, fnewssdf], axis=1).to_html()

### Datetime conversion And Analysis  ###
trump_core_tweet_df['created_at_dt'] = core_tweet_df.created_at.apply(lambda x: datetime.datetime.strptime(x,'%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.UTC))
#g = core_tweet_df.created_at_dt.groupby(by=[core_tweet_df.created_at_dt.map(lambda x : (x.hour))])
'''
In [164]: g.count()
Out[164]:
created_at_dt
0     172
1     241
2     252
3     144
4      76
5      43
6      10
7       7
9      20
10     79
11    155
12    182
13    203
14    159
15    146
16    160
17    139
18    152
19    168
20    164
21    199
22    187
23    150
'''
# TODO: Tweets in 24-hour buckets. When does he tweet the most

# Biggest Days
core_tweet_df['created_at_day'] = core_tweet_df.created_at.apply(lambda x: x.split(' ')[0])
print core_tweet_df.groupby('created_at_day').agg({'created_at_day':len}).sort('created_at_day', ascending=False).rename(columns={'created_at_day':'tcount'})
'''
                created_at_day
created_at_day
Tue                        537
Wed                        515
Thu                        471
Mon                        459
Sat                        427
Sun                        415
Fri                        384
'''
