from flask import request, jsonify 
from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from enum import Enum
import SIOTC.Operations as op
import SIOTC.DatabaseLayer as db
import re

# Checks what type of data is being sent and returns correct object
def CheckContentType():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        print('Json Message received')
        return request.json
    elif 'text/' in content_type:
        print('Text Message received')
        return request.data.decode('utf-8')
    else:
        return 'Content-Type not supported', 415
 

# Verifies that the json payload contains correct data, CHANGE ACCORDING TO DECIDED MESSAGE 
def VerifyJsonContent(content): 
    if(content['mac-adress']):
        print('Message verified')
        return True
    else:
        print('Content not abled to be verified or it does not match the intended format')
        return False
    
# Verifies that the string payload contains correct data, CHANGE ACCORDING TO DECIDED MESSAGE    
def VerifyStringContent(content):
    if("sys" in content):
        print('String Message Verified')
        return True
    else:
        print('Content not abled to be verified or it does not match the intended format')
        return False
    
def VerifyMacContent(content):
    regex_pattern = '^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(regex_pattern, content))

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Check if JWT exists and is valid
        verify_jwt_in_request()

        # Get the id from the JWT
        jwt_id = get_jwt_identity()

        user = jwt_id
        if not user:
            return jsonify({'message': 'Current user not provided.'}), 401

        user_role = op.GetSpecificFromColumnInTableWithSession(user, 'role_id', 'users')

        if user_role != 'System Administrator':
            return jsonify({'message': 'You do not have permission to access this endpoint.'}), 403
        return fn(*args, **kwargs)
    return wrapper


def device_ownership_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_jwt_identity()
        if not user:
            return jsonify({'message': 'Current user not provided.'}), 401
        dbsession, Base = db.GetSession()
        customerID = op.GetSpecificFromColumnInTable(dbsession, Base, user, 'customer_id', 'users')
        customerFK = op.GetSpecificFromColumnInTable(dbsession, Base, user, 'customer_id', 'devices')

        if customerID != customerFK:
            return jsonify({'message': 'User does not own device.'}), 403
        return f(*args, **kwargs)
    return wrapper