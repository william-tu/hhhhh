from flask import Flask, render_template, request, jsonify, current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_sqlalchemy import SQLAlchemy
from responses import not_found,bad_request
from config import Config
from bdmap import BDMap

app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/user', methods=['POST'])
def user():
    name = request.form['name']
    f = request.form['from']
    t = request.form['to']
    if not name or not f or not t:
        return bad_request('params error')
    u = User.query.filter_by(name=name).first()
    if not u:
        u = User(name=name)
        u.fr = f
        u.to = t
        u.distance = BDMap().get_distance(f, t)
        if u.distance:
            u.price = u.distance
        db.session.add(u)
        db.session.commit()
        u.generate_token()

    return jsonify({
        'price': u.price,
        'share_url': '/token/' + u.token,
        'distance': u.distance
    })


@app.route('/token/<string:t>')
def token(t):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(t)
    except Exception:
        return not_found('url not found')
    print data
    u = User.query.filter_by(id=data.get('token')).first()
    if not u:
        return not_found('user not found')
    if u.price > 10:
        u.price = u.price-10
    else:
        u.price = 0
    db.session.add(u)
    db.session.commit()
    print u.name
    return jsonify({
        'data': 'successful'
    })


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

    def __repr__(self):
        return '<user %r>' % self.name


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    app.run(debug=True)
