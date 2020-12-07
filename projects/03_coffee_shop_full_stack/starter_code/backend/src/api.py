from logging import error
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json, sys
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def get_drinks():
    '''
    GET /drinks
        public endpoint
        contains only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    '''
    try:
        drinks = [drink.short() for drink in Drink.query.all()]
        return jsonify({
            'success': True,
            'drinks' : drinks
        }), 200
    except:
        abort(404)

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    '''
    GET /drinks-detail
        requires the 'get:drinks-detail' permission
        contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    '''
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        return jsonify({
            'success': True,
            'drinks' : drinks
        }), 200
    except:
        abort(404)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    '''
    POST /drinks
        requires the 'post:drinks' permission
        creates a new row in the drinks table
        contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
    '''
    error  = None
    body   = request.get_json()
    if body is None: abort(400)
    title  = body.get('title', None)
    recipe = body.get('recipe', None)
    try:
        if title is None or recipe is None: error = 400; return sys.exit()
        drink = Drink(
            title  = title,
            recipe = json.dumps(recipe)
        ).insert()
        drink_created = Drink.query.filter_by(title=title).one_or_none()
        return jsonify({
            'success': True,
            'drinks' : [drink_created.long()]
        }), 201
    except :
        abort(400)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    '''
    PATCH /drinks/<id>
        requires the 'patch:drinks' permission
        updates the corresponding row for <id>
        responds with a 404 error if <id> is not found
        contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
    '''
    error  = None
    body   = request.get_json()
    if body is None: abort(400)
    title  = body.get('title', None)
    recipe = body.get('recipe', None)
    try:
        if title is None and recipe is None: error = 400; return sys.exit()
        drink = Drink.query.filter_by(id=id).one_or_none()
        if drink is None: error = 404; return sys.exit()
        if title is None:
            drink.recipe = json.dumps(recipe)
            drink.update()
        elif recipe is None:
            drink.title = title
            drink.update()
        else:
            drink.title  = title
            drink.recipe = json.dumps(recipe)
            drink.update()
        return jsonify({
            'success': True,
            'drinks' : [drink.long()]
        }), 200
    except:
        if error == 400:
            abort(400)
        elif error == 404:
            abort(404)
        else:
            abort(500)

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    '''
    DELETE /drinks/<id>
        requires the 'delete:drinks' permission
        deletes the corresponding row for <id>
        responds with a 404 error if <id> is not found
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
    '''
    error = None
    try:
        drink = Drink.query.filter_by(id=id).one_or_none()
        if drink is None: error = 404; return sys.exit()
        drink.delete()
        return jsonify({
            'success': True,
            'delete' : drink.id
        }), 200
    except:
        abort(404) if (error == 404) else abort(422)

## Error Handling

@app.errorhandler(400)
def bad_request(error):
    '''
    Handles error 400
    '''
    return jsonify({
        'success': False,
        'error'  : 400,
        'message': 'Bad Request'
    }), 400

@app.errorhandler(404)
def not_found(error):
    '''
    Handles error 404
    '''
    return jsonify({
        'success': False,
        'error'  : 404,
        'message': 'Resource not Found'
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    '''
    Handles error 422
    '''
    return jsonify({
        'success': False,
        'error'  : 422,
        'message': 'Unprocessable Entity'
    }), 422

@app.errorhandler(500)
def unprocessable(error):
    '''
    Handles error 500
    '''
    return jsonify({
        'success': False,
        'error'  : 500,
        'message': 'Internal Server Error'
    }), 500

@app.errorhandler(AuthError)
def auth_error(error):
    '''
    Handles Auth Errors
    '''
    return jsonify({
        'success': False,
        'error'  : error.status_code,
        'message': error.error['description']
    }), error.status_code