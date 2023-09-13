import json
from abc import ABC, abstractmethod
from typing import Dict, NamedTuple, List
import re
import ast
import json5

from autospark.agent.agent_message_builder import AgentLlmMessageBuilder
from autospark.agent.agent_prompt_builder import AgentPromptBuilder
from autospark.helper.json_cleaner import JsonCleaner
from autospark.helper.spark_result_helper import SparkResultParser
from autospark.helper.token_counter import TokenCounter
from autospark.lib.logger import logger

from signal import signal, SIGPIPE, SIG_DFL, SIG_IGN
signal(SIGPIPE, SIG_IGN)


class AgentGPTAction(NamedTuple):
    name: str
    args: Dict


class AgentTasks(NamedTuple):
    tasks: List[Dict] = []
    error: str = ""


class BaseOutputParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> AgentGPTAction:
        """Return AgentGPTAction"""


class AgentSchemaOutputParser(BaseOutputParser):
    def __init__(self, llm=None):
        self.llm = llm

    def fix_json_by_llm(self, session, agent_id, agent_execution_id, jsonStr: str) -> str:

        if not self.llm or not session:
            return jsonStr
        else:
            prompt = AgentPromptBuilder.get_json_fixer_prompt(jsonStr)
            messages = AgentLlmMessageBuilder(session, self.llm, agent_id, agent_execution_id) \
                .build_agent_messages(prompt, [], history_enabled=False,
                                      completion_prompt=None)
            current_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())

            response = self.llm.chat_completion(messages,
                                                TokenCounter.token_limit(self.llm.get_model()) - current_tokens)
            content = response['content']
            if content.startswith("```") and content.endswith("```"):
                content = "```".join(content.split("```")[1:-1])
                content = JsonCleaner.extract_json_section(content)

            return content

    def fix_json_according_schema(self, j, schema) -> str:
        '''星火会返回如下错误案例， 其对 code_description 中把schema的输出也返回了，本质上是模型对shcema理解还
        {
            "thoughts": {
                "reasoning": "首先，我们需要创建一个游戏类，该类包含游戏的基本属性和方法。然后，我们需要创建一个蛇类，该类包含蛇的属性和方法。接下来，我们需要创建一个食物类，该类包含食物的属性和方法。最后，我们需要创建一个主函数，用于初始化游戏、蛇和食物，并处理游戏循环。"
            },
            "tool": {
                "name": "CodingTool",
                "args": {
                    "code_description": {
                        "title": "贪吃蛇游戏代码架构",
                        "description": "编写贪吃蛇游戏的核心类、函数和方法",
                        "type": "string"
                    },
                    "spec_file_name": "snake_game.py"
                }
            }
        }
        '''
        try:
            js = json.loads(j)
        except Exception:
            return j

        if not 'tool' in js:
            return j

        if not "args" in js.get("tool"):
            return j

        args = js.get('tool').get("args")
        for k, v in args.items():
            if type(v) == dict:
                if 'title' in v and 'description' in v and 'type' in v:
                    args[k] = v['description']
                else:
                    args[k] = ''
        js.get("tool")['args'] = args
        return json.dumps(js)

    def parse(self, response: str, session=None, agent_id: str = '', agent_execution_id: str = '') -> AgentGPTAction:
        if response.startswith("```") and response.endswith("```"):
            response = "```".join(response.split("```")[1:-1])
            response = JsonCleaner.extract_json_section(response)

        # 这里如果返回是一个json ，由于星火v2.1 现在对json schema理解还不那么充分，这里做一次fix
        response = self.fix_json_according_schema(response, "")
        # OpenAI returns `str(content_dict)`, literal_eval reverses this
        try:
            logger.debug("AgentSchemaOutputParser: %s" % response)

            response_obj = ast.literal_eval(response)
            return AgentGPTAction(
                name=response_obj['tool']['name'],
                args=response_obj['tool']['args'],
            )
        except BaseException as e:
            st = self.fix_json_by_llm(session, agent_id, agent_execution_id, response)
            response_obj = ast.literal_eval(st)
            return AgentGPTAction(
                name=response_obj['tool']['name'],
                args=response_obj['tool']['args'],
            )


class AgentSchemaToolOutputParser(BaseOutputParser):
    """Parses the output from the agent schema for the tool"""

    def parse(self, response: str) -> AgentGPTAction:
        if response.startswith("```") and response.endswith("```"):
            response = "```".join(response.split("```")[1:-1])
        response = JsonCleaner.extract_json_section(response)
        # ast throws error if true/false params passed in json
        response = JsonCleaner.clean_boolean(response)
        # 这里如果返回是一个json ，由于星火v2.1 现在对json schema理解还不那么充分，这里做一次fix
        response = self.fix_json_according_schema(response, "")
        # OpenAI returns `str(content_dict)`, literal_eval reverses this
        try:
            logger.debug("AgentSchemaOutputParser: ", response)
            response_obj = ast.literal_eval(response)
            args = response_obj['args'] if 'args' in response_obj else {}
            return AgentGPTAction(
                name=response_obj['name'],
                args=args,
            )
        except BaseException as e:
            logger.info(f"AgentSchemaToolOutputParser: Error parsing JSON respons {e}")
            raise e

    def fix_json_according_schema(self, j, schema) -> str:
        '''星火会返回如下错误案例， 其对 code_description 中把schema的输出也返回了，本质上是模型对shcema理解还
        {
            "thoughts": {
                "reasoning": "首先，我们需要创建一个游戏类，该类包含游戏的基本属性和方法。然后，我们需要创建一个蛇类，该类包含蛇的属性和方法。接下来，我们需要创建一个食物类，该类包含食物的属性和方法。最后，我们需要创建一个主函数，用于初始化游戏、蛇和食物，并处理游戏循环。"
            },
            "tool": {
                "name": "CodingTool",
                "args": {
                    "code_description": {
                        "title": "贪吃蛇游戏代码架构",
                        "description": "编写贪吃蛇游戏的核心类、函数和方法",
                        "type": "string"
                    },
                    "spec_file_name": "snake_game.py"
                }
            }
        }
        '''
        try:
            js = json.loads(j)
        except Exception:
            return j

        if not 'tool' in js:
            return j

        if not "args" in js.get("tool"):
            return j

        args = js.get('tool').get("args")
        for k, v in args.items():
            if type(v) == dict:
                if 'title' in v and 'description' in v and 'type' in v:
                    args[k] = v['description']
                else:
                    args[k] = ''
        js.get("tool")['args'] = args
        return json.dumps(js)
