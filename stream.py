#!/usr/bin/python
# -*- encoding: utf-8 -*-
#from tweepy.streaming import StreamListener
#from tweepy import OAuthHandler
#from tweepy import Stream
import tweepy
import json
import codecs
import os
import sys

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

# Go to http://dev.twitter.com and create an app.
# The consumer key and secret will be generated for you after
consumer_key=""
consumer_secret=""

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token=""
access_token_secret=""

@classmethod                    
def parse(cls, api, raw):
        status = cls.first_parse(api, raw)
        setattr(status, 'json', json.dumps(raw))
        return status

tweepy.models.Status.first_parse = tweepy.models.Status.parse
tweepy.models.Status.parse = parse

_dir = os.path.dirname(os.path.abspath(__file__))

class StdOutListener(tweepy.streaming.StreamListener):
    """ A listener handles tweets are the received from the stream.
This is a basic listener that just prints received tweets to stdout.

"""
    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status

class CustomStreamListener(tweepy.StreamListener):
    def on_status(self, status):
	  #if status.lang == "tr":
          print status.user.screen_name
          with codecs.open(os.path.join(_dir, 'tweets.json'), "a", 'utf-8') as textFile:
		print status.text
                textFile.write(status.json)
                textFile.write('\n')

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

class TextOutListener(tweepy.StreamListener):
    def on_data(self, data):
	json_data = json.dumps(data)
        #print json_data['statuses']
        return True

    def on_error(self, status):
        print status


if __name__ == '__main__':
    print "extracting"
    l = CustomStreamListener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    stream = tweepy.Stream(auth, l)
    track = [u'keyword1',u'keyword2']
    stream.filter(track=track)
