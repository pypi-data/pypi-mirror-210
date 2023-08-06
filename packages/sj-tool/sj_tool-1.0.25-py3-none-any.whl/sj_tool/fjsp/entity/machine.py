from typing import List
from typing import Union


class BaseMachine(object):
    def __init__(self, idx, name, available_ops: List[Union[str, int]] = None, unit_times=None):
        """

        :param machine_id:
        :param available_ops:

        {
        "_id": {
            "$oid": "63ad5dc38e83107f8b8092ce"
        },
        "prodLine": "EZP10",
        "planName": "CML",
        "calendarTime": {
            "$date": "2022-02-28T16:00:00.000Z"
        },
        "week": "二",
        "workTime": "12",
        "userName": "duchengkun",
        "createTime": {
            "$date": "2022-12-29T09:28:35.126Z"
        },
        "updateTime": {
            "$date": "2022-12-29T09:28:35.126Z"
        }
    }

        """
        self.id = idx
        self.name = name
        self.unit_times = {} if unit_times is None else unit_times  # {('product_id','process_id'):单个的节拍 }
        self.available_ops = [] if available_ops is None else available_ops
        self.scheduled_ops = []

        # {"8小时":["08:00-11:30,12:15-16:45,"],"12小时":["08:00-11:30,12:15-16:45,17:30-21:30,"],"16小时":["08:00-16:45,17:30-00:45,"],"24小时":["08:00-11:30,12:15-16:45,17:30-20:00,20:00-00:00,00:30-08:00,"],"0小时":["08:00-08:00,"]}
        self.calendar = {}

