from typing import Union


class Order(object):
    def __init__(self, job_id: Union[int, str] = None):
        self.job_id = job_id
