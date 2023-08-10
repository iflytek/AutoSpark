#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: ai_role
@time: 2023/07/18
@contact: ybyang7@iflytek.com
@site:  
@software: PyCharm 

# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃      ☃      ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛ 
"""

#  Copyright (c) 2022. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.
import threading
from abc import ABC, abstractmethod


class BaseRole(ABC):
    """
    base role is a abstract
    """

    @abstractmethod
    def get_prompt(self) -> str:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def get_model(self):
        """
        Returns:
            Represent LLM model
        """
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        "role can run during the agent execution"
        pass



