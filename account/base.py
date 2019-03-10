from pymongo import MongoClient

DB_NAME = 'account_case'
CLIENT = MongoClient()  # создаем клиента
CLIENT_DB = CLIENT[DB_NAME]  # создаем БД


class Meta(type):
    def __new__(cls, clsname, bases, clsdict):
        clsdict['COLLECTION'] = clsname.title()  # 1
        clsdict['db'] = CLIENT_DB
        return type.__new__(cls, clsname, bases, clsdict)
