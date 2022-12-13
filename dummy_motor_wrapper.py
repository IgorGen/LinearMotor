from zaber_motion.ascii import Connection, Device, Axis
from zaber_motion import Units, NoDeviceFoundException, ConnectionFailedException, MovementFailedException

class DummyMotorWrapper(object):
    """
    Dummy class for LinearMotorManager simulation.
    """
    def __init__(self, logger, serial_number, device_mgr_name, com_port: str = '') -> None:
        self.logger = logger
        self.sn = serial_number
        self.device_mgr_name = device_mgr_name
        self.connection = None
        self.device = None
        self.com_port = com_port
        self.logger.debug(f'Init DummyMotorWrapper, COM-port does not defined')

    def move_absolute(self, position: float, unit: Units = Units.LENGTH_MILLIMETRES, wait_until_idle: bool = True)\
            -> None:
        print(f'Dummy: move to absolute position {position}')

    def move_relative(self, position: float, unit: Units = Units.LENGTH_MILLIMETRES, wait_until_idle: bool = True)\
            -> None:
        print(f'Dummy: move to relative position {position}')

