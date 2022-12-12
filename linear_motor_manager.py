import logging
from linear_motor_wrapper import LinearMotorWrapper

MOTOR_TYPE2CLASS = {'X_LSQ': LinearMotorWrapper
                    }


class LinearMotorManager(object):
    def __init__(self, logger, **kwargs):
        self.motor_instances = {}
        for typ, num in kwargs.items():  # typ -> motor type, num -> number of inst
            # typ = typ.replace('-', '_')
            self.motor_instances[typ] = []
            class_obj = MOTOR_TYPE2CLASS[typ]
            for idx in range(num):
                class_inst = class_obj(logger)  # obj of LinearMotorWrapper(logger)
                self.motor_instances[typ].append(class_inst)  # like {'X_LSQ': [inst_0, inst_1, ...]

    def move_absolute(self, motor_type, motor_idx, position):
        motor_inst = self.motor_instances[motor_type][motor_idx]
        motor_inst.move_absolute(position)

    def move_relative(self, motor_type, motor_idx, position):
        motor_inst = self.motor_instances[motor_type][motor_idx]
        motor_inst.move_absolute(position)


def main():
    logger = logging.getLogger("LinearMotorWrapper")
    mgr = LinearMotorManager(logger, X_LSQ=2)
    mgr.move_absolute('X_LSQ', 0, 90)
    mgr.move_absolute('X_LSQ', 1, 120)

    mgr.move_relative('X_LSQ', 0, 7)
    mgr.move_relative('X_LSQ', 1, -18)


if __name__ == '__main__':
    main()
