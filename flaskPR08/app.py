from datetime import datetime
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import hashlib
from captcha.image import ImageCaptcha
import re


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///first.db'
db = SQLAlchemy(app)

image = ImageCaptcha(width=280, height=90)
data = image.generate('hello17world')
image.write('hello17world','demo.png')

class Users(db.Model):
    id = db.Column(db.Integer,autoincrement=True, primary_key = True)
    username = db.Column(db.String(30), unique=True, nullable = False )
    password = db.Column(db.String(200), nullable = False)
    
    def __repr__(self):
        return f"id:{self.id}. user:{self.username}, password: {self.password}"
    
# with app.app_context():
#     db.create_all()

class Roles(db.Model):
    role_id = db.Column(db.Integer,autoincrement=True, primary_key = True)
    role_name = db.Column(db.String(200), nullable = False)

class Humans(db.Model):
    id = db.Column(db.Integer,autoincrement=True, primary_key = True)
    name = db.Column(db.String(20), nullable = True)
    surname = db.Column(db.String(40), nullable = True)
    login = db.Column(db.String(20), nullable = True)
    email = db.Column(db.String(40),  nullable = True)
    Role = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable = True)
    password = db.Column(db.String(100),  nullable = True)
    birthdate = db.Column(db.Date,  nullable = True)

    def __repr__(self):
        return super().__repr__()
    
with app.app_context():
    db.create_all()


@app.route("/home")
@app.route("/")
def home():
    return render_template('home.html')

@app.route("/private_kabinet", methods = ['POST', 'GET'])
def kabinet():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        login = request.form.get('login')
        email = request.form.get('email')
        password = request.form.get('password')
        birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d').date()
        humans = Humans(name = name, password = password, surname = surname, login = login, email=email, birthdate=birthdate)
        try:
            db.session.add(humans)
            db.session.commit()
                
            return redirect('/')
        except Exception as e: 
            print(e)
            return redirect('/')
    else:
        return render_template('private_kabinet.html')


@app.route("/register", methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        copy_password = password.encode()
        salt = username.encode()
        user = Users(username = username, password = str(hashlib.pbkdf2_hmac('sha256', copy_password, salt, 100)))
        print(type(hashlib.pbkdf2_hmac('sha256', copy_password, salt, 100)))
        try:
            db.session.add(user)
            db.session.commit()
                
                
            return redirect('/')
        except Exception as e: 
            print(e)
            return redirect('/')
    else:
        return render_template('register.html', a='demo.png')
    

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        use = Users.query.with_entities(Users.username).filter_by(username=username).first()
        result_use = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ]', '', str(use))
        pas = Users.query.with_entities(Users.password).filter_by(username=username).first()
        result_pas = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ]', '', str(pas))
        copy_password = password.encode()
        salt = username.encode()
        print(result_use, username)
        print(result_pas)
        print(str(hashlib.pbkdf2_hmac('sha256',copy_password,salt,100)))
        if result_use == username and result_pas == str(hashlib.pbkdf2_hmac('sha256',copy_password,salt,100)):
            return redirect ('/')
        else:
            print("Wrong login or password")
            return redirect ('login.html')
    else:
        return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True, ssl_context = ('cert.pem', 'key.pem'))


