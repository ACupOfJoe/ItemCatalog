from flask import (Flask, render_template, request, url_for,
                   redirect, jsonify, flash)
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

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets_google.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Stock Menu Application"

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % slogin_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        flash("You've been sucessfully logged out.")
        return redirect(url_for('readIndustries'))

    else:
        flash("You weren ot logged in to begin with!")
        redirect(url_for('readIndustries'))


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'client_secrets_google.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    login_session['provider'] = 'google'
    response = make_response(json.dumps('Successfully connected user.', 200))

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += 'style = "width: 300px;'
    output += "height: 300px;border-radius: 150px;-webkit-border-radius: "
    output += "150px;-moz-border-radius: 150px;>"
    flash("you are now logged in as %s" % login_session['username'])
    return output


def createUser(login_session):
    newUser = User(
        name=login_session['username'], email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(email=login_session['email'])
    return user.id


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# JSON APIs to view Restaurant Information


@app.route('/industries/<int:industry_id>/stocks/JSON')
def stockListJSON(industry_id):
    session = openSession()
    industry = session.query(Industry).filter_by(id=industry_id).one()
    stocks = session.query(Stock).filter_by(
        industry_id=industry_id).all()
    session.close()
    return jsonify(stocks=[stock.serialize for stock in stocks])


@app.route('/industries/<int:industry_id>/stocks/<int:stock_id>/JSON')
def stockJSON(industry_id, stock_id):
    session = openSession()
    stock = session.query(Stock).filter_by(id=stock_id).one()
    session.close()
    return jsonify(stock=stock.serialize)


@app.route('/JSON')
@app.route('/industries/JSON')
def indsutriesJSON():
    session = openSession()
    industries = session.query(Industry).all()
    session.close()
    return jsonify(industries=[industry.serialize for industry in industries])


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
    if 'username' not in login_session:
        session.close()
        return render_template('publicIndustries.html', industries=industries)
    else:
        session.close()
        return render_template('readIndustries.html', industries=industries)


@app.route('/industries/create/', methods=['GET', 'POST'])
def createIndustry():
    if 'username' not in login_session:
        return redirect('/login')
    session = openSession()
    if request.method == "POST":
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
    if 'username' not in login_session:
        return redirect('/login')
    session = openSession()
    editIndustry = session.query(Industry).filter_by(id=industry_id).one()
    if request.method == "POST":
        if request.form['name']:
            editIndustry.name = request.form['name']
            flash('Industy Successfully Edited {0}'.format(editIndustry.name))
            session.commit()
            session.close()
            return redirect(url_for('readIndustries'))
    else:
        return render_template('updateIndustry.html', industry=editIndustry)


@app.route('/industries/delete/<int:industry_id>/', methods=['GET', 'POST'])
def deleteIndustry(industry_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = openSession()
    deleteThisIndustry = session.query(Industry).filter_by(
        id=industry_id).one()
    if request.method == "POST":
        if request.form['deleteSelection'] == 'yes':
            session.delete(deleteThisIndustry)
            flash("{0} has been sucessfully deleted".format(
                deleteThisIndustry.name))
            session.commit()
            session.close()
            return redirect(url_for('readIndustries'))

        else:
            session.close()
            return redirect(url_for('readIndustries'))
    else:
        return render_template(
            'deleteIndustry.html',
            industry=deleteThisIndustry)


@app.route('/industries/<int:industry_id>/', methods=['GET', 'POST'])
@app.route('/industries/<int:industry_id>/stocks', methods=['GET', 'POST'])
def readStocks(industry_id):
    session = openSession()
    industry = session.query(Industry).filter_by(id=industry_id).one()
    stocks = session.query(Stock).filter_by(industry_id=industry_id)
    return render_template(
        'readStocks.html', industry=industry, stocks=stocks,
        industry_id=industry_id)


@app.route('/industries/<int:industry_id>/stocks/create',
           methods=['GET', 'POST'])
def createStock(industry_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = openSession()
    if request.method == "POST":
        newStock = createStockObject(
            ticker=str(request.form['ticker']),
            industry_id=industry_id)
        session.add(newStock)
        flash('Stock Successfully Added {0}'.format(newStock.ticker))
        session.commit()
        session.close()
        return redirect(url_for('readStocks', industry_id=industry_id))
    # except:
        # return "Error. Possibly your Stock Ticker doesn't exist"
    else:
        return render_template('createStock.html', industry_id=industry_id)


def createStockObject(ticker, industry_id):
    try:
        startTime = datetime.date.today()-datetime.timedelta(days=4)
        df1 = web.DataReader(
                    ticker, 'morningstar',
                    startTime,
                    datetime.date.today(), retry_count=0).reset_index()
        today = datetime.datetime.today()
        yesterday = today - timedelta(days=2)
        yesterday = yesterday.strftime("%Y-%m-%d")
        close_price = df1['Close'].tail(1)
        close_price = str(close_price.to_string(index=False))
        return Stock(ticker=ticker, close_price=close_price,
                     industry_id=industry_id)
    except:
        print "Sorry, we could not find the ticker for that stock"


@app.route('/industries/<int:industry_id>/stocks/<int:stock_id>/update/',
           methods=['GET', 'POST'])
def updateStock(industry_id, stock_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = openSession()
    industry = session.query(Industry).filter_by(id=industry_id).one()
    originalStock = session.query(Stock).filter_by(industry_id=industry_id,
                                                   id=stock_id).one()
    if request.method == "POST":
        if request.form['ticker']:
            updateStock = createStockObject(
                                        str(request.form['ticker']),
                                        industry_id=industry_id)
            updateStock.id = originalStock.id
            session.delete(originalStock)
            flash('Stock Successfully Edited {0}'.format(updateStock.ticker))
            session.add(updateStock)
            session.commit()
            session.close()
            return redirect(url_for('readStocks', industry_id=industry_id,
                            industry=industry))
    else:
        return render_template(
            'updateStock.html', stock=originalStock, stock_id=stock_id,
            industry=industry, industry_id=industry_id)


@app.route('/industries/<int:industry_id>/stocks/<int:stock_id>/delete/',
           methods=['GET', 'POST'])
def deleteStock(industry_id, stock_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = openSession()
    deleteThisStock = session.query(Stock).filter_by(
        id=stock_id, industry_id=industry_id).one()
    industry = session.query(Industry).filter_by(id=industry_id).one()
    if request.method == "POST":
        if request.form['deleteSelection'] == 'yes':
            session.delete(deleteThisStock)
            flash("{0} has been sucessfully deleted".format(
                deleteThisStock.ticker))
            session.commit()
            session.close()
            return redirect(url_for('readStocks', industry_id=industry_id))

        else:
            session.close()
            return redirect(url_for('readStocks', industry_id=industry_id))
    else:
        return render_template(
            'deleteStock.html', stock=deleteThisStock,
            industry_id=industry_id, industry=industry)


@app.route('/HelloWorld')
def main():
    stock1 = createStockObject('aapl')
    stocks = populateListOfStocks(['aapl', 'msft', 'atvi', 'fico', 'ea'])
    return render_template(
        'showStocks.html', stocks=stocks, sector="Technology")

if __name__ == '__main__':
    app.secret_key = "Super Secret Key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
