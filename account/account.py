from pymongo.errors import CollectionInvalid, DuplicateKeyError, WriteError

from base import Meta, CLIENT_DB

CLIENT_DB.drop_collection('Account')


class Account(metaclass=Meta):
    _validator = {
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['number'],
            'properties': {
                'number': {
                    'bsonType': 'string',
                    'minLength': 13,
                    'maxLength': 13,
                    'description': "must be a string of 13 chars and is required"
                },
            }
        }
    }

    def __init__(self):
        try:
            self.db.create_collection(self.COLLECTION, validator=self._validator)
        except CollectionInvalid:
            print(f'<collection {self.COLLECTION} already exists!>')
        finally:
            self.collection = self.db[self.COLLECTION]
            self.collection.create_index('number', unique=True)

    def get_all(self):
        return self.collection.find()

    def add_one(self, document):
        try:
            self.collection.insert_one(document)
        except DuplicateKeyError:
            print(f'<document with number {document.get("number")} already exists!')
        except WriteError:
            print(f'<document failed "number" field validation!>')

    def request(self):
        pipeline = [
            # раскрываем спсисок sessions
            {'$unwind': '$sessions'},
            {'$unwind': {'path': '$sessions.actions'}},

            {'$group': {'_id': '$number', 'actions': {'$push': {
                'type': '$sessions.actions.type',
                'last': '$sessions.actions.created_at',
                'count': {'$sum': 1}
            }}}},

            {'$unwind': '$actions'},

            {'$group': {'_id': {'number': '$_id', 'type': '$actions.type'}, 'arr': {'$push': '$actions.last'}}},

            {'$group': {'_id': '$_id.number', 'actions': {'$push': {
                'type': '$_id.type',
                'last': {'$max': '$arr'},
                'count': {'$size': '$arr'}
            }}}},

            {'$project': {'_id': 0, 'number': '$_id', 'actions': '$actions'}},
        ]
        return list(self.collection.aggregate(pipeline))
