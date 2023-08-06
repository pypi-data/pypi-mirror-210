import datetime

from pydantic import Field
from ebdesk_email_executor.model.base import ListEmail
from ebdesk_email_executor.config import mongo, redis
from bson import ObjectId


class ExecutorAccount:

    def bulk_email(self, model: ListEmail):
        try:
            db = mongo.connect()
            for detail in model:
                dict_data = dict(detail)
                find = db.find_one({'email': dict_data['email']})
                if not find:
                    inserted_id = db.insert_one({
                        "_id": str(ObjectId()),
                        "email": dict_data['email'],
                        "password": dict_data['password'],
                        "status": dict_data['status'],
                        "active": False,
                        "email_type":"google" if "gmail.com" in dict_data['email'] else "other"
                    }).inserted_id
            return "success insert bulk"
        except Exception as e:
            return e
        

    def add_email(self, email=Field(..., example="account@mail.com"), password=Field(..., example="rahasia2023"),
                  status=Field(..., example="ACTIVE|LOCKED|TIMEOUT")):
        try:
            db = mongo.connect()
            find = db.find_one({'email': email})
            if not find:
                inserted_id = db.insert_one({
                    "_id": str(ObjectId()),
                    "email": email,
                    "password": password,
                    "status": status,
                    "active": False,
                    "email_type":"google" if "gmail.com" in email else "other"
                }).inserted_id
                return "insert id = " + str(inserted_id)
            else:
                return "email already in db"
        except Exception as e:
            return "error connection to database"

    def get_email(self):
        try:
            red = redis.connect()
            db = mongo.connect()
            active_true = db.find({"status": "TIMEOUT", "active": True})
            for key in active_true:
                value = red.get(key['email'])
                if not value:
                    db.update_one({"_id": key["_id"]}, {"$set": {"status": "TIMEOUT","active": False}})
            pipeline = [
                {"$match": {"status": "ACTIVE", "active": False}},
                {"$sample": {"size": 1}}
            ]
            email = db.aggregate(pipeline)
            data = next(email, None)
            if not data:
                return None
            # Get counter on redis
            get_count = red.get("count:"+data.get("email"))
            if get_count == None:
                red.set("count:"+data.get("email"), "0")
            else:
                get_count = int(bytes.decode(get_count, 'utf-8'))
                print(data.get("email")+" = "+str(get_count))
                if get_count >= 24:
                    red.set(data.get("email"), "timeout")
                    red.expire(data.get("email"), datetime.timedelta(hours=3))
                    db.update_one({"email": data.get("email")}, {"$set": {"status": "TIMEOUT"}})
                    red.delete("count:"+data.get('email'))
                else:
                    num_count = get_count + 1
                    red.set("count:"+data.get('email'), str(num_count))
            _id = data.get('_id')
            db.update_one({"_id": _id}, {"$set": {"active": True}})
            return data
        except Exception as e:
            return e

    def update_count(self, email):
        try:
            red = redis.connect()
            db = mongo.connect()
            get_count = red.get("count:"+email)
            if get_count is None:
                red.set("count:"+email, "0")
                return "email : "+email+" created on redis"
            else:
                get_count = int(bytes.decode(get_count, 'utf-8'))
                if get_count >= 24:
                    red.set(email, "timeout")
                    red.expire(email, datetime.timedelta(hours=3))
                    db.update_one({"email": email}, {"$set": {"status": "TIMEOUT"}})
                    red.delete("count:"+email)
                    return "timeout"
                else:
                    red.set("count:"+email, str(get_count+1))
                    return "success"
        except Exception as e:
            return e

    def update_active(self, email):
        try:
            db = mongo.connect()
            db.update_one({"email": email}, {"$set": {"active": False}})
        except Exception as e:
            return e

    def handle_timeout(self, email):
        try:
            red = redis.connect()
            db = mongo.connect()
            db.update_one({"email": email}, {"$set": {"status": "TIMEOUT"}})
            red.set(email, "timeout")
            red.expire(email, datetime.timedelta(hours=1))
            return "success insert timeout into email " + email
        except Exception as e:
            return e

    def anti_ban(self):
        try:
            db = mongo.connect()
            db.update_many({},{"$set":{"status":"ACTIVE", "active":False}})
            return "anti ban success"
        except Exception as e:
            return e
        
    def change_status(self, email, status):
        try:
            db = mongo.connect()
            db.update_one({"email":email},{"$set":{"status":status}})
            return "success update status "+email
        except Exception as e:
            return e

    def find_all(self):
        try:
            db = mongo.connect()
            results = db.find()
            documents = []
            for result in results:
                documents.append(result)
            return documents
        except Exception as e:
            return e