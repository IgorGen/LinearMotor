from zaber_motion.ascii import Connection, Device, Axis
from zaber_motion import Units, NoDeviceFoundException, ConnectionFailedException, MovementFailedException
# from zaber_motion import Measurement
from time import sleep, time
import json
import sys
import logging

STOPPER_POSITION = 40


class LinearMotorWrapper(object):
    """
    Represents Linear Motor Wrapper.
    """
    def __init__(self, logger, serial_number, device_mgr_name, com_port: str = '') -> None:
        self.logger = logger
        self.sn = serial_number
        self.device_mgr_name = device_mgr_name
        self.connection = None
        self.device = None
        self.com_port = com_port if com_port else self.recognize_com_port()
        self.connection = None  # self.open_com_port()
        self.device = None  # self.get_device()
        self.axis = self.get_axis()
        self.define_axis_position()
        self.logger.debug(f'Init LinearMotorWrapper, COM-port{self.com_port}')

    def recognize_com_port(self) -> str:
        com_port = ''
        if sys.platform == 'win32':
            from infi.devicemanager import DeviceManager

            dm = DeviceManager()
            dm.root.rescan()
            devices = dm.all_devices

            port_found = False
            for device in devices:
                if port_found:
                    break
                try:
                    name = device.friendly_name if device.has_property("friendly_name") else device.description
                    # if 'USB' in name and 'COM' in name: # TMP - should use line below
                    # if 'USB Serial Port' in name and 'COM' in name:  # check name is correct
                    if self.device_mgr_name in name and 'COM' in name:
                        parse_name = name.split()
                        for item in parse_name:
                            if 'COM' in item:
                                com_port = item.strip('()')
                                connection = self.open_com_port(com_port)
                                devices = connection.detect_devices()
                                device = devices[0]
                                if device.serial_number == self.sn:
                                    self.connection = connection
                                    self.device = device
                                    port_found = True
                                    break
                                else:
                                    connection.close()
                                    com_port = ''
                except Exception as ex:
                    continue
        else:
            import serial.tools.list_ports as list_ports

            comports = list_ports.comports()
            for comport_obj in comports:
                if comport_obj is None:
                    continue
                # product = comport_obj.product
                if 'FT232R' in comport_obj.product:
                    com_port = comport_obj.device
                    break
            else:
                com_port = '/dev/ttyUSB0'

        return com_port

    def open_com_port(self, com_port) -> Connection:
        """
        Open COM-port, gets Connection class instance.
        """
        try:
            connection = Connection.open_serial_port(com_port)
            return connection
        except (NoDeviceFoundException, ConnectionFailedException) as ex:
            # print("No device found on the specified port")
            self.logger.error(ex)
            raise ex

    def get_device(self) -> Device:
        """
        Gets Device class instance of device.
        """
        try:
            devices = self.connection.detect_devices()
            device = devices[0]
            return device
        except NoDeviceFoundException as ex:
            # print("No device found on the specified port")
            print(ex)
            self.logger.error(ex)
            raise ex

    def get_axis(self) -> Axis:
        """
        Gets Axis class instance of device.
        """
        try:
            # devices = self.connection.detect_devices()
            # device = devices[0]
            axis = self.device.get_axis(1)
            return axis
        except NoDeviceFoundException as ex:
            # print("No device found on the specified port")
            print(ex)
            self.logger.error(ex)
            raise ex

    def define_axis_position(self) -> None:
        """
        Position normally set by _home(), otherwise it set explicitly on clash place.
        """
        try:
            start_position = self.get_position()  # After power OFF expected position = 151.5
            if start_position < 150:  # Motor was powered since last initialization, home() does not needed
                return
            # self.move_absolute(STOPPER_POSITION - 10)  # Expected clash to stopper followed by exception
            self._home()  # Raise exception when mechanical issue exists
        except Exception as ex:
            msg = 'Expected exception after stopper clash'
            print(msg)
            self.logger.debug(ex)

            # Set position explicitly where the motor stopped after clash
            self.axis_settings_set_pos(STOPPER_POSITION)

            # Verify position was set correctly
            set_stopper_position = self.get_position()
            pos_error = set_stopper_position - STOPPER_POSITION
            msg = f'Error set stopper position: {pos_error}'
            print(msg)
            self.logger.debug(msg)
            assert abs(pos_error) < 1

    def move_absolute(self, position: float, unit: Units = Units.LENGTH_MILLIMETRES, wait_until_idle: bool = True)\
            -> None:
        """
        Move axis to absolute position.

        Args:
            position: Absolute position.
            unit: Units of position.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        try:
            msg = f'Starting go to absolute position: {position}'
            print(msg)
            self.logger.debug(msg)
            self.axis.move_absolute(position, unit, wait_until_idle)
            self.logger.debug(f'move_absolut to {position} position')
        except MovementFailedException as ex:
            print(ex)
            self.logger.error(ex)
            # raise ex

    def move_relative(self, position: float, unit: Units = Units.LENGTH_MILLIMETRES, wait_until_idle: bool = True)\
            -> None:
        """
        Move axis to relative position.

        Args:
            position: Absolute position.
            unit: Units of position.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        try:
            msg = f'Starting go to relative position: {position}'
            print(msg)
            self.logger.debug(msg)
            self.axis.move_relative(position, unit, wait_until_idle)
            self.logger.debug(f'move_absolut to {position} position')
        except MovementFailedException as ex:
            print(ex)
            self.logger.error(ex)
            # raise ex

    def _home(self, wait_until_idle: bool = True) -> None:
        """
        Do home.
        Raises exception, internal use only

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        try:
            msg = 'Starting home'
            print(msg)
            self.logger.debug(msg)
            self.axis.home(wait_until_idle)
            self.logger.debug('Axes returned to home position')
        except MovementFailedException as ex:
            print(ex)
            self.logger.error(ex)
            raise ex

    def home(self, wait_until_idle: bool = True) -> None:
        """
        Do home.
        Catch exception, but do nor raise it.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        try:
            self._home(wait_until_idle)
        except MovementFailedException as ex:
            pass

    def get_position(self, unit: Units = Units.LENGTH_MILLIMETRES) -> float:
        """
        Get current position.

        Args:
            unit: Units of position.
        """
        position = self.axis.get_position(unit)
        msg = f'Current position: {position}'
        print(msg)
        self.logger.debug(msg)

        return position

    def axis_settings_set_pos(self, position: float, unit: Units = Units.LENGTH_MILLIMETRES) -> None:
        """
        Set position explicitly.

        Args:
            position: Absolute position.
            unit: Units of position.
        """
        try:
            msg = f'Position be set explicitly: {position}'
            print(msg)
            self.logger.debug(msg)
            # self.axis.generic_command('set pos', Measurement(value=position, unit=unit))
            self.axis.settings.set('pos', position, unit)
        except Exception as ex:
            print(ex)
            self.logger.error(ex)

    @property
    def serial_number(self) -> int:
        """
        Serial number of the device.
        """
        return self.device.serial_number

    @property
    def device_id(self) -> int:
        """
        Unique ID of the device hardware.
        """
        return self.device.device_id


def main():
    args = sys.argv[1:]
    com_port = ''
    logger = logging.getLogger("LinearMotorWrapper")

    # Reading run parameters
    if len(args) == 0:
        # com_port = 'COM3'
        pass
    elif len(args) == 1:
        com_port = args[0]
    elif len(args) > 1:
        print(f"\nExpecting 1 argument but got {len(args)} instead!!\n")
        exit(1)

    motor = LinearMotorWrapper(logger, com_port)
    # motor.home()
    position = motor.get_position()

    sleep(2)
    motor.move_absolute(140)  # must be <= 151
    sleep(2)

    motor.move_absolute(100)
    sleep(2)

    motor.move_relative(20)
    sleep(2)

    motor.move_absolute(50)
    sleep(2)
    # motor.move_absolute(10)  # must be > STOPPER_POSITION
    # sleep(2)

    # motor.move_relative(-40)
    # sleep(2)

    motor.move_absolute(75)
    sleep(2)
    # motor.home()


if __name__ == '__main__':
    main()
