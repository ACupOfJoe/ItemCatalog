from flask import (Flask, render_template, request, url_for,
                   redirect, jsonify, flash)
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import User, Stock, Industry, Base
import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
# Must change name of file because of version of pandas that is downloaded.
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

import os

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets_google.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Stock Menu Application"

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    """
    showLogin: This method creates a random string of 32
        characters and uses that to set the STATE of the session.
    Args:
       No arguments
    Returns:
        Returns the login page with the state set.
    """
    print "Checkpoint 0-1"
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/disconnect')
def disconnect():
    """
    disconnect: This method disconnects the user using the gdisconnect method.
    Allows multiple types of
    disconnects to be used
    Args:
       No arguments
    Returns:
       Flashes a message for success or failure and then redirects to the
       readIndustries.html template.
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            flash("You've been sucessfully logged out.")
            return redirect(url_for('readIndustries'))

    else:
        flash("You were not logged in to begin with!")
        redirect(url_for('readIndustries'))


@app.route('/gconnect', methods=['POST'])
def gconnect():
    print "Checkpoint 0"
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
    print "Checkpoint 1" 
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
    print "Checkpoint 10"
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print "Checkpoint 11"
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

    print "Checkpoint 2" 
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    print "Checkpoint 3"
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: ' \
        '150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token={0}'.format(
        login_session['access_token'])
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
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Restaurant Information


@app.route('/industries/<int:industry_id>/stocks/JSON')
def stockListJSON(industry_id):
    """
    stockListJSON: This method gets the list of stocks in JSON format
    Args:
       No arguments
    Returns:
       The list of stocks for a specific industry in JSON format
    """
    session = openSession()
    industry = session.query(Industry).filter_by(id=industry_id).one_or_none()
    stocks = session.query(Stock).filter_by(
        industry_id=industry_id).all()
    session.close()
    return jsonify(stocks=[stock.serialize for stock in stocks])


@app.route('/industries/<int:industry_id>/stocks/<int:stock_id>/JSON')
def stockJSON(industry_id, stock_id):
    """
    stockJSON: This method gets a stock in JSON format
    Args:
       No arguments
    Returns:
       The stock based on industry id and stock_id in JSON format.
    """
    session = openSession()
    stock = session.query(Stock).filter_by(id=stock_id).one_or_none()
    session.close()
    return jsonify(stock=stock.serialize)


@app.route('/JSON')
@app.route('/industries/JSON')
def industriesJSON():
    """
    industriesJSON: This method gets the industries name's in JSON format
    Args:
       No arguments
    Returns:
       The entire set of industries in JSON format.
    """
    session = openSession()
    industries = session.query(Industry).all()
    session.close()
    return jsonify(industries=[industry.serialize for industry in industries])


def openSession():
    """
    openSession: This method gets the opens the
    stocksbyindustrywithusers.db database
    Args:
       No arguments
    Returns:
       A session that can be used to query and do other sql functions.
    """
    engine = create_engine('sqlite:///stocksbyindustrywithusers.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def login_required(f):
    """
    login_required: This method is a function that is used to
    require a specific page to be logged in to
    Args:
       No arguments
    Returns:
       A function that has been decorated with a login requirement.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect('/login')
    return decorated_function


@app.route("/", methods=['GET', 'POST'])
@app.route("/industries/", methods=['GET', 'POST'])
def readIndustries():
    """
    readIndustries: This method reads out all the industries and
    returns two different html pages based on
    whether the user is logged in or not.
    Args:
       No arguments
    Returns:
        Returns a "public" template if the user is not logged in.
        Other wise returns a template with more capabilities.
    """
    session = openSession()
    industries = session.query(Industry).order_by(Industry.name.asc())
    if 'username' not in login_session:
        session.close()
        return render_template('publicIndustries.html', industries=industries)
    else:
        session.close()
        return render_template('readIndustries.html', industries=industries)


@app.route('/industries/create/', methods=['GET', 'POST'])
@login_required
def createIndustry():
    """
    createIndustries: This method brings the user to a page to create a new
    Industry.
    Args:
       No arguments
    Returns:
        Returns an html to create an industry if the method is GET.
        If the method is a POST, creates the new industry
        and then returns to readIndustries html.
    """
    session = openSession()
    if request.method == "POST":
        newIndustry = Industry(
            name=request.form['name'],
            user_id=login_session['username'])
        session.add(newIndustry)
        flash('Industy Successfully Added {0}'.format(newIndustry.name))
        session.commit()
        session.close()
        return redirect(url_for('readIndustries'))
    else:
        return render_template('createIndustry.html')


@app.route('/industries/update/<int:industry_id>/', methods=['GET', 'POST'])
@login_required
def updateIndustry(industry_id):
    """
    updateIndustry: This method allows the user to update an Industry
    Args:
       industry_id (int): Used to identify which industry we are updating.
    Returns:
        Returns an html used to update an industry if the method is GET.
        If the method is a POST updates the current industry,
        and then returns to the readIndustries page
    """

    session = openSession()
    editIndustry = session.query(Industry).filter_by(
        id=industry_id).one_or_none()
    if request.method == "POST":
        if login_session['username'] == editIndustry.user_id:
            if request.form['name']:
                editIndustry.name = request.form['name']
                flash('Industy Successfully Edited {0}'.format(
                    editIndustry.name))
                session.commit()
                session.close()
                return redirect(url_for('readIndustries'))
        elif login_session['username'] != editIndustry.user_id:
            flash("Sorry! You are not authorized to update this industry")
            return redirect(url_for('readIndustries'))
    else:
        return render_template('updateIndustry.html', industry=editIndustry)


@app.route('/industries/delete/<int:industry_id>/', methods=['GET', 'POST'])
@login_required
def deleteIndustry(industry_id):
    """
    deleteIndustry: This method allows the user to delete an Industry
    Args:
       industry_id (int): Used to identify which industry we are deleting.
    Returns:
        Returns an html used to delete an industry if the method is GET.
        If the method is a POST updates the current industry,
        and then returns to the readIndustries page
    """
    session = openSession()
    deleteThisIndustry = session.query(Industry).filter_by(
        id=industry_id).one_or_none()
    if request.method == 'POST':
        if login_session['username'] == deleteThisIndustry.user_id:
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
        elif login_session['username'] != deleteThisIndustry.user_id:
                flash("Sorry! You are not authorized to delete this industry")
                return redirect(url_for('readIndustries'))
    else:
        return render_template(
            'deleteIndustry.html',
            industry=deleteThisIndustry)


@app.route('/industries/<int:industry_id>/', methods=['GET', 'POST'])
@app.route('/industries/<int:industry_id>/stocks', methods=['GET', 'POST'])
def readStocks(industry_id):
    """
    readStocks: This method reads out all the stocks and returns two different
    html pages based on whether the user is logged in or not.
    Args:
       industry_id (int): Used to identify which industry we are reading stocks
       for.
    Returns:
        Returns a "public" template if the user is not logged in.
        Otherwise returns a template with more capabilities.
    """
    session = openSession()
    industry = session.query(Industry).filter_by(id=industry_id).one_or_none()
    stocks = session.query(Stock).filter_by(industry_id=industry_id)
    return render_template(
        'readStocks.html', industry=industry, stocks=stocks,
        industry_id=industry_id)


@app.route('/industries/<int:industry_id>/stocks/create',
           methods=['GET', 'POST'])
@login_required
def createStock(industry_id):
    """
    createStock: This method brings the user to a page to create a new Stock.
    Args:
       industry_id (int): Used to identify which industry we are
       creating a stock for.
    Returns:
        Returns an html to create an Stock if the method is GET.
        If the method is a POST, creates the new stock
        and then returns to readstocks html.
    """
    session = openSession()
    if request.method == "POST":  
        newStock = createStockObject(
            ticker=str(request.form['ticker']),
            industry_id=industry_id,
            user_id=login_session['username'])
        session.add(newStock)
        flash('Stock Successfully Added {0}'.format(newStock.ticker))
        session.commit()
        session.close()
        return redirect(url_for('readStocks', industry_id=industry_id))
    else:
        return render_template('createStock.html', industry_id=industry_id)


def createStockObject(ticker, industry_id, user_id):
    """
    createStockObject: Used to create a stock object with updated close price.
    Args:
        ticker (str): The ticker symbol of the stock to be created
        industry_id (int): Used to identify which industry we are
        creating a stock for.

    Returns:
        Returns a stock object with an updated close price.
    """
    try:
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
            industry_id=industry_id, user_id=user_id)
    except ValueError as e:
        flash("Could not update to stock: {0}".format(str(
            request.form['ticker'])))
        return render_template('readStocks.html', industry_id=industry_id,
                               industry=industry)


@app.route('/industries/<int:industry_id>/stocks/<int:stock_id>/update/',
           methods=['GET', 'POST'])
@login_required
def updateStock(industry_id, stock_id):
    """
    updateStock: This method allows the user to update a Stock
    Args:
       industry_id (int): Used to identify which industry we are updating.
       stock_id (int): Used to identify which stock we are updating.
    Returns:
        Returns an html used to update a stock if the method is GET.
        If the method is a POST updates the current stock,
        and then returns to the readStocks page
    """
    session = openSession()
    industry = session.query(Industry).filter_by(id=industry_id).one_or_none()
    originalStock = session.query(Stock).filter_by(industry_id=industry_id,
                                                   id=stock_id).one_or_none()
    if request.method == "POST":
        if login_session['username'] == originalStock.user_id:
            if request.form['ticker']:
                try:
                    updateStock = createStockObject(
                                                str(request.form['ticker']),
                                                industry_id=industry_id,
                                                user_id=originalStock.user_id)
                    updateStock.id = originalStock.id
                    session.delete(originalStock)
                    flash(' Successfully Edited Stock {0}'.format(
                        updateStock.ticker))
                    session.add(updateStock)
                    session.commit()
                    session.close()
                    return redirect(url_for(
                        'readStocks', industry_id=industry_id,
                        industry=industry))
                except Exception as e:
                    print(e)
                    flash("Could not update to stock: {0}".format(str(
                        request.form['ticker'])))
                    return redirect(url_for(
                        'readStocks', industry_id=industry_id))
        else:
            flash("Sorry! You are not authorized to delete this stock")
            return redirect(url_for('readStocks', industry_id=industry_id))
    else:
        return render_template(
            'updateStock.html', stock=originalStock, stock_id=stock_id,
            industry=industry, industry_id=industry_id)


@app.route('/industries/<int:industry_id>/stocks/<int:stock_id>/delete/',
           methods=['GET', 'POST'])
@login_required
def deleteStock(industry_id, stock_id):
    """
    deleteStock: This method allows the user to delete a Stock
    Args:
       industry_id (int): Used to identify which industry we are updating.
       stock_id (int): Used to identify which stock we are updating.
    Returns:
        Returns an html used to delete a stock if the method is GET.
        If the method is a POST updates the current stock,
        and then returns to the readStocks page
    """
    session = openSession()
    deleteThisStock = session.query(Stock).filter_by(
        id=stock_id, industry_id=industry_id).one_or_none()
    industry = session.query(Industry).filter_by(id=industry_id).one_or_none()
    if request.method == "POST":
        if login_session['username'] == deleteThisStock.user_id:
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
        elif login_session['username'] != deleteThisStock.user_id:
                flash("Sorry! You are not authorized to delete this stock")
                return redirect(url_for('readStocks', industry_id=industry_id))
    else:
        return render_template(
            'deleteStock.html', stock=deleteThisStock,
            industry_id=industry_id, industry=industry)

if __name__ == '__main__':
    app.secret_key = "Super Secret Key"
    app.debug = True
    app.run(    
        host=os.getenv('LISTEN', '0.0.0.0'),
        port=int(os.getenv('PORT', '80')))
