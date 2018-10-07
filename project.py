from flask import Flask, render_template, url_for, redirect, request, flash, jsonify
import os, random, string, json, requests, httplib2
from datetime import datetime
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Users,Categories,Items,Base, Recent

from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response


CLIENT_ID = "684439677805-mdi6vnclev40k51oqama45p3vo461qdr.apps.googleusercontent.com"


print(datetime.now())

REDIRECT_URI = '/gconnect'
APPLICATION_NAME = "Catalog Web App"

app = Flask(__name__)
#csrf = CSRFProtect(app)

sql_lite_db = create_engine('sqlite:///catalogdb.db')
Base.metadata.bind = sql_lite_db
DBsession = sessionmaker(bind = sql_lite_db)
db_session = DBsession()

SECRET_KEY = os.urandom(24)



## -- ## LOGIN

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/googleconnect', methods=['POST'])
def googleconnect():
    # Obtain authorization code
    code = request.data
    # Upgrade the authorization code into a credentials object
    oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
    oauth_flow.redirect_uri = 'postmessage'
    credentials = oauth_flow.step2_exchange(code)

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    #h = httplib2.Http()
    #result = json.loads(h.request(url, 'GET')[1])
    gplus_id = credentials.id_token['sub']
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['email'] = data['email']
    login_session['username'] = data['name']
    #crate a user in DB
    #Users(email=login_session['email'],name=login_session['username'])

    return "Logged in as " + login_session['username']


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html',STATE=state)



## -- ## LOGIN
















#list all catalogs
@app.route('/catalog/')
def showAllCategories():
    recently = db_session.query(Recent).order_by(desc(Recent.created_date)).all()
    results = db_session.query(Categories).all()
    return render_template('catagory.html',a_c=results,a_r=recently)

#list all items for certin catalog
@app.route('/catalog/<string:catalog_name>/items')
def catalogItems(catalog_name):
    all_catagories = db_session.query(Categories).all()
    get_category_id = db_session.query(Categories).filter_by(name=catalog_name).one()
    get_all_items_for_category = db_session.query(Items).filter_by(category_id=get_category_id.id)
    return render_template('listitems.html',a_c=all_catagories,a_i=get_all_items_for_category,c_n=get_category_id.name)

#list discription about certin item in certin catalog
@app.route('/catalog/<string:catalog_name>/<string:item_name>/')
def aboutItem(catalog_name,item_name):
    get_category_id = db_session.query(Categories).filter_by(name=catalog_name).one()
    item  = db_session.query(Items).filter_by(title=item_name, category_id= get_category_id.id).first()
    return render_template('aboutitem.html', item = item, category=get_category_id)

###CRUD--ITEM###

#edit catalog item
@app.route('/catalog/<string:catalog_name>/<string:item_name>/edit', methods=['GET','POST'])
def editItem(catalog_name,item_name):
    if 'username' not in login_session:
        print(login_session)
        return "Please log in :)"
    else:
        results = db_session.query(Categories).all()
        get_category_id = db_session.query(Categories).filter_by(name=catalog_name).one()
        editItem = db_session.query(Items).filter_by(title=item_name, category_id= get_category_id.id).first()
        if request.method == 'POST':
            if request.form['title']:
                editItem.title = request.form['title']
            if request.form['description']:
                editItem.description = request.form['description']
            if request.form.get('categories'):
                find_category = db_session.query(Categories).filter_by(name=request.form.get('categories')).one()
                editItem.category = find_category
            db_session.add(editItem)
            db_session.commit()
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
    results = db_session.query(Categories).all()
    get_category_id = db_session.query(Categories).filter_by(name=catalog_name).one()
    deleteitem = db_session.query(Items).filter_by(title=item_name, category_id= get_category_id.id).first()
    deleteRecent = db_session.query(Recent).filter_by(item_id=deleteitem.id).first()
    if request.method == 'POST':
        db_session.delete(deleteitem)
        db_session.commit()
        db_session.delete(deleteRecent)
        db_session.commit()
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
    results = db_session.query(Categories).all()
    get_category_id = db_session.query(Categories).filter_by(name=catalog_name).one()

    if request.method == 'POST':
        find_category = db_session.query(Categories).filter_by(name=request.form.get('categories')).one()
        createItem = Items(title= request.form['title'], description =request.form['description'],category = find_category)
        db_session.add(createItem)
        db_session.commit()
        output = redirect(url_for('showAllCategories'))
        recent = Recent(item=createItem,created_date=datetime.now())
        db_session.add(recent)
        db_session.commit()
        return output
    else:
        output = render_template('newitem.html',category = get_category_id, r=results)
        return output


## ---JSON---- ##

#shows all items in a catalog
@app.route('/catalog/<string:catalog_name>/items/JSON')
def jsonItemListForCatelog(catalog_name):
    get_category_id = db_session.query(Categories).filter_by(name=catalog_name).one()
    items = db_session.query(Items).filter_by(category_id=get_category_id.id).all()
    return jsonify(Items=[i.serialize for i in items])
#shows all items and all catalogs
@app.route('/catalog/all/JSON')
def jsonAll():
    get_category = db_session.query(Categories).all()
    get_all_items = db_session.query(Items).all()
    #n = get_category + get_all_items
    return jsonify(Categories=[i.serialize for i in get_category],Items=[i.serialize for i in get_all_items])
#shows 1 item in a given catalog
@app.route('/catalog/<string:catalog_name>/<string:item_name>/JSON')
def jsonItem(catalog_name,item_name):
    get_category_id = db_session.query(Categories).filter_by(name=catalog_name).one()
    item  = db_session.query(Items).filter_by(title=item_name, category_id= get_category_id.id).one()
    return jsonify(item.serialize)
#---USER INFO HELPERS---#

# User Helper Functions


def createUser(login_session):
    new_user = Users(name=login_session['username'], email=login_session[
        'email'])
    db_session.add(new_user)
    db_session.commit()
    user = db_session.query(Users).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = db_session.query(Users).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = db_session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = SECRET_KEY
    app.debug = True
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    port = int(os.environ.get('PORT',8080))
    app.run(host = '0.0.0.0', port = port)

