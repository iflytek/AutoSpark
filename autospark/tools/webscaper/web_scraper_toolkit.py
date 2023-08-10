from abc import ABC
from typing import List
from autospark_kit.tools.base_tool import BaseTool, BaseToolkit
from autospark.tools.webscaper.tools import WebScraperTool


class WebScrapperToolkit(BaseToolkit, ABC):
    name: str = "Web Scrapper Toolkit"
    description: str = "Web Scrapper tool kit is used to scrape web"

    def get_tools(self) -> List[BaseTool]:
        return [
            WebScraperTool(),
        ]

    def get_env_keys(self) -> List[str]:
        return []
