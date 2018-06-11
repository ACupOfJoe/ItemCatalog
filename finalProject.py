from flask import Flask, render_template, request, url_for, redirect, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from database_setup import User, Stock, Industry, Base 

from database_setup import Base, Industry, Stock, User
import datetime
from datetime import timedelta
import numpy as np
import pandas as pd 
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web

app = Flask(__name__)

def openSession(): 
	engine = create_engine('sqlite:///stocksbyindustrywithusers.db')
	Base.metadata.bind = engine 
	DBSession = sessionmaker(bind=engine) 
	session = DBSession()
	return session

@app.route("/", methods=['GET', 'POST'])
@app.route("/industries/", methods=['GET', 'POST'])
def readIndustries():
	session = openSession()
	industries = session.query(Industry).order_by(Industry.name.asc())
	for i in industries:
		print type(i.id)
	session.close()
	return render_template('readIndustries.html', industries=industries)

@app.route('/industries/create/', methods=['GET', 'POST'])
def createIndustry(): 
	session = openSession()
	if request.method == "POST":
		print "Method is post"
		newIndustry = Industry(name=request.form['name'])
		session.add(newIndustry)
		flash('Industy Successfully Added {0}'.format(newIndustry.name))
		session.commit()
		session.close()
		return redirect(url_for('readIndustries'))
	else: 
		return render_template('createIndustry.html')

@app.route('/industries/update/<int:industry_id>/', methods=['GET', 'POST'])
def updateIndustry(industry_id): 
	session = openSession()
	editIndustry = session.query(Industry).filter_by(id=industry_id).one()
	print str(editIndustry.name)
	if request.method == "POST":
		print "Method is post"
		if request.form['name']:
			print "Request.form name exists"
			editIndustry.name = request.form['name']
			flash('Industy Successfully Edited {0}'.format(editIndustry.name))
			session.commit()
			session.close()
			return redirect(url_for('readIndustries'))
	else:
		return render_template('updateIndustry.html', industry=editIndustry)

@app.route('/industries/delete/<int:industry_id>/', methods=['GET', 'POST'])
def deleteIndustry(industry_id): 
	session = openSession() 
	deleteThisIndustry = session.query(Industry).filter_by(id=industry_id).one()
	print str(deleteThisIndustry.name)
	if request.method == "POST":
		if request.form['deleteSelection'] == 'yes':
			session.delete(deleteThisIndustry)
			flash("{0} has been sucessfully deleted".format(deleteThisIndustry.name))
			session.commit()
			session.close()
			return redirect(url_for('readIndustries'))
		
		else:
			session.close()
			return redirect(url_for('readIndustries'))
	else:
		return render_template('deleteIndustry.html', industry=deleteThisIndustry)

@app.route('/industries/<int:industry_id>/', methods=['GET', 'POST'] )
@app.route('/industries/<int:industry_id>/stocks', methods=['GET', 'POST'] )
def readStocks(industry_id): 
	session = openSession()
	industry = session.query(Industry).filter_by(id=industry_id).one()
	stocks=session.query(Stock).filter_by(industry_id=industry_id)
	return render_template('readStocks.html', industry=industry, stocks=stocks, industry_id=industry_id)

@app.route('/industries/<int:industry_id>/stocks/create', methods=['GET', 'POST'])
def createStock(industry_id):
	#try: 
	session = openSession()
	if request.method == "POST":
		print "Method is post"
		newStock = createStockObject(ticker=str(request.form['ticker']), industry_id=industry_id)
		session.add(newStock)
		flash('Stock Successfully Added {0}'.format(newStock.ticker))
		session.commit()
		session.close()
		return redirect(url_for('readStocks', industry_id=industry_id))
	#except:
		#return "Error. Possibly your Stock Ticker doesn't exist"
	else: 
		return render_template('createStock.html', industry_id=industry_id)

def createStockObject(ticker, industry_id): 
	try: 
		startTime = datetime.date.today()-datetime.timedelta(days=4)
		print "Readin Data"
		df1 = web.DataReader(ticker, 'morningstar', 
		           	startTime,
		            datetime.date.today(), retry_count=0).reset_index()
		print "Read Data"
		today= datetime.datetime.today()
		yesterday = today - timedelta(days=2)
		yesterday = yesterday.strftime("%Y-%m-%d")
		close_price = df1['Close'].tail(1)
		close_price = str(close_price.to_string(index=False))
		print "Set up variables"
		print close_price[0:]
		return Stock(ticker=ticker, close_price=close_price, industry_id=industry_id)
	except: 
		print "Sorry, we could not find the ticker for that stock"

@app.route('/industries/<int:industry_id>/stocks/<int:stock_id>/update/', methods=['GET', 'POST'])
def updateStock(industry_id, stock_id):
	session = openSession()
	industry = session.query(Industry).filter_by(id=industry_id).one()
	originalStock = session.query(Stock).filter_by(industry_id=industry_id, id=stock_id).one()
	print "ticker and id are: " + str(originalStock.ticker) + str(originalStock.id)
	if request.method == "POST":
		print "Method is post"
		if request.form['ticker']:
			print "Request.form ticker exists"
			updateStock = createStockObject(str(request.form['ticker']), industry_id=industry_id)
			updateStock.id = originalStock.id
			session.delete(originalStock)
			print "New Id is : " + str(updateStock.id)
			flash('Stock Successfully Edited {0}'.format(updateStock.ticker))
			session.add(updateStock)
			session.commit()
			session.close()
			return redirect(url_for('readStocks', industry_id=industry_id, industry=industry))
	else:
		return render_template('updateStock.html', stock=originalStock, stock_id=stock_id, industry=industry, industry_id=industry_id)

@app.route('/HelloWorld')
def main(): 
	stock1 = createStockObject('aapl')
	print "\n" + str(stock1['symbol']) + "\n" + str(stock1['id']) + "\n" + str(stock1['close_price'])
	stocks = populateListOfStocks(['aapl', 'msft', 'atvi', 'fico', 'ea'])
	print stocks
	return render_template('showStocks.html', stocks= stocks, sector = "Technology")

if __name__ == '__main__':
	app.secret_key = "Super Secret Key"
	app.debug = True 
	app.run(host = '0.0.0.0', port=5000)

