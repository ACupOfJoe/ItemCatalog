from flask import Flask, render_template, request, url_for, redirect, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from database_setup import User, Stock, Industry, Base 
app = Flask(__name__)

def openSession(): 
	engine = create_engine('sqlite:///stocksbyindustrywithusers.db')
	Base.metadata.bind = engine 
	DBSession = sessionmaker(bind=engine) 
	session = DBSession()
	return session

@app.route("/", methods=['GET', 'POST'])
@app.route("/industries/", methods=['GET', 'POST'])
def showIndustries():
	session = openSession()
	industries = session.query(Industry).order_by(Industry.name.asc())
	session.close()
	return render_template('showIndustries.html', industries=industries)

@app.route('/industries/new', methods=['GET', 'POST'])
def newIndustry(): 
	session = openSession()
	if request.method == "POST":
		newIndustry = Industry(name=request.form['name'])
		session.add(newIndustry)
		session.commit()
		session.close()
		return redirect(url_for('showIndustries'))
	else: 
		return render_template('newIndustry.html')


@app.route('/HelloWorld')
def main(): 
	stock1 = createStockObject('aapl')
	print "\n" + str(stock1['symbol']) + "\n" + str(stock1['id']) + "\n" + str(stock1['close_price'])
	stocks = populateListOfStocks(['aapl', 'msft', 'atvi', 'fico', 'ea'])
	print stocks
	return render_template('showStocks.html', stocks= stocks, sector = "Technology")

if __name__ == '__main__':
	app.debug = True 
	app.run(host = '0.0.0.0', port=5000)

