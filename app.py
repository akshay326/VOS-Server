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


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email


class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('username', 'email')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


# Main route
@app.route("/")
def main_page():
    return get_user()


# endpoint to create new user
@app.route("/user", methods=["POST"])
def add_user():
    username = request.form['username']
    email = request.form['email']
    print(username)
    print(email)
    new_user = User(username, email)
    result = user_schema.dump(new_user)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(result)


# endpoint to show all users
@app.route("/user", methods=["GET"])
def get_user():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)


# endpoint to get user detail by ID
@app.route("/user/<id>", methods=["GET"])
def user_detail(id):
    user = User.query.get(id)
    result = user_schema.dump(user)
    return jsonify(result)


# endpoint to update user
@app.route("/user/<id>", methods=["PUT"])
def user_update(id):
    user = User.query.get(id)
    username = request.json['username']
    email = request.json['email']

    user.email = email
    user.username = username

    db.session.commit()
    result = user_schema.dump(user)
    return jsonify(result)


# endpoint to delete user
@app.route("/user/<id>", methods=["DELETE"])
def user_delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    result = user_schema.dump(user)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)