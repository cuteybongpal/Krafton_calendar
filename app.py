from flask import Flask, redirect, request, session
from db import dbConnector
from user import UserRepository
import jinjaUtil
import os

dbconnector = None
userRepo = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'withoutme'


@app.route('/')
def hello_world():
    return jinjaUtil.render("main", {})

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
    pw =request.form.get('pw')
    isSuccess = userRepo.isSuccessLogin(id, pw)
    if isSuccess:
        print("성공함")
        session['sessionId'] = id
        print(session['sessionId'])
    else:
        print("실패함")
    return redirect('/')

if __name__ == '__main__':
    dbconnector = dbConnector()
    userRepo = UserRepository(dbconnector)
    app.run()