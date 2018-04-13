from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

from threading import Semaphore

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Database URL
BASE_URL = "https://volunteer-computing.firebaseio.com/primality-tests/"

# Semaphore to prevent race condition if there are multiple
# get requests to `get_working_url` at once.
read_semaphore = Semaphore(value=1)


class PrimeList(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    set_number = db.Column(db.Integer, unique=True)
    state = db.Column(db.String(40))  # Can be 'checked','checking','yet_to_be_checked'
    assigned_to = db.Column(db.String(40))  # The client name or ID its assigned to

    def __init__(self, set_number, state, assigned_to):
        self.set_number = set_number
        self.state = state
        self.assigned_to = assigned_to


class PrimeListSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('set_number', 'state')


prime_schema = PrimeListSchema(many=True)


# endpoint to get the state of primes_list
@app.route("/get_state", methods=["GET"])
def get_shared_resource_state():
    primes_list = PrimeList.query.all()
    result = prime_schema.dump(primes_list)
    return jsonify(result)


# endpoint to get a working URL for the client
# This will call synchronization problems
@app.route("/get_working_url", methods=["GET"])
def get_working_url():

    read_semaphore.acquire()
    
    # Get a unvisited/untested prime set
    prime = PrimeList.query.filter_by(state='yet_to_be_checked').first()
    prime.state = 'checking'
    url = BASE_URL + "prime_sets/" + str(prime.set_number) + "/set/.json"

    # DB has changed. Update it
    db.session.commit()
    
    read_semaphore.release()

    return jsonify(url)


# endpoint to update prime_list
# This happens when a client script checks a set of primes
# and updates the server
@app.route("/update", methods=["PUT"])
def database_update():

    read_semaphore.acquire()

    # `divisor` can be -1(no divisor found) or a natural number
    divisor = int(request.json['divisor'])
    set_number = int(request.json['set_number'])

    if divisor == -1:
        # update prime list
        prime = PrimeList.query.filter_by(set_number=set_number).first()
        prime.state = 'checked'
        db.session.commit()
    else:
        prime = PrimeList.query.filter_by(set_number=set_number).first()
        prime.state = 'found'
        db.session.commit()
    # TODO else do something

    read_semaphore.release()

    return jsonify("Shared variable updated successfully")


# endpoint to reset prime checking list
@app.route("/reset", methods=["GET"])
def reset_shared_variable():

    # Drop old tables and create new one
    db.drop_all()
    db.create_all()
    db.session.commit()

    # Create first 50 sets in DB
    for i in range(50):
        prime = PrimeList(set_number=i, state='yet_to_be_checked',assigned_to='None')
        db.session.add(prime)
        db.session.commit()

    return jsonify("Shared variable reset successfully")


if __name__ == '__main__':
    app.run(debug=True)
