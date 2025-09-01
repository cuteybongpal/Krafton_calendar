from db import dbTable, dbConnector;
import bcrypt

class UserRepository:
    def __init__(self, db:dbConnector):
        self.table = dbTable(db.db, "Users")
    
    def getUser(self, userId):
        return self.table.select({"userId" : userId})
    
    def addUser(self, userId, password):
        user = self.getUser(userId)
        if user != None:
            return False
        self.table.insert({"userId" : userId, "password" : bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())})
        return True

    def isSuccessLogin(self, userId, password):
        user = self.getUser(self, userId)
        if user == None:
            return False
        
        if not(bcrypt.checkpw(password, user["password"])):
            return False
        
        return True
