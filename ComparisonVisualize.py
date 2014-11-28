#!/usr/bin/python
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from pylab import *
from math import *
import os

'''
takes the output of GetFollowerCorrelation and GrabFollowers 
in api_toolkit.py and plots a figure
'''

def loadData(inputFile):
    data = []
    for line in inputFile:
        if line.startswith("#"):
            continue
        data.append([v for v in line.strip().split()])
    return data

def FloatizeMatrixIndicies(data,indicies):
    new_data = []
    for line in data:
	new_line = []
	for i in range(len(line)):
	    if i in indicies:
		new_line.append(float(line[i]))
	    else:
		new_line.append(line[i])
	new_data.append(new_line)
    return new_data

def transpose(data):
        return [[data[j][i] for j in range(len(data))] for i in range(len(data[0]))]

def floatizeList(ls):
    return [float(l) for l in ls]

def refHistogram(target_name):
    in_data = FloatizeMatrixIndicies(loadData(open(target_name+'_comparison.dat')),[1,2,3,4])
    data = transpose(sorted(in_data, key = lambda a1: a1[4]))
    follower_target = float(os.popen('wc %s_follower.txt'%(target_name)).read().split()[0])#assumes both files are consistent in numbers
    size_target = sqrt(follower_target)
    #print data[0]
    fraction_target = array(floatizeList(data[4]))*100
    fraction_source = array(floatizeList(data[3]))*100
    aralik = 6
    text_margin = 4
    indicies = linspace(1,aralik*len(data[0])+1,len(data[0]))
    size_source = [sqrt(float(el)) for el in data[2]]#area will give the size
    #barh(indicies,fraction_target,align='center',color='red', height=aralik*0.4)
    #scatter(size_source*array([0]),indicies, s = size_source, alpha=0.5)
    for i in range(len(data[0])):
    	barh([indicies[i]],[fraction_target[i]],align='center',color='red', height=aralik*0.4, zorder = 0)
    	scatter([0],[indicies[i]], s = size_source[i], alpha=0.5, zorder=1)
    	text(-1*text_margin,indicies[i],data[0][i],ha='right',va='center')
	text(fraction_target[i]+2,indicies[i],r'%3.1f'%fraction_target[i],va='center')
	text(-30,indicies[i],r'%3.1f'%fraction_source[i],ha='right',va='center')
    '''
    labels and explanations
    '''
    axis([-35,max(fraction_target)+4,-2,max(indicies)+4])
    v = axis()
    ref_ind = -1
    scatter([v[1]-aralik],[v[2]+aralik],s=size_target,alpha=0.5)
    scatter([v[1]-aralik],[v[2]+aralik],s=size_source[ref_ind],alpha=0.5)
    text(v[1]-aralik-text_margin,v[2]+3*aralik,'area :',ha='right',va='center')
    text(v[1]-aralik-text_margin,v[2]+2*aralik,'%s vs %s'%(target_name, data[0][ref_ind]),ha='right',va='center')
    text(v[1]-aralik-text_margin,v[2]+aralik,'%i vs %i followers'%(int(follower_target),int(data[2][ref_ind])),ha='right',va='center')
    text(v[0]-aralik,v[3]-aralik,'el porcentaje de los seguidores que siguen tambien %s'%target_name,rotation=90,ha='left')
    text(v[1],v[3],'el porcentaje de los seguidores de %s que tambien siguen la cuenta en y'%target_name,ha='right',va='bottom')
    #text(v[0]-aralik,v[3]-aralik,'percentage of followers also following %s'%target_name,rotation=90,ha='left')
    #text(v[1],v[3],'percentage of %s followers also following account in y'%target_name,ha='right',va='bottom')
    axis('off')
    #ylabel('percentage of followers also following %s'%target_name)
    savefig('compare02_es.png')
    show()

def stdoutFollowerData(target):
    data = FloatizeMatrixIndicies(loadData(open(target_name+'_follower_data.dat')),[2,3,4,5])
    data_sorted = sorted(data, key = lambda a1: a1[2], reverse=True)
    print 'screen_name,followers,influence'
    print ',,no_followers/no_friends'
    for dat in data_sorted:
	if dat[2] > 1000 :
	  print '%s,%i,%6.3f'%(dat[1], int(dat[2]), dat[3])

if __name__ == '__main__':
    target_name = 'guanyem'

    refHistogram(target_name)
