from flask import Flask, render_template, url_for, redirect, request, flash, jsonify
import os, random, string, json, requests, httplib2
from sqlalchemy import create_engine, distinct
from sqlalchemy.orm import sessionmaker
from database_setup import Users,Categories,Items,Base
from flask import session as login_session

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response
from flask_wtf.csrf import CSRFProtect


CLIENT_SECRETS_FILE = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Catalog Web App"

app = Flask(__name__)
csrf = CSRFProtect(app)
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
    code = request.data.decode('utf-8')

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

    flash("you are now logged in as %s" % login_session['username'])
    return output

#disconnect user from google signin
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    print (login_session['access_token'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    print ('result is ')
    print (result)
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
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#list all catalogs
@app.route('/')
@app.route('/catalog/')
def showAllCategories():
    results = session.query(Categories).all()
    return render_template('catagory.html',a_c=results)

#list all items for certin catalog
@app.route('/catalog/<string:catalog_name>/items')
def catalogItems(catalog_name):
    all_catagories = session.query(Categories).all()
    get_category_id = session.query(Categories).filter_by(name=catalog_name).one()
    get_all_items_for_category = session.query(Items).filter_by(category_id=get_category_id.id)
    return render_template('listitems.html',a_c=all_catagories,a_i=get_all_items_for_category,c_n=get_category_id.name)

#list discription about certin item in certin catalog
@app.route('/catalog/<string:catalog_name>/<string:item_name>/')
def aboutItem(catalog_name,item_name):
    get_category_id = session.query(Categories).filter_by(name=catalog_name).one()
    item  = session.query(Items).filter_by(title=item_name,category_id= get_category_id.id).one()
    return render_template('aboutitem.html', item = item, category=get_category_id)

###CRUD--ITEM###

#edit catalog item
@app.route('/catalog/<string:catalog_name>/<string:item_name>/edit', methods=['GET','POST'])
def editItem(catalog_name,item_name):
    #if 'username' not in login_session:
    #    return redirect('/login')
    #else:
    results = session.query(Categories).all()
    get_category_id = session.query(Categories).filter_by(name=catalog_name).one()
    editItem = session.query(Items).filter_by(title=item_name,category_id= get_category_id.id).one()
    if request.method == 'POST':
        if request.form['title']:
            editItem.title = request.form['title']
        if request.form['description']:
            editItem.description = request.form['description']
        if request.form.get('categories'):
            find_category = session.query(Categories).filter_by(name=request.form.get('categories')).one()
            editItem.category = find_category
        session.add(editItem)
        session.commit()
        output = redirect(url_for('showAllCategories'))
        return output
    else:
        output = render_template('itemedit.html',category = get_category_id, item= editItem, r=results)
        return output

#delete catalog item
@app.route('/catalog/<string:catalog_name>/<string:item_name>/delete', methods=['GET','POST'])
def deleteItem(catalog_name,item_name):
    #if 'username' not in login_session:
    #    return redirect('/login')
    results = session.query(Categories).all()
    get_category_id = session.query(Categories).filter_by(name=catalog_name).one()
    deleteitem = session.query(Items).filter_by(title=item_name,category_id= get_category_id.id).one()
    if request.method == 'POST':
        session.delete(deleteitem)
        session.commit()
        output = redirect(url_for('showAllCategories'))
        return output
    else:
        output = render_template('itemdelete.html',category = get_category_id, item= deleteitem, r=results)
        return output

#create a new catalog item
@app.route('/catalog/<string:catalog_name>/item/new', methods=['GET','POST'])
def newItem(catalog_name):
    #if 'username' not in login_session:
    #    return redirect('/login')
    #else:
    results = session.query(Categories).all()
    get_category_id = session.query(Categories).filter_by(name=catalog_name).one()

    if request.method == 'POST':
        find_category = session.query(Categories).filter_by(name=request.form.get('categories')).one()
        createItem = Items(title= request.form['title'], description =request.form['description'],category = find_category)
        session.add(createItem)
        session.commit()
        output = redirect(url_for('showAllCategories'))
        return output
    else:
        output = render_template('newitem.html',category = get_category_id, r=results)
        return output
# ---JSON---- #
@app.route('/catalog/<string:catalog_name>/items/JSON')
def jsonItemListForCatelog():
    pass
@app.route('/catalog/all/JSON')
def jsonAll():
    return "json all"
@app.route('/catalog/<string:catalog_name>/<string:item_name>/JSON')
def jsonItem():
    pass
#---USER INFO HELPERS---#

# User Helper Functions


def createUser(login_session):
    new_user = Users(name=login_session['username'], email=login_session[
        'email'])
    session.add(new_user)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(Users).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = "yum_yum_key"
    app.debug = True
    port = int(os.environ.get('PORT',8080))
    app.run(host = '0.0.0.0', port = port)

