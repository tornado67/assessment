from flask import Blueprint

views = Blueprint('views',__name__)

@views.route('/plotwise')
def plotwise():
    return {"result":"success"}


@views.route('/world')
def world():
    return {"result":"success"}