import json
from abc import ABC, abstractmethod
from typing import Dict, NamedTuple, List
import re
import ast
import json5
from autospark.helper.json_cleaner import JsonCleaner
from autospark.helper.spark_result_helper import SparkResultParser
from autospark.lib.logger import logger


class AgentGPTAction(NamedTuple):
    name: str
    args: Dict


class AgentTasks(NamedTuple):
    tasks: List[Dict] = []
    error: str = ""


class BaseOutputParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> AgentGPTAction:
        """Return AgentGPTAction"""

class AgentSchemaOutputParser(BaseOutputParser):
    def parse(self, response: str) -> AgentGPTAction:
        if response.startswith("```") and response.endswith("```"):
            response = "```".join(response.split("```")[1:-1])
            response = JsonCleaner.extract_json_section(response)

        # OpenAI returns `str(content_dict)`, literal_eval reverses this
        try:
            logger.debug("AgentSchemaOutputParser: ", response)
            response_obj = ast.literal_eval(response)
            return AgentGPTAction(
                name=response_obj['tool']['name'],
                args=response_obj['tool']['args'],
            )
        except BaseException as e:
            try:
                response_obj= SparkResultParser.parse(response)
            except Exception as e:

                return AgentGPTAction(
                    name="ERROR",
                    args={"error": f"Could not parse invalid format: {response} exception{str(e)}"},
                )
            return AgentGPTAction(
                name=response_obj['tool']['name'],
                args=response_obj['tool']['args'],
            )

