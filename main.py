import re, math, time

from flask import Flask, jsonify
from OmegaExpansion import onionI2C

from py_i2c_register.register_list import RegisterList
from py_i2c_register.register import Register

class LidarLight():
    # Register and Segment name constants
    REG_ACQ_COMMAND = "ACQ_COMMAND"
    SEG_ACQ_COMMAND = REG_ACQ_COMMAND

    REG_STATUS = "STATUS"
    SEG_PROC_ERROR_FLAG = "PROC_ERROR_FLAG"
    SEG_HEALTH_FLAG = "HEALTH_FLAG"
    SEG_SECONDARY_RET_FLAG = "SECONDARY_RET_FLAG"
    SEG_INVALID_SIGNAL_FLAG = "INVALID_SIGNAL_FLAG"
    SEG_SIGNAL_OVERFLOW_FLAG = "SIGNAL_OVERFLOW_FLAG"
    SEG_REFERENCE_OVERFLOW_FLAG = "REFERENCE_OVERFLOW_FLAG"
    SEG_BUSY_FLAG = "BUSY_FLAG"

    REG_PEAK_CORR = "PEAK_CORR"
    SEG_PEAK_CORR = REG_PEAK_CORR

    REG_VELOCITY = "VELOCITY"
    SEG_VELOCITY= REG_VELOCITY

    REG_OUTER_LOOP_COUNT = "OUTER_LOOP_COUNT"
    SEG_OUTER_LOOP_COUNT = REG_OUTER_LOOP_COUNT

    REG_DISTANCE = "DISTANCE"
    SEG_DISTANCE = "DISTANCE"

    def __init__(self):
        # Configure control registers
        self.controls = RegisterList(0x62, {})
        self.controls.add(LidarLight.REG_ACQ_COMMAND, 0x00, Register.WRITE, {}) \
            .add(LidarLight.SEG_ACQ_COMMAND, 0, 7, [0] * 8)

        self.controls.add(LidarLight.REG_STATUS, 0x01, Register.READ, {}) \
            .add(LidarLight.SEG_PROC_ERROR_FLAG, 6, 6, [0]) \
            .add(LidarLight.SEG_HEALTH_FLAG, 5, 5, [0]) \
            .add(LidarLight.SEG_SECONDARY_RET_FLAG, 4, 4, [0]) \
            .add(LidarLight.SEG_INVALID_SIGNAL_FLAG, 3, 3, [0]) \
            .add(LidarLight.SEG_SIGNAL_OVERFLOW_FLAG, 2, 2, [0]) \
            .add(LidarLight.SEG_REFERENCE_OVERFLOW_FLAG, 1, 1, [0]) \
            .add(LidarLight.SEG_BUSY_FLAG, 0, 0, [0])

        self.controls.add(LidarLight.REG_PEAK_CORR, 0x0c, Register.READ, {})\
            .add(LidarLight.SEG_PEAK_CORR, 0, 7, [0] * 8)

        self.controls.add(LidarLight.REG_VELOCITY, 0x09, Register.READ, {})\
            .add(LidarLight.SEG_VELOCITY, 0, 7, [0] * 8)

        self.controls.add(LidarLight.REG_OUTER_LOOP_COUNT, 0x11, Register.READ + Register.WRITE, {})\
            .add(LidarLight.SEG_OUTER_LOOP_COUNT, 0, 7, [0] * 8)

        self.controls.add(LidarLight.REG_DISTANCE, 0x8f, Register.READ, {})\
            .add(LidarLight.SEG_DISTANCE, 0, 15, [0] * 16)

    """Writes Register with given name when device is ready
    Determines when device is ready by polling  STATUS.BUSY_FLAG until 0
    
    Args:
        - name(str): Name of register to write
        - max_count(int): Maximum number of times program will loop while waiting for STATUS.BUSY_FLAG to become 0
        - count_delay(float): Delay between each loop while waiting for STATUS.BUSY_FLAG to become 0
    
    Raises:
        - SystemError: If max_count is reached and STATUS.BUSY_FLAG is not 0
        - KeyError: If Register with name is not found
        - ValueError: If max_count is less than 1
    """
    def write_when_ready(self, name, max_count=999, count_delay=0.01):
        # Check max_count is at least 1 so loop below runs
        if max_count < 1:
            raise ValueError("max_count must be >= 1")

        # Check STATUS.BUSY_FLAG
        count = 0
        while count < max_count:
            # Read register
            self.controls.read(LidarLight.REG_STATUS)

            # Check BUSY_FLAG
            busy_flag = self.controls.to_int(LidarLight.REG_STATUS, LidarLight.SEG_BUSY_FLAG)

            if busy_flag == 0:
                # If not busy, write
                return self.controls.write(name)
            else:
                # Otherwise sleep
                time.sleep(count_delay)

            count += 1

        # Raise error if loop exited
        raise SystemError("max_count reached while waiting for STATUS.BUSY_FLAG to become 0, max_count: {}, count_delay: [}".format(max_count, count_delay))

    """Sets bits of RegisterSegment and then writes when the device is ready
    Args:
        - reg_name(str): Name of register to write
        - seg_name(str): Name of segment to write
        - bits(int[]): Bits to write
    """
    def set_bit_when_ready(self, reg_name, seg_name, bits):
        self.controls.set_bits(reg_name, seg_name, bits, write_after=True, write_fn=self.write_when_ready)

    """Sets bits of RegisterSegment and then writes when the device is ready
    Args:
        - reg_name(str): Name of register to write
        - seg_name(str): Name of segment to write
        - val(int): Integer to write
    """
    def set_bit_when_ready_from_int(self, reg_name, seg_name, val):
        self.controls.set_bits_from_int(reg_name, seg_name, val, write_after=True, write_fn=self.write_when_ready)

    """Resets device
    """
    def reset(self):
        self.set_bit_when_ready_from_int(LidarLight.REG_ACQ_COMMAND, LidarLight.SEG_ACQ_COMMAND, 0x00)

    """Sets up Lidar Light device
    """
    def setup(self):
        self.set_bit_when_ready_from_int(LidarLight.REG_ACQ_COMMAND, LidarLight.SEG_ACQ_COMMAND, 0x04)

    def setup_indefinite_measurements(self):
        self.set_bit_when_ready_from_int(LidarLight.REG_ACQ_COMMAND, LidarLight.SEG_ACQ_COMMAND, 0x04)
        self.set_bit_when_ready_from_int(LidarLight.REG_OUTER_LOOP_COUNT, LidarLight.SEG_OUTER_LOOP_COUNT, 0xff)

lidar = LidarLight()
lidar.reset()
lidar.setup_indefinite_measurements()

app = Flask(__name__)

@app.route("/")
def route_home():
    return app.send_static_file("index.html")

@app.route("/distance")
def route_distance():
    # Trigger read
    lidar.set_bit_when_ready_from_int(LidarLight.REG_ACQ_COMMAND, LidarLight.SEG_ACQ_COMMAND, 0x04)

    # Get distance
    distance = lidar.controls.to_int(LidarLight.REG_DISTANCE, LidarLight.SEG_DISTANCE, read_first=True)

    return jsonify(distance)

@app.route("/velocity")
def route_velocity():
    velocity = lidar.controls.to_twos_comp_int(LidarLight.REG_VELOCITY, LidarLight.SEG_VELOCITY, read_first=True)

    return jsonify(velocity)

if __name__== '__main__':
    app.run(host="0.0.0.0")
