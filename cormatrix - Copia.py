from bs4 import BeautifulSoup as bs
from collections import Counter
import datetime as dt
from datetime import datetime,date
import calendar
import csv

import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
#SCROLL WINDOW
from matplotlib.widgets import Slider
#FIM SCROLL WINDOW
import os
import pandas as pd
import pandas_datareader.data as web
import pickle
import requests
import sys
import shutil #NEW 0.1.1

#Poloniex API#
import urllib
import urllib.request
import json
import time
import hmac,hashlib


style.use('ggplot')


#If no IMGS dir, create it
# directory = '\\imgs\\'
# if not os.path.exists(directory):
#     os.makedirs(directory)

## Start and end dates
start_date = date(2017,4,8)
end_date = date(2017,4,9)

## Candlestick period valid values are:
## 300 (5 minutes), 900 (15 minutes), 1800 (30 minutes), 7200 (2 hours), 14400 (4 hours), and 86400 (1 day)
period = 1800



## Pulls coin names from a space seperated text file
def read_crypto_file():
    file = open('coins.txt','r')
    coins = file.read().splitlines()
    return coins

def get_data_from_polo():
    
    tickers = read_crypto_file()
 
    timestamp1 = calendar.timegm(start_date.timetuple())
    start = timestamp1
    
    timestamp2 = calendar.timegm(end_date.timetuple())
    end = timestamp2
    
    if not os.path.exists('coin_dfs'):
        os.makedirs('coin_dfs')
 
## Currency Pairing
    pairing = 'BTC_'


## Creating a Bitcoin/USD datafram for converting coins to USD 
    coin_lookup('BTC',start,end,period,'USDT_')
    df_btc = pd.read_csv('coin_dfs/BTC.csv')
    df_btc.set_index('date', inplace=True)

    df_btc.rename(columns = {'close':'BTC'}, inplace=True)
    df_btc.drop(['high','low','open','quoteVolume','weightedAverage','volume'], 1, inplace=True)
    df_btc.to_pickle('df_btc.pickle')


## Coin.txt lookup
    for ticker in tickers:
        coin_lookup(ticker,start,end,period,pairing)

def coin_lookup(ticker,start,end,period, pairing):
 
## Creates a seperate CSV file for each coin.
        if not os.path.exists('coin_dfs/{}.csv'.format(ticker)):
            print(ticker)
            df = urllib.request.urlopen('https://poloniex.com/public?command=' + "returnChartData" + '&currencyPair=' + str(pairing) + str(ticker) + '&start=' + str(start) + '&end=' + str(end) +'&period=' + str(period))
            str_info = df.read().decode('utf-8')
            info = json.loads(str_info)
            with open('coin_dfs/{}.csv'.format(ticker),'w',encoding='utf8') as f:
                writer = csv.DictWriter(f, fieldnames=['date','high','low','open','close','quoteVolume', 'weightedAverage','volume'])
                print(info)
                writer.writeheader()
                writer.writerows(info)

## Wait after every API call, as a precaution
            time.sleep(5)

        else:
            print('Already have{}'.format(ticker))
   
def compile_data():
    
    get_data_from_polo()

    tickers = read_crypto_file()
    
    main_df = pd.DataFrame()

# Read the BTC price data and set it to head of the dataframe
    df_btc = pd.read_pickle('df_btc.pickle')
    main_df = df_btc

    for count,ticker in enumerate(tickers):
        df = pd.read_csv('coin_dfs/{}.csv'.format(ticker))
        df.set_index('date', inplace=True)

        df.rename(columns = {'close':ticker}, inplace=True)
        df.drop(['high','low','open','quoteVolume','weightedAverage','volume'], 1, inplace=True)
        
# Converts price values from /BTC to /USD
        df_usd = df.join(df_btc)
        df_usd['{}'.format(ticker)] = df_usd['{}'.format(ticker)] * df_usd['BTC']        
        df_usd.drop(['BTC'],1, inplace = True)


        if main_df.empty:
            main_df = df_usd    
        else:

            main_df = main_df.join(df_usd,how='outer')

## Show Progress
        if count % 10 == 0:
            print(count)

    print(main_df.tail())
    main_df.to_csv('coin_joined_closes.csv')


def visualize_data():
    compile_data()
    df = pd.read_csv('coin_joined_closes.csv')
    df.drop(['date'], 1, inplace= True)
    
    df_corr = df.corr()
    
    print(df_corr.head())
    
    data = df_corr.values
    fig = plt.figure(figsize=(15,15), dpi=90)

## Chart layout options
    ax = fig.add_subplot(1,1,1)
    
    heatmap = ax.pcolor(data, cmap=plt.cm.RdYlGn)
    fig.colorbar(heatmap)
    ax.set_xticks(np.arange(data.shape[0]) +0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[1]) +0.5, minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    column_labels = df_corr.columns
    row_labels = df_corr.index

## TITULO E AJUSTE
    #plt.title('{} - {} ({} min) /n'.format(start_date, end_date, (period/60)))
##    
    ax.set_xticklabels(column_labels)
    ax.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap.set_clim(-1,1)
    plt.tight_layout()
    plt.axis('scaled')
    fig = plt.gcf()

    timeFile = time.strftime("%d%m%Y-%H%M%S")
    fig.savefig("D:/GIT/cormatrix/imgs/figure-" + timeFile + ".png")
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()

visualize_data()

# #If coin_dfs dir and csv sheet exist, delete them - *0.1.1*
# sheet = 'D:\\GIT\\cormatrix\\coin_joined_closes.csv'
# if os.path.exists(sheet):
#     os.remove(sheet)
    
# directory = 'd:\\GIT\\cormatrix\\coin_dfs'
# if os.path.exists(directory):
#     shutil.rmtree(directory)

##

##

##

#==============ETHER MARKET======================


style.use('ggplot')


#If no IMGS dir, create it
# directory = '\\imgs\\'
# if not os.path.exists(directory):
#     os.makedirs(directory)

## Start and end dates
start_date = date(2017,4,8)
end_date = date(2017,4,9)

## Candlestick period valid values are:
## 300 (5 minutes), 900 (15 minutes), 1800 (30 minutes), 7200 (2 hours), 14400 (4 hours), and 86400 (1 day)
period = 1800



## Pulls coin names from a space seperated text file
def read_crypto_file():
    file = open('coins_eth.txt','r')
    coins = file.read().splitlines()
    return coins

def get_data_from_polo():
    
    tickers = read_crypto_file()
 
    timestamp1 = calendar.timegm(start_date.timetuple())
    start = timestamp1
    
    timestamp2 = calendar.timegm(end_date.timetuple())
    end = timestamp2
    
    if not os.path.exists('coin_eth_dfs'):
        os.makedirs('coin_eth_dfs')
 
## Currency Pairing
    pairing = 'ETH_'


## Creating a Bitcoin/USD datafram for converting coins to USD 
    coin_lookup('ETH',start,end,period,'USDT_')
    df_eth = pd.read_csv('coin_eth_dfs/ETH.csv')
    df_eth.set_index('date', inplace=True)

    df_eth.rename(columns = {'close':'ETH'}, inplace=True)
    df_eth.drop(['high','low','open','quoteVolume','weightedAverage','volume'], 1, inplace=True)
    df_eth.to_pickle('df_eth.pickle')


## Coin.txt lookup
    for ticker in tickers:
        coin_lookup(ticker,start,end,period,pairing)

def coin_lookup(ticker,start,end,period, pairing):
 
## Creates a seperate CSV file for each coin.
        if not os.path.exists('coin_eth_dfs/{}.csv'.format(ticker)):
            print(ticker)
            df = urllib.request.urlopen('https://poloniex.com/public?command=' + "returnChartData" + '&currencyPair=' + str(pairing) + str(ticker) + '&start=' + str(start) + '&end=' + str(end) +'&period=' + str(period))
            str_info = df.read().decode('utf-8')
            info = json.loads(str_info)
            with open('coin_eth_dfs/{}.csv'.format(ticker),'w',encoding='utf8') as f:
                writer = csv.DictWriter(f, fieldnames=['date','high','low','open','close','quoteVolume', 'weightedAverage','volume'])
                print(info)
                writer.writeheader()
                writer.writerows(info)

## Wait after every API call, as a precaution
            time.sleep(5)

        else:
            print('Already have{}'.format(ticker))
   
def compile_data():
    
    get_data_from_polo()

    tickers = read_crypto_file()
    
    main_df = pd.DataFrame()

# Read the BTC price data and set it to head of the dataframe
    df_eth = pd.read_pickle('df_eth.pickle')
    main_df = df_eth

    for count,ticker in enumerate(tickers):
        df = pd.read_csv('coin_eth_dfs/{}.csv'.format(ticker))
        df.set_index('date', inplace=True)

        df.rename(columns = {'close':ticker}, inplace=True)
        df.drop(['high','low','open','quoteVolume','weightedAverage','volume'], 1, inplace=True)
        
# Converts price values from /BTC to /USD
        df_usd = df.join(df_eth)
        df_usd['{}'.format(ticker)] = df_usd['{}'.format(ticker)] * df_usd['ETH']        
        df_usd.drop(['ETH'],1, inplace = True)


        if main_df.empty:
            main_df = df_usd    
        else:

            main_df = main_df.join(df_usd,how='outer')

## Show Progress
        if count % 10 == 0:
            print(count)

    print(main_df.tail())
    main_df.to_csv('coin_eth_joined_closes.csv')


def visualize_data():
    compile_data()
    df = pd.read_csv('coin_eth_joined_closes.csv')
    df.drop(['date'], 1, inplace= True)
    
    df_corr = df.corr()
    
    print(df_corr.head())
    
    data = df_corr.values
    fig = plt.figure(figsize=(10,10), dpi=90)

## Chart layout options
    ax = fig.add_subplot(1,1,1)
    
    heatmap = ax.pcolor(data, cmap=plt.cm.RdYlGn)
    fig.colorbar(heatmap)
    ax.set_xticks(np.arange(data.shape[0]) +0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[1]) +0.5, minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    column_labels = df_corr.columns
    row_labels = df_corr.index

## TITULO E AJUSTE
    #plt.title('{} - {} ({} min) /n'.format(start_date, end_date, (period/60)))
##    
    ax.set_xticklabels(column_labels)
    ax.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap.set_clim(-1,1)
    plt.tight_layout()
    plt.axis('scaled')
    fig = plt.gcf()

    timeFile = time.strftime("%d%m%Y-%H%M%S")
    fig.savefig("D:\\GIT\\cormatrix\\imgs\\eth-" + timeFile + ".png")
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()

visualize_data()

# #If coin_dfs dir and csv sheet exist, delete them - *0.1.1*
# sheet = 'D:\\GIT\\cormatrix\\coin_eth_joined_closes.csv'
# if os.path.exists(sheet):
#     os.remove(sheet)
    
# directory = 'd:\\GIT\\cormatrix\\coin_eth_dfs'
# if os.path.exists(directory):
#     shutil.rmtree(directory)


#
#================XMR MARKET=====================
#

style.use('ggplot')


#If no IMGS dir, create it
# directory = '\\imgs\\'
# if not os.path.exists(directory):
#     os.makedirs(directory)

## Start and end dates
start_date = date(2017,4,8)
end_date = date(2017,4,9)

## Candlestick period valid values are:
## 300 (5 minutes), 900 (15 minutes), 1800 (30 minutes), 7200 (2 hours), 14400 (4 hours), and 86400 (1 day)
period = 1800

## Pulls coin names from a space seperated text file
def read_crypto_file():
    file = open('coins_xmr.txt','r')
    coins = file.read().splitlines()
    return coins

def get_data_from_polo():
    
    tickers = read_crypto_file()
 
    timestamp1 = calendar.timegm(start_date.timetuple())
    start = timestamp1
    
    timestamp2 = calendar.timegm(end_date.timetuple())
    end = timestamp2
    
    if not os.path.exists('coin_xmr_dfs'):
        os.makedirs('coin_xmr_dfs')
 
## Currency Pairing
    pairing = 'XMR_'


## Creating a Bitcoin/USD datafram for converting coins to USD 
    coin_lookup('XMR',start,end,period,'USDT_')
    df_xmr = pd.read_csv('coin_xmr_dfs/XMR.csv')
    df_xmr.set_index('date', inplace=True)

    df_xmr.rename(columns = {'close':'XMR'}, inplace=True)
    df_xmr.drop(['high','low','open','quoteVolume','weightedAverage','volume'], 1, inplace=True)
    df_xmr.to_pickle('df_xmr.pickle')


## Coin.txt lookup
    for ticker in tickers:
        coin_lookup(ticker,start,end,period,pairing)

def coin_lookup(ticker,start,end,period, pairing):
 
## Creates a seperate CSV file for each coin.
        if not os.path.exists('coin_xmr_dfs/{}.csv'.format(ticker)):
            print(ticker)
            df = urllib.request.urlopen('https://poloniex.com/public?command=' + "returnChartData" + '&currencyPair=' + str(pairing) + str(ticker) + '&start=' + str(start) + '&end=' + str(end) +'&period=' + str(period))
            str_info = df.read().decode('utf-8')
            info = json.loads(str_info)
            with open('coin_xmr_dfs/{}.csv'.format(ticker),'w',encoding='utf8') as f:
                writer = csv.DictWriter(f, fieldnames=['date','high','low','open','close','quoteVolume', 'weightedAverage','volume'])
                print(info)
                writer.writeheader()
                writer.writerows(info)

## Wait after every API call, as a precaution
            time.sleep(5)

        else:
            print('Already have{}'.format(ticker))
   
def compile_data():
    
    get_data_from_polo()

    tickers = read_crypto_file()
    
    main_df = pd.DataFrame()

# Read the BTC price data and set it to head of the dataframe
    df_xmr = pd.read_pickle('df_xmr.pickle')
    main_df = df_xmr

    for count,ticker in enumerate(tickers):
        df = pd.read_csv('coin_xmr_dfs/{}.csv'.format(ticker))
        df.set_index('date', inplace=True)

        df.rename(columns = {'close':ticker}, inplace=True)
        df.drop(['high','low','open','quoteVolume','weightedAverage','volume'], 1, inplace=True)
        
# Converts price values from /BTC to /USD
        df_usd = df.join(df_xmr)
        df_usd['{}'.format(ticker)] = df_usd['{}'.format(ticker)] * df_usd['XMR']        
        df_usd.drop(['XMR'],1, inplace = True)


        if main_df.empty:
            main_df = df_usd    
        else:

            main_df = main_df.join(df_usd,how='outer')

## Show Progress
        if count % 10 == 0:
            print(count)

    print(main_df.tail())
    main_df.to_csv('coin_xmr_joined_closes.csv')


def visualize_data():
    compile_data()
    df = pd.read_csv('coin_xmr_joined_closes.csv')
    df.drop(['date'], 1, inplace= True)
    
    df_corr = df.corr()
    
    print(df_corr.head())
    
    data = df_corr.values
    fig = plt.figure(figsize=(10,10), dpi=90)

## Chart layout options
    ax = fig.add_subplot(1,1,1)
    
    heatmap = ax.pcolor(data, cmap=plt.cm.RdYlGn)
    fig.colorbar(heatmap)
    ax.set_xticks(np.arange(data.shape[0]) +0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[1]) +0.5, minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    column_labels = df_corr.columns
    row_labels = df_corr.index

## TITULO E AJUSTE
    #plt.title('{} - {} ({} min) /n'.format(start_date, end_date, (period/60)))
##    
    ax.set_xticklabels(column_labels)
    ax.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap.set_clim(-1,1)
    plt.tight_layout()
    plt.axis('scaled')
    fig = plt.gcf()

    timeFile = time.strftime("%d%m%Y-%H%M%S")
    fig.savefig("D:\\GIT\\cormatrix\\imgs\\xmr-" + timeFile + ".png")
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()

visualize_data()

# #If coin_dfs dir and csv sheet exist, delete them - *0.1.1*
# sheet = 'D:\\GIT\\cormatrix\\coin_xmr_joined_closes.csv'
# if os.path.exists(sheet):
#     os.remove(sheet)
    
# directory = 'd:\\GIT\\cormatrix\\coin_xmr_dfs'
# if os.path.exists(directory):
#     shutil.rmtree(directory)