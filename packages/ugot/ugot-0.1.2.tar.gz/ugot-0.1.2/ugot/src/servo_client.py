import sys,os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../grpc_pb/')
from ugot.grpc_pb import servo_pb2,servo_pb2_grpc
from base_client import GrpcClient

class ServoClient(GrpcClient):
    def __init__(self, address):
        super().__init__(address)

        self.client = servo_pb2_grpc.ServoServiceGrpcStub(channel=self.channel)

    def controlSingleClamp(self, status):
        # 控制夹手
        input_data = servo_pb2.ControlSingleClampRequest()
        input_data.status = status

        response = self.client.controlSingleClamp(input_data)
        return response

    def getClampStatus(self):
        # 获取夹手状态
        input_data = servo_pb2.GetClampStatusRequest()

        response = self.client.getClampStatus(input_data)
        return response.status


    def roboticArmRestory(self):
        # 机械臂复位
        input_data = servo_pb2.RoboticArmRestoryRequest()

        response = self.client.roboticArmRestory(input_data)
        return response

    def roboticArmMoveToTargetPostion(self, x, y, z, time):
        # 机械臂移动到指定的位置
        input_data = servo_pb2.RoboticArmMovePostionRequest()
        input_data.params.x = x
        input_data.params.y = y
        input_data.params.z = z
        input_data.params.time = int(time / 20)
        response = self.client.roboticArmMoveToTargetPostion(input_data)
        return response

    def roboticArmSetJointPosition(self, params, type=0):
        # 设置机械臂关节
        # params: [{"joint": 1, "position" :80, "time":1000}, ..]:
        input_data = servo_pb2.RoboticArmSetJointPositionRequest()
        for data in params:
            item = input_data.params.add()
            item.joint = data["joint"]
            item.position = data["position"]
            item.time = int(data["time"] / 20)
            item.type = type  # 0控制舵机角度1控制关节角度

        response = self.client.roboticArmSetJointPosition(input_data)
        return response

    def roboticArmGetJoints(self):
        # 获取机械臂关节
        input_data = servo_pb2.RoboticArmGetJointsRequest()

        response = self.client.roboticArmGetJoints(input_data)
        return response