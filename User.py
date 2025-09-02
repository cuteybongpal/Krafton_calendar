from db import dbConnector, dbTable;
import bcrypt

class UserRepository:
    def __init__(self, db:dbConnector):
        dd = db.database
        tName = "Users"
        self.table = dbTable(dd, tName)
    
    def getUser(self, userId):
        return self.table.select_one({"userId" : userId})
    
    def addUser(self, userId, password):
        user = self.getUser(userId)
        if user != None:
            return False
        self.table.insert({"userId" : userId, "password" : bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())})
        return True

    def isSuccessLogin(self, userId, password):
        user = self.getUser(userId)
        if user == None:
            return { "condition" : False, "errorCode" : "해당 유저가 존재하지 않습니다." }
        
        if not(bcrypt.checkpw(password.encode('utf-8'), user["password"])):
            return { "condition" : False, "errorCode" : "비밀번호가 일치하지 않습니다." }
        
        return { "condition" : True }
