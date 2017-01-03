## Twitter Text Message Analysis with NLTK and Pandas
This little project was supposed to be little. So it goes...

This is all of the code that was used to run the analysis at [link here]

###Key files:
*tweet_analyzer.py
--*Holds a class (TextAnalyzer) and code that uses NLTK and Pandas DataFrames to do stuff with the data.
*get_user_tweets.py
--*Supports getting an entire user's timeline of last 3200 tweets. If an existing file is passed in, it will get the oldest tweet from that file and get any tweets made since that file, and then append them. This is a nice feature if you want to continually get tweets from a user on a scheduled job. 
*tweepy.py
--*Simple wrapper that supports authing into Twitter API and making requests to 'search/tweets.json' and 'statuses/user_timeline.json?'
*analysis.py
--*This file contains the code that pulls out the key features of the dataset used in the analysis. It is a mess. 

###Usage
*If you intend on pulling Tweets, you'll need to register an application and get a Consumer Key/Consumer Secret from Twitter. This will be the Client Credentials Authentication method.
