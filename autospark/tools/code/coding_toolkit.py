from abc import ABC
from typing import List

from autospark_kit.tools.base_tool import BaseToolkit, BaseTool
from autospark.tools.code.write_code_as import CodingTool
from autospark.tools.code.write_spec_as import WriteSpecTool
from autospark.tools.code.write_test_as import WriteTestTool


class CodingToolkit(BaseToolkit, ABC):
    name: str = "代码工具"
    description: str = "代码工具套件包含跟代码任务相关的一些工具集"

    def get_tools(self) -> List[BaseTool]:
        return [CodingTool(), WriteSpecTool(), WriteTestTool()]

    def get_env_keys(self) -> List[str]:
        return []
