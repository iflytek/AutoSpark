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


class CodingSchema(BaseModel):
    code_description: str = Field(
        ...,
        description="Description of the coding task",
    )


class CodingTool(BaseTool):
    """
    Used to generate code.

    Attributes:
        llm: LLM used for code generation.
        name : The name of tool.
        description : The description of tool.
        args_schema : The args schema.
        goals : The goals.
        resource_manager: Manages the file resources
    """
    llm: Optional[BaseLlm] = None
    agent_id: int = None
    name = "CodingTool"
    description = (
        "您将获得编写代码的说明。你会写一个很长的答案。"
        "确保架构的每个细节最终都以代码的形式实现。 "
        "一步步思考并说服自己做出正确的决定，以确保我们做出正确的决定 "
        "您将首先列出必要的核心类、函数、方法的名称， "
        "以及对其目的的快速评论。然后您将输出每个文件的内容，包括所有代码。"
    )
    args_schema: Type[CodingSchema] = CodingSchema
    goals: List[str] = []
    resource_manager: Optional[FileManager] = None
    tool_response_manager: Optional[ToolResponseQueryManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, code_description: str) -> str:
        """
        Execute the write_code tool.

        Args:
            code_description : The coding task description.
            code_file_name: The name of the file where the generated codes will be saved.

        Returns:
            Generated code with where the code is being saved or error message.
        """
        prompt = PromptReader.read_tools_prompt(__file__, "write_code_cn.txt") + "\n这是一些用用的知识:\n" + PromptReader.read_tools_prompt(__file__, "generate_logic_cn.txt")
        prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
        prompt = prompt.replace("{code_description}", code_description)
        spec_response = self.tool_response_manager.get_last_response("WriteSpecTool")
        if spec_response != "":
            prompt = prompt.replace("{spec}", "Use this specs for generating the code:\n" + spec_response)
        logger.info(prompt)
        messages = [{"role": "system", "content": prompt}]

        total_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
        token_limit = TokenCounter.token_limit(self.llm.get_model())
        result = self.llm.chat_completion(messages, max_tokens=(token_limit - total_tokens - 100))

        # Get all filenames and corresponding code blocks
        regex = r"(\S+?)\n```\S*\n(.+?)```"
        matches = re.finditer(regex, result["content"], re.DOTALL)

        file_names = []
        # Save each file

        for match in matches:
            # Get the filename
            file_name = re.sub(r'[<>"|?*]', "", match.group(1))

            # Get the code
            code = match.group(2)

            # Ensure file_name is not empty
            if not file_name.strip():
                continue

            file_names.append(file_name)
            save_result = self.resource_manager.write_file(file_name, code)
            if save_result.startswith("Error"):
                return save_result

        # Get README contents and save
        split_result = result["content"].split("```")
        if len(split_result) > 0:
            readme = split_result[0]
            save_readme_result = self.resource_manager.write_file("README.md", readme)
            if save_readme_result.startswith("Error"):
                return save_readme_result

        return result["content"] + "\n 代码已成功生成:  " + ", ".join(file_names)
