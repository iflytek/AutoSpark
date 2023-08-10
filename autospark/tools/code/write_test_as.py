import re
from typing import Type, Optional, List

from pydantic import BaseModel, Field

from autospark.agent.agent_prompt_builder import AgentPromptBuilder
from autospark.helper.prompt_reader import PromptReader
from autospark.helper.token_counter import TokenCounter
from autospark.lib.logger import logger
from autospark.llms.base_llm import BaseLlm
from autospark.resource_manager.file_manager import FileManager
from autospark_kit.tools.base_tool import BaseTool
from autospark.tools.tool_response_query_manager import ToolResponseQueryManager


class WriteTestSchema(BaseModel):
    test_description: str = Field(
        ...,
        description="测试任务描述",
    )
    test_file_name: str = Field(
        ...,
        description="要写入的文件的名称。仅包含文件名。不包括路径。"
    )


class WriteTestTool(BaseTool):
    """
    Used to generate unit tests based on the specification.

    Attributes:
        llm: LLM used for test generation.
        name : The name of tool.
        description : The description of tool.
        args_schema : The args schema.
        goals : The goals.
        resource_manager: Manages the file resources
    """
    llm: Optional[BaseLlm] = None
    agent_id: int = None
    name = "WriteTestTool"
    description = (
        "您是一位超级聪明的开发人员，使用测试驱动开发根据规范编写测试。\n"
        "请根据上述规范生成测试。测试应该尽可能简单， "
        "但仍然涵盖了所有功能。\n"
        "将它们写入文件中"
    )
    args_schema: Type[WriteTestSchema] = WriteTestSchema
    goals: List[str] = []
    resource_manager: Optional[FileManager] = None
    tool_response_manager: Optional[ToolResponseQueryManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, test_description: str, test_file_name: str) -> str:
        """
        Execute the write_test tool.

        Args:
            test_description : The specification description.
            test_file_name: The name of the file where the generated tests will be saved.

        Returns:
            Generated unit tests or error message.
        """
        prompt = PromptReader.read_tools_prompt(__file__, "write_test_cn.txt")
        prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
        prompt = prompt.replace("{test_description}", test_description)

        spec_response = self.tool_response_manager.get_last_response("WriteSpecTool")
        if spec_response != "":
            prompt = prompt.replace("{spec}",
                                    "请根据以下规范描述生成单元测试:\n" + spec_response)
        else:
            spec_response = self.tool_response_manager.get_last_response()
            if spec_response != "":
                prompt = prompt.replace("{spec}",
                                        "请根据以下规范描述生成单元测试:\n" + spec_response)

        messages = [{"role": "system", "content": prompt}]
        logger.info(prompt)

        total_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
        token_limit = TokenCounter.token_limit(self.llm.get_model())
        result = self.llm.chat_completion(messages, max_tokens=(token_limit - total_tokens - 100))

        regex = r"(\S+?)\n```\S*\n(.+?)```"
        matches = re.finditer(regex, result["content"], re.DOTALL)

        file_names = []
        # Save each file

        for match in matches:
            # Get the filename
            file_name = re.sub(r'[<>"|?*]', "", match.group(1))
            code = match.group(2)
            if not file_name.strip():
                continue

            file_names.append(file_name)
            save_result = self.resource_manager.write_file(file_name, code)
            if save_result.startswith("Error"):
                return save_result

        # Save the tests to a file
        # save_result = self.resource_manager.write_file(test_file_name, code_content)
        if not result["content"].startswith("Error"):
            return result["content"] + " \n 测试文件已经成功生成: " + test_file_name
        else:
            return save_result
