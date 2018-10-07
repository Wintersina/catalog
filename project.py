from flask import Flask, render_template, url_for, redirect, request, flash, jsonify
import os, random, string, json, requests, httplib2
from datetime import datetime
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Users,Categories,Items,Base, Recent

#from flask_wtf.csrf import CSRFProtect

print(datetime.now())

REDIRECT_URI = '/gconnect'
APPLICATION_NAME = "Catalog Web App"

app = Flask(__name__)
#csrf = CSRFProtect(app)

sql_lite_db = create_engine('sqlite:///catalogdb.db')
Base.metadata.bind = sql_lite_db
DBsession = sessionmaker(bind = sql_lite_db)
session = DBsession()

SECRET_KEY = os.urandom(24)





#list all catalogs
@app.route('/catalog/')
def showAllCategories():
    recently = session.query(Recent).order_by(desc(Recent.created_date)).all()
    results = session.query(Categories).all()
    return render_template('catagory.html',a_c=results,a_r=recently)

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
    item  = session.query(Items).filter_by(title=item_name,category_id= get_category_id.id).first()
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
    editItem = session.query(Items).filter_by(title=item_name,category_id= get_category_id.id).first()
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
    deleteitem = session.query(Items).filter_by(title=item_name,category_id= get_category_id.id).first()
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
        recent = Recent(item=createItem,created_date=datetime.now())
        session.add(recent)
        session.commit()
        return output
    else:
        output = render_template('newitem.html',category = get_category_id, r=results)
        return output


## ---JSON---- ##

#shows all items in a catalog
@app.route('/catalog/<string:catalog_name>/items/JSON')
def jsonItemListForCatelog(catalog_name):
    get_category_id = session.query(Categories).filter_by(name=catalog_name).one()
    items = session.query(Items).filter_by(category_id=get_category_id.id).all()
    return jsonify(Items=[i.serialize for i in items])
#shows all items and all catalogs
@app.route('/catalog/all/JSON')
def jsonAll():
    get_category = session.query(Categories).all()
    get_all_items = session.query(Items).all()
    #n = get_category + get_all_items
    return jsonify(Categories=[i.serialize for i in get_category],Items=[i.serialize for i in get_all_items])
#shows 1 item in a given catalog
@app.route('/catalog/<string:catalog_name>/<string:item_name>/JSON')
def jsonItem(catalog_name,item_name):
    get_category_id = session.query(Categories).filter_by(name=catalog_name).one()
    item  = session.query(Items).filter_by(title=item_name,category_id= get_category_id.id).one()
    return jsonify(item.serialize)
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
    app.secret_key = SECRET_KEY
    app.debug = True
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    port = int(os.environ.get('PORT',8080))
    app.run(host = '0.0.0.0', port = port)

