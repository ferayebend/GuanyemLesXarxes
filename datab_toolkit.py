#!/usr/bin/python
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from pylab import *

import json
import codecs
import pymongo
import time
import sys
import os
import re

def getOldTweets(filename):
    input_file  = file(filename, "r")
    tweets = []
    for lines in input_file:
	tweets.append(json.loads(lines))
    return tweets

def get_users(filename):
    users = []
    f = open(filename)
    for lines in f:
	users.append(lines.strip())
    return users

def stdoutStatus(jsonarray):
    for tweet in jsonarray:
	print tweet['text']

def inputDb(collection_name, filename):
    '''
    init db
    '''
    input_file  = file(filename, "r")

    for lines in input_file:#memory efficient loop
    	data ={}
    	tweet = json.loads(lines)
        data['created_at'] = time.mktime(time.strptime(tweet['created_at'],"%a %b %d %H:%M:%S +0000 %Y"))
    	data['user_name'] = tweet['user']['screen_name']
	data['user_id']   = tweet['user']['id_str']
    	data['_id'] = tweet['id']
	data['lang'] = tweet['lang']
	data['text'] = tweet['text']
	#print tweet['user']['screen_name']
	#print tweet['entities']['hashtags']
	data['hashtags'] = tweet['entities']['hashtags']
	if collection_name.find_one({'_id':data['_id']}):
	   continue
	else:
	   collection_name.insert(data) #takes care of duplicates 
    #input_file.close()  
    #posts.remove({u'lang':{'$nin':[u'tr']}}) #remove non turkish 

def inputUser(collection_name, filename):
    '''
    init db
    '''
    input_file  = file(filename, "r")

    for lines in input_file:#memory efficient loop
    	data ={}
    	user = json.loads(lines)
	try:
	     user['id']
	except KeyError:
	     print user
	     continue #assuming there is an acceptable error
        data['created_at'] = time.mktime(time.strptime(user['created_at'],"%a %b %d %H:%M:%S +0000 %Y"))
    	data['user_name'] = user['screen_name']
	#data['user_id']   = tweet['user']['id_str']
    	data['_id'] = user['id']
	data['listed_count'] = user['listed_count']
	data['description'] = user['description']
        data['followers_count'] =  user['followers_count']
        data['friends_count'] = user['friends_count']
	data['statuses_count'] = user['statuses_count']
	if collection_name.find_one({'_id':data['_id']}):
	   continue
	else:
	   collection_name.insert(data) #takes care of duplicates 
    input_file.close()  
    #posts.remove({u'lang':{'$nin':[u'tr']}}) #remove non turkish 


def KeywordFilter(InCollection,regex,sortindex,searchindex):
    histogram_array=[]
    for entry in InCollection.find({searchindex:  {'$in':[re.compile('%s'%(regex))]} }):
        histogram_array.append(entry[sortindex])#in seconds
    return histogram_array

def KeywordFilterSimple(InCollection,regex,sortindex,searchindex):
    histogram_array=[]
    for entry in InCollection.find({searchindex:  {'$in':[regex]} }):
        histogram_array.append(entry[sortindex])#in seconds
    return histogram_array

def KeywordComparison(posts):
    posts.create_index([("created_at", pymongo.ASCENDING)])
    OCdates = []
    RTdates = []
    for post in posts.find().sort([("created_at", pymongo.ASCENDING)]):
        RTdates.append(post['created_at'])#in seconds
    for post in posts.find({'text':  {'$nin':[re.compile('RT @')]} }).sort([("created_at", pymongo.ASCENDING)]):
        OCdates.append(post['created_at'])#in seconds
    mindate = min(min(RTdates),min(OCdates))#in UTC seconds
    maxdate = max(max(RTdates),max(OCdates))#in UTC seconds

    nRTdates = (array(RTdates)-array(mindate))/array(3600.)#convert to hours
    nOCdates = (array(OCdates)-array(mindate))/array(3600.)#convert to hours
    nmindate = min(min(nRTdates),min(nOCdates))#
    nmaxdate = max(max(nRTdates),max(nOCdates))

    #my_bin = linspace(mindate,maxdate,200)
    my_bin = linspace(nmindate,nmaxdate,200)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    nRT, bins, patch = ax.hist(nRTdates, bins=my_bin)
    #nOC, bins, patch = ax.hist(nOCdates, bins=my_bin)
    #ax.xaxis.set_minor_locator(MultipleLocator(3600))
    #ax.xaxis.set_major_locator(MultipleLocator(12*3600))

    '''
    comparison keyword
    '''
    polis = 'polis*'
    saldiri = 'sald?r*'
    pdates = KeywordFilter(posts,polis,'created_at','text')
    npdates = (array(pdates)-array(mindate))/array(3600.)
    np, bins, patch = ax.hist(npdates, bins=my_bin)
    print len(list(np))

    start_time_formatted = time.strftime("%d %b %Y %H:%M:%S +0000",time.gmtime(mindate+2*3600))#türkiye saati
    print max(list(nRT))
    ax.text(nmindate,max(list(nRT)),start_time_formatted)
    ylabel(r"birim zaman basina twit sayisi")
    xlabel(r'ilk twitten itibaren gecen zaman')
    show()

def KeywordComparison(posts,start_time,end_time,binsize,keywords):
    posts.create_index([("created_at", pymongo.ASCENDING)])
    RTdates = []
    for post in posts.find({"created_at": {"$gte": start_time, "$lte": end_time}}).sort([("created_at", pymongo.ASCENDING)]):
        RTdates.append(post['created_at'])#in seconds
    mindate = min(RTdates)#in UTC seconds
    maxdate = max(RTdates)#in UTC seconds
    print 'mindate =',mindate

    nRTdates = (array(RTdates)-array(mindate))/array(60.)#convert to minutes?
    nmindate = min(nRTdates)#
    nmaxdate = max(nRTdates)

    #my_bin = linspace(mindate,maxdate,200)
    #my_bin = linspace(nmindate,nmaxdate,20)
    #binsize = 2
    my_bin = arange(nmindate,nmaxdate+binsize,binsize)
    

    fig = plt.figure()
    ax = fig.add_subplot(111)
    nRT, bins, patch = ax.hist(nRTdates, bins=my_bin)
    clf()
    #nOC, bins, patch = ax.hist(nOCdates, bins=my_bin)
    #ax.xaxis.set_minor_locator(MultipleLocator(3600))
    #ax.xaxis.set_major_locator(MultipleLocator(12*3600))


    print len(my_bin[1:]), len(nRT)

    '''
    comparison keyword
    '''
    nps = []
    #keywords = ['gcalvetbarot','Camacho','herrerajoan','Albert_Rivera','HiginiaRoig']
    for key in keywords:
        keydates = KeywordFilterSimple(posts,key,'created_at','text')
        nkeydates = (array(keydates)-array(mindate))/array(60.)
        np, bins, patch = hist(nkeydates, bins=my_bin)
	nps.append(np)
	clf()

    plot(my_bin[1:]-array(binsize/2.),nRT,'ro-', linewidth = 2)
    for h in nps:
	plot(my_bin[1:]-array(binsize/2.),h,'o-', linewidth = 2)

    #legend(handles=keywords)

    start_time_formatted = time.strftime("%d %b %Y %H:%M:%S +0000",time.gmtime(mindate+2*3600))#türkiye saati
    print max(list(nRT))
    ax.text(nmindate,max(list(nRT)),start_time_formatted)
    ylabel(r"birim zaman basina twit sayisi")
    xlabel(r'ilk twitten itibaren gecen zaman')

def Timeline(posts,start_time,end_time,binsize):
    posts.create_index([("created_at", pymongo.ASCENDING)])
    RTdates = []
    for post in posts.find({"created_at": {"$gte": start_time,"$lte": end_time}}).sort([("created_at", pymongo.ASCENDING)]):
        RTdates.append(post['created_at'])#in seconds
    mindate = min(RTdates)#in UTC seconds
    maxdate = max(RTdates)#in UTC seconds
    print 'mindate =',mindate

    nRTdates = (array(RTdates)-array(mindate))/array(60.)#convert to minutes?
    nmindate = min(nRTdates)#
    nmaxdate = max(nRTdates)

    #my_bin = linspace(mindate,maxdate,200)
    #my_bin = linspace(nmindate,nmaxdate,20)
    #binsize = 2
    my_bin = arange(nmindate,nmaxdate+binsize,binsize)
    

    fig = plt.figure()
    ax = fig.add_subplot(111)
    nRT, bins, patch = ax.hist(nRTdates, bins=my_bin)
    clf()
    #nOC, bins, patch = ax.hist(nOCdates, bins=my_bin)
    #ax.xaxis.set_minor_locator(MultipleLocator(3600))
    #ax.xaxis.set_major_locator(MultipleLocator(12*3600))
    print len(my_bin[1:]), len(nRT)
    plot(my_bin[1:]-array(binsize/2.),nRT,'ro-', linewidth = 2)

    start_time_formatted = time.strftime("%d %b %Y %H:%M:%S",time.gmtime(mindate+4*3600.))#ispanya saati
    print max(list(nRT))
    #text(nmindate,1.15*max(list(nRT)),start_time_formatted)
    figtext(0.13,0.91,start_time_formatted, horizontalalignment='left')

    v = axis()
    #ylabel(r"birim zaman basina twit sayisi")
    #xlabel(r'ilk twitten itibaren gecen zaman')
    ylabel(r"Quantitat dels tuits per %2.1f minuts"%binsize)
    xlabel(r'Temps a partir del primer tuit (mins)')
    #savefig('frequencia231114.png')
    #savefig('frequencia300914.png')
    return max(nRT), min(nRT), mindate+4*3600., maxdate

def VerticalLine(times, mintime, maxtweet):
    #plot([(time-mintime)/60.,(time-mintime)/60.],[0.6*maxtweet,0.9*maxtweet],'k-',linewidth = 2)
    #print (time-mintime)/60.
    for t in times:
        time_formatted = time.strftime("%H:%M",time.gmtime(mintime+t*60.))#ispanya saati
        print t, time_formatted
        plot([t,t],[0.2*maxtweet,0.55*maxtweet],'k-',linewidth = 2)
	text(t,3,time_formatted,horizontalalignment='center', verticalalignment='bottom', rotation='vertical')


def WOReTweets(posts,since,reftime,binsize, filename):
    posts.create_index([("created_at", pymongo.ASCENDING)])
    RTdates = []
    for post in posts.find({"created_at": {"$gte": since}}).sort([("created_at", pymongo.ASCENDING)]):
        RTdates.append(post['created_at'])#in seconds
    mindate = min(RTdates)
    filtered = posts.find({"created_at": {"$gte": mindate+(reftime-binsize/2.)*60.,"$lte": mindate+(reftime+binsize/2.)*60.}})
    untw = []
    counts = []
    for post in filtered:
	if post['text'] in untw:
	   counts[untw.index(post['text'])] += 1
	else:
	   untw.append(post['text'])
	   counts.append(1)
    unique_tweets = [(untw[i],counts[i]) for i in range((len(counts)))]
    sorted_rts = sorted(unique_tweets, key = lambda a: a[1], reverse = True)
    outname = '%s_rts.dat'%filename
    out = codecs.open(outname, encoding='utf-8', mode='a+')
    out.write('#at %3.1f: %i\n'%(reftime,filtered.count()))
    for i in range(3):#assuming there are more than 3 tweets in the chunk
    	out.write('%i, %s\n'%(sorted_rts[i][1],sorted_rts[i][0]))
    out.close()
    #for i in range(len(untw)):
    #	print counts[i], untw[i]


def WOTweets(posts,since,reftime,binsize,filename):
    posts.create_index([("created_at", pymongo.ASCENDING)])
    RTdates = []
    for post in posts.find({"created_at": {"$gte": since}}).sort([("created_at", pymongo.ASCENDING)]):
        RTdates.append(post['created_at'])#in seconds
    mindate = min(RTdates)
    filtered = posts.find({"created_at": {"$gte": mindate+(reftime-binsize/2.)*60.,"$lte": mindate+(reftime+binsize/2.)*60.}})
    outname = '%s_tw.dat'%filename
    out = codecs.open(outname, encoding='utf-8', mode='a+')
    out.write('#at %3.1f: %i\n'%(reftime,filtered.count()))
    for post in filtered:
    	out.write('%s\n'%(post['text']))
    out.close()

def UserContributions(posts,filename):
    '''
	compiles the contribution of the users within a given 
    '''
    unUs = []
    counts = []
    for post in posts.find():
	if post['user_name'] in unUs:
	   counts[unUs.index(post['user_name'])] += 1
	else:
	   unUs.append(post['user_name'])
	   counts.append(1)
    unique_users = [(unUs[i],counts[i]) for i in range((len(counts)))]
    sorted_users = sorted(unique_users, key = lambda a: a[1], reverse = True)
    outname = '%s_user_statistics.dat'%filename
    if os.path.isfile(outname):
	os.popen('rm %s'%outname)
    out = codecs.open(outname, encoding='utf-8', mode='a+')
    #out.write('#at %3.1f: %i\n'%(reftime,filtered.count()))
    for i in range(len(sorted_users)):#assuming there are more than 3 tweets in the chunk
    	out.write('%i, %s\n'%(sorted_users[i][1],sorted_users[i][0]))
    out.close()

def clean(word):
    newword = word.replace(',','').replace(':','').replace('…','').replace('"','').replace('.','').replace(')','').replace('(','').replace('!','').replace('?','')
    return newword

def WordFrequency(posts,filterWords,filename):
    '''
	used for creating Word clouds
	output can be inputted into http://www.wordle.net/advanced
    '''
    unWords = []
    counts = []
    for post in posts.find():
	postWords = post['text'].split()
	for postWord in postWords:
	   cleanPostWord = clean(postWord)
	   if ('http' in cleanPostWord) or (cleanPostWord in filterWords):
	      continue
	   elif cleanPostWord in unWords:
	      counts[unWords.index(cleanPostWord)] += 1   
	   else:
	      unWords.append(cleanPostWord)
	      counts.append(1)
    unique_words = [(unWords[i],counts[i]) for i in range((len(counts)))]
    sorted_words = sorted(unique_words, key = lambda a: a[1], reverse = True)
    outname = '%s_word_frequency.dat'%filename
    if os.path.isfile(outname):
	os.popen('rm %s'%outname)
    out = codecs.open(outname, encoding='utf-8', mode='a+')
    #out.write('#at %3.1f: %i\n'%(reftime,filtered.count()))
    for i in range(len(sorted_words)):#assuming there are more than 3 tweets in the chunk
    	out.write('%s: %i\n'%(sorted_words[i][0],sorted_words[i][1]))
	#out.write('%s\n'%sorted_words[i][0])
    out.close()

def PlotTweetFrequency(binsize,times, keywords):
    '''
	NOT WORKING (well)
	binsize: in minutes
	times: handpicked array of interesting times (e.g. peaks)
	keywords: array of strings (broken due since KeywordComparison not working)
    '''

    since = time.mktime(time.strptime('14 Nov 2014 07:00:00 +0000',"%d %b %Y %H:%M:%S +0000"))
    until = time.mktime(time.strptime('20 Nov 2014 15:20:00 +0000',"%d %b %Y %H:%M:%S +0000"))

    #print since, until
    binsize = 4
    maxtweets, mintweets, mintime, maxtime = Timeline(posts,since,until,binsize)
    #text(0.9*(maxtime-mintime)/60,maxtweets,'#pujol324',ha='right')
    #figtext(0.88,0.85,'#pujol324',ha='right',size =15)

    #times = [117.0,127, 137.0,145.0, 159.0, 165.0,181.0, 191.,197.]
    #times = [127.0,165.0,197.] #300914
    #times = [74.8]#,157.0,176.0,189.0,229.0] #051014
    #VerticalLine(times, mintime, maxtweets)

    KeywordComparison(posts,since, until,binsize, keywords)

    #savefig('frequencia_noucodietic02.png')
    show()

def FollowerOps(users):
    '''
    	followback algortihm:
	gets the twitters user that are in the database 
	(which have interacted with the target account through mentions of RTs)
	checks whether they are friends of followers of the target account
	if not, compiles a list
    ''' 

    #get follower list
    followerIds = []
    for user in users.find():
	followerIds.append(str(user['_id']))

    #get friends list
    friendIds = get_users('%s_firen.txt'%user_name)

    #pull unique elements from the database
    uniqueIds = {}
    posts.find().sort([("created_at", pymongo.ASCENDING)])
    for post in posts.find({"created_at": {"$gte": since,"$lte":until}}):
	if post['user_id'] in uniqueIds:
	   continue
	elif post['user_name'] == user_name:
	   continue
	else:
	   #uniqueIds.append({post['user_id']: post['user_name']})
	   uniqueIds[post['user_id']] =  post['user_name']
    print 'unique ids in this set of posts:',len(uniqueIds)


    #get target group
    targetUsers = []
    for userId in uniqueIds.keys():
	if userId in followerIds:
	   continue
	elif userId in friendIds:
	   continue
	else:
	   targetUsers.append(userId)
    print 'target ids in this set of posts:',len(targetUsers)
    
    out = codecs.open('target.dat', encoding='utf-8', mode='w')
    for ids in targetUsers:
	out.write('%s\t%s\n'%(ids,uniqueIds[ids]))
    out.close()

if __name__ == '__main__':
    client = pymongo.MongoClient()

    db = client['guanyem-db']
    posts = db.posts #this is a collection

    #inputDb(posts,'guanyem_131114.json')

    '''
	write a followers collection and a friends collection
    '''

    user_name = 'guanyem'
    users = db.users
    #inputUser(users,'guanyem_follower_data_full.dat')

    #UserContributions(posts,'noucodietic')

    #FilterWords  = [lines.replace('\n','') for lines in codecs.open('filterWords.dat', encoding='utf-8', mode='r')]
    #WordFrequency(posts,FilterWords,'noucodietic02')
