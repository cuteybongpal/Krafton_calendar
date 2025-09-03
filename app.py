from flask import Flask, redirect, request, session, jsonify
from db import dbConnector
from user import UserRepository
from memos import memoRepository, memo
from meal import meal, mealRepository
from datetime import date
import jinjaUtil
import secrets

# 커리큘럼 API용 MongoDB 연결(분리 구성)
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLL_NAME  # 별도 config.py에 정의해 두세요.

dbconnector = None
userRepo = None
memoRepo = None
mealRepo = None

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
    
    meal = mealRepo.getMeal(date.today().isoformat())  
    
    datadict =  {
        "userId" : userId,
        "memos" : memos,
    }
    if (meal == None):
        datadict['meal'] = None
    else:
        datadict['meal'] = {"menu" : meal['menu']}
    
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

@app.route('/meal/add', methods=['POST'])
def addMeal():
    date = request.form.get('date')
    menu = request.form.get('meal')

    m = meal(date, menu)
    isSuccess = mealRepo.addMemo(m)
    return jinjaUtil.render('error' , {"errorCode" : isSuccess['errorCode']})

# MongoDB(커리큘럼) 연결
mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
mongo_db = mongo_client[DB_NAME]

import re
def weeks_sort_key(w: str) -> int:
    # "W02~W05" → 2, "W010" → 10
    m = re.match(r"W0?(\d+)", w or "")
    return int(m.group(1)) if m else 999

@app.get("/api/curriculum")
def api_curriculum():
    
    docs = list(mongo_db[COLL_NAME].find(
        {}, {"_id": 0, "weeks": 1, "description": 1}
    ))
    docs.sort(key=lambda d: weeks_sort_key(d.get("weeks", "")))
    if len(docs) == 0:
        return RuntimeError("intentional 500")
    return jsonify(docs), 200
        
    
if __name__ == '__main__':
    dbconnector = dbConnector()
    userRepo = UserRepository(dbconnector)
    memoRepo = memoRepository(dbconnector)
    mealRepo = mealRepository(dbconnector)
    app.run()