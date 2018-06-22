from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import json

from database_setup import Base, Industry, Stock, User
import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
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

Results:

"""


def createStockObject(ticker, industry_id):
    startTime = datetime.date.today()-datetime.timedelta(days=4)
    print "Readin Data"
    df1 = web.DataReader(
                ticker, 'morningstar',
                startTime,
                datetime.date.today(), retry_count=0).reset_index()
    print "Read Data"
    today = datetime.datetime.today()
    yesterday = today - timedelta(days=2)
    yesterday = yesterday.strftime("%Y-%m-%d")
    close_price = df1['Close'].tail(1)
    close_price = str(close_price.to_string(index=False))
    print "Set up variables"
    print close_price[0:]
    return Stock(
        ticker=ticker, close_price=close_price,
        industry_id=industry_id)
"""
user1 = User(name="Joseph", email="joevasquez927@live.com", picture=None)
session.add(user1)
session.commit()
print "Added user1"

industry1 = Industry(
    name="Independent Power and Renewable Electricity Producers",
    user_id=user1.id)
session.add(industry1)
session.commit()
print "Added industry1"
industry2 = Industry(name="Software", user_id=user1.id)
session.add(industry2)
session.commit()
print "Added industry2"
industry3 = Industry(name="Trading Companies and Distributors",
                     user_id=user1.id)
session.add(industry3)
session.commit()
print "Added industry3"
stock1 = createStockObject('HNP', industry1.id)
session.add(stock1)
session.commit()
print "Added stock1"
stock2 = createStockObject('NEP', industry1.id)
session.add(stock2)
session.commit()
print "Added stock2"
stock3 = createStockObject('AZRE', industry1.id)
session.add(stock3)
session.commit()
print "Added stock3"
stock4 = createStockObject('VMW', industry2.id)
session.add(stock4)
session.commit()
print "Added stock4"
stock5 = createStockObject('PAYC', industry2.id)
session.add(stock5)
session.commit()
print "Added stock5"
stock6 = createStockObject('WK', industry2.id)
session.add(stock6)
session.commit()
print "Added stock6"
stock7 = createStockObject('COLM', industry3.id)
session.add(stock7)
session.commit()
print "Added stock7"
stock8 = createStockObject('LAKE', industry3.id)
session.add(stock8)
session.commit()
print "Added stock8"
stock9 = createStockObject('NKE', industry3.id)
session.add(stock9)
session.commit()
print "Added stock9"
"""
stockJSON = json.loads(open("stocksJSON.json").read())
for stock in stockJSON['stock']:
    ticker = str(stock[u'ticker'])
    industry_id = str(stock[u'industry_id'])
    stock_input = createStockObject(
        ticker,
        industry_id)
    print "Successfully added a stock with a ticker and closing price of: " + stock_input.close_price + stock_input.ticker
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
        name=name, user_id=user_id, 
        user=user)
    session.add(industry_input)
    session.commit()