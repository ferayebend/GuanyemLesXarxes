#!/usr/bin/python
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import requests
from requests_oauthlib import OAuth1
from urlparse import parse_qs
import json
import codecs
from math import ceil
import os.path
import time
import random

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

# Go to http://dev.twitter.com and create an app.
# The consumer key and secret will be generated for you after
CONSUMER_KEY="O3sWz4crU3F3dh0ZUVuQA"
CONSUMER_SECRET="7LazjOzT9XdTYnnDwMNXmguhFwderSu5GEqtwe8ay0"

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
OAUTH_TOKEN="2385331032-NV8uby0kbauYNEoQrCPaMkRQS7mH05Fc6xkgCeM"
OAUTH_TOKEN_SECRET="WqDU4A0RXmb1GfLd6QLLHPEvNIUTa3pA47Jbhud71MYbV"


def setup_oauth():
    """Authorize your app via identifier."""
    # Request token
    oauth = OAuth1(CONSUMER_KEY, client_secret=CONSUMER_SECRET)
    r = requests.post(url=REQUEST_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)

    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]
    
    # Authorize
    authorize_url = AUTHORIZE_URL + resource_owner_key
    print 'Please go here and authorize: ' + authorize_url
    
    verifier = raw_input('Please input the verifier: ')
    oauth = OAuth1(CONSUMER_KEY,
                   client_secret=CONSUMER_SECRET,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=verifier)

    # Finally, Obtain the Access Token
    r = requests.post(url=ACCESS_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)
    token = credentials.get('oauth_token')[0]
    secret = credentials.get('oauth_token_secret')[0]

    return token, secret


def get_oauth():
    oauth = OAuth1(CONSUMER_KEY,
                client_secret=CONSUMER_SECRET,
                resource_owner_key=OAUTH_TOKEN,
                resource_owner_secret=OAUTH_TOKEN_SECRET)
    return oauth

def get_users(filename):
    users = []
    f = open(filename)
    for lines in f:
	users.append(lines.strip())
    return users

def loadData(inputFile):
    data = []
    for line in inputFile:
        if line.startswith("#"):
            continue
        data.append([v for v in line.strip().split()])
    return data

def loadDataS(inputFile,seperator):
    data = []
    for line in inputFile:
        if line.startswith("#"):
            continue
        data.append([v for v in line.strip().split(seperator)])
    return data

def transpose(data):
        return [[data[j][i] for j in range(len(data))] for i in range(len(data[0]))]


def getFollowers(user):
    falovirs = []
    f = open(user+'_falovir.txt')
    for lines in f:
	falovirs.append(lines.strip())
    return falovirs

def get_unique(data):
    result=[]
    result.append(data[0])
    for i in range(len(data)):
        if data[i] in result:
            continue
        else:
                result.append(data[i])
    return result

def getCommonFollowerCount(source_user,target_user):
    '''
    target is the account we are interested in
    '''
    source_followers = get_followers(source_user)
    target_followers = get_followers(target_user)
    source_count = len(source_followers)
    target_count = len(target_followers)
    count = 0
    for f in source_followers:
	if f in target_followers:
	   count += 1
    return count, source_count, float(count)/float(source_count), float(count)/float(target_count)

def getCommonFollowerArrayCount(source_followers,target_followers):
    '''
    target is the account we are interested in
    '''
    source_count = len(source_followers)
    target_count = len(target_followers)
    count = 0
    target_copy = target_followers
    for f in source_followers:
	if f in target_copy:
	   count += 1
	   source_followers.remove(f)
	   #target_copy.remove(f)
	   '''
	   for efficiency the matching elements are taken out
	   if userlists are badly made, the repeating elements will not be noticed
	   '''
    return count, source_count, float(count)/float(source_count), float(count)/float(target_count)

def getOldTweets(filename):
    input_file  = file(filename, "r")
    tweets = []
    for lines in input_file:
	tweets.append(json.loads(lines))
    return tweets

def getOldTweetsID(filename):
    input_file  = file(filename, "r")
    tweetIDs = []
    for lines in input_file:
	tweet = json.loads(lines)
	tweetIDs.append(tweet["id"])
    return tweetIDs

def GrabSearch(hashtag,since):
    #since = -1 #default?
    PROFILE = "https://api.twitter.com/1.1/search/tweets.json?q=%s&max_id=%i&result_type=recent&count=100"%(hashtag,since)
    if not OAUTH_TOKEN:
        token, secret = setup_oauth()
        print "OAUTH_TOKEN: " + token
        print "OAUTH_TOKEN_SECRET: " + secret
        print
    else:
        oauth = get_oauth()
        r = requests.get(url=PROFILE, auth=oauth)
        search= r.json()
	#print taym['statuses']
	return search

def GrabTweets(name):
    PROFILE = "https://api.twitter.com/1.1/statuses/user_timeline.json?include_entities=true&include_rts=true&screen_name=%s"%name
    if not OAUTH_TOKEN:
        token, secret = setup_oauth()
        print "OAUTH_TOKEN: " + token
        print "OAUTH_TOKEN_SECRET: " + secret
        print
    else:
        oauth = get_oauth()
        r = requests.get(url=PROFILE, auth=oauth)
        taym= r.json()
	#print taym['statuses']
	return taym

def GrabFollowers(name, no_followers):
    if no_followers < 5001:
    	PROFILE = "https://api.twitter.com/1.1/followers/ids.json?cursor=-1&screen_name=%s&count=5000"%name
    	if not OAUTH_TOKEN:
           token, secret = setup_oauth()
           print "OAUTH_TOKEN: " + token
           print "OAUTH_TOKEN_SECRET: " + secret
           print
    	else:
           oauth = get_oauth()
           r = requests.get(url=PROFILE, auth=oauth)
	   print r
           followers = r.json()
	   time.sleep(61)
	   return followers['ids']
    elif no_followers > 5000:
	no_cursor = int(ceil(no_followers/5000.))
	followers_rest = no_followers%5000
	followers = []
	next_cursor = -1
	for i in range(no_cursor):
	    if i == no_cursor-1:
	       f_query = followers_rest
	    else:
	       f_query = 5000
    	    PROFILE = "https://api.twitter.com/1.1/followers/ids.json?cursor=%i&screen_name=%s&count=%i"%(next_cursor,name,f_query)
	    print next_cursor
    	    if not OAUTH_TOKEN:
               token, secret = setup_oauth()
               print "OAUTH_TOKEN: " + token
               print "OAUTH_TOKEN_SECRET: " + secret
               print
    	    else:
               oauth = get_oauth()
               r = requests.get(url=PROFILE, auth=oauth)
	       print r
	       next_cursor = r.json()['next_cursor']
	       #print next_cursor
               followers += r.json()['ids']
	       time.sleep(61)
	return followers


def GrabFollowerCount(name):
    PROFILE = "https://api.twitter.com/1.1/statuses/user_timeline.json?include_entities=true&include_rts=false&count=1&screen_name=%s"%name
    if not OAUTH_TOKEN:
        token, secret = setup_oauth()
        print "OAUTH_TOKEN: " + token
        print "OAUTH_TOKEN_SECRET: " + secret
        print
    else:
        oauth = get_oauth()
        r = requests.get(url=PROFILE, auth=oauth)
        taym= r.json()
	no_followers = int(taym[0]['user']['followers_count'])
	print no_followers
	return no_followers

def GrabFriends(name, no_followers):
    if no_followers < 5001:
    	PROFILE = "https://api.twitter.com/1.1/friends/ids.json?cursor=-1&screen_name=%s&count=5000"%name
    	if not OAUTH_TOKEN:
           token, secret = setup_oauth()
           print "OAUTH_TOKEN: " + token
           print "OAUTH_TOKEN_SECRET: " + secret
           print
    	else:
           oauth = get_oauth()
           r = requests.get(url=PROFILE, auth=oauth)
	   print r
           followers = r.json()
	   time.sleep(61)
	   return followers['ids']
    elif no_followers > 5000:
	no_cursor = int(ceil(no_followers/5000.))
	followers_rest = no_followers%5000
	followers = []
	next_cursor = -1
	for i in range(no_cursor):
	    if i == no_cursor-1:
	       f_query = followers_rest
	    else:
	       f_query = 5000
    	    PROFILE = "https://api.twitter.com/1.1/followers/ids.json?cursor=%i&screen_name=%s&count=%i"%(next_cursor,name,f_query)
	    print next_cursor
    	    if not OAUTH_TOKEN:
               token, secret = setup_oauth()
               print "OAUTH_TOKEN: " + token
               print "OAUTH_TOKEN_SECRET: " + secret
               print
    	    else:
               oauth = get_oauth()
               r = requests.get(url=PROFILE, auth=oauth)
	       print r
	       next_cursor = r.json()['next_cursor']
	       #print next_cursor
               followers += r.json()['ids']
	       time.sleep(61)
	return followers

def GrabFriendCount(name):
    PROFILE = "https://api.twitter.com/1.1/statuses/user_timeline.json?include_entities=true&include_rts=false&count=1&screen_name=%s"%name
    if not OAUTH_TOKEN:
        token, secret = setup_oauth()
        print "OAUTH_TOKEN: " + token
        print "OAUTH_TOKEN_SECRET: " + secret
        print
    else:
        oauth = get_oauth()
        r = requests.get(url=PROFILE, auth=oauth)
        taym= r.json()
	no_friends = int(taym[0]['user']['friends_count'])
	print no_friends
	return no_friends

def GrabTweetsExp(name,max_id):
    PROFILE = "https://api.twitter.com/1.1/statuses/user_timeline.json?include_entities=true&include_rts=true&count=200&max_id=%s&screen_name=%s"%(max_id,name)
    if not OAUTH_TOKEN:
        token, secret = setup_oauth()
        print "OAUTH_TOKEN: " + token
        print "OAUTH_TOKEN_SECRET: " + secret
        print
    else:
        oauth = get_oauth()
        r = requests.get(url=PROFILE, auth=oauth)
        taym= r.json()
	#print taym['statuses']
	return taym

def GrabHistory(user):
    '''
    very ugly workaround for grabbing the whole timeline 3200 max 
    '''
    switch = 0
    for i in range(100):#cirkin cozum
      if switch < 2:
	last = os.popen('tail -1 %s_taymlayn.txt'%user).read()
	last_tweet = json.loads(last)
	last_id = str(last_tweet['id'])
	print "%s taymlayninda yeni bir sey var mi?"%user
	taymlayn = GrabTweetsExp(user,last_id)
	filename = '%s_taymlayn.txt'%user
	if os.path.isfile(filename):
 	   OldTweets = getOldTweetsID(filename)
	   #print OldTweets[0]['text']
	   out = open(filename,'a+')
	   for tweet in taymlayn:
		if tweet['id'] in OldTweets:
		  print tweet['id'], ' tibiti dosyada'
		  switch = switch+1
		  continue
		else:
		   #print 'mujde! yeni tibit: '#,tweet['text']
		   switch = 0
		   json.dump(tweet,out)
		   out.write('\n')
	   out.close()
	else:
	   writeTweets(taymlayn,filename)

def GrabUserInfo(user_id):
    PROFILE = "https://api.twitter.com/1.1/users/show.json?user_id=%s&include_entities=false"%user_id
    if not OAUTH_TOKEN:
        token, secret = setup_oauth()
        print "OAUTH_TOKEN: " + token
        print "OAUTH_TOKEN_SECRET: " + secret
        print
    else:
        oauth = get_oauth()
        r = requests.get(url=PROFILE, auth=oauth)
        user = r.json()
	print r
	#print r.json()
	return user


def GetNewTimelines(users):
    for user in users:
	print "%s taymlayninda yeni bir sey var mi?"%user
	taymlayn = GrabTweets(user)
	filename = '%s_taymlayn.txt'%user
	if os.path.isfile(filename):
 	   OldTweets = getOldTweetsID(filename)
	   #print OldTweets[0]['text']
	   out = open(filename,'a+')
	   for tweet in taymlayn:
		if tweet['id'] in OldTweets:
		  print tweet['id'], ' tibiti dosyada'
		  continue
		else:
		   print 'mujde! yeni tibit: '#,tweet['text']
		   json.dump(tweet,out)
		   out.write('\n')
	   out.close()
	else:
	   writeTweets(taymlayn,filename)


def writeTweets(tweets,filename):
    out = codecs.open(filename, encoding='utf-8', mode='w')
    for tweet in tweets:
    	json.dump(tweet,out)
    	out.write('\n')
    out.close()

def GetFollowerCorrelation(target_name,users):
    target_followers = getFollowers(target_name)
    out = codecs.open(target_name+'_comparison.dat', encoding='utf-8', mode='w')
    for user in users:
	source_followers = getFollowers(user)
	common_count, source_count, source_frac, target_frac = getCommonFollowerArrayCount(source_followers,target_followers)
	out_string = '%s\t%i\t%i\t%f\t%f\n'%(user,common_count, source_count, source_frac, target_frac)
	print out_string
	out.write('%s'%out_string)
    out.close()

def GetSearchResults(hashtag):
    #hashtag = 'GuanyemSantAntoni'
    #since = -1 #default

    outname = '%s_search.json'%hashtag
    #if os.path.isfile(outname):
    #	os.popen('rm %s'%outname)
    
    if os.path.isfile(outname):
    	out = codecs.open(outname, encoding='utf-8', mode='a+')
    	finalt = json.loads(os.popen('tail -1 %s'%outname).read())
    	since = finalt['id']
    	print 'starting from %s'%since
    else:
    	out = codecs.open(outname, encoding='utf-8', mode='a+')
	since = -1
	print 'new file'

    search = GrabSearch(hashtag,since)
    try:
	print search['search_metadata']
    except KeyError:
	print search['errors'][0]['message']
	if search['errors'][0]['code'] == 88:
	   print 'waiting...'
	   time.sleep(15*60+1)
    search = GrabSearch(hashtag,since)
    since = search['search_metadata']['max_id']
    for tweet in search['statuses']:
	current_max_date = tweet['created_at']
	current_max_id = tweet['id']
	print current_max_date, tweet['text']
	json.dump(tweet,out)
	out.write('\n')
    out.close()
    print 'compare with', current_max_date, current_max_id

def ReadUserIds(input_file):
    #input_file  = file(filename, "r")
    Ids = []
    for lines in input_file:#memory efficient loop
    	user = json.loads(lines)
	try:
	     user['id']
	except KeyError:
	     print user
	     continue #assuming there is an acceptable error
	Ids.append(str(user['id'])) #conversion to string for getFollowers comparison
    return Ids

if __name__ == "__main__":

    #users = get_users('userlistGuanyem3.txt')
    
    #followers = get_users('guanyem_falovir.txt')
    #OldTweets = getOldTweets('')

    #account_name = 'guanyem'
    #users += [account_name]
    users = ['guanyem']

    #GetFollowerCorrelation(account_name,users)

    '''
    account_name = 'guanyem'
    followers = get_users(account_name + '_falovir.txt')

    if os.path.isfile(account_name+'_follower_data_full.dat'):
	was_open = True
    else:
	was_open = False

    out2 = codecs.open(account_name+'_follower_data_full.dat', encoding='utf-8', mode='a+')
    if was_open:
	recorded_ids = ReadUserIds(out2)
	print len(recorded_ids)
    else:
	recorded_ids = []
    count = 0
    #print 'waiting...'
    #time.sleep(15*60+1)


    for user_id in followers:
	if user_id in recorded_ids:
	   continue
	else:
    	  user_info = GrabUserInfo(user_id)
	  try:
	     print user_info['screen_name']
	  except KeyError:
	     print user_info['errors'][0]['message']
	     if user_info['errors'][0]['code'] == 34 or user_info['errors'][0]['code'] == 63:
		continue
	     elif user_info['errors'][0]['code'] == 88:
	        print 'waiting...'
	        time.sleep(15*60+1)
		user_info = GrabUserInfo(user_id)#not good since still it can 404
	  json.dump(user_info,out2)
	  out2.write('\n')
    out2.close()
    '''

    for user in users:
	print user
    	friends = GrabFriends(user,GrabFriendCount(user))
	filename = '%s_firen.txt'%user
    	out = codecs.open(filename, encoding='utf-8', mode='w')
    	for friend in friends:
    	    out.write('%s\n'%friend)
    	out.close()

    for user in users:
	print user
    	followers = GrabFollowers(user,GrabFollowerCount(user))
	filename = '%s_falovir.txt'%user
    	out = codecs.open(filename, encoding='utf-8', mode='w')
    	for follower in followers:
    	    out.write('%s\n'%follower)
    	out.close()


    


    '''
	try:
	   print tweet['id']
	except KeyError:
	   print tweet['errors'][0]['message']
	   if user_info['errors'][0]['code'] == 88:
	        print 'waiting...'
	        time.sleep(15*60+1)
	print tweet['user']['screen_name']
	print tweet['status']['text']
    	json.dump(tweet,out)
    	out.write('\n')
    out.close()
    '''
