from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
import socket
import time


class DeviceListener(ServiceListener):
    #设备名称+IP列表
    device_info = {}
    #原始方法
    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        #print(f"Service {name} updated")
        pass
    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        #print(f"Service {name} removed")
        pass
    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        #print(f"Service {name} added, service info: {info}")
        #print("name: ",info.name)
        device_name = info.name.split(".")[0].split(":")
        result_name = "UGOT_" + device_name[-2] + device_name[-1]
        #print("device_name : ",result_name)
        #print("ip: ",  socket.inet_ntoa(info.addresses[0]))
        device_ip = socket.inet_ntoa(info.addresses[0])
        self.device_info[result_name] = device_ip

class DeviceScan:
    listener = DeviceListener()
    device_name_list=[]
    device_info_list={}
    def device_discovery(self):
        zeroconf = Zeroconf()
        #当连接wifi的时候服务名不带usb
        browser = ServiceBrowser(zeroconf, "_uExplore_channel_server._tcp.local.", self.listener)
        #当连接usb调试线时候服务名带usb
        browser = ServiceBrowser(zeroconf, "_uExplore_channel_server_usb._tcp.local.", self.listener)
        time.sleep(2)
        zeroconf.close()
    def get_device_info_list(self):
        self.device_info_list = self.listener.device_info
        return self.device_info_list
    def get_device_name_list(self):
        for key in self.listener.device_info:
            self.device_name_list.append(key)
        return self.device_name_list
    def get_device_ip_by_name(self,name):
        device_info = self.get_device_info_list()
        for key in device_info:
            if key == name:
                return device_info[key]
        return ""


    
