from typing import Dict


class Changeover(object):
    def __init__(self):
        self.info = {}

    def add(self, pre_model, pre_op_type, post_model, cur_op_type, machine, time_length):
        """
        :param pre_model: 前置产品的系列 或者 半成品
        :param pre_op_type:
        :param post_model:
        :param cur_op_type:
        :param machine:
        :param time_length:
        :return:
        """
        self.info[(pre_model, pre_op_type, post_model, cur_op_type, machine)] = time_length

    def get(self, pre_model, pre_op_type, post_model, cur_op_type, machine):
        if (pre_model, pre_op_type, post_model, cur_op_type, machine) not in self.info:
            return 0
        return self.info[(pre_model, pre_op_type, post_model, cur_op_type, machine)]
