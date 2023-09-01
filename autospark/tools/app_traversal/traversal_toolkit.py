from abc import ABC
from typing import List

from autospark_kit.tools.base_tool import BaseToolkit, BaseTool

from autospark.tools.app_traversal.traversal_tool import ClickDevice, GetDeviceHierarchy, GetOperationHistory, \
    OperationSetup


class TraversalToolkit(BaseToolkit, ABC):
    name: str = "Traversal Toolkit"
    description: str = "Toolkit containing tools for app traversal"

    def get_tools(self) -> List[BaseTool]:
        return [
            ClickDevice(),
            GetDeviceHierarchy(),
            GetOperationHistory(),
            OperationSetup(),
        ]

    def get_env_keys(self) -> List[str]:
        return [
            "LLM",
            "DEVICE",
            "PACKAGE_NAME"
        ]
