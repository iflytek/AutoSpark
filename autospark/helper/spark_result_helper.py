#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: spark_result_helper
@time: 2023/07/25
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
import re


def parse_args_str(args):
    retdict = {}
    pattern = r'(\w+)[:：]'
    result =re.findall(pattern, args)
    if result:
        reg = ''
        for item in result:
            reg += f"{item}(?P<{item}>.*)"
        reg = re.compile(reg)
        m = re.search(reg, args)
        for item in result:
            retdict[item] = clean_args_value(m.group(item))
    return retdict

def clean_args_value(s):
    s = s.strip(":：")
    s = s.strip(",; \'\"")
    return s

class SparkResultParser:

    @classmethod
    def parse(cls, input_str: str = ""):
        """
        Clean the boolean values in the given string.
        原因: <为什么这么做？>
        计划: <计划如何做?>
        命令名称: <从命令中选择的一个命令英文名称,必须取上述name字段>
        命令参数: <参数1key>:<参数2value>, <参数2key>:<参数2value>
        注意: <模型提示需要注意事项>
        Args:
            input_str (str): The string from which the json section is to be extracted.

        Returns:
            str: The extracted json section.
        """
        reasonning_regex = "原因[：:](?P<reasoning>.+)"
        plan_regex = "计划[:：](?P<plan>.+)"
        command_regex = "命令名称[:：](?P<command>.+)"
        args_regex = "命令参数[:：](?P<args>.+)"
        notice_regex = "注意[:：](?P<criticism>.+)"
        lines = input_str.split("\n")
        full_regs = "|".join([reasonning_regex, plan_regex, command_regex, args_regex, notice_regex])
        for line in lines:
            line = line.strip()
            if not line:
                continue
        fp = re.compile(full_regs)
        m = re.findall(fp, input_str)
        reasoning, plan, command, args, notice = "", "", "", "", ""
        for r, p, c, a, n in m:
            if r:
                reasoning = r
            if p:
                plan = p
            if c:
                command = c
            if a:
                args = a
            if n:
                notice = n
        result = {"thoughts": {}, "tool": {"name": "", "args": {}}}
        if args:
            args_dict = parse_args_str(args)

            result["tool"]["args"] = args_dict
        if command:
            result["tool"]["name"] = command
        else:
            raise Exception("Not get command from llm response...")
        if plan:
            result["thoughts"]["plan"] = plan
        if notice:
            result["thoughts"]["criticism"] = plan
        if reasoning:
            result["thoughts"]["reasoning"] = reasoning
        return result



if __name__ == '__main__':
    t = '''原因： 当前任务节点是TASK-1,需要发送一封邮件给ybyang7@iflytek.com,内容是下班早点回家。

计划： 首先，我们需要使用"Send Email"命令来发送邮件。然后，在邮件正文中添加下班早点回家的建议。

命令名称： Send Email

命令参数： to: ybyang7@iflytek.com; subject: 请下班早点回家； body: 亲爱的ybyang7,希望你下班后能够早点回家休息。注意安全哦！"
    '''
    print(SparkResultParser.parse(t))
    args = ' to: ybyang7@iflytek.com,subject: 请下班早点回家，body: 亲爱的ybyang7,请下班早点回家，注意安全。'

    print(parse_args_str(args))
