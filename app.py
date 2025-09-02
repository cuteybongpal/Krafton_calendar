from flask import Flask, redirect, request, session, make_response
from db import dbConnector
from user import UserRepository
from memos import memoRepository, memo
import jinjaUtil
import secrets

dbconnector = None
userRepo = None
memoRepo = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'withoutme'

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

@app.route('/')
def hello_world():
    userId = session.get('userId')
    memos = memoRepo.getMemos({"user" : userId})

    datadict =  {
        "userId" : userId,
        "memos" : memos
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

@app.route('/memo/create', methods=['POST'])
def addMemo():
    userId = session.get('userId')
    if userId == None or userId == '':
        return jinjaUtil.render('error', {"errorCode" : "로그인을 하고 이용해주세요"})
    
    startTime = request.form.get('startTime')
    endTime = request.form.get('endTime')
    content = request.form.get('content')
    date = request.form.get('date')

    mem = memo(startTime, endTime, content, userId, 0, date)
    isSuccess = memoRepo.addMemo(mem) 
    if (not isSuccess['condition']):
        return jinjaUtil('error', {"errorCode" : isSuccess["errorCode"]})
    return redirect('/')

@app.route('/memo/delete', methods=['GET'])
def delMemo():
    id = request.args.get('id')
    memoRepo.removeMemo(id)
    return redirect('/')

@app.route('/memo/modify', methods=['POST'])
def modMemo():
    id = request.form.get('id')
    startTime = request.form.get('editStartTime')
    endTime = request.form.get('editEndTime')
    content = request.form.get('editContent')
    memoRepo.modifyMemo(id, {"endTime" : endTime, "startTime" : startTime, "content" : content})
    return redirect('/')


if __name__ == '__main__':
    dbconnector = dbConnector()
    userRepo = UserRepository(dbconnector)
    memoRepo = memoRepository(dbconnector)
    app.run()