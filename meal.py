from db import dbConnector, dbTable;
from bson import ObjectId
import traceback

class meal:
    def __init__(self, date, menu):
        self.date = date
        self.menu = menu
        # 쓰레기값 넣어도 됨 getMemos로 가져올 때 빼곤
        self.id = id

    def to_dict(self):
        return {
            "date" : self.date,
            "menu" : self.menu
        }

class mealRepository:
    def __init__(self, db:dbConnector):
        dd = db.database
        tName = "Meals"
        self.table = dbTable(dd, tName)
    
    def getMeal(self, date: str):
        meal = self.table.select_one({"date" : date})
        if (meal == None):
            return None
        return meal
    
    def addMemo(self, meal: meal):
        m = self.getMeal(meal.date)
        
        try:
            if (m != None):
                self.table.update({"date" : meal.date},{'$set' : {"menu" : meal.menu}})
            else:
                self.table.insert({"date": meal.date, "menu" : meal.menu})
        except Exception as e:
            return {"condition" : False, "errorCode" : f"메뉴를 DB에 저장하는데 실패했습니다 {traceback.extract_tb(e.__traceback__)}"}
        
        return {"condition" : True, "errorCode" : "메뉴 저장 성공!"}
    
    def removeMemo(self, id: str):
        self.table.delete({"_id": ObjectId(id)})

    def modifyMemo(self, id:str, data:dict):
        self.table.update({"_id" : ObjectId(id)}, {'$set': data})
