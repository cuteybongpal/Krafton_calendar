from pymongo import MongoClient

class dbConnector:
    def __init__(self):
        self.client = MongoClient("mongodb://rootadmin:관리자강비@127.0.0.1:27017/admin?authSource=admin")
        self.database = self.client["MyDb"]

class dbTable:
    def __init__(self, db, tableName):
        self.table = db[tableName]

    def insert(self, datadict):
        self.table.insert_one(datadict)

    def delete(self, filter):
        self.table.delete_many(filter)

    def update(self, filter, newValue):
        self.table.update_many(filter, newValue)
    
    def select_one(self, filter):
        return self.table.find_one(filter)
    
    def select_many(self, filter):
        return self.table.find(filter)
        
