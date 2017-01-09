## Twitter Tweet Analysis with NLTK and Pandas
This little project was supposed to be little. So it goes... I initially set out to figure out what features made up Donald J. Trump's tweets. You can do that now with any user's timeline with the code in this repo.

This is all of the code that was used to run the analysis written up [here](https://sweet-as-tandy.com/2017/01/04/what-donald-trump-is-tweeting-analyzing-tweets-with-nltk-and-pandas/).

###Key files:
* tweet_analyzer.py
  * Holds a class (TextAnalyzer) and code that uses NLTK and Pandas DataFrames to do stuff with the data.
* get_user_tweets.py
  * Supports getting an entire user's timeline of last 3200 tweets. If an existing file is passed in, it will get the oldest tweet from that file and get any tweets made since that file, and then append them. This is a nice feature if you want to continually get tweets from a user on a scheduled job. 
* tweepy.py
  * Simple wrapper that supports authing into Twitter API and making requests to 'search/tweets.json' and 'statuses/user_timeline.json?'
* analysis.py
  * This file contains the code that pulls out the key features of the dataset used in the analysis. It is a mess. 

###Usage
* If you intend on pulling Tweets, you'll need to register an application and get a Consumer Key/Consumer Secret from Twitter. This will be the Client Credentials Authentication method.
* Update your config.json file with the new credentials and rename it to config.json instead of config.json.sample.
* Pull some tweets done for a a user's timeline
  * For the First run: python get_user_timeline.py --user_handle realDonaldTrump
  * For runs afterward, like if you wanted to run this on a scheduled job: python get_user_timeline.py --user_handle realDonaldTrump --existing_file --existing_file realDonaldTrump_master_tweet_list.json . This command will append any newly found tweets to the file.
* Use text_analyzer.py to create a dataframe. You can check out example code in analysis.py
