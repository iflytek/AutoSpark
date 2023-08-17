import json
import re

from pydantic.types import List

from autospark.helper.prompt_reader import PromptReader
from autospark.helper.token_counter import TokenCounter
from autospark.lib.logger import logger
from autospark_kit.tools.base_tool import BaseTool
from autospark.types.model_source_types import ModelSourceType

FINISH_NAME = "finish"


class AgentPromptBuilder:

    @staticmethod
    def add_list_items_to_string(items: List[str]) -> str:
        list_string = ""
        for i, item in enumerate(items):
            list_string += f"{i + 1}. {item}\n"
        return list_string

    @classmethod
    def add_tools_to_prompt(cls, tools: List[BaseTool], add_finish: bool = True, model_source_type:ModelSourceType=ModelSourceType.OpenAI) -> str:
        final_string = ""
        print(tools)
        for i, item in enumerate(tools):
            if model_source_type != ModelSourceType.SparkAI:
                final_string += f"{i + 1}. {cls._generate_command_string(item)}\n"
            else:
                #final_string += f"{i + 1}. {cls._generate_command_string_spark(item)}\n"
                final_string += f"{i + 1}. {cls._generate_command_string(item)}\n"

        finish_description = (
            "use this to signal that you have finished all your objectives"
        )
        finish_args = (
            '"response": "final response to let '
            'people know you have finished your objectives"'
        )
        finish_string = (
            f"{len(tools) + 1}. \"{FINISH_NAME}\": "
            f"{finish_description}, args: {finish_args}"
        )
        if add_finish:
            final_string = final_string + finish_string + "\n\n"
        else:
            final_string = final_string + "\n"

        return final_string

    @classmethod
    def _generate_command_string(cls, tool: BaseTool) -> str:
        output = f"\"{tool.name}\": {tool.description}"
        # print(tool.args)
        output += f", args json schema: {json.dumps(tool.args)}"
        return output

    @classmethod
    def _generate_command_string_spark(cls, tool: BaseTool) -> str:
        output = f"\"{tool.name}\": {tool.description}"

        # print(tool.args)
        def build_spark_tool(kargs: dict):
            o = ""
            for key, v in kargs.items():
                o += f"{key}: \"<{key}>\","
            return o

        output += f", args : {build_spark_tool(tool.args)}"
        return output

    @classmethod
    def clean_prompt(cls, prompt):
        prompt = re.sub('[ \t]+', ' ', prompt)
        return prompt.strip()

    @classmethod
    def get_auto_spark_single_prompt(cls):
        response_format = {
            "thoughts": {
                "text": "thought",
                "reasoning": "short reasoning",
                "plan": "- short bulleted\n- list that conveys\n- long-term plan",
                "criticism": "constructive self-criticism",
                "speak": "thoughts summary to say to user",
            },
            "tool": {"name": "tool name/task name", "args": {"arg name": "arg value(escape in case of string)"}}
        }
        formatted_response_format = json.dumps(response_format, indent=4)

        as_prompt = PromptReader.read_agent_prompt(__file__, "autospark.txt")

        as_prompt = AgentPromptBuilder.clean_prompt(as_prompt).replace("{response_format}",
                                                                       formatted_response_format)
        return {"prompt": as_prompt, "variables": ["goals", "instructions", "constraints", "tools"]}

    @classmethod
    def start_watcher_based(cls):
        autospark_prompt = PromptReader.read_agent_prompt(__file__, "initialize_autospark_tasks.txt")
        return {"prompt": AgentPromptBuilder.clean_prompt(autospark_prompt), "variables": ["goals", "instructions"]}

    @classmethod
    def analyse_autospark_task(cls):
        constraints = [
            'Exclusively use the tools listed in double quotes e.g. "tool name"'
        ]
        autospark_prompt = PromptReader.read_agent_prompt(__file__, "analyse_autospark_task.txt")
        autospark_prompt = AgentPromptBuilder.clean_prompt(autospark_prompt) \
            .replace("{constraints}", AgentPromptBuilder.add_list_items_to_string(constraints))
        return {"prompt": autospark_prompt, "variables": ["goals", "instructions", "tools", "current_task"]}

    @classmethod
    def create_autospark_tasks(cls):
        # just executed task `{last_task}` and got the result `{last_task_result}`
        autospark_prompt = PromptReader.read_agent_prompt(__file__, "create_autospark_tasks.txt")
        return {"prompt": AgentPromptBuilder.clean_prompt(autospark_prompt),
                "variables": ["goals", "instructions", "last_task", "last_task_result", "pending_tasks"]}

    @classmethod
    def prioritize_autospark_tasks(cls):
        # just executed task `{last_task}` and got the result `{last_task_result}`
        autospark_prompt = PromptReader.read_agent_prompt(__file__, "prioritize_autospark_tasks.txt")
        return {"prompt": AgentPromptBuilder.clean_prompt(autospark_prompt),
                "variables": ["goals", "instructions", "last_task", "last_task_result", "pending_tasks"]}

    @classmethod
    def start_task_based(cls):
        as_prompt = PromptReader.read_agent_prompt(__file__, "initialize_tasks.txt")

        return {"prompt": AgentPromptBuilder.clean_prompt(as_prompt), "variables": ["goals", "instructions"]}
        # as_prompt = as_prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(goals))

    @classmethod
    def analyse_task(cls):
        constraints = [
            'Exclusively use the tools listed in double quotes e.g. "tool name"'
        ]
        as_prompt = PromptReader.read_agent_prompt(__file__, "analyse_task.txt")
        as_prompt = AgentPromptBuilder.clean_prompt(as_prompt) \
            .replace("{constraints}", AgentPromptBuilder.add_list_items_to_string(constraints))
        return {"prompt": as_prompt, "variables": ["goals", "instructions", "tools", "current_task"]}

    @classmethod
    def create_tasks(cls):
        # just executed task `{last_task}` and got the result `{last_task_result}`
        as_prompt = PromptReader.read_agent_prompt(__file__, "create_tasks.txt")
        return {"prompt": AgentPromptBuilder.clean_prompt(as_prompt),
                "variables": ["goals", "instructions", "last_task", "last_task_result", "pending_tasks"]}

    @classmethod
    def prioritize_tasks(cls):
        # just executed task `{last_task}` and got the result `{last_task_result}`
        as_prompt = PromptReader.read_agent_prompt(__file__, "prioritize_tasks.txt")
        return {"prompt": AgentPromptBuilder.clean_prompt(as_prompt),
                "variables": ["goals", "instructions", "last_task", "last_task_result", "pending_tasks"]}

    @classmethod
    def replace_main_variables(cls, as_prompt: str, goals: List[str], instructions: List[str],
                               constraints: List[str],
                               tools: List[BaseTool], add_finish_tool: bool = True, model_source_type: ModelSourceType=ModelSourceType.OpenAI):
        as_prompt = as_prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(goals))
        if len(instructions) > 0 and len(instructions[0]) > 0:
            task_str = "INSTRUCTION(Follow these instruction to decide the flow of execution and decide the next steps for achieving the task):"
            as_prompt = as_prompt.replace("{instructions}",
                                                        "INSTRUCTION: " + '\n' + AgentPromptBuilder.add_list_items_to_string(
                                                            instructions))
            as_prompt = as_prompt.replace("{task_instructions}",
                                                        task_str + '\n' + AgentPromptBuilder.add_list_items_to_string(
                                                            instructions))
        else:
            as_prompt = as_prompt.replace("{instructions}", '')
        as_prompt = as_prompt.replace("{task_instructions}", "")
        as_prompt = as_prompt.replace("{constraints}",
                                                    AgentPromptBuilder.add_list_items_to_string(constraints))

        # logger.info(tools)
        tools_string = AgentPromptBuilder.add_tools_to_prompt(tools, add_finish_tool, model_source_type)
        as_prompt = as_prompt.replace("{tools}", tools_string)
        return as_prompt

    @classmethod
    def replace_task_based_variables(cls, as_prompt: str, current_task: str, last_task: str,
                                     last_task_result: str, pending_tasks: List[str], completed_tasks: list,
                                     token_limit: int):
        if "{current_task}" in as_prompt:
            as_prompt = as_prompt.replace("{current_task}", current_task)
        if "{last_task}" in as_prompt:
            as_prompt = as_prompt.replace("{last_task}", last_task)
        if "{last_task_result}" in as_prompt:
            as_prompt = as_prompt.replace("{last_task_result}", last_task_result)
        if "{pending_tasks}" in as_prompt:
            as_prompt = as_prompt.replace("{pending_tasks}", str(pending_tasks))

        completed_tasks.reverse()
        if "{completed_tasks}" in as_prompt:
            completed_tasks_arr = []
            for task in completed_tasks:
                completed_tasks_arr.append(task['task'])
            as_prompt = as_prompt.replace("{completed_tasks}", str(completed_tasks_arr))

        base_token_limit = TokenCounter.count_message_tokens([{"role": "user", "content": as_prompt}])
        pending_tokens = token_limit - base_token_limit
        final_output = ""
        if "{task_history}" in as_prompt:
            for task in reversed(completed_tasks[-10:]):
                final_output = f"Task: {task['task']}\nResult: {task['response']}\n" + final_output
                token_count = TokenCounter.count_message_tokens([{"role": "user", "content": final_output}])
                # giving buffer of 100 tokens
                if token_count > min(600, pending_tokens):
                    break
            as_prompt = as_prompt.replace("{task_history}", "\n" + final_output + "\n")
        return as_prompt
