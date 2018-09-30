from flask import Flask, render_template, url_for, redirect, request, flash, jsonify
import os
from sqlalchemy import create_engine, distinct
from sqlalchemy.orm import sessionmaker
from database_setup import Users,Categories,Items,Base

app = Flask(__name__)


sql_lite_db = create_engine('sqlite:///catalogdb.db')
Base.metadata.bind = sql_lite_db
DBsession = sessionmaker(bind = sql_lite_db)
session = DBsession()

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
