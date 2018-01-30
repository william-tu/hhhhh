# -*- coding:utf-8 -*-
from flask import Flask, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from bdmap import BDMap
from config import Config
from responses import not_found, bad_request

app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user', methods=['POST'])
def user():
    name = request.form['name']
    f = request.form['from']
    if not name or not f:
        return bad_request('params error')
    u = User.query.filter_by(name=name).first()
    if not u:
        u = User(name=name)
        u.fr = f
        u.distance = BDMap().get_distance(f)
        if u.distance:
            u.price = u.distance
        db.session.add(u)
        db.session.commit()
        u.generate_token()

    return jsonify({
        'price': u.price,
        'share_url': '/token/' + u.token,
        'distance': u.distance,
        'all_user': User.count_user()
    })


@app.route('/token/<string:t>')
def token(t):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(t)
    except Exception:
        return not_found('url not found')
    u = User.query.filter_by(id=data.get('token')).first()
    if not u:
        return not_found('user not found')
    if u.price > 10:
        u.price = u.price-10
    else:
        u.price = 0
    db.session.add(u)
    db.session.commit()
    flash(u"为好友砍价成功")
    return redirect(url_for('.index'))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)
    fr = db.Column(db.String(200))
    to = db.Column(db.String(200))
    price = db.Column(db.Integer, default=0)
    distance = db.Column(db.Integer, default=0)
    token = db.Column(db.String(200))

    def generate_token(self):
        s = Serializer(current_app.config['SECRET_KEY'], 60*60*24*365)
        self.token=s.dumps({'token': self.id})
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def count_user():
        return len(User.query.all())

    def __repr__(self):
        return '<user %r>' % self.name


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    app.run(debug=True)
