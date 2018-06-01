from flask import Flask, render_template, request, url_for, redirect, jsonify
import pandas as pd 
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import datetime
import Tkinter
import matplotlib 
import numpy as np
import time


matplotlib.use('Agg')
app = Flask(__name__)



#Fake Restaurants
stockCatalogItem
#https://eresearch.fidelity.com/eresearch/markets_sectors/sectors/sectors_in_market.jhtml
stockCatalogAll = [{'name': 'Internet & Catalog Retail', 'id': '1'}, {'name':'Independent Power and Renewable Electricity Producers', 'id':'2'},{'name':'Real Estate Management & Development', 'id':'3'}, {'name':'Software', 'id':'3'}]


#Fake Menu Items
stock = {'symbol': '', 'id': '1', 'close_price': 0.00, 'data': ''}
listOfStocks = [stock]
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1', 'restaurant_id': '1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2', 'restaurant_id':'1'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3', 'restaurant_id':'2'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4', 'restaurant_id':'3'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5', 'restaurant_id':'1'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree', 'id': '1', 'restaurant_id': '1'}

#output_file("line.html")
startTime = datetime.date.today()-datetime.timedelta(days=365)
df1 = web.DataReader("aapl", 'morningstar',
	            startTime,
	            datetime.date.today()).reset_index()
stock['symbol'] = 'aapl'
stock['id'] = '1'
#stock['data'] = df1['Close']
#https://stackoverflow.com/questions/21738566/how-to-set-a-variable-to-be-todays-date-in-python-pandas
time = time.strftime("%Y/%m/%d")
stock['close_price'] = (df1.loc[df1['Date'] == (pd.to_datetime(time))]['Close'].reset_index())
print stock['close_price'] = stock['close_price']['Close']

def createStockObject(ticker): 
	startTime = datetime.date.today()-datetime.timedelta(days=365)
	df1 = web.DataReader(ticker, 'morningstar',
	            startTime,
	            datetime.date.today()).reset_index()
	stock['symbol'] = df1.loc[df1['Date'] == (pd.to_datetime(time))]['Symbol'].reset_index()
	stock['symbol'] = stock['symbol']['Symbol']
	stock['id'] = str(len(listOfStocks))
	stock['close_price'] = (df1.loc[df1['Date'] == (pd.to_datetime(time))]['Close'].reset_index())
	stock['close_price'] = stock['close_price']['Close']
	stock['data'] = df1['Close']
	return stock.copy()


