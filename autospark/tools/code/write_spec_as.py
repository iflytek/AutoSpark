from typing import Type, Optional, List

from pydantic import BaseModel, Field

from autospark.agent.agent_prompt_builder import AgentPromptBuilder
from autospark.helper.prompt_reader import PromptReader
from autospark.helper.token_counter import TokenCounter
from autospark.lib.logger import logger
from autospark.llms.base_llm import BaseLlm
from autospark.resource_manager.file_manager import FileManager
from autospark_kit.tools.base_tool import BaseTool


class WriteSpecSchema(BaseModel):
    task_description: str = Field(
        ...,
        description="规范任务描述。",
    )

    spec_file_name: str = Field(
        ...,
        description="要写入的文件的名称。仅包含文件名。不包括路径。"
    )


class WriteSpecTool(BaseTool):
    """
    Used to generate program specification.

    Attributes:
        llm: LLM used for specification generation.
        name : The name of tool.
        description : The description of tool.
        args_schema : The args schema.
        goals : The goals.
        resource_manager: Manages the file resources
    """
    llm: Optional[BaseLlm] = None
    agent_id: int = None
    name = "WriteSpecTool"
    description = (
        "一个编写程序规范的工具。"
    )
    args_schema: Type[WriteSpecSchema] = WriteSpecSchema
    goals: List[str] = []
    resource_manager: Optional[FileManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, task_description: str, spec_file_name: str) -> str:
        """
        Execute the write_spec tool.

        Args:
            task_description : The task description.
            spec_file_name: The name of the file where the generated specification will be saved.

        Returns:
            Generated specification or error message.
        """
        prompt = PromptReader.read_tools_prompt(__file__, "write_spec_cn.txt")
        prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
        prompt = prompt.replace("{task}", task_description)
        messages = [{"role": "system", "content": prompt}]

        total_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
        token_limit = TokenCounter.token_limit(self.llm.get_model())
        result = self.llm.chat_completion(messages, max_tokens=(token_limit - total_tokens - 100))

        # Save the specification to a file
        write_result = self.resource_manager.write_file(spec_file_name, result["content"])
        if not write_result.startswith("Error"):
            return result["content"] + "\n 程序规范文件已经成功生成。"
        else:
            return write_result
