from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid, DuplicateKeyError, WriteError

DB_NAME = 'payment_case'
client = MongoClient()
db = client[DB_NAME]

db.drop_collection('accrual')
db.drop_collection('payment')
db.drop_collection('refs')

accs = [
    {'id': 1, 'month': 1, 'date': datetime(2019, 1, 2).isoformat()},
    {'id': 2, 'month': 1, 'date': datetime(2019, 1, 20).isoformat()},
    {'id': 3, 'month': 1, 'date': datetime(2019, 1, 15).isoformat()},
    {'id': 4, 'month': 2, 'date': datetime(2019, 2, 16).isoformat()},
    {'id': 5, 'month': 2, 'date': datetime(2019, 2, 20).isoformat()},
]

pays = [
    {'id': 1, 'month': 12, 'date': datetime(2018, 12, 25).isoformat()},
    {'id': 2, 'month': 1, 'date': datetime(2019, 1, 15).isoformat()},
    {'id': 3, 'month': 2, 'date': datetime(2019, 2, 2).isoformat()},
    {'id': 4, 'month': 2, 'date': datetime(2019, 2, 25).isoformat()},
    {'id': 5, 'month': 3, 'date': datetime(2019, 3, 1).isoformat()},
    {'id': 6, 'month': 2, 'date': datetime(2019, 2, 4).isoformat()},
    {'id': 7, 'month': 3, 'date': datetime(2019, 3, 25).isoformat()},
    {'id': 8, 'month': 1, 'date': datetime(2019, 1, 9).isoformat()},
]

accrual = db['accrual']
payment = db['payment']

refs = db['refs']

accrual.insert_many(accs)
payment.insert_many(pays)

EXCLUDED = []  # accruals
BY_MONTH_FAILED = []  # payments
BY_DATE_FAILED = []  # payments


def can_pay_by_date(payment_date: datetime, accrual_date: datetime):
    '''проверяет, что платеж имеет более позднюю дату, чем долг'''
    return payment_date > accrual_date


def accruals_for_one_payment_by_month(payment, excluded=tuple()):
    '''
    ищет свободные долги для платежа (ПО МЕСЯЦУ)
    :param payment: платеж
    :param excluded: список исключенных из поиска платежей (ids)
    :return: подходящий долг или None
    '''
    accruals = accrual.find({
        'month': payment['month'],
        'id': {'$nin': excluded}
    }).sort([('date', 1)]).limit(1)
    try:
        r = next(accruals)
        if can_pay_by_date(payment['date'], r['date']):
            EXCLUDED.append(r['id'])
            return r
        BY_MONTH_FAILED.append(payment)
    except StopIteration:
        BY_MONTH_FAILED.append(payment)
        return


def accruals_for_one_payment_by_date(payment, excluded=tuple()):
    '''
    ищет свободные долги для платежа ПО ДАТЕ, после того, как прошел поиск по месяцам
    :param payment: платеж
    :param excluded: список исключенных из поиска платежей (ids)
    :return: подходящий долг или None
    '''
    accruals = accrual.find({
        'id': {'$nin': excluded}
    }).sort([('date', -1)]).limit(1)
    try:
        r = next(accruals)
        if can_pay_by_date(payment['date'], r['date']):
            EXCLUDED.append(r['id'])
            return r
    except StopIteration:
        return


all_payments = payment.find()
for pay in all_payments:
    acc = accruals_for_one_payment_by_month(pay, tuple(EXCLUDED))
    if acc:
        refs.insert_one(
            {
                'payment': pay['id'],
                'accrual': acc['id']
            }
        )

for pay in BY_MONTH_FAILED:
    acc = accruals_for_one_payment_by_date(pay, tuple(EXCLUDED))
    if acc:
        refs.insert_one(
            {
                'payment': pay['id'],
                'accrual': acc['id']
            }
        )
    else:
        BY_DATE_FAILED.append(pay['id'])

for i in refs.find({}, {'_id': 0}):
    print(i)

print(BY_DATE_FAILED)
