from abc import ABC
from typing import List
from autospark_kit.tools.base_tool import BaseTool, BaseToolkit
from autospark.tools.file.append_file import AppendFileTool
from autospark.tools.file.delete_file import DeleteFileTool
from autospark.tools.file.list_files import ListFileTool
from autospark.tools.file.read_file import ReadFileTool
from autospark.tools.file.write_file import WriteFileTool


class FileToolkit(BaseToolkit, ABC):
    name: str = "File Toolkit"
    description: str = "File Tool kit contains all tools related to file operations"

    def get_tools(self) -> List[BaseTool]:
        return [AppendFileTool(), DeleteFileTool(), ListFileTool(), ReadFileTool(), WriteFileTool()]

    def get_env_keys(self) -> List[str]:
        return []
