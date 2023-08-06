from ugot.src.model_client import ModelClient
from ugot.src.vision_client import VisionClient
from ugot.src.util import num_normal, Color
from ugot.src.enum import E_Model, E_Device, E_Vision, E_Audio
from ugot.src.scan_device import DeviceScan
from ugot.src.device_client import DeviceClient
from ugot.src.audio_client import AudioClient
from ugot.src.sensor_client import SensorClient
from ugot.src.network_client import NetworkClient
from ugot.src.power_client import PowerClient
from ugot.src.bluetooth_client import BlueToothClient
from ugot.src.servo_client import ServoClient
from ugot.src.gpio_client import GpioClient

import logging
import json
import threading
import time
import sys

class UGOT:
    def __init__(self):
        pass

    def scan_device(self):
        """搜索扫描设备

        搜索获取同一局域网内的UGOT设备并打印.

        Args:
            无

        Returns:
            name_list (dict): 格式：{"设备名称1":"IP地址1","设备名称2":"IP地址2",...}

        """
        self.SCAN = DeviceScan()
        self.SCAN.device_discovery()
        name_list = self.SCAN.get_device_info_list()
        print(name_list)
        return name_list

    def initialize(self, device_ip):
        """初始化设备

        通过IP地址初始化相关设备.

        Args:
            device_ip (str): 设备的IP地址字符串

        Returns:
            无

        """
        if len(device_ip) == 0:
            print("please input device ip !")
            return
        address = device_ip + ':50051'
        print(address)
        self.__initialize_modules(address)

    def __initialize_modules(self, address):

        self.MODEL = ModelClient(address)
        self.VISION = VisionClient(address)
        self.DEVICE = DeviceClient(address)
        self.AUDIO = AudioClient(address)
        self.SENSOR = SensorClient(address)
        self.NETWORK = NetworkClient(address)
        self.POWER = PowerClient(address)
        self.BLUETOOTH = BlueToothClient(address)
        self.SERVO = ServoClient(address)
        self.GPIO = GpioClient(address)

    """

    >>>>>>>>>>>
    >> 变形车 <<
    >>>>>>>>>>>

    """
    def transform_set_chassis_height(self, height: float):
        """
        设置变形车底盘高度

        Args:
            height (int):  [1-7] 单位厘米

        Returns:
            无

        """
        if not isinstance(height, int):
            typestr = 'int is required (got type {})'.format(type(height).__name__)
            func_name = sys._getframe().f_code.co_name
            error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
            print(error_msg)
            return
        height = height * 10  # 换算成mm
        height = int(num_normal(height, 70, 10))
        self.MODEL.transform_set_height(height)

    def transform_move_speed(self, direction, speed):
        """
        变形工程车前进/后退运动

        Args:
            direction (int): 方向（0：前进；1：后退）
            speed (int): [5-80] 速度，单位 厘米/秒

        Returns:
            无

        """
        speed = num_normal(speed, 80, 5)
        if direction == E_Model.Direction.forward:
            self.MODEL.transform_move_control(linear_speed=speed, direction=0)
        elif direction == E_Model.Direction.backward:
            self.MODEL.transform_move_control(linear_speed=speed, direction=180)
        else:
            self.__print_move_direction_error_msg(sys._getframe().f_code.co_name, direction)

    def transform_turn_speed(self, turn: int, speed: int):
        """
        变形工程车左转/右转运动

        Args:
            turn (int): 方向（2：左转；3：右转）
            speed (int): [5-280] 速度，单位 度/秒

        Returns:
            无

        """
        speed = num_normal(speed, 280, 5)
        if turn == E_Model.Direction.turn_left:
            self.MODEL.transform_move_control(rotate_speed=speed)
        elif turn == E_Model.Direction.turn_right:
            self.MODEL.transform_move_control(rotate_speed=-speed)
        else:
            self.__print_move_turn_error_msg(sys._getframe().f_code.co_name, turn)

    def transform_move_speed_times(self, direction, speed, times, unit):
        """
        控制变形车前后运动x秒/cm后停止

        Args:
            direction (int): 方向（0：前进；1：后退）
            speed (int): [5-80] 速度，单位 厘米/秒
            times (int): [0-200] 持续范围
            unit (int): 单位类型（0：表示按秒运动；1：表示按厘米运动）

        Returns:
            无

        """
        tar_direction = 0
        if direction == E_Model.Direction.forward:
            tar_direction = 0
        elif direction == E_Model.Direction.backward:
            tar_direction = 180
        else:
            self.__print_move_direction_error_msg(sys._getframe().f_code.co_name, direction)
            return

        if times == 0:
            # 时长/里程等于0，此积木块不做控制
            logging.error(' 时长/里程等于0，此积木块不做控制')
            return

        speed = num_normal(speed, 80, 5)
        times = num_normal(times, 200, 0)

        if unit == E_Model.Unit.second:
            self.MODEL.transform_move_control(linear_speed=speed, direction=tar_direction, time=times)
        elif unit == E_Model.Unit.mileage:
            self.MODEL.transform_move_control(linear_speed=speed, direction=tar_direction, mileage=times)
        else:
            self.__print_move_unit_m_error_msg(sys._getframe().f_code.co_name, unit)

    def transform_turn_speed_times(self, turn, speed, times, unit):
        """
        控制变形车左右运动x秒/度后停止

        Args:
            turn (int): 方向（2：左转；3：右转）
            speed (int): [5-280] 速度，单位 度/秒
            times (int): [0-200] 持续范围
            unit (int): 单位类型（0：表示按秒运动；2：表示按度运动）

        Returns:
            无

        """
        speed = num_normal(speed, 280, 5)
        tar_speed = 0
        if turn == E_Model.Direction.turn_left:
            tar_speed = speed
        elif turn == E_Model.Direction.turn_right:
            tar_speed = -speed
        else:
            self.__print_move_turn_error_msg(sys._getframe().f_code.co_name, turn)
            return

        if times == 0:
            # 时长/里程等于0，此积木块不做控制
            logging.error(' 时长/里程等于0，此积木块不做控制')
            return

        times = num_normal(times, 200, 0)

        if unit == E_Model.Unit.second:
            self.MODEL.transform_move_control(rotate_speed=tar_speed, time=times)
        elif unit == E_Model.Unit.angle:
            self.MODEL.transform_move_control(rotate_speed=tar_speed, target_angle=times)
        else:
            self.__print_move_unit_a_error_msg(sys._getframe().f_code.co_name, unit)

    def transform_move_turn(self, direction, speed, turn, turn_speed):
        """
        控制变形车向指定方向运动同时做旋转运动

        Args:
            direction (int): 方向（0：前进；1：后退）
            speed (int): [5-80] 前进/后退速度，单位 厘米/秒
            turn (int): 方向（2：左转；3：右转）
            turn_speed (int): [5-280] 旋转速度，单位 度/秒

        Returns:
            无

        """
        tar_direction = 0
        if direction == E_Model.Direction.forward:
            tar_direction = 0
        elif direction == E_Model.Direction.backward:
            tar_direction = 180
        else:
            self.__print_move_direction_error_msg(sys._getframe().f_code.co_name, direction)
            return

        tar_speed = 0
        turn_speed = num_normal(turn_speed, 280, 5)
        if turn == E_Model.Direction.turn_left:
            tar_speed = turn_speed
        elif turn == E_Model.Direction.turn_right:
            tar_speed = -turn_speed
        else:
            self.__print_move_turn_error_msg(sys._getframe().f_code.co_name, turn)
            return

        speed = num_normal(speed, 80, 5)

        self.MODEL.transform_move_control(linear_speed=speed, direction=tar_direction, rotate_speed=tar_speed)

    def transform_motor_control(self, lf, rf, lb, rb):
        """
        控制变形车四个电机转动

        Args:
            lf (int):左前轮速度，[-360, 360] 单位 转/分
            rf (int):右前轮速度，[-360, 360] 单位 转/分
            lb (int):左后轮速度，[-360, 360] 单位 转/分
            rb (int):右后轮速度，[-360, 360] 单位 转/分

        Returns:
            无

        """
        lf = num_normal(lf, 360, -360)
        rf = num_normal(rf, 360, -360)
        lb = num_normal(lb, 360, -360)
        rb = num_normal(rb, 360, -360)
        self.MODEL.transform_motor_control(lf, rf, lb, rb)

    def transform_stop(self):
        """
        变形车停止运动

        Returns:
            无

        """
        self.MODEL.transform_stop()

    def transform_arm_control(self, joint, position, time):
        """
        设置变形车四个臂角度

        Args:
            joint (int): 臂(1:左前臂；2:左后臂；3:右后臂；4:右前臂)
            position (int): 角度，单位 度
            time (int): 时长，单位 ms

        Returns:
            无

        """
        self.MODEL.transform_arm_control(joint, position, int(time / 20))

    def transform_adaption_control(self, option):
        """
        开启/关闭自适应，变形车可以根据不同地形调整姿态

        Args:
            option (bool): 开关状态 True表示开，False表示关

        Returns:
            无

        """
        if option:
            self.MODEL.transform_adaption(E_Model.Adaption.ON)
        else:
            self.MODEL.transform_adaption(E_Model.Adaption.OFF)

    """

    >>>>>>>>>>>
    >> 麦轮车 <<
    >>>>>>>>>>>

    """

    """麦轮车
        """

    def mecanum_translate_speed(self, angle, speed):
        """
        麦轮车向指定方向做平移运动

        Args:
            angle (int): [-180, 180] 角度 单位:度(以XY为平面，Y轴为0度方向，左[0, -180] 右[0, 180])
            speed (int): [5-80] 前进/后退速度，单位 厘米/秒

        Returns:
            无

        """
        angle = num_normal(angle, 180, -180)
        speed = num_normal(speed, 80, 5)
        self.MODEL.mecanum_move_control(linear_speed=speed, direction=angle)

    def mecanum_translate_speed_times(self, angle, speed, times, unit):
        """
        麦轮车向指定方向做平移运动x秒/cm后停止

        Args:
            angle (int): [-180, 180] 角度 单位:度(以XY为平面，Y轴为0度方向，左[0, -180] 右[0, 180])
            speed (int): [5-80] 速度，单位 度/秒
            times (int): [0-200] 持续范围
            unit (int): 单位类型（0：表示按秒运动；1：表示按厘米运动）

        Returns:

        """
        if times == 0:
            # 时长/里程等于0，此积木块不做控制
            logging.error(' 时长/里程等于0，此积木块不做控制')
            return

        angle = num_normal(angle, 180, -180)
        speed = num_normal(speed, 80, 5)
        times = num_normal(times, 200, 0)

        if unit == E_Model.Unit.second:
            self.MODEL.mecanum_move_control(linear_speed=speed, direction=angle, time=times)
        elif unit == E_Model.Unit.mileage:
            self.MODEL.mecanum_move_control(linear_speed=speed, direction=angle, mileage=times)
        else:
            self.__print_move_unit_m_error_msg(sys._getframe().f_code.co_name, unit)

    def mecanum_move_xyz(self, x_speed, y_speed, z_speed):
        """
        控制麦轮车以指定速度沿指定方向持续运动

        Args:
            x_speed (int) : x轴方向速度 [-80, 80]
            y_speed (int) : y轴方向速度 [-80, 80]
            z_speed (int) : z轴方向速度 [-280, 280]

        Returns:

        """
        x_speed = num_normal(x_speed, 80, -80)
        y_speed = num_normal(y_speed, 80, -80)
        z_speed = num_normal(z_speed, 280, -280)
        self.MODEL.mecanum_xyz_control(x_speed, y_speed, z_speed)

    def mecanum_move_speed(self, direction, speed):
        """
        麦轮车前进/后退运动

        Args:
            direction (int): 方向（0：前进；1：后退）
            speed (int): [5-80] 速度，单位 厘米/秒

        Returns:
            无
        """
        speed = num_normal(speed, 80, 5)
        if direction == E_Model.Direction.forward:
            self.MODEL.mecanum_move_control(linear_speed=speed, direction=0)
        elif direction == E_Model.Direction.backward:
            self.MODEL.mecanum_move_control(linear_speed=speed, direction=180)
        else:
            self.__print_move_direction_error_msg(sys._getframe().f_code.co_name, direction)
            return

    def mecanum_turn_speed(self, turn, speed):
        """
        麦轮车左转/右转运动

        Args:
            turn (int): 方向（2：左转；3：右转）
            speed (int): [5-280] 速度，单位 度/秒

        Returns:
            无

        """
        speed = num_normal(speed, 280, 5)
        if turn == E_Model.Direction.turn_left:
            self.MODEL.mecanum_move_control(rotate_speed=speed)
        elif turn == E_Model.Direction.turn_right:
            self.MODEL.mecanum_move_control(rotate_speed=-speed)
        else:
            self.__print_move_turn_error_msg(sys._getframe().f_code.co_name, turn)

    def mecanum_move_speed_times(self, direction, speed, times, unit):
        """
        控制麦轮车前后运动x秒/cm后停止

        Args:
            direction (int): 方向（0：前进；1：后退）
            speed (int): [5-80] 速度，单位 厘米/秒
            times (int): [0-200] 持续范围
            unit (int): 单位类型（0：表示按秒运动；1：表示按厘米运动）

        Returns:
            无

        """
        tar_direction = 0
        if direction == E_Model.Direction.forward:
            tar_direction = 0
        elif direction == E_Model.Direction.backward:
            tar_direction = 180
        else:
            self.__print_move_direction_error_msg(sys._getframe().f_code.co_name, direction)
            return

        if times == 0:
            # 时长/里程等于0，此积木块不做控制
            logging.error(' 时长/里程等于0，此积木块不做控制')
            return

        speed = num_normal(speed, 80, 5)
        times = num_normal(times, 200, 0)

        if unit == E_Model.Unit.second:
            self.MODEL.mecanum_move_control(linear_speed=speed, direction=tar_direction, time=times)
        elif unit == E_Model.Unit.mileage:
            self.MODEL.mecanum_move_control(linear_speed=speed, direction=tar_direction, mileage=times)
        else:
            self.__print_move_unit_m_error_msg(sys._getframe().f_code.co_name, unit)

    def mecanum_turn_speed_times(self, turn, speed, times, unit):
        """
        控制麦轮车左右运动x秒/度后停止

        Args:
            turn (int): 方向（2：左转；3：右转）
            speed (int): [5-280] 速度，单位 度/秒
            times (int): [0-200] 持续范围
            unit (int): 单位类型（0：表示按秒运动；2：表示按度运动）

        Returns:
            无
        """
        speed = num_normal(speed, 280, 5)
        tar_speed = 0
        if turn == E_Model.Direction.turn_left:
            tar_speed = speed
        elif turn == E_Model.Direction.turn_right:
            tar_speed = -speed
        else:
            self.__print_move_turn_error_msg(sys._getframe().f_code.co_name, turn)
            return

        if times == 0:
            # 时长/里程等于0，此积木块不做控制
            logging.error(' 时长/里程等于0，此积木块不做控制')
            return

        times = num_normal(times, 200, 0)

        if unit == E_Model.Unit.second:
            self.MODEL.mecanum_move_control(rotate_speed=tar_speed, time=times)
        elif unit == E_Model.Unit.angle:
            self.MODEL.mecanum_move_control(rotate_speed=tar_speed, target_angle=times)
        else:
            self.__print_move_unit_a_error_msg(sys._getframe().f_code.co_name, unit)

    def mecanum_move_turn(self, angle, speed, turn, turn_speed):
        """
        控制麦轮车向指定方向运动同时做旋转运动

        Args:
            angle (int): [-180, 180] 角度 单位:度(以XY为平面，Y轴为0度方向，左[0, -180] 右[0, 180])
            speed (int): [5-80] 前进/后退速度，单位 厘米/秒
            turn (int): 方向（2：左转；3：右转）
            turn_speed (int): [5-280] 旋转速度，单位 度/秒

        Returns:
            无

        """
        angle = num_normal(angle, 180, -180)
        tar_speed = 0
        turn_speed = num_normal(turn_speed, 280, 5)
        if turn == E_Model.Direction.turn_left:
            tar_speed = turn_speed
        elif turn == E_Model.Direction.turn_right:
            tar_speed = -turn_speed
        else:
            self.__print_move_turn_error_msg(sys._getframe().f_code.co_name, turn)
            return

        speed = num_normal(speed, 80, 5)

        self.MODEL.mecanum_move_control(linear_speed=speed, direction=angle, rotate_speed=tar_speed)

    def mecanum_motor_control(self, lf, rf, lb, rb):
        """
        控制麦轮车四个电机转动

        Args:
            lf (int):左前轮速度，[-360, 360] 单位 转/分
            rf (int):右前轮速度，[-360, 360] 单位 转/分
            lb (int):左后轮速度，[-360, 360] 单位 转/分
            rb (int):右后轮速度，[-360, 360] 单位 转/分

        Returns:
            无

        """
        lf = num_normal(lf, 360, -360)
        rf = num_normal(rf, 360, -360)
        lb = num_normal(lb, 360, -360)
        rb = num_normal(rb, 360, -360)
        self.MODEL.mecanum_motor_control(lf, rf, lb, rb)

    def mecanum_stop(self):
        """
        麦轮车停止运动

        Returns:
            无

        """
        self.MODEL.mecanum_stop()

    """

    >>>>>>>>>>>
    >> 平衡车 <<
    >>>>>>>>>>>

    """

    def balance_start_balancing(self):
        """
        启动小车并保持自平衡

        Returns:
            无
        """
        self.MODEL.balance_keep_balancing(True)

    def balance_stop_balancing(self):
        """
        停止小车并保持自平衡

        Returns:
            无
        """
        self.MODEL.balance_keep_balancing(False)

    def balance_set_acceleration(self, acceleration):
        """
        设置平衡车加速度

        Args:
            acceleration (float): 加速度

        Returns:
            无
        """

        if not (isinstance(acceleration, float) or isinstance(acceleration, int)):
            typestr = 'int is required (got type {})'.format(type(acceleration).__name__)
            func_name = sys._getframe().f_code.co_name
            error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
            print(error_msg)
            return
        if acceleration > 0:
            self.MODEL.setBalanceAcceleration(acceleration)

    def balance_reset_acceleration(self):
        """
        重置平衡车加速度

        Returns:
            无
        """
        self.MODEL.resetAcceleration('all')

    def balance_move_speed(self, direction, speed):
        """
        平衡车前进/后退运动

        Args:
            direction (int): 方向（0：前进；1：后退）
            speed (int): [5-80] 速度，单位 厘米/秒

        Returns:
            无
        """
        speed = num_normal(speed, 80, 5)
        if direction == E_Model.Direction.forward:
            self.MODEL.balance_move_control(linear_speed=speed, direction=0)
        elif direction == E_Model.Direction.backward:
            self.MODEL.balance_move_control(linear_speed=speed, direction=180)
        else:
            self.__print_move_direction_error_msg(sys._getframe().f_code.co_name, direction)
            return

    def balance_turn_speed(self, turn, speed):
        """
        平衡车左转/右转运动

        Args:
            turn (int): 方向（2：左转；3：右转）
            speed (int): [5-360] 速度，单位 度/秒

        Returns:
            无
        """
        # 平衡车转动速度限制5-360
        speed = num_normal(speed, 360, 5)
        if turn == E_Model.Direction.turn_left:
            self.MODEL.balance_move_control(rotate_speed=speed)
        elif turn == E_Model.Direction.turn_right:
            self.MODEL.balance_move_control(rotate_speed=-speed)
        else:
            self.__print_move_turn_error_msg(sys._getframe().f_code.co_name, turn)

    def balance_move_speed_times(self, direction, speed, times, unit):
        """
        控制平衡车前后运动x秒/cm后停止

        Args:
            direction (int): 方向（0：前进；1：后退）
            speed (int): [5-80] 速度，单位 厘米/秒
            times (int): [0-200] 持续范围
            unit (int): 单位类型（0：表示按秒运动；1：表示按厘米运动）

        Returns:
            无

        """
        tar_direction = 0
        if direction == E_Model.Direction.forward:
            tar_direction = 0
        elif direction == E_Model.Direction.backward:
            tar_direction = 180
        else:
            self.__print_move_direction_error_msg(sys._getframe().f_code.co_name, direction)
            return

        if times == 0:
            # 时长/里程等于0，此积木块不做控制
            logging.error(' 时长/里程等于0，此积木块不做控制')
            return

        speed = num_normal(speed, 80, 5)
        times = num_normal(times, 200, 0)

        if unit == E_Model.Unit.second:
            self.MODEL.balance_move_control(linear_speed=speed, direction=tar_direction, time=times)
        elif unit == E_Model.Unit.mileage:
            self.MODEL.balance_move_control(linear_speed=speed, direction=tar_direction, mileage=times)
        else:
            self.__print_move_unit_m_error_msg(sys._getframe().f_code.co_name, unit)

    def balance_turn_speed_times(self, turn, speed, times, unit):
        """
        控制平衡左右运动x秒/度后停止

        Args:
            turn (int): 方向（2：左转；3：右转）
            speed (int): [5-360] 速度，单位 度/秒
            times (int): [0-200] 持续范围
            unit (int): 单位类型（0：表示按秒运动；2：表示按度运动）

        Returns:
            无
        """
        tar_speed = 0
        speed = num_normal(speed, 360, 5)
        if turn == E_Model.Direction.turn_left:
            tar_speed = speed
        elif turn == E_Model.Direction.turn_right:
            tar_speed = -speed
        else:
            self.__print_move_turn_error_msg(sys._getframe().f_code.co_name, turn)
            return

        if times == 0:
            # 时长/里程等于0，此积木块不做控制
            logging.error(' 时长/里程等于0，此积木块不做控制')
            return

        times = num_normal(times, 200, 0)

        if unit == E_Model.Unit.second:
            self.MODEL.balance_move_control(rotate_speed=tar_speed, time=times)
        elif unit == E_Model.Unit.angle:
            self.MODEL.balance_move_control(rotate_speed=tar_speed, target_angle=times)
        else:
            self.__print_move_unit_a_error_msg(sys._getframe().f_code.co_name, unit)

    def balance_move_turn(self, direction, speed, turn, turn_speed):
        """
        控制平衡车指定方向运动同时做旋转

        Args:
            direction (int): 方向（0：前进；1：后退）
            speed (int): [5-80] 前进/后退速度，单位 厘米/秒
            turn (int): 方向（2：左转；3：右转）
            turn_speed (int): [5-360] 旋转速度，单位 度/秒

        Returns:
            无
        """
        tar_direction = 0
        if direction == E_Model.Direction.forward:
            tar_direction = 0
        elif direction == E_Model.Direction.backward:
            tar_direction = 180
        else:
            self.__print_move_direction_error_msg(sys._getframe().f_code.co_name, direction)
            return

        tar_speed = 0
        # 平衡车转动速度限制0-360
        turn_speed = num_normal(turn_speed, 360, 5)
        if turn == E_Model.Direction.turn_left:
            tar_speed = turn_speed
        elif turn == E_Model.Direction.turn_right:
            tar_speed = -turn_speed
        else:
            self.__print_move_turn_error_msg(sys._getframe().f_code.co_name, turn)
            return

        speed = num_normal(speed, 80, 5)

        self.MODEL.balance_move_control(linear_speed=speed, direction=tar_direction, rotate_speed=tar_speed)


    """

    >>>>>>>>>>>
    >> 机械臂 <<
    >>>>>>>>>>>

    """

    def mechanical_clamp_release(self):
        """
        打开夹手

        Returns:
            无
        """
        self.SERVO.controlSingleClamp(0)

    def mechanical_clamp_close(self):
        """
        闭合夹手

        Returns:
            无
        """
        self.SERVO.controlSingleClamp(1)

    def mechanical_get_clamp_status(self):
        """
        获取夹手状态

        Returns:
            状态 (int): 0 打开，1，闭合

        """
        result = self.SERVO.getClampStatus()
        return result

    def mechanical_arms_restory(self):
        """
        机械臂复位

        Returns:
            无
        """
        self.SERVO.roboticArmRestory()

    def mechanical_joint_control(self, angle1, angle2, angle3, duration):
        """
        机械臂关节角度控制

        Args:
            angle1 (int): 关节1角度 [-90, 90] 单位：度
            angle2 (int): 关节2角度 [-80, 110] 单位：度
            angle3 (int): 关节3角度 [-90, 90] 单位：度
            duration (int): 运行时长 [20, 5000] 单位：毫秒

        Returns:

        """
        params = []
        angle1 = num_normal(angle1, 90, -90)
        angle2 = num_normal(angle2, 110, -80)
        angle3 = num_normal(angle3, 90, -90)
        duration = num_normal(duration, 5000, 20)
        params.append({'joint': 1, 'position': angle1, 'time': duration})
        params.append({'joint': 2, 'position': angle2, 'time': duration})
        params.append({'joint': 3, 'position': angle3, 'time': duration})
        self.SERVO.roboticArmSetJointPosition(params, 1)

    def mechanical_single_joint_control(self, joint, angle, duration):
        """
        机械臂单个关节角度控制

        Args:
            joint (int) : 关节序号(1: 关节1, 2: 关节2, 3: 关节3)
            angle (int) : 关节角度(关节1：[-90, 90], 关节2：[-80, 110], 关节3：[-90, 90], )
            duration (int): 运行时长 [20, 5000] 单位：毫秒

        Returns:
            无

        """
        valid_joint = True

        if joint == 1:
            angle = num_normal(angle, 90, -90)
        elif joint == 2:
            angle = num_normal(angle, 110, -80)
        elif joint == 3:
            angle = num_normal(angle, 90, -90)
        else:
            valid_joint = False

        if valid_joint:
            duration = num_normal(duration, 5000, 20)
            params = [{'joint': joint, 'position': angle, 'time': duration}]
            self.SERVO.roboticArmSetJointPosition(params, 1)
        else:
            typestr = 'invalid value of joint id, expected 1/2/3, got {}'.format(joint)
            func_name = sys._getframe().f_code.co_name
            error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
            print(error_msg)

    def mechanical_move_axis(self, x, y, z, duration):
        """
        以小车为坐标系，逆解算机械臂，移动到位置x,y,z

        Args:
            x (float/int): x坐标 [-5, 25] 单位cm
            y (float/int): y坐标 [-25, 25] 单位cm
            z (float/int): z坐标 [-16, 16] 单位cm
            duration (int): 运行时长 [20, 5000] 单位：毫秒

        Returns:

        """
        error_value = None
        if not (isinstance(x, float) or isinstance(x, int)):
            error_value = x
        elif not (isinstance(y, float) or isinstance(y, int)):
            error_value = y
        elif not (isinstance(z, float) or isinstance(z, int)):
            error_value = z

        if error_value is not None:
            func_name = sys._getframe().f_code.co_name
            typestr = 'int or float is required (got type {})'.format(type(error_value).__name__)
            error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
            print(error_msg)
            return

        x = int(x * 10)  # 换算成mm
        x = num_normal(x, 250, -50)

        y = int(y * 10)  # 换算成mm
        y = num_normal(y, 250, -250)

        z = int(z * 10)  # 换算成mm
        z = num_normal(z, 160, -160)

        duration = num_normal(duration, 5000, 20)

        self.SERVO.roboticArmMoveToTargetPostion(x, y, z, duration)

    def __print_move_direction_error_msg(self, func_name, input_value):
        typestr = 'invalid value of direction, expected 0 or 1, got {}'.format(input_value)
        error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
        print(error_msg)

    def __print_move_turn_error_msg(self, func_name, input_value):
        typestr = 'invalid value of turn, expected 2 or 3, got {}'.format(input_value)
        error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
        print(error_msg)

    def __print_move_unit_m_error_msg(self, func_name, input_value):
        typestr = 'invalid value of unit, expected 0 or 1, got {}'.format(input_value)
        error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
        print(error_msg)

    def __print_move_unit_a_error_msg(self, func_name, input_value):
        typestr = 'invalid value of unit, expected 0 or 2, got {}'.format(input_value)
        error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
        print(error_msg)

    """

       >>>>>>>>>>>
       >> AI视觉 <<
       >>>>>>>>>>>

       """
    def load_models(self, models):
        """
        加载模型，可选多个

        Args:
            models (list): 要加载的模型列表，对应关系为： knn: 'custom_knn', 人体姿态: 'human_pose', 文字识别: 'word_recognition',
                                                    颜色识别: 'color_recognition', ArpilTag/二维码: 'apriltag_qrcode',
                                                    表情识别/人脸特征: 'face_attribute', 车牌识别: 'lpd_recognition', 手势识别: 'gesture',
                                                    交通识别标识: 'traffic_sign', 人脸识别: 'face_recognition', 单轨/双轨: 'line_recognition'

        Returns:
            是否加载成功 True or False
        """
        if not len(models):
            typestr = 'models is empty!'
            func_name = sys._getframe().f_code.co_name
            error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
            print(error_msg)
            return False
        elif not isinstance(models, list):
            typestr = 'list is required (got type {})'.format(type(models).__name__)
            func_name = sys._getframe().f_code.co_name
            error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
            print(error_msg)
            return False
        return self.VISION.load_models(models)

    def release_models(self, models = None):
        """
        卸载模型

        Args:
            models (list): 要卸载的模型列表，参数同load_models的参数。默认为None，如果不传，则卸载所有模型

        Returns:
            是否卸载成功 True or False
        """
        self.VISION.release_models(models)

    def get_qrcode_apriltag_total_info(self):
        """
        获取二维码&AprilTag信息

        Args:
            无
        Returns:
            二维码&AprilTag识别结果 (list): [qrcode, id, center_x, center_y, height, width, area, distance5, distance7, distance10, x, y, z]
                                :qrcode(str): 二维码内容
                                :id(int): AprilTag id
                                :center_x(float): AprilTag 中心点x
                                :center_y(float): AprilTag 中心点y
                                :height(float): AprilTag 高度
                                :width(float): AprilTag 宽度
                                :area(float): AprilTag 面积
                                :distance5(float): AprilTag(5x5cm)距离
                                :distance7(float): AprilTag(7x7cm)距离
                                :distance10(float): AprilTag(10x10cm)距离
                                :x(float): AprilTag卡片姿态角度 x
                                :y(float): AprilTag卡片姿态角度 y
                                :z(float): AprilTag卡片姿态角度 z
        """
        result = self.VISION.qrcode_inference()

        qrcode = ''
        id = center_x = center_y = height = width = area = dis5 = dis7 = dis10 = x = y = z = -1

        if result is not None:
            data = json.loads(result)
            if data is not None:
                if 'qrcode' in data:
                    qrcode_list = data["qrcode"]

                    max_item = None
                    max_area = 0
                    for item in qrcode_list:
                        position = item['position']
                        t_area = position[2] * position[3]
                        if t_area > max_area:
                            max_area = t_area
                            max_item = item
                    if max_item is not None:
                        qrcode = max_item['data']
                if 'apriltag' in data:
                    apriltag_list = data["apriltag"]
                    max_item = None
                    max_area = 0
                    for item in apriltag_list:
                        position = item['position']
                        t_area = position[2] * position[3]
                        if t_area > max_area:
                            max_area = t_area
                            max_item = item
                    if max_item is not None:
                        position = max_item['position']
                        id = max_item['id']
                        center_x = round(max_item['center'][0], 2)
                        center_y = round(max_item['center'][1], 2)
                        height = round(position[3], 2)
                        width = round(position[2], 2)
                        area = round(position[3] * position[2], 2)
                        dis5 = round(max_item['instance'][0], 2)
                        dis7 = round(max_item['instance'][1], 2)
                        dis10 = round(max_item['instance'][2], 2)
                        x = round(max_item['pose_ypr'][0], 2)
                        y = round(max_item['pose_ypr'][1], 2)
                        z = round(max_item['pose_ypr'][2], 2)

        result = [qrcode, id, center_x, center_y, height, width, area, dis5, dis7, dis10, x, y, z]
        return result

    def get_license_plate_total_info(self):
        """
        获取车牌信息

        Args:
            无

        Returns:
            车牌识别结果 (list): [number, type, center_x, center_y, height, width, area]
                        :number(str): 车牌号
                        :type(str): 车牌类型（蓝牌/绿牌）
                        :center_x(float): 中心点x
                        :center_y(float): 中心点y
                        :height(float): 高度
                        :width(float): 宽度
                        :area(float): 面积
        """

        response = self.VISION.license_plate_inference()

        number = typestr = ''
        center_x = center_y = height = width = area = -1

        if response is not None:
            data = json.loads(response)
            if data is not None and isinstance(data, list):
                max_item = None
                max_area = 0
                for item in data:
                    position = item['position']
                    t_area = position[2] * position[3]
                    if t_area > max_area:
                        max_area = t_area
                        max_item = item

                # [{'lp': 'äº¬Q58A77', 'position': [297, 264, 109, 36], 'type': 'è\x93\x9dç\x89\x8c'}]
                if max_item is not None:
                    number = max_item['lp']
                    type = max_item['type']
                    if type == E_Vision.LPD.blue:
                        typestr = '蓝牌'
                    elif type == E_Vision.LPD.green:
                        typestr = '绿牌'
                    position = max_item['position']
                    center_x = position[0] + position[2] / 2
                    center_y = position[1] + position[3] / 2
                    width = position[2]
                    height = position[3]
                    area = position[2] * position[3]
        result = [number, typestr, center_x, center_y, height, width, area]
        logging.debug("get_license_plate_total_info `s result  is :{}".format(result))
        return result

    def get_pose_total_info(self):
        """
        返回识别到的人体关键点坐标

        Args:
            无

        Returns:
            姿势识别结果(list) [右耳x, y, 右眼x, y, 鼻子x, y, 左眼x, y, 左耳x, y, 右手x, y, 右肘x, y, 右肩x, y, 左肩x, y, 左肘x, y, 左手x, y, 右胯x, y, 左胯x, y, 右膝x, y, 左膝x, y, 右脚x, y, 左脚x, y, ]
        """
        response = self.VISION.pose_identify()

        indexes = []

        if response is not None:
            data = json.loads(response)
            if data is not None and isinstance(data, list):
                if len(data) > 0:
                    pose = data[0]['keypoint']
                    for idx in E_Vision.Pose.TotalPoseIndexes:
                        x = y = 0
                        if idx < len(pose):
                            points = pose[idx]
                            x = int(round(points['x'], 0))
                            y = int(round(points['y'], 0))
                            x = max(0, x)  # 小于0按照0处理
                            y = max(0, y)  # 小于0按照0处理

                        indexes.extend([x, y])
        if len(indexes) == 0:
            # 未识别到结果
            for idx in E_Vision.Pose.TotalPoseIndexes:
                indexes.extend([0, 0])
        logging.debug("get_pose_total_info `s result  is :{}".format(indexes))
        return indexes

    """交通识别
        """

    def get_traffic_total_info(self):
        """
        获取交通标志识别结果

        Args:
            无

        Returns:
            交通标志识别结果 (list): [sign, center_x, center_y, height, width, area]
                        :sign(str): 交通标志(绿灯, 鸣笛, 左转, 右转, 斑马线, 红灯, 注意儿童, 禁止长时间停车, 进入隧道, 黄灯)
                        :center_x(float): 中心点x
                        :center_y(float): 中心点y
                        :height(float): 高度
                        :width(float): 宽度
                        :area(float): 面积
        """

        response = self.VISION.traffic_inference()

        sign = ''
        center_x = center_y = height = width = area = -1

        if response is not None:
            data = json.loads(response)
            if data is not None and isinstance(data, list):
                max_item = None
                max_area = 0
                for item in data:
                    position = item['position']
                    t_area = position[2] * position[3]
                    if t_area > max_area:
                        max_area = t_area
                        max_item = item

                if max_item is not None:
                    label = max_item["label"]
                    if label in E_Vision.Traffic.TrafficSigns:
                        sign = E_Vision.Traffic.TrafficSigns[label]
                    position = max_item['position']
                    center_x = round(position[0] + position[2] / 2, 2)
                    center_y = round(position[1] + position[3] / 2, 2)
                    width = round(position[2], 2)
                    height = round(position[3], 2)
                    area = round(position[2] * position[3], 2)
            else:
                logging.debug("warning-----no data in traffic_inference")
        result = [sign, center_x, center_y, height, width, area]
        logging.debug("get_traffic_total_info `s result is :{}".format(result))
        return result

    def get_face_recognition_total_info(self):
        """
        人脸识别结果

        Returns:
            人脸识别结果(list): [name, count, center_x, center_y, height, width, area]
                        :name(str): 姓名（不认识的话则为陌生人）
                        :count(int): 识别到的人脸数量
                        :center_x(float): 中心点x
                        :center_y(float): 中心点y
                        :height(float): 高度
                        :width(float): 宽度
                        :area(float): 面积
        """
        response = self.VISION.face_recognition_inference()
        name = ''
        count = 0
        center_x = center_y = height = width = area = -1

        if response is not None:
            data = json.loads(response)
            if data is not None and isinstance(data, list):
                count = len(data)
                max_item = None
                max_area = 0
                for item in data:

                    position = item['position']
                    t_area = position[2] * position[3]
                    if t_area > max_area:
                        max_area = t_area
                        max_item = item

                # {'emotion': 2, 'gender': 0, 'mask': 1, 'position': [0, 14, 103, 199]}
                # mask:0——带口罩，1——未戴口罩，2——口罩没有正确佩戴
                if max_item is not None:
                    name = max_item['name']
                    if name == '':  # 有返回人脸，但是是没录入的，认为是陌生人
                        name = '陌生人'
                    position = max_item['position']
                    center_x = position[0] + position[2] / 2
                    center_y = position[1] + position[3] / 2
                    width = position[2]
                    height = position[3]
                    area = position[2] * position[3]

        result = [name, count, center_x, center_y, height, width, area]
        logging.debug("get_face_recognition_total_info `s result  is :{}".format(result))
        return result

    def get_face_characteristic_total_info(self):
        """
        获取人脸特征识别结果

        Args:
            无

        Returns:
            人脸特征识别结果 (list): [gender, mask_info, emotion, male_count, female_count, mask_count, notwell_mask_count, unmask_count, center_x, center_y, height, width, area]
                            :gender(str): 性别
                            :mask_info(str): 口罩情况
                            :emotion(str): 表情
                            :male_count(int): 男性数量
                            :female_count(int): 女性数量
                            :mask_count(int): 佩戴口罩数量
                            :notwell_mask_count(int): 未佩戴好口罩数量
                            :unmask_count(int): 未佩戴口罩数量
                            :center_x(float): 中心点x
                            :center_y(float): 中心点y
                            :height(float): 高度
                            :width(float): 宽度
                            :area(float): 面积
        """
        response = self.VISION.face_characteristic_inference()

        gender_str = mask_str = emotion_str = ''
        male_count = female_count = mask_count = notwell_mask_count = unmask_count = 0
        center_x = center_y = height = width = area = -1

        if response is not None:
            data = json.loads(response)
            if data is not None and isinstance(data, list):
                max_item = None
                max_area = 0
                for item in data:

                    # 统计性别&口罩数量
                    gender = item["gender"]
                    mask = item["mask"]
                    if gender == 0:
                        male_count += 1
                    elif gender == 1:
                        female_count += 1

                    if mask == 0:
                        mask_count += 1
                    elif mask == 2:
                        notwell_mask_count += 1
                    elif mask == 1:
                        unmask_count += 1

                    position = item['position']
                    t_area = position[2] * position[3]
                    if t_area > max_area:
                        max_area = t_area
                        max_item = item

                # {'emotion': 2, 'gender': 0, 'mask': 1, 'position': [0, 14, 103, 199]}
                # mask:0——带口罩，1——未戴口罩，2——口罩没有正确佩戴
                if max_item is not None:
                    gender = max_item["gender"]
                    if gender == 0:
                        gender_str = '男性'
                    elif gender == 1:
                        gender_str = '女性'

                    mask = max_item["mask"]
                    if mask == 0:
                        mask_str = '佩戴口罩'
                    elif mask == 1:
                        mask_str = '未佩戴口罩'
                    elif mask == 2:
                        mask_str = '未佩戴好口罩'
                    emotion = max_item["emotion"]
                    if emotion == 0:  # '生气'
                        emotion_str = '生气'
                    elif emotion == 1:  # '开心'
                        emotion_str = '开心'
                    elif emotion == 2:  # '平静'
                        emotion_str = '平静'
                    elif emotion == 3:  # '惊讶'
                        emotion_str = '惊讶'

                    position = max_item['position']
                    center_x = position[0] + position[2] / 2
                    center_y = position[1] + position[3] / 2
                    width = position[2]
                    height = position[3]
                    area = position[2] * position[3]

        result = [gender_str, mask_str, emotion_str, male_count, female_count, mask_count, notwell_mask_count,
                  unmask_count, center_x, center_y, height, width, area]
        logging.debug("get_face_characteristic_total_info `s result  is :{}".format(result))
        return result

    def __judge_track_line_type(self, data):
        cross_type = E_Vision.Intersection.noline  # 线类型
        line_type = E_Vision.LineType.single  # 单双轨类型
        max_item = None

        # 当没有检测到线、也没有检测到标志的时候，表示——无线
        # 当没有检测到标志，但是有线的时候，表示——一条线

        # 判断单轨还是双轨
        if "single_start" in data and "single_end" in data:
            line_type = E_Vision.LineType.single
        elif "double_start" in data and "double_end" in data:
            line_type = E_Vision.LineType.double

        # 先判断是不是有标志牌
        has_sign = False
        if "traffic_sign" in data:
            traffic_sign = data["traffic_sign"]
            if not isinstance(traffic_sign, list) or not len(traffic_sign):
                # 标志数组为空，按没有标识处理
                has_sign = False

            max_area = 0
            for item in traffic_sign:
                position = item["position"]
                area = position[2] * position[3]
                if area > max_area:
                    max_area = area
                    max_item = item
            if max_item is not None:
                has_sign = True

        if has_sign:
            # 有标志牌，按照标志牌里的路口
            if "label" in max_item:
                label = max_item["label"]
                # 有标志，按标志路口走
                if label == 0:
                    cross_type = E_Vision.Intersection.crossroad
                elif label == 1:
                    cross_type = E_Vision.Intersection.ycross
        else:
            # 没有标志，判断线类型
            if "single_start" in data and "single_end" in data:
                single_start = data["single_start"]
                single_end = data["single_end"]
                if single_start[0] == -1 and single_start[1] == -1 and single_end[0] == -1 and single_end[1] == -1:
                    cross_type = E_Vision.Intersection.noline
                else:
                    cross_type = E_Vision.Intersection.straight
            elif "double_start" in data and "double_end" in data:
                double_start = data["double_start"]
                double_end = data["double_end"]
                if double_start[0] == -1 and double_start[1] == -1 and double_end[0] == -1 and double_end[1] == -1:
                    cross_type = E_Vision.Intersection.noline
                else:
                    cross_type = E_Vision.Intersection.straight

        # print("----cross_type:{}, line_type:{} max_item:{}".format(cross_type, line_type, max_item))

        return cross_type, line_type, max_item

    def set_track_recognition_line(self, line_type):
        """
        设置当前识别的车道线类型

        Args:
            line_type (int): 0: 单轨, 1: 双轨

        Returns:
            无
        """
        if not (line_type == 0 or line_type == 1):
            func_name = sys._getframe().f_code.co_name
            typestr = 'invalid value of line_type, expected 0 or 1, got {}'.format(line_type)
            error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
            print(error_msg)
            return
        self.VISION.set_track_color_line(0, line_type)

    def get_single_track_total_info(self):
        """
        获取单轨识别结果

        Args:
            无

        Returns:
            单轨识别结果(list): [offset, type, x, y]
                        :offset(int): 单轨偏移量
                        :type(int): 单轨线类型(1 直线, 2 y字路口, 3 十字路口, 0 无线)
                        :x(float): 路口坐标x
                        :y(float): 路口坐标y
        """
        logging.debug("get_single_track_total_info ")

        offset = type = center_x = center_y = 0

        response = self.VISION.track_recognition_inference()

        if response is not None:
            data = json.loads(response)
            if data is not None:
                cross_type, line_type, max_item = self.__judge_track_line_type(data)

                # 路口类型
                if line_type == E_Vision.LineType.single:
                    if cross_type == E_Vision.Intersection.straight:  # 1 直线
                        type = 1
                    elif cross_type == E_Vision.Intersection.ycross:  # 2 y字路口
                        type = 2
                    elif cross_type == E_Vision.Intersection.crossroad:  # 3 十字路口
                        type = 3
                    else:
                        type = 0  # 其余情况默认为无线
                else:
                    type = 0  # 轨道类型不一致，返回无线

                # 坐标
                if max_item is not None:
                    position = max_item["position"]
                    center_x = position[0] + position[2] / 2
                    center_y = position[1] + position[3] / 2

                # 偏移量
                if 'offset' in data:
                    offset = data['offset']

        result = [offset, type, center_x, center_y]

        logging.debug(' get_single_track_total_info `s result is :{}'.format(result))

        return result

    def get_double_track_total_info(self):
        """
        获取双轨识别结果

        Args:
            无

        Returns:
            双轨识别结果(list): [offset, type, x, y]
                        :offset(int): 双轨偏移量
                        :type(int): 双轨线类型(1 直线, 2 路口, 0 无线)
                        :x(float): 路口坐标x
                        :y(float): 路口坐标y
        """

        offset = type = center_x = center_y = 0

        response = self.VISION.track_recognition_inference()
        if response is not None:
            data = json.loads(response)
            if data is not None:
                cross_type, line_type, max_item = self.__judge_track_line_type(data)

                # 路口类型
                if line_type == E_Vision.LineType.double:
                    if cross_type == E_Vision.Intersection.straight:  # 1 直线
                        type = 1
                    # y字路口和十字路口都返回2
                    elif cross_type == E_Vision.Intersection.ycross:  # 2 y字路口
                        type = 2
                    elif cross_type == E_Vision.Intersection.crossroad:  # 3 十字路口
                        type = 2
                    else:
                        type = 0  # 其余情况默认为无线
                else:
                    type = 0  # 轨道类型不一致，返回无线

                # 坐标
                if max_item is not None:
                    position = max_item["position"]
                    center_x = position[0] + position[2] / 2
                    center_y = position[1] + position[3] / 2

                # 偏移量
                if 'offset' in data:
                    offset = data['offset']

        result = [offset, type, center_x, center_y]

        logging.debug(' get_double_track_total_info `s result is :{}'.format(result))

        return result

    def get_color_total_info(self):
        """
        获取颜色识别结果

        Args:
            无

        Returns:
            颜色识别结果 (list): [color, shape, center_x, center_y, height, width, area]
                        :color(str): 颜色
                        :shape(str): 形状(小球/方块)
                        :center_x(float): 中心点x
                        :center_y(float): 中心点y
                        :height(float): 高度
                        :width(float): 宽度
                        :area(float): 面积
        """
        response = self.VISION.color_identify()

        colorstr = typestr = ''
        center_x = center_y = height = width = area = -1

        if response is not None:
            data = json.loads(response)
            if data is not None and isinstance(data, list):
                max_item = None
                max_area = 0
                for item in data:
                    position = item['position']
                    t_area = position[2] * position[3]
                    if t_area > max_area:
                        max_area = t_area
                        max_item = item

                # [{'area': 34581, 'color': 'red', 'shape': 'ball', "position" : [ 119, 272, 164, 143 ]}]
                if max_item is not None:
                    color = max_item['color']
                    if color == 'red':
                        colorstr = '红色'
                    elif color == 'orange':
                        colorstr = '橙色'
                    elif color == 'yellow':
                        colorstr = '黄色'
                    elif color == 'green':
                        colorstr = '绿色'
                    elif color == 'blue':
                        colorstr = '蓝色'
                    elif color == 'purple':
                        colorstr = '紫色'
                    shape = max_item['shape']
                    if shape == 'ball':
                        typestr = '小球'
                    elif shape == 'square':
                        typestr = '方块'
                    position = max_item['position']
                    center_x = position[0] + position[2] / 2
                    center_y = position[1] + position[3] / 2
                    width = position[2]
                    height = position[3]
                    area = position[2] * position[3]

        result = [colorstr, typestr, center_x, center_y, height, width, area]
        logging.debug("get_color_total_info `s result  is :{}".format(result))
        return result

    def get_words_result(self):
        """
        获取文字识别结果

        Args:
            无

        Returns:
            文字识别结果 (str):
        """
        result = self.VISION.word_identify()

        empty_ret = ''

        if result is not None:
            data = json.loads(result)
            if not 'words' in data:
                return empty_ret
            words = data["words"]
            if not isinstance(words, list):
                return empty_ret
            if len(words) > 0:
                ret = ','.join(words)
                logging.debug("get_words_result result is :{}".format(ret))
                return ret
        return empty_ret

    def get_gesture_result(self):
        """
        获取手势识别结果

        Args:
            无

        Returns:
            手势识别结果 (str): (石头/剪刀/布/ok/点赞)
        """
        result = self.VISION.gesture_inference()
        ret = ''

        if result is not None:
            data = json.loads(result)
            if data is None:
                return ret
            gesture = data["gesture"]
            if gesture == 'stone':
                ret = '石头'
            elif gesture == 'scissor':
                ret = '剪刀'
            elif gesture == 'palm':
                ret = '布'
            elif gesture == 'ok':
                ret = 'OK'
            elif gesture == 'good':
                ret = '点赞'
            else:
                ret = ''
            logging.debug('-------get_gesture_result is {}'.format(ret))
            return ret
            # {'confidence': 0.92, 'gesture': 'palm', 'position': [121, 352, 365, 244]]}
        return ret

    # def start_auto_inference(self, models):
    #     response = self.VISION.startAutoInference(models)
    #     for item in response:
    #         print('111111',item)
    #         yield item

    """

    >>>>>>>>>>>
    >> 语音 <<
    >>>>>>>>>>>

    """

    def play_sound(self, data, wait=False):
        """
        播放内置音效

        Args:
            data (str): 待播放内容
                    动物分类: bear 熊, bird 鸟, chicken 鸡, cow 牛, dog 狗, elephant 大象, giraffe 长颈鹿, horse 马, lion 狮子, monkey 猴子, pig 猪, rhinoceros 犀牛, sealions 海狮, tiger 老虎, walrus 海象
                    命令分类: complete 完成, cover 掩护, move 移动, received 收到, support 支援, transfiguration 变身, yes 遵命
                    情绪分类: happy 高兴, yawn 哈欠, snoring 呼噜, surprise 惊讶, actingcute 热泪盈眶, angry 生气, fail 失败, lose 失落, doubt 疑问, nonsense 呓语, cheerful 愉快, come_and_play 歌曲1, flexin 歌曲2, london_bridge 歌曲3, yankee_doodle 歌曲4
                    机器分类: ambulance 救护车, busy_tone 忙音, carhorn 汽车喇叭, carhorn1 汽车喇叭1, doorbell 门铃, engine 引擎, laser 激光, meebot 小黄人, police_car_1 警车1, police_car_2 警车2, ringtones 来电铃声, robot 机器人, telephone_call 电话呼叫, touch_tone 按键音, wave 电波
            wait (bool, optional): 是否阻塞, 默认False, 不阻塞

        Returns:
            无
        """
        if not wait:
            thread = threading.Thread(target=self._play_audio_file, args=(data, E_Audio.Type.DEFAULT,))
            thread.setDaemon(True)
            thread.start()
            time.sleep(0.1)
        else:
            self.AUDIO.playAudioFile(data, E_Audio.Type.DEFAULT)

    def play_sound_upload(self, data, wait=False):
        """
        播放上传的音频

        Args:
            data (str): 待播放内容，需要加上文件类型后缀
            wait (bool, optional): 是否阻塞, 默认False, 不阻塞

        Returns:
            无
        """
        if not wait:
            thread = threading.Thread(target=self._play_audio_file, args=(data, E_Audio.Type.UPLOAD,))
            thread.setDaemon(True)
            thread.start()
            time.sleep(0.1)
        else:
            self.AUDIO.playAudioFile(data, E_Audio.Type.UPLOAD)

    def play_record(self, data, wait=False):
        """
        播放录音

        Args:
            data (string): 待播放的录音
            wait (bool, optional): 是否阻塞, 默认False, 不阻塞

        Returns:
            无
        """

        if not wait:
            thread = threading.Thread(target=self._play_audio_file, args=(data, E_Audio.Type.RECORD,))
            thread.setDaemon(True)
            thread.start()
            time.sleep(0.1)
        else:
            self.AUDIO.playAudioFile(data, E_Audio.Type.RECORD)

    def play_tone(self, tone, beat, wait=False):
        """
        播放音调

        Args:
            tone (str): 音调 (C5, D5, E5, F5, G5, A5, B5, C6)
            beat (int): 节拍 (0: 1/8拍, 1: 1/4拍, 2: 1/2拍, 3: 1拍, 4: 2拍)

        Returns:
            无
        """
        if beat in E_Audio.Beat.BEATS:
            data = tone.upper() + '-' + E_Audio.Beat.BEATS[beat]
        else:
            return
        self.play_sound(data, wait)

    def _play_audio_file(self, data, type):
        self.AUDIO.playAudioFile(data, type)

    def start_audio_asr(self):
        """
        启动监听

        Returns:
            听到的语音内容 (str)
        """

        result = ''
        response = self.AUDIO.setAudioAsr()
        data = response.data
        if response.code == 0:
            if data:
                result = data
        return result

    def start_audio_nlp(self, data, wait=False):
        """
        监听语音并进行回答NLP

        Args:
            data (string): 问题
            wait (bool, optional): True阻塞等待, 默认False, 不阻塞

        Returns:
            无
        """

        if not wait:
            thread = threading.Thread(target=self._play_nlp, args=(data,))
            thread.setDaemon(True)
            thread.start()
            time.sleep(1)
        else:
            self._play_nlp(data)

    def _play_nlp(self, data):
        result = self.AUDIO.setAudioNlp(data)
        data = result.data
        if data:
            self.play_audio_tts(data, 0, True)

    def play_audio_tts(self, data, voice_type = 0, wait=False):
        """
        播放TTS语音

        Args:
            data (string): 待播放内容
            voice_type (int): 音色(0: 女声, 1: 男声) 默认为0女声
            wait (bool, optional): 是否阻塞, 默认False, 不阻塞

        Returns:
            无
        """

        if not (voice_type == 0 or voice_type == 1):
            func_name = sys._getframe().f_code.co_name
            typestr = 'invalid value of voice_type, expected 0 or 1, got {}'.format(voice_type)
            error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
            print(error_msg)
            return

        if not wait:
            thread = threading.Thread(target=self._play_tts, args=(data, voice_type,))
            thread.setDaemon(True)
            thread.start()
        else:
            self.AUDIO.setAudioTts(data, voice_type)

    def _play_tts(self, data, voice_type):
        self.AUDIO.setAudioTts(data, voice_type)

    def set_volume(self, volume):
        """
        设置音量

        Args:
            volume(int): 音量 (0-100)

        Returns:
            无
        """
        tar_volume = num_normal(volume, 100, 0)
        self.DEVICE.setVolume(tar_volume)

    def get_volume(self):
        """
        获取音量

        Returns:
            音量情况 (list): [volume, isMute]
                    :volume(int) 音量值 0-100
                    :isMute(bool) 是否静音
        """

        response = self.DEVICE.getVolume()
        return [response.volume, response.isMute]


    def stop_audio(self):
        """
        停止播放声音

        Returns:
            无
        """
        self.AUDIO.stopPlayAudio()

    def enable_audio_direction(self):
        """
        开启声源定位

        Returns:
            无
        """
        self.AUDIO.enableAudioDirection()

    def disable_audio_direction(self):
        """
        关闭声源定位

        Returns:
            无
        """
        self.AUDIO.disableAudioDirection()

    def get_audio_direction(self):
        """
        获取声源定位方向

        Returns:
            声源方向 (str): (左方/右方/前方/后方)
        """

        result = self.AUDIO.getDirectionOfAudio()
        if result.code == 0:
            angle = result.angle
            if angle == -1:  # -1表示没有声音或者无效
                return ''
            ret = ''
            if 45 <= angle < 135:
                ret = '前方'
            elif 135 <= angle < 225:
                ret = '左方'
            elif 225 <= angle < 315:
                ret = '后方'
            elif angle >= 315 or angle < 45:
                ret = '右方'
            return ret
        return ''

    """
    
    >>>>>>>>>>>
    >> 显示屏 <<
    >>>>>>>>>>>

    """

    def screen_display_background(self, color):
        """
        主控显示屏显示背景色

        Args:
            color (int): [0-8] 0 黑色;1 白色;2 紫色;3 红色;4 橙色;5 黄色;6 绿色;7 青色;8 蓝色

        Returns:
            无

        """
        if color in E_Device.Color.ColorList:
            dest_color = E_Device.Color.ColorList[color]
            self.DEVICE.display_background(dest_color)
        else:
            logging.error(' unsupported color of {}'.format(color))
            func_name = sys._getframe().f_code.co_name
            typestr = 'invalid value of color, expected [0-8], got {}'.format(color)
            error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
            print(error_msg)
            return

    def screen_print_text(self, text, color):
        """
        主控显示屏打印文字

        Args:
            text (string): 要打印的文字内容
            color (int): [0-8] 0 黑色;1 白色;2 紫色;3 红色;4 橙色;5 黄色;6 绿色;7 青色;8 蓝色

        Returns:
            无
        """
        if color in E_Device.Color.ColorList:
            dest_color = E_Device.Color.ColorList[color]
            self.DEVICE.print_text(text, dest_color)
        else:
            func_name = sys._getframe().f_code.co_name
            typestr = 'invalid value of color, expected [0-8], got {}'.format(color)
            error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
            print(error_msg)
            return

    def screen_print_text_newline(self, text, color):
        """
        主控显示屏打印文字并换行

        Args:
            text (string): 要打印的文字内容
            color (int): [0-8] 0 黑色;1 白色;2 紫色;3 红色;4 橙色;5 黄色;6 绿色;7 青色;8 蓝色

        Returns:
            无

        """
        if color in E_Device.Color.ColorList:
            dest_color = E_Device.Color.ColorList[color]
            self.DEVICE.print_text_newline(text, dest_color)
        else:
            func_name = sys._getframe().f_code.co_name
            typestr = 'invalid value of color, expected [0-8], got {}'.format(color)
            error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
            print(error_msg)
            return

    # def screen_display_image(self, image_name):
    #     self.DEVICE.display_image(image_name)

    def screen_clear(self):
        """
        清空主控显示屏

        Returns:
            无

        """
        self.DEVICE.clear_screen()

    """
    
    >>>>>>>>>>>
    >> 灯光 <<
    >>>>>>>>>>>

    """

    def show_light_rgb(self, lights, red, green, blue):
        """
        主控灯条按照RGB颜色显示

        Args:
            lights[list]: 灯条数组 [0 - 3] 0:上灯条 1:左灯条 2:右灯条 3:下灯条
            red(int): [0-255] R值
            green(int): [0-255] G值
            blue(int): [0-255] B值

        Returns:
            无

        """

        for id in lights:
            if not 0 <= id <= 3:
                func_name = sys._getframe().f_code.co_name
                typestr = 'invalid value of lights id , expected [0-3], got {}'.format(id)
                error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
                print(error_msg)
                return

        color = Color.create_color_rgb(red, green, blue)

        top_light_color = -1
        left_light_color = -1
        right_light_color = -1
        down_light_color = -1
        if E_Device.Light.ID.TOP in lights:
            top_light_color = color.color
        if E_Device.Light.ID.LEFT in lights:
            left_light_color = color.color
        if E_Device.Light.ID.RIGHT in lights:
            right_light_color = color.color
        if E_Device.Light.ID.DOWN in lights:
            down_light_color = color.color

        self.DEVICE.showLightColor(top_light_color, left_light_color, right_light_color, down_light_color)

    def show_light_hsv(self, lights, hue_percent, saturation, value):
        """
        主控灯条按照颜色、饱和度、亮度显示

        Args:
            lights[list]: 灯条数组 [0 - 3] 0:上灯条 1:左灯条 2:右灯条 3:下灯条
            hue_percent(int): [0-100] 颜色
            saturation(int): [0-100] 饱和度
            value(int): [0-100] 亮度

        Returns:
            无

        """
        for id in lights:
            if not 0 <= id <= 3:
                func_name = sys._getframe().f_code.co_name
                typestr = 'invalid value of lights id , expected [0-3], got {}'.format(id)
                error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
                print(error_msg)
                return

        color = Color.create_color_hsv(hue_percent, saturation, value)

        top_light_color = -1
        left_light_color = -1
        right_light_color = -1
        down_light_color = -1
        if E_Device.Light.ID.TOP in lights:
            top_light_color = color.color
        if E_Device.Light.ID.LEFT in lights:
            left_light_color = color.color
        if E_Device.Light.ID.RIGHT in lights:
            right_light_color = color.color
        if E_Device.Light.ID.DOWN in lights:
            down_light_color = color.color

        self.DEVICE.showLightColor(top_light_color, left_light_color, right_light_color, down_light_color)

    def show_light_rgb_effect(self, red, green, blue, effect):
        """
        主控灯条显示等效（按照RGB）

        Args:
            red(int): [0-255] R值
            green(int): [0-255] G值
            blue(int): [0-255] B值
            effect(int): [0-3] 灯效类型 0:常亮 1:关闭 2:呼吸 3:闪烁

        Returns:
            无

        """
        color = Color.create_color_rgb(red, green, blue)
        if not 0 <= effect <= 3:
            func_name = sys._getframe().f_code.co_name
            typestr = 'invalid value of effect, expected [0-3], got {}'.format(effect)
            error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
            print(error_msg)
            return
        self.DEVICE.showLightEffect(color.color, effect)

    def show_light_hsv_effect(self, hue_percent, saturation, value, effect):
        """
        主控灯条显示等效（按照颜色、饱和度、亮度）

        Args:
            hue_percent(int): [0-100] 颜色
            saturation(int): [0-100] 饱和度
            value(int): [0-100] 亮度
            effect(int): [0-3] 灯效类型 0:常亮 1:关闭 2:呼吸 3:闪烁

        Returns:
            无

        """
        color = Color.create_color_hsv(hue_percent, saturation, value)
        if not 0 <= effect <= 3:
            func_name = sys._getframe().f_code.co_name
            typestr = 'invalid value of effect, expected [0-3], got {}'.format(effect)
            error_msg = 'TypeError: {}(): {}'.format(func_name, typestr)
            print(error_msg)
            return
        self.DEVICE.showLightEffect(color.color, effect)

    def turn_off_lights(self):
        """
        关闭所有灯光

        Returns:
            无
        """
        self.DEVICE.turnOffAllLights()

    """

    >>>>>>>>>>>
    >> 传感器 <<        
    >>>>>>>>>>>

    """

    def read_distance_data(self, id):
        """
        读取传感器数据

        Args:
            id (int): 传感器ID

        Returns:
            距离 (int) 单位是cm, 如果为-1，表示未获取到
        """
        logging.debug('read_distance_sensor id:{}'.format(id))

        data = self.SENSOR.getDistanceSensorValue(id)
        if data is not None:
            if data.deviceId == str(id):
                logging.debug('-----获取传感器 {} 的距离为:{}'.format(id, data.value))
                if data.value == -1: # -1表示未获取到
                    return -1
                # 返回值单位是毫米，转换成厘米
                return data.value / 10
        return 0

    def read_gyro_data(self):
        """
        读取陀螺仪数据

        Returns:
            陀螺仪数据 (list): [pitch, roll, yaw, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z]
                        :pitch(float): 俯仰角
                        :roll(float): 横滚角
                        :yaw(float): 偏航角
                        :gyro_x(float): 角速度x
                        :gyro_y(float): 角速度y
                        :gyro_z(float): 角速度z
                        :accel_x(float): 加速度x
                        :accel_y(float): 加速度y
                        :accel_z(float): 加速度z
        """

        data = self.SENSOR.getIMUSensorValue()

        pitch = roll = yaw = gyro_x = gyro_y = gyro_z = accel_x = accel_y = accel_z = 0
        if data is not None:
            pitch = round(data.pitch, 2)
            roll = round(data.roll, 2)
            yaw = round(data.yaw, 2)
            gyro_x = round(data.gyro_x, 2)
            gyro_y = round(data.gyro_y, 2)
            gyro_z = round(data.gyro_z, 2)
            accel_x = round(data.accel_x, 2)
            accel_y = round(data.accel_y, 2)
            accel_z = round(data.accel_z, 2)

        result = [pitch, roll, yaw, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z]
        return result

    def get_attitude(self):
        """
        获取主控姿态

        Returns:
            陀螺仪数据 (list): [is_lean_forward, is_lean_backward, is_lean_left, is_lean_right, is_screen_up, is_screen_down, is_shake]
                        :is_lean_forward(bool): 是否向前倾斜
                        :is_lean_backward(bool): 是否向后倾斜
                        :is_lean_left(bool): 是否左倾斜
                        :is_lean_right(bool): 是否右倾斜
                        :is_screen_up(bool): 是否屏幕朝上
                        :is_screen_down(bool): 是否屏幕朝下
                        :is_shake(bool): 是否震动
        """
        data = self.SENSOR.getAttitudeTilt()
        lean_forward = lean_backward = lean_left = lean_right = screen_up = screen_down = shake = False
        if data is not None:
            lean_forward = data.tilt_forward
            lean_backward = data.tilt_back
            lean_left = data.tilt_left
            lean_right = data.tilt_right
            screen_up = data.face_up
            screen_down = data.face_down
            shake = data.shaking
        result = [lean_forward, lean_backward, lean_left, lean_right, screen_up, screen_down, shake]

        return result

    """

    >>>>>>>>>>>
    >> 物联网 <<        
    >>>>>>>>>>>

    """

    def enable_broadcast(self):
        """
        开启局域网广播

        Returns:
            无
        """
        self.NETWORK.setBrocastEnable('1')

    def disable_broadcast(self):
        """
        关闭局域网广播

        Returns:
            无
        """
        self.NETWORK.setBrocastEnable('0')

    def send_broadcast_message(self, message):
        """
        发送局域网广播消息

        Args:
            message(str): 要发送的消息

        Returns:

        """
        s = str(message)
        if s is None:
            s = ''
        self.NETWORK.sendBrocastMsg(s)

    def set_broadcast_channel(self, channel):
        """
        设置域网广播频道

        Args:
            channel(int) : 频道，取值范围[0-99]

        Returns:
            无
        """
        self.NETWORK.setBrocastPort(num_normal(channel, 99, 0))

    def get_broadcast_message(self):
        """
        获取接收到的局域网广播消息内容

        Returns:
            消息内容(str)
        """
        result = self.NETWORK.getReceivedBrocastMsg()
        return result

    def get_wifi_status(self):
        """
        获取当前连接的Wi-Fi信息

        Returns:
            Wi-Fi信息(list): [ssid, ip_address, mac, rssi, key_mgmt]
                        :ssid (str): ssid
                        :ip_address (str): ip地址
                        :mac (str): mac地址
                        :rssi (str): 信号强度
                        :key_mgmt (str): 加密方式
        """
        response = self.NETWORK.getWifiStatus()
        if response.code == 0:
            data = response.data
            return [data.ssid, data.key_mgmt, data.mac, data.rssi, data.key_mgmt]
        return ['', '', '', '', '']

    """

    >>>>>>>>>>>
    >> 电池 <<        
    >>>>>>>>>>>

    """
    def get_power_status(self):
        """
        获取电池状态

        Returns:
            状态 (list): [scale, power_plug, status]
                    :scale (int): 电量百分比
                    :power_plug (bool): 是否插入电源线
                    :status (int): 状态 (0 正常, 1 低电, 2 充电中, 3 充满电, 4 异常)
        """
        response = self.POWER.getPowerValue()
        if response.code == 0:
            data = response.data
            return [data.scale, data.power_plug, data.status]
        return None

    """

    >>>>>>>>>>>
    >> 蓝牙 <<        
    >>>>>>>>>>>

    """

    def get_bluetooth_status(self):
        """
        获取当前蓝牙信息

        Returns:
            蓝牙状态信息 (list): [poweron, connected, remote_device_name, remote_device_address]
                        :poweron(bool): 是否打开蓝牙
                        :connected(bool): 是否连接蓝牙外设
                        :remote_device_name(str): 外设名称
                        :remote_device_address(str): 外设名称 mac address

        """
        response = self.BLUETOOTH.getBtStatus()
        if response.code == 0:
            remoteDevice = response.remoteDevice
            return [response.poweron, response.connected, remoteDevice.name, remoteDevice.address]
        return None

    def get_joypad_pressing_buttons(self):
        """
        获取当前按下的按钮

        Returns:
            列表 (list) : 当前按下的按钮列表[]，对应值为：
                        L1: 按钮L1, L2: 按钮L2, LS: 左滚轮按下按钮
                        R1: 按钮R1, R2: 按钮R2, RS: 右滚轮按下按钮
                        U: 方向键上, D: 方向键下, L: 方向键左, R: 方向键右
                        X: 按钮X, Y: 按钮Y, A: 按钮A, B: 按钮B
        """
        response = self.NETWORK.get_joypad_button_state()
        return response

    def get_joypad_coordinate(self):
        """
        获取手柄滚轮坐标

        Returns:
            滚轮坐标 (list): [LX, LY, RX, RY]
                    :LX(int): 左滚轮X坐标 取值范围 [-255, 255]
                    :LY(int): 左滚轮Y坐标 取值范围 [-255, 255]
                    :RX(int): 右滚轮X坐标 取值范围 [-255, 255]
                    :RY(int): 右滚轮Y坐标 取值范围 [-255, 255]

        """
        response = self.NETWORK.get_joypad_coordinate()
        return response

    def get_mac_address(self):
        """
        获取主控mac地址

        Returns:
            mac地址(str)
        """
        response = self.DEVICE.getMacAddress()
        if response.code == 0:
            return response.mac
        return ''

    def get_device_name(self):
        """
        获取主控名称

        Returns:
            主控名称(str): UGOT_XXXX
        """
        response = self.DEVICE.getMacAddress()
        if response.code == 0:
            mac = response.mac
            mac_array = mac.split(':')
            if len(mac_array) > 2:
                last = mac_array.pop()
                last2 = mac_array.pop()
                name = 'ugot_' + last2 + last
                name = name.upper()
                return name
        return ''

    """

    >>>>>>>>>>>
    >> 外设列表 <<        
    >>>>>>>>>>>

    """

    def get_peripheral_devices_list(self):
        """
        获取所有外接设备列表

        Returns:
            设备列表 (list): [ {'type': '', 'deviceId': '', 'firmware': '', 'serial': '', ......]
                        :type (str): 设备类型 motor: 电机, servo: 舵机, power: 电池, Clamp: 抓手, Infrared: 测距传感器
                        :deviceId (str): 设备ID
                        :firmware (str): 设备版本
                        :serial (str): 设备序列号
        """
        response = self.DEVICE.getDeviceList()
        if response.code == 0:

            result = []
            for key in list(response.data):
                item = response.data[key]
                for device in item.device_list:
                    # if device.type == 'motor' or device.type == 'servo':
                    result.append({'type':device.type, 'deviceId':device.deviceId, 'firmware':device.firmware, 'serial':device.serial})

            return result
        return []

    """

    >>>>>>>>>>>
    >> 引脚 <<        
    >>>>>>>>>>>

    """

    def set_pin_level(self, pin, level):
        """
        设置引脚电平

        Args:
            pin (int): 引脚序号，可设置的引脚为4/5/6
            level (bool): True高电平，False低电平

        Returns:
            无
        """
        self.GPIO.setGpioExport(str(pin), level)

    def read_pin_level(self, pin):
        """
        读取引脚电平

        Args:
            pin (int): 引脚序号，可设置的引脚为4/5/6

        Returns:
            电平 (int): 1高电平 0低电平
        """
        data = self.GPIO.readGpio(str(pin))
        if data.code == 0:
            result = data.result
            return int(result)
        return 0

    def set_pin_pwm(self, pin, duty_cycle):
        """
        将一个模拟数值写进引脚

        Args:
            pin (int): 引脚序号，可设置的引脚为1/2
            duty_cycle (int): 数值 取值范围[0, 255]

        Returns:
            无
        """
        duty_cycle = num_normal(duty_cycle, 255, 0)
        self.GPIO.setGpioStartExportPwm(str(pin), duty_cycle)

    def set_serial_serbaud(self, baudrate):
        """
        设置串口波特率

        Args:
            baudrate (int): 波特率，可选值: 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200

        Returns:

        """
        self.GPIO.setSerbaud(baudrate=baudrate)

    def write_serial_string(self, newline, text):
        """
        向串口写入字符

        Args:
            newline (bool): 是否换行 True换行，False不换行
            text (str): 要写入的字符

        Returns:
            无
        """
        text = str(text)
        if newline:
            text += '\r\n'
        self.GPIO.serialExportString(value=text)

    def write_serial_number(self, number):
        """
        向串口写入数字

        Args:
            number (int): 要写入的数字

        Returns:
            无
        """

        text = str(number)
        self.GPIO.serialExportString(value=text)

    def read_serial_byte(self):
        """
        读取串口字节

        Returns:
            字节 (str): 字节
        """

        data = self.GPIO.serialReadByte()
        if data.code == 0:
            result = data.result
            return result
        return ''

    def read_serial_string(self):
        """
        读取串口字符串

        Returns:
            字符串 (str): 字符串
        """
        data = self.GPIO.serialReadString()
        if data.code == 0:
            result = data.result
            return result
        return ''

    def read_serial_string_until(self, char):
        """
        读取串口字符串直到

        Args:
            char (str) : 字符串

        Returns:
            字符串 (str): 字符串
        """
        data = self.GPIO.serialReadUtil(char_=char)
        if data.code == 0:
            result = data.result
            return result
        return ''

    def clear_gpio_serial(self):
        """
        释放串口资源

        Returns:
            无
        """
        self.GPIO.clearAllGpioAndSerial()

