import os
import threading
import time

import uiautomator2 as u2
from utils import get_newest_file_info

class Device(object):
    """
    该类封装了一些常用的操作，如点击，滑动等
    """

    _instance_lock = threading.Lock()

    def __init__(self, sn=""):
        if sn == "":
            self.d = u2.connect()
        else:
            self.d = u2.connect(sn)
    

    def __new__(cls, *args, **kwargs) -> object:
        """
        使用new方法实现单例模式
        :param args:
        :param kwargs:
        :return:
        """
        if not hasattr(Device, "_instance"):
            with Device._instance_lock:
                if not hasattr(Device, "_instance"):
                    Device._instance = object.__new__(cls)
        return Device._instance


    def click(self, x: int, y: int) -> bool:
        """
        对设备进行点击操作
        :param x: x坐标
        :param y: y坐标
        :return: 执行结果
        """
        self.d.click(x, y)
        return True

    def get_hierarchy(self):
        """
        获取当前页面的hierarchy
        :return: hierarchy树
        """
        page_source = self.d.dump_hierarchy(compressed=True, pretty=True)
        return page_source


    def start_app(self, app_name: str) -> bool:
        """
        启动app
        :param app_name: app名称
        :return: 执行结果
        """
        self.d.app_start(app_name)
        return True

    def save_screen_shot_in_newest_operation_dir(self):
        """
        获取当前页面的截图保存在最新操作的文件夹下
        :return: 截图
        """
        filename, filepath = get_newest_file_info("./history/operation")
        screen_dir_name = filename.split('.')[0]
        if not os.path.exists(f"./history/screen_shot/{screen_dir_name}"):
            os.mkdir(f"./history/screen_shot/{screen_dir_name}")
        screen_shot = self.d.screenshot(filename=f"./history/screen_shot/{screen_dir_name}/{time.strftime('%Y_%m_%d_%H_%M_%S')}.png")
        return screen_shot
