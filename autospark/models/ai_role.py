#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: role
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
from __future__ import annotations

import json

from sqlalchemy import Column, Integer, String

from autospark.models.base_model import DBBaseModel


class AIRole(DBBaseModel):
    """
    Represents an role entity.

    Attributes:
        id (int): The unique identifier of the agent.
        name (str): The name of the agent.
        project_id (int): The identifier of the associated project.
        description (str): The description of the agent.
        agent_workflow_id (int): The identifier of the associated agent workflow.
    """

    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    project_id = Column(Integer)
    description = Column(String)
    agent_workflow_id = Column(Integer)
    prompt = Column(String)

    def __repr__(self):
        """
        Returns a string representation of the Role object.

        Returns:
            str: String representation of the Role.

        """
        return f"Role(id={self.id}, name='{self.name}', project_id={self.project_id}, " \
               f"description='{self.description}', agent_workflow_id={self.agent_workflow_id})"

    @classmethod
    def fetch_prompt(cls, session, role_id: int):
        """
        Fetches the configuration of an agent.

        Args:
            session: The database session object.
            role_id (int): The ID of the agent.

        Returns:
            str: Parsed ai_role prompt.

        """

        ai_role = session.query(AIRole).filter_by(id=role_id).first()
        return ai_role.prompt
