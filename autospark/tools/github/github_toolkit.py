from abc import ABC
from typing import List
from autospark_kit.tools.base_tool import BaseTool, BaseToolkit
from autospark.tools.github.add_file import GithubAddFileTool
from autospark.tools.github.delete_file import GithubDeleteFileTool
from autospark.tools.github.search_repo import GithubRepoSearchTool


class GitHubToolkit(BaseToolkit, ABC):
    name: str = "GitHub Toolkit"
    description: str = "GitHub Tool Kit contains all github related to tool"

    def get_tools(self) -> List[BaseTool]:
        return [GithubAddFileTool(), GithubDeleteFileTool(), GithubRepoSearchTool()]

    def get_env_keys(self) -> List[str]:
        return [
            "GITHUB_ACCESS_TOKEN",
            "GITHUB_USERNAME",
            # Add more file related config keys here
        ]
