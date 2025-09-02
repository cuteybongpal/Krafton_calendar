from flask import Flask, redirect, request, session, make_response
from db import dbConnector
from user import UserRepository
import jinjaUtil
import secrets

dbconnector = None
userRepo = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'withoutme'

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

@app.route('/')
def hello_world():
    datadict =  {
        "userId" : session.get('userId')
    }
    if (session.get('userId') == 'admin@admin'):
        return jinjaUtil.render("admin", datadict)
    else:
        return jinjaUtil.render("student", datadict)

@app.route('/signup', methods=['POST'])
def signup():
    id = request.form.get('email')
    pw =request.form.get('pw')
    isSuccess = userRepo.addUser(id, pw)
    print(isSuccess)
    return redirect('/')

@app.route('/login', methods=['POST'])
def llllll():
    id = request.form.get('email')
    pw = request.form.get('pw')
    isSuccess = userRepo.isSuccessLogin(id, pw)
    print(id)
    if not isSuccess['condition']:
        return jinjaUtil.render('error', {"errorCode" : isSuccess["errorCode"]});
    sessionId = secrets.token_urlsafe(32)
    session['sessionId'] = sessionId
    session['userId'] = id
    print(id)
    return redirect('/')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('sessionId')
    session.pop('userId')
    return redirect('/')
if __name__ == '__main__':
    dbconnector = dbConnector()
    userRepo = UserRepository(dbconnector)
    app.run()