
import sys,os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../grpc_pb/')
from ugot.grpc_pb import model_pb2,model_pb2_grpc
from base_client import GrpcClient

MODEL_TYPE_MECANUM = 'mecanum'
MODEL_TYPE_BALANCE = 'balance'
MODEL_TYPE_TRANSFORM = 'transform'

class ModelClient(GrpcClient):
    def __init__(self, address):
        super().__init__(address)

        self.client = model_pb2_grpc.ModelServiceGrpcStub(channel=self.channel)
        # 舵机
        pass

    def model_move_control(self, linear_speed=0, direction=0, rotate_speed=0, time=0, mileage=0, target_angle=0,
                           model_type='', client_type=0):
        """ 模型通用运动控制接口
        """

        # print('received model_move_control parameters {} {} {} {} {} {}'.format(linear_speed, direction, rotate_speed, time, mileage, target_angle))

        input_data = model_pb2.ModelControlRequest()
        input_data.type = model_type
        input_data.client_type = client_type  # 1表示手柄操作

        input_data.params.linear_speed = linear_speed
        input_data.params.direction = direction
        input_data.params.rotate_speed = rotate_speed
        input_data.params.time = time
        input_data.params.mileage = mileage
        input_data.params.target_angle = target_angle

        response = self.client.modelCommonControl(input_data)
        return response

    def mecanum_move_control(self, linear_speed=0, direction=0, rotate_speed=0, time=0, mileage=0, target_angle=0,
                               client_type=0):
        """ 麦轮车通用控制
        """

        response = self.model_move_control(linear_speed, direction, rotate_speed, time, mileage, target_angle,
                                            model_type=MODEL_TYPE_MECANUM, client_type=client_type)
        return response

    def mecanum_stop(self):
        """ 小车停止
        """
        input_data = model_pb2.MecanumStopRequest()

        input_data.type = MODEL_TYPE_MECANUM

        response = self.client.mecanumStop(input_data)
        return response

    def mecanum_motor_control(self, lf, rf, lb, rb):
        """ 变形工程车电机控制
        """
        input_data = model_pb2.MotorControlRequest()

        input_data.type = MODEL_TYPE_MECANUM

        input_data.params.lf_joint = lf
        input_data.params.rf_joint = rf
        input_data.params.lb_joint = lb
        input_data.params.rb_joint = rb

        response = self.client.mecanumMotorControl(input_data)
        return response

    def mecanum_xyz_control(self, speed_x, speed_y, speed_z):
        """ 麦轮车xyz控制
        """
        input_data = model_pb2.XYZControlRequest()

        input_data.type = MODEL_TYPE_MECANUM

        input_data.params.linear_x = speed_x
        input_data.params.linear_y = speed_y
        input_data.params.angle_z = speed_z

        response = self.client.mecanumXYZControl(input_data)
        return response

    def transform_move_control(self, linear_speed=0, direction=0, rotate_speed=0, time=0, mileage=0, target_angle=0,
                               client_type=0):
        """ 变形工程车通用控制
        """

        response = self.model_move_control(linear_speed, direction, rotate_speed, time, mileage, target_angle,
                                            model_type=MODEL_TYPE_TRANSFORM, client_type=client_type)
        return response

    def transform_motor_control(self, lf, rf, lb, rb):
        """ 变形工程车电机控制
        """
        input_data = model_pb2.MotorControlRequest()

        input_data.type = MODEL_TYPE_TRANSFORM

        input_data.params.lf_joint = lf
        input_data.params.rf_joint = rf
        input_data.params.lb_joint = lb
        input_data.params.rb_joint = rb

        response = self.client.mecanumMotorControl(input_data)
        return response

    def transform_stop(self):
        """ 小车停止
        """
        input_data = model_pb2.MecanumStopRequest()

        input_data.type = MODEL_TYPE_TRANSFORM

        response = self.client.mecanumStop(input_data)
        return response

    def transform_arm_control(self, joint, position, time):
        input_data = model_pb2.TransformArmsControlRequest()

        input_data.type = MODEL_TYPE_TRANSFORM

        input_data.params.joint = joint
        input_data.params.position = position
        input_data.params.time = int(time / 20)

        response = self.client.transformArmsControl(input_data)
        return response

    def transform_set_height(self, height):
        input_data = model_pb2.TransformSetHeightRequest()

        input_data.type = MODEL_TYPE_TRANSFORM

        input_data.params.height = height

        response = self.client.transformSetHeight(input_data)
        return response

    def transform_adaption(self, enable):
        input_data = model_pb2.EnableAdaptivePoseRequest()

        input_data.type = MODEL_TYPE_TRANSFORM

        input_data.params.enable = enable

        response = self.client.enableAdaptivePose(input_data)
        return response

    def transform_set_height_by_increment(self, increment):
        input_data = model_pb2.TransformSetHeightIncrementRequest()

        input_data.type = MODEL_TYPE_TRANSFORM
        input_data.client_type = 1  # 1表示手柄操作

        input_data.params.increment = increment

        response = self.client.transformSetHeightByIncrement(input_data)
        return response

    def balance_move_control(self, linear_speed=0, direction=0, rotate_speed=0, time=0, mileage=0, target_angle=0,
                             client_type=0):
        """ 平衡车通用控制
        """

        response = self.model_move_control(linear_speed, direction, rotate_speed, time, mileage, target_angle,
                                            model_type=MODEL_TYPE_BALANCE, client_type=client_type)
        return response

    def balance_keep_balancing(self, start, keep_balance=True):
        """启动小车并保持自平衡
        """
        input_data = model_pb2.BalanceKeepBalancingRequest()
        input_data.type = MODEL_TYPE_BALANCE

        input_data.params.start = start
        input_data.params.keep_balance = keep_balance

        response = self.client.balanceKeepBalancing(input_data)
        return response

    def setAcceleration(self, type, linear_x=0.0, linear_y=0.0, linear_z=0.0, angular_x=0.0, angular_y=0.0, augular_z=0.0):
        """设置加速度通用接口
        """
        input_data = model_pb2.SetAccelerationRequest()

        input_data.type = type

        input_data.params.linear_x = linear_x
        input_data.params.linear_y = linear_y
        input_data.params.linear_z = linear_x
        input_data.params.angular_x = angular_x
        input_data.params.angular_y = angular_y
        input_data.params.angular_z = augular_z

        response = self.client.setAcceleration(input_data)
        return response

    def setBalanceAcceleration(self, linear_x=0.0):
        """设置平衡车加速度
        """
        input_data = model_pb2.SetAccelerationRequest()

        input_data.type = MODEL_TYPE_BALANCE

        input_data.params.linear_x = linear_x
        input_data.params.linear_y = 0
        input_data.params.linear_z = 0
        input_data.params.angular_x = 0
        input_data.params.angular_y = 0
        input_data.params.angular_z = 8

        response = self.client.setAcceleration(input_data)
        return response

    def resetAcceleration(self, type):
        """重置加速度
        """
        input_data = model_pb2.ResetAccelerationRequest()

        input_data.type = type # type=all表示不区分模型

        response = self.client.resetAcceleration(input_data)
        return response

    def stopAllModels(self):
        input_data = model_pb2.MecanumStopRequest()

        input_data.type = 'all'

        response = self.client.mecanumStop(input_data)
        return response
    def __del__(self):
        # 销毁时候停止模型
        try:
            self.stopAllModels()
        except Exception as e:
            print('model stopAllModels error:')