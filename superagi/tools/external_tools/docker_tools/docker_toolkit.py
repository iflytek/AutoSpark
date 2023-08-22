from abc import ABC
from autospark_kit.tools.base_tool import BaseToolkit, BaseTool
from typing import Type, List
from artifacts_docker_tool import DockerImageListTool


class IflytekArtifactoryToolkit(BaseToolkit, ABC):
    name: str = "docker tools"
    description: str = "docker tools contains all tools related to Iflytek Artifactory"

    def get_tools(self) -> List[BaseTool]:
        return [DockerImageListTool()]

    def get_env_keys(self) -> List[str]:
        return ["ArtifactoryUrl", "DockerUsername", "DockerPassword"]
