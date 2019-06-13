
from flask import Blueprint, request, abort, jsonify
from jinja2 import TemplateNotFound
import os

verification_token=os.environ.get('VERIFICATION_TOKEN')




slash = Blueprint('slash', __name__, template_folder='templates')
@slash.route('/slash_up')
def slash_up():
    "Are we alive?"
    return "<html><body><h1>Tikkat /slash is up</h1></body></html>"

@slash.route('/rj75ud/slash', methods=['POST'])
def slashcmd():
    "Simple slash command"
    if request.form.get('token'):
        if request.form['token'] == verification_token:
            payload = {'text': 'Meow - Tikkat does not say much yet.'}
            print(jsonify(payload))
            return jsonify(payload)
        print("Error - token not correct")
        abort(404)
    else:
        print("Error - request not correct")
        abort(404)




