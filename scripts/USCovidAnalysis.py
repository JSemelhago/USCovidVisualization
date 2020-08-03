#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import plotly.express as px
import json
import requests
import csv
import re
import shutil
import os
import sys
from urllib.request import urlopen

#Flush output directory
shutil.rmtree('../output/')
try:
    os.mkdir('../output')
    os.mkdir('../shapefiles')
except OSError:
    print('Output directory creation failed')
else:
    print('Successfully created output directory')

#Test internet connection
try:
    response = urlopen('https://www.google.com/', timeout=10)
except Exception as e:
    print('There was an error accessing the Internet: %s' %e)
    sys.exit()
else:
    print('Successfully connected to the Internet')


link = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_confirmed_usafacts.csv'

#Retrieve updated csv from USA Factbook
with requests.Session() as session:
    download = session.get(link)
    decodedContent = download.content.decode('utf-8-sig')

    content = csv.reader(decodedContent.splitlines(), delimiter = ',')
    coviddf = pd.DataFrame(content)

if coviddf.empty:
    print('There was an error in downloading the data!')
else:
    print('Successfully downloaded Covid data')



#Get rid of unnecessary first few rows
coviddf.columns = coviddf.iloc[0]
coviddf = coviddf[1:]
coviddf['countyFIPS'] = coviddf['countyFIPS'].astype(int)


unprocessed_coviddf = coviddf.copy(deep=False)


#Get rid of statewide unallocated
coviddf = coviddf[coviddf['countyFIPS']!=0]

#Drop all the dates except the newest one
coviddf.drop(coviddf.iloc[:,3:-1],axis=1,inplace=True)


#Get population data
popdf = pd.read_csv('../data/us_popdata_2019.csv')

if popdf.empty:
    print('There was an error reading the population data!')
else:
    print('Successfully read the population data')

#Condense pop. data
popdf = popdf.loc[:,['STATE','COUNTY','CTYNAME','POPESTIMATE2019']]
#Add leading zeros
popdf['COUNTY'] = popdf['COUNTY'].apply(lambda x: str(x).zfill(3))


#Combine state and county to fips (county fips must match in both datasets)
popdf.rename(columns={'COUNTY':'fips'},inplace=True)
popdf['fips'] = popdf['STATE'].apply(lambda x: str(x))+popdf['fips']
popdf.drop(labels=['STATE'],axis=1,inplace=True)
popdf['fips']=pd.to_numeric(popdf['fips'])

#Get rid of state levels
popdf = popdf.loc[popdf['fips']%1000!=0]



#Get difference of counties
print('This is the list of different counties from the Covid and population data ',list(set(coviddf['countyFIPS'])-set(popdf['fips'])))


#Kusilvak and Wade Hampton are the same, get rid of Kusilvak to match GeoJSON
coviddf = coviddf.loc[coviddf['County Name']!='Kusilvak Census Area']


#Oglala Lakota County in the GeoJSON file is Shannon County (name was changed in 2015)
coviddf.loc[coviddf['County Name']=='Oglala Lakota County', 'countyFIPS'] = 46113
coviddf.loc[coviddf['countyFIPS']==46113, 'County Name'] = 'Shannon County'

print('Kusilvak Census Area and Oglala Lakota County have been changed in accordance with GeoJSON')

popdf.rename(columns={'fips':'countyFIPS'},inplace=True)


#Merge population/Covid data
original_columns = coviddf.shape[1]
coviddf = pd.merge(left = coviddf, right = popdf, on = 'countyFIPS', how = 'outer')
coviddf = coviddf.dropna()

if coviddf.shape[1] < original_columns:
    print('There was an error in merging the population and Covid dataframes!')
else:
    print('Successfully merged the population and Covid dataframes')


#Drop counties that are not officially recognized (Princess Cruise Ship, NYC, etc.)
coviddf = coviddf[coviddf['CTYNAME'].notna()]


#Drop unneeded columns
coviddf.drop(labels=['CTYNAME','State'], axis=1, inplace=True,)


#Rename most recent date column and convert columns to int
date = str(coviddf.columns.to_list()[-2])
coviddf.rename(columns={coviddf.columns[-2]:'cases'},inplace=True)
coviddf['cases'] = coviddf['cases'].astype('int64')
coviddf['POPESTIMATE2019'] = coviddf['POPESTIMATE2019'].astype('int64')


#Add cases per 100k
coviddf['cases_per_100k'] = coviddf['cases'].div(coviddf['POPESTIMATE2019']).mul(100000)
coviddf['cases_per_100k'] = coviddf['cases_per_100k'].astype('float64')

if coviddf['cases_per_100k'].isna().sum()>0:
    print('There was an error in calculating the cases_per_100k column!')
else:
    print('Successfully calculated the cases_per_100k column')


#Format to GeoJSON id
coviddf['countyFIPS']="0500000US"+coviddf['countyFIPS'].apply(lambda x: str(x).zfill(5))
coviddf['countyFIPS'] = coviddf['countyFIPS'].astype('string')


#Rename for a better naming system
coviddf.rename(columns={'countyFIPS':'county_fips','County Name':'county_name','POPESTIMATE2019':'population'}, inplace=True)
coviddf['county_name'] = coviddf['county_name'].astype('string')


#Format date for file output name
date_components = re.split('(\W)', date)
for i in np.arange(0, len(date_components), 2):
    date_components[i] = date_components[i].zfill(2)
date_components = ['_' if x=='/' else x for x in date_components]
date = ''.join(date_components)


#Export processed and unprocessed dataframes
coviddf.to_csv('../output/Processed - USCovidbyCounty_'+date+'.csv',index=False)
unprocessed_coviddf.to_csv('../output/Unprocessed - USCovidbyCounty_'+date+'.csv',index=False)

if os.listdir('../output/') == []:
    print('There was an error in outputting the data files!')
else:
    print('Successfully outputted the processed data files')


#Create csvt file for QGIS import
df_types = []

for i in list(coviddf.dtypes):
    df_types.append(str(i))

dtype_map = {'string':'"String"',
             'int64':'"Integer"',
             'float64':'"Real"'}

df_types = list(map(dtype_map.get, df_types))

csvt_df = pd.DataFrame(pd.Series(df_types)).T
csvt_df.to_csv('../output/Processed - USCovidbyCounty_'+date+'.csvt', index=False, header=False, quoting=csv.QUOTE_NONE)

if not os.path.exists('../output/Processed - USCovidbyCounty_'+date+'.csvt'):
    print('There was an error in outputting the csvt file')
else:
    print('Successfully outputted the csvt file')


#Export choropleth map

uscounties = '../data/uscounties.json'

usmap = json.load(open(uscounties))

fig=px.choropleth_mapbox(data_frame=coviddf,
                    geojson=usmap,
                    featureidkey='properties.GEO_ID',
                    locations='county_fips',
                    color='cases_per_100k',
                    color_continuous_scale='Viridis',
                    zoom=3,
                    opacity=0.7,
                    #Colours range from minimum of dataset to 99th percentile
                    range_color=(coviddf['cases_per_100k'].min(), np.percentile(coviddf['cases_per_100k'].tolist(), 99)),
                    mapbox_style='carto-positron',
                    hover_name='county_name')

fig.write_html('../output/uscoviddistribution_'+date+'.html')

if not os.path.exists('../output/uscoviddistribution_'+date+'.html'):
    print('There was an error in outputting the choropleth map!')
else:
    print('Successfully outputted the choropleth map')