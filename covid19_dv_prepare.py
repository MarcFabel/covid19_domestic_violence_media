#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 14:24:04 2020

@author: marcfabel

Description:
    This program loads the data, generates a workable data set and a figure 
    comparing media coverage in 2020 to preceeding years

Inputs:
    genios_articles_häusliche_Gewalt.csv
    genios_articles_all.csv

Outputs:
    articles_domestic_violence.csv                      workable data-set
    domestic_violence__2020_vs_2015-2019.jpg            figure

"""


# packages
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.dates as mdates

#style.available
style.use('seaborn-darkgrid')
import pandas as pd


# HOME directories
z_media_input =     '/Users/marcfabel/Dropbox/temp/'
z_media_output =    '/Users/marcfabel/Dropbox/temp/'
z_media_figures =   '/Users/marcfabel/Dropbox/temp/'
z_prefix =          'domestic_violence_'





###############################################################################
#           Read in Data
###############################################################################


#generate dfs 
violence = pd.read_csv(z_media_input + 'genios_articles_häusliche_Gewalt.csv', sep=',',
                    names=['date', 'art_violence'], header=0, index_col='date',
                    parse_dates=True, dayfirst=True)


articles = pd.read_csv(z_media_input + 'genios_articles_all.csv', sep=',',
                       names=['date', 'art_all'], header=0,
                       index_col='date', parse_dates=True , dayfirst=True)

articles = articles.join(violence, how='inner')
articles['art_violence_ratio'] = articles['art_violence'] * 1000 / articles['art_all']



# generate dataset
articles_out = articles[['art_violence', 'art_violence_ratio']].copy()
articles_out.rename(columns={'art_violence':'violence_absolute', 'art_violence_ratio':'violence_relative'}, inplace=True)
articles_out.to_csv(z_media_output + 'articles_domestic_violence.csv', sep=';', encoding='UTF-8')


# delete outlier (for graph)
articles.drop(pd.Timestamp('2019-01-01 00:00:00'), inplace=True)


# moving average
articles['art_violence_ratio_ma5'] = articles.art_violence_ratio.rolling(window=5).mean()


# pivot table
temp = articles[['art_violence_ratio', 'art_violence_ratio_ma5']].copy()
temp['year'] 	= temp.index.map(lambda x: x.strftime('%Y'))
temp['month'] 	= temp.index.map(lambda x: x.strftime('%m'))
temp['day'] 	= temp.index.map(lambda x: x.strftime('%d'))
temp.reset_index(inplace=True, drop=False)
temp['date'] = temp['month'] + '.' + temp.day
temp.drop(['month', 'day'], inplace=True, axis='columns')
articles_per_year = temp.pivot_table(index='date', columns='year') 


# DatetimeIndex
articles_per_year['year'] = '2020'
articles_per_year.reset_index(inplace=True, drop=False)

articles_per_year['date'] = pd.to_datetime(articles_per_year[('date','')] +'.'+
                 articles_per_year[('year','')],
                 format='%m.%d.%Y')
articles_per_year.set_index(articles_per_year[('date','')],inplace=True)






###############################################################################
#           Graph
###############################################################################
c_shading = 'darkgreen'
c_opacity = 0.15

fig, ax = plt.subplots()
ax.axvspan(datetime(2020,3,23), datetime(2020,4,30), color=c_shading, alpha=c_opacity)
ax.plot(articles_per_year.loc[:'2020-04'].index.values, articles_per_year.loc[:'2020-04'][('art_violence_ratio_ma5','2015')], color='darkgrey', alpha=0.7, label='2015-2019 smoothed')
ax.plot(articles_per_year.loc[:'2020-04'].index.values, articles_per_year.loc[:'2020-04'][('art_violence_ratio_ma5','2016')], color='darkgrey', alpha=0.7)
ax.plot(articles_per_year.loc[:'2020-04'].index.values, articles_per_year.loc[:'2020-04'][('art_violence_ratio_ma5','2017')], color='darkgrey', alpha=0.7)
ax.plot(articles_per_year.loc[:'2020-04'].index.values, articles_per_year.loc[:'2020-04'][('art_violence_ratio_ma5','2018')], color='darkgrey', alpha=0.7)
ax.plot(articles_per_year.loc[:'2020-04'].index.values, articles_per_year.loc[:'2020-04'][('art_violence_ratio_ma5','2019')], color='darkgrey', alpha=0.7)
ax.plot(articles_per_year.index.values, articles_per_year[('art_violence_ratio','2020')],alpha=0.6, label='2020 unsmoothed', linewidth=1.5)
ax.plot(articles_per_year.index.values, articles_per_year[('art_violence_ratio_ma5','2020')], label='2020 smoothed', linewidth=3.5)

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_minor_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.xaxis.set_minor_formatter(mdates.DateFormatter('\n%Y'))
ax.set(xlabel='Date', ylabel='Number of articles covering domestic violence,\n per 1,000 articles') #xlabel='months',
ax.legend()
plt.savefig(z_media_figures + z_prefix + '_2020_vs_2015-2019.jpg')
