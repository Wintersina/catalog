from flask import Flask, render_template, url_for, redirect, request, flash, jsonify
import os, random, string, json, requests
from sqlalchemy import create_engine, distinct
from sqlalchemy.orm import sessionmaker
from database_setup import Users,Categories,Items,Base
from flask import session as login_session

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response


CLIENT_SECRETS_FILE = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Catalog Web App"

app = Flask(__name__)

app.secret_key = 'omzY7yqx45yBmQDmlGH5_brw'

sql_lite_db = create_engine('sqlite:///catalogdb.db')
Base.metadata.bind = sql_lite_db
DBsession = sessionmaker(bind = sql_lite_db)
session = DBsession()




#have user login
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase+string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

#connect google oauth with server and redirect
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
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
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
    #h = httplib2.Http()
    #result = json.loads(h.request(url, 'GET')[1])
    resp = requests.get(url)
    result = json.loads(resp.content.decode('utf-8'))
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
    if result['issued_to'] != CLIENT_SECRETS_FILE:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

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

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


@app.route('/')
def root():
    return "you are root"

#list all catalogs
@app.route('/catalog/')
def showAllCategories():
    return "you are at all categories"

#list all items for certin catalog
@app.route('/catalog/<string:catalog_name>/items')
def catalogItems(catalog_name):
    return "you reached %s" % catalog_name

#list discription about certin item in certin catalog
@app.route('/catalog/<string:catalog_name>/<string:item_name>/')
def aboutItem(catalog_name,item_name):
    return "you reached %s with about me for %s" % (catalog_name,item_name)

###CRUD--ITEM###

#edit catalog item
@app.route('/catalog/<string:catalog_name>/<string:item_name>/edit')
def editItem(catalog_name,item_name):
    return "you reached edit"

#delete catalog item
@app.route('/catalog/<string:catalog_name>/<string:item_name>/delete')
def deleteItem(catalog_name,item_name):
    return "you reached delete"

#create a new catalog item
@app.route('/catalog/<string:catalog_name>/item/new')
def newItem(catalog_name):
    return "you reached new item creation"

if __name__ == '__main__':
    app.secret_key = "yum_yum_key"
    app.debug = True
    port = int(os.environ.get('PORT',8000))
    app.run(host = '0.0.0.0', port = port)
