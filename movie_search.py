#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 13:36:09 2021

@author: sako
"""

from tqdm import tqdm
import pandas as pd
import difflib

# importing the module
import imdb

# creating instance of IMDb
ia = imdb.IMDb()
  
# movie name
names = pd.read_csv('/home/sako/Data science lessons/My  projects/movies_imdbpy/movies_list.csv',index_col = 0,header=0)
print(names)

names = pd.DataFrame(data = ['Drunk Punch Love'] , columns = ['movies']  )
print(names)

#ranks of actors
ranks = 3

#%% ___________ Get main actor ______________

def main_actors(cast):
    actors = [] 
    for i in range(len(cast)):
        actors.append(cast[i].data['name'])        
    return actors


#%% _______ RUN query _____________

# searchning the movies and apply metadata filter
df_movies = pd.DataFrame()

for idx,name in enumerate(tqdm(names.movies,total=len(names))):
    
    #search for movie based on name
    movie_results = ia.search_movie(name)    
    
    #generate metadata
    df_movie = pd.DataFrame()
    for item in movie_results:
        df_movie  = df_movie.append(pd.DataFrame(data = [[item]+item.values()], columns = ['data']+item.keys()))

    #remove outliers by title 
    nearest = difflib.get_close_matches(name, df_movie['title'])
    df_movie = df_movie.query("title in @nearest")

    #craete common index and append
    df_movie['searcher'] = df_movie.shape[0]*[name]
    df_movies = df_movies.append(df_movie)
    
#reindex and filter out non-movies    
df_movies.index = range(df_movies.shape[0])
df_movies = df_movies[df_movies['kind'].str.contains('movie')]


    
#%% ________ Extract additional info ____________ 

data = pd.DataFrame() 

for movie in tqdm(df_movies.itertuples(),total=len(df_movies)):    
    
    #extract details of movies based on filtered meta-data    
    movie_data_json = ia.get_movie(movie.data.getID()).data    

    #get cast name list and sort alphabetically 
    try:
        all_actors = main_actors(movie_data_json['cast'])
        movie_data_json['main_actors'] = all_actors[0 : ranks+1] 
        movie_data_json['all_actors_sorted'] = sorted(all_actors)
        
    except: 
        movie_data_json['main_actors'] = ''    
        
    movie_data = pd.json_normalize(movie_data_json)
    movie_data['searcher'] = [movie.searcher] 
    data = data.append(movie_data)    

data.index = range(data.shape[0])
data.votes.fillna(1,inplace=True)

#%%

#filter coloumns
select = ['searcher','year','title','localized title','main_actors','all_actors_sorted', 'genres', 'runtimes','rating', 'votes','kind','imdbID']
data_Clean = data[select]
#data_final = pd.merge(names,data_Clean,left_on='movies',right_on='searcher',how='outer')[['movies','searcher','year','title','localized title','main_actors','all_actors_sorted', 'genres', 'runtimes','rating', 'votes','kind','imdbID']]

#data_final.to_csv('/home/sako/Data science lessons/My  projects/movies_imdbpy/movies_list_results.csv')  
  
#%%

#get populat ones
idx = data_Clean.groupby(['searcher'])['votes'].transform(max) == data_Clean['votes']
data_pop = data_Clean[idx]
data_pop = pd.merge(names,data_pop,left_on='movies',right_on='searcher',how='outer')



