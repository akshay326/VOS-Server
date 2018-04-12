from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


# Assuming there are 50 prime sets
primes_list = {}

# Database URL
BASE_URL = "https://volunteer-computing.firebaseio.com/primality-tests/"


# endpoint to get the state of primes_list
@app.route("/get_state", methods=["GET"])
def get_shared_resource_state():
    return jsonify(primes_list)


# endpoint to get a working URL for the client
# This will call synchronization problems
@app.route("/get_working_url", methods=["GET"])
def user_detail():

    # Find which set is to be checked
    i = 0
    for i in range(len(primes_list)):
        if primes_list[i] == 'yet_to_be_checked':
            primes_list[i] = 'checking'

    # Return the corresponding URL to download dataset
    url = BASE_URL+"prime_sets/"+str(i)+"/set/.json"

    return jsonify(url)


# endpoint to update prime_list
# This happens when a client script checks a set of primes
# and updates the server
@app.route("/update", methods=["PUT"])
def user_update():

    # `divisor` can be -1(no divisor found) or a natural number
    divisor = request.json['divisor']
    set_number = request.json['set_number']

    if divisor == -1:
        # update prime list
        primes_list[set_number] = 'checked'
    # TODO else do something

    return jsonify("Shared variable updated successfully")


# endpoint to reset prime checking list
@app.route("/reset", methods=["GET"])
def reset_shared_variable():

    for i in range(50):
        primes_list[i] = 'yet_to_be_checked'

    return jsonify("Shared variable reset successfully")


if __name__ == '__main__':
    app.run(debug=True)