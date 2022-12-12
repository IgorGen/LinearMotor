from zaber_motion.ascii import Connection
from zaber_motion import Units, NoDeviceFoundException, ConnectionFailedException
from time import sleep, time
from math import pi, cos
from matplotlib import pyplot as plt
import json
import sys

AXIS_LEN = 151.5
TIME_STEP = 0.048
MAIN_FREQ = 76.5e9  # [Hz]
quart_lambda = (3e8 / MAIN_FREQ / 4) * 1000  # [mm]
HELP_DOC = """Usage:
python LinEng.py [COM port num] [frequency] [amplitude] [duration (optional)]

Doc:
COM port num: the serial port of the engine (check in device manager for usb serial COM ports)
frequency:    the sin movement frequency in Hertz
amplitude:    the sin movement amplitude in millimeters 
duration:     the movement duration in seconds - if not specified set to infinity"""


def goto(axis, pos, speed=25) -> None:
    """
    Function moves the engine to pos
    :param axis: Engine reference
    :param pos: Position on the rail [mm]
    :param speed: The speed to move at [mm / sec]
    :return: None
    """

    # Starting to move
    cur_pos = axis.get_position(Units.LENGTH_MILLIMETRES)
    sign = 1 if cur_pos < pos else -1
    axis.move_velocity(speed * sign, Units.VELOCITY_MILLIMETRES_PER_SECOND)

    #  Waiting till the engine gets to the desired position
    while abs(cur_pos - AXIS_LEN / 2) > 0.1:
        cur_pos = axis.get_position(Units.LENGTH_MILLIMETRES)
    axis.move_velocity(0, Units.VELOCITY_MILLIMETRES_PER_SECOND)


def vel_sin(axis, f: float, amp: float, dur: float = -1) -> list:
    """
    Function makes sin movements on engine

    :param axis: engine reference
    :param f: sin frequency
    :param amp: sin amplitude
    :param dur: movement duration in seconds, if not specified det to infinity
    :return: a list that documents the engine position
            during the movement for indication
    """

    total_t = 0
    amp = amp * 2 * pi * f
    pos_vec = []

    # Centering engine at the middle rail
    goto(axis, AXIS_LEN / 2)

    center_pos = axis.get_position(Units.LENGTH_MILLIMETRES)
    print(f"Starting sin motion around: {center_pos}")
    start_move = time()
    while dur == -1 or time() - start_move < dur:

        # Moving sin
        start = time()
        pos_vec.append(axis.get_position(Units.LENGTH_MILLIMETRES))
        axis.move_velocity(amp * cos(2 * pi * f * total_t), Units.VELOCITY_MILLIMETRES_PER_SECOND)
        end = time()

        # Making sure the time for the sinus
        # is changing in a constant rate (of 1 / TIME_STEP)
        duration = end - start
        del_t = TIME_STEP - duration
        if del_t > 0:
            sleep(del_t)
            total_t += TIME_STEP
        else:
            total_t += duration

    # Printing value avg and sinus center, since they
    # need to be equal the diff is the drifting offset
    print(f"drifting avg = {sum(pos_vec) / len(pos_vec) - center_pos}")

    return pos_vec


def main():
    args = sys.argv[1:]

    # Reading run parameters
    if len(args) == 0:
        with open("prms.json", "r") as f:
            args = list(json.load(f).values())
    elif len(args) == 1 and args[0] in ("?", "help"):
        print(HELP_DOC)
        exit(1)
    elif len(args) < 3 or len(args) > 4:
        print(f"\nExpecting 3-4 arguments but got {len(args)} instead!!\n")
        print(HELP_DOC)
        exit(1)

    try:
        port = args[0]
        with Connection.open_serial_port(f"COM{port}") as connection:

            # Getting engine reference
            device_list = connection.detect_devices()
            device = device_list[0]
            axis = device.get_axis(1)

            for reps in range(0, 100):
                # Movement - 1/4 wavelength step, then back to starting position
                # Use break points to manually record with sensor between movements
                axis.move_absolute(50, Units.LENGTH_MILLIMETRES)
                axis.move_relative(quart_lambda, Units.LENGTH_MILLIMETRES)
                axis.move_absolute(50, Units.LENGTH_MILLIMETRES)


    except (NoDeviceFoundException, ConnectionFailedException):
        print("\nNo device found on the specified port")


if __name__ == '__main__':
    main()
