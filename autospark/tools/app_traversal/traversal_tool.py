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
        # Your logic here
        device = Device(sn=self.get_tool_config("DEVICE"))
        print("x is {}, y is {}, node_info is {}".format(x, y, node_info))
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
        # Your logic here
        # page_source = act.get_hierarchy()
        # print(f"get device hierarchy {page_source}")
        # memory = ConversationBufferMemory(return_messages=True)
        # conversation = ConversationChain(memory=memory, prompt=declutter_hierarchy_prompt, llm=gpt4, verbose=True)
        # result = conversation.predict(input=page_source)
        # chain = LLMChain(llm=gpt3_16k, prompt=declutter_hierarchy_prompt, verbose=True)
        # result = chain.run(input=read_hierarchy("test0"))
        device = Device(sn=self.get_tool_config("DEVICE"))
        page_source = device.get_hierarchy()
        print(page_source)
        tree_xml = Hierarchy(page_source,self.get_tool_config("PACKGENAME")).declutter_hierarchy()
        # tree_dict = get_md_code(result)[0]
        print(tree_xml)
        # return read_hierarchy("test")
        return tree_xml

if __name__ == '__main__':
    print(GetDeviceHierarchy()._execute())
    # print(ClickDevice().run(x=1, y=2, node_info="test"))
