#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
import os
import bottle
from bottle import response, run, request, post
import re, json
import hashlib
from uuid import uuid4

from peewee import SqliteDatabase

from models.db_user import DBUser
from models.db_sessions import DBSessions
from models.db_place import DBPlace
from models.db_route import DBRoute
from models.db_route_places import DBRoutePlaces



def login(email, password, ip):
    answer = ''
    result = DBUser.select(DBUser.id).where((DBUser.email == email) & (DBUser.password == hashlib.sha256(password.encode('utf-8')).hexdigest()))
    if result and result.count() == 1:
        for item in result:
            answer = uuid4()
            DBSessions.create(id = item.id, token = answer)
    else:
        print("No info")
    print("--",answer)
    return {'token':str(answer)}


def add_place(title, description, lat, lng, image):
    try:
        DBPlace.create(title = title, description = description, lat = lat, lng = lng, image = image, force_insert=True)
        return json.dumps({"status": 200})
    except:
        return "Error"

def remove_place(id_place):
    try:
        DBPlace.delete().where( DBPlace.id == id_place).execute()
        return "OK"
    except:
        return "Error"

def get_place(id_place):
    print(id_place)
    place = DBPlace.select().where(DBPlace.id == id_place).get()
    place_json = json.dumps({
        'name': place.title,
        'description': place.description,
        'lat': place.lat,
        'lng': place.lng,
        'image': place.image
    })
    print("-->", place, place_json)
    return place_json

def get_places():
    places = list()
    querry = DBPlace.select().execute()
    for place in querry:
        places.append({
            'id': place.id,
            'name': place.title,
            'description': place.description,
            'lat': place.lat,
            'lng': place.lng,
            'image': place.image
        })
    return json.dumps(places)


def add_route(name,description, total_places, places, image):
    try:
        DBRoute.create(title=name, description=description, total_places=total_places, image = image, force_insert=True)
    except:
        return "Error"

    route_id = DBRoute.select(DBRoute.id).order_by(DBRoute.id.desc()).get()

    try:
        for item in places:
            DBRoutePlaces.create(id_route=route_id, id_place=item)
        return "OK"
    except:
        remove_route(route_id)
        return "Error"


def remove_route(id_route):
    try:
        DBRoute.delete().where(DBRoute.id == id_route).execute()
        return "OK"
    except:
        return "Error"

def get_route(id_route):
    return DBRoute.select().where(DBRoute.id == id_route).execute()


def get_routes():
    routes = list()
    querry = DBRoute.select().execute()
    for route in querry:
        routes.append({
            'name': route.title,
            'description': route.description,
            'total_places': route.total_places,
            'image': route.image
        })
    return json.dumps(routes)

#######################
    # SERVER #
#######################

class EnableCors(object):
    def apply(self, fn, context):
        def _enabled_cors(*args, **kwargs):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
            if bottle.request.method != 'OPTIONS':
                return fn(*args, **kwargs)
        return _enabled_cors

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024
app = bottle.app()

@app.route('/', method=['OPTIONS', 'GET'])
def greeting():
    return "Hello"

@app.route('/login', method=['OPTIONS', 'POST'])
@app.route('/login/', method=['OPTIONS', 'POST'])
def loginUser():
    response.headers['Content-type'] = 'application/json'
    email = request.json['email']
    password = request.json['password']
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
    print(email, password)
    if email and password:
        return login(email, password, client_ip)
    return "Error"

@app.route('/admin', method=['OPTIONS', 'POST'])
@app.route('/admin/', method=['OPTIONS', 'POST'])
def adminUser():
    response.headers['Content-type'] = 'application/json'
    try:
        db = SqliteDatabase('data/lo.db')
        db.create_tables([DBUser])
        db.create_tables([DBSessions])
        db.create_tables([DBPlace])
        db.create_tables([DBRoute])
        db.create_tables([DBRoutePlaces])
    except Exception as ex:
        pass
    DBUser.create(id = 1, email = "admin", password = "admin")
    return "Ok"

@app.route('/logout', method=['OPTIONS', 'POST'])
@app.route('/logout/', method=['OPTIONS', 'POST'])
def logout():
    try:
        token = request.headers['Authorization']
        print(token)
        if DBSessions.select().where(DBSessions.token == token).count() == 1:
            DBSessions.delete().where(DBSessions.token == token).execute()
            return "Ok"
        return "Error"
    except:
        return "Error"

@app.route('/add_place', method=['OPTIONS', 'POST'])
@app.route('/add_place/', method=['OPTIONS', 'POST'])
def add_place_server():
    try:
        token = request.headers['Authorization']
        print(DBSessions.select().where(DBSessions.token == token).count())
        if DBSessions.select().where(DBSessions.token == token).count() == 1:
            print("!!!")
            print(request.json.get('image'))
            return add_place(
                request.json["name"],
                request.json["description"],
                request.json["lat"],
                request.json["lng"],
                request.json.get('image')
            )
        else:
            return "Error"
    except:
        return "Error"

@app.route('/remove_place', method=['OPTIONS', 'DELETE'])
@app.route('/remove_place/', method=['OPTIONS', 'DELETE'])
def remove_place_server():
    try:
        token = request.headers['Authorization']
        if DBSessions.select().where(DBSessions.token == token).count() == 1:
            # request.forms.get("title")
            return remove_place(
                request.forms.get("id")
            )
        return "Error"
    except:
        return "Error"

@app.route('/get_places', method=['OPTIONS', 'GET'])
@app.route('/get_places/', method=['OPTIONS', 'GET'])
def get_places_server():
    response.headers['Content-type'] = 'application/json'
    try:
        token = request.headers['Authorization']
        if DBSessions.select().where(DBSessions.token == token).count() == 1:
            return get_places()
        return "Error"
    except:
        return "Error"

@app.route('/get_place/<id>', method=['OPTIONS', 'GET'])
def get_place_id_server(id):
    try:
        token = request.headers['Authorization']
        if DBSessions.select().where(DBSessions.token == token).count() == 1:
            return get_place(id)
        return "Error"
    except:
        return "Error"

@app.route('/get_routes', method=['OPTIONS', 'GET'])
@app.route('/get_routes/', method=['OPTIONS', 'GET'])
def get_places_server():
    response.headers['Content-type'] = 'application/json'
    try:
        token = request.headers['Authorization']
        if DBSessions.select().where(DBSessions.token == token).count() == 1:
            return get_routes()
        return "Error"
    except:
        return "Error"

@app.route('/add_route', method=['OPTIONS', 'POST'])
@app.route('/add_route/', method=['OPTIONS', 'POST'])
def add_route_server():
    try:
        token = request.headers['Authorization']
        if DBSessions.select().where(DBSessions.token == token).count() == 1:
            return add_route(
                request.json["name"],
                request.json["description"],
                request.json["total_places"],
                request.json["places"],
                request.json.get('image')
            )
        else:
            return "Error"
    except:
        return "Error"

app.install(EnableCors())
#
# @app.hook('after_request')
# def enable_cors():
#     print("!!!")
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
#     response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

# app.run(port=8002)

app.run(host='0.0.0.0', port=os.environ.get("PORT", 5000))