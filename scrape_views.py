##
## python3
## Scrape wikipedia to get number of views.
## author: @kaustubhhiware
##

import requests
import re
import matplotlib.pyplot as plt
import argparse
import copy
import numpy as np
import pandas as pd
import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go
floating_point = '[-+]?[0-9]*\.?[0-9]*'
integer = '[0-9]*'
not_found = 'N/A'
num_seasons = 0

def average_function(l):
    l2 = [i for i in l if i!= '-']
    return sum(l2) / len(l2)


def get_seasons_imdb(url):
    r = requests.get(url)
    start = [m.start() for m in re.finditer('Seasons', r.text)][0]
    start_str = '?season='
    season_start = start + r.text[start:].find(start_str)
    season_end = season_start + r.text[season_start:].find('&ref')
    num = int(r.text[ season_start + len(start_str) : season_end ])
    global num_seasons
    num_seasons = num
    print ('Number of seasons', num_seasons)
    return num_seasons


def get_seasons(table1):
    # season_end = [m.start() for m in re.finditer('</a></td>', table1) ][-1]
    # seasons = table1[season_end - 100: season_end]
    # seasons_ind = [m.start() for m in re.finditer('">', seasons) ][-1]

    num = len( [ m.start() for m in re.finditer('<tr>', table1) ] ) - 1
    # num = int(filter(None, re.findall(integer, seasons[seasons_ind:]))[0])
    global num_seasons
    num_seasons = num
    print( 'Number of seasons', num_seasons)
    return


def wikiscrape(wikiurl, isprint=True, onlySeasons = False):
    # imdb page: http://www.imdb.com/title/tt0369179/
    r = requests.get(wikiurl)
    txt = r.text

    start = [m.start() for m in re.finditer('<table', txt)]
    end = [m.start() for m in re.finditer('/table>', txt)]

    # first table is premier dates. Next 12 are only needed
    # The first table should probably give the number of seasons

    get_seasons( txt[ start[0] : end[0] ] )
    if onlySeasons:
        return
    start = start[1:num_seasons + 1]
    end = end[1:num_seasons + 1]
    all_views = []

    for i in range(num_seasons):
        if isprint:
            print( 'Season ',i+1)
        season = txt[start[i]:end[i]]
        epstart = [m.start() for m in re.finditer('<tr', season)]
        epend = [m.start() for m in re.finditer('tr>', season)]
        season_views = []

        for j in range(1, len(epstart)):
            if isprint:
                print( '\t\tEpisode', j,)
            episode = season[epstart[j]:epend[j]]
            view_start = [m.start() for m in re.finditer('<td', episode)][-1]
            view_end = [m.start() for m in re.finditer('/td>', episode)][-1]
        
            views = episode[view_start:view_end]
            found = re.findall(not_found, views)
            if len(found) == 0:
                episodeviews = '-'
            else:
                numviews = float([_f for _f in re.findall(floating_point, views) if _f][0])
                episodeviews = numviews

            if isprint:
                print( episodeviews)
            season_views.append(episodeviews)

        if isprint:
            print( season_views)
        all_views.append(season_views)


    # for i in range(num_seasons):
    #   print( 'Season ',i)
    #   for each in all_views[i]:
    #       print( each)
    #   print( '\n\n')
    for i in range(num_seasons):
        if isprint:
            print( len(all_views[i]),)

    print( '')

    v, a, avg = [], [], [] # views, average

    for i in range(num_seasons):
        av = average_function(all_views[i])
        season_av = []
        for each in all_views[i]:
            if not isinstance(each, float):
                each = 0
            a.append(float(each)-av)
            v.append(av)
            season_av.append(av)
        avg.append(season_av)

        # for j in range(8):
        #   a.append(0.0-av)
        #   v.append(0)

    # tabprint(a)
    # tabprint(v)

    return all_views, avg


def tabprint(l):
    print( l)
    for season in l:
        for episode in season:
            print( str(episode)+'\t'),
        print( '0\t0\t0\t0\t0\t0\t0\t0\t'),

    print( '\n\n\n')


def imdbscrape(imdburl,decider, isprint=True):
    all_views, avg = [], []

    for i in range(1, num_seasons+1):
        season_views = []
        url = imdburl + 'episodes?season='+str(i)
        r = requests.get(url)
        txt = r.text
        if decider==1:
           if isprint:
              print( 'Season ',i)
        
        end = [m.start() for m in re.finditer('<span class="ipl-rating-star__total-votes">', txt)]
        for j in range(len(end)):
            if decider==1:
                if isprint:
                  print( '\t\tEpisode', j+1,)
            each = end[j]
            episode = txt[each-100:each]
            rating = float([k for k in [_f for _f in re.findall(floating_point, episode) if _f] if k!='-'][0])
            # print( rating)
            if decider==1:
               if isprint:
                print( rating)
            season_views.append(rating)

        if not season_views:
            continue # undeclared seasons

        av = average_function(season_views)
        if decider==1:
            print( '\t\tAverage', av)
        avg.append([av]*len(season_views))
        all_views.append(season_views)

    # tabprint(all_views)
    # tabprint(avg)

    # for each in all_views:
    #     print( len(each),)
    # print( '')
    return all_views, avg

def episode_scrape(show,season_num,episode_num):
    imdburl = get_link(show, ' imdb', 'https://www.imdb.com')
    wikiurl = get_link(show, ' episodes wikipedia', 'https://en.wikipedia.org')
    imdb_rating=[]
    url = imdburl + 'episodes?season='+str(season_num)
    r = requests.get(url)
    txt = r.text
    end = [m.start() for m in re.finditer('<span class="ipl-rating-star__total-votes">', txt)]
    for j in range(len(end)):
        each = end[j]
        episode = txt[each-100:each]
        rating = float([k for k in [_f for _f in re.findall(floating_point, episode) if _f] if k!='-'][0])
        imdb_rating.append(rating)
    season_views,avg=wikiscrape(wikiurl,False)
    print("IMDB Rating :",imdb_rating[episode_num-1])
    #print(season_views)
    print("US Viewers(millions) :",season_views[season_num-1][(episode_num-1)])
    imdburl = get_link(show, ' season '+str(season_num)+' episode '+str(episode_num)+' imdb', 'https://www.imdb.com')   
    print("IMDB Link :",url)
    
def cast_scrape(show):
    wikiurl=get_link(show, 'star cast' , 'https://en.wikipedia.org')
    r = requests.get(wikiurl)
    txt = r.text
    start = [m.start() for m in re.finditer('Starring', txt)]
    txt=txt[start[0]::]
    end = [m.start() for m in re.finditer('/div>', txt)]
    txt=txt[0:end[0]]
    end = [m.start() for m in re.finditer('<li>', txt)]
    txt=txt[end[0]::]
    l=[];
    while(len(txt)>0):
        try:
            end = [m.start() for m in re.finditer('">', txt)]
            txt=txt[end[0]+2::]
            end = [m.start() for m in re.finditer('<', txt)]
            l.append(txt[0:end[0]])
            end = [m.start() for m in re.finditer('<li>', txt)]
            txt=txt[end[0]::]
        except IndexError:
            break
        
    return l
    




def average_plot(views,average,show,decider,loc='lower center'):

    views2, average2 = [], []

    for each in views:
        print( len(each), )
    print( '')
    
    for i in range(len(average)):
        av = average_function(average[i])
        if len(views[i]) > len(average[i]):
            average[i] = average[i] + [av]* ( len(views[i]) - len(average[i]) )

   
    appenditure = min([len(each) for each in views]) + 1
    print(appenditure)
    for each in views:
        views2 += [j if isinstance(j, float) else 0 for j in each] + [0]* int(appenditure / 2)
    for each in average:
        average2 += [j if isinstance(j, float) else 0 for j in each] + [0]* int(appenditure / 2)
    
    x = range( len(views2) )
    print(x)
    q=[]
    for item in range(len(views)+1):
        q.append(item)
    if decider==2:
        plt.plot(x, views2, label='Views')
        plt.plot(x, average2, label='Average')
        plt.legend(loc=loc, ncol=4)
        small = int( min([i for i in views2 if i!=0]) ) - 1
        large = int( max(views2) ) + 1
        plt.ylim(small, large)
        plt.show()
    if decider==1:
        tls.set_credentials_file(username='shalini1', api_key='0duBXtZGI1b2ehhpR8Fe')
        trace0=go.Scatter(x=q,y=views2)
        trace1=go.Scatter(x=q,y=average2)
        data=[]
        data.append(trace0)
        data.append(trace1)
        layout=dict(title="IMDB/views", xaxis=dict(title="Episodes"),yaxis=dict(title="No of Views"))
        fig=dict(data=data,layout=layout)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    

        py.plot(fig, filename=show+'avgchart.png.html')


def barchart(views,show,decider,loc='upper center'):
    maxep = 0
    data=[]
    for i in range(len(views)):
       
        for j in range(len(views[i])):
            episode = views[i][j]
            if not isinstance(episode, float):
                views[i][j] = 0 if j==0 else views[i][j]

        maxep = max(maxep, len(views[i]))
    
    xaxis = range(maxep)
    q=[]
    for item in range(maxep+1):
        q.append(item)
    print(q)
    for i in range(len(views)):
        views[i] += [views[i][-1]]* ( maxep - len(views[i]) )
    if decider==2:
        for i in range(len(views)):
            plt.plot(xaxis, views[i], label=str(i+1))
        plt.legend(loc=loc, ncol = 4)
        plt.show()

    if decider==1:
        tls.set_credentials_file(username='shalini1', api_key='0duBXtZGI1b2ehhpR8Fe')
        for i in range(len(views)):
            trace0 = go.Bar(x=q, y=views[i])
            trace1 = go.Scatter(x=q, y=views[i])
            layout=dict(title="IMDB/views", xaxis=dict(title="Episodes"),yaxis=dict(title="No of Views"))
            data.append(trace0)
            data.append(trace1)
        fig=dict(data=data,layout=layout)
        py.plot(fig,filename=show+'barchart.png.html')
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   jk knn kl̥



     
























