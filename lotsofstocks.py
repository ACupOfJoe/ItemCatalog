from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import json

from database_setup import Base, Industry, Stock, User
import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
# Must change name of file because of version of pandas that is downloaded.
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web


"""Information taken from lotsofmenus.py from Udacity"""
engine = create_engine('sqlite:///stocksbyindustrywithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()



"""This method takes in a ticker symbol uses web.Datareader to find the closing
price of the stock
Inputs:
ticker: String representing the ticker for the stock you want to add
catalog_id: Integer representing which catalog the stock object belogs to

Results: In a stock object that has the closing price of the stock, and industry id

"""
def createStockObject(ticker, industry_id):
    startTime = datetime.date.today()-datetime.timedelta(days=4)
    print "Readin Data"
    df1 = web.DataReader(
                ticker, 'robinhood',
                startTime,
                datetime.date.today(), retry_count=0).reset_index()
    print "Read Data"
    today = datetime.datetime.today()
    yesterday = today - timedelta(days=2)
    yesterday = yesterday.strftime("%Y-%m-%d")
    close_price = df1['close_price'].tail(1)
    close_price = str(close_price.to_string(index=False))
    print "Set up variables"
    print close_price[0:]
    return Stock(
        ticker=ticker, close_price=close_price,
        industry_id=industry_id)

stockJSON = json.loads(open("stocksJSON.json").read())
for stock in stockJSON[u'stock']:
    ticker = str(stock[u'ticker'].upper())
    print ticker
    industry_id = str(stock['industry_id'])
    print industry_id
    stock_input = createStockObject(
        ticker,
        industry_id)
    print "Successfully added a stock with a ticker and closing price of: " \
    + stock_input.close_price + stock_input.ticker
    session.add(stock_input)
    session.commit()


for user in stockJSON['user']:
    name = user[u'name']
    email = user[u'email']
    picture = user[u'picture']
    user_input = User(name=name, email=email, picture=picture)
    session.add(user_input)
    session.commit()

for industry in stockJSON['industry']:
    name = industry[u'name']
    user_id = industry[u'user_id']
    user = session.query(User).filter_by(id=1).one_or_none()
    industry_input = Industry(
        name=name, user_id=user_id)
    session.add(industry_input)
    session.commit()
