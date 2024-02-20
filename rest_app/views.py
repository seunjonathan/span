'''
    If you need help setting up your python dev environment, MS have a
    nice tutorial here: https://code.visualstudio.com/docs/python/python-tutorial 
'''

import logging
import re

from datetime import datetime, timezone
from functools import wraps
from flask import jsonify, request, abort
from dotenv import load_dotenv

from . import app
from .services.Config import *
from .services.Delta import *

# logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# This is to disable INFO logs from azure - there are too many of them!
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
# or
# app.logger.basicConfig(level=logging.INFO)

load_dotenv()

# Startup debug info
startup_message={
    "version": VERSION,
    "container-tag": CONTAINER_VERSION
}
logger.info(startup_message)

# API Key decorator.
# See https://coderwall.com/p/4qickw/require-an-api-key-for-a-route-in-flask-using-only-a-decorator
def require_appkey(view_function):
    '''
        This method is a decorator that can be used to protect calls to the 
        web app methods. In this case, the protection is API-key based.
    '''
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if request.headers.get('api-key') and request.headers.get('api-key') == API_KEY:
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function


@app.route("/", methods=['GET'])
@require_appkey
def version():
    '''
        This endpoint can be used to verify which version of the code was deployed
    '''
    result = {
        'message': MESSAGE,
        'container':CONTAINER_VERSION,
        'version' : VERSION
        }
    return jsonify(result)


@app.route("/get_schedules", methods=['GET'])
@require_appkey
def schedule():
    '''
        Gets a table of schedules for the given date range
    '''
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date is not None and end_date is not None:
        path = 'silver'
        pandas_df = build_schedule_table(FS, 'processed', path, start_date, end_date, VESSEL_CODES_FILTER)
        # Drop the Z at the end of the time. Ref: https://dev.azure.com/seaspan-edw/DataOps/_workitems/edit/1168
        j = pandas_df.to_json(orient='records', date_format='iso')
        j_z_removed = re.sub(REGEX, '\\1', j)
        return j_z_removed
    else:
        return "Bad Request", 400

    
@app.route("/event", methods=['POST'])
@require_appkey
def event():
    '''
        Implemented for story https://dev.azure.com/seaspan-edw/DataOps/_workitems/edit/1862
        Used to POST an event. Here an event can be either a ferry arrival or departure event. 
    '''
    receipt_time = datetime.now(timezone.utc)
    body = request.get_json()
    process_event(body, receipt_time)
    return '', 200 # Gabriel asked for nothing to be retuned, not even 'OK'.
  