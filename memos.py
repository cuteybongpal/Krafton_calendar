from db import dbConnector, dbTable;
from bson import ObjectId

class memo:
    def __init__(self, startTime, endTime, content, userName, id, date):
        self.startTime = startTime
        self.date = date
        self.endTime = endTime
        self.content = content
        self.user = userName
        # 쓰레기값 넣어도 됨 getMemos로 가져올 때 빼곤
        self.id = id

    def to_dict(self):
        return {
            "startTime" : self.startTime,
            "endTime" : self.endTime,
            "conetent" : self.content,
            "user" : self.user,
            "_id" : id
        }

class memoRepository:
    def __init__(self, db:dbConnector):
        dd = db.database
        tName = "Memos"
        self.table = dbTable(dd, tName)
    
    def getMemos(self, filter:dict):
        memolist = list(self.table.select_many(filter))
        memos = []

        for m in memolist:
            dict ={ "startTime":m["startTime"], "endTime":m["endTime"], "content":m["content"], "user":m["user"], "id":str(m["_id"]), "date" : m['date']}
            memos.append(dict)
        return memos
    
    def addMemo(self, memo: memo):
        try:
            self.table.insert({"startTime" : memo.startTime, "date" : memo.date, "endTime" : memo.endTime, "content" : memo.content, "user" : memo.user})
        except:
            return {"condition" : False, "errorCode" : "메모를 DB에 저장하는데 실패했습니다."}
        
        return {"condition" : True, "errorCode" : "메모 저장 성공!"}
    
    def removeMemo(self, id: str):
        self.table.delete({"_id": ObjectId(id)})

    def modifyMemo(self, id:str, data:dict):
        self.table.update({"_id" : ObjectId(id)}, {'$set': data})
