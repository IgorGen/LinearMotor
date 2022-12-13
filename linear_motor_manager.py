import json
import os
import sys
import logging
from linear_motor_wrapper import LinearMotorWrapper
from dummy_motor_wrapper import DummyMotorWrapper

MOTOR_TYPE2CLASS = {
    'X-LSQ': LinearMotorWrapper,
    'X-LRQ': DummyMotorWrapper
}



class LinearMotorManager(object):
    def __init__(self, logger, **kwargs):
        self.motor_instances = {}
        self.config = LinearMotorManager.load_config()  # list
        for data_item in self.config:  # dict
            motor_type = data_item['type']
            properties = data_item['properties']  # list
            self.motor_instances[motor_type] = []

            class_obj = MOTOR_TYPE2CLASS[motor_type]
            for proper in properties:
                class_inst = class_obj(logger, proper['sn'], proper['device_mgr_name'])
                self.motor_instances[motor_type].insert(proper['index'], class_inst)

        # for typ, num in kwargs.items():  # typ -> motor type, num -> number of inst
        #     # typ = typ.replace('-', '_')
        #     self.motor_instances[typ] = []
        #     class_obj = MOTOR_TYPE2CLASS[typ]
        #     for idx in range(num):
        #         class_inst = class_obj(logger)  # obj of LinearMotorWrapper(logger)
        #         self.motor_instances[typ].append(class_inst)  # like {'X_LSQ': [inst_0, inst_1, ...]

    @staticmethod
    def load_config():
        json_path = ''
        if sys.platform == 'win32':
            json_path = os.path.join(os.path.dirname(__file__), 'linear_motor_config_win32.json')  # in real be another path
        else:
            json_path = os.path.join(os.path.dirname(__file__), 'linear_motor_config_linux.json')  # in real be another path

        with open(json_path) as f:
            return json.load(f)

    def move_absolute(self, motor_type, motor_idx, position):
        motor_inst = self.motor_instances[motor_type][motor_idx]
        motor_inst.move_absolute(position)

    def move_relative(self, motor_type, motor_idx, position):
        motor_inst = self.motor_instances[motor_type][motor_idx]
        motor_inst.move_relative(position)


def main():
    logger = logging.getLogger("LinearMotorWrapper")
    mgr = LinearMotorManager(logger)  #, X_LSQ=2)
    mgr.move_absolute('X-LSQ', 0, 90)
    mgr.move_absolute('X-LSQ', 1, 120)

    mgr.move_relative('X-LRQ', 0, 7)
    mgr.move_relative('X-LRQ', 1, -18)


if __name__ == '__main__':
    main()
