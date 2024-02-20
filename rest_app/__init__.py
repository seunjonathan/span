from flask import Flask  # Import the Flask class

app = Flask(__name__)    # Create an instance of the class for our use

'''
    For some reason, I get a TypeError: '<' not supported between instances of 'int' and 'str'
    This happens when coverting the exif_dict to a json in the response. Flask by default sorts the
    dictionary. By turning off sort we avoid the error.
    NOTE: In production, a unicorn server is used, not Flask, so we might still hit this error
'''
app.config['JSON_SORT_KEYS'] = False
