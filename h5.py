# -*- coding:utf-8 -*-
import hashlib
import random
import string
import time

from flask import Flask, render_template, request, jsonify, current_app, flash, redirect, url_for, session
from flask_cache import Cache
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import requests

from bdmap import BDMap
from config import Config
from responses import not_found, bad_request

app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
CORS(app)
cache = Cache(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sign', methods=['POST'])
def s():
    url = request.json.get('url')
    nonce_str = request.json.get('nonce_str')
    timestamp = request.json.get('timestamp')
    if not url or not nonce_str or not timestamp:
        return bad_request('params less')
    sign = Sign(url, nonce_str, timestamp).sign()
    return jsonify({
        'app_id': current_app.config['WX_APP_ID'],
        'sign': sign.get('signature')
    })


@app.route('/user', methods=['POST'])
def user():
    name = request.form.get('name')
    f = request.form.get('from')
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
    elif u.fr != f:
        u.fr = f
        u.distance = BDMap().get_distance(f)
        if u.distance:
            u.price = u.distance
        db.session.add(u)
        db.session.commit()
    return jsonify({
        'price': u.price,
        'share_url': '/' + u.token,
        'distance': u.distance,
        'all_user': User.count_user()
    })


@app.route('/<string:t>', methods=['GET', 'POST'])
def token(t):
    data = int(t)
    u = User.query.filter_by(id=data).first()
    if not u:
        return not_found('url not found')
    if session.get('has_click_for_user_' + str(data), -1) == data:
        flash(u'你已经为该用户砍价过了')
        return redirect(url_for('.index'))
    session['has_click_for_user_' + str(data)] = data
    if u.price > 10:
        u.price = u.price - 10
    else:
        u.price = 0
    db.session.add(u)
    db.session.commit()
    flash(u'为好友砍价成功')
    return redirect(url_for('.index'))
    # s = Serializer(current_app.config['SECRET_KEY'])
    # try:
    #     data = s.loads(t)
    # except Exception:
    #     return not_found('url not found')
    # if session.get('has_click_for_user_' + str(data.get('token')), -1) == data.get('token'):
    #     flash(u'你已经为该用户砍价过了')
    #     return redirect(url_for('.index'))
    # session['has_click_for_user_' + str(data.get('token'))] = data.get('token')
    # u = User.query.filter_by(id=data.get('token')).first()
    # if not u:
    #     return not_found('user not found')
    # if u.price > 10:
    #     u.price = u.price - 10
    # else:
    #     u.price = 0
    # db.session.add(u)
    # db.session.commit()
    # flash(u'为好友砍价成功')
    # return redirect(url_for('.index'))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)
    fr = db.Column(db.String(200))
    to = db.Column(db.String(200), default=u'衡阳')
    price = db.Column(db.Integer, default=0)
    distance = db.Column(db.Integer, default=0)
    token = db.Column(db.String(200))

    def generate_token(self):
        # s = Serializer(current_app.config['SECRET_KEY'], 60 * 60 * 24 * 365)
        self.token = self.id # s.dumps({'token': self.id})
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def count_user():
        return len(User.query.all())

    def __repr__(self):
        return '<user %r>' % self.name


@cache.memoize(timeout=60*60)
def get_jsapi(self):
    res = requests.request('get',
                  'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(
                      self.app_id,
                      self.secret))
    res = requests.request('GET', 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={}&type=jsapi'.format(
        res.json().get('access_token')))
    return res.json().get('ticket')


class Sign(object):
    def __init__(self, url, nonce_str, timestamp):
        self.app_id = current_app.config['WX_APP_ID']
        self.secret = current_app.config['WX_SECRET']
        self.nonce_str = nonce_str
        self.timestamp = timestamp
        self.ret = {
            'nonceStr': self.nonce_str,
            'jsapi_ticket': self.get_jsapi(),
            'timestamp': self.timestamp,
            'url': url,

        }

    # def __create_nonce_str(self):
    #     return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
    #
    # def __create_timestamp(self):
    #     return int(time.time())

    def sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        return self.ret

    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(cls, '_instance'):
    #         cls._instance = object.__new__(cls, *args, **kwargs)
    #     return cls._instance


if __name__ == '__main__':
    # db.drop_all()
    # db.create_all()
    app.run(debug=True)
