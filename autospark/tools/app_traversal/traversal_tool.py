import time
from typing import Type

from autospark_kit.tools.base_tool import BaseTool
from pydantic import Field, BaseModel
from autospark.tools.app_traversal.device import Device
from autospark.tools.app_traversal.hierarchy import Hierarchy
from autospark.tools.app_traversal.utils import get_newest_file_info


class ClickActionSchema(BaseModel):
    x: int = Field(
        ...,
        description="X-axis coordinates"
    )
    y: int = Field(
        ...,
        description="Y-axis coordinates"
    )
    node_info: str = Field(
        ...,
        description="the full node content of the control"
    )


class ClickDevice(BaseTool):
    name = "Click Actuator"
    description = "click on the device, need to provide the coordinates of the x and y axes, as well as the full node " \
                  "content of the control, return the click " \
                  "result"
    args_schema: Type[ClickActionSchema] = ClickActionSchema

    def _execute(self, x: int, y: int, node_info: str) -> bool:
        device = Device(sn=self.get_tool_config("DEVICE"))
        newest_file, newest_file_path = get_newest_file_info("./history/operation")
        write_content = "'operation':'Click Actuator','click_coordinates':'{x},{y}','operation_node_info':{node_info}".format(
            x=x, y=y, node_info=node_info)
        with open(newest_file_path, "a", encoding="utf-8") as f:
            f.write(write_content)
            f.write("\n")
        device.save_screen_shot_in_newest_operation_dir()
        return device.click(x, y)

class GetDeviceHierarchy(BaseTool):
    name = "Get Device Hierarchy Tree"
    description = "Get the Android device`s Hierarchy tree,return the latest Hierarchy tree"

    def _execute(self, ) -> str:
        device = Device(sn=self.get_tool_config("DEVICE"))
        page_source = device.get_hierarchy()
        tree_xml = Hierarchy(page_source, self.get_tool_config("PACKGENAME")).declutter_hierarchy()
        return tree_xml

class GetOperationHistory(BaseTool):
    name = "Get Operation History List"
    description = "Get the historical operation data of the traversal operation and provide it in the form of a list, and the operation order conforms to the list order"

    def _execute(self, ) -> list:
        newest_file, newest_file_path = get_newest_file_info("./history/operation")
        with open(newest_file_path, "r", encoding="utf-8") as f:
            history_text = f.readlines()
        print(history_text)
        return history_text


class OperationSetup(BaseTool):
    name = "Operation Setup"
    description = "Pre-preparation for the operation does not require an active call"

    def _execute(self, ) -> None:
        with open(f"./history/operation/operation_{time.strftime('%Y_%m_%d_%H_%M_%S')}.txt", "w",
                  encoding="utf-8") as f:
            f.close()


if __name__ == '__main__':
    print(GetDeviceHierarchy()._execute())
    # print(ClickDevice().run(x=1, y=2, node_info="test"))
