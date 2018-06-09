from flask import Flask, render_template, request, url_for, redirect, jsonify, flash
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
def readIndustries():
	session = openSession()
	industries = session.query(Industry).order_by(Industry.name.asc())
	session.close()
	return render_template('readIndustries.html', industries=industries)

@app.route('/industries/new', methods=['GET', 'POST'])
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

@app.route('/industries/update/<int:industry_id>', methods=['GET', 'POST'])
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

@app.route('/industries/delete/<int:industry_id>', methods=['GET', 'POST'])
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

