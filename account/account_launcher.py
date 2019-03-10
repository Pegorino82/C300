if __name__ == '__main__':
    from datetime import datetime
    from pprint import pprint

    from account import Account

    a = Account()
    acc_1 = {
        'number': '7800000000000',
        'name': 'Пользователь №',
        'sessions': [
            {
                'created_at': datetime(2016, 1, 1, 0, 0, 0).isoformat(),
                'session_id': '6QBnQhFGgDgC2FDfGwbgEaLbPMMBofPFVrVh9Pn2quooAcgxZc',
                'actions': [
                    {
                        'type': 'read',
                        'created_at': datetime(2016, 1, 10, 1, 20, 1).isoformat(),
                    },
                    {
                        'type': 'read',
                        'created_at': datetime(2016, 1, 1, 1, 33, 59).isoformat(),
                    },
                    {
                        'type': 'create',
                        'created_at': datetime(2016, 1, 1, 1, 21, 13).isoformat(),
                    }
                ],
            }
        ]
    }
    acc_2 = {
        'number': '7800000000001',
        'name': 'Пользователь №',
        'sessions': [
            {
                'created_at': datetime(2015, 1, 10, 0, 0, 0).isoformat(),
                'session_id': '6QBnQhFGgDgC2FDfGwbgEaLbPMMBofPFVrVh9Pn2quooAcgxZc',
                'actions': [
                    {
                        'type': 'read',
                        'created_at': datetime(2015, 1, 11, 1, 20, 1).isoformat(),
                    },
                    {
                        'type': 'read',
                        'created_at': datetime(2015, 1, 12, 1, 33, 59).isoformat(),
                    },
                    {
                        'type': 'create',
                        'created_at': datetime(2016, 1, 13, 1, 21, 13).isoformat(),
                    }
                ],
            }
        ]
    }
    a.add_one(acc_1)
    a.add_one(acc_2)

    for i in a.request():
        pprint(i)
